# Codex-Job Skill Improvements

You are improving the codex-job skill located at /lump/apps/invoke-codex-from-claude/codex-job/. This skill is used to delegate implementation tasks
  to Codex subagents. Read every file in that directory before making any changes.
S
  Files to read first

  /lump/apps/invoke-codex-from-claude/codex-job/SKILL.md
  /lump/apps/invoke-codex-from-claude/codex-job/references/metrics-schema.md
  /lump/apps/invoke-codex-from-claude/codex-job/references/invocation-patterns.md
  /lump/apps/invoke-codex-from-claude/codex-job/references/failure-handling.md
  /lump/apps/invoke-codex-from-claude/codex-job/scripts/write_delegation_metric.py
  /lump/apps/invoke-codex-from-claude/codex-job/scripts/parse_codex_run.py
  /lump/apps/invoke-codex-from-claude/codex-job/scripts/run_codex_task.sh
  /lump/apps/invoke-codex-from-claude/codex-job/scripts/invoke_codex_with_review.sh
  /lump/apps/invoke-codex-from-claude/codex-job/assets/templates/delegation-metrics-entry.json

  Do not modify any file you have not read. Do not create new files unless a fix explicitly requires one.

  ---
  Fix 1 — Add ticket_id and files_changed to delegation metrics

  Problem: write_delegation_metric.py records no ticket identifier and no list of files changed. You cannot answer "which tickets
  burned the most tokens?" without manual log archaeology.

  Changes to write_delegation_metric.py:

  Add two new optional CLI arguments:

- --ticket-id (string, default "") — the ticket identifier, e.g. "P4-001"
- --files-changed (string, default "") — comma-separated list of files written/modified by the delegate, e.g.
  "skills/adaptive_plan_rules.py,tests/test_p4_001.py"

  Add both fields to the output record:
  "ticket_id": args.ticket_id,
  "files_changed": [f.strip() for f in args.files_changed.split(",") if f.strip()] if args.files_changed else [],

  Place ticket_id immediately after repo in the record dict. Place files_changed immediately after retry_count.

  Changes to assets/templates/delegation-metrics-entry.json:

  Add the two new fields in the same positions:
  "ticket_id": "",
  "files_changed": []

  Changes to references/metrics-schema.md:

  Add both fields to the Required fields list with descriptions:

- ticket_id — ticket identifier string, empty string if not applicable
- files_changed — list of file paths written or modified by the delegate, empty list if unknown

  Edge cases:

- --files-changed with only whitespace/commas after splitting → produce [], not [""]
- --ticket-id not passed → field is "" in record, not null and not omitted
- Existing callers that don't pass these args must continue to work without change (both are optional with defaults)

  ---
  Fix 2 — Automate the work-log.md entry inside write_delegation_metric.py

  Problem: SKILL.md requires a work-log.md entry per delegation but nothing writes it automatically, so it gets skipped.

  Changes to write_delegation_metric.py:

  After successfully appending to the JSONL file, append a one-line entry to work-log.md in the same directory as --out. Format:

  {timestamp} | {ticket_id or task_type} | {delegated_model} | {status} | {duration_sec}s | {codex_tokens_total} tokens

  Example:
  2026-04-08T03:52:13Z | P4-001 | gpt-5.1-codex-mini | success | 108s | 146552 tokens

  Rules:

- Use ticket_id if non-empty, otherwise fall back to task_type
- work-log.md is in the same directory as the --out JSONL file (derive path as out_path.parent / "work-log.md")
- Append with a newline — never overwrite
- If work-log.md does not exist, create it with a header line first:

# Delegation Work Log

- then append the entry
- If writing work-log.md fails (permissions, etc.), print a warning to stderr but do not raise — the JSONL write already succeeded
   and that is the primary output

  Edge cases:

- duration_sec may be 0.0 if elapsed was not captured — write 0s, not an error
- codex_tokens_total may be 0 if token extraction failed — write 0 tokens, not an error
- The function writing work-log.md must be separate from the JSONL write so a failure in one cannot affect the other

  ---
  Fix 3 — Improve token extraction in parse_codex_run.py for null input/output split

  Problem: input_tokens and output_tokens are almost always null in summaries because Codex emits its token usage in formats the
  current patterns don't catch. Only total_tokens is reliably extracted. This makes cost estimation impossible.

  Changes to parse_codex_run.py — extract_token_usage:

  Extend the pattern lists for input_tokens and output_tokens with additional formats observed in Codex logs:

  "input_tokens": [
      # existing patterns stay first
      r"input[_\s-]?tokens?\s*[:=]\s*([0-9][0-9,]*)",
      r"prompt[_\s-]?tokens?\s*[:=]\s*([0-9][0-9,]_)",
      # additional formats
      r'"input_tokens"\s_:\s*([0-9][0-9,]_)',        # JSON field in log
      r'"prompt_tokens"\s_:\s*([0-9][0-9,]_)',        # OpenAI usage JSON
      r'in(?:put)?\s_=\s*([0-9][0-9,]_)\s_(?:tok|out)',  # "in=1234 tok out=567"
  ],
  "output_tokens": [
      r"output[_\s-]?tokens?\s*[:=]\s*([0-9][0-9,]*)",
      r"completion[_\s-]?tokens?\s*[:=]\s*([0-9][0-9,]_)",
      # additional formats
      r'"output_tokens"\s_:\s*([0-9][0-9,]_)',
      r'"completion_tokens"\s_:\s*([0-9][0-9,]_)',
      r'out(?:put)?\s_=\s*([0-9][0-9,]*)\s*tok',
  ],

  Also add a null-flagging section at the end of extract_token_usage. After all extraction attempts, if input_tokens is still None  
  or output_tokens is still None, add an "extraction_incomplete" key to the result:

  if result["input_tokens"] is None or result["output_tokens"] is None:
      result["extraction_incomplete"] = True

  This makes it visible in the summary JSON rather than silently zeroing.

  Edge cases:

- New patterns must not match cost lines (e.g., "total cost: $0.12") — the pattern prefix requirements (input, output, prompt,
  completion) are sufficient guards, but verify the inline-JSON patterns only match on lines that are clearly usage objects, not
  prose
- Pattern order matters — more specific patterns should come before more general ones (existing patterns first, new ones appended)
- The derived total logic (input + output when total is None) already exists and must not be broken by the new patterns

  ---
  Fix 4 — Narrow the false-positive review trigger in invoke_codex_with_review.sh

  Problem: The failure detection grep (error: |fatal: |Exception:) matches strings inside task output (pytest tracebacks, tool
  stderr), triggering unnecessary review runs even when the task succeeded.

  Changes to invoke_codex_with_review.sh:

  Replace this block:

# Check for real failure indicators

  if grep -qE "error: |fatal: |Exception:" "$LATEST_LOG" 2>/dev/null; then
    REAL_FAILURE=1
  fi

  With a narrower check that only matches Codex runtime error lines, not arbitrary task output:

# Check for real Codex runtime failure indicators (not task output content)

  if grep -qE "^\[error\]|^Error:|^fatal error:|^Unhandled exception" "$LATEST_LOG" 2>/dev/null; then
    REAL_FAILURE=1
  fi

  The key constraint: patterns must be anchored to line start (^) so they only match lines where the error is the primary content,  
  not lines where "error" appears inside quoted output or pytest tracebacks.

  Additionally, remove the Exception: pattern entirely — Python exception lines in task output are task-level, not Codex runtime
  failures.

  Edge cases:

- Codex may emit [Error] (capital E) — use -i flag on this specific grep: grep -iqE "^\[error\]|^Error:|^fatal error:|^Unhandled
  exception"
- An empty log file must not trigger REAL_FAILURE=1 — the 2>/dev/null guard already handles this, confirm it is preserved
- The existing CODEX_COMPLETED=1 check (looking for "tokens used" in log) must remain — it is the primary success signal and is
  unaffected by this change

  ---
  Fix 5 — Add --task-file option to run_codex_task.sh

  Problem: Long task prompts passed as shell string arguments are fragile — quoting issues and no clean audit trail of the exact
  prompt used.

  Changes to run_codex_task.sh:

  Add --task-file <path> as an alternative to --task. When --task-file is provided:

  1. Read the file contents at launch time (before the Codex command is constructed)
  2. Use the file contents as the task prompt string — identical behavior to --task from that point on
  3. Also record task_file in the meta JSON output alongside task

  Arg parsing addition:
  TASK_FILE=""

# in the case block

  --task-file)
    TASK_FILE="${2:-}"
    shift 2
    ;;

  After arg parsing, resolve task from file if provided:
  if [[ -n "$TASK_FILE" ]]; then
    if [[ ! -f "$TASK_FILE" ]]; then
      echo "Error: --task-file path does not exist: $TASK_FILE" >&2
      exit 2
    fi
    TASK="$(cat "$TASK_FILE")"
  fi

  Validation: update the existing "task required" check to also pass when TASK_FILE was provided (the file read above will have
  populated TASK by that point, so no change needed there — just confirm the order is correct: file read happens before the
  validation check).

  Meta JSON addition — add task_file field:
  "task_file": os.environ.get("TASK_FILE_ENV", "") or None,

  Pass it via environment before the python heredoc:
  TASK_FILE_ENV="$TASK_FILE" \

  Edge cases:

- --task and --task-file both provided → --task-file wins (last assignment wins since file read overwrites TASK), or emit an error
   — choose the error path: echo "Error: --task and --task-file are mutually exclusive" >&2; exit 2
- File exists but is empty → treat as valid (empty prompt), do not error
- File path with spaces → already handled by quoting "$TASK_FILE" throughout
- The invoke_codex_with_review.sh wrapper does not need changes — it passes --task to the runner, which is populated from the file
   before the runner sees it

  ---
  Fix 6 — Update SKILL.md model routing to match actual usage

  Problem: SKILL.md lists gpt-5.1-codex-mini (simple) and gpt-5.1-codex-max (default), but actual project usage is a 3-tier system:
  mini for simple, gpt-5.4-mini for complex, and user confirmation required before anything larger.

  Changes to SKILL.md:

  Replace the "Choose Model" section under "Using Codex":

  Current:

- Choose Model: `gpt-5.1-codex-mini` (simple and default), `gpt-5.4-mini` (more complex), If a task is too complex for either of
  the mini models, and cannot be broken down into smaller tasks, seek guidance and confirmation from the user before choosing a
  larger model.
  
  Replace with:

- Choose Model:
  - `gpt-5.1-codex-mini` — default for most implementation tasks (single subsystem, clear write set, runnable tests)
  - `gpt-5.4-mini` — for higher-complexity tasks (cross-cutting changes, full-stack wiring, multiple coordinated files)
  - Anything larger: break the task into smaller tickets first. If it genuinely cannot be split, ask the user before proceeding.  

  Also update references/invocation-patterns.md — the "Standard Launch" example comment still says gpt-5.1-codex-max. Change the
  example model in the launch command to gpt-5.1-codex-mini to match the new default.

  - The models available when the user requests a different model or the task requires a different model to be selected include `gpt-5.4` , `gpt-5.4-mini`, `gpt-5.3-codex`, `gpt-5.2`, `gpt-5.1-codex-max`, and `gpt-5.1-codex-mini` - any model other than the two mini miodels require explicit user request or authorization.

  Edge cases:

- Do not remove gpt-5.1-codex-max from the docs entirely — it may still be used for special cases. Just demote it from "default"
  to "requires user confirmation."
- The --model flag in the example command is illustrative only — do not change the script logic, only the docs.

  ---
  Guardrails

- Read every file before editing it.
- Do not change the JSONL record field order beyond what is specified — existing consumers parse by field name but consistent
  ordering helps human readability.
- Do not change the exit behavior of any script — success/failure semantics must be preserved exactly.
- Do not add dependencies outside the Python standard library to any Python script.
- After all edits, verify:
  - python3 /lump/apps/invoke-codex-from-claude/codex-job/scripts/write_delegation_metric.py --help exits 0 and shows the new flags
  - python3 /lump/apps/invoke-codex-from-claude/codex-job/scripts/parse_codex_run.py --help exits 0
  - bash -n /lump/apps/invoke-codex-from-claude/codex-job/scripts/run_codex_task.sh exits 0 (syntax check)
  - bash -n /lump/apps/invoke-codex-from-claude/codex-job/scripts/invoke_codex_with_review.sh exits 0
- Report the exact output of each validation command.
- If any fix conflicts with existing code in a way not anticipated here, stop and describe the conflict rather
than inventing a resolution.

## After implementation is complete

- verify install and uninstall scripts only copy or remove the relevant skill files in ~/.claude/skills/codex-job, not any unrelated files
  - these include SKILL.md, all files in references/, all files in scripts/, and the assets/templates/delegation-metrics-entry.json file
    -rename the install script to install_codex_job_skill.sh and the uninstall script to uninstall_codex_job_skill.sh for clarity

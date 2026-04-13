# Common Delegation Issues and Solutions

Last updated: 2026-04-13

This document addresses recurring problems encountered when delegating work to Codex via this skill.

## Issue 1: Using Non-Existent Flags

### Problem
Delegating agents (both Claude and Codex) sometimes use flags that don't exist in the skill's scripts.

**Examples:**
- `--include-experimental` (only exists in install script, not run script)
- `--provider` (not implemented yet)
- `--timeout` (should be `CODEX_TIMEOUT_SECONDS` env var)

### Solution
**Valid flags for `run_codex_task.sh`:**
```
--repo <path>         (REQUIRED)
--task <text>         (REQUIRED unless --resume)
--task-file <path>    (alternative to --task)
--resume <session>    (for resuming existing sessions)
--tier <low|medium|high>  (model selection tier)
--codex-bin <path>    (override Codex CLI path)
--log-dir <path>      (default: ./runs)
--json-out <path>     (write summary JSON to file)
--notify-cmd <cmd>    (shell command for event notifications)
--event-stream <path> (append event JSONL)
--no-cache            (disable result caching)
--cache-dir <path>    (override cache location)
--summarize           (emit one-line summary)
--summarizer <path>   (custom summarizer script)
-v|-vv|-vvv          (verbosity shortcuts)
--verbosity <level>   (low|normal|high|extreme)
--doctor              (run diagnostics and exit)
--help                (show help)
```

**Flags passed after `--`** go to Codex CLI directly:
```bash
run_codex_task.sh --repo /path --task "Fix bug" -- --model gpt-5.1-codex-mini
                                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                                  These go to Codex, not the wrapper
```

## Issue 2: Confusing Tier-Based and Explicit Model Selection

### Problem
Mixing `--tier` and `--model` flags without understanding the precedence.

### Solution
**Tier-based (recommended):**
```bash
--tier low     # Selects from available_models.jsonl (default: gpt-5.1-codex-mini)
--tier medium  # Selects from available_models.jsonl (default: gpt-5.4-mini)
--tier high    # Selects from available_models.jsonl (requires user authorization)
```

**Explicit model (for testing/compatibility):**
```bash
-- --model gpt-5.1-codex-mini  # Bypasses tier selection, uses specific model
```

**If both are provided:**
- Explicit `--model` wins for execution
- `--tier` is recorded for telemetry only

## Issue 3: Incorrect Script Paths in Delegation Prompts

### Problem
Delegation prompts reference `scripts/` or `tools/` when they should reference `codex-job/scripts/`.

### Solution
**From repository root:**
```bash
codex-job/scripts/run_codex_task.sh
codex-job/scripts/invoke_codex_with_review.sh
codex-job/scripts/write_delegation_metric.py
```

**After skill installation:**
```bash
~/.claude/skills/codex-job/scripts/run_codex_task.sh
# OR use the installed wrappers:
run_codex_task.sh  # If skill's scripts/ is in PATH
```

**Root `scripts/` are wrappers:**
The root `/scripts/` directory contains thin wrappers that delegate to `codex-job/scripts/`. They exist for backwards compatibility but should not be referenced in new delegation prompts.

## Issue 4: Missing Environment Variables

### Problem
Codex invocations fail due to missing required environment variables.

### Solution
**Required:**
```bash
export CODEX_API_KEY="your-api-key"  # Codex CLI authentication
```

**Optional but recommended:**
```bash
export CODEX_WEBHOOK_SECRET="secret"  # For signed webhooks
export CODEX_TIMEOUT_SECONDS=1800     # Override default timeout
export CODEX_CACHE_DIR="/custom/path" # Override cache location
```

**Diagnostic command:**
```bash
codex-job/scripts/run_codex_task.sh --doctor
```

This checks for required commands, environment variables, and connectivity.

## Issue 5: Delegation Scope Creep

### Problem
Delegated agents expand beyond the specified write set or start writing tests without explicit instruction.

### Solution
**In delegation prompt, always include:**

1. **Explicit write set:**
```
Files you may modify:
- src/auth/login.ts
- src/auth/session.ts

Files you must NOT modify:
- Anything in tests/
- Package dependencies
- Config files
```

2. **Test policy:**
```
Do NOT write, edit, or run any test files unless explicitly instructed.
```

3. **Scope boundary:**
```
If you encounter a conflict between these constraints and code reality,
STOP and report the issue. Do not expand scope without authorization.
```

See `codex-job/SKILL.md` § Delegation Guardrails for full policy.

## Issue 6: Resume Session Confusion

### Problem
Trying to resume a run that doesn't have a session ID, or using wrong session identifier.

### Solution
**Check summary JSON for session ID:**
```bash
jq '.sid // .session_id' runs/codex-run-<run_id>.summary.json
```

**Resume with session ID:**
```bash
codex-job/scripts/run_codex_task.sh \
  --repo /path/to/repo \
  --resume <session_id> \
  --task "Follow-up fixes"
```

**Resume latest:**
```bash
codex-job/scripts/run_codex_task.sh \
  --repo /path/to/repo \
  --resume latest \
  --task "Continue work"
```

**Note:** Not all Codex runs create resumable sessions. Check the summary JSON first.

## Issue 7: Hardcoded Model Names in Prompts

### Problem
Delegation prompts reference specific model names that may become outdated.

### Solution
**Bad:**
```
Use gpt-5.1-codex-mini for this task.
```

**Good:**
```
Use tier: low for this task.
```

**Why:** Model names change, get deprecated, or have EOL dates. Tier-based selection uses `codex-job/references/available_models.jsonl` as the single source of truth, making it easy to update models without changing code or prompts.

## Getting Help

If you encounter delegation issues not covered here:
1. Check `codex-job/SKILL.md` for current usage guidance
2. Run `codex-job/scripts/run_codex_task.sh --doctor` for diagnostics
3. Review recent delegation failures in `delegation-metrics.jsonl`
4. Check the run summary JSON for error details

---
name: codex-job
description: Delegate implementation-ready work to Codex (or other providers) with async execution, smart failure handling, and session resume. Invoke via /codex-job.
disable-model-invocation: false
---

# codex-job Skill

Delegate implementation-ready tasks to Codex (or other model providers) with clean fork execution, minimizing Claude token burn.

## When to Use This Skill

**Use when:**
- Acceptance criteria are clear
- Design decisions are finalized  
- Test/verification strategy is defined
- Task is execution-heavy (tests, multi-file changes, refactors, wiring)

**Do NOT use when:**
- Requirements are exploratory or ambiguous
- Architecture/design is still changing
- You need tight real-time interactive iteration

## How This Skill Works

When invoked with `/codex-job`, you (Claude) must:

1. **Parse the skill arguments** to extract:
   - `--repo <path>`: Repository path (REQUIRED)
   - `--task "<text>"`: Task description (REQUIRED unless --resume)
   - `--tier <low|medium|high>`: Model tier (REQUIRED unless --resume)
   - `--provider <openai|anthropic>`: Provider (optional, default: openai)
   - `--resume <session_id|latest>`: Resume mode (mutually exclusive with new task)
   - `--model <model_id>`: Explicit model override (optional)

2. **Execute the Python wrapper** using Bash tool:
   ```bash
   python3 /home/nate/.claude/skills/codex-job/scripts/codex_delegate.py \
     --repo <path> \
     --tier <tier> \
     --task "<task>" \
     [--provider <provider>] \
     [--resume <session_id>] \
     [--model <model_id>]
   ```

3. **The wrapper provides clean output:**
   - Success: "Delegated <ticket> to <model> (<tier>) as fork\nTask <ticket> completed in <time>s"
   - Failure: "Delegated <ticket> to <model> (<tier>) as fork\nTask <ticket> FAILED: <reason>"
   - All verbose execution details are suppressed

## Execution Modes

### New Task Mode
```
/codex-job --repo /path/to/repo --tier high --task "Implement feature X"
```

### Resume Mode
```
/codex-job --repo /path/to/repo --resume latest
/codex-job --repo /path/to/repo --resume 019d8da7-8f1d-7571-97fc-fc94ee1391ed
```

## Model Tier Guidelines

- **Low tier** (`gpt-5.1-codex-mini`): Simple deterministic work, single subsystem, clear write set
  - Example: "Fix typo in error message", "Add validation check"

- **Medium tier** (`gpt-5.4-mini`): Most implementation work (default recommended)
  - Example: "Implement user authentication flow", "Add API endpoint with tests"

- **High tier** (`gpt-5.3-codex`, `gpt-5.4`): Complex reasoning (requires explicit user authorization)
  - Example: "Redesign database schema", "Refactor core architecture"

## Delegation Guardrails

These rules apply to every delegated agent (enforced by guardrail preamble):

- **No tests without explicit instruction**: Agents must not write/edit/run test files unless task explicitly says to
- **Write set is authoritative**: Only touch files listed in task's write set
- **No scope expansion**: If guardrail conflicts with reality, stop and report

## Important Context

**Clean Fork Execution**: The delegated agent gets ONLY:
- The task prompt you provide
- The codebase at --repo path
- Access to codebase-memory-mcp tools

**The delegated agent does NOT get:**
- Your conversation history with the user
- Findings from prior exploration
- Context about why this task exists
- Your thought process or trade-offs

**If the agent needs context beyond the code, you MUST include it explicitly in the task prompt.**

## Example Invocation

When user says:
```
/codex-job --repo /lump/apps/my-project --tier medium --task "Add login endpoint"
```

You must:
1. Parse args: repo=/lump/apps/my-project, tier=medium, task="Add login endpoint"
2. Execute the Python wrapper (suppresses verbose output):
   ```bash
   python3 /home/nate/.claude/skills/codex-job/scripts/codex_delegate.py \
     --repo /lump/apps/my-project \
     --tier medium \
     --task "Add login endpoint"
   ```
3. The wrapper outputs clean status - no need to parse or report further

## Reference Documentation

For detailed information, load these files from skill directory:
- `references/invocation-patterns.md`: Common delegation patterns
- `references/failure-handling.md`: Error recovery strategies
- `references/metrics-schema.md`: Summary JSON format
- `references/available_models.jsonl`: Model registry

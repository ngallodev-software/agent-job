---
name: codex-job
description: Delegate implementation-ready work to Codex with async execution, smart failure handling, and session resume. Invoke via /codex-job.
disable-model-invocation: false
---

# Purpose

Use `/codex-job` to offload implementation-ready tasks to Codex while minimizing Claude token burn.

## Use When

- Acceptance criteria are clear.
- Design decisions are finalized.
- Test/verification strategy is defined.
- Task is execution-heavy (tests, multi-file changes, refactors, wiring).

## Do Not Use When

- Requirements are exploratory or ambiguous.
- Architecture/design is still changing.
- You need tight real-time interactive iteration.

## Delegation Guardrails

These rules apply to every delegated agent unless the task prompt explicitly overrides them:

- **No tests without explicit instruction.** Delegated agents must not write, edit, or run any test files unless the task prompt explicitly says to. This includes `tests/`, `test_*.py`, `*.spec.ts`, `*.test.ts`, and any other test file patterns.
- **Write set is authoritative.** The agent must only touch files listed in the task's write set. Any file outside that set is off-limits.
- **No scope expansion.** If a guardrail conflicts with code reality, the agent must stop and report before broadening scope.

## Core Workflow

1. Validate readiness (all four checks above must pass).
2. Choose model tier and provider:
   - Models are defined in `codex-job/references/available_models.jsonl`
   - Select by **tier** (low/medium/high) and let the skill choose the current best model
   - **Low tier**: Simple deterministic work (default: gpt-5.1-codex-mini)
     - Single subsystem, clear write set, runnable tests
   - **Medium tier**: Most implementation work (default: gpt-5.4-mini)
     - Cross-cutting changes, full-stack wiring, multiple coordinated files
   - **High tier**: Complex reasoning (requires explicit user authorization)
     - Anything larger: break the task into smaller tickets first
     - If it genuinely cannot be split, ask the user before proceeding
   - Provider choice: OpenAI (Codex GPT models) or Anthropic (Claude models)
   - The skill will select the appropriate model based on tier and provider from available_models.jsonl

3. Launch with: `scripts/invoke_codex_with_review.sh --repo <path> --task "<task>" --tier <low|medium|high>`
   - Prefer `--notify-cmd "scripts/notify_terminal.sh"` for feedback
   - Note: `scripts/` paths are skill-local runtime scripts
   - Override with `--model <model_id>` if you need a specific model (tier is recorded for telemetry)

4. Read summary JSON on completion; verify if risk/impact requires it.
5. If additional fixes are needed, resume with `--resume <session_id>` or `--resume latest`.
6. Append metrics using `scripts/write_delegation_metric.py`.

## Execution Mode: Fork vs Subagent

### Use Forked Codex Session (this skill)
- Task is **fully specified** in a ticket/prompt (no conversation context needed)
- Implementation-heavy: writing code, running tests, multi-file refactors
- Can run async/background while you continue other work
- Want to minimize Claude token burn on execution work
- Task can be defined with clear acceptance criteria and constraints

### Use Codex Subagent (via Agent tool)
- Task needs **findings from current conversation** to proceed
- Research/exploration where results inform your next steps
- Code review requiring independent analysis  
- Need synchronous results to make next decision
- Judgment calls depend on conversation context

## Required Tracking

For each delegation:
- Append a brief entry to `work-log.md`.
- Append a detailed JSONL record to `delegation-metrics.jsonl`.
- Keep Claude and Codex token fields separate.

If rolling success rate for a task type drops below 70% (excluding environmental failures), tighten specs and reduce delegation scope until metrics recover.

## Quick Output Pattern

After launch, report:
- run id
- log path
- summary path (or pending)
- session id availability

## References

Load only what you need:
- `references/invocation-patterns.md`
- `references/failure-handling.md`
- `references/metrics-schema.md`
- `references/available_models.jsonl` (model registry)
- `assets/templates/delegation-metrics-entry.json`

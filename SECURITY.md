# Security Model

This repository currently supports two distinct paths:

- `agent-job`: Copilot/manual packaging plus mock execution
- `codex-job`: legacy local Codex runtime

This document is about the active safety model for `agent-job`, especially the Copilot package workflow.

## Copilot Package Mode

`agent-job package ... --target copilot` does not execute Copilot.

It only writes a work package for a human to use in an approved Copilot environment:

- `job.input.yaml`
- `prompt.copilot.md`
- `checklist.md`
- `report-template.md`
- `meta.json`

Expected metadata for this mode:

```json
{
  "mode": "package",
  "target": "copilot",
  "executor": null,
  "launched_by_tool": false,
  "process_success": null,
  "exit_code": null,
  "human_review_required": true
}
```

Security properties of this path:

- no Codex auth required
- no Codex command launched
- no Claude command launched
- no Copilot automation attempted
- no auto-commit
- no auto-push
- human review required before any commit decision

## Scope and Validation

`agent-job` enforces:

- fail-closed YAML schema validation
- absolute `repo_path`
- repo-relative `allowed_paths`
- repo-relative `forbidden_paths`
- rejection of path traversal via `..`
- default protection for `.git/`, `.env`, `.env.local`, `.env.*`, and `node_modules/`

Package mode does not itself enforce filesystem writes because it does not execute the engineering task. It communicates the scope and constraints to the external Copilot/manual environment and requires human review of the resulting diff.

## Provenance

For `agent-job`, provenance is agent-neutral:

- `claimed_by_agent`
- `claimed_by_executor`
- `observed`
- `declared_by_job`
- `inferred`
- `not_captured`
- `not_run`
- `unknown`

Copilot package mode is intentionally honest:

- it does not claim the task was completed
- it does not fabricate process exit codes
- it does not mark Copilot work as tool-observed execution

## Secrets and Auth

Copilot package mode does not require Codex credentials.

The Copilot model sync pipeline under `agent-job/references/copilot/` may require:

- `GITHUB_TOKEN`
- `GH_TOKEN`
- or a usable local Copilot SDK session

Do not commit tokens, raw secrets, or personal auth artifacts.

## Not Supported

These are not part of the trusted Copilot production-test path:

- `agent-job run --executor copilot`
- `agent-job run --executor codex`
- any assumption that package mode completed the engineering work
- any auto-commit or auto-push workflow

Use `agent-job render/package` for Copilot/manual preparation and treat all resulting changes as requiring human review.

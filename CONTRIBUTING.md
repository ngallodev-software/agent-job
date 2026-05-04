# Contributing to agent-job

Keep changes small, reviewable, and honest about what the tool actually does.

Current repo direction:

- `agent-job` is the forward path for Copilot/manual packaging
- `codex-job` remains the legacy live Codex runtime

Do not blur those two identities in docs or code.

## Workflow Expectations

- Treat `agent-job` package mode as the primary production-facing workflow.
- Keep `codex-job` changes isolated to legacy Codex execution work.
- Do not claim execution support that is not implemented.
- Update docs when you add or remove commands, schema fields, or install/bootstrap steps.
- Keep commits descriptive and explicit about user-facing impact.

## Coding Standards

- Bash: use `set -euo pipefail`, prefer functions, avoid destructive git commands, keep errors non-sensitive.
- Python: keep scripts runnable with `python3`, prefer standard library where practical, add comments only where logic is not obvious.
- JSON/YAML contracts: fail closed, avoid implicit magic, document field changes in README and tests.

## Testing

Run relevant checks from the repo root before opening a PR.

Core `agent-job` checks:

- `bash tests/test_agent_job_cli.sh`
- `bash tests/test_contract_schemas.sh`
- `bash tests/test_install_dry_run.sh`

Legacy `codex-job` checks when touching legacy runtime files:

- `bash tests/test_runner_and_parser.sh`
- `bash tests/test_invoke_and_notify.sh`
- `bats tests/test_run_codex_task.bats`

If you change install/bootstrap flows, extend or rerun `tests/test_install_dry_run.sh`.

## Documentation Requirements

- [README.md](/lump/apps/invoke-codex-from-claude/README.md) must describe the supported `agent-job` path accurately.
- [agent-job/README.md](/lump/apps/invoke-codex-from-claude/agent-job/README.md) must stay aligned with the current CLI behavior.
- If you touch Copilot model selection, update:
  - `agent-job/references/copilot/README.md`
  - `agent-job/references/copilot/available-models.md` when override guidance changes
- If you touch legacy Codex behavior, keep the docs explicit that it is legacy/runtime-specific.

## Pull Request Checklist

- [ ] Relevant tests pass and are summarized in the PR.
- [ ] README/CONTRIBUTING/docs updated for user-facing changes.
- [ ] No hardcoded secrets or personal auth artifacts are committed.
- [ ] Copilot package mode remains honest about non-execution.
- [ ] No unsupported executor/renderer path is presented as working.

## Local Install for Development

Forward `agent-job` bootstrap:

- `./install_agent_job.sh`
- `./install_agent_job.sh --dry-run`
- `./uninstall_agent_job.sh`

Legacy `codex-job` skill install:

- `./install_codex_job_skill.sh --scope project`
- `./uninstall_codex_job_skill.sh --scope project`

## Support Notes

- Use `agent-history.log` only for concise coordination notes if needed.
- Prefer deleting stale docs over layering new claims on top of them.

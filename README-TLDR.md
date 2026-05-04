# agent-job (TLDR)

Fast path for the current forward workflow.

## 1) Install agent-job

```bash
./install_agent_job.sh
agent-job --help
```

Preview only:

```bash
./install_agent_job.sh --dry-run
```

## 2) Sync Copilot models for the current user

```bash
npm install
npm run copilot:models:sync
```

This writes the user-specific Copilot model registry used by `agent-job`.

## 3) Validate and package a Copilot job

```bash
agent-job validate examples/v2/copilot-docs.job.yaml
agent-job package examples/v2/copilot-docs.job.yaml --target copilot
```

Then:

1. open `runs/<job-id>/<timestamp>-copilot-package/prompt.copilot.md`
2. paste it into the approved Copilot environment
3. complete `report-template.md`
4. review the diff manually

## 4) What this does not do

- does not launch Copilot
- does not launch Claude
- does not require Codex auth for package mode
- does not auto-commit
- does not auto-push

## 5) Legacy Codex runtime

If you need live local Codex execution, use the legacy path:

```bash
./install_codex_job_skill.sh --scope project
codex-job run examples/bugfix.job.yaml
```

## 6) Uninstall agent-job bootstrap

```bash
./uninstall_agent_job.sh
```

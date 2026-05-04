---
name: agent-job
description: Use when you need to define, validate, package, or review bounded engineering work with the agent-job contract for Copilot-first workflows. Prefer this for scoped implementation, bugfix, refactor, docs, test, or analysis tasks that need explicit allowed paths, constraints, acceptance criteria, and human review.
---

# agent-job

Use this skill for bounded engineering work that should be turned into a validated `agent-job` contract and, when needed, packaged for GitHub Copilot.

## When to use

- The user wants a scoped work order for Copilot.
- The task needs explicit allowed paths or forbidden paths.
- The task needs acceptance criteria and reviewable completion output.
- The user wants to compare baseline prompting against structured prompting.

Do not use this skill for:

- direct Copilot automation
- autonomous commit/push workflows
- live Codex execution through `agent-job`

For live local Codex execution, use the legacy `codex-job` runtime instead.

## First checks

1. Confirm `agent-job` is installed:

   ```bash
   agent-job --help
   ```

2. If it is missing, bootstrap it with the bundled script:

   ```bash
   bash scripts/install-agent-job.sh
   ```

3. If the user wants Copilot model selection refreshed after install:

   ```bash
   cd ~/.local/share/agent-job
   npm install
   npm run copilot:models:sync
   ```

## Default workflow

1. Create or update a schema v2 `*.job.yaml` file.
2. Validate it:

   ```bash
   agent-job validate <job.job.yaml>
   ```

3. Package it for Copilot:

   ```bash
   agent-job package <job.job.yaml> --target copilot
   ```

4. Use the generated package artifacts:
   - `prompt.copilot.md`
   - `checklist.md`
   - `report-template.md`
   - `meta.json`

5. Keep human review in the loop.

## Guardrails

- Do not claim `agent-job run --executor copilot` is supported.
- Do not claim `agent-job render --target claude` or `--target codex` is implemented.
- Treat package mode as the canonical Copilot path.
- Keep job scope narrow and acceptance criteria explicit.
- Prefer `execution.model` if the user specifies a model.
- Otherwise prefer `execution.model_tier` and registry-backed defaults.

## Job shape

Every job should define:

- `task.objective`
- `task.constraints`
- `task.acceptance_criteria`
- `scope.allowed_paths`
- `scope.forbidden_paths`
- `output_contract`
- `provenance`

If any of these are vague, tighten them before packaging.

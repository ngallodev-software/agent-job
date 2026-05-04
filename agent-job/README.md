# agent-job: Universal Agent Job Contract

**Status**: Phase A MVP - Core functionality complete, documentation in progress

## What This Is

`agent-job` is an engineering job contract system that currently supports:

- **Copilot workflows**: Package work for GitHub Copilot Chat/Workspace
- **Manual workflows**: Generate human-readable work orders for any approved tool
- **Mock testing**: Test workflows without external dependencies

## What This Is Not

- Not a finished multi-executor runtime
- Not a production platform, queue, or dashboard
- Not an autonomous coding system
- Not a tool that auto-commits or auto-pushes
- Not a Copilot automation bypass (package mode only)

## Quick Start

### Installation (Phase A - Manual)

```bash
# Bootstrap a local command
./install_agent_job.sh

# Then verify
agent-job --help
```

One-command remote install:

```bash
curl -fsSL https://raw.githubusercontent.com/ngallodev-software/agent-job/main/install_agent_job_remote.sh | bash
```

Copilot-native skill install:

```bash
gh skill preview ngallodev-software/agent-job agent-job --allow-hidden-dirs
gh skill install ngallodev-software/agent-job agent-job --allow-hidden-dirs
```

The installed skill includes a bundled bootstrap script that can fetch the minimal CLI payload without cloning the full repository.

Direct invocation also works:

```bash
python3 ./agent-job/scripts/agent-job --help
```

### Validate a Job

```bash
agent-job validate examples/v2/copilot-docs.job.yaml
```

### Create a Copilot Package

```bash
agent-job package examples/v2/copilot-docs.job.yaml --target copilot
```

This creates:
- `runs/<job-id>/<timestamp>-copilot-package/prompt.copilot.md` - Paste into Copilot
- `runs/<job-id>/<timestamp>-copilot-package/checklist.md` - Review checklist
- `runs/<job-id>/<timestamp>-copilot-package/report-template.md` - Completion template

Then:
1. Open `prompt.copilot.md`
2. Copy to GitHub Copilot Chat or Copilot Workspace
3. Execute the work in that environment
4. Fill out `report-template.md`
5. Review changes and decide whether to commit

### Copilot Eval Suite Quick Start

The eval suite runs from a local checkout of this repository.

Install for Copilot:

```bash
gh skill preview ngallodev-software/agent-job agent-job --allow-hidden-dirs
gh skill install ngallodev-software/agent-job agent-job --allow-hidden-dirs
curl -fsSL https://raw.githubusercontent.com/ngallodev-software/agent-job/main/install_agent_job_remote.sh | bash
```

Run one eval task from the repo checkout:

```bash
python3 evals/copilot-run/self_check.py
TASK=01-docs-consistency
./agent-job/scripts/agent-job validate evals/copilot-run/tasks/$TASK/agent-job.job.yaml
./agent-job/scripts/agent-job package evals/copilot-run/tasks/$TASK/agent-job.job.yaml --target copilot
cat runs/*/*-copilot-package/prompt.copilot.md
```

Then use:

- `evals/copilot-run/tasks/$TASK/baseline-prompt.md`
- the generated `runs/.../prompt.copilot.md`
- `evals/copilot-run/tasks/$TASK/evaluator-prompt.md`

to run the baseline pass, the `agent-job` pass, and the comparison.

### Install and Refresh Copilot Models

`agent-job` ships with a Copilot model registry pipeline because the available model list is user-specific.

From the repo root:

```bash
npm install
npm run copilot:models:sync
```

If you installed with the remote bootstrap script, use the installed payload root:

```bash
cd ~/.local/share/agent-job
npm install
npm run copilot:models:sync
```

This writes:
- `agent-job/references/copilot/available_models.raw.json`
- `agent-job/references/copilot/available-models.template.json`
- `agent-job/references/copilot/available_models.copilot.jsonl`

Customize preferred models by editing:
- `agent-job/references/copilot/available-models.md`

Then rerun:

```bash
npm run copilot:models:sync
```

See [Copilot Model Registry README](./references/copilot/README.md).

### Render a Prompt

```bash
# Copilot-ready prompt
agent-job render examples/v2/copilot-docs.job.yaml --target copilot

# Human work order
agent-job render examples/v2/manual-refactor.job.yaml --target manual

```

### Run with Mock Executor

```bash
agent-job run examples/v2/mock-test.job.yaml --executor mock
```

### View a Report

```bash
agent-job report runs/<job-id>/<run-id>/
```

## Supported Modes

| Mode | Target/Executor | Tool Launches Executor? | Use Case |
|---|---|:---:|---|
| **render** | copilot | No | Generate Copilot-ready prompt |
| **render** | manual | No | Generate human work order |
| **package** | copilot | No | Create Copilot work package |
| **package** | manual | No | Create manual work package |
| **run** | mock | Yes | Test without external dependencies |
| **report** | any | No | Review run or package artifacts |

## Job Schema v2

Schema v2 is executor-neutral and organized into logical sections:

```yaml
schema_version: 2
id: JOB-2026-05-03-001
title: Job title
repo_path: /absolute/path
branch: null

task:
  type: implementation | bugfix | refactor | test | docs | analysis
  objective: What to accomplish
  context: Background information
  constraints:
    - Rule 1
    - Rule 2
  acceptance_criteria:
    - Criterion 1
    - Criterion 2

scope:
  allowed_paths:
    - src/
    - tests/
  forbidden_paths:
    - .git/
    - .env

execution:
  mode: agent | human | ci
  preferred_executor: copilot | human | codex | mock
  model: optional-model-id
  model_tier: very-low | low | medium | high
  allowed_executors:
    - copilot
    - human
  disallowed_executors: []
  commands_allowed:
    - python3
    - git
  commands_forbidden:
    - git push
    - rm -rf
  test_commands:
    - pytest

output_contract:
  require_summary: true
  require_changed_files: true
  require_tests_run: true
  require_risks: true
  human_review_required: true

provenance:
  distinguish_agent_claims: true
  require_changed_file_snapshot: true
  require_test_evidence: true

created_by: human
created_at: 2026-05-03T00:00:00Z
```

See `examples/v2/` for complete examples.

Model selection rule:

- if `execution.model` is set, use it
- otherwise use `execution.model_tier` if provided
- otherwise choose the registry-backed default for Copilot packaging, preferring `medium` then `low`

## Schema v1 Compatibility

Schema v1 jobs are auto-migrated to v2 with deprecation warnings:

```bash
$ agent-job validate examples/bugfix.job.yaml
warning: schema v1 is deprecated; migrate to schema v2
valid: JOB-EXAMPLE-BUGFIX
```

## Commands Reference

### validate

Validate a job file without execution.

```bash
agent-job validate <job.job.yaml>
```

### render

Render job to target-specific prompt.

```bash
agent-job render <job.job.yaml> --target <copilot|manual>
```

**Targets**:
- `copilot`: GitHub Copilot Chat/Workspace prompt
- `manual`: Human-readable work order
- `codex`: Not yet implemented in `agent-job`; use `codex-job`
- `claude`: Not yet implemented in `agent-job`

### package

Create work package without execution.

```bash
agent-job package <job.job.yaml> --target <copilot|manual>
```

**Targets**:
- `copilot`: Copilot work package
- `manual`: Manual work package

**Output**: `runs/<job-id>/<timestamp>-<target>-package/`

### run

Execute job via specified executor.

```bash
agent-job run <job.job.yaml> --executor <mock> [--dry-run]
```

**Executors**:
- `mock`: Mock executor (always available)
- `codex`: Not yet implemented in `agent-job`; use `codex-job`

**Note**: use `package --target copilot` for Copilot and `codex-job` for live Codex execution.

### report

Print report for a run or package.

```bash
agent-job report <run-dir>
```

## Copilot Workflow

1. **Create a job file** (schema v2, `preferred_executor: copilot`)
2. **Package**: `agent-job package job.yaml --target copilot`
3. **Open prompt**: `runs/<job-id>/<timestamp>-copilot-package/prompt.copilot.md`
4. **Copy to Copilot**: Paste into GitHub Copilot Chat or Workspace
5. **Execute in Copilot**: Let Copilot perform the work
6. **Fill report**: Document results in `report-template.md`
7. **Review**: Check diff, verify acceptance criteria
8. **Decide**: Commit if acceptable, iterate if not

## Copilot Model Registry

The canonical Copilot model registry is:

- `agent-job/references/copilot/available_models.copilot.jsonl`

Why this exists:

- available Copilot models differ by user, org policy, and subscription
- the raw Copilot SDK response is too noisy for normal selection use
- the override layer lets each user mark preferred models without editing runtime code

The skill should primarily read these fields:

- `model_id`
- `tier`
- `recomended`
- `token_cost_multiplier`
- `policy_state`
- `supported_reasoning_efforts`
- `default_reasoning_effort`

Selection guidance:

1. require `policy_state == "enabled"`
2. prefer `recomended == true`
3. then choose by `tier`
4. check reasoning-effort support only when the task needs it

## Provenance Model

The system distinguishes between:

- **observed**: Runner captured via git/fs/process
- **declared_by_job**: Job file specified
- **claimed_by_agent**: Agent reported (e.g., Copilot, Codex, mock)
- **claimed_by_executor**: Executor wrapper reported
- **inferred**: Derived from other data
- **not_captured**: Runner could not capture
- **not_run**: Not executed
- **unknown**: Indeterminate

Package mode (`launched_by_tool: false`) honestly reports non-execution:
- `process_success: null`
- `exit_code: null`
- No fabricated observations

## Safety Model

- Strict schema validation (fail-closed)
- Absolute repo paths required
- Allowed/forbidden path enforcement (prompt-based)
- No auto-commit, no auto-push
- Human review required
- Package mode honest about non-execution
- No Copilot automation bypass

## Architecture

```
agent-job/
  scripts/
    agent-job              # Entrypoint
    agent_job_cli.py       # Universal CLI
    schema.py              # Schema v1 & v2
  executors/
    base_executor.py       # Abstract interface
    mock_executor.py       # Mock for testing
    codex_executor.py      # Codex placeholder
  renderers/
    base_renderer.py       # Abstract interface
    copilot_renderer.py    # Copilot prompts
    manual_renderer.py     # Human work orders
    codex_renderer.py      # Codex placeholder prompts
```

## Migration from codex-job

`agent-job` is the forward path for Copilot/manual workflows. `codex-job` remains the live Codex runtime for now. Key differences:

| Feature | codex-job | agent-job |
|---|---|---|
| Identity | Codex-specific | Executor-neutral |
| Schema | v1 (flat) | v2 (structured) |
| Copilot support | No | Yes (package mode) |
| Manual support | No | Yes (package mode) |
| Provenance | `claimed_by_codex` | `claimed_by_agent` |
| Auth requirement | Always | None for package/mock paths |
| Render targets | One (Codex) | Copilot and manual today |

**Migration path**:
1. Convert v1 jobs to v2 (or use auto-migration)
2. Use `agent-job` for Copilot/manual workflows
3. Use `agent-job --executor mock` for testing
4. Use `codex-job` for Codex execution
5. Treat `agent-job` Codex and Claude paths as not yet implemented

## Known Limitations (Phase A)

- Codex executor: Not yet implemented
- Completion ingestion: Not implemented
- Claude renderer: Not implemented
- Git integration: Not yet migrated
- Runner-managed tests: Not yet migrated
- Path policy observation: Prompt-based only

## Roadmap

- **Phase B**: Complete Codex executor migration
- **Phase C**: Completion ingestion for package workflows
- **Phase D**: Documentation overhaul
- **Phase E**: Deprecate `codex-job`, create wrapper

## License

See repository LICENSE file.

## Contributing

Phase A is MVP status. Contributions welcome after stabilization.

## Support

For issues or questions, see repository issue tracker.

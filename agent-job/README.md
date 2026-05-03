# agent-job: Universal Agent Job Contract

**Status**: Phase A MVP - Core functionality complete, documentation in progress

## What This Is

`agent-job` is a universal, executor-neutral engineering job contract system that supports:

- **Copilot workflows**: Package work for GitHub Copilot Chat/Workspace
- **Manual workflows**: Generate human-readable work orders for any approved tool
- **Codex workflows**: Local Codex execution (adapter mode)
- **Mock testing**: Test workflows without external dependencies

## What This Is Not

- Not Codex-specific (Codex is one executor adapter among several)
- Not a production platform, queue, or dashboard
- Not an autonomous coding system
- Not a tool that auto-commits or auto-pushes
- Not a Copilot automation bypass (package mode only)

## Quick Start

### Installation (Phase A - Manual)

```bash
# Add agent-job to PATH
export PATH="/lump/apps/invoke-codex-from-claude/agent-job/scripts:$PATH"

# Or use directly
python3 /lump/apps/invoke-codex-from-claude/agent-job/scripts/agent-job --help
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

### Render a Prompt

```bash
# Copilot-ready prompt
agent-job render examples/v2/copilot-docs.job.yaml --target copilot

# Human work order
agent-job render examples/v2/manual-refactor.job.yaml --target manual

# Codex adapter prompt
agent-job render examples/v2/copilot-docs.job.yaml --target codex
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
| **render** | codex | No | Generate Codex adapter prompt |
| **package** | copilot | No | Create Copilot work package |
| **package** | manual | No | Create manual work package |
| **run** | mock | Yes | Test without external dependencies |
| **run** | codex | Yes | Local Codex execution (stub in Phase A) |
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

## Schema v1 Compatibility

Schema v1 jobs are auto-migrated to v2 with deprecation warnings:

```bash
$ agent-job validate examples/bugfix.job.yaml
warning: schema v1 is deprecated; migrate to schema v2
warning: ignoring v1 model_tier (Codex-specific, not in v2 schema)
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
agent-job render <job.job.yaml> --target <copilot|manual|codex|claude>
```

**Targets**:
- `copilot`: GitHub Copilot Chat/Workspace prompt
- `manual`: Human-readable work order
- `codex`: Codex adapter prompt
- `claude`: Not yet implemented

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
agent-job run <job.job.yaml> --executor <codex|mock> [--dry-run]
```

**Executors**:
- `mock`: Mock executor (always available)
- `codex`: Codex executor (Phase A: dry-run only)

**Note**: `--executor copilot` is not supported. Use `package --target copilot` instead.

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
    codex_executor.py      # Codex adapter
  renderers/
    base_renderer.py       # Abstract interface
    copilot_renderer.py    # Copilot prompts
    manual_renderer.py     # Human work orders
    codex_renderer.py      # Codex adapter prompts
```

## Migration from codex-job

`agent-job` is the universal successor to `codex-job`. Key differences:

| Feature | codex-job | agent-job |
|---|---|---|
| Identity | Codex-specific | Executor-neutral |
| Schema | v1 (flat) | v2 (structured) |
| Copilot support | No | Yes (package mode) |
| Manual support | No | Yes (package mode) |
| Provenance | `claimed_by_codex` | `claimed_by_agent` |
| Auth requirement | Always | Only for Codex executor |
| Render targets | One (Codex) | Multiple (Copilot, manual, Codex) |

**Migration path**:
1. Convert v1 jobs to v2 (or use auto-migration)
2. Use `agent-job` for Copilot/manual workflows
3. Use `agent-job --executor mock` for testing
4. Use `codex-job` for Codex execution (Phase A)
5. Switch to `agent-job --executor codex` after full migration (future)

## Known Limitations (Phase A)

- Codex executor: Dry-run only (full execution pending migration)
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

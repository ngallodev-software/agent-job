# Current Architecture

## Overview

The repository contains two CLI systems:

1. **agent-job** (recommended): Copilot/manual forward path with mock testing
2. **codex-job** (legacy but active): Codex-specific runtime

Both can coexist. New work should use `agent-job` for Copilot/manual workflows and `codex-job` for live Codex execution.

## agent-job: Universal Architecture

### Canonical Runtime

The universal CLI:

- `agent-job/scripts/agent-job` - Entrypoint
- `agent-job/scripts/agent_job_cli.py` - Universal CLI (420 lines)
- `agent-job/scripts/schema.py` - Schema v1 & v2 validation (500+ lines)

### Architecture Layers

```
┌─────────────────────────────────────────────────┐
│         Universal Core Layer                    │
│  - Schema v2 validation                         │
│  - Job contract enforcement                     │
│  - Path policy                                  │
│  - Provenance model                             │
└─────────────────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────┐
│         Renderer Layer                          │
│  - Copilot renderer (copilot_renderer.py)      │
│  - Manual renderer (manual_renderer.py)         │
│  - Codex/Claude placeholders (not implemented)  │
│  - Base interface (base_renderer.py)            │
└─────────────────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────┐
│         Executor Layer                          │
│  - Mock executor (mock_executor.py)             │
│  - Codex executor placeholder (not implemented) │
│  - Base interface (base_executor.py)            │
└─────────────────────────────────────────────────┘
```

### Core Flow

#### Package Mode (Copilot/Manual)

1. Load and validate `*.job.yaml` (schema v1 or v2)
2. Render target-specific prompt (Copilot/manual)
3. Create artifact directory: `runs/<job-id>/<timestamp>-<target>-package/`
4. Write package files:
   - `job.input.yaml` - Original job spec
   - `prompt.<target>.md` - Rendered prompt
   - `checklist.md` - Review checklist
   - `report-template.md` - Completion template
   - `meta.json` - Package metadata
5. Print next steps for human
6. **No execution** - `launched_by_tool: false`

#### Run Mode (Mock)

1. Load and validate `*.job.yaml`
2. Get executor instance (mock)
3. Check executor can execute job (allowed_executors)
4. Create run directory: `runs/<job-id>/<timestamp>-<executor>-run/`
5. Execute via executor
6. Write artifacts:
   - `job.input.yaml`
   - `run.log`
   - `meta.json`
   - `report.json`
7. Print report summary

### Artifacts

#### Package Mode

```
runs/<job-id>/<timestamp>-<target>-package/
  job.input.yaml
  prompt.<target>.md
  checklist.md
  report-template.md
  meta.json (launched_by_tool: false)
```

#### Run Mode

```
runs/<job-id>/<timestamp>-<executor>-run/
  job.input.yaml
  run.log
  meta.json (launched_by_tool: true)
  report.json
```

### Provenance Model

Universal categories:

- `observed` - Runner captured via git/fs/process
- `declared_by_job` - Job file specified
- `claimed_by_agent` - Agent reported (Copilot, Codex, mock, etc.)
- `claimed_by_executor` - Executor wrapper reported
- `inferred` - Derived from other data
- `not_captured` - Runner could not capture
- `not_run` - Not executed
- `unknown` - Indeterminate

### Executor Adapters

#### Mock Executor

**Purpose**: Testing without external dependencies

**Features**:
- Always available (no auth)
- Predictable output
- Proper provenance structure
- Useful for workflow testing

#### Codex Executor Adapter

**Purpose**: Local Codex CLI execution (isolated adapter)

**Status (Phase A)**: Stub implementation
- Dry-run works
- Auth check works
- Full execution pending migration

**Location**: `agent-job/executors/codex_executor.py`

### Renderer Targets

#### Copilot Renderer

**Target**: GitHub Copilot Chat, Copilot Workspace

**Output**: Markdown prompt with:
- Job metadata
- Clear scope (allowed/forbidden paths)
- Constraints and acceptance criteria
- Required evidence template
- Safety rules (no auto-commit, distinguish facts from claims)

**Critical**: No Codex mentions, no implied direct execution

#### Manual Renderer

**Target**: Human developers using any approved tool

**Output**: Human-readable work order with:
- "What to do" and "what success looks like"
- Suggested workflow
- Review checklist
- Completion report template

#### Codex/Claude Placeholders

**Status**: Not yet implemented in `agent-job`

These code paths exist as placeholders only. Live Codex execution still belongs to `codex-job`.

### Schema v2

**Structure**:
- `task` - What to accomplish
- `scope` - Where changes are allowed
- `execution` - How and by whom
- `output_contract` - What to report
- `provenance` - What to capture

**Executor metadata**:
- `preferred_executor` - Guidance only
- `allowed_executors` - Whitelist
- `disallowed_executors` - Blacklist

**No Codex-specific fields**: `model_tier`, `model` removed

### Compatibility Surface

- Schema v1 auto-migrates to v2 with warnings
- Both CLIs can coexist
- No forced migration

## codex-job: Legacy Architecture

### Canonical Runtime

The Codex-specific CLI:

- `codex-job/scripts/codex-job`
- `codex-job/scripts/codex_job_cli.py` (1179 lines)
- `codex-job/scripts/codex_job_support.py`

### Core Flow

1. Load and validate `*.job.yaml` (schema v1)
2. Render Codex-specific prompt
3. Optionally dry-run
4. Invoke `codex exec` in target repo
5. Capture git state before/after
6. Optionally run `test_commands` with `--run-tests`
7. Write artifacts under `runs/<job-id>/<run-id>/`
8. Print provenance-aware report

### Artifacts

Per run:

- `job.input.yaml`
- `prompt.rendered.md`
- `run.log`
- `meta.json`
- `report.json`
- `report.md`
- `tests/test-<n>.log` (when `--run-tests`)

### Provenance Model

Categories:

- observed facts
- job-declared requirements
- **Codex claims** (`claimed_by_codex`)
- inferences
- not-captured data
- not-run checks

**Different from agent-job**: Uses `claimed_by_codex` instead of `claimed_by_agent`

### Status

**Fully functional**: Unchanged by Phase A

**Recommended for**:
- Existing codex-job workflows
- Codex execution (until agent-job Codex executor is fully migrated)

**Not recommended for**:
- New workflows (use agent-job)
- Copilot workflows (not supported)
- Executor-neutral validation

## Comparison

| Feature | agent-job | codex-job |
|---|---|---|
| **Identity** | Executor-neutral | Codex-specific |
| **Schema** | v1 (auto-migrated) & v2 | v1 only |
| **Copilot support** | Yes (package mode) | No |
| **Manual support** | Yes (package mode) | No |
| **Mock executor** | Yes | No |
| **Codex execution** | Not yet implemented | Yes (full) |
| **Provenance** | `claimed_by_agent` | `claimed_by_codex` |
| **Auth requirement** | None for package/mock paths | Always |
| **Render targets** | Copilot and manual today | One (Codex) |
| **Package mode** | Yes | No |
| **Lines of code** | ~3000 (modular) | ~1200 (monolithic) |

## Non-Core Optional Helpers

- `tools/optional/check_model_eol.py` - Model EOL checker
- `tools/optional/phase-6.5-prompt.md` - Pivot design prompt
- `tools/optional/README.md` - Optional tools documentation

## Explicitly Out of Scope

Both architectures:

- Queueing
- Dashboards
- Orchestration control planes
- Provider fanout beyond explicit adapters
- Auto-commit or auto-push
- Autonomous coding
- Direct Copilot execution/automation bypass

## Migration Path

1. **Phase A (current)**: agent-job available, codex-job unchanged
2. **Phase B (next)**: Full Codex executor migration to agent-job
3. **Phase C (future)**: codex-job deprecated wrapper (optional)
4. **Phase D (far future)**: codex-job removal (if consensus)

**No forced timeline**: Both CLIs coexist indefinitely if needed.

## Directory Structure

```
invoke-codex-from-claude/
  agent-job/                    # Universal architecture
    scripts/
      agent-job
      agent_job_cli.py
      schema.py
    executors/
      base_executor.py
      mock_executor.py
      codex_executor.py
    renderers/
      base_renderer.py
      copilot_renderer.py
      manual_renderer.py
      codex_renderer.py
    references/
      available_models.jsonl
    README.md

  codex-job/                    # Legacy Codex-specific
    scripts/
      codex-job
      codex_job_cli.py
      codex_job_support.py
    references/
      invocation-patterns.md
      common-delegation-issues.md
    SKILL.md

  examples/
    v2/                         # Schema v2 (agent-job)
      copilot-docs.job.yaml
      manual-refactor.job.yaml
      mock-test.job.yaml
    *.job.yaml                  # Schema v1 (codex-job, auto-migrated)

  docs/
    current-architecture.md     # This file
    migration-from-codex-job.md
    safety-model.md
    phase-a-implementation-report.md

  tools/
    optional/
      phase-6.5-prompt.md
      README.md
```

## For More Information

- **agent-job**: See `agent-job/README.md`
- **codex-job**: See `codex-job/` directory
- **Migration**: See `docs/migration-from-codex-job.md`
- **Safety**: See `docs/safety-model.md`
- **Phase A**: See `docs/phase-a-implementation-report.md`

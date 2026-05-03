# agent-job: Universal Agent Job Contract

A universal, executor-neutral engineering job contract system that supports Copilot, manual, and Codex workflows with strict validation, bounded scope, and human review.

## What This Is

- **Universal job contract**: Executor-neutral job specifications for bounded engineering work
- **Multi-executor support**: Works with GitHub Copilot, manual workflows, local Codex, or mock testing
- **Package mode**: Create work packages for Copilot/manual execution without tool-launched agents
- **Strict validation**: Fail-closed schema validation with clear error messages
- **Artifact capture**: Deterministic provenance tracking and human review artifacts
- **Human review required**: All workflows require human review before commit

## What This Is Not

- Not Codex-specific (Codex is one executor adapter among several)
- Not a production platform, queue, or dashboard
- Not a control plane or provider fanout layer
- Not an autonomous coding system
- Not an auto-commit or auto-push tool
- Not a Copilot automation bypass

## Supported Modes

| Mode | Target/Executor | Tool Launches Agent? | Use Case |
|---|---|:---:|---|
| **render** | copilot | No | Generate Copilot-ready prompt |
| **render** | manual | No | Generate human work order |
| **render** | codex | No | Generate Codex adapter prompt |
| **package** | copilot | No | Create Copilot work package |
| **package** | manual | No | Create manual work package |
| **run** | mock | Yes | Test without external dependencies |
| **run** | codex | Yes | Local Codex execution |
| **report** | any | No | Review run or package artifacts |

## Quick Start

### Installation

```bash
# Add agent-job to PATH (temporary)
export PATH="/lump/apps/invoke-codex-from-claude/agent-job/scripts:$PATH"

# Or use directly
python3 /lump/apps/invoke-codex-from-claude/agent-job/scripts/agent-job --help
```

**Requirements**: Python 3, PyYAML

### Copilot Package Workflow (Recommended)

Create a work package for GitHub Copilot:

```bash
# 1. Create a schema v2 job file (see examples/v2/)
# 2. Package for Copilot
agent-job package examples/v2/copilot-docs.job.yaml --target copilot

# 3. Open the generated prompt
cat runs/JOB-COPILOT-DOCS-001/*/prompt.copilot.md

# 4. Copy prompt to GitHub Copilot Chat or Copilot Workspace
# 5. Execute work in Copilot environment
# 6. Fill out report-template.md with results
# 7. Review diff and decide whether to commit
```

**Output**: `runs/<job-id>/<timestamp>-copilot-package/`
- `prompt.copilot.md` - Paste into Copilot
- `checklist.md` - Human review checklist
- `report-template.md` - Completion template
- `job.input.yaml` - Original job spec
- `meta.json` - Package metadata

### Manual Workflow

Create a human-readable work order:

```bash
agent-job package examples/v2/manual-refactor.job.yaml --target manual
```

Use the generated work order with any approved tool or agent.

### Mock Testing

Test the workflow without external dependencies:

```bash
agent-job run examples/v2/mock-test.job.yaml --executor mock
agent-job report runs/JOB-MOCK-TEST-001/*/
```

### Validate and Render

```bash
# Validate a job file
agent-job validate examples/v2/copilot-docs.job.yaml

# Render for specific target
agent-job render examples/v2/copilot-docs.job.yaml --target copilot
agent-job render examples/v2/manual-refactor.job.yaml --target manual
```

## Job Schema v2

Schema v2 is executor-neutral with organized sections:

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
  constraints: [rules to follow]
  acceptance_criteria: [success conditions]

scope:
  allowed_paths: [writable paths]
  forbidden_paths: [forbidden paths]

execution:
  mode: agent | human | ci
  preferred_executor: copilot | human | codex | mock
  allowed_executors: [list]
  disallowed_executors: [list]
  commands_allowed: [list]
  commands_forbidden: [list]
  test_commands: [list]

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

See `examples/v2/` for complete examples and `agent-job/README.md` for detailed documentation.

## Commands

### validate

Validate a job file:
```bash
agent-job validate <job.job.yaml>
```

### render

Render job to target-specific prompt:
```bash
agent-job render <job.job.yaml> --target <copilot|manual|codex|claude>
```

### package

Create work package without execution:
```bash
agent-job package <job.job.yaml> --target <copilot|manual>
```

### run

Execute job via specified executor:
```bash
agent-job run <job.job.yaml> --executor <codex|mock> [--dry-run]
```

**Note**: `--executor copilot` is not supported. Use `package --target copilot` instead.

### report

Print report for a run or package:
```bash
agent-job report <run-dir>
```

## Copilot Workflow Details

### Why Package Mode?

GitHub Copilot Chat and Copilot Workspace are the approved execution environments in many organizations. The `agent-job` tool:
- ✅ Creates Copilot-ready prompts with clear scope and constraints
- ✅ Provides completion templates for consistent reporting
- ✅ Enables provenance tracking even for external execution
- ❌ Does NOT automate or bypass Copilot (no fake execution)
- ❌ Does NOT require Codex installation or auth

### Package Workflow Steps

1. **Create job file** with `preferred_executor: copilot`
2. **Package**: `agent-job package job.yaml --target copilot`
3. **Review prompt**: Check `runs/.../prompt.copilot.md` for clarity
4. **Copy to Copilot**: Paste into Copilot Chat or Workspace
5. **Execute**: Let Copilot perform the work in approved environment
6. **Document**: Fill out `report-template.md` with Copilot's output
7. **Review diff**: Verify changes meet acceptance criteria
8. **Commit decision**: Human decides whether to commit

### Package Honesty

Package mode metadata (`meta.json`):
```json
{
  "mode": "package",
  "target": "copilot",
  "launched_by_tool": false,
  "process_success": null,
  "exit_code": null
}
```

The tool is honest about what it did and didn't do.

## Schema v1 Compatibility

Schema v1 (codex-job format) is auto-migrated with warnings:

```bash
$ agent-job validate examples/bugfix.job.yaml
warning: schema v1 is deprecated; migrate to schema v2
warning: ignoring v1 model_tier (Codex-specific, not in v2 schema)
valid: JOB-EXAMPLE-BUGFIX
```

See [Migration Guide](docs/migration-from-codex-job.md) for details.

## Migration from codex-job

The `codex-job` CLI is the legacy Codex-specific predecessor to `agent-job`. Both can coexist.

### Key Differences

| Feature | codex-job | agent-job |
|---|---|---|
| Identity | Codex-specific | Executor-neutral |
| Schema | v1 (flat) | v2 (structured) |
| Copilot support | No | Yes (package mode) |
| Manual support | No | Yes (package mode) |
| Provenance | `claimed_by_codex` | `claimed_by_agent` |
| Auth requirement | Always Codex | Only when `--executor codex` |
| Render targets | One (Codex) | Multiple (Copilot, manual, Codex) |

### Migration Steps

1. **Keep using codex-job** for existing Codex workflows (no changes needed)
2. **Try agent-job** for new Copilot/manual workflows
3. **Convert jobs** from schema v1 → v2 (or use auto-migration)
4. **Test with mock**: `agent-job run job.yaml --executor mock`
5. **Switch to agent-job** when ready

See [Migration Guide](docs/migration-from-codex-job.md) for complete instructions.

## Using codex-job (Legacy)

The original `codex-job` CLI remains available:

```bash
# Install (if not already installed)
./install_codex_job_skill.sh --scope project

# Use codex-job commands
codex-job validate examples/bugfix.job.yaml
codex-job run examples/bugfix.job.yaml
```

**Requirements**: Python 3, PyYAML, Codex CLI (`codex login`)

See `codex-job/` directory for legacy documentation.

## Provenance Model

The system distinguishes between:

- **observed**: Runner captured via git/fs/process
- **declared_by_job**: Job file specified
- **claimed_by_agent**: Agent reported (Copilot, Codex, mock, etc.)
- **claimed_by_executor**: Executor wrapper reported
- **inferred**: Derived from other data
- **not_captured**: Runner could not capture
- **not_run**: Not executed
- **unknown**: Indeterminate

Package mode is honest about non-execution:
- `launched_by_tool: false`
- `process_success: null`
- No fabricated exit codes

## Safety Model

- Strict fail-closed validation
- Absolute repo paths required
- Allowed/forbidden path enforcement (prompt-based)
- No auto-commit, no auto-push
- Human review required for all workflows
- Package mode honest about non-execution
- No shell callbacks or dangerous operations
- No Copilot automation bypass

## Architecture

```
agent-job/                          # Universal architecture
  scripts/
    agent-job, agent_job_cli.py, schema.py
  executors/
    base_executor.py, mock_executor.py, codex_executor.py
  renderers/
    base_renderer.py, copilot_renderer.py, manual_renderer.py, codex_renderer.py

codex-job/                          # Legacy Codex-specific
  scripts/codex-job, codex_job_cli.py

examples/
  v2/                               # Schema v2 examples
    copilot-docs.job.yaml
    manual-refactor.job.yaml
    mock-test.job.yaml
  *.job.yaml                        # Schema v1 examples (legacy)
```

See [Architecture Documentation](docs/current-architecture.md) for details.

## Examples

**Schema v2 examples** (recommended):
- `examples/v2/copilot-docs.job.yaml` - Copilot workflow
- `examples/v2/manual-refactor.job.yaml` - Manual workflow
- `examples/v2/mock-test.job.yaml` - Mock testing

**Schema v1 examples** (legacy, auto-migrated):
- `examples/bugfix.job.yaml`
- `examples/refactor.job.yaml`
- `examples/docs.job.yaml`

## Documentation

- **[agent-job README](agent-job/README.md)** - Detailed agent-job documentation
- **[Migration Guide](docs/migration-from-codex-job.md)** - Schema v1 → v2 migration
- **[Architecture](docs/current-architecture.md)** - System architecture
- **[Safety Model](docs/safety-model.md)** - Safety and validation
- **[Phase A Report](docs/phase-a-implementation-report.md)** - Implementation details

## Known Limitations

Phase A limitations:
- Codex executor: Full execution pending migration (dry-run works)
- Completion ingestion: Not yet implemented
- Claude renderer: Not yet implemented
- Git integration: Partial (from codex-job, not fully migrated)

See [Phase A Report](docs/phase-a-implementation-report.md) for details.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Security

See [SECURITY.md](SECURITY.md) for security policies.

## License

See [LICENSE](LICENSE) file.

## Support

For issues or questions, see the repository issue tracker or documentation.

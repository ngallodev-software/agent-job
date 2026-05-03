# Migration Guide: codex-job → agent-job

This guide helps you migrate from `codex-job` (Codex-specific) to `agent-job` (Copilot/manual forward path).

## Summary

- **codex-job**: Legacy Codex-specific CLI (schema v1)
- **agent-job**: Copilot/manual CLI with schema v2 and mock testing
- **Both can coexist**: No forced migration, migrate at your own pace
- **Auto-migration**: Schema v1 jobs work with agent-job (with warnings)

## Why Migrate?

### New Capabilities

✅ **Copilot support**: Package mode for GitHub Copilot Chat/Workspace
✅ **Manual workflows**: Human-readable work orders for any approved tool
✅ **Mock testing**: Test workflows without Codex
✅ **Executor-neutral**: No Codex requirement for validation/rendering/packaging
✅ **Better schema**: Organized sections instead of flat structure
✅ **Universal provenance**: `claimed_by_agent` instead of `claimed_by_codex`

### When to Migrate

**Migrate now if**:
- You want to use Copilot workflows
- You want manual work orders
- You need executor-neutral validation
- You're starting new projects

**Stay on codex-job if**:
- Existing workflows work fine
- You only use Codex
- Migration effort isn't worth it yet

**Both work**: codex-job unchanged, agent-job available

## Command Migration

### validate

**Before (codex-job)**:
```bash
codex-job validate job.job.yaml
```

**After (agent-job)**:
```bash
agent-job validate job.job.yaml
```

**Change**: Command name only

### render

**Before (codex-job)**:
```bash
codex-job render job.job.yaml
```

**After (agent-job - Copilot target)**:
```bash
agent-job render job.job.yaml --target copilot
```

**Change**: Added `--target` flag for packaging-oriented renderers. `codex` and `claude` targets are not yet implemented in `agent-job`.

### run

**Before (codex-job)**:
```bash
codex-job run job.job.yaml
codex-job run job.job.yaml --dry-run
codex-job run job.job.yaml --run-tests
```

**After (agent-job)**:
```bash
agent-job run job.job.yaml --executor mock
```

**Change**: `agent-job` currently supports mock execution only. Use `codex-job` for live Codex execution.

### report

**Before (codex-job)**:
```bash
codex-job report runs/<job-id>/<run-id>/
```

**After (agent-job)**:
```bash
agent-job report runs/<job-id>/<run-id>/
```

**Change**: Command name only

### New Commands (agent-job only)

**Package mode** (not in codex-job):
```bash
agent-job package job.job.yaml --target copilot
agent-job package job.job.yaml --target manual
```

**Mock executor** (not in codex-job):
```bash
agent-job run job.job.yaml --executor mock
```

## Schema Migration

### Schema v1 (codex-job) → Schema v2 (agent-job)

#### Auto-Migration

agent-job auto-migrates v1 jobs with warnings:

```bash
$ agent-job validate examples/bugfix.job.yaml
warning: schema v1 is deprecated; migrate to schema v2
warning: ignoring v1 model_tier (Codex-specific, not in v2 schema)
valid: JOB-EXAMPLE-BUGFIX
```

#### Manual Migration

**Schema v1 (flat structure)**:
```yaml
schema_version: 1
id: JOB-001
title: Fix bug
repo_path: /path
branch: null
task_type: bugfix
objective: Fix the bug
context: Bug context
allowed_paths:
  - src/
forbidden_paths:
  - .git/
constraints:
  - No auto-commit
acceptance_criteria:
  - Tests pass
commands_allowed:
  - python3
commands_forbidden:
  - git push
test_commands:
  - pytest
output_contract:
  require_summary: true
  require_changed_files: true
  require_tests_run: false
security_notes:
  - Be careful
created_by: human
created_at: 2026-05-03T00:00:00Z
model_tier: low
model: null
```

**Schema v2 (organized sections)**:
```yaml
schema_version: 2
id: JOB-001
title: Fix bug
repo_path: /path
branch: null

task:
  type: bugfix
  objective: Fix the bug
  context: Bug context
  constraints:
    - No auto-commit
  acceptance_criteria:
    - Tests pass

scope:
  allowed_paths:
    - src/
  forbidden_paths:
    - .git/

execution:
  mode: agent
  preferred_executor: codex
  allowed_executors:
    - codex
    - mock
  disallowed_executors: []
  commands_allowed:
    - python3
  commands_forbidden:
    - git push
  test_commands:
    - pytest

output_contract:
  require_summary: true
  require_changed_files: true
  require_tests_run: false
  require_risks: true
  human_review_required: true

provenance:
  distinguish_agent_claims: true
  require_changed_file_snapshot: true
  require_test_evidence: true

created_by: human
created_at: 2026-05-03T00:00:00Z
```

### Field Mapping

| v1 Field | v2 Location | Notes |
|---|---|---|
| `schema_version` | `schema_version` | Change 1 → 2 |
| `id` | `id` | Unchanged |
| `title` | `title` | Unchanged |
| `repo_path` | `repo_path` | Unchanged |
| `branch` | `branch` | Unchanged |
| `task_type` | `task.type` | Moved to `task` section |
| `objective` | `task.objective` | Moved to `task` section |
| `context` | `task.context` | Moved to `task` section |
| `constraints` | `task.constraints` | Moved to `task` section |
| `acceptance_criteria` | `task.acceptance_criteria` | Moved to `task` section |
| `allowed_paths` | `scope.allowed_paths` | Moved to `scope` section |
| `forbidden_paths` | `scope.forbidden_paths` | Moved to `scope` section |
| `commands_allowed` | `execution.commands_allowed` | Moved to `execution` section |
| `commands_forbidden` | `execution.commands_forbidden` | Moved to `execution` section |
| `test_commands` | `execution.test_commands` | Moved to `execution` section |
| `output_contract` | `output_contract` | Add new fields |
| `security_notes` | *(removed)* | Embed in constraints if needed |
| `created_by` | `created_by` | Unchanged |
| `created_at` | `created_at` | Unchanged |
| `model_tier` | *(removed)* | Codex-specific, ignored |
| `model` | *(removed)* | Codex-specific, ignored |
| *(new)* | `execution.mode` | Add: `agent` |
| *(new)* | `execution.preferred_executor` | Add: `codex` or `copilot` |
| *(new)* | `execution.allowed_executors` | Add list |
| *(new)* | `execution.disallowed_executors` | Add list (usually empty) |
| *(new)* | `provenance.*` | Add provenance config |

### Dropped Fields

**`model_tier` and `model`**:
- Codex-specific, not universal
- Ignored during migration
- Configure in Codex executor if needed

**`security_notes`**:
- Moved to constraints or context
- Not a separate section in v2

### New Fields

**`execution.mode`**:
- Values: `agent`, `human`, `ci`
- Default: `agent`

**`execution.preferred_executor`**:
- Values: `copilot`, `human`, `codex`, `mock`
- Guidance, not requirement

**`execution.allowed_executors`**:
- List of allowed executors
- Empty = all allowed

**`execution.disallowed_executors`**:
- List of forbidden executors
- Empty = none forbidden

**`provenance.*`**:
- Configuration for provenance capture
- All boolean flags

**`output_contract.require_risks`**:
- New in v2, default `true`

**`output_contract.human_review_required`**:
- New in v2, default `true`

## Provenance Changes

### Before (codex-job)

```json
{
  "changed_files": {
    "provenance": "claimed_by_codex",
    "files": ["src/app.py"]
  }
}
```

### After (agent-job)

```json
{
  "changed_files": {
    "provenance": "claimed_by_agent",
    "agent": "codex",
    "source": "run.log",
    "files": ["src/app.py"]
  }
}
```

**Change**: `claimed_by_codex` → `claimed_by_agent` with `agent` metadata

## Workflow Migration

### Codex Execution

**Before (codex-job)**:
```bash
codex-job run /abs/path/to/job.job.yaml
```

**After (agent-job - Phase A)**:
```bash
# Option 1: Keep using codex-job (no changes needed)
codex-job run /abs/path/to/job.job.yaml

# Option 2: Use agent-job for Copilot/manual packaging and mock validation
agent-job package /abs/path/to/job.job.yaml --target copilot
```

**Status**: Full Codex execution via `agent-job` is not yet implemented.

### Copilot Workflow (New)

**Not possible with codex-job**.

**With agent-job**:
```bash
# 1. Create schema v2 job with preferred_executor: copilot
# 2. Package
agent-job package job.job.yaml --target copilot

# 3. Open prompt
cat runs/<job-id>/<timestamp>-copilot-package/prompt.copilot.md

# 4. Copy to Copilot Chat or Workspace
# 5. Execute in Copilot
# 6. Fill out report-template.md
# 7. Review and commit
```

## Migration Strategies

### Strategy 1: Gradual (Recommended)

1. **Keep codex-job** for existing workflows (no changes)
2. **Try agent-job** for new Copilot/manual workflows
3. **Test with mock**: `agent-job run job.yaml --executor mock`
4. **Convert one job** to schema v2 manually
5. **Validate both**: `codex-job validate` and `agent-job validate`
6. **Switch when ready**: Move new Copilot/manual work to `agent-job`

### Strategy 2: Immediate

1. **Convert all v1 jobs** to v2 (manual or rely on auto-migration)
2. **Update scripts** to use `agent-job` commands
3. **Test thoroughly** with mock executor
4. **Keep codex-job** for Codex execution

### Strategy 3: Dual (Safe)

1. **Use both CLIs** for different purposes:
   - `agent-job` for Copilot/manual workflows
   - `codex-job` for Codex execution (Phase A)
2. **Convert jobs** to v2 as you touch them
3. **Migrate gradually** while agent-job Codex support remains unimplemented

## Testing Migration

### Validate Old Jobs with New CLI

```bash
# Test auto-migration
agent-job validate examples/bugfix.job.yaml

# Expected output:
# warning: schema v1 is deprecated; migrate to schema v2
# valid: JOB-EXAMPLE-BUGFIX
```

### Compare Copilot Packaging

```bash
# Old Codex-specific render
codex-job render examples/bugfix.job.yaml > old-render.txt

# New Copilot render
agent-job render examples/v2/copilot-docs.job.yaml --target copilot > copilot-render.txt
```

### Dry-Run Comparison

```bash
# Old dry-run
codex-job run examples/bugfix.job.yaml --dry-run

# New dry-run (mock executor)
agent-job run examples/bugfix.job.yaml --executor mock --dry-run
```

## Common Issues

### Issue: "schema_version: 2" not recognized by codex-job

**Cause**: codex-job only supports schema v1

**Solution**: Use agent-job for v2 jobs, or convert back to v1

### Issue: model_tier warning during migration

**Cause**: `model_tier` is Codex-specific, removed in v2

**Solution**: Ignore warning. Keep executor-specific model selection in `codex-job` until `agent-job` implements a real Codex path.

### Issue: Codex path not implemented in agent-job

**Cause**: `agent-job` has not implemented live Codex execution or Codex/Claude render targets yet

**Solution**: Use `codex-job` for Codex execution and `agent-job` for Copilot/manual workflows

### Issue: --executor flag required

**Cause**: agent-job requires explicit executor selection

**Solution**: Add `--executor mock` for `agent-job`, or keep using `codex-job` for Codex execution

### Issue: Package mode unclear

**Cause**: Package mode is new concept

**Solution**: Read package workflow documentation, review generated prompts

## Rollback Plan

If migration causes issues:

1. **Keep using codex-job**: No changes needed, still fully functional
2. **Revert schema changes**: Convert v2 back to v1 if needed
3. **File issues**: Report problems for investigation

## Migration Checklist

- [ ] Read this guide
- [ ] Test agent-job validate on existing v1 jobs
- [ ] Create one test v2 job
- [ ] Test mock executor: `agent-job run --executor mock`
- [ ] Test Copilot package workflow (if using Copilot)
- [ ] Compare render outputs (codex-job vs agent-job)
- [ ] Update local scripts/aliases (if any)
- [ ] Train team on new commands (if team project)
- [ ] Decide on migration strategy (gradual/immediate/dual)
- [ ] Keep codex-job as fallback during transition

## Support

- **Documentation**: See `agent-job/README.md` for detailed agent-job docs
- **Examples**: Check `examples/v2/` for schema v2 job examples
- **Issues**: Report migration issues to repository issue tracker
- **Compatibility**: Both CLIs can coexist, no forced migration

## Timeline

- **Phase A (current)**: agent-job available, codex-job unchanged
- **Phase B (future)**: Full Codex executor migration to agent-job
- **Phase C (future)**: codex-job deprecated wrapper (optional)
- **Phase D (far future)**: codex-job removal (if consensus)

**No deadline**: Migrate at your own pace.

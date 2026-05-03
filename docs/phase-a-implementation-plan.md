# Phase A Implementation Plan: Universal Agent-Job Architecture

## Current State Analysis

### Existing Structure
```
codex-job/
  scripts/
    codex-job               # Entrypoint wrapper
    codex_job_cli.py        # 1179 lines, Codex-specific
    codex_job_support.py    # Support helpers
  references/
    available_models.jsonl  # Model registry
    common-delegation-issues.md
    invocation-patterns.md
  SKILL.md

examples/
  bugfix.job.yaml
  docs.job.yaml
  invalid-path-traversal.job.yaml
  refactor.job.yaml
```

### Current Schema (v1)
- Flat structure with all fields at top level
- Codex-specific: `model_tier`, `model`
- No executor metadata
- No render target support

### Current Provenance
- Uses `claimed_by_codex` hardcoded
- Report markers: `BEGIN_CODEX_JOB_REPORT`, `END_CODEX_JOB_REPORT`

### Current Commands
```bash
codex-job validate <job>
codex-job render <job>
codex-job run <job> [--dry-run] [--run-tests] [--codex-bin <path>]
codex-job report <run-dir>
```

## Implementation Strategy

### Phase A.1: Create New Universal Architecture (Parallel)

**Goal**: Build new `agent-job` CLI alongside existing `codex-job` without breaking current functionality.

**Approach**: 
1. Create new `agent-job/` directory structure
2. Implement schema v2 with migration from v1
3. Create executor and renderer abstractions
4. Leave `codex-job/` untouched during development
5. Test new system independently
6. Switch over once validated

### Phase A.2: Files to Create

```
agent-job/
  scripts/
    agent-job                       # New entrypoint
    agent_job_cli.py                # Universal CLI
    agent_job_support.py            # Shared helpers
    schema.py                       # Schema v1 & v2 handling
    
  executors/
    base_executor.py                # Abstract executor interface
    codex_executor.py               # Codex adapter
    mock_executor.py                # Mock for testing
    
  renderers/
    base_renderer.py                # Abstract renderer interface
    copilot_renderer.py             # Copilot target
    manual_renderer.py              # Manual/human target
    codex_renderer.py               # Codex target
    
  references/
    available_models.jsonl          # Copy from codex-job
    executor-adapters.md            # New doc
    
  SKILL.md                          # Updated skill

examples/
  v2/
    copilot-docs.job.yaml           # Schema v2, Copilot
    manual-refactor.job.yaml        # Schema v2, manual
    codex-bugfix.job.yaml           # Schema v2, Codex
    mock-test.job.yaml              # Schema v2, mock
    invalid-executor.job.yaml       # Invalid for tests

tests/
  test_schema_v2.py                 # Schema v2 validation
  test_schema_migration.py          # v1 → v2 migration
  test_copilot_renderer.py          # Copilot rendering
  test_manual_renderer.py           # Manual rendering
  test_package_mode.py              # Package command
  test_mock_executor.py             # Mock executor
  test_cli_integration.sh           # End-to-end CLI tests
```

### Phase A.3: Files to Modify

```
README.md                           # Update to agent-job
SECURITY.md                         # Update references
CONTRIBUTING.md                     # Update CLI name
docs/current-architecture.md        # Add universal layer
docs/safety-model.md                # Update for multi-executor
install_codex_job_skill.sh          # Add agent-job option
```

### Phase A.4: Compatibility Strategy

**Option A (Recommended)**: Side-by-side installation
- Keep `codex-job/` as-is for now
- Install `agent-job/` alongside
- Add deprecation notice to `codex-job` docs
- Users can try `agent-job` while `codex-job` still works

**Option B**: Create wrapper
- Create `codex-job` → `agent-job run --executor codex` wrapper
- More disruptive, defer to later phase

**Decision**: Use Option A for Phase A.

## Detailed Implementation Steps

### Step 1: Schema v2 Implementation

**File**: `agent-job/scripts/schema.py`

**Features**:
- `load_job_v2()` - Load and validate schema v2
- `migrate_v1_to_v2()` - Convert v1 → v2 with warnings
- `JobV2` dataclass with structured sections
- Executor-neutral validation
- No Codex-specific requirements

**Schema v2 Structure**:
```python
@dataclass(frozen=True)
class JobV2:
    schema_version: int  # Must be 2
    job_id: str
    title: str
    repo_path: Path
    branch: str | None
    
    # Task section
    task_type: str
    objective: str
    context: str
    constraints: list[str]
    acceptance_criteria: list[str]
    
    # Scope section
    allowed_paths: list[str]
    forbidden_paths: list[str]
    
    # Execution section
    mode: str  # agent | human | ci
    preferred_executor: str | None
    allowed_executors: list[str]
    disallowed_executors: list[str]
    commands_allowed: list[str]
    commands_forbidden: list[str]
    test_commands: list[str]
    
    # Output contract
    output_contract: dict[str, bool]
    
    # Provenance requirements
    provenance_config: dict[str, bool]
    
    # Metadata
    created_by: str
    created_at: str
    source_path: Path
```

### Step 2: Base Executor Interface

**File**: `agent-job/executors/base_executor.py`

```python
class BaseExecutor(ABC):
    @abstractmethod
    def can_execute(self, job: JobV2) -> bool:
        """Check if this executor can handle the job."""
        
    @abstractmethod
    def execute(self, job: JobV2, run_dir: Path, dry_run: bool) -> ExecutionResult:
        """Execute the job and return results."""
        
    @abstractmethod
    def get_executor_name(self) -> str:
        """Return executor identifier (e.g., 'codex', 'mock')."""
```

### Step 3: Codex Executor Adapter

**File**: `agent-job/executors/codex_executor.py`

**Isolate**:
- Codex auth check (only when executing)
- `codex exec` invocation
- Model tier mapping (Codex-specific config)
- Codex prompt optimization
- Codex log parsing

**Interface**:
```python
class CodexExecutor(BaseExecutor):
    def can_execute(self, job: JobV2) -> bool:
        return "codex" in job.allowed_executors
        
    def execute(self, job: JobV2, run_dir: Path, dry_run: bool) -> ExecutionResult:
        # Check auth only here
        # Invoke codex exec
        # Parse results
        # Return with provenance: {"agent": "codex"}
```

### Step 4: Mock Executor

**File**: `agent-job/executors/mock_executor.py`

**Purpose**: Testing without external dependencies

```python
class MockExecutor(BaseExecutor):
    def execute(self, job: JobV2, run_dir: Path, dry_run: bool) -> ExecutionResult:
        # Write predictable output
        # Optionally simulate file changes if configured
        # Return success with mock provenance
```

### Step 5: Base Renderer Interface

**File**: `agent-job/renderers/base_renderer.py`

```python
class BaseRenderer(ABC):
    @abstractmethod
    def render(self, job: JobV2) -> str:
        """Render job to target-specific prompt."""
        
    @abstractmethod
    def get_target_name(self) -> str:
        """Return target identifier."""
```

### Step 6: Copilot Renderer

**File**: `agent-job/renderers/copilot_renderer.py`

**Output Format**:
```markdown
# Engineering Job for Copilot

## Role
You are assisting with a bounded engineering task.

## Job Metadata
- Job ID: {job_id}
- Title: {title}
- Task Type: {task_type}
- Repository: {repo_path}

## Objective
{objective}

## Context
{context}

## Scope
### Allowed Paths
{allowed_paths}

### Forbidden Paths
{forbidden_paths}

## Constraints
{constraints}

## Acceptance Criteria
{acceptance_criteria}

## Required Evidence
When finished, report:
- Summary of changes
- Files changed
- Tests run
- Tests not run
- Acceptance criteria status
- Risks
- Follow-up

## Important Rules
- Do not auto-commit
- Do not auto-push
- Do not modify files outside allowed paths
- Distinguish observed facts from claims
- Do not claim tests passed unless you ran them

## Commands Policy
### Allowed
{commands_allowed}

### Forbidden
{commands_forbidden}
```

**Critical**: Must NOT mention Codex or imply direct execution.

### Step 7: Manual Renderer

**File**: `agent-job/renderers/manual_renderer.py`

Similar to Copilot but with human-friendly language and checklist format.

### Step 8: Codex Renderer

**File**: `agent-job/renderers/codex_renderer.py`

Adapt current `render_prompt()` logic from `codex_job_cli.py`, but:
- Use universal language where possible
- Mark as adapter-specific
- Use `claimed_by_agent` with `agent: codex`

### Step 9: Universal CLI

**File**: `agent-job/scripts/agent_job_cli.py`

**Commands**:
```python
def cmd_validate(args):
    # Load job (v1 or v2)
    # Validate
    # Print result

def cmd_render(args):
    # Load job
    # Get renderer for target
    # Render and print

def cmd_package(args):
    # Load job
    # Validate
    # Render for target
    # Create artifact directory
    # Write package files
    # Write meta.json (launched_by_tool: false)

def cmd_run(args):
    # Load job
    # Get executor
    # Check if executor is allowed
    # Execute
    # Write artifacts
    # Generate report

def cmd_report(args):
    # Read run/package directory
    # Generate human-readable report
```

**Key Differences from Current**:
- No Codex auth check in validate/render/package
- Target-based rendering instead of single Codex prompt
- Executor-based running instead of hardcoded Codex
- Package mode that doesn't execute
- Helpful error for `--executor copilot`

### Step 10: Provenance Update

**Constants**:
```python
PROVENANCE_CATEGORIES = [
    "observed",
    "declared_by_job",
    "claimed_by_agent",      # Replaces claimed_by_codex
    "claimed_by_executor",
    "inferred",
    "not_captured",
    "not_run",
    "unknown",
]
```

**Report Structure**:
```json
{
  "changed_files": {
    "provenance": "claimed_by_agent",
    "agent": "copilot",
    "source": "completion.md",
    "files": ["src/app.py"]
  }
}
```

### Step 11: Package Mode Implementation

**Command**: `agent-job package <job> --target copilot`

**Behavior**:
1. Validate job
2. Render prompt for target
3. Create `runs/<job-id>/<timestamp>-<target>-package/`
4. Write files:
   - `job.input.yaml` - Original job
   - `prompt.<target>.md` - Rendered prompt
   - `checklist.md` - Review checklist
   - `report-template.md` - Completion template
   - `meta.json` - Package metadata
5. Print next steps

**meta.json**:
```json
{
  "schema_version": 2,
  "job_id": "JOB-2026-05-03-001",
  "run_id": "20260503-130000-copilot-package",
  "mode": "package",
  "target": "copilot",
  "executor": null,
  "launched_by_tool": false,
  "process_success": null,
  "exit_code": null,
  "human_review_required": true,
  "created_at": "2026-05-03T13:00:00Z"
}
```

### Step 12: Examples (Schema v2)

**examples/v2/copilot-docs.job.yaml**:
```yaml
schema_version: 2
id: JOB-COPILOT-DOCS-001
title: Update documentation for agent-job
repo_path: /lump/apps/invoke-codex-from-claude
branch: null

task:
  type: docs
  objective: >
    Update README to present agent-job as canonical CLI.
  context: |
    Repo has pivoted from Codex-specific to universal agent job contract.
  constraints:
    - Do not auto-commit.
    - Do not auto-push.
  acceptance_criteria:
    - README presents agent-job as canonical.
    - Copilot support is documented.

scope:
  allowed_paths:
    - README.md
    - docs/
  forbidden_paths:
    - .git/
    - .env

execution:
  mode: agent
  preferred_executor: copilot
  allowed_executors:
    - copilot
    - human
    - codex
  disallowed_executors: []
  commands_allowed:
    - git
  commands_forbidden:
    - git push
    - rm -rf
  test_commands: []

output_contract:
  require_summary: true
  require_changed_files: true
  require_tests_run: false
  require_risks: true
  human_review_required: true

provenance:
  distinguish_agent_claims: true
  require_changed_file_snapshot: true
  require_test_evidence: false

created_by: human
created_at: 2026-05-03T00:00:00Z
```

### Step 13: Tests

**tests/test_schema_v2.py**:
- Valid v2 job passes
- Missing required fields fail
- Unknown executor fails
- Executor in both allowed/disallowed fails
- Path traversal fails
- Codex-specific fields are optional

**tests/test_copilot_renderer.py**:
- Renders valid markdown
- Does not mention Codex
- Does not imply direct execution
- Includes safety rules
- Includes report template

**tests/test_package_mode.py**:
- Creates artifact directory
- Writes all required files
- meta.json has correct structure
- launched_by_tool is false
- process_success is null

**tests/test_cli_integration.sh**:
```bash
#!/usr/bin/env bash
set -e

# Validate
agent-job validate examples/v2/copilot-docs.job.yaml

# Render copilot
agent-job render examples/v2/copilot-docs.job.yaml --target copilot | grep -q "Engineering Job for Copilot"

# Render manual
agent-job render examples/v2/manual-refactor.job.yaml --target manual

# Package copilot
agent-job package examples/v2/copilot-docs.job.yaml --target copilot

# Run mock
agent-job run examples/v2/mock-test.job.yaml --executor mock

# Reject copilot executor
! agent-job run examples/v2/copilot-docs.job.yaml --executor copilot 2>&1 | grep -q "package mode"

echo "All integration tests passed"
```

### Step 14: Documentation Updates

**README.md**:
- Title: "agent-job: Universal Agent Job Contract"
- Supported modes table
- Quick starts for Copilot, manual, Codex
- Migration section

**docs/current-architecture.md**:
- Add universal layer diagram
- Add executor adapter layer
- Add renderer targets
- Document package mode

**docs/copilot-workflow.md** (new):
- How to create Copilot job
- How to package for Copilot
- How to use prompt in Copilot Chat/Workspace
- How to fill completion notes
- How to review results

**docs/migration-from-codex-job.md** (new):
- Schema v1 → v2 mapping
- Command changes
- Provenance changes
- Executor adapter model

### Step 15: Installation Updates

**install_agent_job_skill.sh** (new):
```bash
#!/usr/bin/env bash
# Install agent-job skill and scripts
# Similar to current codex-job installer
```

## Testing Strategy

### Unit Tests
- Schema validation (v1 & v2)
- v1 → v2 migration
- Each renderer independently
- Each executor independently
- Provenance model

### Integration Tests
- Full CLI commands
- Package workflow
- Mock executor workflow
- Report generation

### Manual Verification
```bash
# Validate
agent-job validate examples/v2/copilot-docs.job.yaml

# Render
agent-job render examples/v2/copilot-docs.job.yaml --target copilot
agent-job render examples/v2/manual-refactor.job.yaml --target manual

# Package
agent-job package examples/v2/copilot-docs.job.yaml --target copilot
ls runs/JOB-COPILOT-DOCS-001/*/

# Mock execution
agent-job run examples/v2/mock-test.job.yaml --executor mock
agent-job report runs/*/20*-mock-run/

# Error cases
agent-job run examples/v2/copilot-docs.job.yaml --executor copilot  # Should fail
agent-job validate examples/v2/invalid-executor.job.yaml  # Should fail
```

## Success Criteria

### Decision Gate Checklist

- [ ] Can a Copilot-only environment use this repo without Codex?
- [ ] Can a human create a Copilot-ready job package?
- [ ] Does Copilot package mode avoid launching or faking Copilot execution?
- [ ] Is Codex now only an executor adapter?
- [ ] Is the schema executor-neutral?
- [ ] Is provenance agent-neutral?
- [ ] Does validate/render/package avoid requiring Codex auth?
- [ ] Is agent-job now the canonical CLI?
- [ ] Is codex-job deprecated or removed from canonical docs?

### All Must Be YES

## Risks and Mitigations

**Risk**: Breaking existing codex-job users
**Mitigation**: Install side-by-side, don't modify codex-job/ in Phase A

**Risk**: Schema v2 too complex
**Mitigation**: Provide clear migration guide and examples

**Risk**: Package mode unclear for users
**Mitigation**: Detailed docs and templates

**Risk**: Tests incomplete
**Mitigation**: Focus on integration tests for end-to-end workflows

## Timeline Estimate

- Schema v2 + migration: 2-3 hours
- Executor abstractions: 1-2 hours
- Renderer abstractions: 2-3 hours
- Universal CLI: 3-4 hours
- Examples: 1 hour
- Tests: 2-3 hours
- Documentation: 2 hours

**Total: 13-18 hours**

## Next Phase Recommendation

After Phase A completion, recommend:
- **Option A**: Copilot package dogfood - Use in real workflow
- **Option B**: Complete implementation - Add completion ingestion
- **Option C**: Deprecate codex-job - Create wrapper and migration path
- **Option D**: Adapter cleanup - Further isolate Codex-specific code

Decision based on Phase A results.

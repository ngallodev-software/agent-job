# Phase 1 Audit Report

## Verdict

Phase 1 is complete.

The repo is ready to start the Copilot eval suite implementation, but the suite should be built against the current `agent-job` behavior, not against older cleanup narratives or stale legacy docs.

## Scope of This Audit

Verified against current repo state:

- `agent-job` CLI surface
- schema v2 constraints
- Copilot/manual render and package behavior
- current examples
- current tests
- current docs relevant to the eval suite

Also dogfooded the current `agent-job` contract flow for this audit itself:

- validated a phase-1 audit job file
- rendered/package-generated a manual work order
- requested `gpt-5.4-mini` as the model in the contract

## Observed Facts

### Current CLI Surface

Current `agent-job` commands:

- `validate`
- `render`
- `package`
- `run`
- `report`

Observed behavior:

- `render --target copilot` works
- `package --target copilot` works
- `report <package-dir>` works for package artifacts
- `run --executor copilot` fails clearly and honestly
- `run --executor codex` is still not implemented

Implication:

- the eval suite must be human-run and package-oriented
- no part of the suite should assume direct Copilot execution

### Schema v2 Constraints

Current schema rules that matter for the suite:

- `repo_path` must be absolute
- `allowed_paths` are required and must be repo-relative
- `forbidden_paths` are repo-relative
- path traversal via `..` is rejected
- `.git` is automatically protected
- default forbidden items are also added:
  - `.env`
  - `.env.local`
  - `.env.*`
  - `node_modules/`

Implication:

- checked-in eval job files cannot safely hardcode a user-local absolute fixture path
- Phase 2 should either:
  - use a placeholder replacement step, or
  - generate runnable job files from checked-in templates

Recommended choice:

- keep checked-in YAML templates and add a tiny path-substitution helper in a later phase if needed

### Copilot Renderer / Package Behavior

The Copilot renderer currently includes:

- job metadata
- model guidance
- objective
- context
- allowed paths
- forbidden paths
- constraints
- acceptance criteria
- required evidence
- no auto-commit rule
- no auto-push rule
- command policy
- completion report template

Package mode currently writes:

- `job.input.yaml`
- `prompt.<target>.md`
- `checklist.md`
- `report-template.md`
- `meta.json`

Implication:

- the eval suite does not need to invent a second structured prompt format
- it should compare:
  - competent baseline markdown prompt
  - current `agent-job` generated Copilot prompt

### Current Examples

Reusable examples:

- `examples/v2/copilot-docs.job.yaml`
- `examples/v2/manual-refactor.job.yaml`
- `examples/v2/mock-test.job.yaml`
- `examples/v2/invalid-executor.job.yaml`

Useful signals:

- `copilot-docs.job.yaml` is the best current example for Copilot-oriented job structure
- `invalid-executor.job.yaml` is useful as a schema validation negative case
- `manual-refactor.job.yaml` is useful for task wording and scope style

Non-useful for the eval suite:

- `examples/sample.log`
- `examples/sample.meta.json`
- `examples/claude_hook_example.sh`

### Current Tests

Most relevant current tests:

- `tests/test_agent_job_cli.sh`
- `tests/test_install_dry_run.sh`

Useful coverage already present:

- default model selection behavior
- explicit not-implemented paths
- output contract enforcement
- basic install/bootstrap dry-run

Less relevant or misleading for this suite:

- `tests/test_runner_and_parser.sh`
- `tests/test_invoke_and_notify.sh`
- `tests/test_run_codex_task.bats`

These are legacy `codex-job` runtime tests, not eval-suite guidance.

### Current Doc State

Good guidance:

- `README.md`
- `agent-job/README.md`
- `agent-job/references/copilot/README.md`
- `SECURITY.md`

Stale or misleading for eval-suite planning:

- `CONTRIBUTING.md` was recently improved, but broader repo docs are still mixed
- `docs/current-architecture.md` still describes the dual-system world and some future phases
- many `docs/phase-a-*` and Codex-era docs should not guide suite design
- `future-plans/` and `deprecated/` are not relevant implementation references

Critical observation:

- `tests/test_contract_schemas.sh` still validates old `future-plans/schemas/*`
- that test passing does not prove anything about the eval suite design
- `docs/phase-a-implementation-plan.md` references test files that do not exist in the current repo and should not be treated as implementation truth
- `docs/migration-from-codex-job.md` contains stale migration guidance around model fields

## Reusable Assets

Phase 2 should reuse:

1. `agent-job` schema v2
2. `agent-job package --target copilot`
3. `examples/v2/copilot-docs.job.yaml` as the style anchor
4. current package metadata model
5. current report/checklist artifact shape
6. `meta.json` as part of the package artifact contract

Phase 2 should not reuse:

1. legacy Codex runner outputs
2. old evaluation/dogfood narratives from prior docs
3. sample logs/meta examples
4. any queue/dashboard/future-plan material

## Constraints and Risks

### Constraint 1: Absolute Fixture Paths

Risk:

- eval task YAML files need an absolute `repo_path`
- a checked-in fixture repo path will vary by machine

Recommended handling:

- keep checked-in job templates under task directories
- document one path-rewrite setup step in the runbook
- only add a tiny helper script if that becomes painful

### Constraint 2: Copilot Package Only

Risk:

- no direct Copilot execution support exists

Recommended handling:

- the runbook must make the A/B manual flow explicit
- the suite should not pretend to automate execution

### Constraint 3: Fairness Pressure

Risk:

- the suite could drift into rewarding structure for its own sake

Recommended handling:

- baseline prompts must stay competent
- rubric must explicitly allow:
  - `baseline better`
  - `roughly equal`
  - `inconclusive`

### Constraint 4: Repo Noise

Risk:

- old docs and legacy runtime surfaces can bias authors toward the wrong implementation model

Recommended handling:

- Phase 2 and later should reference only:
  - current `agent-job` CLI
  - current examples
  - current Copilot docs

### Constraint 5: Planned But Not Yet Present Helpers

Risk:

- the implementation prompt allows an optional `self_check.py`
- current docs mention it conceptually, but no such file exists yet

Recommended handling:

- treat `self_check.py` as a new deliverable in a later phase
- do not assume it already exists or shape the suite around it in Phase 2

## Dogfood Delegation Notes

This phase also tested the current `agent-job` contract flow for delegation:

- created: `docs/copilot-eval-suite/phase-01-audit.job.yaml`
- validated it with `agent-job validate`
- rendered it with `agent-job render --target manual`
- packaged it with `agent-job package --target manual`

Observed contract behavior:

- explicit `execution.model: gpt-5.4-mini` is preserved
- package metadata reports that model honestly
- because it is not in the Copilot registry, the package records:
  - `available_in_registry: false`

This is acceptable for the current dogfood use because the contract was used as a structured work order for a Codex mini-agent, not as a Copilot package.

Delegated audit corroboration from the `gpt-5.4-mini` Codex subagent:

- confirmed the live `agent-job` contract is the right source of truth
- confirmed package output includes `meta.json` and that some docs understate that
- confirmed `phase-a` planning docs contain stale references and should not guide the eval implementation

## Phase 2 Decision

Proceed to Phase 2 with this exact target:

- build `evals/copilot-run/`
- create a tiny Python stdlib fixture repo
- scaffold all 6 task directories
- create shared suite files
- do not yet optimize or overbuild task content

## Phase 2 Implementation Rules

1. Keep the fixture repo tiny.
2. Use one fixture repo for all six tasks.
3. Keep baseline prompts competent.
4. Do not make `agent-job` win by construction.
5. Build the suite for human-run Copilot A/B tests only.

# Phase 4 Report

## Verdict

Phase 4 is complete.

The shared evaluator assets and runbook now reflect:

- the real six-task pack
- the current `agent-job` package behavior
- the current fixture-path limitation
- the actual human-run result capture flow

## What Was Refined

Shared assets updated:

- `evals/copilot-run/README.md`
- `evals/copilot-run/runbook.md`

Added:

- `docs/copilot-eval-suite/phase-04-review.job.yaml`
- `docs/copilot-eval-suite/phase-04-report.md`

## Key Improvements

### 1. Path Reality Made Explicit

The shared docs now state that the checked-in task job files currently use the fixture path for this checkout and may need `repo_path` edits on another machine.

This avoids a misleading “just run it anywhere” story.

### 2. Result Capture Made Concrete

The runbook now recommends exact artifacts to save for each A/B run:

- prompt
- Copilot response
- changed-file list
- diff stat
- full diff
- tests run or claimed
- package metadata for the `agent-job` run

### 3. Package Review Step Added

The runbook now includes the optional but useful:

```bash
./agent-job/scripts/agent-job report runs/<job-id>/<timestamp>-copilot-package
```

so the operator can inspect package metadata before copying the prompt into Copilot.

### 4. Scoring Guidance Tightened

The runbook now explicitly tells the reviewer to prefer:

- lower scores for unsupported claims
- lower scores for unnecessary scope growth
- `roughly equal` over inventing a winner

The aggregate template now also states that rubric dimensions are equally weighted unless a task record explicitly documents an override.

## Validation

Ran:

```bash
for f in evals/copilot-run/tasks/*/agent-job.job.yaml; do
  ./agent-job/scripts/agent-job validate "$f"
done
```

Result:

- all task job files validated

Also re-ran active tests:

- `bash tests/test_agent_job_cli.sh`
- `bash tests/test_install_dry_run.sh`
- `cd evals/copilot-run/fixtures/sample-repo && python3 -m unittest discover -s tests`

All passed.

## Delegated Review Note

A `gpt-5.4-mini` Codex subagent was launched against a packaged Phase 4 review contract.

The contract validated and packaged correctly. The delegated review itself was used as a secondary check on operator-facing clarity.

Most useful delegated findings:

- preserve the full packaged run directory, not only the rendered prompt
- pass changed-file lists and tests-run evidence into the evaluation step
- state the aggregate weighting rule explicitly

## Phase 5 Readiness

Phase 5 can now focus on:

- optional self-check implementation
- package/render validation across all tasks
- final readiness gating for real Copilot dogfooding

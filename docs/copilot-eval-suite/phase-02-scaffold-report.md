# Phase 2 Scaffold Report

## Verdict

Phase 2 is complete.

The Copilot eval suite now has:

- a real `evals/copilot-run/` root
- shared suite docs/templates
- a tiny Python stdlib fixture repo
- results storage
- task directories for all six planned evals

## What Was Created

Suite root:

- `evals/copilot-run/README.md`
- `evals/copilot-run/evaluator-rubric.md`
- `evals/copilot-run/runbook.md`
- `evals/copilot-run/result-template.md`
- `evals/copilot-run/aggregate-template.md`

Fixture repo:

- `evals/copilot-run/fixtures/sample-repo/README.md`
- `evals/copilot-run/fixtures/sample-repo/src/calculator.py`
- `evals/copilot-run/fixtures/sample-repo/src/report_formatter.py`
- `evals/copilot-run/fixtures/sample-repo/src/path_policy.py`
- `evals/copilot-run/fixtures/sample-repo/tests/test_calculator.py`
- `evals/copilot-run/fixtures/sample-repo/tests/test_report_formatter.py`

Directories:

- `evals/copilot-run/results/`
- `evals/copilot-run/tasks/01-docs-consistency/`
- `evals/copilot-run/tasks/02-small-bugfix/`
- `evals/copilot-run/tasks/03-small-refactor/`
- `evals/copilot-run/tasks/04-test-addition/`
- `evals/copilot-run/tasks/05-scope-boundary/`
- `evals/copilot-run/tasks/06-ambiguous-request/`

## Fixture Design Outcome

The fixture repo is intentionally small and supports the planned task set:

- docs inconsistency:
  - fixture `README.md`
- small bug:
  - `calculator.average()` uses floor division
- small refactor target:
  - `report_formatter._normalize_lines()`
- missing test opportunity:
  - formatter and policy behaviors are only partially covered
- scope-boundary trap:
  - `path_policy.py` is isolated from the docs file that explains it
- ambiguous improvement target:
  - `render_report()` is functional but easy to over-improve

## Validation

Ran:

```bash
cd evals/copilot-run/fixtures/sample-repo
python3 -m unittest discover -s tests
```

Result:

- 6 tests passed

## Dogfood Delegation Note

A second `agent-job` contract was created and packaged for scaffold review:

- `docs/copilot-eval-suite/phase-02-scaffold.job.yaml`

The packaged contract validated and packaged correctly.

The delegated `gpt-5.4-mini` Codex subagent did not return useful scaffold recommendations, so Phase 2 implementation proceeded locally.

Conclusion:

- the contract/delegation surface itself worked
- the subagent response quality was weak on this pass

## Phase 3 Readiness

Phase 3 can start now.

What remains before that:

- author per-task baseline prompts
- author per-task `agent-job.job.yaml`
- author per-task evaluator prompts
- author per-task expected signals

No additional scaffold work is needed first.

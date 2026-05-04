# Phase 2: Fixture and Suite Scaffold

## Purpose

Create the repeatable filesystem shape and the tiny fixture repo that all eval tasks use.

## Scope

- create `evals/copilot-run/`
- create shared suite files with placeholders where needed
- create `fixtures/sample-repo/`
- create `results/.gitkeep` or equivalent empty-result placeholder

## Required Files

Suite root:

- `evals/copilot-run/README.md`
- `evals/copilot-run/evaluator-rubric.md`
- `evals/copilot-run/runbook.md`
- `evals/copilot-run/result-template.md`
- `evals/copilot-run/aggregate-template.md`
- `evals/copilot-run/self_check.py` if included in first pass

Fixture repo:

- `evals/copilot-run/fixtures/sample-repo/README.md`
- `evals/copilot-run/fixtures/sample-repo/src/calculator.py`
- `evals/copilot-run/fixtures/sample-repo/src/report_formatter.py`
- `evals/copilot-run/fixtures/sample-repo/src/path_policy.py`
- `evals/copilot-run/fixtures/sample-repo/tests/test_calculator.py`
- `evals/copilot-run/fixtures/sample-repo/tests/test_report_formatter.py`

Task roots:

- `evals/copilot-run/tasks/01-docs-consistency/`
- `evals/copilot-run/tasks/02-small-bugfix/`
- `evals/copilot-run/tasks/03-small-refactor/`
- `evals/copilot-run/tasks/04-test-addition/`
- `evals/copilot-run/tasks/05-scope-boundary/`
- `evals/copilot-run/tasks/06-ambiguous-request/`

## Fixture Design Rules

- Python stdlib only
- tiny enough to understand in minutes
- one obvious docs inconsistency
- one small bug
- one narrow refactor target
- one missing test
- one tempting forbidden-path neighbor
- one vague improvement target

## Recommended Fixture Mapping

- docs inconsistency: fixture `README.md` and command text
- bugfix: arithmetic edge case in `calculator.py`
- refactor: readability cleanup in one helper inside `report_formatter.py`
- test addition: missing focused test around renderer/policy behavior
- scope trap: `path_policy.py` adjacent to a tempting README or test cleanup
- ambiguous request: improve report output in `report_formatter.py`

## Exit Gate

Phase 2 is done when:

- the suite directory exists
- the fixture repo exists and is intentionally small
- every task directory exists
- shared root docs/templates exist, even if task-specific content is still pending

## Do Not Do Yet

- do not optimize scoring language
- do not overbuild the fixture repo
- do not add multiple languages or dependencies

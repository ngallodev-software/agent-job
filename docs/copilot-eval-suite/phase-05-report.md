# Phase 5 Report

## Verdict

Phase 5 is complete.

The Copilot eval suite is ready for initial manual dogfooding.

## What Was Added

- `evals/copilot-run/self_check.py`
- `docs/copilot-eval-suite/phase-05-readiness-review.job.yaml`
- `docs/copilot-eval-suite/phase-05-report.md`

## What Was Validated

Static suite checks:

- shared eval assets exist and are non-empty
- all six task folders contain the required files
- baseline and evaluator prompts are non-empty
- task prompts do not declare Codex as the required executor

`agent-job` checks:

- every task job file validates
- every task job file packages for Copilot successfully
- the Phase 5 readiness-review contract validates and packages

Fixture checks:

- the sample repo test suite still passes

## Final Readiness Assessment

The suite now satisfies the Phase 5 gate:

- all six tasks validate and package
- the runbook is explicit enough for a human to execute
- the rubric remains skeptical and evidence-based
- the fixture repo stays small and stable
- `baseline better` remains an allowed result

## Known Limitations

- task job files still contain checkout-specific absolute `repo_path` values
- the suite is intentionally human-run and does not automate Copilot interaction
- package quality is being tested; real Copilot output quality still requires live manual runs

## Delegated Review Note

A final `gpt-5.4-mini` Codex review contract was packaged and used for a last readiness check.

Its main job was to answer:

- are there any blockers left
- are we preserving the right evidence
- should we stop iterating on framework work and start manual evals

Delegated verdict:

- no blockers found
- go for manual Copilot dogfooding

Nice-to-have follow-ups from that review:

- reduce the manual `repo_path` edit step for non-local checkouts
- add a later helper for path substitution
- optionally add a tiny fixture reset helper to reduce operator overhead

## Next Action

Do not add more framework work first.

Run 1 to 2 real manual Copilot tasks from the suite and inspect:

1. operator friction
2. fairness of the comparison
3. whether `agent-job` materially improves reviewability or scope control

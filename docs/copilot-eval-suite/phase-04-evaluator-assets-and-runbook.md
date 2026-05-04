# Phase 4: Evaluator Assets and Runbook

## Purpose

Turn the raw tasks into an executable human workflow with a shared rubric, result templates, and explicit operating instructions.

## Scope

- finish suite root docs
- finalize scoring rubric
- finalize operator runbook
- define result capture shape
- define aggregation summary template

## Required Artifacts

- `evals/copilot-run/README.md`
- `evals/copilot-run/evaluator-rubric.md`
- `evals/copilot-run/runbook.md`
- `evals/copilot-run/result-template.md`
- `evals/copilot-run/aggregate-template.md`

## Rubric Requirements

Dimensions:

- task clarity
- scope control
- changed-file discipline
- acceptance criteria satisfaction
- evidence quality
- test reporting quality
- safety
- human reviewability
- friction
- overall usefulness

For each dimension, define:

- score 1
- score 3
- score 5

Special penalties:

- unsupported test-pass claims
- forbidden-path changes
- broad unrelated rewrites
- verbosity that makes the workflow harder to use

## Runbook Requirements

Must specify:

- fixture prep
- reset strategy between A/B runs
- exact baseline run steps
- exact `agent-job package` steps
- exact evaluation prompt step
- result storage layout
- human review role

## Result Capture Rules

Store per task:

- baseline prompt
- baseline response
- baseline diff summary
- agent-job prompt path
- agent-job response
- agent-job diff summary
- evaluator output
- optional human override

## Exit Gate

Phase 4 is done when:

- a human can run one task end to end without inventing steps
- the rubric defines scores clearly enough to compare runs
- the aggregate template can summarize multiple task results manually

## Do Not Do Yet

- do not build parsers or dashboards unless trivial
- do not add telemetry or auto-ingestion

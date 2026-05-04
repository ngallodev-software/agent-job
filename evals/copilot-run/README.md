# Copilot-Run Evals for agent-job

## Purpose

This suite measures whether `agent-job` improves Copilot-assisted engineering work compared with a competent plain markdown prompt.

It is designed for human-run A/B evaluation:

- Run A: baseline prompt
- Run B: `agent-job` generated Copilot package prompt

## What These Evals Measure

- task clarity
- scope control
- changed-file discipline
- acceptance criteria satisfaction
- evidence quality
- test reporting quality
- safety
- reviewability
- operator friction
- overall usefulness

## What These Evals Do Not Measure

- direct Copilot automation
- autonomous completion ingestion
- telemetry or dashboard metrics
- large-project performance
- Codex execution quality

## Required Environment

- a Copilot-capable environment such as Copilot Chat or Copilot Workspace
- local checkout of this repo
- Python 3
- `agent-job` available by direct path or shell command

Optional:

- Copilot model registry synced for the current user

## Quick Start

1. prepare the fixture repo
2. choose one task under `tasks/`
3. run the baseline prompt in Copilot
4. reset the fixture repo
5. generate the `agent-job` package prompt
6. run the generated prompt in Copilot
7. use the evaluator prompt to compare both runs
8. record the result with `result-template.md`

## Eval Structure

- `fixtures/sample-repo/`: tiny repeatable fixture repo
- `tasks/<task-id>/`: per-task prompts and job files
- `results/`: captured run outputs
- `evaluator-rubric.md`: scoring rules
- `runbook.md`: exact operator workflow
- `result-template.md`: per-task result record
- `aggregate-template.md`: multi-task summary

## How to Run One Task

Use the instructions in `runbook.md`.

Do not improvise the A/B flow. The suite is only useful if both runs use the same task, the same fixture state, and the same reviewer rubric.

## How to Compare Baseline vs Agent-Job

- compare the actual Copilot responses
- compare changed files and diff scope
- compare tests run or claimed
- compare how clearly success was bounded
- compare review burden

Do not reward structure by default. Reward only what improved the work.

## How to Score Results

Use `evaluator-rubric.md`.

Allowed outcomes:

- `agent-job clearly better`
- `agent-job slightly better`
- `roughly equal`
- `baseline better`
- `inconclusive`

## How to Interpret Results

The suite is not trying to prove `agent-job` wins.

The question is whether the packaging workflow creates enough real value to justify the extra operator steps.

## Decision Thresholds

Strong evidence to continue:

- `agent-job` wins on at least 4 of 6 tasks
- average score delta is at least `+0.75`
- reviewability improves by at least `+1.0`
- safety or scope control clearly improves
- friction remains acceptable

Simplify:

- `agent-job` wins on 2 to 3 tasks
- value exists but overhead is high
- prompts are too long or too rigid

Stop or redesign:

- baseline wins or ties on most tasks
- `agent-job` increases confusion
- Copilot ignores the structure
- human review is not improved
- package workflow is too cumbersome

## Limitations

- human review is still required
- Copilot behavior may vary across environments and org policy
- this is a small-task suite, not a full production benchmark
- fixture tasks are realistic but intentionally bounded

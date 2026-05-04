# Phase 3: Task Authoring

## Purpose

Author the six paired eval tasks so each compares a competent baseline prompt against a structured `agent-job` package for the same work.

## Scope

Per task, create:

- `baseline-prompt.md`
- `agent-job.job.yaml`
- `evaluator-prompt.md`
- `expected-signals.md`

## Task Set

1. `01-docs-consistency`
2. `02-small-bugfix`
3. `03-small-refactor`
4. `04-test-addition`
5. `05-scope-boundary`
6. `06-ambiguous-request`

## Authoring Rules

### Baseline Prompt

Must include:

- objective
- enough context to be competent
- requested output summary
- reminder to avoid unrelated changes

Must not include:

- full schema structure
- artificially weak instructions
- hidden traps not shared by the `agent-job` version

### agent-job.job.yaml

Must include:

- schema v2
- objective
- context
- allowed paths
- forbidden paths
- constraints
- acceptance criteria
- output contract
- Copilot execution intent
- no auto-commit
- no auto-push
- human review expectation

### evaluator-prompt.md

Must:

- compare baseline vs `agent-job`
- instruct Copilot to be skeptical
- score with evidence
- allow `baseline better`
- allow `roughly equal`
- allow `inconclusive`

### expected-signals.md

Must define:

- what a strong `agent-job` win would look like
- what a baseline win would look like
- red flags that invalidate confidence

Must not define:

- exact code output
- one predetermined winner

## Recommended Sequence

Author in this order:

1. docs consistency
2. small bugfix
3. test addition
4. small refactor
5. scope boundary
6. ambiguous request

Reason:

- easiest tasks establish prompt style first
- later tasks stress ambiguity and scope control after the template language is stable

## Exit Gate

Phase 3 is done when:

- all 6 task folders contain all 4 files
- each task pair is semantically equivalent
- no baseline prompt is intentionally weak
- each job file is structurally ready for validation

## Do Not Do Yet

- do not start collecting eval results
- do not add more than 6 tasks in the first pass

# Copilot Eval Suite Implementation Plan

This directory holds the source prompt and the phased implementation plan for the Copilot-run eval suite.

Files:

- `source-prompt.md`: original implementation prompt moved from repo root
- `phase-01-repo-audit-and-shape.md`
- `phase-02-fixture-and-suite-scaffold.md`
- `phase-03-task-authoring.md`
- `phase-04-evaluator-assets-and-runbook.md`
- `phase-05-validation-and-readiness.md`

## Goal

Build a human-run, Copilot-only evaluation suite that compares:

- a competent baseline Copilot prompt
- an `agent-job` Copilot package prompt

for the same small engineering tasks.

The suite should answer:

> Does `agent-job` materially improve Copilot-assisted engineering work over a normal competent prompt?

## Tight Phase Order

1. Repo audit and suite shape
2. Fixture repo and scaffold
3. Task authoring
4. Evaluator assets and operator workflow
5. Validation and readiness gate

## Delivery Rule

Do not build extras before the previous phase passes its gate.

Specifically avoid:

- dashboards
- telemetry
- Copilot automation
- fake eval results
- broad framework work

## Global Acceptance Standard

The suite is implementation-ready when:

- every task has both prompt modes
- every `agent-job.job.yaml` validates
- Copilot package generation works for every task
- the fixture repo is small and repeatable
- the runbook is explicit enough for a human to execute without guessing
- scoring allows `baseline better`, `roughly equal`, and `inconclusive`

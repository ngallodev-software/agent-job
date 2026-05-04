# Phase 5: Validation and Readiness Gate

## Purpose

Prove the suite is internally consistent and ready for real Copilot dogfooding.

## Scope

- run static suite checks
- validate every `agent-job.job.yaml`
- render/package each task for Copilot
- fix wording or path issues
- record remaining known limitations

## Validation Commands

Minimum:

```bash
python3 evals/copilot-run/self_check.py
```

If `agent-job` is available:

```bash
agent-job validate evals/copilot-run/tasks/<task-id>/agent-job.job.yaml
agent-job package evals/copilot-run/tasks/<task-id>/agent-job.job.yaml --target copilot
```

Run that for all 6 tasks.

## What To Check

- all required files exist
- all task folders are complete
- no baseline prompt is empty
- no evaluator prompt is empty
- no task prompt says Codex is the required executor
- all job files validate
- all job files package successfully
- generated prompts are readable enough to paste into Copilot

## Recommended Final Fixes Only

- adjust wording for clarity
- adjust path placeholders
- tighten acceptance criteria
- tighten forbidden-path language
- remove accidental bias favoring either side

## Final Readiness Gate

The suite is ready when:

- all six tasks validate and package
- the runbook is executable by a human
- the rubric is skeptical and evidence-based
- the fixture repo is stable and small
- the suite still allows `baseline better` as a valid result

## Post-Phase Outcome

Once Phase 5 passes, the next action is not more framework work.

The next action is:

1. run 1 or 2 tasks manually in Copilot
2. inspect friction and fairness
3. only then decide whether the suite needs expansion or simplification

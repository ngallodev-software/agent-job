# Phase 1: Repo Audit and Suite Shape

## Purpose

Confirm the current `agent-job` surface, choose the exact eval suite root, and lock the suite contract before creating fixtures or tasks.

## Scope

- inspect current `agent-job` CLI behavior
- confirm schema v2 expectations
- confirm Copilot render/package path
- inspect examples and tests that can be reused
- choose the final eval directory shape

## Outputs

1. Short repo audit note
2. Final suite structure decision:
   - `evals/copilot-run/`
   - `evals/copilot-run/tasks/`
   - `evals/copilot-run/fixtures/sample-repo/`
   - `evals/copilot-run/results/`
3. Decision on fixture path strategy:
   - absolute paths in checked-in YAML with placeholder replacement
   - or generated YAML from templates
4. Decision on whether `self_check.py` is included in first pass

## Key Decisions To Lock

- `agent-job` remains package-only for Copilot
- no direct Copilot execution support is assumed
- the suite uses a tiny Python stdlib fixture repo
- baseline prompts must be competent, not weak on purpose
- evaluation scoring must permit `agent-job` to lose or tie

## Recommended Implementation

- use a checked-in fixture repo under `evals/copilot-run/fixtures/sample-repo/`
- use checked-in job templates with a clear repo-path placeholder
- add a tiny helper later only if placeholder substitution becomes awkward
- include `self_check.py` in the first implementation because it is cheap and protects the suite contract

## Exit Gate

Phase 1 is done when:

- the suite directory plan is fixed
- the fixture strategy is fixed
- the operator workflow is fixed at a high level
- no unresolved CLI/schema assumption remains

## Do Not Do Yet

- do not write all task content
- do not build result aggregation logic
- do not create a large fixture app

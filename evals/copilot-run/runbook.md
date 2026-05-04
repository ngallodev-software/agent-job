# Copilot Eval Runbook

## Setup

1. start from a clean working tree
2. choose a task under `tasks/`
3. prepare a clean reset point for `fixtures/sample-repo/`
4. ensure `agent-job` is runnable

Recommended direct invocation:

```bash
./agent-job/scripts/agent-job
```

## Prepare Fixture Repo

Use the fixture at:

```bash
evals/copilot-run/fixtures/sample-repo/
```

Before each A/B pair:

- create a clean branch in the fixture repo, or
- reset the fixture repo to a known clean state

## Baseline Run

1. open the fixture repo in the Copilot environment
2. paste `baseline-prompt.md` for the task
3. let Copilot perform the task
4. save:
   - Copilot response
   - changed files
   - diff summary
   - tests run or claimed

Store artifacts under:

```text
evals/copilot-run/results/<task-id>/baseline/
```

## Agent-Job Run

1. reset the fixture repo to the same clean state
2. generate the package prompt:

```bash
./agent-job/scripts/agent-job package evals/copilot-run/tasks/<task-id>/agent-job.job.yaml --target copilot
```

3. open the generated `prompt.copilot.md`
4. paste it into Copilot
5. let Copilot perform the task
6. save:
   - Copilot response
   - changed files
   - diff summary
   - tests run or claimed

Store artifacts under:

```text
evals/copilot-run/results/<task-id>/agent-job/
```

## Evaluation Run

1. paste `evaluator-prompt.md` into Copilot
2. provide:
   - baseline prompt
   - baseline response
   - baseline diff summary
   - agent-job prompt
   - agent-job response
   - agent-job diff summary
3. save the output as:

```text
evals/copilot-run/results/<task-id>/evaluation.md
```

## Human Review

Human reviews the evaluator output and overrides it only when the evidence supports that override.

Use `result-template.md` to capture the final record.

## Important Rules

- do not use `run --executor copilot`
- do not use Codex for the A/B runs
- do not use Claude for the A/B runs
- do not auto-commit
- do not auto-push
- do not compare runs from different fixture states

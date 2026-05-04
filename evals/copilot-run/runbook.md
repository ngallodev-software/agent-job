# Copilot Eval Runbook

## Setup

1. start from a clean working tree
2. choose a task under `tasks/`
3. if your repo is not checked out at `/lump/apps/invoke-codex-from-claude`, update `repo_path` in that task’s `agent-job.job.yaml`
4. prepare a clean reset point for `fixtures/sample-repo/`
5. ensure `agent-job` is runnable

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

Suggested reset pattern:

```bash
cd evals/copilot-run/fixtures/sample-repo
git checkout -B eval-<task-id>
git reset --hard
git clean -fd
```

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

Recommended local capture:

- save the baseline prompt text as `prompt.md`
- save the Copilot response as `response.md`
- save changed-file list as `changed-files.txt`
- save `git diff --stat` as `diff-stat.txt`
- save full diff as `diff.patch`
- save tests run or claimed as `tests.txt`

## Agent-Job Run

1. reset the fixture repo to the same clean state
2. generate the package prompt:

```bash
./agent-job/scripts/agent-job package evals/copilot-run/tasks/<task-id>/agent-job.job.yaml --target copilot
```

3. open the generated `prompt.copilot.md`
4. optionally review the package summary:

```bash
./agent-job/scripts/agent-job report runs/<job-id>/<timestamp>-copilot-package
```

5. paste it into Copilot
6. let Copilot perform the task
7. save:
   - Copilot response
   - changed files
   - diff summary
   - tests run or claimed

Store artifacts under:

```text
evals/copilot-run/results/<task-id>/agent-job/
```

Recommended local capture:

- save the generated packaged prompt as `prompt.copilot.md`
- keep the full packaged run directory under `runs/<job-id>/<timestamp>-copilot-package/`
- save the Copilot response as `response.md`
- save changed-file list as `changed-files.txt`
- save `git diff --stat` as `diff-stat.txt`
- save full diff as `diff.patch`
- save tests run or claimed as `tests.txt`
- save the generated package `meta.json`
- save the generated package `checklist.md`
- save the generated package `report-template.md`

## Evaluation Run

1. paste `evaluator-prompt.md` into Copilot
2. provide:
   - baseline prompt
   - baseline response
   - baseline changed files
   - baseline diff summary
   - baseline tests run or claimed
   - agent-job prompt
   - agent-job response
   - agent-job changed files
   - agent-job diff summary
   - agent-job tests run or claimed
   - agent-job package `meta.json`
3. save the output as:

```text
evals/copilot-run/results/<task-id>/evaluation.md
```

## Human Review

Human reviews the evaluator output and overrides it only when the evidence supports that override.

Use `result-template.md` to capture the final record.

When in doubt, prefer:

- lower scores for unsupported claims
- lower scores for unnecessary scope growth
- `roughly equal` over inventing a winner
- the evidence over the evaluator's rhetoric

## Important Rules

- do not use `run --executor copilot`
- do not use Codex for the A/B runs
- do not use Claude for the A/B runs
- do not auto-commit
- do not auto-push
- do not compare runs from different fixture states
- do not score from memory; score from the captured artifacts

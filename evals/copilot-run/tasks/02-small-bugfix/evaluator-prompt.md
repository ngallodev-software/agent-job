# Copilot Eval: Small Bugfix

You are evaluating two Copilot-assisted runs of the same small bugfix.

- Run A used a normal competent prompt.
- Run B used an `agent-job` Copilot package.

Evaluate whether Run B added real value.

For this task, focus especially on:

- whether the bug target was clear
- whether the changed files stayed narrow
- whether tests were run or only claimed
- whether the final explanation is easy to audit

Use this scale:

- `1` = poor
- `2` = weak
- `3` = acceptable
- `4` = good
- `5` = excellent

Return:

| Dimension | Baseline Score | Agent-Job Score | Delta | Evidence |
|---|---:|---:|---:|---|

Compare:

- task clarity
- scope control
- changed-file discipline
- acceptance criteria satisfaction
- evidence quality
- test reporting quality
- safety
- reviewability
- friction
- overall usefulness

Then answer:

- Did agent-job clearly improve the workflow?
- Did agent-job add too much friction?
- Did either run make unsupported claims?
- Did either run touch unrelated files?
- Which workflow would you prefer for paid engineering work?
- Overall result: `agent-job clearly better` / `agent-job slightly better` / `roughly equal` / `baseline better` / `inconclusive`

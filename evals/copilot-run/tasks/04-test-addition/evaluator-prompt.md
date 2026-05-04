# Copilot Eval: Test Addition

You are evaluating two Copilot-assisted runs of the same test-addition task.

- Run A used a competent baseline prompt.
- Run B used an `agent-job` Copilot package prompt.

For this task, focus especially on:

- whether the run stayed test-only
- whether the added test is specific and meaningful
- whether tests run are reported clearly
- whether the final output is easy for a human reviewer to audit

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

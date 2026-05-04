# Copilot Eval: Small Refactor

You are comparing two Copilot-assisted runs of the same small refactor.

- Run A used a competent baseline prompt.
- Run B used an `agent-job` Copilot package prompt.

Evaluate whether Run B improved the workflow without rewarding structure for its own sake.

For this task, pay extra attention to:

- scope creep
- behavior preservation
- whether the change stayed small
- whether tests were used to support the no-behavior-change claim

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

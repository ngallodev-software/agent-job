# Copilot Eval: Docs Consistency

You are comparing two Copilot-assisted runs of the same docs task in a tiny fixture repo.

- Run A used a competent plain markdown prompt.
- Run B used an `agent-job` Copilot package prompt.

Evaluate whether Run B added value over Run A.

Be skeptical.

Do not favor Run B just because it is more structured.
Do not favor Run A just because it is shorter.

For this task, pay extra attention to:

- command accuracy
- changed-file discipline
- whether the run stayed inside README.md
- whether the summary and risk notes are useful to a reviewer

Use this scale:

- `1` = poor
- `2` = weak
- `3` = acceptable
- `4` = good
- `5` = excellent

Return this table:

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

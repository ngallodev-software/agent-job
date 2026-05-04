# Copilot Eval: Ambiguous Request

You are comparing two Copilot-assisted runs of the same intentionally ambiguous task.

- Run A used a competent baseline prompt.
- Run B used an `agent-job` Copilot package prompt.

The key question is whether Run B reduced ambiguity enough to improve the work without adding too much friction.

Pay extra attention to:

- whether the success criteria became clearer
- whether the change stayed bounded
- whether either run overengineered the formatter
- whether the final explanation makes review easier

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

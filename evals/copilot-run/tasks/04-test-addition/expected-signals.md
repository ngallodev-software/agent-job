# Expected Signals

A strong `agent-job` win would show:

- a focused test-only diff
- no opportunistic source edits
- clear explanation of what behavior is now covered
- precise test command reporting

A baseline win would show:

- equally focused coverage and equally honest reporting
- no need for the extra package structure

Red flags:

- source file changes despite a test-only scope
- vague or redundant tests
- unsupported “all tests passed” claims

# Expected Signals

A strong `agent-job` win would show:

- source change stayed within the allowed file set
- README.md remained untouched
- test additions, if any, were tightly coupled to the requested behavior
- the final report explicitly notes the bounded scope

A baseline win would show:

- equally disciplined file scope
- no unrelated cleanup
- no need for the structured package to maintain control

Red flags:

- README changes
- broad cleanup in path_policy.py
- extra refactors outside the requested improvement

# Sample Repo

This is a tiny fixture repo for the `agent-job` Copilot eval suite.

## Purpose

The fixture is intentionally small and supports six bounded eval tasks:

- docs consistency
- small bugfix
- small refactor
- test addition
- scope boundary
- ambiguous improvement request

## Running Tests

Run the unit tests with:

```bash
python3 -m unittest discover -s tests
```

## Notes

- `src/calculator.py` contains a small arithmetic issue that is not fully covered by tests yet.
- `src/report_formatter.py` contains a small readability/refactor target and an under-tested formatting path.
- `src/path_policy.py` is useful for scope-boundary tasks.
- Keep changes focused. This fixture is not meant to become a real application.

# Gemini Support Deprecation

Date: 2026-04-13
Reason: Dead-end feature, not part of core skill vision

## Moved to deprecated/

### Scripts
- `codex-job/scripts/run_gemini_task.sh`
- `codex-job/scripts/invoke_gemini_with_review.sh`
- `codex-job/scripts/parse_gemini_run.py`

### Tests
- `tests/fake_gemini.sh`
- `tests/test_gemini_runner_and_parser.sh`

### Run Artifacts
- Various `runs/gemini-run-*.meta.json` and `runs/gemini-run-*.summary.json` files remain in runs/ for historical reference

## References Still in Docs

The following documentation still mentions Gemini but will not be updated to remove references (low priority):
- README.md (mentions Gemini variant)
- codex-job/references/metrics-schema.md
- CONTRIBUTING.md
- docs/STEERING.md
- agent-notes/go-live-rec-detailed-plan.md
- agent-notes/session-handoff-2026-02-18-phase2-3.md
- docs/PROJECT-SUMMARY.md

Consider these historical references. The skill no longer supports Gemini delegation.

## Rationale

Focus on Claude → Codex delegation pattern. Gemini support was experimental and never reached production quality.

# Repository Reorganization Summary

Date: 2026-04-13
Status: IN PROGRESS

## Completed

✅ Created directory structure (deprecated/, future-plans/, repo-dev-agents/)
✅ Updated .gitignore for untracked files
✅ Analyzed and categorized all agents (see AGENT-CATEGORIZATION.md)
✅ Identified future-plans content (see FUTURE-PLANS-INVENTORY.md)
✅ Compared duplicate files (see DUPLICATE-FILES-ANALYSIS.md)
✅ Moved Gemini code to deprecated/ with deprecation note
✅ Created available_models.jsonl in codex-job/references/
✅ Removed hardcoded model names from:
  - codex-job/scripts/run_codex_task.sh (map_tier_to_model function)
  - codex-job/references/invocation-patterns.md
  - codex-job/scripts/codex_task.py
✅ Consolidated SKILL.md (merged best of both versions)
✅ Added fork vs subagent guidance to SKILL.md
✅ Moved .claude/skills/codex-job/ to deprecated/

## Remaining File Moves

### Agents (18 files)
Move from `.claude/agents/team/` to new locations:

**To future-plans/agents/** (7 UI/control-plane agents):
- ui-product-designer.md
- data-viz-ux.md
- job-queue-designer.md
- frontend-test-engineer.md
- design-system-engineer.md
- frontend-state-architect.md
- accessibility-qa.md

**To repo-dev-agents/** (11 skill development agents):
- model-tier-integrator.md
- technical-writer.md
- installation-engineer.md
- bash-error-handling-specialist.md
- test-generator-shell.md
- json-minimizer.md
- security-hardener.md
- self-diagnosis-creator.md
- caching-architect.md
- python-post-processor.md
- webhook-signer.md

### Future-Plans Content
- ui/ → future-plans/ui/
- codex-job/scripts/job_queue.py → future-plans/queue/
- codex-job/scripts/job_queue_server.py → future-plans/queue/
- codex-job/assets/job-dashboard.html → future-plans/queue/ (dashboard for queue)
- scripts/bootstrap_ui.sh → future-plans/scripts/
- scripts/ui_doctor.sh → future-plans/scripts/
- docs/STEERING.md → future-plans/docs/
- docs/ADR-*.md (4 files) → future-plans/docs/
- docs/UI-SKILLS-AND-PLUGINS-SETUP.md → future-plans/docs/
- docs/IDEAS-next-architecture-sprints.md → future-plans/docs/
- agent-notes/.ignore-for-now/*.md → future-plans/planning/
- agent-notes/go-live-*.md → future-plans/planning/
- agent-notes/mvp-architecture-reassessment.md → future-plans/planning/
- agent-notes/session-handoff-*-phase2-3.md → future-plans/planning/

## Still TODO

- [ ] Execute agent file moves
- [ ] Execute future-plans content moves
- [ ] Update README.md
- [ ] Update CLAUDE.md
- [ ] Update install scripts if needed
- [ ] Fix delegation issue documentation
- [ ] Commit and push to remote

## Notes

- Root /scripts/ are wrappers (KEEP, not duplicates)
- Codex-job/scripts/ is canonical implementation
- Model selection now tier-based via available_models.jsonl
- Gemini support deprecated

# Agent Categorization Analysis

Generated: 2026-04-13
Task: Analyze .claude/agents/team/ to determine repo-dev vs future-plans vs skill-useful

## Summary

- **Future-Plans (UI/Control-Plane)**: 7 agents → move to future-plans/agents/
- **Repo-Dev (Skill Development)**: 9 agents → move to repo-dev-agents/
- **Skill-Useful (Potentially)**: 2 agents → analyze for Python conversion or deprecation

## Future-Plans Agents (Multi-Agent Orchestration Control Plane)

These align with STEERING.md's vision for the orchestration control plane UI, not the simple Claude delegation skill.

1. **ui-product-designer** - UX flows for orchestration, approvals, run timelines
2. **data-viz-ux** - Dashboards for tokens, costs, queue health, policy decisions
3. **job-queue-designer** - Job queue with dashboard (already partially implemented in codex-job/scripts/job_queue*.py)
4. **frontend-test-engineer** - UI test coverage for control-plane workflows
5. **design-system-engineer** - UI tokens, components, accessibility baselines
6. **frontend-state-architect** - Client-side state for control-plane UIs
7. **accessibility-qa** - WCAG compliance for orchestration UI

**Action**: Move to `future-plans/agents/`

## Repo-Dev Agents (Skill Development & Maintenance)

These are useful for developing THIS repo's skill code, but not for distribution with the skill.

1. **model-tier-integrator** - Implements tier-based model selection (ALREADY COMPLETED - this work is done)
2. **technical-writer** - Produces README/CONTRIBUTING docs
3. **installation-engineer** - Improves install/uninstall scripts
4. **bash-error-handling-specialist** - Hardens bash scripts
5. **test-generator-shell** - Expands test coverage for scripts
6. **json-minimizer** - Optimizes summary JSON schema
7. **security-hardener** - Audits scripts for secret safety
8. **self-diagnosis-creator** - Adds --doctor diagnostics
9. **caching-architect** - Implements result caching (ALREADY IMPLEMENTED in run_codex_task.sh)

**Action**: Move to `repo-dev-agents/`

**Note**: model-tier-integrator and caching-architect have already completed their work. Their specs are historical context.

## Skill-Useful Agents (Needs Analysis)

These might be useful as part of the skill, but agents shouldn't nest under skill structure.

1. **python-post-processor** - Creates deterministic Python utilities to replace LLM post-processing
   - **Analysis**: This describes a PATTERN (replace LLM calls with deterministic code), not an agent to distribute
   - **Recommendation**: Move to repo-dev-agents/ (useful for skill development, not end-user distribution)

2. **webhook-signer** - Adds HMAC signing to webhook payloads
   - **Analysis**: This is a feature enhancement to notify_claude_hook.sh
   - **Status**: Feature not yet implemented
   - **Recommendation**: Move to repo-dev-agents/ (would be used to BUILD the feature, not distributed)

**Action**: Move both to `repo-dev-agents/`

## Final Distribution

- `future-plans/agents/`: 7 agents (UI/orchestration control plane)
- `repo-dev-agents/`: 11 agents (skill development helpers)
- `deprecated/`: 0 agents (none are obsolete, just misplaced)

## Notes

- No agents should be nested under the skill directory structure (codex-job/)
- Agents are development tools, not runtime components
- The skill itself (codex-job/) should contain only:
  - SKILL.md (instructions)
  - scripts/ (runtime implementation)
  - references/ (documentation, examples)
  - assets/ (templates)

# Future-Plans Content Inventory

Generated: 2026-04-13
Task: Identify content aligned to orchestration control plane (STEERING.md) vs simple Claude delegation skill

## Content to Move to future-plans/

### UI Directory (Entire React Dashboard)
**Location**: `/ui/`
**Reason**: React dashboard for control plane, not needed for simple delegation skill
**Contents**:
- React/Vite/TypeScript application
- src/ components for orchestration UI
- Playwright tests
- package.json with recharts, redux, react-query dependencies

**Action**: Move entire `/ui/` directory to `future-plans/ui/`

---

### Job Queue Implementation
**Files**:
- `codex-job/scripts/job_queue.py` (10KB, Feb 18)
- `codex-job/scripts/job_queue_server.py` (9KB, Feb 18)

**Reason**: Queue + server is part of control plane vision, not simple skill delegation
**Related Docs**: 
- `docs/ADR-0003-persistence-and-queue-strategy.md`
- Agent: job-queue-designer.md

**Action**: Move to `future-plans/queue/`

---

### UI Bootstrap & Doctor Scripts
**Files**:
- `scripts/bootstrap_ui.sh` (960 bytes, Feb 18)
- `scripts/ui_doctor.sh` (1009 bytes, Feb 18)

**Reason**: UI setup/diagnostics for control plane dashboard
**Action**: Move to `future-plans/scripts/`

---

### Control Plane Documentation
**Files**:
- `docs/STEERING.md` - Product vision for orchestration control plane
- `docs/ADR-0001-control-plane-core-architecture.md` - Architecture for multi-agent orchestration
- `docs/ADR-0002-control-plane-language-selection.md` - Language choices for control plane
- `docs/ADR-0003-persistence-and-queue-strategy.md` - Queue & persistence design
- `docs/ADR-0004-event-schema-and-state-machine.md` - Event contracts & state machine
- `docs/UI-SKILLS-AND-PLUGINS-SETUP.md` - UI plugin bootstrap notes
- `docs/IDEAS-next-architecture-sprints.md` - Future architecture ideas

**Reason**: These describe the future orchestration platform, not the current simple skill
**Action**: Move to `future-plans/docs/`

**Keep in docs/**: README, CONTRIBUTING, skill-specific docs

---

### Phase 2/3 Planning Documents
**Files**:
- `agent-notes/.ignore-for-now/phase2-optimizer.md`
- `agent-notes/.ignore-for-now/phase3-polisher.md`
- `agent-notes/go-live-rec-detailed-plan.md`
- `agent-notes/go-live-recomendations.md`
- `agent-notes/mvp-architecture-reassessment.md`
- `agent-notes/session-handoff-2026-02-18-phase2-3.md`

**Reason**: Planning for control plane phases beyond simple skill
**Action**: Move to `future-plans/planning/`

---

## Summary

Move to `future-plans/`:
- `ui/` → `future-plans/ui/`
- `codex-job/scripts/job_queue*.py` → `future-plans/queue/`
- `scripts/bootstrap_ui.sh`, `scripts/ui_doctor.sh` → `future-plans/scripts/`
- Control plane ADRs and STEERING.md → `future-plans/docs/`
- Phase 2/3 planning docs → `future-plans/planning/`

Keep in main repo (current skill scope):
- `codex-job/` (skill implementation)
- `install*.sh` / `uninstall*.sh` (skill installers)
- `tests/` for skill scripts
- Core skill documentation

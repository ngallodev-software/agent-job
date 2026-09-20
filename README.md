# agent-job — historical predecessor to Agent-Workflow

> **Retired on 2026-09-20. Do not install or use this repository as an active workflow.**

`agent-job` was an intermediate executor-neutral architecture between the earlier `codex-job` work and the current **Agent-Workflow** product. Its last development activity was May 4, 2026.

Active development moved to:

- https://github.com/ngallodev-software/agent-workflow

## What agent-job contributed

This project helped establish several ideas that now exist in stronger form in Agent-Workflow:

- executor-neutral bounded work contracts;
- explicit writable/forbidden scope;
- package/preparation without pretending execution occurred;
- separation of agent claims from executor observations;
- human-review-first completion;
- target-specific rendering for external execution environments;
- comparative evaluation of plain prompting versus structured workflow prompting.

Those ideas are preserved through Agent-Workflow's Agent Run contracts, prompt packs, external-worker boundary, provider/provenance evidence, evaluation, independent review, acceptance, and comparative benchmark system.

## What is not being carried forward

The following are historical implementation details, not compatibility surfaces:

- schema v1/v2 `agent-job` job files;
- Copilot/manual renderers and package directories;
- the unfinished Codex executor;
- mock-executor runtime behavior;
- Copilot-specific model sync and hand-maintained model-tier selection;
- `agent-job` installers and GitHub skill installation;
- the old `codex-job` copy retained in this repository;
- checkout-specific eval paths and free-form result templates.

Do not add new executor support or finish the old migration plan here.

## Preserved benchmark research

The six-task Copilot A/B evaluation suite remains useful as historical research input. It covered:

1. documentation consistency;
2. a small bugfix;
3. a small behavior-preserving refactor;
4. test-only coverage;
5. scope-boundary discipline;
6. an intentionally ambiguous request.

The valuable experimental principle was to ask whether added workflow structure justified its friction, not to assume the structured arm should win. Agent-Workflow now tracks re-authoring those task classes under its current comparative benchmark contracts.

See [MIGRATION.md](MIGRATION.md) for the detailed mapping.

## Local cleanup

Historical installs may exist in one or more of these places:

- `~/.local/share/agent-job`
- `~/.local/bin/agent-job`
- shell profile blocks marked `agent-job path (agent-job)`
- a GitHub/Copilot-installed `agent-job` skill

Use the retained uninstall script or remove stale local copies carefully. Do not reinstall from this repository.

## Repository status

The implementation, eval assets, documents, and Git history are retained for source archaeology. Install entrypoints are intentionally disabled. No feature development should occur here; useful concepts should be implemented in Agent-Workflow instead.

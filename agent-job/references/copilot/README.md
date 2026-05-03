# Copilot Model Registry

This directory holds the user-specific GitHub Copilot model registry for `agent-job`.

## Purpose

Different users can see different Copilot models depending on:

- GitHub plan
- organization policy
- Copilot subscription level
- model rollout state

Do not hardcode model lists in prompts, docs, or runtime logic. Refresh this registry for the current user instead.

## Canonical Files

- [available_models.copilot.jsonl](/lump/apps/invoke-codex-from-claude/agent-job/references/copilot/available_models.copilot.jsonl): filtered machine-readable registry used by the skill
- [available_models.raw.json](/lump/apps/invoke-codex-from-claude/agent-job/references/copilot/available_models.raw.json): raw Copilot SDK response
- [available-models.md](/lump/apps/invoke-codex-from-claude/agent-job/references/copilot/available-models.md): human override file for tier and preference metadata
- [available-models.template.json](/lump/apps/invoke-codex-from-claude/agent-job/references/copilot/available-models.template.json): filtered JSON preview of the final registry

## Install

From the repo root:

```bash
npm install
```

Requirements:

- Node `>=22`
- GitHub Copilot access for the current user
- one of:
  - `GITHUB_TOKEN`
  - `GH_TOKEN`
  - an SDK-usable local Copilot auth/session

## Refresh the Registry

From the repo root:

```bash
npm run copilot:models:sync
```

This sequence:

1. fetches the raw Copilot model list for the current user
2. writes `available_models.raw.json`
3. applies local overrides from `available-models.md`
4. writes `available-models.template.json`
5. writes `available_models.copilot.jsonl`

You can also fetch only the raw payload:

```bash
npm run copilot:models:fetch
```

## Customizing Preferred Models

Edit [available-models.md](/lump/apps/invoke-codex-from-claude/agent-job/references/copilot/available-models.md), then rerun:

```bash
npm run copilot:models:sync
```

Line format:

```text
model-id, 1.0x, medium tier
model-id, 1.0x, medium tier, recommended
```

Notes:

- entries in `available-models.md` are overrides, not the source of truth for what models exist
- only models returned by Copilot fetch will appear in the generated registry
- `recommended` sets `recomended: true` in the generated JSONL
- `recomended` is intentionally spelled that way in output for compatibility with the current skill surface

## Fields the Skill Should Use

The main fields to read from `available_models.copilot.jsonl` are:

- `model_id`
- `tier`
- `recomended`
- `token_cost_multiplier`
- `policy_state`
- `supported_reasoning_efforts`
- `default_reasoning_effort`

Treat other fields as supporting metadata unless a new feature explicitly needs them.

## Selection Guidance

When choosing a model:

1. require `policy_state == "enabled"`
2. prefer `recomended == true`
3. then choose by `tier`
4. if reasoning level matters, check `supported_reasoning_efforts`

If a fetched model is missing a tier override, add it to `available-models.md` and rerun sync.

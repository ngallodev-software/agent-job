#!/usr/bin/env python3
"""Registry-backed model selection for agent-job packaging and prompts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ModelSelection:
    """Resolved model selection for a job."""

    model_id: str
    source: str
    tier: str | None
    recommended: bool
    policy_state: str | None
    available_in_registry: bool


def _registry_path() -> Path:
    return Path(__file__).resolve().parent.parent / "references" / "copilot" / "available_models.copilot.jsonl"


def _load_registry_models() -> list[dict[str, Any]]:
    registry_path = _registry_path()
    if not registry_path.exists():
        raise FileNotFoundError(f"Copilot model registry not found: {registry_path}")
    models: list[dict[str, Any]] = []
    for line in registry_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        parsed = json.loads(line)
        if isinstance(parsed, dict):
            models.append(parsed)
    return models


def _enabled_models(models: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [model for model in models if model.get("policy_state") == "enabled" and model.get("model_id")]


def _model_sort_key(model: dict[str, Any]) -> tuple[int, float, str]:
    recommended = bool(model.get("recomended"))
    multiplier = model.get("token_cost_multiplier")
    if not isinstance(multiplier, (int, float)):
        multiplier = 999999.0
    model_id = str(model.get("model_id") or "")
    return (0 if recommended else 1, float(multiplier), model_id)


def _select_for_tiers(models: list[dict[str, Any]], tiers: list[str]) -> dict[str, Any] | None:
    for tier in tiers:
        matches = [model for model in models if model.get("tier") == tier]
        if matches:
            return sorted(matches, key=_model_sort_key)[0]
    return None


def resolve_job_model(job: Any) -> ModelSelection:
    """Resolve an explicit or default model for the job."""
    explicit_model = getattr(job, "model", None)
    explicit_tier = getattr(job, "model_tier", None)

    if explicit_model:
        try:
            enabled = _enabled_models(_load_registry_models())
        except FileNotFoundError:
            return ModelSelection(
                model_id=explicit_model,
                source="execution.model",
                tier=explicit_tier,
                recommended=False,
                policy_state=None,
                available_in_registry=False,
            )
        for model in enabled:
            if model.get("model_id") == explicit_model:
                return ModelSelection(
                    model_id=explicit_model,
                    source="execution.model",
                    tier=model.get("tier") if isinstance(model.get("tier"), str) else explicit_tier,
                    recommended=bool(model.get("recomended")),
                    policy_state=model.get("policy_state") if isinstance(model.get("policy_state"), str) else None,
                    available_in_registry=True,
                )
        return ModelSelection(
            model_id=explicit_model,
            source="execution.model",
            tier=explicit_tier,
            recommended=False,
            policy_state=None,
            available_in_registry=False,
        )

    enabled = _enabled_models(_load_registry_models())
    if not enabled:
        raise ValueError("Copilot model registry has no enabled models")

    if explicit_tier:
        tier_order = [explicit_tier]
    else:
        tier_order = ["medium", "low", "very-low", "high"]

    selected = _select_for_tiers(enabled, tier_order)
    if selected is None:
        selected = sorted(enabled, key=_model_sort_key)[0]

    return ModelSelection(
        model_id=str(selected["model_id"]),
        source="registry_default",
        tier=selected.get("tier") if isinstance(selected.get("tier"), str) else explicit_tier,
        recommended=bool(selected.get("recomended")),
        policy_state=selected.get("policy_state") if isinstance(selected.get("policy_state"), str) else None,
        available_in_registry=True,
    )

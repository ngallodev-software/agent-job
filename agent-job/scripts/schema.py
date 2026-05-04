#!/usr/bin/env python3
"""Universal agent job schema: v1 (legacy) and v2 (executor-neutral)."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

try:
    import yaml
except ImportError as exc:
    print("error: PyYAML is required (python3 -m pip install pyyaml)", file=sys.stderr)
    raise SystemExit(2) from exc


class ValidationError(Exception):
    """Raised when a job file fails validation."""


MAX_JOB_BYTES = 64 * 1024
TASK_TYPES = {"implementation", "bugfix", "refactor", "test", "docs", "analysis"}
EXECUTION_MODES = {"agent", "human", "ci"}
KNOWN_EXECUTORS = {"codex", "mock", "human"}  # copilot not executable
KNOWN_TARGETS = {"copilot", "manual", "codex", "claude"}
KNOWN_MODEL_TIERS = {"very-low", "low", "medium", "high"}


@dataclass(frozen=True)
class JobV2:
    """Schema v2: Executor-neutral job specification."""

    schema_version: int
    job_id: str
    title: str
    repo_path: Path
    branch: str | None

    # Task section
    task_type: str
    objective: str
    context: str
    constraints: list[str]
    acceptance_criteria: list[str]

    # Scope section
    allowed_paths: list[str]
    forbidden_paths: list[str]

    # Execution section
    mode: str
    preferred_executor: str | None
    model: str | None
    model_tier: str | None
    allowed_executors: list[str]
    disallowed_executors: list[str]
    commands_allowed: list[str]
    commands_forbidden: list[str]
    test_commands: list[str]

    # Output contract
    output_contract: dict[str, bool]

    # Provenance requirements
    provenance_config: dict[str, bool]

    # Metadata
    created_by: str
    created_at: str
    source_path: Path


def load_yaml_file(job_path: Path) -> dict[str, Any]:
    """Load and parse YAML job file."""
    if not job_path.exists():
        raise ValidationError(f"job file not found: {job_path}")
    if not job_path.is_file():
        raise ValidationError(f"job path is not a file: {job_path}")
    size = job_path.stat().st_size
    if size > MAX_JOB_BYTES:
        raise ValidationError(f"job file too large: {job_path} ({size} bytes > {MAX_JOB_BYTES} bytes)")
    try:
        raw = yaml.safe_load(job_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValidationError(f"malformed YAML: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValidationError("job file must be a YAML mapping at the top level")
    return raw


def require_string(raw: Mapping[str, Any], key: str, *, allow_empty: bool = False) -> str:
    """Extract required string field."""
    value = raw.get(key)
    if not isinstance(value, str):
        raise ValidationError(f"{key} must be a string")
    if not allow_empty and not value.strip():
        raise ValidationError(f"{key} must not be empty")
    return value


def optional_string(raw: Mapping[str, Any], key: str) -> str | None:
    """Extract optional string field."""
    value = raw.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValidationError(f"{key} must be a string or null")
    trimmed = value.strip()
    return trimmed or None


def parse_timestamp(raw_value: str, key: str) -> str:
    """Validate ISO-8601 timestamp."""
    try:
        datetime.fromisoformat(raw_value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValidationError(f"{key} must be a valid ISO-8601 timestamp") from exc
    return raw_value


def require_timestamp(raw: Mapping[str, Any], key: str) -> str:
    """Extract required timestamp field."""
    value = raw.get(key)
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    if not isinstance(value, str):
        raise ValidationError(f"{key} must be a string")
    return parse_timestamp(value, key)


def validate_list_of_strings(raw: Mapping[str, Any], key: str, *, required: bool = False) -> list[str]:
    """Extract and validate list of strings."""
    value = raw.get(key)
    if value is None:
        if required:
            raise ValidationError(f"{key} is required")
        return []
    if not isinstance(value, list):
        raise ValidationError(f"{key} must be a list")
    out: list[str] = []
    for idx, item in enumerate(value):
        if not isinstance(item, str):
            raise ValidationError(f"{key}[{idx}] must be a string")
        trimmed = item.strip()
        if not trimmed:
            raise ValidationError(f"{key}[{idx}] must not be empty")
        out.append(trimmed)
    if required and not out:
        raise ValidationError(f"{key} must not be empty")
    return out


def validate_path_entry(raw_value: str, field_name: str, idx: int, repo_path: Path) -> str:
    """Validate a single path entry."""
    if raw_value.startswith("/"):
        raise ValidationError(f"{field_name}[{idx}] must be repo-relative, not absolute")
    raw_path = PurePosixPath(raw_value)
    if raw_path == PurePosixPath(""):
        raise ValidationError(f"{field_name}[{idx}] must not be empty")
    if any(part == ".." for part in raw_path.parts):
        raise ValidationError(f"{field_name}[{idx}] escapes repo via '..'")
    resolved = (repo_path / Path(*raw_path.parts)).resolve(strict=False)
    try:
        resolved.relative_to(repo_path)
    except ValueError as exc:
        raise ValidationError(f"{field_name}[{idx}] resolves outside repo_path") from exc
    return raw_path.as_posix()


def normalize_repo_relative_paths(
    values: list[str], field_name: str, repo_path: Path, *, reject_git: bool = False
) -> list[str]:
    """Normalize and validate repo-relative paths."""
    normalized: list[str] = []
    for idx, value in enumerate(values):
        path_value = validate_path_entry(value, field_name, idx, repo_path)
        if reject_git and (path_value == ".git" or path_value.startswith(".git/")):
            raise ValidationError(f"{field_name}[{idx}] must not target .git")
        normalized.append(path_value)
    return normalized


def validate_output_contract(raw: Mapping[str, Any]) -> dict[str, bool]:
    """Validate output contract section."""
    default = {
        "require_summary": True,
        "require_changed_files": True,
        "require_tests_run": False,
        "require_risks": True,
        "human_review_required": True,
    }
    value = raw.get("output_contract")
    if value is None:
        return default
    if not isinstance(value, dict):
        raise ValidationError("output_contract must be a mapping")
    out = dict(default)
    for key in default:
        if key not in value:
            continue
        if not isinstance(value[key], bool):
            raise ValidationError(f"output_contract.{key} must be a boolean")
        out[key] = value[key]
    unknown = sorted(set(value) - set(default))
    if unknown:
        raise ValidationError(f"output_contract contains unknown keys: {', '.join(unknown)}")
    return out


def validate_provenance_config(raw: Mapping[str, Any]) -> dict[str, bool]:
    """Validate provenance configuration section."""
    default = {
        "distinguish_agent_claims": True,
        "require_changed_file_snapshot": True,
        "require_test_evidence": True,
    }
    value = raw.get("provenance")
    if value is None:
        return default
    if not isinstance(value, dict):
        raise ValidationError("provenance must be a mapping")
    out = dict(default)
    for key in default:
        if key not in value:
            continue
        if not isinstance(value[key], bool):
            raise ValidationError(f"provenance.{key} must be a boolean")
        out[key] = value[key]
    unknown = sorted(set(value) - set(default))
    if unknown:
        raise ValidationError(f"provenance contains unknown keys: {', '.join(unknown)}")
    return out


def load_job_v2_from_mapping(raw: Mapping[str, Any], source_path: Path) -> JobV2:
    """Validate a schema v2 mapping and return a JobV2."""
    schema_version = raw.get("schema_version")
    if schema_version != 2:
        raise ValidationError(f"expected schema_version: 2, got {schema_version!r}")

    job_id = require_string(raw, "id")
    if not re.fullmatch(r"[A-Za-z0-9._-]+", job_id):
        raise ValidationError("id contains dangerous characters; use letters, numbers, ., _, -")

    repo_path_value = require_string(raw, "repo_path")
    repo_path = Path(repo_path_value)
    if not repo_path.is_absolute():
        raise ValidationError("repo_path must be absolute")
    if not repo_path.exists():
        raise ValidationError(f"repo_path does not exist: {repo_path}")
    if not repo_path.is_dir():
        raise ValidationError(f"repo_path is not a directory: {repo_path}")
    repo_path = repo_path.resolve()

    title = require_string(raw, "title")
    branch_value = raw.get("branch")
    if branch_value is not None and not isinstance(branch_value, str):
        raise ValidationError("branch must be a string or null")
    branch = branch_value.strip() if isinstance(branch_value, str) and branch_value.strip() else None

    # Task section
    task = raw.get("task")
    if not isinstance(task, dict):
        raise ValidationError("task section must be a mapping")

    task_type = require_string(task, "type")
    if task_type not in TASK_TYPES:
        raise ValidationError(f"unsupported task.type: {task_type!r} (allowed: {', '.join(sorted(TASK_TYPES))})")

    objective = require_string(task, "objective")
    context = optional_string(task, "context") or ""
    constraints = validate_list_of_strings(task, "constraints", required=True)
    acceptance_criteria = validate_list_of_strings(task, "acceptance_criteria", required=True)

    # Scope section
    scope = raw.get("scope")
    if not isinstance(scope, dict):
        raise ValidationError("scope section must be a mapping")

    allowed_paths = normalize_repo_relative_paths(
        validate_list_of_strings(scope, "allowed_paths", required=True),
        "scope.allowed_paths",
        repo_path,
        reject_git=True,
    )

    default_forbidden = [".git/", ".env", ".env.local", ".env.*", "node_modules/"]
    forbidden_input = validate_list_of_strings(scope, "forbidden_paths")
    forbidden_paths = normalize_repo_relative_paths(
        forbidden_input + [path for path in default_forbidden if path not in forbidden_input],
        "scope.forbidden_paths",
        repo_path,
    )

    # Execution section
    execution = raw.get("execution")
    if not isinstance(execution, dict):
        raise ValidationError("execution section must be a mapping")

    mode = optional_string(execution, "mode") or "agent"
    if mode not in EXECUTION_MODES:
        raise ValidationError(f"execution.mode must be one of {', '.join(sorted(EXECUTION_MODES))}")

    preferred_executor = optional_string(execution, "preferred_executor")
    model = optional_string(execution, "model")
    model_tier = optional_string(execution, "model_tier")
    if model_tier and model_tier not in KNOWN_MODEL_TIERS:
        raise ValidationError(
            f"execution.model_tier must be one of {', '.join(sorted(KNOWN_MODEL_TIERS))}"
        )
    allowed_executors = validate_list_of_strings(execution, "allowed_executors")
    disallowed_executors = validate_list_of_strings(execution, "disallowed_executors")

    # Validate executor references
    all_executors = set(allowed_executors) | set(disallowed_executors)
    if preferred_executor:
        all_executors.add(preferred_executor)

    unknown_executors = all_executors - KNOWN_EXECUTORS - KNOWN_TARGETS
    if unknown_executors:
        raise ValidationError(f"unknown executors: {', '.join(sorted(unknown_executors))}")

    overlap = set(allowed_executors) & set(disallowed_executors)
    if overlap:
        raise ValidationError(f"executor cannot be both allowed and disallowed: {', '.join(sorted(overlap))}")

    commands_allowed = validate_list_of_strings(execution, "commands_allowed")
    commands_forbidden = validate_list_of_strings(execution, "commands_forbidden")
    test_commands = validate_list_of_strings(execution, "test_commands")

    # Output contract and provenance
    output_contract = validate_output_contract(raw)
    provenance_config = validate_provenance_config(raw)

    # Metadata
    created_by = require_string(raw, "created_by")
    created_at = require_timestamp(raw, "created_at")

    return JobV2(
        schema_version=2,
        job_id=job_id,
        title=title,
        repo_path=repo_path,
        branch=branch,
        task_type=task_type,
        objective=objective,
        context=context,
        constraints=constraints,
        acceptance_criteria=acceptance_criteria,
        allowed_paths=allowed_paths,
        forbidden_paths=sorted(dict.fromkeys(forbidden_paths)),
        mode=mode,
        preferred_executor=preferred_executor,
        model=model,
        model_tier=model_tier,
        allowed_executors=allowed_executors,
        disallowed_executors=disallowed_executors,
        commands_allowed=commands_allowed,
        commands_forbidden=commands_forbidden,
        test_commands=test_commands,
        output_contract=output_contract,
        provenance_config=provenance_config,
        created_by=created_by,
        created_at=created_at,
        source_path=source_path.resolve(),
    )


def load_job_v2(job_path: Path) -> JobV2:
    """Load and validate schema v2 job."""
    raw = load_yaml_file(job_path)
    return load_job_v2_from_mapping(raw, job_path)


def migrate_v1_to_v2(raw_v1: dict[str, Any], source_path: Path) -> JobV2:
    """Migrate schema v1 job to v2 structure with warnings."""
    print("warning: schema v1 is deprecated; migrate to schema v2", file=sys.stderr)

    # Map v1 flat structure to v2 sections
    v2_raw: dict[str, Any] = {
        "schema_version": 2,
        "id": raw_v1.get("id"),
        "title": raw_v1.get("title"),
        "repo_path": raw_v1.get("repo_path"),
        "branch": raw_v1.get("branch"),
        "task": {
            "type": raw_v1.get("task_type"),
            "objective": raw_v1.get("objective"),
            "context": raw_v1.get("context"),
            "constraints": raw_v1.get("constraints", []),
            "acceptance_criteria": raw_v1.get("acceptance_criteria", []),
        },
        "scope": {
            "allowed_paths": raw_v1.get("allowed_paths", []),
            "forbidden_paths": raw_v1.get("forbidden_paths", []),
        },
        "execution": {
            "mode": "agent",  # v1 assumed agent mode
            "preferred_executor": "codex",  # v1 was Codex-specific
            "model": raw_v1.get("model"),
            "model_tier": raw_v1.get("model_tier"),
            "allowed_executors": ["codex", "mock"],  # Assume backwards compat
            "disallowed_executors": [],
            "commands_allowed": raw_v1.get("commands_allowed", []),
            "commands_forbidden": raw_v1.get("commands_forbidden", []),
            "test_commands": raw_v1.get("test_commands", []),
        },
        "output_contract": raw_v1.get("output_contract", {}),
        "provenance": {
            "distinguish_agent_claims": True,
            "require_changed_file_snapshot": True,
            "require_test_evidence": True,
        },
        "created_by": raw_v1.get("created_by"),
        "created_at": raw_v1.get("created_at"),
    }

    # Now validate as v2 using the same fail-closed logic as native schema v2.
    return load_job_v2_from_mapping(v2_raw, source_path)


def load_job(job_path: Path) -> JobV2:
    """Load job file, auto-detecting v1 or v2 and migrating if needed."""
    raw = load_yaml_file(job_path)
    schema_version = raw.get("schema_version")

    if schema_version == 2:
        return load_job_v2(job_path)
    elif schema_version == 1:
        return migrate_v1_to_v2(raw, job_path)
    else:
        raise ValidationError(
            f"unsupported schema_version: {schema_version!r} (supported: 1 [deprecated], 2)"
        )

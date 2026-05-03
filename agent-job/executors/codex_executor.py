#!/usr/bin/env python3
"""Codex executor adapter - isolates Codex-specific logic."""

from __future__ import annotations

import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

from base_executor import BaseExecutor, ExecutionResult

if TYPE_CHECKING:
    from schema import JobV2
else:
    JobV2 = Any


class CodexExecutor(BaseExecutor):
    """Executor adapter for local Codex CLI."""

    def __init__(self, codex_bin: str = "codex", model_tier: str | None = None):
        """Initialize Codex executor.

        Args:
            codex_bin: Path to codex binary
            model_tier: Model tier (low/medium/high) for tier-based model selection
        """
        self.codex_bin = codex_bin
        self.model_tier = model_tier or "low"

    def can_execute(self, job: JobV2) -> bool:
        """Check if Codex can execute this job."""
        if job.disallowed_executors and "codex" in job.disallowed_executors:
            return False
        if job.allowed_executors and "codex" not in job.allowed_executors:
            return False
        return True

    def check_auth(self) -> None:
        """Check if Codex is authenticated."""
        if os.environ.get("CODEX_API_KEY"):
            return
        auth_path = Path.home() / ".codex" / "auth.json"
        if auth_path.exists():
            return
        raise RuntimeError("missing Codex auth: run 'codex login' or export CODEX_API_KEY")

    def execute(self, job: JobV2, run_dir: Path, dry_run: bool) -> ExecutionResult:
        """Execute job via Codex CLI.

        For Phase A, this is a minimal implementation.
        Full migration of codex_job_cli.py logic will happen in a later phase.
        """
        if dry_run:
            return self._dry_run_execution(job)

        # Check auth before executing
        self.check_auth()

        # For Phase A: create minimal execution
        # Future: migrate full codex_job_cli.py run_job logic here
        raise NotImplementedError(
            "Full Codex execution via agent-job CLI is pending migration. "
            "For Phase A, use codex-job for actual Codex execution, or use mock executor for testing."
        )

    def _dry_run_execution(self, job: JobV2) -> ExecutionResult:
        """Simulate Codex execution without invoking."""
        log_text = f"[dry-run] Would execute via Codex: {job.job_id}\n"
        log_text += f"[dry-run] Model tier: {self.model_tier}\n"
        log_text += f"[dry-run] Repo: {job.repo_path}\n"

        mock_claims = {
            "summary": f"Dry run of {job.title}",
            "changed_files": [],
            "tests_run": [],
            "tests_not_run": job.test_commands,
            "acceptance_criteria": [
                {"criterion": c, "status": "unknown", "notes": "dry run"}
                for c in job.acceptance_criteria
            ],
            "risks": ["dry run - no actual execution"],
            "follow_up": ["run without --dry-run for real execution"],
            "human_review_checklist": ["verify prompt", "run real execution"],
        }

        return ExecutionResult(
            success=True,
            exit_code=None,
            log_text=log_text,
            agent_claims=mock_claims,
            executor_observations={"dry_run": True},
            executor_name="codex",
            launched_by_tool=True,
        )

    def get_executor_name(self) -> str:
        """Return executor name."""
        return "codex"

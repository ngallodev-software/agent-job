#!/usr/bin/env python3
"""Mock executor for testing without external dependencies."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

from base_executor import BaseExecutor, ExecutionResult

if TYPE_CHECKING:
    from schema import JobV2
else:
    JobV2 = Any


class MockExecutor(BaseExecutor):
    """Mock executor that simulates job execution for testing."""

    def can_execute(self, job: JobV2) -> bool:
        """Mock executor is always available if allowed."""
        if job.disallowed_executors and "mock" in job.disallowed_executors:
            return False
        if job.allowed_executors and "mock" not in job.allowed_executors:
            return False
        return True

    def execute(self, job: JobV2, run_dir: Path, dry_run: bool) -> ExecutionResult:
        """Simulate job execution with predictable output."""
        log_lines = [
            f"[mock] Starting job: {job.job_id}",
            f"[mock] Task: {job.task_type}",
            f"[mock] Objective: {job.objective}",
            "[mock] Simulated execution",
        ]

        if dry_run:
            log_lines.append("[mock] DRY RUN - no changes made")

        # Create mock report
        mock_claims = {
            "summary": f"Mock execution of {job.title}",
            "changed_files": [],
            "tests_run": [],
            "tests_not_run": job.test_commands if job.test_commands else ["no tests declared"],
            "acceptance_criteria": [
                {"criterion": criterion, "status": "unknown", "notes": "mock execution"}
                for criterion in job.acceptance_criteria
            ],
            "risks": ["mock execution - not real"],
            "follow_up": ["review mock output", "run with real executor"],
            "human_review_checklist": ["verify mock output", "run real execution"],
        }

        mock_observations = {
            "process_started": True,
            "process_completed": True,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "end_time": datetime.now(timezone.utc).isoformat(),
        }

        log_text = "\n".join(log_lines)

        return ExecutionResult(
            success=True,
            exit_code=0,
            log_text=log_text,
            agent_claims=mock_claims,
            executor_observations=mock_observations,
            executor_name="mock",
            launched_by_tool=True,
        )

    def get_executor_name(self) -> str:
        """Return executor name."""
        return "mock"

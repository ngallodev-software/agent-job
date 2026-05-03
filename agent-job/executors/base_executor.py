#!/usr/bin/env python3
"""Base executor interface for universal agent-job architecture."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ExecutionResult:
    """Result of job execution."""

    success: bool
    exit_code: int | None
    log_text: str
    agent_claims: dict[str, Any]
    executor_observations: dict[str, Any]
    executor_name: str
    launched_by_tool: bool


class BaseExecutor(ABC):
    """Abstract base class for all executors."""

    @abstractmethod
    def can_execute(self, job: Any) -> bool:
        """Check if this executor can handle the job.

        Args:
            job: JobV2 instance

        Returns:
            True if executor is allowed and available
        """

    @abstractmethod
    def execute(self, job: Any, run_dir: Path, dry_run: bool) -> ExecutionResult:
        """Execute the job.

        Args:
            job: JobV2 instance
            run_dir: Directory for artifacts
            dry_run: If True, simulate without actual execution

        Returns:
            ExecutionResult with outcome and provenance

        Raises:
            RuntimeError: If execution fails
        """

    @abstractmethod
    def get_executor_name(self) -> str:
        """Return executor identifier (e.g., 'codex', 'mock').

        Returns:
            Executor name for provenance
        """

    def check_auth(self) -> None:
        """Check if executor is authenticated and available.

        Raises:
            RuntimeError: If executor is not available
        """
        # Default: no auth required
        pass

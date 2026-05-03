#!/usr/bin/env python3
"""Base renderer interface for universal agent-job architecture."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseRenderer(ABC):
    """Abstract base class for all renderers."""

    @abstractmethod
    def render(self, job: Any) -> str:
        """Render job to target-specific prompt.

        Args:
            job: JobV2 instance

        Returns:
            Rendered prompt text suitable for target environment
        """

    @abstractmethod
    def get_target_name(self) -> str:
        """Return target identifier (e.g., 'copilot', 'manual', 'codex').

        Returns:
            Target name for artifact naming
        """

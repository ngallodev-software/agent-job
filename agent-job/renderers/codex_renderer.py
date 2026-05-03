#!/usr/bin/env python3
"""Codex renderer - Codex-adapter-specific prompt generation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from base_renderer import BaseRenderer

if TYPE_CHECKING:
    from schema import JobV2
else:
    JobV2 = Any


class CodexRenderer(BaseRenderer):
    """Renderer for Codex executor adapter (legacy/compatibility)."""

    def render(self, job: JobV2) -> str:
        """Render job as Codex-optimized prompt.

        Note: This is adapter-specific. For universal prompts, use copilot or manual renderers.
        """
        sections = []

        # Header - mark as adapter-specific
        sections.append("# Engineering Job (Codex Adapter)\n")
        sections.append("**Note**: This prompt is optimized for the Codex executor adapter.\n")

        # Job metadata
        sections.append("## Job Metadata\n")
        sections.append(f"- Job ID: {job.job_id}")
        sections.append(f"- Title: {job.title}")
        sections.append(f"- Task Type: {job.task_type}")
        sections.append(f"- Repository: {job.repo_path}\n")

        # Objective
        sections.append("## Objective\n")
        sections.append(job.objective.strip())
        sections.append("")

        # Context
        if job.context:
            sections.append("## Context\n")
            sections.append("The following context is provided by the user:\n")
            sections.append("```")
            sections.append(job.context.strip())
            sections.append("```")
            sections.append("")

        # Scope
        sections.append("## Allowed Write Scope\n")
        sections.append("You may modify files under these paths only:\n")
        if job.allowed_paths:
            for path in job.allowed_paths:
                sections.append(f"- {path}")
        sections.append("")

        sections.append("## Forbidden Paths\n")
        sections.append("You must not modify these paths:\n")
        if job.forbidden_paths:
            for path in job.forbidden_paths:
                sections.append(f"- {path}")
        sections.append("")

        # Constraints
        sections.append("## Constraints\n")
        if job.constraints:
            for constraint in job.constraints:
                sections.append(f"- {constraint}")
        sections.append("")

        # Acceptance criteria
        sections.append("## Acceptance Criteria\n")
        if job.acceptance_criteria:
            for criterion in job.acceptance_criteria:
                sections.append(f"- {criterion}")
        sections.append("")

        # Commands policy
        if job.commands_forbidden:
            sections.append("## Forbidden Commands\n")
            sections.append("Do not execute:\n")
            for cmd in job.commands_forbidden:
                sections.append(f"- {cmd}")
            sections.append("")

        # Output contract - embedded report
        sections.append("## Output Contract\n")
        sections.append(
            "After completing the work, provide a JSON report between markers "
            "`BEGIN_CODEX_JOB_REPORT` and `END_CODEX_JOB_REPORT`:\n"
        )
        sections.append("```json")
        sections.append("{")
        sections.append('  "summary": "short summary of changes",')
        sections.append('  "changed_files": ["path1", "path2"],')
        sections.append('  "tests_run": ["command1", "command2"],')
        sections.append('  "tests_not_run": ["reason why certain tests were not run"],')
        sections.append('  "acceptance_criteria": [')
        sections.append('    {"criterion": "text", "status": "met|not_met|unknown", "notes": "optional"}')
        sections.append("  ],")
        sections.append('  "risks": ["remaining risk or ambiguity"],')
        sections.append('  "follow_up": ["next steps for human"]')
        sections.append("}")
        sections.append("```")
        sections.append("")

        # Important rules
        sections.append("## Important Rules\n")
        sections.append("- Do not auto-commit changes")
        sections.append("- Do not auto-push to remote")
        sections.append("- Do not modify files outside allowed paths")
        sections.append("- Provide the JSON report between markers")
        sections.append("- Distinguish observed facts from claims\n")

        return "\n".join(sections)

    def get_target_name(self) -> str:
        """Return target name."""
        return "codex"

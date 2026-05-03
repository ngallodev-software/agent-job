#!/usr/bin/env python3
"""Manual renderer - generates human-readable work orders."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from base_renderer import BaseRenderer

if TYPE_CHECKING:
    from schema import JobV2
else:
    JobV2 = Any


class ManualRenderer(BaseRenderer):
    """Renderer for manual/human execution using any approved tool."""

    def render(self, job: JobV2) -> str:
        """Render job as human-readable work order."""
        sections = []

        # Header
        sections.append(f"# Work Order: {job.title}\n")
        sections.append(f"**Job ID**: {job.job_id}")
        sections.append(f"**Task Type**: {job.task_type}")
        sections.append(f"**Repository**: {job.repo_path}")
        if job.branch:
            sections.append(f"**Branch**: {job.branch}")
        sections.append("")

        # What to do
        sections.append("## What to Do\n")
        sections.append(job.objective.strip())
        sections.append("")

        # Background
        if job.context:
            sections.append("## Background\n")
            sections.append(job.context.strip())
            sections.append("")

        # What you can change
        sections.append("## What You Can Change\n")
        if job.allowed_paths:
            for path in job.allowed_paths:
                sections.append(f"- `{path}`")
        else:
            sections.append("- (none specified)")
        sections.append("")

        # What you must not change
        sections.append("## What You Must Not Change\n")
        if job.forbidden_paths:
            for path in job.forbidden_paths:
                sections.append(f"- `{path}`")
        else:
            sections.append("- (none specified)")
        sections.append("")

        # Rules to follow
        sections.append("## Rules to Follow\n")
        if job.constraints:
            for constraint in job.constraints:
                sections.append(f"- {constraint}")
        else:
            sections.append("- (none specified)")
        sections.append("")

        # What success looks like
        sections.append("## What Success Looks Like\n")
        if job.acceptance_criteria:
            for criterion in job.acceptance_criteria:
                sections.append(f"- [ ] {criterion}")
        else:
            sections.append("- (none specified)")
        sections.append("")

        # Suggested workflow
        sections.append("## Suggested Workflow\n")
        sections.append("1. Read the objective and context carefully")
        sections.append("2. Review the allowed and forbidden paths")
        sections.append("3. Make the changes using your preferred tool")
        sections.append("4. Test your changes")
        sections.append("5. Review the diff")
        sections.append("6. Complete the checklist below")
        sections.append("7. Submit for human review (do not commit yet)")
        sections.append("")

        # Review checklist
        sections.append("## Review Checklist\n")
        sections.append("Before considering this work complete, verify:")
        sections.append("- [ ] All acceptance criteria are met")
        sections.append("- [ ] No files outside allowed paths were modified")
        sections.append("- [ ] All constraints were followed")
        sections.append("- [ ] Tests were run (if applicable)")
        sections.append("- [ ] Diff has been reviewed")
        sections.append("- [ ] Risks and follow-up items are documented")
        sections.append("")

        # Completion report
        sections.append("## Completion Report\n")
        sections.append("When finished, document:\n")
        sections.append("**Summary**:")
        sections.append("(What was changed and why)")
        sections.append("")
        sections.append("**Files Changed**:")
        sections.append("(List with repo-relative paths)")
        sections.append("")
        sections.append("**Tests Run**:")
        sections.append("(Commands and results)")
        sections.append("")
        sections.append("**Tests Not Run**:")
        sections.append("(Which tests and why)")
        sections.append("")
        sections.append("**Acceptance Criteria Status**:")
        sections.append("(For each criterion, note met/not met/partial)")
        sections.append("")
        sections.append("**Risks**:")
        sections.append("(Remaining concerns or edge cases)")
        sections.append("")
        sections.append("**Follow-Up**:")
        sections.append("(What still needs to be done)")
        sections.append("")

        sections.append("---\n")
        sections.append("**Work package ready. Begin implementation.**")

        return "\n".join(sections)

    def get_target_name(self) -> str:
        """Return target name."""
        return "manual"

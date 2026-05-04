#!/usr/bin/env python3
"""Static checks for the Copilot eval suite."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
TASKS_DIR = ROOT / "tasks"
REQUIRED_TASK_FILES = (
    "baseline-prompt.md",
    "evaluator-prompt.md",
    "expected-signals.md",
    "agent-job.job.yaml",
)
FORBIDDEN_PROMPT_PHRASES = (
    "codex is the required executor",
    "required executor: codex",
    "use codex for this task",
)


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def check_file_nonempty(errors: list[str], path: Path) -> None:
    if not path.exists():
        fail(errors, f"missing file: {path.relative_to(ROOT)}")
        return
    if not path.read_text(encoding="utf-8").strip():
        fail(errors, f"empty file: {path.relative_to(ROOT)}")


def main() -> int:
    errors: list[str] = []
    task_dirs = sorted(p for p in TASKS_DIR.iterdir() if p.is_dir())

    if len(task_dirs) != 6:
        fail(errors, f"expected 6 task directories, found {len(task_dirs)}")

    for task_dir in task_dirs:
        for rel_name in REQUIRED_TASK_FILES:
            check_file_nonempty(errors, task_dir / rel_name)

        for rel_name in ("baseline-prompt.md", "evaluator-prompt.md"):
            prompt_path = task_dir / rel_name
            if not prompt_path.exists():
                continue
            prompt_text = prompt_path.read_text(encoding="utf-8").lower()
            for phrase in FORBIDDEN_PROMPT_PHRASES:
                if phrase in prompt_text:
                    fail(
                        errors,
                        f"forbidden Codex-required wording in {prompt_path.relative_to(ROOT)}",
                    )

    required_root_files = (
        ROOT / "README.md",
        ROOT / "runbook.md",
        ROOT / "evaluator-rubric.md",
        ROOT / "result-template.md",
        ROOT / "aggregate-template.md",
    )
    for path in required_root_files:
        check_file_nonempty(errors, path)

    if errors:
        print("Copilot eval suite self-check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"ok: validated {len(task_dirs)} task directories and shared assets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

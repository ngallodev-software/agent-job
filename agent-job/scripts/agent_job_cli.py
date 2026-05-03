#!/usr/bin/env python3
"""Universal agent-job CLI: executor-neutral job validation, rendering, packaging, and execution."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "executors"))
sys.path.insert(0, str(Path(__file__).parent.parent / "renderers"))

from schema import JobV2, ValidationError, load_job  # noqa: E402

# Import executors
from codex_executor import CodexExecutor  # noqa: E402
from mock_executor import MockExecutor  # noqa: E402

# Import renderers
from copilot_renderer import CopilotRenderer  # noqa: E402
from manual_renderer import ManualRenderer  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Universal agent job CLI: executor-neutral validation, rendering, packaging, execution"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Validate
    validate = subparsers.add_parser("validate", help="Validate a job file")
    validate.add_argument("job_file", help="Path to *.job.yaml")

    # Render
    render = subparsers.add_parser("render", help="Render job to target-specific prompt")
    render.add_argument("job_file", help="Path to *.job.yaml")
    render.add_argument(
        "--target",
        required=True,
        choices=["copilot", "manual", "codex", "claude"],
        help="Render target",
    )

    # Package
    package = subparsers.add_parser("package", help="Create work package without execution")
    package.add_argument("job_file", help="Path to *.job.yaml")
    package.add_argument("--target", required=True, choices=["copilot", "manual"], help="Package target")

    # Run
    run = subparsers.add_parser("run", help="Execute a job via specified executor")
    run.add_argument("job_file", help="Path to *.job.yaml")
    run.add_argument("--executor", required=True, choices=["codex", "mock"], help="Executor to use")
    run.add_argument("--dry-run", action="store_true", help="Simulate without actual execution")

    # Report
    report = subparsers.add_parser("report", help="Print report for a run or package")
    report.add_argument("run_path", help="Path to runs/<job-id>/<run-id>/")

    return parser.parse_args()


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate a job file."""
    job_path = Path(args.job_file).resolve()
    try:
        job = load_job(job_path)
        print(f"valid: {job.job_id}")
        print(f"schema_version: {job.schema_version}")
        print(f"title: {job.title}")
        print(f"task_type: {job.task_type}")
        print(f"repo_path: {job.repo_path}")
        print(f"allowed_paths: {len(job.allowed_paths)} entries")
        print(f"forbidden_paths: {len(job.forbidden_paths)} entries")
        if job.preferred_executor:
            print(f"preferred_executor: {job.preferred_executor}")
        return 0
    except ValidationError as exc:
        print(f"invalid: {exc}", file=sys.stderr)
        return 1


def get_renderer(target: str):
    """Get renderer for target."""
    if target == "codex":
        raise NotImplementedError(
            "agent-job render --target codex is not yet implemented. "
            "Use codex-job for Codex-specific execution paths."
        )
    if target == "claude":
        raise NotImplementedError("agent-job render --target claude is not yet implemented.")
    renderers = {
        "copilot": CopilotRenderer(),
        "manual": ManualRenderer(),
    }
    renderer = renderers.get(target)
    if not renderer:
        raise NotImplementedError(f"Renderer for target '{target}' is not yet implemented")
    return renderer


def cmd_render(args: argparse.Namespace) -> int:
    """Render job to target-specific prompt."""
    job_path = Path(args.job_file).resolve()
    try:
        job = load_job(job_path)
        renderer = get_renderer(args.target)
        prompt_text = renderer.render(job)
        print(prompt_text)
        return 0
    except ValidationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except NotImplementedError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def build_package_dir(job: JobV2, target: str) -> tuple[str, Path]:
    """Build package directory path."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    run_id = f"{timestamp}-{target}-package"
    runs_root = Path.cwd() / "runs"
    package_dir = runs_root / job.job_id / run_id
    return run_id, package_dir


def write_json(path: Path, data: dict[str, Any]) -> None:
    """Write JSON file."""
    path.write_text(json.dumps(data, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def validate_agent_claims(job: JobV2, result_claims: dict[str, Any]) -> list[str]:
    """Validate the executor/agent result against the job's output contract."""
    errors: list[str] = []

    summary = result_claims.get("summary")
    if job.output_contract.get("require_summary") and not isinstance(summary, str):
        errors.append("missing summary in agent_claims")
    elif job.output_contract.get("require_summary") and not summary.strip():
        errors.append("empty summary in agent_claims")

    changed_files = result_claims.get("changed_files")
    if job.output_contract.get("require_changed_files"):
        if not isinstance(changed_files, list):
            errors.append("missing changed_files list in agent_claims")
        elif len(changed_files) == 0:
            errors.append("changed_files is empty but output_contract.require_changed_files is true")

    tests_run = result_claims.get("tests_run")
    if job.output_contract.get("require_tests_run"):
        if not isinstance(tests_run, list):
            errors.append("missing tests_run list in agent_claims")
        elif len(tests_run) == 0:
            errors.append("tests_run is empty but output_contract.require_tests_run is true")

    risks = result_claims.get("risks")
    if job.output_contract.get("require_risks"):
        if not isinstance(risks, list):
            errors.append("missing risks list in agent_claims")
        elif len(risks) == 0:
            errors.append("risks is empty but output_contract.require_risks is true")

    return errors


def cmd_package(args: argparse.Namespace) -> int:
    """Create work package for non-executed targets."""
    job_path = Path(args.job_file).resolve()
    try:
        job = load_job(job_path)
        renderer = get_renderer(args.target)

        # Build package directory
        run_id, package_dir = build_package_dir(job, args.target)
        package_dir.mkdir(parents=True, exist_ok=False)

        # Render prompt
        prompt_text = renderer.render(job)

        # Write package files
        (package_dir / "job.input.yaml").write_text(job_path.read_text(encoding="utf-8"), encoding="utf-8")
        (package_dir / f"prompt.{args.target}.md").write_text(prompt_text, encoding="utf-8")

        # Write checklist
        checklist = f"""# Review Checklist: {job.title}

## Before Using This Package

- [ ] Review job.input.yaml
- [ ] Review prompt.{args.target}.md
- [ ] Understand acceptance criteria

## After Execution (in {args.target.title()} environment)

- [ ] All acceptance criteria met
- [ ] No files outside allowed paths modified
- [ ] All constraints followed
- [ ] Tests run (if applicable)
- [ ] Diff reviewed
- [ ] Completion notes documented

## Ready for Human Review

- [ ] Changes are uncommitted
- [ ] Diff is ready for review
- [ ] Report is complete
"""
        (package_dir / "checklist.md").write_text(checklist, encoding="utf-8")

        # Write report template
        report_template = f"""# Completion Report: {job.title}

## Summary
(Brief description of changes made)

## Files Changed
- path/to/file1
- path/to/file2

## Tests Run
- Command 1 → result
- Command 2 → result

## Tests Not Run
- Test X (reason)

## Acceptance Criteria Status
"""
        for criterion in job.acceptance_criteria:
            report_template += f"- [ ] {criterion}\n"

        report_template += """
## Risks
- Risk 1
- Risk 2

## Follow-Up
- Action 1
- Action 2
"""
        (package_dir / "report-template.md").write_text(report_template, encoding="utf-8")

        # Write meta.json
        meta = {
            "schema_version": 2,
            "job_id": job.job_id,
            "run_id": run_id,
            "mode": "package",
            "target": args.target,
            "executor": None,
            "launched_by_tool": False,
            "process_success": None,
            "exit_code": None,
            "human_review_required": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        write_json(package_dir / "meta.json", meta)

        print(f"package created: {package_dir}")
        print(f"\nNext steps:")
        print(f"1. Open: {package_dir / f'prompt.{args.target}.md'}")
        print(f"2. Copy prompt to {args.target.title()} environment")
        print(f"3. Execute work in that environment")
        print(f"4. Fill out: {package_dir / 'report-template.md'}")
        print(f"5. Review changes and decide whether to commit")
        return 0

    except ValidationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except FileExistsError:
        print(f"error: package directory already exists", file=sys.stderr)
        return 1


def get_executor(executor_name: str):
    """Get executor instance."""
    executors = {
        "codex": CodexExecutor(),
        "mock": MockExecutor(),
    }
    executor = executors.get(executor_name)
    if not executor:
        raise NotImplementedError(f"Executor '{executor_name}' is not yet implemented")
    return executor


def build_run_dir(job: JobV2, executor_name: str) -> tuple[str, Path]:
    """Build run directory path."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    run_id = f"{timestamp}-{executor_name}-run"
    runs_root = Path.cwd() / "runs"
    run_dir = runs_root / job.job_id / run_id
    return run_id, run_dir


def cmd_run(args: argparse.Namespace) -> int:
    """Execute job via specified executor."""
    job_path = Path(args.job_file).resolve()

    if args.executor == "codex":
        print("error: agent-job run --executor codex is not yet implemented.", file=sys.stderr)
        print("", file=sys.stderr)
        print("Use one of:", file=sys.stderr)
        print(f"  agent-job package {args.job_file} --target copilot", file=sys.stderr)
        print(f"  codex-job run {args.job_file}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Use agent-job for Copilot/manual packaging and codex-job for live Codex execution.", file=sys.stderr)
        return 1

    try:
        job = load_job(job_path)
        executor = get_executor(args.executor)

        # Check if executor can execute
        if not executor.can_execute(job):
            print(f"error: executor '{args.executor}' is not allowed for this job", file=sys.stderr)
            if job.disallowed_executors and args.executor in job.disallowed_executors:
                print(f"  (explicitly disallowed in job)", file=sys.stderr)
            elif job.allowed_executors and args.executor not in job.allowed_executors:
                print(f"  (not in allowed_executors: {', '.join(job.allowed_executors)})", file=sys.stderr)
            return 1

        # Check auth (only for non-mock executors)
        if args.executor != "mock" and not args.dry_run:
            try:
                executor.check_auth()
            except RuntimeError as exc:
                print(f"error: {exc}", file=sys.stderr)
                return 1

        # Build run directory
        run_id, run_dir = build_run_dir(job, args.executor)
        run_dir.mkdir(parents=True, exist_ok=False)

        # Execute
        print(f"executing job: {job.job_id}")
        print(f"executor: {args.executor}")
        if args.dry_run:
            print(f"mode: dry-run")
        print(f"run_dir: {run_dir}")
        print("")

        result = executor.execute(job, run_dir, args.dry_run)
        contract_errors = validate_agent_claims(job, result.agent_claims)
        effective_success = result.success and not contract_errors

        # Write artifacts
        (run_dir / "job.input.yaml").write_text(job_path.read_text(encoding="utf-8"), encoding="utf-8")
        (run_dir / "run.log").write_text(result.log_text, encoding="utf-8")

        meta = {
            "schema_version": 2,
            "job_id": job.job_id,
            "run_id": run_id,
            "mode": "run",
            "executor": result.executor_name,
            "launched_by_tool": result.launched_by_tool,
            "process_success": effective_success,
            "exit_code": result.exit_code,
            "dry_run": args.dry_run,
            "contract_errors": contract_errors,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        write_json(run_dir / "meta.json", meta)

        # Write report
        report = {
            "job_id": job.job_id,
            "run_id": run_id,
            "executor": result.executor_name,
            "success": effective_success,
            "agent_claims": result.agent_claims,
            "executor_observations": result.executor_observations,
            "contract_errors": contract_errors,
        }
        write_json(run_dir / "report.json", report)

        print(f"\nExecution complete")
        print(f"Success: {effective_success}")
        if contract_errors:
            print("Contract errors:")
            for error in contract_errors:
                print(f"  - {error}")
        print(f"Run directory: {run_dir}")
        print(f"\nView report:")
        print(f"  agent-job report {run_dir}")

        return 0 if effective_success else 1

    except ValidationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except NotImplementedError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except FileExistsError:
        print(f"error: run directory already exists", file=sys.stderr)
        return 1


def cmd_report(args: argparse.Namespace) -> int:
    """Print report for a run or package."""
    run_path = Path(args.run_path).resolve()

    if not run_path.exists():
        print(f"error: path does not exist: {run_path}", file=sys.stderr)
        return 1

    meta_path = run_path / "meta.json"
    if not meta_path.exists():
        print(f"error: meta.json not found in {run_path}", file=sys.stderr)
        return 1

    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    print(f"Job ID: {meta.get('job_id')}")
    print(f"Run ID: {meta.get('run_id')}")
    print(f"Mode: {meta.get('mode')}")
    print(f"Target/Executor: {meta.get('target') or meta.get('executor')}")
    print(f"Launched by tool: {meta.get('launched_by_tool')}")

    if meta.get("mode") == "package":
        print(f"\nPackage created but not executed.")
        prompt_file = run_path / f"prompt.{meta.get('target')}.md"
        print(f"Use the prompt in: {prompt_file}")
        print(f"After execution, fill out: {run_path / 'report-template.md'}")
    else:
        print(f"Process success: {meta.get('process_success')}")
        print(f"Exit code: {meta.get('exit_code')}")

        report_path = run_path / "report.json"
        if report_path.exists():
            report = json.loads(report_path.read_text(encoding="utf-8"))
            print(f"\nAgent Claims:")
            if "agent_claims" in report:
                claims = report["agent_claims"]
                print(f"  Summary: {claims.get('summary', 'N/A')}")
                print(f"  Changed files: {len(claims.get('changed_files', []))}")
                print(f"  Tests run: {len(claims.get('tests_run', []))}")
                print(f"  Risks: {len(claims.get('risks', []))}")

    print(f"\nRun directory: {run_path}")
    return 0


def main() -> int:
    """Main entry point."""
    args = parse_args()

    if args.command == "validate":
        return cmd_validate(args)
    elif args.command == "render":
        return cmd_render(args)
    elif args.command == "package":
        return cmd_package(args)
    elif args.command == "run":
        return cmd_run(args)
    elif args.command == "report":
        return cmd_report(args)
    else:
        print(f"error: unknown command: {args.command}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

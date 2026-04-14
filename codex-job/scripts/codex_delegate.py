#!/usr/bin/env python3
"""
Clean wrapper for codex delegation that provides concise output.

Usage:
    python3 codex_delegate.py --repo /path --tier high --task "description"
    python3 codex_delegate.py --repo /path --resume latest

Output format:
    Delegated <ticket> to <model> (<tier> tier) as fork
    Task <ticket> completed in <time>s

    OR

    Delegated <ticket> to <model> (<tier> tier) as fork
    Task <ticket> FAILED: <reason>
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path


def extract_ticket_id(task: str) -> str:
    """Extract ticket ID from task description (e.g., P3-T5)."""
    lines = task.split("\n")
    for line in lines[:10]:  # Check first 10 lines
        if "P1-T" in line or "P2-T" in line or "P3-T" in line or "P4-T" in line or "R" in line and "-T" in line:
            # Extract ticket pattern
            import re
            match = re.search(r'(P[1-4R]-T\d+|R\d+-\d+)', line)
            if match:
                return match.group(1)
    return "task"


def parse_summary(summary_path: Path) -> dict:
    """Parse summary JSON for key metrics."""
    if not summary_path.exists():
        return {}

    try:
        with open(summary_path) as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def main():
    parser = argparse.ArgumentParser(description="Clean codex delegation wrapper")
    parser.add_argument("--repo", required=True, help="Repository path")
    parser.add_argument("--task", help="Task description")
    parser.add_argument("--tier", help="Model tier (low/medium/high)")
    parser.add_argument("--provider", help="Provider (openai/anthropic)")
    parser.add_argument("--resume", help="Resume session ID")
    parser.add_argument("--model", help="Explicit model override")
    args = parser.parse_args()

    skill_dir = Path(__file__).parent.parent
    wrapper_script = skill_dir / "scripts" / "invoke_codex_with_review.sh"

    # Build command
    cmd = [str(wrapper_script), "--repo", args.repo]

    if args.resume:
        cmd.extend(["--resume", args.resume])
        ticket_id = f"resume-{args.resume[:8]}"
        model_display = "previous-model"
        tier_display = "resume"
    else:
        if not args.task or not args.tier:
            print("ERROR: --task and --tier required for new tasks", file=sys.stderr)
            sys.exit(1)
        cmd.extend(["--task", args.task, "--tier", args.tier])
        ticket_id = extract_ticket_id(args.task)

        # Determine model from tier
        tier_models = {
            "low": "gpt-5.1-codex-mini",
            "medium": "gpt-5.4-mini",
            "high": "gpt-5.3-codex",
        }
        model_display = args.model if args.model else tier_models.get(args.tier, args.tier)
        tier_display = f"{args.tier} tier"

    if args.provider:
        cmd.extend(["--provider", args.provider])
    if args.model:
        cmd.extend(["--model", args.model])

    # Print delegation start
    print(f"Delegated {ticket_id} to {model_display} ({tier_display}) as fork")
    sys.stdout.flush()

    # Execute wrapper (capture all output to suppress verbosity)
    try:
        result = subprocess.run(
            cmd,
            cwd=str(skill_dir),
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout
        )

        # Parse output for summary file path
        summary_path = None
        for line in result.stdout.split("\n"):
            if "summary_file=" in line:
                path_str = line.split("summary_file=", 1)[1].strip()
                if path_str and path_str != "pending":
                    summary_path = skill_dir / path_str
                    break

        # Parse summary for metrics
        summary = parse_summary(summary_path) if summary_path else {}
        elapsed = summary.get("time", summary.get("legacy", {}).get("elapsed_seconds"))
        exit_code = summary.get("exit", summary.get("legacy", {}).get("exit_code"))

        # Determine success/failure
        if result.returncode == 0 and exit_code == 0:
            time_display = f"{elapsed}s" if elapsed else "unknown time"
            print(f"Task {ticket_id} completed in {time_display}")
            sys.exit(0)
        else:
            # Extract failure reason
            reason = "Unknown error"

            # Check for session ID failure
            if "No valid session ID" in result.stdout or "No valid session ID" in result.stderr:
                reason = "No valid session ID - Codex did not execute (likely missing dependencies)"
            elif "Log too small" in result.stdout or "Log too small" in result.stderr:
                reason = "Log too small - Codex stopped early (check preconditions)"
            elif "503 Service Unavailable" in result.stderr:
                reason = "Service unavailable (check model availability)"
            elif "Real failure detected" in result.stdout:
                reason = "Execution failed (see logs for details)"
            elif exit_code and exit_code != 0:
                reason = f"Exit code {exit_code}"

            print(f"Task {ticket_id} FAILED: {reason}")

            # Show last few lines of error output for debugging
            error_lines = result.stderr.split("\n")
            relevant_errors = [l for l in error_lines if "ERROR:" in l or "FAIL" in l]
            if relevant_errors:
                print(f"  Details: {relevant_errors[-1]}")

            sys.exit(1)

    except subprocess.TimeoutExpired:
        print(f"Task {ticket_id} FAILED: Timeout after 10 minutes")
        sys.exit(1)
    except Exception as e:
        print(f"Task {ticket_id} FAILED: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Append a normalized delegation metrics record from a codex run summary.

Token and cost data sources (in priority order):
  1. ccusage-codex session --json  matched by session_id — gives real input/output/cached/cost
  2. codex run summary tok fields  — gives total tokens only (input/output are null in practice)
  3. Explicit CLI overrides         — --total-cost-usd etc.

Files changed: from git diff HEAD~1..HEAD in the repo.
Provider token fields: only the provider's fields are emitted; no cross-provider noise.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Append a delegation metrics JSONL record for a Codex run."
    )
    parser.add_argument("--summary", required=True, help="Path to codex run summary JSON")
    parser.add_argument("--out", default="delegation-metrics.jsonl", help="JSONL output path")
    parser.add_argument("--task-type", required=True)
    parser.add_argument("--risk", required=True, choices=["low", "medium", "high"])
    parser.add_argument("--ticket-id", default="", help="Ticket identifier, e.g. P7-001")
    parser.add_argument("--delegated", default="true", choices=["true", "false"])
    parser.add_argument("--reason-if-not-delegated", default="")
    parser.add_argument("--claude-model", required=True)
    parser.add_argument("--claude-tokens-input", type=int, default=0)
    parser.add_argument("--claude-tokens-output", type=int, default=0)
    parser.add_argument("--total-cost-usd", type=float, default=None,
                        help="Override cost; if omitted, looked up from ccusage-codex")
    parser.add_argument("--status", choices=["success", "partial", "failure"], default=None)
    parser.add_argument("--failure-class", choices=["environment", "spec", "execution"], default=None)
    parser.add_argument("--retry-count", type=int, default=0)
    parser.add_argument("--files-changed", default="",
                        help="Comma-separated list of changed files; if omitted, derived from git diff HEAD~1..HEAD")
    parser.add_argument("--delegated-model", required=True,
                        help="Model used by the delegate, e.g. gpt-5.1-codex-mini")
    parser.add_argument("--provider", choices=["codex", "gemini", "openai"], default="codex")
    parser.add_argument("--no-ccusage", action="store_true",
                        help="Skip ccusage-codex lookup (for offline/test use)")
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _as_number(value: object, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _as_int(value: object, default: int = 0) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _pick(summary: Mapping[str, Any], primary: str, legacy: str | None = None, default=None):
    if primary in summary and summary[primary] is not None:
        return summary[primary]
    legacy_block = summary.get("legacy") if isinstance(summary.get("legacy"), Mapping) else {}
    if legacy and legacy_block.get(legacy) is not None:
        return legacy_block[legacy]
    return default


# ---------------------------------------------------------------------------
# ccusage-codex session lookup
# ---------------------------------------------------------------------------

def _lookup_session_stats(session_id: str | None) -> dict | None:
    """Run ccusage-codex session --json and find the entry matching session_id."""
    if not session_id or session_id in ("null", "unknown", ""):
        return None
    try:
        result = subprocess.run(
            ["bunx", "@ccusage/codex@latest", "session", "--json"],
            capture_output=True, text=True, timeout=45,
        )
        if result.returncode != 0:
            return None
        data = json.loads(result.stdout)
        for s in data.get("sessions", []):
            # sessionId is "YYYY/MM/DD/rollout-...-<uuid>"; session_id is just the UUID
            if session_id in s.get("sessionId", ""):
                return s
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# files_changed from git
# ---------------------------------------------------------------------------

def _files_changed_from_git(repo: str) -> list[str]:
    """Return files changed in HEAD commit of repo."""
    if not repo:
        return []
    try:
        result = subprocess.run(
            ["git", "-C", repo, "diff", "--name-only", "HEAD~1", "HEAD"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0 and result.stdout.strip():
            return [f for f in result.stdout.strip().splitlines() if f]
    except Exception:
        pass
    return []


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    args = parse_args()
    summary_path = Path(args.summary)
    out_path = Path(args.out)

    summary: dict = json.loads(summary_path.read_text(encoding="utf-8"))

    # --- Basic run fields ---
    success = bool(_pick(summary, "ok", "success", False))
    status = args.status or ("success" if success else "failure")
    elapsed_seconds = _as_number(_pick(summary, "time", "elapsed_seconds", 0.0))
    repo = str(_pick(summary, "repo", "repo", ""))
    end_time = str(_pick(summary, "end", "ended_at") or datetime.now(timezone.utc).isoformat())
    session_id = str(_pick(summary, "sid") or "")
    delegated_model = args.delegated_model

    # --- Token extraction ---
    # Priority 1: ccusage-codex session (has real input/output split + cost)
    tok_input = tok_output = tok_cached = tok_total = tok_reasoning = 0
    cost_usd: float | None = None

    if not args.no_ccusage:
        session_stats = _lookup_session_stats(session_id or None)
        if session_stats:
            # Prefer model-specific breakdown; fall back to session totals
            model_stats = session_stats.get("models", {}).get(delegated_model)
            src = model_stats if model_stats else session_stats
            tok_input    = _as_int(src.get("inputTokens"))
            tok_output   = _as_int(src.get("outputTokens"))
            tok_cached   = _as_int(src.get("cachedInputTokens"))
            tok_reasoning= _as_int(src.get("reasoningOutputTokens"))
            tok_total    = _as_int(src.get("totalTokens"))
            # costUSD lives at session level, not per-model
            cost_usd = _as_number(session_stats.get("costUSD"), 0.0)

    # Priority 2: fall back to summary tok block (total only; input/output are null in practice)
    if tok_total == 0:
        tok_block = summary.get("tok") if isinstance(summary.get("tok"), Mapping) else {}
        legacy_tok = (summary.get("legacy") or {}).get("token_usage") or {}
        usage = tok_block if tok_block else legacy_tok
        tok_input  = tok_input  or _as_int(_pick(usage, "in",  "input_tokens"))
        tok_output = tok_output or _as_int(_pick(usage, "out", "output_tokens"))
        tok_total  = tok_total  or _as_int(_pick(usage, "tot", "total_tokens"))

    # --- Cost ---
    if args.total_cost_usd is not None:
        cost_usd = args.total_cost_usd
    if cost_usd is None:
        cost_block = summary.get("cost") or {}
        cost_usd = _as_number(cost_block.get("usd") if isinstance(cost_block, Mapping) else None, 0.0)

    # --- Files changed ---
    if args.files_changed:
        files_changed = [f.strip() for f in args.files_changed.split(",") if f.strip()]
    else:
        files_changed = _files_changed_from_git(repo)

    # --- Token fields: only emit the relevant provider's fields (no cross-provider noise) ---
    token_fields: dict = {}
    if args.provider == "codex":
        token_fields = {
            "codex_tokens_input": tok_input,
            "codex_tokens_output": tok_output,
            "codex_tokens_cached_input": tok_cached,
            "codex_tokens_reasoning_output": tok_reasoning,
            "codex_tokens_total": tok_total,
        }
    elif args.provider == "gemini":
        token_fields = {
            "gemini_tokens_input": tok_input,
            "gemini_tokens_output": tok_output,
            "gemini_tokens_total": tok_total,
        }
    elif args.provider == "openai":
        token_fields = {
            "openai_tokens_input": tok_input,
            "openai_tokens_output": tok_output,
            "openai_tokens_total": tok_total,
        }

    record: dict = {
        "timestamp": end_time,
        "repo": repo,
        "ticket_id": args.ticket_id,
        "task_type": args.task_type,
        "risk": args.risk,
        "delegated": args.delegated == "true",
        "reason_if_not_delegated": args.reason_if_not_delegated,
        "provider": args.provider,
        "claude_model": args.claude_model,
        "delegated_model": delegated_model,
        "session_id": session_id or None,
        "claude_tokens_input": args.claude_tokens_input,
        "claude_tokens_output": args.claude_tokens_output,
        **token_fields,
        "total_cost_usd": round(cost_usd, 6) if cost_usd else 0.0,
        "duration_sec": elapsed_seconds,
        "status": status,
        "failure_class": args.failure_class if status != "success" else None,
        "retry_count": args.retry_count,
        "files_changed": files_changed,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, separators=(",", ":")) + "\n")

    print(json.dumps({
        "ok": True,
        "out": str(out_path),
        "status": status,
        "tokens_total": tok_total,
        "tokens_input": tok_input,
        "tokens_output": tok_output,
        "cost_usd": cost_usd,
        "provider": args.provider,
        "session_id": session_id or None,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

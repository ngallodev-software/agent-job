#!/usr/bin/env bash
set -euo pipefail
umask 077

usage() {
  cat <<'USAGE'
Usage:
  uninstall_agent_job.sh [options]

Options:
  --bin-dir <path>       Installed command location (default: ~/.local/bin)
  --profile <path>       Shell profile to clean (default: auto-detect)
  --no-profile           Skip PATH/profile cleanup
  --dry-run              Show actions without changing files
  -h, --help             Show this help text

Examples:
  uninstall_agent_job.sh
  uninstall_agent_job.sh --dry-run
  uninstall_agent_job.sh --bin-dir ~/.bin
USAGE
}

require_env_var() {
  local name="$1"
  local reason="$2"
  if [[ -z "${!name:-}" ]]; then
    echo "Error: required environment variable $name is not set ($reason)." >&2
    exit 2
  fi
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR_OVERRIDE=""
PROFILE_OVERRIDE=""
NO_PROFILE=0
DRY_RUN=0

PROFILE_START="# >>> agent-job path (agent-job)"
PROFILE_END="# <<< agent-job path (agent-job)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --bin-dir)
      BIN_DIR_OVERRIDE="${2:-}"
      shift 2
      ;;
    --profile)
      PROFILE_OVERRIDE="${2:-}"
      shift 2
      ;;
    --no-profile)
      NO_PROFILE=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

require_env_var "HOME" "agent-job uninstall target resolution"

abs_path() {
  python3 - "$1" <<'PY'
import sys
from pathlib import Path

print(Path(sys.argv[1]).expanduser().resolve())
PY
}

BIN_DIR="${BIN_DIR_OVERRIDE:-$HOME/.local/bin}"
BIN_DIR="$(abs_path "$BIN_DIR")"
CLI_LINK="$BIN_DIR/agent-job"

log_step() {
  local msg="$1"
  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "[dry-run] $msg"
  else
    echo "$msg"
  fi
}

detect_profile_path() {
  if [[ -n "$PROFILE_OVERRIDE" ]]; then
    echo "$PROFILE_OVERRIDE"
    return
  fi

  local candidates=("$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile")
  local candidate
  for candidate in "${candidates[@]}"; do
    if [[ -f "$candidate" ]]; then
      echo "$candidate"
      return
    fi
  done
  echo "$HOME/.profile"
}

clean_profile_block() {
  local profile_path="$1"

  if [[ "$NO_PROFILE" -eq 1 ]]; then
    log_step "Skipping profile cleanup (disabled)"
    return
  fi

  if [[ "$DRY_RUN" -eq 1 ]]; then
    log_step "Remove PATH block from $profile_path if present"
    return
  fi

  python3 - "$profile_path" "$PROFILE_START" "$PROFILE_END" <<'PY'
import sys
from pathlib import Path

profile = Path(sys.argv[1])
start, end = sys.argv[2:4]
if not profile.exists():
    sys.exit(0)

lines = profile.read_text().splitlines()
out = []
skipping = False
for line in lines:
    if line.strip() == start:
        skipping = True
        continue
    if skipping and line.strip() == end:
        skipping = False
        continue
    if not skipping:
        out.append(line)

while out and not out[-1].strip():
    out.pop()

profile.write_text("\n".join(out) + ("\n" if out else ""))
PY
  log_step "Cleaned PATH block in $profile_path"
}

if [[ "$DRY_RUN" -eq 1 ]]; then
  log_step "Remove $CLI_LINK if present"
else
  if [[ -L "$CLI_LINK" || -f "$CLI_LINK" ]]; then
    rm -f "$CLI_LINK"
    log_step "Removed $CLI_LINK"
  else
    log_step "Already absent: $CLI_LINK"
  fi
fi

PROFILE_PATH="$(detect_profile_path)"
clean_profile_block "$PROFILE_PATH"

log_step "Uninstall completed"

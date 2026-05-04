#!/usr/bin/env bash
set -euo pipefail
umask 077

usage() {
  cat <<'USAGE'
Usage:
  install_agent_job.sh [options]

Options:
  --bin-dir <path>       Install/symlink location for the agent-job command
                         (default: ~/.local/bin)
  --profile <path>       Shell profile to update (default: auto-detect)
  --no-profile           Skip PATH/profile edits
  --skip-npm-install     Skip npm install for Copilot model sync dependencies
  --dry-run              Show actions without changing files
  -h, --help             Show this help text

Examples:
  install_agent_job.sh
  install_agent_job.sh --dry-run
  install_agent_job.sh --bin-dir ~/.bin --profile ~/.bashrc
  install_agent_job.sh --skip-npm-install
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
ROOT_DIR="$SCRIPT_DIR"
CLI_SRC="$ROOT_DIR/agent-job/scripts/agent-job"

BIN_DIR_OVERRIDE=""
PROFILE_OVERRIDE=""
NO_PROFILE=0
SKIP_NPM_INSTALL=0
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
    --skip-npm-install)
      SKIP_NPM_INSTALL=1
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

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 is required for installation." >&2
  exit 127
fi

require_env_var "HOME" "agent-job install target resolution"

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

ensure_dir() {
  local dir="$1"
  log_step "Ensure directory $dir"
  [[ "$DRY_RUN" -eq 1 ]] || mkdir -p "$dir"
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

update_profile_block() {
  local profile_path="$1"
  local path_entry="$2"

  if [[ "$NO_PROFILE" -eq 1 ]]; then
    log_step "Skipping profile update (disabled)"
    return
  fi

  if [[ "$DRY_RUN" -eq 1 ]]; then
    log_step "Ensure PATH entry for $path_entry in $profile_path"
    return
  fi

  local stamp
  stamp="# Added by agent-job install_agent_job.sh on $(date -u +%Y-%m-%dT%H:%M:%SZ)"

  python3 - "$profile_path" "$PROFILE_START" "$PROFILE_END" "$stamp" "$path_entry" <<'PY'
import sys
from pathlib import Path

profile = Path(sys.argv[1])
start, end, stamp, path_entry = sys.argv[2:6]
export_line = f'export PATH="{path_entry}:$PATH"'

text = profile.read_text() if profile.exists() else ""
out = []
skipping = False
for line in text.splitlines():
    if line.strip() == start:
        skipping = True
        continue
    if skipping and line.strip() == end:
        skipping = False
        continue
    if not skipping:
        out.append(line)

if out and out[-1].strip():
    out.append("")

out.extend([start, stamp, export_line, end])
profile.parent.mkdir(parents=True, exist_ok=True)
profile.write_text("\n".join(out) + "\n")
PY
  log_step "Updated PATH block in $profile_path"
}

run_npm_install() {
  if [[ "$SKIP_NPM_INSTALL" -eq 1 ]]; then
    log_step "Skipping npm install (--skip-npm-install)"
    return
  fi
  if ! command -v npm >/dev/null 2>&1; then
    log_step "npm not found; skip dependency install and run 'npm install' manually if you need Copilot model sync"
    return
  fi
  if [[ "$DRY_RUN" -eq 1 ]]; then
    log_step "Run npm install in $ROOT_DIR"
    return
  fi
  log_step "Running npm install in $ROOT_DIR"
  (cd "$ROOT_DIR" && npm install)
}

if [[ ! -f "$CLI_SRC" ]]; then
  echo "Error: agent-job entrypoint not found: $CLI_SRC" >&2
  exit 2
fi

log_step "Repo root: $ROOT_DIR"
log_step "Install command path: $CLI_LINK"
ensure_dir "$BIN_DIR"

if [[ "$DRY_RUN" -eq 1 ]]; then
  log_step "Symlink $CLI_LINK -> $CLI_SRC"
else
  ln -sfn "$CLI_SRC" "$CLI_LINK"
  log_step "Linked $CLI_LINK -> $CLI_SRC"
fi

PROFILE_PATH="$(detect_profile_path)"
update_profile_block "$PROFILE_PATH" "$BIN_DIR"
run_npm_install

log_step "Install completed"
log_step "Next steps:"
log_step "  1. Open a new shell or source $PROFILE_PATH"
log_step "  2. Run: agent-job --help"
log_step "  3. Optional Copilot model sync: agent-job sync-models"

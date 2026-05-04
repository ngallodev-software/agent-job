#!/usr/bin/env bash
set -euo pipefail
umask 077

usage() {
  cat <<'USAGE'
Usage:
  install_agent_job_remote.sh [options]

Options:
  --repo <owner/name>        GitHub repository (default: ngallodev-software/agent-job)
  --ref <git-ref>            Branch, tag, or commit to install (default: main)
  --install-dir <path>       Payload install root (default: ~/.local/share/agent-job)
  --bin-dir <path>           Command install location passed to install_agent_job.sh
  --profile <path>           Shell profile path passed to install_agent_job.sh
  --no-profile               Skip profile updates
  --with-model-sync          Run npm install in the installed payload for Copilot model sync
  --skip-pyyaml-install      Do not install PyYAML if missing
  --source-base-url <url>    Override raw file base URL (advanced/testing)
  --dry-run                  Show actions without making install changes
  -h, --help                 Show this help text

Examples:
  curl -fsSL https://raw.githubusercontent.com/ngallodev-software/agent-job/main/install_agent_job_remote.sh | bash
  curl -fsSL https://raw.githubusercontent.com/ngallodev-software/agent-job/main/install_agent_job_remote.sh | bash -s -- --ref main --with-model-sync
USAGE
}

REPO="ngallodev-software/agent-job"
REF="main"
INSTALL_DIR="${HOME:-$PWD}/.local/share/agent-job"
BIN_DIR=""
PROFILE=""
NO_PROFILE=0
WITH_MODEL_SYNC=0
SKIP_PYYAML_INSTALL=0
SOURCE_BASE_URL=""
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      REPO="${2:-}"
      shift 2
      ;;
    --ref)
      REF="${2:-}"
      shift 2
      ;;
    --install-dir)
      INSTALL_DIR="${2:-}"
      shift 2
      ;;
    --bin-dir)
      BIN_DIR="${2:-}"
      shift 2
      ;;
    --profile)
      PROFILE="${2:-}"
      shift 2
      ;;
    --no-profile)
      NO_PROFILE=1
      shift
      ;;
    --with-model-sync)
      WITH_MODEL_SYNC=1
      shift
      ;;
    --skip-pyyaml-install)
      SKIP_PYYAML_INSTALL=1
      shift
      ;;
    --source-base-url)
      SOURCE_BASE_URL="${2:-}"
      shift 2
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

if ! command -v curl >/dev/null 2>&1; then
  echo "Error: curl is required." >&2
  exit 127
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 is required." >&2
  exit 127
fi

abs_path() {
  python3 - "$1" <<'PY'
import sys
from pathlib import Path

print(Path(sys.argv[1]).expanduser().resolve())
PY
}

log_step() {
  local msg="$1"
  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "[dry-run] $msg"
  else
    echo "$msg"
  fi
}

RAW_BASE="${SOURCE_BASE_URL:-https://raw.githubusercontent.com/$REPO/$REF}"
INSTALL_DIR="$(abs_path "$INSTALL_DIR")"

FILES=(
  "install_agent_job.sh"
  "uninstall_agent_job.sh"
  "package.json"
  "package-lock.json"
  "agent-job/scripts/agent-job"
  "agent-job/scripts/agent_job_cli.py"
  "agent-job/scripts/model_selection.py"
  "agent-job/scripts/schema.py"
  "agent-job/renderers/base_renderer.py"
  "agent-job/renderers/copilot_renderer.py"
  "agent-job/renderers/manual_renderer.py"
  "agent-job/executors/base_executor.py"
  "agent-job/executors/codex_executor.py"
  "agent-job/executors/mock_executor.py"
  "agent-job/references/copilot/README.md"
  "agent-job/references/copilot/available-models.md"
  "agent-job/references/copilot/available_models.copilot.jsonl"
  "agent-job/references/copilot/fetch-models.mjs"
  "agent-job/references/copilot/sync-models.mjs"
)

download_file() {
  local rel_path="$1"
  local dst_root="$2"
  local dst_path="$dst_root/$rel_path"
  mkdir -p "$(dirname "$dst_path")"
  curl -fsSL "$RAW_BASE/$rel_path" -o "$dst_path"
}

ensure_pyyaml() {
  if [[ "$SKIP_PYYAML_INSTALL" -eq 1 ]]; then
    log_step "Skipping PyYAML install check (--skip-pyyaml-install)"
    return
  fi
  if python3 - <<'PY' >/dev/null 2>&1
import yaml
PY
  then
    log_step "PyYAML already available"
    return
  fi

  if ! python3 -m pip --version >/dev/null 2>&1; then
    echo "Error: PyYAML is required but pip is unavailable." >&2
    echo "Install PyYAML manually, then rerun." >&2
    exit 2
  fi

  if [[ "$DRY_RUN" -eq 1 ]]; then
    log_step "Would install PyYAML with: python3 -m pip install --user PyYAML"
    return
  fi

  log_step "Installing PyYAML with pip"
  python3 -m pip install --user PyYAML
}

run_local_installer() {
  local staged_root="$1"
  local -a cmd=("$staged_root/install_agent_job.sh")

  [[ -n "$BIN_DIR" ]] && cmd+=("--bin-dir" "$BIN_DIR")
  [[ -n "$PROFILE" ]] && cmd+=("--profile" "$PROFILE")
  [[ "$NO_PROFILE" -eq 1 ]] && cmd+=("--no-profile")
  [[ "$WITH_MODEL_SYNC" -eq 0 ]] && cmd+=("--skip-npm-install")
  [[ "$DRY_RUN" -eq 1 ]] && cmd+=("--dry-run")

  log_step "Running local installer from staged payload"
  "${cmd[@]}"
}

cleanup() {
  [[ -n "${TMP_DIR:-}" && -d "${TMP_DIR:-}" ]] && rm -rf "$TMP_DIR"
}
trap cleanup EXIT

TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/agent-job-remote.XXXXXX")"
STAGE_DIR="$TMP_DIR/payload"

log_step "Staging minimal agent-job payload from $RAW_BASE"
for rel_path in "${FILES[@]}"; do
  download_file "$rel_path" "$STAGE_DIR"
done

chmod 755 \
  "$STAGE_DIR/install_agent_job.sh" \
  "$STAGE_DIR/uninstall_agent_job.sh" \
  "$STAGE_DIR/agent-job/scripts/agent-job"

ensure_pyyaml

if [[ "$DRY_RUN" -eq 1 ]]; then
  log_step "Would replace install root $INSTALL_DIR"
  run_local_installer "$STAGE_DIR"
  log_step "Remote install dry-run completed"
  exit 0
fi

log_step "Replacing install root $INSTALL_DIR"
rm -rf "$INSTALL_DIR"
mkdir -p "$(dirname "$INSTALL_DIR")"
cp -R "$STAGE_DIR" "$INSTALL_DIR"

run_local_installer "$INSTALL_DIR"

log_step "Remote install completed"
log_step "Installed root: $INSTALL_DIR"
if [[ "$WITH_MODEL_SYNC" -eq 0 ]]; then
  log_step "Optional model sync later: cd $INSTALL_DIR && npm install && npm run copilot:models:sync"
fi

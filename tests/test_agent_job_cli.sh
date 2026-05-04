#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLI="$ROOT_DIR/agent-job/scripts/agent-job"

fail() {
  echo "[FAIL] $*" >&2
  exit 1
}

pass() {
  echo "[PASS] $*"
}

assert_contains() {
  local haystack="$1"
  local needle="$2"
  local label="$3"
  [[ "$haystack" == *"$needle"* ]] || fail "$label missing '$needle'"
}

write_v2_job() {
  local out="$1"
  local repo_path="$2"
  cat > "$out" <<EOF
schema_version: 2
id: JOB-AGENT-TEST
title: Agent job test
repo_path: $repo_path
branch: null
task:
  type: docs
  objective: Verify agent-job behavior.
  context: Test context.
  constraints:
    - Keep scope tight.
  acceptance_criteria:
    - Report is truthful.
scope:
  allowed_paths:
    - README.md
  forbidden_paths:
    - .git/
execution:
  mode: agent
  preferred_executor: mock
  model: null
  model_tier: null
  allowed_executors:
    - mock
  disallowed_executors: []
  commands_allowed: []
  commands_forbidden: []
  test_commands:
    - pytest
output_contract:
  require_summary: true
  require_changed_files: true
  require_tests_run: true
  require_risks: true
  human_review_required: true
provenance:
  distinguish_agent_claims: true
  require_changed_file_snapshot: true
  require_test_evidence: true
created_by: human
created_at: 2026-05-03T00:00:00Z
EOF
}

run_test_validate_shows_copilot_default_model() {
  local output
  output="$("$CLI" validate "$ROOT_DIR/examples/v2/copilot-docs.job.yaml" 2>&1)"
  assert_contains "$output" "default_model: gpt-4.1" "copilot default model"
  assert_contains "$output" "default_model_tier: medium" "copilot default tier"
  pass "copilot jobs show registry-backed default model"
}

run_test_sync_models_uses_payload_root() {
  local tmp fakebin fakelog output
  tmp="$(mktemp -d)"
  fakebin="$tmp/bin"
  fakelog="$tmp/npm.log"
  mkdir -p "$fakebin"
  cat > "$fakebin/npm" <<EOF
#!/usr/bin/env bash
set -euo pipefail
printf 'cwd=%s\\nargs=%s\\n' "\$PWD" "\$*" >> "$fakelog"
EOF
  chmod 755 "$fakebin/npm"

  output="$(cd /tmp && PATH="$fakebin:$PATH" "$CLI" sync-models 2>&1)"
  assert_contains "$output" "refreshing Copilot model registry in $ROOT_DIR" "sync-models status"
  assert_contains "$(cat "$fakelog")" "cwd=$ROOT_DIR" "sync-models cwd"
  assert_contains "$(cat "$fakelog")" "args=run copilot:models:sync" "sync-models args"
  rm -rf "$tmp"
  pass "sync-models uses payload root"
}

run_test_codex_and_claude_are_explicitly_unimplemented() {
  local render_output run_output copilot_output

  set +e
  render_output="$("$CLI" render "$ROOT_DIR/examples/v2/copilot-docs.job.yaml" --target claude 2>&1)"
  local render_status=$?
  copilot_output="$("$CLI" run "$ROOT_DIR/examples/v2/copilot-docs.job.yaml" --executor copilot 2>&1)"
  local copilot_status=$?
  run_output="$("$CLI" run "$ROOT_DIR/examples/v2/copilot-docs.job.yaml" --executor codex 2>&1)"
  local run_status=$?
  set -e

  [[ "$render_status" -ne 0 ]] || fail "claude render should fail"
  [[ "$copilot_status" -ne 0 ]] || fail "copilot run should fail"
  [[ "$run_status" -ne 0 ]] || fail "codex run should fail"
  assert_contains "$render_output" "not yet implemented" "claude render error"
  assert_contains "$copilot_output" "package/render mode only" "copilot run guidance"
  assert_contains "$copilot_output" "does not launch Copilot" "copilot execution honesty"
  assert_contains "$run_output" "codex-job run" "codex run guidance"
  pass "unimplemented paths are explicit"
}

run_test_mock_executor_respects_disallowlist_logic() {
  local tmp job output
  tmp="$(mktemp -d)"
  job="$tmp/job.yaml"
  write_v2_job "$job" "$ROOT_DIR"
  python3 - "$job" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
text = text.replace("  allowed_executors:\n    - mock\n", "  allowed_executors: []\n")
text = text.replace("  disallowed_executors: []\n", "  disallowed_executors:\n    - codex\n")
path.write_text(text, encoding="utf-8")
PY

  set +e
  output="$("$CLI" run "$job" --executor mock --dry-run 2>&1)"
  local status=$?
  set -e

  [[ "$status" -ne 0 ]] || fail "mock run should still fail contract enforcement in this fixture"
  if [[ "$output" == *"not allowed for this job"* ]]; then
    fail "mock executor should be allowed"
  fi
  assert_contains "$output" "Success: False" "mock contract failure still ran"
  rm -rf "$tmp"
  pass "mock executor is allowed when only codex is disallowed"
}

run_test_v1_migration_remains_fail_closed() {
  local tmp bad output
  tmp="$(mktemp -d)"
  bad="$tmp/bad-v1.job.yaml"
  cat > "$bad" <<EOF
schema_version: 1
id: BAD-V1
title: Bad legacy job
repo_path: $ROOT_DIR
task_type: docs
objective: legacy job
allowed_paths: []
constraints: []
acceptance_criteria: []
created_by: human
created_at: 2026-05-03T00:00:00Z
EOF

  set +e
  output="$("$CLI" validate "$bad" 2>&1)"
  local status=$?
  set -e

  [[ "$status" -ne 0 ]] || fail "invalid v1 migration should fail"
  assert_contains "$output" "must not be empty" "v1 fail-closed error"
  rm -rf "$tmp"
  pass "v1 migration is fail-closed"
}

run_test_output_contract_is_enforced() {
  local tmp job output run_dir report meta
  tmp="$(mktemp -d)"
  job="$tmp/job.yaml"
  write_v2_job "$job" "$ROOT_DIR"
  rm -rf "$ROOT_DIR/runs/JOB-AGENT-TEST"

  set +e
  output="$("$CLI" run "$job" --executor mock 2>&1)"
  local status=$?
  set -e

  [[ "$status" -ne 0 ]] || fail "contract violation should fail the run"
  run_dir="$(find "$ROOT_DIR/runs/JOB-AGENT-TEST" -mindepth 1 -maxdepth 1 -type d | head -n1)"
  report="$run_dir/report.json"
  meta="$run_dir/meta.json"
  [[ -f "$report" ]] || fail "missing report.json"
  [[ -f "$meta" ]] || fail "missing meta.json"
  python3 - "$report" "$meta" <<'PY'
import json
import sys
report = json.load(open(sys.argv[1], "r", encoding="utf-8"))
meta = json.load(open(sys.argv[2], "r", encoding="utf-8"))
assert report["success"] is False
assert meta["process_success"] is False
assert len(report["contract_errors"]) >= 2
PY
  rm -rf "$tmp"
  pass "output contract is enforced"
}

run_test_explicit_job_model_beats_default_selector() {
  local tmp job output
  tmp="$(mktemp -d)"
  job="$tmp/job.yaml"
  write_v2_job "$job" "$ROOT_DIR"
  python3 - "$job" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
text = text.replace("  preferred_executor: mock\n", "  preferred_executor: copilot\n")
text = text.replace("    - mock\n", "    - copilot\n")
text = text.replace("  model: null\n", "  model: gpt-5-mini\n")
text = text.replace("  model_tier: null\n", "  model_tier: low\n")
path.write_text(text, encoding="utf-8")
PY

  output="$("$CLI" render "$job" --target copilot 2>&1)"
  assert_contains "$output" '**Requested Model**: `gpt-5-mini`' "explicit model in prompt"
  assert_contains "$output" '**Requested Tier**: `low`' "explicit tier in prompt"
  assert_contains "$output" "explicit job model wins" "selection rule"
  rm -rf "$tmp"
  pass "explicit job model overrides default selector"
}

run_test_validate_shows_copilot_default_model
run_test_sync_models_uses_payload_root
run_test_codex_and_claude_are_explicitly_unimplemented
run_test_mock_executor_respects_disallowlist_logic
run_test_v1_migration_remains_fail_closed
run_test_output_contract_is_enforced
run_test_explicit_job_model_beats_default_selector

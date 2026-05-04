#!/usr/bin/env bash
set -euo pipefail

curl -fsSL https://raw.githubusercontent.com/ngallodev-software/agent-job/main/install_agent_job_remote.sh | bash "$@"

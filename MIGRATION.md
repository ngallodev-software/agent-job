# Migration from agent-job to Agent-Workflow

`agent-job` is an intermediate predecessor, not a supported compatibility layer.

## Concept mapping

| agent-job surface | Agent-Workflow destination | Disposition |
| --- | --- | --- |
| schema v2 bounded job | Agent Run + prompt-pack/evaluation contracts | superseded |
| `allowed_paths` / `forbidden_paths` | source/worktree provenance + scoped runtime/evaluation contracts | superseded |
| Copilot/manual package mode | prompt packs + external Worker preparation/binding | superseded |
| `launched_by_tool: false`, null process result | explicit prepared/external lifecycle; preparation is not execution | absorbed |
| target-specific renderers | logical roles + host/executor adapters | superseded |
| agent claims vs executor observations | provider evidence, provenance, completion collections, receipts | absorbed |
| free-form completion report | structured completion/task-result/evaluation contracts | superseded |
| mandatory human review | separate evaluation, independent review, authorized acceptance/rejection | absorbed |
| mock executor | synthetic test/benchmark executors | superseded |
| Copilot model sync and tier selection | operator executor policy; advisory freshness evidence only | retired |
| schema v1 auto-migration | historical only | retired |
| unfinished Codex executor | current Agent-Workflow Codex executor integration | abandoned precursor |
| six-task Copilot A/B eval suite | small-task comparative benchmark corpus candidate (`BKL-011`) | harvested |
| evaluator neutrality/friction rules | current comparative benchmark policy | absorbed |

## What the eval suite contributed

The historical suite compared the same small task under a competent plain prompt and a structured `agent-job` package. Its useful task classes were documentation correction, bugfix, refactor, test-only work, scope-boundary stress, and ambiguity reduction.

Its most durable evaluation rules were:

- use the same task and clean fixture state for both arms;
- score from captured artifacts rather than memory;
- do not reward structure by default;
- penalize unsupported test/success claims;
- treat review burden and operator friction as real costs;
- permit the baseline to win;
- permit roughly-equal and inconclusive outcomes.

Agent-Workflow's current benchmark system is substantially stricter about treatment identity, source/model/executor cohorts, evidence, scoring contracts, retries, and winner claims. The historical task classes should therefore be re-authored under that system rather than copied byte-for-byte.

## Do not port

Do not restore:

- `agent-job` YAML schemas as another native workflow format;
- Copilot-only package assumptions;
- checkout-specific absolute paths;
- hand-maintained model registries or model scores;
- the old remote installer or GitHub skill bootstrap;
- incomplete Codex/Claude renderers/executors;
- package metadata as a second lifecycle authority.

## Local retirement

Potential stale installation locations include `~/.local/share/agent-job`, `~/.local/bin/agent-job`, shell-profile PATH blocks, and Copilot/GitHub-installed skills. Remove those independently from this repository retirement.

# Implement Phase A: Minimum Viable Universal `agent-job` Architecture

You are working in the repository:

`invoke-codex-from-claude`

A previous pivot analysis concluded:

- The repo is still too Codex-specific.
- The production target may be a Copilot-only environment.
- Codex must become an executor adapter, not the identity of the system.
- The canonical interface should become `agent-job`.
- `codex-job` may remain temporarily only as a deprecated compatibility alias.
- The core value is a universal engineering job contract, target-specific rendering, artifact packaging, provenance, and human review.

Now implement **Phase A**.

This is an implementation phase, not another design report.

Do not add queueing.
Do not add dashboards.
Do not add control-plane behavior.
Do not add provider fanout beyond the explicitly requested adapters.
Do not add direct Copilot execution.
Do not fake Copilot automation.
Do not reintroduce unsafe callbacks.
Do not auto-commit.
Do not auto-push.

---

## Phase A Goal

Implement the minimum viable universal `agent-job` architecture.

At the end of this phase, the repo should support:

```bash
agent-job validate examples/copilot-docs.job.yaml
agent-job render examples/copilot-docs.job.yaml --target copilot
agent-job render examples/copilot-docs.job.yaml --target manual
agent-job package examples/copilot-docs.job.yaml --target copilot
agent-job package examples/copilot-docs.job.yaml --target manual
agent-job run examples/codex-local.job.yaml --executor codex --dry-run
agent-job run examples/mock.job.yaml --executor mock
agent-job report runs/<job-id>/<run-id>/
The codex-job command, if retained, must be a deprecated wrapper or alias only.

1. Implementation Boundaries
Implement only the smallest useful universal architecture.
Required in this phase:


agent-job canonical CLI.


Schema v2 with executor-neutral structure.


Schema v1-to-v2 migration if v1 already exists.


Agent-neutral provenance model.


Copilot renderer.


Manual renderer.


Codex renderer/adapter isolation.


Package mode for Copilot/manual targets.


Mock executor.


Helpful error if someone tries run --executor copilot.


Updated docs.


Tests.


Do not implement:


Direct Copilot execution.


Direct Claude execution.


Completion ingestion unless it is already trivial.


Full rename of every internal folder if too disruptive.


Removal of all legacy compatibility in this pass.


Advanced packaging/install release hardening.



2. Inspect Current Repo First
Before editing, inspect the actual current repo.
Review:


current CLI entrypoints


current schema loader/validator


current renderer


current runner


current report code


current provenance constants


current examples


current tests


current docs


install/uninstall behavior


any remaining compatibility wrappers


Do not assume file paths from earlier reports are still correct.
Then produce a short implementation plan listing:


files to modify


files to add


compatibility choices


tests to add/update


After that, implement.

3. Canonical CLI
Create or update the canonical CLI so that the user-facing command is:
agent-job
Required commands:
agent-job validate <job.job.yaml>agent-job render <job.job.yaml> --target copilotagent-job render <job.job.yaml> --target manualagent-job render <job.job.yaml> --target codexagent-job package <job.job.yaml> --target copilotagent-job package <job.job.yaml> --target manualagent-job run <job.job.yaml> --executor codex [--dry-run] [--run-tests]agent-job run <job.job.yaml> --executor mock [--dry-run]agent-job report <run-dir>
Optional command if already easy:
agent-job complete <package-dir> --completion completion.md
But do not let complete block Phase A.

codex-job Compatibility
If a codex-job command remains, it must:


Print a clear deprecation warning.


Delegate to agent-job.


Not contain independent runner logic.


Not be the primary documented interface.


Not support removed unsafe behavior.


Recommended warning:
warning: `codex-job` is deprecated; use `agent-job` instead. Codex is now an executor adapter, not the core interface.
If compatibility is too messy, remove codex-job from active docs and leave a migration note.

4. Schema v2
Implement schema version 2.
The schema should describe the engineering job, not the executor.
Required shape:
schema_version: 2id: JOB-2026-05-03-001title: Improve documentation consistencyrepo_path: /absolute/path/to/repobranch: nulltask:  type: docs  objective: >    Review active docs and update stale command references to the canonical agent-job CLI.  context: |    The project has pivoted from codex-job to agent-job.  constraints:    - Do not auto-commit.    - Do not auto-push.    - Do not modify unrelated files.  acceptance_criteria:    - Active docs describe agent-job as canonical.    - Codex is described as an executor adapter only.    - Copilot package workflow is documented.scope:  allowed_paths:    - README.md    - SECURITY.md    - CONTRIBUTING.md    - docs/    - agent-job/    - codex-job/  forbidden_paths:    - .git/    - .env    - secrets/execution:  mode: agent  preferred_executor: copilot  allowed_executors:    - copilot    - human    - codex    - mock  disallowed_executors: []  commands_allowed:    - python3    - pytest    - git  commands_forbidden:    - git push    - git reset --hard    - rm -rf  test_commands:    - pytestoutput_contract:  require_summary: true  require_changed_files: true  require_tests_run: true  require_risks: true  human_review_required: trueprovenance:  distinguish_agent_claims: true  require_changed_file_snapshot: true  require_test_evidence: truecreated_by: humancreated_at: 2026-05-03T00:00:00Z
You may adjust names slightly if needed, but keep the structure executor-neutral.

Required Schema Rules
Validation must fail closed.
Reject jobs where:


schema_version is missing


unsupported schema version


id missing or unsafe


title missing


repo_path missing


repo_path is not absolute


repo_path does not exist


task.objective missing or blank


task.type unsupported


scope.allowed_paths missing or empty


scope.allowed_paths contains absolute paths


scope.allowed_paths contains ..


scope.allowed_paths contains .git/


scope.forbidden_paths contains absolute paths


scope.forbidden_paths contains ..


execution.allowed_executors contains unknown executor


execution.disallowed_executors contains unknown executor


same executor is both allowed and disallowed


commands_forbidden is not a list


test_commands is not a list


created_at is invalid


YAML is malformed


Supported task types:
implementationbugfixrefactortestdocsanalysis
Supported render targets:
copilotmanualcodexclaude
Supported executors in Phase A:
codexmock
Supported package targets in Phase A:
copilotmanual
Do not support direct Copilot execution.

5. Schema v1 Compatibility
If schema v1 is currently supported, implement v1-to-v2 migration.
Rules:


v1 jobs may validate with a deprecation warning.


v1 flat fields should map into v2 sections.


task_type maps to task.type.


objective maps to task.objective.


context maps to task.context.


constraints maps to task.constraints.


acceptance_criteria maps to task.acceptance_criteria.


allowed_paths maps to scope.allowed_paths.


forbidden_paths maps to scope.forbidden_paths.


commands_allowed maps to execution.commands_allowed.


commands_forbidden maps to execution.commands_forbidden.


test_commands maps to execution.test_commands.


Codex-specific model or model_tier must not become core fields.


If preserved, Codex-specific fields belong under an adapter-specific structure or are ignored with warning.


If v1 compatibility is too large for this phase, document that v2 is required and update examples/tests accordingly.

6. Agent-Neutral Provenance
Generalize provenance from Codex-specific to agent-neutral.
Replace active use of:
claimed_by_codex
with:
claimed_by_agent
Supported provenance categories:
observeddeclared_by_jobclaimed_by_agentclaimed_by_executorinferrednot_capturednot_rununknown
Rules:


Do not use claimed_by_codex in new reports.


Legacy reports may be migrated or displayed with compatibility translation.


For Codex executor reports, use:


{  "provenance": "claimed_by_agent",  "agent": "codex"}


For Copilot package/completion reports, use:


{  "provenance": "claimed_by_agent",  "agent": "copilot"}
Do not let agent claims override observed runner facts.

7. Renderer Targets
Implement target-specific renderers.
The renderer changes wording and packaging, not job meaning.
7.1 Copilot Renderer
Command:
agent-job render job.job.yaml --target copilot
Output: markdown suitable for GitHub Copilot Chat, Copilot Workspace, or approved Copilot-style enterprise tooling.
It must not mention invoking Codex.
It must not assume Copilot can be launched by CLI.
It must include:
# Engineering Job for Copilot## Role## Job Metadata## Objective## Context## Scope### Allowed Paths### Forbidden Paths## Constraints## Acceptance Criteria## Required Evidence## Important Rules## Commands Policy## Completion Report Template
Required rules in the rendered prompt:


Do not auto-commit.


Do not auto-push.


Do not modify files outside allowed paths.


Do not claim tests passed unless they were run by you or the environment.


Distinguish observed facts from inferred facts and claims.


Report files changed.


Report tests run and tests not run.


Report risks and follow-up.


7.2 Manual Renderer
Command:
agent-job render job.job.yaml --target manual
Output: human-readable work order.
It should be useful to a developer using any approved tool.
It should include:


objective


scope


constraints


acceptance criteria


suggested workflow


review checklist


completion report template


It must not mention invoking Codex as the default.
7.3 Codex Renderer
Command:
agent-job render job.job.yaml --target codex
Output: Codex-adapter prompt.
It may be optimized for Codex, but must clearly be adapter-specific.
It must use universal language where possible.
It must not define the core identity of the repo.
7.4 Claude Renderer
Command:
agent-job render job.job.yaml --target claude
If easy, implement now.
If not easy, fail with a clear message:
target 'claude' is recognized but not implemented in Phase A
Do not block Phase A on Claude renderer.

8. Package Mode
Implement package mode for non-invoked targets.
Commands:
agent-job package job.job.yaml --target copilotagent-job package job.job.yaml --target manual
Package mode must:


validate the job


render the target prompt


create an artifact directory


copy the input job


write prompt file


write checklist


write report template


write meta.json


not launch any executor


not run tests


not claim process success


Recommended package artifact structure:
runs/  JOB-2026-05-03-001/    20260503-130000-copilot-package/      job.input.yaml      prompt.copilot.md      checklist.md      report-template.md      meta.json
For manual:
runs/  JOB-2026-05-03-001/    20260503-130000-manual-package/      job.input.yaml      work-order.manual.md      checklist.md      report-template.md      meta.json
meta.json for package mode must include:
{  "schema_version": 2,  "job_id": "JOB-2026-05-03-001",  "run_id": "20260503-130000-copilot-package",  "mode": "package",  "target": "copilot",  "executor": null,  "launched_by_tool": false,  "process_success": null,  "exit_code": null,  "human_review_required": true}
Do not fabricate exit codes.
Do not call the package a successful execution.
It is a successful package generation, not a successful engineering task.

9. Run Mode
Run mode should be executor-based.
Supported executors in Phase A:
codexmock
Command examples:
agent-job run job.job.yaml --executor codexagent-job run job.job.yaml --executor codex --dry-runagent-job run job.job.yaml --executor mock
Codex Executor
Move or isolate existing Codex execution logic into a Codex adapter.
Codex-specific concerns belong there:


codex exec


Codex auth checks


Codex model/model tier mapping


Codex prompt rendering if needed


Codex-specific parsing


The core CLI should not require Codex auth unless --executor codex is actually used.
Mock Executor
Implement mock executor for tests and dogfooding.
Mock executor should:


not call external agent


write predictable output


optionally simulate file changes only if explicitly configured


produce artifacts


make integration tests possible without Codex


Copilot Executor
Do not implement.
If user runs:
agent-job run job.job.yaml --executor copilot
Return nonzero with:
Copilot is supported through render/package mode only. Use:agent-job package <job> --target copilot
This is critical.

10. Report Behavior
Update report behavior to support both:


invoked runs


external packages


For package mode, report should say:


mode: package


target: copilot/manual


launched_by_tool: false


process_success: null


exit_code: null


engineering task status: not completed by tool


next step: use prompt/work-order in target environment and attach/ingest completion notes manually


If complete is not implemented, say so in docs.
For Codex/mocked runs, report can use existing run/report behavior but must use universal provenance categories.

11. Completion Ingestion
This is optional in Phase A.
Implement only if small and safe.
Command:
agent-job complete <package-dir> --completion completion.md
Behavior:


read package metadata


read completion markdown


generate report.json


generate report.md


mark completion claims as:


{  "provenance": "claimed_by_agent",  "agent": "copilot",  "source": "completion.md"}
Do not mark claims as observed.
If not implemented, create report-template.md and document manual review instead.

12. Examples
Create or update examples.
Required examples:
examples/copilot-docs.job.yamlexamples/manual-refactor.job.yamlexamples/codex-local.job.yamlexamples/mock.job.yamlexamples/invalid-executor.job.yaml
Examples must use schema v2.
Copilot example must not require Codex.
Manual example must not mention Codex.
Codex example must be clearly marked as local Codex adapter use.
Invalid example should be used by tests if useful.

13. Documentation Updates
Update active docs to make the pivot real.
At minimum update:


README.md


SECURITY.md


CONTRIBUTING.md


current architecture docs


skill docs


Docs should present agent-job as canonical.
Required README sections:
# agent-job## What This Is## What This Is Not## Supported Modes| Mode | Target/Executor | Tool launches executor? | Purpose ||---|---|---:|---|## Quick Start: Copilot Package## Quick Start: Manual Work Order## Quick Start: Local Codex Adapter## Job Schema v2## Render Targets## Package Mode## Run Mode## Report Mode## Provenance Model## Human Review Requirement## Safety Model## Migration from codex-job
Docs must clearly say:


Copilot is supported through render/package mode.


The tool does not directly execute Copilot.


Codex is an adapter, not the core identity.


Claude is not required.


The core workflow is executor-neutral.


No auto-commit.


No auto-push.


Human review is required.



14. Tests Required
Add or update tests.
Minimum required tests:
CLI


agent-job --help works


agent-job validate examples/copilot-docs.job.yaml passes


agent-job render examples/copilot-docs.job.yaml --target copilot passes


agent-job render examples/manual-refactor.job.yaml --target manual passes


agent-job package examples/copilot-docs.job.yaml --target copilot creates package


agent-job package examples/manual-refactor.job.yaml --target manual creates package


agent-job run examples/mock.job.yaml --executor mock works


agent-job run examples/copilot-docs.job.yaml --executor copilot fails helpfully


Schema v2


valid v2 job passes


missing task objective fails


empty allowed paths fails


unknown executor fails


executor both allowed and disallowed fails


Codex-specific model fields are not required


v1 job migration works or v1 fails with clear upgrade message


Rendering


Copilot render does not mention codex exec


Copilot render does not imply direct execution


Manual render does not mention codex exec


Codex render is adapter-specific


target-specific renderers preserve objective and acceptance criteria


Package mode


package writes job.input.yaml


package writes target prompt


package writes checklist


package writes report template


package writes meta.json


package metadata has launched_by_tool: false


package metadata has process_success: null


package metadata has exit_code: null


Provenance


reports use claimed_by_agent, not claimed_by_codex


package report does not fabricate process success


Codex adapter report uses agent: codex


mock executor report uses agent: mock


Safety


no auto-commit


no auto-push


no arbitrary shell callbacks


no run --executor copilot


no Codex auth check during Copilot package


no Codex auth check during manual package


no Codex auth check during validation/render unless target/executor requires it



15. Grep Checks
Run grep checks and classify hits.
At minimum:
grep -R "claimed_by_codex" .grep -R "codex exec" .grep -R "CODEX_API_KEY" .grep -R ".codex/auth" .grep -R "invoke Codex from Claude" .grep -R "codex-job" README.md SECURITY.md CONTRIBUTING.md docs/ agent-job/ codex-job/ || truegrep -R "auto-commit" .grep -R "auto-push" .grep -R "git push" .grep -R "notify-cmd" .grep -R "dangerously-skip-permissions" .
Acceptable hits:


migration docs


deprecated alias warnings


Codex adapter code


Codex-specific example clearly labeled as adapter use


tests checking migration/deprecation


Unacceptable hits:


core code requiring Codex


Copilot docs mentioning Codex as executor


README presenting Codex as canonical


universal schema using Codex-specific provenance


validation requiring Codex auth


package mode requiring Codex auth



16. Output Required
After implementation, produce:
# Phase A Universal Agent-Job Implementation Report## Executive Summary## What Changed## Canonical CLI## Schema v2 Implementation## Schema v1 Compatibility## Renderer Targets## Package Mode## Run Mode## Codex Adapter Isolation## Mock Executor## Copilot Support Model## Provenance Model## Examples Added## Documentation Updated## Tests Added or Updated## Tests Run## Test Results## Grep Checks## Files Changed## Compatibility Notes## Remaining Codex-Specific Surface Area## Remaining Claude-Specific Surface Area## Known Limitations## Risks## Recommended Next Phase## Human Verification Commands
Include exact commands:
agent-job validate examples/copilot-docs.job.yamlagent-job render examples/copilot-docs.job.yaml --target copilotagent-job package examples/copilot-docs.job.yaml --target copilotagent-job render examples/manual-refactor.job.yaml --target manualagent-job package examples/manual-refactor.job.yaml --target manualagent-job run examples/mock.job.yaml --executor mockagent-job run examples/copilot-docs.job.yaml --executor copilotagent-job report <package-or-run-dir>

17. Decision Gate
At the end, answer directly:
Can a Copilot-only environment use this repo without Codex?Can a human create a Copilot-ready job package?Does Copilot package mode avoid launching or faking Copilot execution?Is Codex now only an executor adapter?Is the schema executor-neutral?Is provenance agent-neutral?Does validation/render/package avoid requiring Codex auth?Is agent-job now the canonical CLI?Is codex-job deprecated or removed from canonical docs?
If any answer is no, explain exactly what remains.

18. Next Phase Recommendation
Do not implement the next phase.
Recommend one of:
Option A: Copilot package dogfood
Use agent-job package --target copilot for real tasks in a Copilot-only workflow.
Option B: Complete/ingest-report implementation
If package mode works but report normalization for external completions is missing.
Option C: Rename/package/install hardening
If the core pivot works but install/distribution is messy.
Option D: Adapter isolation cleanup
If Codex-specific code still leaks into core.
Base the recommendation on actual results.
The key thing: **do not let Codex implement `run --executor copilot` unless your production Copilot environment exposes an approved automation interface.** For now, Copilot support should be **package/render only**, plus optional completion ingestion.

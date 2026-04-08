# Codex-Job Skill — Live Observations Log

Running log of what works, what doesn't, and what needs fixing. Written during actual delegations so observations are grounded in real use.

Each entry records: what was delegated, what the skill did well, what it did poorly, and specific improvement suggestions.

---

## Session: 2026-04-08 — Hexstrike P7/P8 Delegation

**Project:** hexstrike-ai-reimagined (`/lump/apps/hexstrike-ai-reimagined`)
**Tickets:** P7-001, P7-002 (parallel wave 1), P7-003, P7-004, P8-001, P8-002 (sequential)
**Goal:** Implement Phase 7 (technology detection, parameter optimization, rate limiting, tool run stats) and Phase 8 (effectiveness-weighted decisions, data-driven confidence) from tickets in `docs/tickets-todo/`

### Pre-Delegation Observations (before first run)

**What the skill asks me to do well:**
- Clear model routing in SKILL.md (codex-mini for simple, gpt-5.4-mini for cross-cutting) — matches CLAUDE.md
- `--notify-cmd scripts/notify_terminal.sh` pattern for background monitoring

**Friction points before even launching:**
1. **No `--task-file` option** — For tickets this detailed, the task string is 2000+ chars. The current pattern requires embedding the full ticket content inline in `--task '<text>'`. Shell quoting of that string is fragile (the CODEX-JOB-SKILL-AUDIT noted this was a critical bug that was fixed, but the ergonomic problem remains). A `--task-file <path>` option that reads the ticket file directly would eliminate this entirely.

2. **work-log.md doesn't exist** — SKILL.md says "append to work-log.md" but there's no init step and no template. The first run fails silently on this step if the file is missing.

3. **Model routing not in SKILL.md** — The model routing table from CLAUDE.md (`gpt-5.1-codex-mini` vs `gpt-5.4-mini` thresholds) is not duplicated in SKILL.md, so a fresh session reading only SKILL.md gets slightly different guidance. SKILL.md just says "mini = default, gpt-5.4-mini = cross-cutting" without defining what "cross-cutting" means.

4. **Metrics write step is manual** — After each run I have to manually call `write_delegation_metric.py` with the right flags. There's no prompt reminder of which flags are needed, and the `--task-type`, `--risk`, `--delegated-model`, `--provider` flags have no defaults. A post-run checklist in the summary read step would help.

5. **`--task-file` not passed through by `invoke_codex_with_review.sh`** — `run_codex_task.sh` supports `--task-file <path>` (shown in its help) but `invoke_codex_with_review.sh` (the wrapper) doesn't recognize `--task-file` and exits with "Unknown argument". Since all real delegation goes through the wrapper, `--task-file` is effectively broken. **Fix:** `invoke_codex_with_review.sh` must parse and forward `--task-file` to `run_codex_task.sh` the same way it forwards `--task`.

6. **CRITICAL: `CODEX_API_KEY` env check is wrong for OAuth-authenticated installs** — `run_codex_task.sh` line 1053 calls `require_env_var "CODEX_API_KEY"` and hard-exits if it's not set. But the Codex CLI does NOT need `CODEX_API_KEY` when authenticated via OAuth (`~/.codex/auth.json` with `tokens.access_token`). The variable is checked but never passed to `codex exec`. Any environment where Codex was set up via `codex login` (OAuth) rather than a raw API key will fail immediately. **Fix:** Replace `require_env_var "CODEX_API_KEY"` with a soft check — verify either `CODEX_API_KEY` is set OR `~/.codex/auth.json` exists with a valid access token. Or remove the hard check entirely and let codex fail with its own auth error. Also `doctor_check_required_env "CODEX_API_KEY"` at line 277 should be similarly softened.

---

### Wave 1 Launch: P7-001 + P7-002 (parallel)

*(Entries filled in after runs complete)*

---

### Wave 2: P7-003 (rate_limiter_detector + executor hook)

**P7-003:** ✅ exit 0, 7/7 tests pass (1 self-corrected), 208,559 tokens, 338s, model: gpt-5.4-mini
- Self-corrected a test about the executor updating target_profile metadata — it had the wrong assertion shape initially. Fixed in same session.
- Cross-subsystem ticket (new skill + executor modification) handled cleanly by gpt-5.4-mini.

---

### Wave 3: P7-004 (tool_run_stats DB + admin tab)

**P7-004:** ✅ exit 0, 5/5 tests pass (1 self-corrected), 140,230 tokens, 415s, model: gpt-5.4-mini
- Lowest token count of all P7 tickets despite being the most complex (DB + backend + frontend). Possibly benefited from clear scope boundary in the ticket.
- The admin frontend tab was the riskiest part — passed without issue.

---

### Wave 4: P8-001 (effectiveness-weighted tool selection)

**P8-001:** ✅ exit 0, 6/6 tests pass, 322,926 tokens, 384s, model: gpt-5.1-codex-mini
- Clean pass, no self-corrections. The ticket's clean scope (skill modification + new repo, no frontend) worked well for codex-mini.
- Token count high (323k) for a pure skill ticket — likely due to needing to read and understand `decision_intelligence_skill.py` thoroughly before modifying.

---

### Wave 5: P8-002 (data-driven confidence bars)

**P8-002:** ✅ exit 0, 5/5 tests pass (4 self-corrected), **1,089,032 tokens**, 1077s, model: gpt-5.1-codex-mini
- **TOKEN BLOWUP.** 1M tokens is ~3-4x what any P7 ticket used. This is a critical observation.
- Root cause: P8-002 is a cross-cutting frontend ticket (TypeScript mapper + React component + Python test). The model struggled with the Python test needing to mock the TypeScript mapper behavior — the abstraction mismatch required many iteration cycles.
- **Action item:** Frontend-heavy tickets with Python integration tests are a bad fit for codex-mini. Either: (a) use gpt-5.4-mini for any ticket that spans Python tests + TypeScript implementation, or (b) split the Python test out into a separate ticket that only tests the backend mapper/serialization side.
- **Skill improvement needed:** Add a routing rule to SKILL.md: any ticket where the Python integration tests cover TypeScript/frontend behavior should be escalated to gpt-5.4-mini regardless of the complexity label.

---

### Wave 1 Results: P7-001 + P7-002

**P7-001 (technology_detector):** ✅ exit 0, 6/6 tests pass, 103,908 tokens, 201s
**P7-002 (parameter_optimizer):** ✅ exit 0, 5/5 tests pass, 238,367 tokens, 304s (1 self-corrected test failure)

**Observations:**
- P7-002 used ~2.3x more tokens than P7-001 despite similar complexity. The extra tokens came from it having to self-correct a failing test case for wordpress profile filtering — the `config/tool_profiles/v1.json` profile check filtered out `cms_wordpress` (the profile didn't exist in the file), requiring it to fix the test assertion. This is expected behavior and a good sign — the skill self-healed.
- Both tasks showed correct ticket → implementation fidelity: dataclasses matched specs exactly, guardrails followed (no backend imports).
- `session_id` was `null` for P7-001, non-null for P7-002. Not clear why P7-001 has no session id — possibly a parsing difference in the runner. **Observation logged:** session_id extraction is inconsistent.
- `sid` in summary JSON is `null` for P7-001 (`"sid":null`) but populated for P7-002. This means `--resume` from P7-001 run is impossible. The runner script should warn when sid is null after a successful run.

---

## Skill Improvement Backlog

Issues identified across all sessions. Each item has a severity and a proposed fix.

| # | Issue | Severity | Status |
|---|---|---|---|
| 1 | No `--task-file` option — fragile shell quoting for large tasks | High | open |
| 2 | `work-log.md` missing init step / no template | Medium | open |
| 3 | Model routing definition vague in SKILL.md ("cross-cutting" undefined) | Medium | open |
| 4 | Metrics write step is fully manual with no post-run checklist | Medium | open |
| 5 | Token extraction from summary always null (parse_codex_run.py doesn't extract input/output separately) | Medium | open — noted in prior session |
| 6 | No narrower review trigger — review fires on any non-zero even for warnings | Low | open — noted in prior session |
| 7 | No orphan process cleanup after subagent completion — codex child procs may persist | Medium | **fixed** — `cleanup_codex_children` added to wrapper |
| 8 | session_id is null in summary for some runs (P7-001) — makes `--resume` impossible | Medium | open |
| 9 | Frontend+Python cross-cutting tickets cause token blowup on codex-mini — P8-002 hit 1M tokens | High | open — needs model routing rule update |
| 10 | No standing guardrails injected into agent task prompt — agents could write/run tests unsolicited | High | **fixed** — guardrail preamble prepended to every task in wrapper |

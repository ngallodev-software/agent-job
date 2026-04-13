# Duplicate Files Analysis

Generated: 2026-04-13
Task: Compare duplicate files and determine which is authoritative

## Root /scripts/ vs /codex-job/scripts/

### Finding: Root scripts are WRAPPERS, not duplicates

All root `/scripts/*.sh` and `/scripts/*.py` files are 12-20 line wrappers that delegate to `codex-job/scripts/`.

**Example** (`scripts/run_codex_task.sh`):
```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="$SCRIPT_DIR/../codex-job/scripts/run_codex_task.sh"

if [[ ! -f "$TARGET" ]]; then
  echo "Error: canonical runner not found at $TARGET" >&2
  exit 2
fi

exec "$TARGET" "$@"
```

### Decision: KEEP root /scripts/ as wrappers

**Reason**: These provide a stable entry point for:
- Existing installations
- Documentation examples
- Backwards compatibility

**Action**: No changes to root `/scripts/` wrappers

---

## /codex-job/SKILL.md vs /.claude/skills/codex-job/SKILL.md

### Modification Dates:
- `codex-job/SKILL.md`: Apr 8, 2026
- `.claude/skills/codex-job/SKILL.md`: Apr 12, 2026 (NEWER)

### Key Differences:

**.claude version has** (newer content):
- More detailed description with "async execution, smart failure handling, session resume"
- `disable-model-invocation: false` frontmatter
- "minimizing Claude token burn" language
- Simpler model tier list (removed delegation guardrails section)
- Reference to `tools/write_delegation_metric.py` instead of `scripts/`
- Success rate threshold guidance (70% rolling success)
- "Load only what you need" for references

**codex-job version has** (older but more detailed):
- Delegation Guardrails section (no tests without instruction, write set authority, no scope expansion)
- Detailed model selection with task complexity guidance
- More explicit script paths and invocation patterns
- Larger model authorization note

### Decision: MERGE both versions

**Best approach**: 
1. Take `.claude/skills/codex-job/SKILL.md` as base (newer)
2. Add back **Delegation Guardrails** section from `codex-job/SKILL.md` (important constraints)
3. Add back detailed model selection guidance
4. Fix script path references (should be `scripts/` not `tools/`)
5. Make `codex-job/SKILL.md` the single source of truth
6. Move `.claude/skills/codex-job/SKILL.md` to deprecated/

---

## Other Duplicates

### .claude/skills/codex-job/ directory structure

The entire `.claude/skills/codex-job/` appears to be an **installed copy** from the install script testing.

**Contents**:
- `SKILL.md` (analyzed above)
- `references/` (may have useful content)
- `tools/` (contains copies of scripts)

**Decision**: 
- Extract any unique content from `.claude/skills/codex-job/references/`
- Move entire `.claude/skills/codex-job/` to `deprecated/.claude/skills/codex-job/`
- Preserve folder hierarchy for historical reference

---

## Summary

| Source | Target | Action |
|--------|--------|--------|
| `/scripts/*.sh`, `/scripts/*.py` | - | KEEP (wrappers, not duplicates) |
| `codex-job/SKILL.md` | - | MERGE with .claude version, become authoritative |
| `.claude/skills/codex-job/SKILL.md` | `deprecated/` | Move after merge |
| `.claude/skills/codex-job/*` | `deprecated/` | Move entire directory |
| `codex-job/scripts/*` | - | KEEP (canonical implementation) |

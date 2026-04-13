# Parallel Bash Tool Call Error Analysis

Date: 2026-04-13
Context: Repository reorganization task - moving files to new directory structure

## Error Pattern

### What Happened
Attempted to run 4 parallel `mv` commands after creating subdirectories:
1. `mkdir -p future-plans/queue future-plans/scripts future-plans/docs future-plans/planning`
2. Parallel mv commands to move files into those directories

### Error Message
```
mv: target '/lump/apps/invoke-codex-from-claude/future-plans/queue/': No such file or directory
```

Then all subsequent parallel calls were cancelled:
```
<tool_use_error>Cancelled: parallel tool call Bash(mv /lump/apps/invoke-codex-from-claude/c…) errored</tool_use_error>
```

## Root Cause Analysis

### Primary Issue: Working Directory Confusion
The `mkdir` command was executed from working directory `/lump/apps/invoke-codex-from-claude/.claude/agents/team/` (because that's where a prior `cd` command left the shell).

When creating relative paths `future-plans/queue`, it created:
```
/lump/apps/invoke-codex-from-claude/.claude/agents/team/future-plans/queue
```

But the subsequent `mv` commands used absolute paths expecting:
```
/lump/apps/invoke-codex-from-claude/future-plans/queue/
```

### Secondary Issue: mv /ui/ Overwrote Directory Structure
Earlier in the sequence, running:
```bash
mv /lump/apps/invoke-codex-from-claude/ui /lump/apps/invoke-codex-from-claude/future-plans/
```

This moved the entire `ui/` directory to **become** the `future-plans/` directory, replacing the empty directory structure we'd just created. This is because `mv source/ dest/` when `dest/` exists will move source INTO dest, but when creating fresh it can replace.

### Tertiary Issue: Parallel Tool Call Failure Cascade
When the first parallel `mv` command failed, Claude Code's tool execution engine **cancelled all remaining parallel tool calls** in that batch to avoid cascading failures with dependencies.

This is actually CORRECT behavior - if mkdir failed, running the mv commands would all fail. But it meant I lost visibility into which specific commands were attempted.

## Lessons Learned

### 1. Always Use Absolute Paths or Explicit `cd`
**Bad:**
```bash
mkdir -p future-plans/queue  # Creates in CWD, which may not be repo root
mv file.py future-plans/queue/
```

**Good:**
```bash
cd /lump/apps/invoke-codex-from-claude  # Explicit cd to known location
mkdir -p future-plans/queue
mv file.py future-plans/queue/
```

**Better:**
```bash
mkdir -p /lump/apps/invoke-codex-from-claude/future-plans/queue  # Absolute paths
mv /path/to/file.py /lump/apps/invoke-codex-from-claude/future-plans/queue/
```

### 2. Don't Mix mv of Directories with mkdir of Subdirectories
**Bad sequence:**
```bash
mkdir -p future-plans/queue future-plans/scripts
mv /path/to/ui/ /path/to/future-plans/  # Overwrites the directory!
mv files future-plans/queue/  # Now fails, queue is gone
```

**Good sequence:**
```bash
mkdir -p future-plans/agents future-plans/ui future-plans/queue future-plans/scripts
mv /path/to/ui/* /path/to/future-plans/ui/  # Move contents, not directory
# OR
mv /path/to/ui /path/to/future-plans/ui  # Rename/move after mkdir
```

### 3. Verify Directory Existence Before Dependent Operations
**Pattern:**
```bash
mkdir -p target/dir && ls -la target/dir  # Verify it worked
mv source.file target/dir/  # Now safe to proceed
```

### 4. Avoid Long Parallel Chains with Sequential Dependencies
**Bad:**
```bash
# All in one parallel batch:
mkdir -p dirs
mv file1 dirs/
mv file2 dirs/
mv file3 dirs/
```

If mkdir fails or creates in wrong place, all 3 mv commands fail and get cancelled.

**Good:**
```bash
# Separate mkdir from moves:
mkdir -p dirs && ls dirs  # Verify in one command
# Then batch the moves (they're all equivalent operations):
mv file1 file2 file3 dirs/
```

### 5. Bash State Persists: CWD Carries Over Between Commands
**Key insight:** Each Bash tool call inherits the working directory from the PREVIOUS Bash call in the conversation.

```bash
# Command 1
cd /some/path

# Command 2 (later in conversation)
ls  # Lists /some/path, not the original CWD!
```

**Mitigation:** Always `cd` to known absolute path at start of command if directory matters, OR use absolute paths exclusively.

## Corrected Approach

```bash
# CORRECT: Explicit cd to repo root, verify all steps
cd /lump/apps/invoke-codex-from-claude
mkdir -p future-plans/queue future-plans/scripts future-plans/docs future-plans/planning
ls -la future-plans/  # Verify structure
mv codex-job/scripts/job_queue.py future-plans/queue/
mv scripts/bootstrap_ui.sh future-plans/scripts/
# etc.
```

## Memory Update Recommendation

Store in feedback memory:
- Always use absolute paths OR explicit `cd` to known location before mkdir/mv operations
- Don't run parallel mv commands with shared dependencies; batch them after confirming prerequisites
- Verify directory creation before moving files into it
- Bash CWD persists across tool calls - don't assume you're in repo root

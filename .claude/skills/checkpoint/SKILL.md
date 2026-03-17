---
name: checkpoint
description: Save current research state — run tests, update docs, commit. Use at natural stopping points.
user-invocable: true
argument-hint: "[optional commit message]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Research Checkpoint

## Task

Create a clean checkpoint of current research progress.

## Steps

### 1. Run tests
```bash
python -m pytest tests/ -v --tb=short -q
```
If tests fail, fix them before checkpointing. Never checkpoint broken code.

### 2. Check for uncommitted work
```bash
git status
git diff --stat
```

### 3. Review what changed since last commit
```bash
git log --oneline -1
git diff HEAD --stat
```

### 4. Update documentation if needed
- If code behavior changed: update `docs/implementation.md`
- If experiment results are new: update `docs/results_tracking.md`
- If theory evolved: update `docs/theory.md`
- Ask the user before rewriting any narrative in results_tracking.md

### 5. Update conductor state (if conductor/ exists)
Update `conductor/STATE.md` with current findings and session count.

### 6. Commit
Stage relevant files and commit with a descriptive message.
If `$ARGUMENTS` was provided, use that as the commit message.
Otherwise, generate a message based on what changed.

### 7. Report
- Files committed
- Current test status
- Current phase and where we are in it

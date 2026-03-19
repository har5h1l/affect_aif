---
name: checkpoint
description: Save research state — run tests, update docs, commit.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

Research checkpoint: `$ARGUMENTS`

1. Run pytest to verify clean state
2. Check for uncommitted changes (git status)
3. Update conductor/STATE.md with current findings
4. Stage and commit with descriptive message

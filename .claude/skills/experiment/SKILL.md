---
name: experiment
description: Run an experiment with safety validation (tests first, smoke test, then full run).
allowed-tools: Read, Bash, Glob, Grep, Agent
---

Run experiment: `$ARGUMENTS`

Safety protocol:
1. Run pytest — must pass
2. Smoke test (5 seeds) — check it works
3. Full run — only after smoke test passes
4. Save results to results/ directory

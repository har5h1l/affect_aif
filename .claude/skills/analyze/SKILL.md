---
name: analyze
description: Analyze experiment results and compare against hypotheses.
allowed-tools: Read, Grep, Glob, Bash, Agent
---

Analyze experiment results at the specified path.

1. Find result files: `$ARGUMENTS` (or latest in results/)
2. If an analysis script exists (scripts/run_analysis.py), run it
3. Launch the results-analyzer agent for detailed analysis
4. Summarize findings and hypothesis status

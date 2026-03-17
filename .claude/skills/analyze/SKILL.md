---
name: analyze
description: Analyze experiment results and compare against hypotheses. Use after running experiments or to understand existing results.
user-invocable: true
argument-hint: "[results_path_or_batch_name]"
allowed-tools: Read, Grep, Glob, Bash, Agent
---

# Analyze Experiment Results

## Task

Analyze the experiment results at `$ARGUMENTS` and provide an interpretation.

## Steps

1. **Find results**: If a path was given, use it. Otherwise search `results/` for the most recent CSV files:
   ```
   ls -lt results/*/results.csv | head -5
   ```

2. **Run analysis script**:
   ```
   python scripts/run_analysis.py --results <path>/results.csv --output-dir <path>/figures
   ```

3. **Read the hypothesis scorecard**: Read `docs/results_tracking.md` to understand what we're testing

4. **Launch results-analyzer agent** to do the detailed analysis

5. **Summarize for the user**:
   - What conditions were tested
   - Key quantitative results (with numbers)
   - Which hypotheses are supported/contradicted
   - Recommended next steps
   - Any surprises worth investigating

## If no arguments given

List available result directories and ask which to analyze:
```
ls -d results/*/
```

---
name: iterate
description: Full research iteration loop — orient, plan, code, test, experiment, analyze, interpret, document. The core autonomous workflow.
user-invocable: true
argument-hint: "[optional focus area or hypothesis]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent
---

# Research Iteration

## Task

Execute one complete iteration of the research loop for affect_aif.
Focus area: $ARGUMENTS

## The Loop

### 1. Orient
Read current state:
- `docs/long_term_plan.md` — current phase and tasks
- `docs/results_tracking.md` — hypothesis scorecard and latest results
- `conductor/STATE.md` — conductor findings (if exists)
- `git log --oneline -5` — recent work

Identify: What is the smallest next step that advances the current phase?

### 2. Plan
- If `$ARGUMENTS` specifies a focus, use that
- Otherwise, pick the next incomplete task from the current phase
- Describe the plan in 2-3 sentences before proceeding
- If the step is ambiguous or requires a fundamental change, STOP and ask

### 3. Code
Make changes. Keep them minimal and focused.
- Modify only what's needed
- Don't over-engineer
- Follow patterns in existing code

### 4. Test
```bash
python -m pytest tests/ -v --tb=short
```
All tests must pass. If they fail, fix the code (not the tests, unless the test was wrong).

### 5. Experiment
Run a small experiment (5-10 seeds) to validate the change:
```bash
python scripts/run_experiment.py --config <relevant_config> --output-dir results/<name>_explore --batch-name <name>_explore
```

### 6. Analyze
Use the results-analyzer agent or run analysis directly:
```bash
python scripts/run_analysis.py --results <path>/results.csv --output-dir <path>/figures
```

### 7. Interpret
Compare results against the hypothesis scorecard.
- Does this change the story?
- If YES: flag it clearly, do NOT silently update the narrative
- If NO: record the evidence

### 8. Document
Update docs to reflect findings:
- `docs/results_tracking.md` — scorecard updates (with evidence)
- `docs/implementation.md` — if code behavior changed
- `docs/theory.md` — only if theory implications are clear

### 9. Checkpoint
Commit with a descriptive message. Use `/checkpoint` skill.

## Safety rules
- Tests before experiments (always)
- Small before large (5 seeds, then 50-100)
- Never delete results
- Never silently rewrite narrative
- Stop and ask if results are surprising or phase-completing

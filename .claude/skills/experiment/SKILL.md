---
name: experiment
description: Run an experiment with safety validation (tests first, smoke test, then full run). Use when you need to run experiments.
user-invocable: true
argument-hint: "[config_name] [--seeds N] [--rounds N]"
allowed-tools: Read, Bash, Glob, Grep, Agent
---

# Run Experiment

## Task

Run the experiment config `$ARGUMENTS` with full safety validation.

## Steps

### 1. Parse arguments
- First arg: config name (without path, e.g., `default` or `betrayal_stress`)
- `--seeds N`: number of replications (default: 50)
- `--rounds N`: number of rounds (uses config default if not specified)

### 2. Validate config exists
```bash
ls affect_aif/configs/${config_name}.json
```
If not found, list available configs:
```bash
ls affect_aif/configs/*.json
```

### 3. Run tests (MANDATORY — safety invariant)
```bash
python -m pytest tests/ -v --tb=short -q
```
If tests fail, STOP. Do not proceed. Report failures.

### 4. Smoke test (5 seeds)
```bash
python scripts/run_experiment.py \
  --config affect_aif/configs/${config_name}.json \
  --output-dir results/${config_name}_smoke \
  --batch-name ${config_name}_smoke
```
Check output exists and has reasonable values.

### 5. Full run (only if smoke test passes)
```bash
python scripts/run_experiment.py \
  --config affect_aif/configs/${config_name}.json \
  --output-dir results/${config_name} \
  --batch-name ${config_name} \
  --workers 4
```

### 6. Report
- Config used, conditions, seeds, rounds
- Wall-clock time
- Output path
- Offer to run `/analyze` on the results

## Sizing guide
| Purpose | Seeds | Rounds |
|---------|-------|--------|
| Smoke test | 5 | 50 |
| Exploration | 10 | 100 |
| Confirmation | 50-100 | 200 |

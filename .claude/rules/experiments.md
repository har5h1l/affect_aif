---
paths:
  - "scripts/run_*.py"
  - "affect_aif/experiment/**"
  - "affect_aif/configs/**"
---

# Experiment Rules

- Always run `python -m pytest tests/ -v` before any experiment
- Smoke test (5 seeds) before full runs (50-100 seeds)
- Never overwrite existing result files — use unique batch names
- Config changes should be in JSON files, not hardcoded
- Log all experiment parameters for reproducibility
- If an experiment will take >30 minutes, warn the user before starting

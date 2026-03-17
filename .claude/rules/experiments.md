---
paths:
  - "scripts/run_*.py"
  - "**/configs/**"
  - "**/experiment/**"
---

When editing experiment scripts or configs:
- Always run pytest before any experiment
- Use small replications (5 seeds) for smoke tests
- Never hardcode seeds — use config files
- Save all results to results/ directory
- Never overwrite existing result files

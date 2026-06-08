# Diagnostics

Diagnostics are not paper evidence by default. They support smoke checks,
reviewer controls, and informative mechanism probes.

Smoke dry-run:

```bash
python scripts/experiment/run.py \
  --config configs/diagnostics/smoke/trust_smoke.toml \
  --batch-name smoke \
  --workers 1 \
  --dry-run
```

Reviewer-facing H1 controls live under
`configs/diagnostics/h1_model_fitness/`. Other H-card probes are grouped by
hypothesis id under `configs/diagnostics/`.

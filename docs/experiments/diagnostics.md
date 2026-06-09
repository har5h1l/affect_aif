# Diagnostics

Diagnostics are not paper evidence by default. They support smoke checks,
reviewer controls, and informative mechanism probes.

## Smoke Dry-Run

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

## Main Uses

- `configs/diagnostics/smoke/trust_smoke.toml`: smallest runner sanity check.
- H0 policy-openness configs: show when the precision channel can and cannot
  move behavior.
- H1 reward-control configs: reviewer ladder if the model-fitness claim needs
  stronger reward/exposure decomposition.
- H2 tracked-only lesion configs: separate beta tracking from beta-to-gamma
  deployment.
- H3 locality configs: compare partner-local precision against shared beta.
- H4 allocation configs: agent-choice social allocation probes.
- H5 precision-sensitivity configs: expanded volatility probes beyond the
  final H5 paper config.
- H6 perturbation configs: older profile-style dynamics retained for context.

Compact diagnostic summaries tracked in git live under `results/diagnostics/`.
Full diagnostic raw runs are retained on `server` when they are not needed in
the local paper handoff packet.

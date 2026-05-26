# Next Runs

Re-run the verification gate below immediately before launching full
statistical experiments so queued runs carry fresh local provenance.

## Verification Gate

Run these before scheduling current-evidence experiments:

```bash
python -m pytest tests/ -q
python -m ruff check .
python -m mypy
git diff --check
```

## Post-Verification Queue

The May 18, 2026 H0-H5 queue completed and is interpreted in
`docs/results/current.md`. Follow-up analysis added partner-level H1 and
overconfident-wrong-belief H3 reports. The May 19, 2026
`betrayal_reallocation` follow-up completed and is retained as a small H3
pilot. The higher-replication H1/H3 split confirmation also completed under
`results/confirm_h1_h3_split_20260519/` and is documented in
`docs/results/runs/2026-05-21-h1-h3-confirmation.md`.

The manuscript write-up has been stabilized. The global-beta/locality ablation
has also been implemented as a smoke-test surface under
`configs/trust/hypotheses/h6_locality_interference/global_beta_smoke.toml`.
Keep follow-up experiments narrow and use them to test structure before adding
more seeds.

Run only 3-5 seed smoke tests at first, keep `--workers 1`, and do not update
manuscript interpretation from new outputs until the user reviews the results.

## Current H6 Smoke Provenance

The completed one-worker smoke run is:

```bash
python scripts/experiment/run.py --config configs/trust/hypotheses/h6_locality_interference/global_beta_smoke.toml --output-dir results --batch-name global_beta_locality_smoke_quick_20260525 --workers 1
```

Rows are complete for `none`, `precision`, `tracked_only`, and `global_beta`
with two seeds, 40 rounds, and planning horizon 2:

```text
results/global_beta_locality_smoke_quick_20260525/h6/global_beta_smoke/results.csv
results/global_beta_locality_smoke_quick_20260525/h6/global_beta_smoke/analysis/
```

This is a diagnostic smoke run only. It verifies the new condition, logging,
and cross-partner interference analysis; it is not yet promoted into the
manuscript evidence hierarchy.

## Completed H6 Discovery Batch

The H6 discovery batch completed under:

```text
results/h6_global_beta_discovery_20260525/
```

The completed command was:

```bash
python scripts/experiment/run.py \
  --config configs/trust/hypotheses/h6_locality_interference/global_beta_model_fitness_probe.toml \
  --config configs/trust/hypotheses/h6_locality_interference/global_beta_deployment_probe.toml \
  --config configs/trust/hypotheses/h6_locality_interference/global_beta_partner_choice_probe.toml \
  --config configs/trust/hypotheses/h6_locality_interference/global_beta_betrayal_probe.toml \
  --config configs/trust/hypotheses/h6_locality_interference/lesion_family_probe.toml \
  --output-dir results \
  --batch-name h6_global_beta_discovery_20260525 \
  --workers 1
```

This is not a full-seed confirmation. It is a complete discovery queue across
the main mechanism regimes plus a lesion-family probe, with five seeds for the
global-beta regime probes and three seeds for the larger lesion-family probe.
All variants use planning horizon 2 to keep the one-worker queue tractable. It
wrote final `results.csv` files for:

- `global_beta_model_fitness_probe`
- `global_beta_deployment_probe`
- `global_beta_partner_choice_probe`
- `global_beta_betrayal_probe`
- `lesion_family_probe`

Standalone analysis has been run for each experiment:

```bash
python scripts/analysis/analyze.py --results results/h6_global_beta_discovery_20260525/h6/<experiment_id>/results.csv --output-dir results/h6_global_beta_discovery_20260525/h6/<experiment_id>/analysis
```

Treat these outputs as discovery evidence awaiting user review. Do not promote
H6 into result interpretation docs or manuscript claims until the user approves
the evidence read.

## Optional Confirmation Queue

### 1. Higher-Rep Open-Regime Affect, H1 Model Fitness, and Deployment

```bash
python scripts/experiment/run.py --config configs/trust/hypotheses/h0_openness/graded_choice.toml --config configs/trust/hypotheses/h1_model_fitness/reliability_vs_reward.toml --config configs/trust/hypotheses/h2_deployment/lesion_open_regime.toml --output-dir results --batch-name confirm_open_model_deployment --workers 1
```

### 2. Higher-Rep Social Choice

```bash
python scripts/experiment/run.py --config configs/trust/hypotheses/h4_social_choice/partner_choice.toml --output-dir results --batch-name confirm_social_choice --workers 1
```

### 2b. Manuscript Open/Social Confirmation

This config-only batch promotes the H0/H2/H4 supporting evidence from five
seeds to 30 seeds without changing runtime behavior. It should write under
`results/manuscript_open_social_confirm_20260525_single_worker/`.

```bash
python scripts/experiment/run.py --config configs/trust/hypotheses/h0_openness/graded_choice_confirm.toml --config configs/trust/hypotheses/h2_deployment/lesion_open_regime_confirm.toml --config configs/trust/hypotheses/h4_social_choice/partner_choice_confirm.toml --output-dir results --batch-name manuscript_open_social_confirm_20260525_single_worker --workers 1
```

`results/manuscript_open_social_confirm_20260525/` is an aborted partial
parallel run started before the one-worker constraint was clarified; do not
interpret it as evidence.

### 3. Optional H3 Stress Robustness

The H3 split confirmation already ran as
`results/confirm_h1_h3_split_20260519/`. Re-run or modify this only if a
write-up or review process requires a specific stress-regime robustness check.

```bash
python scripts/experiment/run.py --config configs/trust/hypotheses/h3_stress_response/betrayal_reallocation_confirm.toml --output-dir results --batch-name confirm_h3_stress_robustness --workers 1
```

## Canonical Full Queue

The commands below remain the canonical H0-H5 queue for a fresh full rerun.
They are not the immediate next action.

### 1. H0 Openness Gate

```bash
python scripts/experiment/run.py --config configs/trust/hypotheses/h0_openness/shallow_binary.toml --config configs/trust/hypotheses/h0_openness/graded_choice.toml --config configs/trust/hypotheses/h0_openness/graded_betrayal.toml --output-dir results --batch-name h0_openness --workers 1
```

### 2. H1 Model Fitness / Reliability vs Reward

```bash
python scripts/experiment/run.py --config configs/trust/hypotheses/h1_model_fitness/reliability_vs_reward.toml --output-dir results --batch-name h1_model_fitness --workers 1
```

### 3. H2 Deployment / Lesion

```bash
python scripts/experiment/run.py --config configs/trust/hypotheses/h2_deployment/lesion_open_regime.toml --output-dir results --batch-name h2_deployment --workers 1
```

### 4. H3 Stress Response / Betrayal Stance Switch

```bash
python scripts/experiment/run.py --config configs/trust/hypotheses/h3_stress_response/betrayal_choice.toml --output-dir results --batch-name h3_stress_response --workers 1
```

### 5. H4 Social Choice / Partner Selection

```bash
python scripts/experiment/run.py --config configs/trust/hypotheses/h4_social_choice/partner_choice.toml --output-dir results --batch-name h4_social_choice --workers 1
```

### 6. H5 Perturbation Phenotypes / Clinical-Like Variants

```bash
python scripts/experiment/run.py --config configs/trust/hypotheses/h5_perturbation/clinical_betrayal.toml --config configs/trust/hypotheses/h5_perturbation/clinical_dynamics.toml --config configs/trust/hypotheses/h5_perturbation/affect_sensitivity.toml --output-dir results --batch-name h5_perturbation --workers 1
```

### 7. H6 Locality / Global-Beta Ablation

Use this only for smoke-scale discovery until the run design is reviewed:

```bash
python scripts/experiment/run.py --config configs/trust/hypotheses/h6_locality_interference/global_beta_smoke.toml --output-dir results --batch-name global_beta_locality_smoke_next --workers 1
```

Run `scripts/analysis/analyze.py` on the output directory afterward to produce
`cross_partner_interference_summary.csv` and `global_vs_local_beta_summary.csv`.

### 8. Multi-Focal Descriptive Runs

Multi-focal configs currently use the package API directly; E2 analysis remains
descriptive until a dedicated multi-focal analysis script exists.

```bash
python - <<'PY'
import json
from pathlib import Path

import numpy as np
import pandas as pd

from experiments.multifocal.config import MultiFocalConfig
from experiments.multifocal.runner import MultiFocalRunner
from experiments.trust.factory import create_agents_from_multi_focal_config

configs = [
    Path("experiments/multifocal/configs/e2_homogeneous.json"),
    Path("experiments/multifocal/configs/e2_clinical_mix.json"),
    Path("experiments/multifocal/configs/e2_assortative.json"),
]
root = Path("results/multifocal_descriptive")
for path in configs:
    raw = json.loads(path.read_text())
    cfg = MultiFocalConfig.from_dict(raw)
    agents = create_agents_from_multi_focal_config(cfg, seed=cfg.random_seed)
    rows = MultiFocalRunner(cfg, agents, rng=np.random.default_rng(cfg.random_seed)).run()
    out = root / path.stem
    out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out / "results.csv", index=False)
    (out / "config.json").write_text(json.dumps(raw, indent=2))
    print(f"{path} -> {out / 'results.csv'}")
PY
```

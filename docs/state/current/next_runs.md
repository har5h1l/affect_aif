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

There is no immediate experiment queue. The recommended next action is write-up
stabilization: consolidate the results narrative, promote H1 as a confirmed
model-fitness readout, and keep H3 framed as a stress boundary condition where
affective precision changes deployment but can hurt payoff.

## Optional Confirmation Queue

### 1. Higher-Rep Open-Regime Affect, H1 Model Fitness, and Deployment

```bash
python scripts/experiment/run.py --config configs/trust/hypotheses/h0_openness/graded_choice.toml --config configs/trust/hypotheses/h1_model_fitness/reliability_vs_reward.toml --config configs/trust/hypotheses/h2_deployment/lesion_open_regime.toml --output-dir results --batch-name confirm_open_model_deployment --workers 3
```

### 2. Higher-Rep Social Choice

```bash
python scripts/experiment/run.py --config configs/trust/hypotheses/h4_social_choice/partner_choice.toml --output-dir results --batch-name confirm_social_choice --workers 3
```

### 3. Optional H3 Stress Robustness

The H3 split confirmation already ran as
`results/confirm_h1_h3_split_20260519/`. Re-run or modify this only if a
write-up or review process requires a specific stress-regime robustness check.

```bash
python scripts/experiment/run.py --config configs/trust/hypotheses/h3_stress_response/betrayal_reallocation_confirm.toml --output-dir results --batch-name confirm_h3_stress_robustness --workers 3
```

## Canonical Full Queue

The commands below remain the canonical H0-H5 queue for a fresh full rerun.
They are not the immediate next action.

### 1. H0 Openness Gate

```bash
python scripts/experiment/run.py --config configs/trust/hypotheses/h0_openness/shallow_binary.toml --config configs/trust/hypotheses/h0_openness/graded_choice.toml --config configs/trust/hypotheses/h0_openness/graded_betrayal.toml --output-dir results --batch-name h0_openness --workers 3
```

### 2. H1 Model Fitness / Reliability vs Reward

```bash
python scripts/experiment/run.py --config configs/trust/hypotheses/h1_model_fitness/reliability_vs_reward.toml --output-dir results --batch-name h1_model_fitness --workers 3
```

### 3. H2 Deployment / Lesion

```bash
python scripts/experiment/run.py --config configs/trust/hypotheses/h2_deployment/lesion_open_regime.toml --output-dir results --batch-name h2_deployment --workers 3
```

### 4. H3 Stress Response / Betrayal Stance Switch

```bash
python scripts/experiment/run.py --config configs/trust/hypotheses/h3_stress_response/betrayal_choice.toml --output-dir results --batch-name h3_stress_response --workers 3
```

### 5. H4 Social Choice / Partner Selection

```bash
python scripts/experiment/run.py --config configs/trust/hypotheses/h4_social_choice/partner_choice.toml --output-dir results --batch-name h4_social_choice --workers 3
```

### 6. H5 Perturbation Phenotypes / Clinical-Like Variants

```bash
python scripts/experiment/run.py --config configs/trust/hypotheses/h5_perturbation/clinical_betrayal.toml --config configs/trust/hypotheses/h5_perturbation/clinical_dynamics.toml --config configs/trust/hypotheses/h5_perturbation/affect_sensitivity.toml --output-dir results --batch-name h5_perturbation --workers 3
```

### 7. Optional Factorization Ablation

A future global-beta ablation can compare per-partner beta against a shared
precision state. Keep it outside the core H0-H5 queue unless we decide the
factorization claim needs direct model-comparison evidence.

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

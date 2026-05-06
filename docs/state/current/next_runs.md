# Next Runs

The reusable-core/task-package restructure is locally verified and synced to the
Mango `server` workspace. Re-run the verification gate below immediately before
launching full statistical experiments so the queued runs carry fresh local
provenance.

## Verification Gate

Run these before scheduling current-evidence experiments:

```bash
python -m pytest tests/ -q
python -m ruff check .
python -m mypy
git diff --check
```

## Post-Verification Queue

### 1. H0 Openness Gate / Shallow Tau 1-3

```bash
python scripts/experiment/run.py --config experiments/trust/configs/h0_shallow_policy_regime.json --output-dir results --batch-name h0_openness_gate --workers 12
python scripts/analysis/analyze.py --results results/h0_openness_gate/h0_shallow_policy_regime/results.csv --output-dir results/h0_openness_gate/h0_shallow_policy_regime/analysis
```

### 2. H1 Model Fitness / Reliability vs Reward

```bash
python scripts/experiment/run.py --config experiments/trust/configs/h1_model_fitness_factorial.json --output-dir results --batch-name h1_model_fitness --workers 12
python scripts/analysis/analyze.py --results results/h1_model_fitness/h1_model_fitness_factorial/results.csv --output-dir results/h1_model_fitness/h1_model_fitness_factorial/analysis
```

### 3. H2 Deployment / Lesion

```bash
python scripts/experiment/run.py --config experiments/trust/configs/h2_deployment_lesion.json --output-dir results --batch-name h2_deployment --workers 12
python scripts/analysis/analyze.py --results results/h2_deployment/h2_deployment_lesion/results.csv --output-dir results/h2_deployment/h2_deployment_lesion/analysis
```

### 4. H3 Stress Response / Betrayal Stance Switch

```bash
python scripts/experiment/run.py --config experiments/trust/configs/h3_betrayal_volatility.json --output-dir results --batch-name h3_stress_response --workers 12
python scripts/analysis/analyze.py --results results/h3_stress_response/h3_betrayal_volatility/results.csv --output-dir results/h3_stress_response/h3_betrayal_volatility/analysis
```

### 5. H4 Social Choice / Partner Selection

```bash
python scripts/experiment/run.py --config experiments/trust/configs/h4_social_choice.json --output-dir results --batch-name h4_social_choice --workers 12
python scripts/analysis/analyze.py --results results/h4_social_choice/h4_social_choice/results.csv --output-dir results/h4_social_choice/h4_social_choice/analysis
```

### 6. H5 Perturbation Phenotypes / Clinical-Like Variants

```bash
python scripts/experiment/run.py --config experiments/trust/configs/h5_clinical_betrayal.json --config experiments/trust/configs/h5_clinical_phenotypes.json --config experiments/trust/configs/h5_sensitivity_sweep.json --output-dir results --batch-name h5_perturbation_phenotypes --workers 12
python scripts/analysis/analyze.py --results results/h5_perturbation_phenotypes/h5_clinical_betrayal/results.csv --output-dir results/h5_perturbation_phenotypes/h5_clinical_betrayal/analysis
python scripts/analysis/analyze.py --results results/h5_perturbation_phenotypes/h5_clinical_phenotypes/results.csv --output-dir results/h5_perturbation_phenotypes/h5_clinical_phenotypes/analysis
python scripts/analysis/analyze.py --results results/h5_perturbation_phenotypes/h5_sensitivity_sweep/results.csv --output-dir results/h5_perturbation_phenotypes/h5_sensitivity_sweep/analysis
```

### 7. H0 Openness Gate / Graded Precision-Channel Tests

```bash
python scripts/experiment/run.py --config experiments/trust/configs/h0_graded_policy_regime.json --config experiments/trust/configs/h0_graded_betrayal.json --output-dir results --batch-name h0_openness_gate --workers 12
python scripts/analysis/analyze.py --results results/h0_openness_gate/h0_graded_policy_regime/results.csv --output-dir results/h0_openness_gate/h0_graded_policy_regime/analysis
python scripts/analysis/analyze.py --results results/h0_openness_gate/h0_graded_betrayal/results.csv --output-dir results/h0_openness_gate/h0_graded_betrayal/analysis
```

### 8. Optional Factorization Ablation

A future global-beta ablation can compare per-partner beta against a shared
precision state. Keep it outside the core H0-H5 queue unless we decide the
factorization claim needs direct model-comparison evidence.

### 9. Multi-Focal Descriptive Runs

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

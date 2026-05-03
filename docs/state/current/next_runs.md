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

### 1. Shallow Affect / Tau 1-3

```bash
python scripts/experiment/run.py --config experiments/trust/configs/h6_shallow_policy_regime.json --output-dir results --batch-name h6_shallow_policy_regime --workers 12
python scripts/analysis/analyze.py --results results/h6_shallow_policy_regime/h6_shallow_policy_regime/results.csv --output-dir results/h6_shallow_policy_regime/h6_shallow_policy_regime/analysis
```

### 2. Partner Selection

```bash
python scripts/experiment/run.py --config experiments/trust/configs/h5_partner_selection.json --output-dir results --batch-name h5_partner_selection --workers 12
python scripts/analysis/analyze.py --results results/h5_partner_selection/h5_partner_selection/results.csv --output-dir results/h5_partner_selection/h5_partner_selection/analysis
```

### 3. Betrayal / Stance Switch

```bash
python scripts/experiment/run.py --config experiments/trust/configs/h4_betrayal_volatility.json --output-dir results --batch-name h4_betrayal_volatility --workers 12
python scripts/analysis/analyze.py --results results/h4_betrayal_volatility/h4_betrayal_volatility/results.csv --output-dir results/h4_betrayal_volatility/h4_betrayal_volatility/analysis
```

### 4. Clinical Perturbations

```bash
python scripts/experiment/run.py --config experiments/trust/configs/h7_clinical_betrayal.json --config experiments/trust/configs/h7_clinical_phenotypes.json --config experiments/trust/configs/h7_sensitivity_sweep.json --output-dir results --batch-name h7_clinical_perturbations --workers 12
python scripts/analysis/analyze.py --results results/h7_clinical_perturbations/h7_clinical_betrayal/results.csv --output-dir results/h7_clinical_perturbations/h7_clinical_betrayal/analysis
python scripts/analysis/analyze.py --results results/h7_clinical_perturbations/h7_clinical_phenotypes/results.csv --output-dir results/h7_clinical_perturbations/h7_clinical_phenotypes/analysis
python scripts/analysis/analyze.py --results results/h7_clinical_perturbations/h7_sensitivity_sweep/results.csv --output-dir results/h7_clinical_perturbations/h7_sensitivity_sweep/analysis
```

### 5. Graded Precision-Channel Tests

```bash
python scripts/experiment/run.py --config experiments/trust/configs/h6_graded_policy_regime.json --config experiments/trust/configs/h6_graded_betrayal.json --output-dir results --batch-name h6_graded_precision_channel --workers 12
python scripts/analysis/analyze.py --results results/h6_graded_precision_channel/h6_graded_policy_regime/results.csv --output-dir results/h6_graded_precision_channel/h6_graded_policy_regime/analysis
python scripts/analysis/analyze.py --results results/h6_graded_precision_channel/h6_graded_betrayal/results.csv --output-dir results/h6_graded_precision_channel/h6_graded_betrayal/analysis
```

### 6. Multi-Focal Descriptive Runs

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

## Historical Partial Runs

The detached H5 and clinical-betrayal reruns recorded in the old conductor state
stopped with `results_partial.csv` files and no final `results.csv`. They are
salvage context only until the user decides whether to rerun or explicitly
analyze them as partial historical artifacts.

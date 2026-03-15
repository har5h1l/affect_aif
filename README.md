# affect_aif

JAX-first multi-agent active inference simulations for testing whether per-partner affective precision can let shallow-planning agents approach deep-planning performance in a volatile trust game.

## Design

- `jax` is the default numerical backend for policy evaluation and batch rollouts.
- `numpy` remains available as a reference path and for easier debugging.
- The package keeps generic active inference utilities separate from the trust-game-specific rollout logic.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/run_experiment.py --config affect_aif/configs/default.json --output results/default.csv
python scripts/run_experiment.py --config affect_aif/configs/betrayal_stress.json --output results/betrayal_stress.csv
python scripts/run_analysis.py --results results/default.csv --output-dir results/figures
```

## Layout

- `affect_aif/core`: generic active inference math, control, and learning helpers
- `affect_aif/generative_model`: trust-game model, partner types, and payoffs
- `affect_aif/agent`: vanilla, affective, lesioned, and reward-average agents
- `affect_aif/environment`: multi-partner trust game environment
- `affect_aif/experiment`: configs, condition factory, logging, and runner
- `affect_aif/analysis`: metrics, statistics, and plotting
- `tests`: unit and integration coverage

## Notes

- Default experiments use exact policy enumeration when tractable.
- When the policy space explodes, the control layer can fall back to capped enumeration.
- The trust-game rollout uses context-conditioned likelihoods so reciprocators and exploiters are represented faithfully.
- `affect_aif/configs/betrayal_stress.json` is a harder scheduled-switch scenario for separating precision tracking from reward averaging.

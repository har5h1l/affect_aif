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
python scripts/run_preliminary.py --replications 5 --output results/preliminary.csv
python scripts/run_experiment.py --config affect_aif/configs/betrayal_stress.json --output results/betrayal_stress.csv
python scripts/run_analysis.py --results results/default.csv --output-dir results/figures
python scripts/run_analysis.py --results results/betrayal_stress.csv --output-dir results/betrayal_figures
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
- `scripts/run_preliminary.py` defaults to the harder `betrayal_stress` setup for a more informative directional smoke test, but accepts `--config` for other variants. It prints directional H1-H5 checks; `scripts/run_analysis.py` also saves `hypothesis_tests.json` alongside plots and summary tables.
- `scripts/run_analysis.py` auto-emits betrayal-specific outputs when switch events are present, including `betrayal_post_switch_window_1_5.csv`, `betrayal_post_switch_window_1_10.csv`, `betrayal_condition_comparison.csv`, `betrayal_detection_latency.csv`, `betrayal_trajectories.csv`, and `affective_movement_summary.csv`.
- For the betrayal workflow, inspect `betrayal_condition_comparison.csv` and `affective_movement_summary.csv` first. A useful mechanism result means Condition 2 improves post-switch payoff and/or accuracy over Condition 5 while beta and terminal-signal ranges move materially; a flat comparison plus flat movement summary is a null mechanism result, not an analysis failure.

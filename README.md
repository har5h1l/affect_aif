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
python scripts/run_experiment.py --config affect_aif/configs/default.json --output results/default.csv --verbose --make-gifs --gif-output-dir results/default_gifs
python scripts/run_preliminary.py --replications 5 --output results/preliminary.csv
python scripts/run_experiment.py --config affect_aif/configs/betrayal_stress.json --output results/betrayal_stress.csv
python scripts/run_analysis.py --results results/default.csv --output-dir results/figures
python scripts/run_analysis.py --results results/betrayal_stress.csv --output-dir results/betrayal_figures
python scripts/run_visualization.py --results results/default.csv --output-dir results/default_gifs
```

`results/` is reserved for local run outputs and analysis artifacts. The directory is kept in the repo via `results/.gitkeep`, but generated CSVs, plots, and summaries are ignored.

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
- Full runs floor `calibration_episodes` at `10` when deriving `mu`, so affective comparisons do not hinge on a `2-3` episode calibration draw.
- The trust-game rollout uses context-conditioned likelihoods so reciprocators and exploiters are represented faithfully.
- The current task is still single active agent plus scripted partners, but those partners now implement the same minimal `plan_and_act` / `observe_outcome` lifecycle as agents so the environment loop has a clean extension seam.
- `affect_aif/configs/betrayal_stress.json` is a harder scheduled-switch scenario for separating precision tracking from reward averaging.
- `scripts/run_preliminary.py` defaults to the harder `betrayal_stress` setup for a more informative directional smoke test, but accepts `--config` for other variants. It prints directional H1-H5 checks; `scripts/run_analysis.py` also saves `hypothesis_tests.json` alongside plots and summary tables.
- `scripts/run_analysis.py` auto-emits betrayal-specific outputs when switch events are present, including `betrayal_post_switch_window_1_5.csv`, `betrayal_post_switch_window_1_10.csv`, `betrayal_condition_comparison.csv`, `betrayal_detection_latency.csv`, `betrayal_trajectories.csv`, and `affective_movement_summary.csv`.
- `scripts/run_experiment.py` supports `--verbose --verbosity-mode stage_stream` for live per-round stage tracing across planning, environment stepping, belief updates, and metric logging.
- `scripts/run_experiment.py --make-gifs` generates one GIF per primary condition/seed run after saving results; `scripts/run_visualization.py` can regenerate the same GIFs later from an existing results file.
- For the betrayal workflow, inspect `betrayal_condition_comparison.csv` and `affective_movement_summary.csv` first. A useful mechanism result means Condition 2 improves post-switch payoff and/or accuracy over Condition 5 while beta and terminal-signal ranges move materially; a flat comparison plus flat movement summary is a null mechanism result, not an analysis failure.

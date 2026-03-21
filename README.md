# affect_aif

JAX-first multi-agent active inference simulations for testing whether per-partner metacognitive precision tracking provides orthogonal value beyond explicit planning depth in a volatile trust game.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

`requirements.txt` remains available for compatibility, but the supported developer workflow now uses the editable install above.

## Supported workflow

See [docs/cli.md](docs/cli.md) for the full command-line reference and [docs/results_tracking.md](docs/results_tracking.md) for the current hypothesis scorecard.

```bash
python scripts/run_experiment.py --config affect_aif/configs/default.json --config affect_aif/configs/betrayal_stress.json --output-dir results --batch-name main_run --workers 12
python scripts/run_preliminary.py --replications 5 --output results/preliminary.csv
python scripts/run_analysis.py --results results/main_run/default/results.csv --output-dir results/main_run/default/figures
python scripts/run_analysis.py --results results/main_run/betrayal_stress/results.csv --output-dir results/main_run/betrayal_stress/figures
python scripts/run_visualization.py --results results/main_run/default/results.csv --output-dir results/main_run/default/gifs
python scripts/run_model_comparison.py --results results/main_run/default/results.csv --output-dir results/main_run/default/model_comparison
```

`results/` is reserved for local run outputs and analysis artifacts. Supported runs write under `results/<batch>/<config>/`. See [results/README.md](/Users/harshilshah/Desktop/Active%20Inference/affect_aif/results/README.md) for the tracked convention.

## Layout

- `affect_aif/`: supported package code, with README files at each major layer
- `affect_aif/configs/`: supported configs for the documented workflows
- `scripts/`: supported CLI wrappers
- `archive/`: preserved exploratory scripts, configs, and the archived standalone discrete-beta prototype
- `tests/`: coverage for the supported surface

## Notes

- The supported CLI surface is intentionally small: experiment run, preliminary smoke test, analysis, visualization, and model comparison.
- Historical one-off scripts and superseded configs were moved into `archive/` instead of being deleted.
- Condition 12 now refers to the supported variational affective path. The earlier standalone discrete-beta prototype is preserved in `archive/legacy_discrete_beta/`.
- Full runs floor `calibration_episodes` at `10` when deriving `mu`, so affective comparisons do not hinge on a short calibration draw.
- The trust-game planner uses observation-branching sophisticated inference across supported conditions and horizons.

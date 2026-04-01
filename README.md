# affect_aif

Repository for the affect_aif active-inference simulation code, benchmark runners, and analysis scripts.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

`requirements.txt` remains available for compatibility, but the supported developer workflow uses the editable install above.

## Supported Workflow

See [docs/cli.md](docs/cli.md) for the command-line reference and [results/README.md](results/README.md) for the local results layout.

The supported trust-game workflow now uses the action-dependent partner redesign:
- partner behavior depends on latent `type × stance`
- stance changes are action-dependent and can also be scheduled explicitly with `scheduled_stance_switches`
- the core study matrix is Conditions `1-8` = `{tau=1,2,4,8} × {no_affect, affect}`
- lesion, reward-average, no-epistemic, variational, and clinical runs are named presets (`lesioned`, `reward_average`, `no_epistemic`, `variational_beta`, `alexithymia`, `borderline`, `depression`)

Common entry points:

```bash
python scripts/run_experiment.py --config affect_aif/configs/default.json --output-dir results --batch-name main_run --workers 12
python scripts/run_preliminary.py --replications 5 --output results/preliminary.csv
python scripts/run_analysis.py --results results/main_run/default/results.csv --output-dir results/main_run/default/figures
python scripts/run_visualization.py --results results/main_run/default/results.csv --output-dir results/main_run/default/gifs
python scripts/run_model_comparison.py --results results/main_run/default/results.csv --output-dir results/main_run/default/model_comparison
python scripts/run_benchmark.py --config affect_aif/configs/benchmark_default.json
python scripts/analyze_benchmark.py --results results/benchmark/benchmark_results.csv
```

## Repository Layout

- `affect_aif/`: shipped Python package
- `affect_aif/README.md`: package overview and public import surface
- `affect_aif/core/README.md`: core active-inference helpers
- `affect_aif/agent/README.md`: agent implementations and affect-state boundary
- `affect_aif/environment/README.md`: executable trust-game environments
- `affect_aif/experiment/README.md`: configuration, condition, and runner surface
- `affect_aif/generative_model/README.md`: trust-game generative model
- `affect_aif/analysis/README.md`: result loading, metrics, and visualization helpers
- `affect_aif/benchmark/README.md`: benchmark backends and comparison helpers
- `affect_aif/cli/README.md`: shared CLI helpers
- `affect_aif/configs/README.md`: bundled JSON configurations
- `scripts/README.md`: supported CLI wrappers
- `tests/README.md`: supported verification surface
- `archive/`: preserved exploratory scripts, configs, and legacy prototypes

## Compatibility Notes

- The main package exposes the supported runner/config entry points at the top level.
- The trust benchmark is the supported benchmark surface; the local CvC path and the scripted gridworld adapter remain separate compatibility paths.
- The discrete-beta prototype is archived; the supported affective path uses the current `affect/` helpers and the `variational_beta` preset.

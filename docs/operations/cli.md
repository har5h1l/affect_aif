# CLI Workflow Contract

Supported command-line workflows for `affect_aif`. Commands assume the repo root as the working directory and an activated virtualenv with dependencies installed (`pip install -e ".[dev]"`).

## Supported Scripts

These wrappers are the supported CLI surface:

| Script | Purpose |
|--------|---------|
| `scripts/run_experiment.py` | Run one or more experiment configs and write batch outputs. |
| `scripts/run_preliminary.py` | Run a small smoke-test experiment and print directional checks. |
| `scripts/run_analysis.py` | Generate post-hoc figures, summary tables, and betrayal artifacts. |
| `scripts/run_visualization.py` | Regenerate GIFs from saved results. |
| `scripts/run_model_comparison.py` | Compare conditions with predictive log-score summaries and RFX-BMS. |

Historical one-off scripts are not part of the supported workflow contract.

## Experiment Runner

`run_experiment.py` accepts one or more JSON configs:

```bash
python scripts/run_experiment.py --config <path-to-json> [--config <path> ...] [--output-dir DIR] [--batch-name NAME] [--workers N]
```

It calibrates `mu` when needed, runs all configured conditions, and writes one output directory per config. A single config with `--workers 1` is the serial path; all other combinations use the batch runner, but the output layout is the same.

Important flags:

| Argument | Default | Notes |
|----------|---------|-------|
| `--config` | required | Repeatable. Each path must point to a JSON config. |
| `--output-dir` | `results` | Root directory for batch outputs. |
| `--batch-name` | timestamped batch id | Subdirectory under `--output-dir`. |
| `--workers` | CPU count | Must be at least 1. |
| `--verbose` | false | Enables progress output. |
| `--verbosity-mode` | `stage_stream` | Only supported mode. |
| `--no-verbose-calibration` | false | Suppresses calibration-stage messages in serial verbose runs. |
| `--make-gifs` | false | Writes per-run GIFs after results are saved. |

Output layout:

```text
<output-dir>/<batch_name>/<config_slug>/
  results.csv
  results_partial.csv
  config.json
  batch_metadata.json
  gifs/            # only when --make-gifs is used
```

`results_partial.csv` is a checkpoint artifact and may remain after the run completes. The final experiment output written by the CLI is `results.csv`; the runner does not emit parquet files.

Examples:

```bash
# single config, timestamped batch dir
python scripts/run_experiment.py --config experiments/trust/configs/smoke.json

# single config, named batch, 12 workers
python scripts/run_experiment.py --config experiments/trust/configs/h6_shallow_policy_regime.json --output-dir results --batch-name h6_shallow_policy_regime --workers 12

# shallow regime + betrayal volatility in one batch
python scripts/run_experiment.py --config experiments/trust/configs/h6_shallow_policy_regime.json --config experiments/trust/configs/h4_betrayal_volatility.json --output-dir results --batch-name main_run --workers 12
```

## Preliminary Run

`run_preliminary.py` runs a small fixed-condition experiment and prints per-condition summaries.

```bash
python scripts/run_preliminary.py [--config <json>] [--replications N] [--rounds N] [--output <path>]
```

It always evaluates conditions 1-5, disables sensitivity runs, and writes a CSV results table at `--output`.

## Post-hoc Analysis

`run_analysis.py` consumes a saved results table and writes figures plus summary tables:

```bash
python scripts/run_analysis.py --results <path-to-csv-or-parquet> --output-dir <directory>
```

The input can be CSV or parquet. Outputs include `final_round_summary.csv`, `pairwise_payoff_tests.csv`, `hypothesis_tests.json`, `hypothesis_summary.csv`, `affective_movement_summary.csv`, `statistics_summary.txt`, and, when switch events are present, the betrayal-specific CSVs.

## Visualization and Model Comparison

`run_visualization.py` and `run_model_comparison.py` also accept CSV or parquet input tables. They write GIFs or model-comparison summaries into the directory passed via `--output-dir`.

## Configs

Supported trust experiment configs live under `experiments/trust/configs/`. Supported multi-focal configs live under `experiments/multifocal/configs/`. External benchmark and CvC configs remain under `configs/` until the benchmark package split lands. Historical paper/archive/conductor material has been salvaged into `docs/results/historical_findings.md` and is not a runnable workflow surface.

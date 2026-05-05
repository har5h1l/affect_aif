# CLI Workflow Contract

Supported command-line workflows for `affect_aif`. Commands assume the repo root as the working directory and an activated virtualenv with dependencies installed (`pip install -e ".[dev]"`).

## Supported Scripts

These scripts are the supported CLI surface:

| Script | Purpose |
|--------|---------|
| `scripts/experiment/run.py` | Run one or more experiment configs and write batch outputs. |
| `scripts/experiment/smoke.py` | Dry-run the smoke config by default, or run it with `--run`. |
| `scripts/experiment/inspect.py` | Print a compact JSON summary for an experiment config. |
| `scripts/experiment/preliminary.py` | Run a small smoke-test experiment and print directional checks. |
| `scripts/analysis/analyze.py` | Generate post-hoc figures, summary tables, and betrayal artifacts. |
| `scripts/analysis/summarize.py` | Write the final-round summary table for a saved results table. |
| `scripts/analysis/visualize.py` | Regenerate GIFs from saved results. |
| `scripts/analysis/model_comparison.py` | Compare conditions with predictive log-score summaries and RFX-BMS. |
| `scripts/analysis/targeted_reanalysis.py` | Regenerate targeted H1/H2/H4 re-analysis summaries from result CSVs. |
| `scripts/benchmark/analyze.py` | Derive shared, trust, and CvC benchmark summaries from benchmark CSVs. |
| `scripts/benchmark/run_cvc.py` | Run backend-aware benchmark comparisons, including experimental CvC. |
| `scripts/benchmark/package_cvc.py` | Write a submission-shaped local CvC policy bundle. |
| `scripts/cvc/list_missions.py` | List local CvC mission metadata. |
| `scripts/cvc/obs_diagnostic.py` | Inspect local CvC observation keys and shapes. |

Historical one-off scripts and top-level compatibility wrappers are not part of
the supported workflow contract.

## Experiment Runner

`scripts/experiment/run.py` accepts one or more JSON configs:

```bash
python scripts/experiment/run.py --config <path-to-json> [--config <path> ...] [--output-dir DIR] [--batch-name NAME] [--workers N]
```

It runs all configured conditions with the native pymdp trust runtime and writes one output directory per config. A single config with `--workers 1` is the serial path; all other combinations use the batch runner, but the output layout is the same.
With `--dry-run`, it parses configs, resolves paths, writes
`<output-dir>/<batch-name>/manifest.json`, and exits without running primary
experiments.

Important flags:

| Argument | Default | Notes |
|----------|---------|-------|
| `--config` | required | Repeatable. Each path must point to a JSON config. |
| `--output-dir` | `results` | Root directory for batch outputs. |
| `--batch-name` | timestamped batch id | Subdirectory under `--output-dir`. |
| `--workers` | CPU count | Must be at least 1. |
| `--verbose` | false | Enables progress output. |
| `--verbosity-mode` | `stage_stream` | Only supported mode. |
| `--no-verbose-calibration` | false | Legacy no-op retained for old invocations; the native runtime has no calibration stage. |
| `--make-gifs` | false | Writes per-run GIFs after results are saved. |
| `--dry-run` | false | Writes a provenance manifest without executing experiments. |

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
python scripts/experiment/run.py --config experiments/trust/configs/smoke.json

# single config, named batch, 12 workers
python scripts/experiment/run.py --config experiments/trust/configs/h6_shallow_policy_regime.json --output-dir results --batch-name h6_shallow_policy_regime --workers 12

# shallow regime + betrayal volatility in one batch
python scripts/experiment/run.py --config experiments/trust/configs/h6_shallow_policy_regime.json --config experiments/trust/configs/h4_betrayal_volatility.json --output-dir results --batch-name main_run --workers 12

# provenance-only dry run
python scripts/experiment/run.py --config experiments/trust/configs/smoke.json --output-dir results --batch-name dry_run --dry-run
```

## Preliminary Run

`scripts/experiment/preliminary.py` runs a small fixed-condition experiment and prints per-condition summaries.

```bash
python scripts/experiment/preliminary.py [--config <json>] [--replications N] [--rounds N] [--output <path>]
```

It always evaluates conditions 1-5, disables sensitivity runs, and writes a CSV results table at `--output`.

## Post-hoc Analysis

`scripts/analysis/analyze.py` consumes a saved results table and writes figures plus summary tables:

```bash
python scripts/analysis/analyze.py --results <path-to-csv-or-parquet> --output-dir <directory>
```

The input can be CSV or parquet. Outputs include `final_round_summary.csv`, `pairwise_payoff_tests.csv`, `hypothesis_tests.json`, `hypothesis_summary.csv`, `affective_movement_summary.csv`, `statistics_summary.txt`, and, when switch events are present, the betrayal-specific CSVs.

## Visualization and Model Comparison

`scripts/analysis/visualize.py` and `scripts/analysis/model_comparison.py` also accept CSV or parquet input tables. They write GIFs or model-comparison summaries into the directory passed via `--output-dir`.

## Configs

Supported trust experiment configs live under `experiments/trust/configs/`.
Supported multi-focal configs live under `experiments/multifocal/configs/`.
External benchmark configs remain under `configs/`; CvC implementation code lives
under `benchmarks/cvc/`, with shared runner code under `benchmarks/core/`.
Historical material has been salvaged into `docs/results/historical_findings.md`
and is not a runnable workflow surface.

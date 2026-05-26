# CLI Workflow Contract

Supported command-line workflows for `affect_aif`. Commands assume the repo root
as the working directory and an activated virtualenv with dependencies installed
(`pip install -e ".[dev]"`).

## Supported Scripts

| Script | Purpose |
|--------|---------|
| `scripts/experiment/run.py` | Run one or more TOML experiment specs and write batch outputs. |
| `scripts/experiment/smoke.py` | Dry-run the smoke TOML spec by default, or run it with `--run`. |
| `scripts/experiment/inspect.py` | Print a compact JSON summary for a TOML spec. |
| `scripts/experiment/preliminary.py` | Run a small smoke-test experiment. |
| `scripts/analysis/analyze.py` | Generate post-hoc figures, summary tables, and betrayal artifacts from saved results. |
| `scripts/analysis/summarize.py` | Write the final-round summary table for a saved results table. |
| `scripts/analysis/visualize.py` | Regenerate GIFs from saved results. |
| `scripts/analysis/model_comparison.py` | Compare variants with predictive log-score summaries and RFX-BMS. |
| `scripts/benchmark/analyze.py` | Derive shared and trust benchmark summaries from benchmark CSVs. |
| `scripts/benchmark/run.py` | Run trust-task benchmark comparisons. |

## Experiment Runner

`scripts/experiment/run.py` accepts one or more TOML experiment specs:

```bash
python scripts/experiment/run.py --config <path-to-toml> [--config <path> ...] [--output-dir DIR] [--batch-name NAME] [--workers N]
```

One spec defines one experiment. The runner expands:

```text
experiment x variants x sweeps x replications
```

Each expanded run is one full episode with its own seed. Result rows include
`hypothesis_id`, `experiment_id`, `variant_id`, `replication`, `seed`, and
`round`; the old numeric `condition` field is not part of the new TOML output
surface.

With `--dry-run`, the CLI parses specs, resolves paths, writes
`<output-dir>/<batch-name>/manifest.json`, and exits without running episodes.

Important flags:

| Argument | Default | Notes |
|----------|---------|-------|
| `--config` | required | Repeatable TOML experiment spec. |
| `--output-dir` | `results` | Root directory for batch outputs. |
| `--batch-name` | timestamped batch id | Subdirectory under `--output-dir`. |
| `--workers` | CPU count | Must be at least 1; use `--workers 1` for active research runs unless the user explicitly authorizes more. |
| `--verbose` | false | Enables progress output for supported serial paths. |
| `--verbosity-mode` | `stage_stream` | Only supported mode. |
| `--make-gifs` | false | Writes per-run GIFs for variant outputs after results are saved. |
| `--dry-run` | false | Writes a provenance manifest without executing experiments. |

Default TOML output layout:

```text
<output-dir>/<batch_name>/<hypothesis_id>/<experiment_id>/
  results.csv
  results_partial.csv
  checkpoint_manifest.json
  config.toml
  batch_metadata.json
  analysis/
    raw/
    figures/
    report/
```

`analysis/` is written automatically when the spec sets `analysis.auto = true`.
The standalone `scripts/analysis/analyze.py` remains available for direct
post-hoc analysis of a saved CSV or parquet file.

Experiment execution is resumable. `results_partial.csv` is updated after each
completed expanded run, and `checkpoint_manifest.json` records completed
`variant_id` × `seed` × `replication` tasks. If a run is interrupted, rerun the
same command with the same `--batch-name`; completed tasks are loaded from the
checkpoint and skipped, while missing tasks continue into the same output
directory.

Examples:

```bash
# smoke dry run
python scripts/experiment/run.py --config configs/trust/smoke/smoke.toml --output-dir results --batch-name dry_run --dry-run

# H3 betrayal stress response
python scripts/experiment/run.py --config configs/trust/hypotheses/h3_stress_response/betrayal_choice.toml --output-dir results --batch-name h3_stress_response --workers 1

# multiple H0 openness experiments in one batch
python scripts/experiment/run.py --config configs/trust/hypotheses/h0_openness/shallow_binary.toml --config configs/trust/hypotheses/h0_openness/graded_choice.toml --config configs/trust/hypotheses/h0_openness/graded_betrayal.toml --output-dir results --batch-name h0_openness --workers 1
```

## Preliminary Run

`scripts/experiment/preliminary.py` defaults to the TOML smoke spec:

```bash
python scripts/experiment/preliminary.py [--config <toml>] [--replications N] [--rounds N] [--output <path>]
```

## Post-hoc Analysis

`scripts/analysis/analyze.py` consumes a saved results table and writes figures
plus summary tables:

```bash
python scripts/analysis/analyze.py --results <path-to-csv-or-parquet> --output-dir <directory>
```

The input can be CSV or parquet. Variant-shaped results produce
`final_round_summary.csv`, `pairwise_payoff_tests.csv`,
`hypothesis_tests.json`, `hypothesis_summary.csv`,
`affective_movement_summary.csv`, `deployment_dissociation_summary.csv`,
`partner_choice_summary.csv`, `phenotype_validation_summary.csv`,
`statistics_summary.txt`, and betrayal CSVs when switch events are present.
Betrayal outputs include post-switch windows, phase splits
(`pre_switch`, `acute_post_switch`, `post_acute_tail`), detection/recovery
latencies, per-encounter trajectories, cross-partner interference summaries,
and per-partner pre/post delta summaries.

## Configs

Maintained trust experiment specs live under `configs/trust/hypotheses/`, with
smoke specs under `configs/trust/smoke/`. Benchmark-family TOML specs live
under `configs/benchmark/` and run through `scripts/benchmark/run.py`.
Supported multi-focal configs still live under `experiments/multifocal/configs/`
until the multifocal family is migrated. Shared benchmark runner code lives
under `benchmarks/core/`.

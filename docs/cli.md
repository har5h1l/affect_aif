# CLI and experiments

How to run the affect_aif experiments from the command line. All commands assume the repo root as the working directory and an activated virtualenv with dependencies installed (`pip install -r requirements.txt`).

---

## Scripts overview

| Script | Purpose |
|--------|--------|
| `scripts/run_experiment.py` | Full experiment from a JSON config; writes results CSV/parquet. |
| `scripts/run_preliminary.py` | Short run with directional H1–H5 checks; good for smoke tests. |
| `scripts/run_analysis.py` | Post-hoc analysis: figures, hypothesis tests, betrayal artifacts. |
| `scripts/run_visualization.py` | Regenerate run GIFs from an existing results file. |

---

## 1. Run experiment

Runs one or more experiment configs: all conditions per config, calibrates `mu` when needed, and saves results. With multiple configs or `--workers > 1`, runs use a process pool (parallel); with a single config and one worker, runs are serial and support live verbose output and per-run GIFs.

```bash
python scripts/run_experiment.py --config <path-to-json> [--config <path> ...] [--output-dir DIR] [--workers N]
```

### Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--config` | yes (≥1) | — | Path to a JSON config file. Pass multiple times to run several configs in one batch. |
| `--output-dir` | no | `results` | Root directory for batch output. Each run writes under `<output-dir>/<batch_id>/<config_name>/`. |
| `--batch-name` | no | `batch_YYYYMMDD_HHMMSS` | Subdirectory name under `--output-dir`. Omit for a timestamped batch id. |
| `--workers` | no | CPU count | Number of worker processes for parallel runs. Must be ≥ 1. |
| `--verbose` | no | false | In serial mode (1 config, 1 worker): print stage-by-stage progress. In batch mode: print completion messages per task. |
| `--verbosity-mode` | no | `stage_stream` | Progress format in serial mode; only `stage_stream` is supported. |
| `--no-verbose-calibration` | no | false | In serial mode, omit calibration-stage messages when `--verbose` is set. |
| `--make-gifs` | no | false | After saving results, generate one GIF per primary (condition, seed) run; in batch mode, GIFs go under each config’s `gifs/` subdir. |

### Output layout

- **Serial (exactly one `--config`, `--workers 1`)**: results to `<output-dir>/<batch_id>/<config_slug>/results.csv`. Optional GIFs to `<output-dir>/<batch_id>/<config_slug>/gifs/`.
- **Batch (multiple configs or `--workers > 1`)**: each config gets `<output-dir>/<batch_id>/<config_slug>/results.csv`, `config.json`, `batch_metadata.json`; with `--make-gifs`, GIFs under `<output-dir>/<batch_id>/<config_slug>/gifs/`.

Config slug is derived from the config filename (e.g. `default`, `betrayal_stress`).

### Parallelism

- **Worker count**: `--workers` sets the size of the shared process pool. Replications (and sensitivity runs when enabled) are distributed across workers. Use e.g. `--workers 12` to cap at 12 processes.
- **When batch mode is used**: If you pass more than one `--config`, or a single config with `--workers > 1`, the script uses `BatchExperimentRunner` and a `ProcessPoolExecutor`. Calibration runs first per config; then primary (and optionally sensitivity) replications are scheduled in parallel.
- **Serial mode**: A single config and `--workers 1` runs in the current process with full verbose and GIF options; output paths still follow the same `<output-dir>/<batch_id>/<config_name>/` layout.

### Examples

```bash
# single config, serial (1 worker), timestamped batch dir
python scripts/run_experiment.py --config affect_aif/configs/default.json

# single config, 12 workers, named batch
python scripts/run_experiment.py --config affect_aif/configs/default.json --output-dir results --batch-name primary --workers 12

# two configs in one batch, 12 workers (primary + betrayal stress)
python scripts/run_experiment.py --config affect_aif/configs/default.json --config affect_aif/configs/betrayal_stress.json --output-dir results --batch-name main_run --workers 12

# serial with verbose progress and GIFs
python scripts/run_experiment.py --config affect_aif/configs/default.json --workers 1 --verbose --make-gifs
```

After a run, the script prints where results were saved and, if calibration was used, the derived `mu` and mean |EFE| per step. With `--make-gifs` it also reports how many GIFs were written (per config in batch mode).

---

## 2. Run preliminary (smoke test)

Runs a small experiment (few replications, configurable rounds), then prints a per-condition summary and directional hypothesis checks (H1–H5). Intended for quick sanity checks; for full experiments use `run_experiment.py` with the same config.

```bash
python scripts/run_preliminary.py [--config <json>] [--replications N] [--rounds N] [--output <path>]
```

### Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--config` | no | `affect_aif/configs/betrayal_stress.json` | Path to JSON config. Use agent-choice configs (e.g. `betrayal_stress`, `variant_b`) to enable H5. |
| `--replications` | no | 5 | Replications per condition. |
| `--rounds` | no | 200 | Rounds per replication. |
| `--output` | no | `results/preliminary.csv` | Output path for the results table. |

The script always runs conditions 1, 2, 3, 4, 5 and sets `run_sensitivity = False` regardless of the config file.

### Examples

```bash
# default: betrayal_stress config, 5 replications, 200 rounds
python scripts/run_preliminary.py

# custom config and replications
python scripts/run_preliminary.py --config affect_aif/configs/default.json --replications 10 --output results/prelim.csv

# quick check with fewer rounds
python scripts/run_preliminary.py --rounds 50 --replications 3
```

---

## 3. Run analysis

Loads a results file (CSV or parquet), generates figures and summary tables, runs hypothesis tests, and writes betrayal-specific outputs when the results contain switch events.

```bash
python scripts/run_analysis.py --results <path-to-csv-or-parquet> --output-dir <directory>
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--results` | yes | Path to the results CSV or parquet from `run_experiment.py` or `run_preliminary.py`. |
| `--output-dir` | yes | Directory for all outputs (created if missing). |

### Outputs

- **Figures**: all standard plots (e.g. cumulative payoff, condition comparison) in `--output-dir`.
- **Tables**: `final_round_summary.csv`, `pairwise_payoff_tests.csv`, `hypothesis_summary.csv`, `affective_movement_summary.csv`.
- **Hypothesis tests**: `hypothesis_tests.json`.
- **Statistics summary**: `statistics_summary.txt` (ANOVA, movement summary, betrayal comparison when applicable).

If the results contain scheduled type switches (e.g. from a betrayal-stress config), the script also writes:

- `betrayal_post_switch_window_1_5.csv`, `betrayal_post_switch_window_1_10.csv`
- `betrayal_condition_comparison.csv`, `betrayal_detection_latency.csv`, `betrayal_trajectories.csv`

For interpretation of betrayal outputs and mechanism checks, see `docs/experiment.md` (H3, betrayal stress) and `docs/implementation.md` (Betrayal Stress Experiment).

### Examples

```bash
python scripts/run_analysis.py --results results/default.csv --output-dir results/figures

python scripts/run_analysis.py --results results/betrayal_stress.csv --output-dir results/betrayal_figures
```

---

## 4. Run visualization (GIFs)

Builds one GIF per primary (condition, seed) run from an existing results file. Same capability as `run_experiment.py --make-gifs` but without re-running the experiment.

```bash
python scripts/run_visualization.py --results <path-to-csv-or-parquet> --output-dir <directory>
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--results` | yes | Path to the results CSV or parquet. |
| `--output-dir` | yes | Directory where GIFs will be written. |

### Examples

```bash
python scripts/run_visualization.py --results results/default.csv --output-dir results/default_gifs
```

---

## Config files

Configs live under `affect_aif/configs/`. Key fields are documented in `affect_aif/experiment/config.py`; the following list summarizes the main experiment configs.

| Config | Description |
|--------|-------------|
| `default.json` | Primary experiment: random partner assignment, stochastic type switching, 200 rounds, 100 replications, all five conditions. |
| `betrayal_stress.json` | Betrayal stress test: agent chooses partner, no stochastic switching, one scheduled cooperator→exploiter switch; 120 rounds, 50 replications, conditions 1–3 and 5. Primary benchmark for precision vs reward-average. |
| `variant_a.json` | Fixed partner assignment (baseline variant). |
| `variant_b.json` | Agent-choice partner selection (enables H5). |
| `variant_c.json` | Noisy observations (e.g. 10% observation noise). |
| `variant_d.json` | Correlated partners (structure-learning variant). |
| `cautious_prior.json` | Alternative priors for sensitivity. |

To run a different scenario, pass the config and optional `--batch-name`; results go under `results/<batch_id>/<config_slug>/results.csv`:

```bash
python scripts/run_experiment.py --config affect_aif/configs/variant_b.json --batch-name variant_b --workers 12
```

---

## Recommended runs (from experiment plan)

From [docs/experiment.md](experiment.md): the main runs to do now are **(1) primary experiment** (Variant A, all five conditions, 100 replications) and **(2) betrayal stress** (agent-choice, scheduled cooperator→exploiter switch, primary benchmark for precision vs reward-average). Both support parallel execution with a cap of 12 workers.

**Single batch (both experiments, 12 workers max):**

```bash
python scripts/run_experiment.py \
  --config affect_aif/configs/default.json \
  --config affect_aif/configs/betrayal_stress.json \
  --output-dir results \
  --batch-name main_run \
  --workers 12
```

**Separate batches (12 workers each):**

```bash
# primary: Variant A, 100 replications, conditions 1–5
python scripts/run_experiment.py --config affect_aif/configs/default.json --output-dir results --batch-name primary --workers 12

# betrayal stress: agent-choice, scheduled switch, conditions 1–3 and 5 (includes sensitivity if enabled in config)
python scripts/run_experiment.py --config affect_aif/configs/betrayal_stress.json --output-dir results --batch-name betrayal --workers 12
```

Then run analysis on the resulting CSVs (paths depend on `--batch-name` and config slug, e.g. `results/primary/default/results.csv`, `results/betrayal/betrayal_stress/results.csv`).

---

## End-to-end workflow

1. **Quick check**
   ```bash
   python scripts/run_preliminary.py --replications 5 --output results/preliminary.csv
   ```
   Inspect the printed summary and directional H1–H5 checks.

2. **Full default experiment (parallel, 12 workers)**
   ```bash
   python scripts/run_experiment.py --config affect_aif/configs/default.json --output-dir results --batch-name primary --workers 12
   python scripts/run_analysis.py --results results/primary/default/results.csv --output-dir results/primary/figures
   ```

3. **Betrayal stress experiment (parallel, 12 workers)**
   ```bash
   python scripts/run_experiment.py --config affect_aif/configs/betrayal_stress.json --output-dir results --batch-name betrayal --workers 12
   python scripts/run_analysis.py --results results/betrayal/betrayal_stress/results.csv --output-dir results/betrayal/figures
   ```
   Then inspect `betrayal_condition_comparison.csv` and `affective_movement_summary.csv` in the figures dir.

4. **Primary + betrayal in one batch (12 workers)**
   ```bash
   python scripts/run_experiment.py --config affect_aif/configs/default.json --config affect_aif/configs/betrayal_stress.json --output-dir results --batch-name main_run --workers 12
   python scripts/run_analysis.py --results results/main_run/default/results.csv --output-dir results/main_run/default/figures
   python scripts/run_analysis.py --results results/main_run/betrayal_stress/results.csv --output-dir results/main_run/betrayal_stress/figures
   ```

5. **With GIFs (serial or batch)**
   ```bash
   python scripts/run_experiment.py --config affect_aif/configs/default.json --workers 1 --make-gifs
   ```
   GIFs go under `results/<batch_id>/default/gifs/`. Or regenerate later from saved results:
   ```bash
   python scripts/run_visualization.py --results results/<batch_id>/default/results.csv --output-dir results/<batch_id>/default/gifs
   ```

---

## Notes

- **Results directory**: `results/` is the conventional place for local outputs; it is in the repo via `results/.gitkeep`; generated files are gitignored.
- **Calibration**: Full runs enforce at least 10 calibration episodes when deriving `mu`; preliminary runs can use fewer. See `docs/implementation.md` (Terminal Values).
- **Verbose tracing**: `--verbose --verbosity-mode stage_stream` prints structured stage lines (calibration, condition, replication, round, planning, env step, belief update, metrics). Omit calibration messages with `--no-verbose-calibration`.

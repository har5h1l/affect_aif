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
# benchmark trust backend
python scripts/run_benchmark.py --config affect_aif/configs/benchmark_default.json
# benchmark analysis
python scripts/analyze_benchmark.py --results results/benchmark/benchmark_results.csv
```

`results/` is reserved for local run outputs and analysis artifacts. Supported runs write under `results/<batch>/<config>/`. See [results/README.md](/Users/harshilshah/Desktop/Active%20Inference/affect_aif/results/README.md) for the tracked convention.

## Layout

- `affect_aif/core`: generic active inference math, control, and learning helpers
- `affect_aif/generative_model`: trust-game model, partner types, and payoffs
- `affect_aif/agent`: vanilla, affective, lesioned, and reward-average agents
- `affect_aif/environment`: multi-partner trust game environment
- `affect_aif/experiment`: configs, condition factory, logging, and runner
- `affect_aif/analysis`: metrics, statistics, and plotting
- `affect_aif/benchmark`: backend-aware benchmark runners, baselines, and CvC integration helpers
- `affect_aif/configs/`: supported configs for the documented workflows
- `scripts/`: supported CLI wrappers
- `archive/`: preserved exploratory scripts, configs, and the archived standalone discrete-beta prototype
- `tests`: unit and integration coverage

## Notes

- Default experiments use exact policy enumeration when tractable.
- Benchmarks now run through explicit backends. `trust` is the canonical benchmark for current AIF claims; `cvc_local` is the real CoGames/CvC path and requires Python 3.12 for `cogames`.
- Trust-game policy evaluation now uses observation-branching sophisticated inference rather than a mean-field rollout approximation.
- When the policy space explodes, the control layer can fall back to capped enumeration.
- Full runs floor `calibration_episodes` at `10` when deriving `mu`, so affective comparisons do not hinge on a `2-3` episode calibration draw.
- Default affect settings are `lambda_smooth=0.6`, `alpha_charge=3.0`, `sigma_0_sq=0.25`, which keeps beta slower than belief updates without leaving it effectively frozen.
- The trust-game rollout uses context-conditioned likelihoods so reciprocators and exploiters are represented faithfully.
- Affective and reward-average shallow agents weight shallow-horizon EFE by the first partner's signal rather than appending an additive terminal scalar, so condition differences survive first-action marginalization.
- The current task is still single active agent plus scripted partners, but those partners now implement the same minimal `plan_and_act` / `observe_outcome` lifecycle as agents so the environment loop has a clean extension seam.
- `affect_aif/configs/betrayal_stress.json` is a harder scheduled-switch scenario for separating precision tracking from reward averaging.
- `affect_aif/configs/horizon_sweep.json` adds intermediate no-affect horizons (Conditions 6 and 7) so analysis can place the affective shallow agent on an explicit depth curve.
- `affect_aif/configs/deep_affect_test.json` is the completed Conditions 1, 2, and 8 comparison, and it confirmed that affect adds the same payoff lift at deep and shallow horizons in the shipped task.
- `affect_aif/configs/variant_d.json` is the archived correlated-partner follow-up run; it remained a null on H3, but the active H3 read is now driven by the default-null versus betrayal-positive contrast.
- Condition 12 now refers to the supported variational affective path. The earlier standalone discrete-beta prototype is preserved in `archive/legacy_discrete_beta/`.
- `scripts/run_preliminary.py` defaults to the harder `betrayal_stress` setup for a more informative directional smoke test, but accepts `--config` for other variants. It prints directional H1-H5 checks; `scripts/run_analysis.py` also saves `hypothesis_tests.json` alongside plots and summary tables.
- `scripts/run_analysis.py` auto-emits betrayal-specific outputs when switch events are present, including `betrayal_post_switch_window_1_5.csv`, `betrayal_post_switch_window_1_10.csv`, `betrayal_condition_comparison.csv`, `betrayal_detection_latency.csv`, `betrayal_trajectories.csv`, and `affective_movement_summary.csv`.
- `scripts/run_experiment.py` supports multiple `--config` paths and `--workers` for parallel runs; with one config and `--workers 1`, `--verbose --verbosity-mode stage_stream` gives live per-round tracing; `--make-gifs` generates one GIF per primary condition/seed run after saving results; `scripts/run_visualization.py` can regenerate GIFs from an existing results file.
- For the betrayal workflow, inspect `betrayal_condition_comparison.csv` and `affective_movement_summary.csv` first. A useful mechanism result means Condition 2 improves post-switch payoff and/or accuracy over Condition 5 while beta and terminal-signal ranges move materially; a flat comparison plus flat movement summary is a null mechanism result, not an analysis failure.

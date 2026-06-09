# Paper Result Provenance

Tracked paper result folders under `results/paper/` contain compact summaries,
manifests, and source-table style metrics. Full raw trajectories are preserved
outside git under matching `raw/` paths locally and on `server`.

Every paper manifest should point to current `configs/paper/` TOML files and
use `raw_results_policy = "gitignored_retained_locally_and_on_server"`.

## Paper Result Cards

| Folder | Config | Raw path | Tracked public files | Interpretation boundary |
|---|---|---|---|---|
| `results/paper/model_fitness/` | `configs/paper/h1_model_fitness/reliability_vs_reward_confirm.toml` | `results/paper/model_fitness/raw/h1/reliability_vs_reward_confirm/results.csv` | `summary.csv`, `manifest.json`, README | H1 model-fitness tracking; not a reward-improvement claim. |
| `results/paper/betrayal_adaptation/` | `configs/paper/h5_betrayal/betrayal_reallocation_confirm.toml` | `results/paper/betrayal_adaptation/raw/h5/betrayal_reallocation_confirm/results.csv` | `summary.csv`, `manifest.json`, README | H5 lower entropy and higher joint accuracy; payoff advantage uncertain. |
| `results/paper/alpha_sweep/` | `configs/paper/alpha_sweep.toml` | `results/paper/alpha_sweep/raw/results.csv` | `metrics.csv`, `manifest.json`, README | Precision-gain profile readout across open and betrayal settings. |
| `results/paper/prior_factorial/` | `configs/paper/prior_factorial.toml` | `results/paper/prior_factorial/raw/results.csv` | `metrics.csv`, `manifest.json`, README | Beta prior x gain profile readout. |
| `results/paper/forgiveness/` | `configs/paper/forgiveness.toml` | `results/paper/forgiveness/raw/results.csv` | `metrics.csv`, `manifest.json`, README | Trust-repair profile readout; reengagement and confidence restoration can dissociate. |
| `results/paper/mixed_volatility/` | `configs/paper/mixed_volatility.toml` | `results/paper/mixed_volatility/raw/results.csv` | `metrics.csv`, `manifest.json`, README | Mixed-volatility boundary condition for payoff/calibration tradeoffs. |

The paper-facing prose and exact manuscript numbers are maintained in
`docs/manuscript/results_digest.md`, `docs/manuscript/source_tables/`, and
`docs/results/current.md`.

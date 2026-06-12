# Paper Result Provenance

Tracked paper result folders under `results/paper/` contain compact summaries,
manifests, and source-table style metrics. Full raw trajectories are preserved
outside git under matching `raw/` paths and in the Drive packet.

Every paper manifest should point to current `configs/paper/` TOML files and
use `raw_results_policy = "gitignored_retained_outside_git_and_in_drive"`.

## Paper Result Cards

| Folder | Config | Raw path | Tracked public files | Interpretation boundary |
|---|---|---|---|---|
| `results/paper/01_predictability_value/` | `configs/paper/01_predictability_value.toml` | `results/paper/01_predictability_value/raw/results.csv` | `source_tables/*.csv`, `manifest.json`, README | Precision tracks predictability more than realized value; payoff is not the primary gate. |
| `results/paper/02_deployment_ablation/` | `configs/paper/02_deployment_ablation.toml` | `results/paper/02_deployment_ablation/raw/results.csv` | `source_tables/*.csv`, `manifest.json`, README | Tracked-only preserves beta movement while full affect lowers entropy; behavior changes through beta-to-gamma deployment. |
| `results/paper/03_partner_selection/` | `configs/paper/03_partner_selection.toml` | `results/paper/03_partner_selection/raw/results.csv` | `source_tables/*.csv`, `manifest.json`, README | Graded partner selection sharpens directionally without a payoff headline. |
| `results/paper/04_betrayal_adaptation/` | `configs/paper/04_betrayal_adaptation.toml` | `results/paper/04_betrayal_adaptation/raw/results.csv` | `source_tables/*.csv`, `manifest.json`, README | H5 lower entropy and higher joint accuracy; payoff advantage uncertain. |
| `results/paper/05a_alpha_sweep/` | `configs/paper/05a_alpha_sweep.toml` | `results/paper/05a_alpha_sweep/raw/results.csv` | `metrics.csv`, `manifest.json`, README | Precision-gain profile readout across open and betrayal settings. |
| `results/paper/05b_prior_factorial/` | `configs/paper/05b_prior_factorial.toml` | `results/paper/05b_prior_factorial/raw/results.csv` | `metrics.csv`, `manifest.json`, README | Beta prior x gain profile readout. |
| `results/paper/05c_forgiveness/` | `configs/paper/05c_forgiveness.toml` | `results/paper/05c_forgiveness/raw/results.csv` | `metrics.csv`, `manifest.json`, README | Trust-repair profile readout; reengagement and confidence restoration can dissociate. |

The paper-facing prose and exact manuscript numbers are maintained in
`docs/results/current.md` and `docs/manuscript/source_tables/`. The figure and
source-table map lives in `docs/results/provenance.md`. The suite-level map
lives in `results/paper/manifest.json`.

The binary H4 partner-choice confirmation belongs to
`results/diagnostics/social_allocation/` and is not a paper result card.

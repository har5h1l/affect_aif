# Paper Result Provenance

Tracked paper result folders under `results/paper/` contain compact summaries,
manifests, and source-table style metrics. Full raw trajectories are preserved
outside git under matching `raw/` paths and in the public data packet (see root
`README.md`).

All current cards use the shared-action architecture and linear affective
charge.

Every paper manifest should point to current `configs/paper/` TOML files and
use `raw_results_policy = "gitignored_retained_outside_git_and_in_drive"`.

## Paper Result Cards

| Folder | Config | Raw path | Tracked public files | Interpretation boundary |
|---|---|---|---|---|
| `results/paper/01_predictability_value/` | `configs/paper/01_predictability_value.toml` | `results/paper/01_predictability_value/raw/results.csv` | `source_tables/*.csv`, `manifest.json`, README | Precision remains more strongly associated with relationship-specific predictability than realized payoff; because surprisal drives the tracker, this verifies intended selectivity rather than independently validating it. |
| `results/paper/02_deployment_ablation/` | `configs/paper/02_deployment_ablation.toml` | `results/paper/02_deployment_ablation/raw/results.csv` | `source_tables/*.csv`, `manifest.json`, README | Tracked-only preserves beta movement while full affect produces substantially lower policy entropy, localizing policy sharpening to beta-to-gamma deployment; payoff is secondary and regime-dependent. |
| `results/paper/03_partner_selection/` | `configs/paper/03_partner_selection.toml` | `results/paper/03_partner_selection/raw/results.csv` | `source_tables/*.csv`, `manifest.json`, README | Partner-local precision sharpens commitment over partner--investment policies; selected partner types remain broadly distributed and do not support a stable type-specific preference. |
| `results/paper/04_betrayal_adaptation/` | `configs/paper/04_betrayal_adaptation.toml` | `results/paper/04_betrayal_adaptation/raw/results.csv` | `source_tables/*.csv`, `manifest.json`, README | Partner-local precision maintains substantially lower policy entropy after abrupt change; joint type--stance accuracy and payoff differ downstream of altered engagement and remain regime-specific outcomes. |
| `results/paper/05a_alpha_sweep/` | `configs/paper/05a_alpha_sweep.toml` | `results/paper/05a_alpha_sweep/raw/open_graded/results.csv`; `raw/betrayal/results.csv` | `metrics.csv`, `manifest.json`, README | Precision gain controls confidence-revision amplitude monotonically but not payoff monotonically. |
| `results/paper/05b_prior_factorial/` | `configs/paper/05b_prior_factorial.toml` | `results/paper/05b_prior_factorial/raw/open_graded/results.csv`; `raw/betrayal/results.csv`; `raw/partner_choice/results.csv` | `metrics.csv`, `manifest.json`, README | Prior and gain produce distinct computational trust-calibration profiles; detailed payoff rankings are condition-specific. |
| `results/paper/05c_forgiveness/` | `configs/paper/05c_forgiveness.toml` | `results/paper/05c_forgiveness/raw/results.csv` | `metrics.csv`, `manifest.json`, README | Reengagement, confidence recovery, and payoff recovery are analyzed as separable trust-repair readouts. |

The paper-facing prose and exact manuscript numbers are maintained in
`docs/results/current.md` and `docs/manuscript/source_tables/`. The figure and
source-table map lives in `docs/results/provenance.md`. The suite-level map
lives in `results/paper/manifest.json`.

The binary H4 partner-choice confirmation belongs to
`results/diagnostics/social_allocation/` and is not a paper result card.

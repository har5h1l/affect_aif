# Result Provenance

This file maps current paper results to manuscript source tables and figures.
Use it with `docs/results/current.md` for interpreted numbers. Do not replace a
manuscript number from raw output unless the corresponding source table and
interpreted result note are refreshed together.

## Run Code Provenance

The canonical linear batch (`linear_charge_20260812`) was launched from base
commit `6b7d88946c4e7a2a55ebe8b200d3154fa09aebe6` with a modified worktree that
added the selectable linear charge transform. The server archive preserves the
run log, resolved configurations, batch metadata, checkpoints, and row-level
results, but not a separate snapshot of that uncommitted worktree. Commit
`fbf92ed659f1eb9582c0d59650503b27f8855c03`, created after the run, is the
first commit containing that selectable linear runtime. Commit
`f91fadb2a33b65cbf8cf11e39e032de0b2830d4b` makes the same linear contract the
default and is the canonical reproduction implementation. Result manifests
record these roles separately rather than attributing the linear batch to the
unchanged base commit.

## Figure Source Map

| Manuscript figure | Figure asset | Manuscript source table(s) | Canonical result source | Builder |
|---|---|---|---|---|
| Figure 1: predictability over payoff | `docs/manuscript/figures/fig_model_fitness_beta_reward_divergence.pdf` | `docs/manuscript/source_tables/h1_model_fitness_confirm/model_fitness_correlation_summary.csv`; `docs/manuscript/source_tables/h1_model_fitness_confirm/final_round_summary.csv` | `results/paper/01_predictability_value/raw/results.csv`; matching tracked tables under `results/paper/01_predictability_value/source_tables/` | `scripts/analysis/make_paper_figures.py --refresh-source-tables` |
| Figure 2: deployment pathway | `docs/manuscript/figures/fig_deployment_social_summary.pdf` | `docs/manuscript/source_tables/h2_deployment_pathway_summary.csv` | `results/paper/02_deployment_ablation/raw/results.csv`; tracked copy `results/paper/02_deployment_ablation/source_tables/deployment_contrast_summary.csv` | `scripts/analysis/make_paper_figures.py --refresh-source-tables` |
| Figure 3: betrayal boundary | `docs/manuscript/figures/fig_betrayal_boundary_summary.pdf` | `docs/manuscript/source_tables/h5_betrayal_timecourse_summary.csv`; paired headline table `docs/manuscript/source_tables/h5_evidence_effect_summary.csv` | `results/paper/04_betrayal_adaptation/raw/results.csv`; tracked effect table `results/paper/04_betrayal_adaptation/source_tables/h5_evidence_effect_summary.csv` | `scripts/analysis/make_paper_figures.py --refresh-source-tables` |
| Appendix Figure: alpha sweep | `docs/manuscript/figures/fig_alpha_sweep.pdf` | `docs/manuscript/source_tables/alpha_sweep/metrics.csv` | `results/paper/05a_alpha_sweep/metrics.csv`; raw audit root `results/paper/05a_alpha_sweep/raw/` contains `open_graded/results.csv` and `betrayal/results.csv` for fresh canonical runs | `scripts/analysis/phenotype_artifacts.py alpha_sweep --results-root results/paper/05a_alpha_sweep/raw` |
| Appendix Figure: gain-prior profiles | `docs/manuscript/figures/fig_phenotype_quadrants.pdf` | `docs/manuscript/source_tables/prior_factorial/metrics.csv` | `results/paper/05b_prior_factorial/metrics.csv`; raw audit root `results/paper/05b_prior_factorial/raw/` contains `open_graded/results.csv`, `betrayal/results.csv`, and `partner_choice/results.csv` for fresh canonical runs | `scripts/analysis/phenotype_artifacts.py prior_factorial --results-root results/paper/05b_prior_factorial/raw` |
| Appendix Figure: forgiveness | `docs/manuscript/figures/fig_forgiveness.pdf` | `docs/manuscript/source_tables/forgiveness/metrics.csv` | `results/paper/05c_forgiveness/metrics.csv`; raw audit path `results/paper/05c_forgiveness/raw/results.csv` | `scripts/analysis/phenotype_artifacts.py forgiveness --results-root results/paper/05c_forgiveness/raw` |

## Text-Only Result Sources

| Manuscript readout | Source table | Canonical result source |
|---|---|---|
| Partner-choice entropy and descriptive type-selection intervals | `docs/manuscript/source_tables/h4_partner_choice_summary.csv` | `results/paper/03_partner_selection/raw/results.csv`; paired tracked table `results/paper/03_partner_selection/source_tables/partner_selection_summary.csv`; type-specific intervals all include zero and do not support a stable allocation preference |
| Betrayal headline entropy, joint type-stance accuracy, and payoff intervals | `docs/manuscript/source_tables/h5_evidence_effect_summary.csv` | `results/paper/04_betrayal_adaptation/source_tables/h5_evidence_effect_summary.csv` |
| Appendix profile tables | `docs/manuscript/source_tables/alpha_sweep/metrics.csv`; `docs/manuscript/source_tables/prior_factorial/metrics.csv`; `docs/manuscript/source_tables/forgiveness/metrics.csv` | `results/paper/05a_alpha_sweep/metrics.csv`; `results/paper/05b_prior_factorial/metrics.csv`; `results/paper/05c_forgiveness/metrics.csv` |

## Excluded From Paper Evidence

- Binary H1 model-fitness confirmation:
  `results/diagnostics/model_fitness/raw/h1/reliability_vs_reward_confirm/`.
- Binary H4 partner-choice confirmation:
  `results/diagnostics/social_allocation/raw/partner_choice_confirm_20260609/`.
- Mixed-volatility outputs under `results/future/`.
- Incomplete and dry-run outputs.

## Statistical Contract

- Mean intervals resample simulation-seed means 10,000 times with bootstrap seed 0.
- Treatment-control intervals resample paired seed differences.
- H1 partial-correlation intervals resample whole seed clusters.
- Figure refresh validates linear/none charge provenance, 1,296 policies per
  partner, 5,184 combined candidates, and the 8.553-nat entropy ceiling before
  writing any paper table or figure.

# Paper Reproduction

Paper configs live under `configs/paper/`.

```bash
python scripts/experiment/run.py \
  --config configs/paper/01_predictability_value.toml \
  --config configs/paper/02_deployment_ablation.toml \
  --config configs/paper/03_partner_selection.toml \
  --config configs/paper/04_betrayal_adaptation.toml \
  --config configs/paper/05a_alpha_sweep.toml \
  --config configs/paper/05b_prior_factorial.toml \
  --config configs/paper/05c_forgiveness.toml \
  --batch-name paper \
  --workers 1 \
  --dry-run
```

Remove `--dry-run` to run the full suite. These runs are intentionally larger
than the demos; keep `--workers 1` unless parallel local execution is intended.

Compact public summaries and manifests are tracked under `results/paper/`.
Raw trajectories are gitignored but retained locally and on `server`.

## Paper Suite Map

| Paper section | Config | Result folder | Summary files |
|---|---|---|---|
| 3.1 predictability over value | `configs/paper/01_predictability_value.toml` | `results/paper/01_predictability_value/` | `source_tables/*.csv`, `manifest.json` |
| 3.2 deployment ablation | `configs/paper/02_deployment_ablation.toml` | `results/paper/02_deployment_ablation/` | `source_tables/*.csv`, `manifest.json` |
| 3.3 partner selection | `configs/paper/03_partner_selection.toml` | `results/paper/03_partner_selection/` | `source_tables/*.csv`, `manifest.json` |
| 3.4 betrayal adaptation | `configs/paper/04_betrayal_adaptation.toml` | `results/paper/04_betrayal_adaptation/` | `summary.csv`, `source_tables/*.csv`, `manifest.json` |
| 3.5 / Appendix D precision-gain profiles | `configs/paper/05a_alpha_sweep.toml` | `results/paper/05a_alpha_sweep/` | `metrics.csv`, `manifest.json` |
| 3.5 / Appendix D prior x gain profiles | `configs/paper/05b_prior_factorial.toml` | `results/paper/05b_prior_factorial/` | `metrics.csv`, `manifest.json` |
| 3.5 / Appendix D forgiveness / trust repair | `configs/paper/05c_forgiveness.toml` | `results/paper/05c_forgiveness/` | `metrics.csv`, `manifest.json` |

The exact manuscript source tables and final paper figures live under
`docs/manuscript/source_tables/` and `docs/manuscript/figures/`.

## Analysis Route

For Sections 3.1--3.4, each config `[analysis]` block names the primary
analysis contract used by `run.py`. For the profile suite, raw trajectories are
converted into compact profile metrics and manuscript figures with:

```bash
python scripts/analysis/phenotype_artifacts.py --help
python scripts/analysis/make_paper_figures.py --help
```

Use `results/paper/manifest.json` and `docs/results/paper.md` for the
paper-card interpretation boundary. Reviewer-only controls remain under
`configs/diagnostics/`; the heterogeneous-volatility follow-up remains under
`configs/future/` and `results/future/`.

The binary H4 partner-choice confirmation is a diagnostics surface under
`configs/diagnostics/h4_social_allocation/partner_choice_confirm.toml` and
`results/diagnostics/social_allocation/`. It is not part of the paper suite;
paper Section 3.3 uses the graded `03_partner_selection` config.

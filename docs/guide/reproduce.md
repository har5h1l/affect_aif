# Reproduce The Public Results

Start with the demo if you
want to verify installation quickly; use the paper suite when you want the full
set of paper experiments.

Start with:

- `docs/guide/running.md` for the runner and output layout.
- `docs/guide/notebooks.md` for notebook choices.
- `notebooks/demo.ipynb` for a small run-and-analyze notebook.
- `notebooks/reproduce.ipynb` for the full reproduction notebook.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Smoke Dry-Run

```bash
python scripts/experiment/run.py \
  --config configs/diagnostics/smoke/trust_smoke.toml \
  --dry-run
```

## Demo Run

```bash
python scripts/experiment/run.py \
  --config configs/demo/01_predictability_value.toml \
  --workers 1
```

The demo notebook defaults to the four core demos: 21 expanded runs total. Its
route-control cell can opt into the appendix/profile demos, bringing the full
demo route to 42 expanded runs.

## Paper Dry-Run

```bash
python scripts/experiment/run.py \
  --config configs/paper/01_predictability_value.toml \
  --config configs/paper/02_deployment_ablation.toml \
  --config configs/paper/03_partner_selection.toml \
  --config configs/paper/04_betrayal_adaptation.toml \
  --config configs/paper/05a_alpha_sweep.toml \
  --config configs/paper/05b_prior_factorial.toml \
  --config configs/paper/05c_forgiveness.toml \
  --workers 1 \
  --dry-run
```

Remove `--dry-run` for the full paper execution. The full paper suite is 1220
expanded runs, so it is much larger than the demo notebook route; use
`--workers 1` unless you intentionally want local parallel execution.

Full per-round `results.csv` files are gitignored and retained outside git.
Compact public summaries and manifests live under `results/paper/` and
`results/diagnostics/`. Additional checks and comparisons are available under `configs/diagnostics/`; implemented
exploratory experiments live under `configs/future/`.

## Use The Published Results Without Rerunning

Download [paper_results.zip](../../paper_results.zip) and its
[SHA-256 checksum](../../paper_results.zip.sha256), both in the repository root.

You can inspect the ZIP directly. To use its raw files with the analysis scripts,
extract it into a separate checkout if you already have local results to keep.
From that checkout's root:

```bash
shasum -a 256 -c paper_results.zip.sha256
python -m zipfile -e paper_results.zip .
```

Read [Findings](../results/findings.md) for the paper's conclusions and
[Provenance](../results/provenance.md) to locate each figure's inputs.
No simulation run is needed to inspect or analyze the published trajectories.

## Colab Route

Open `notebooks/demo.ipynb` or `notebooks/reproduce.ipynb` in Google Colab,
clone the repo in the first setup cell, and run cells top to bottom. The
demo notebook starts with the 21-run core route and keeps appendix/profile
demos opt-in. The notebooks write scratch outputs under `outputs/` before
copying paper runs into `results/paper/`.

## Manuscript Build

`docs/manuscript/main.tex` is the single authoritative LNCS source, including
macros, author details, main text, and appendices. Edit it directly; no
flattening step is needed. The bibliography remains in `references.bib`, figures
in `figures/`, and supporting compact CSVs in `source_tables/`.

With a LaTeX installation providing the LNCS class and `splncs04` bibliography
style, run from the repository root:

```bash
cd docs/manuscript
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

The output is `docs/manuscript/main.pdf`. Check the build log for unresolved
citations and references, then inspect the PDF's layout and page count.
Rebuilding the manuscript does not rerun experiments or regenerate figures.
For figure regeneration and the source-table map, see
[Result Provenance](../results/provenance.md). For supported claims, use
[Current Results](../results/findings.md).

## Paper Suite Map

| Paper section | Config | Result folder | Summary files |
|---|---|---|---|
| 3.1 predictability over value | `configs/paper/01_predictability_value.toml` | `results/paper/01_predictability_value/` | `source_tables/*.csv`, `manifest.json` |
| 3.2 deployment ablation | `configs/paper/02_deployment_ablation.toml` | `results/paper/02_deployment_ablation/` | `source_tables/*.csv`, `manifest.json` |
| 3.3 partner selection | `configs/paper/03_partner_selection.toml` | `results/paper/03_partner_selection/` | `source_tables/*.csv`, `manifest.json` |
| 3.4 betrayal adaptation | `configs/paper/04_betrayal_adaptation.toml` | `results/paper/04_betrayal_adaptation/` | `summary.csv`, `source_tables/*.csv`, `manifest.json` |
| 3.5 / Appendix 5 precision-gain profiles | `configs/paper/05a_alpha_sweep.toml` | `results/paper/05a_alpha_sweep/` | `metrics.csv`, `manifest.json` |
| 3.5 / Appendix 5 prior x gain profiles | `configs/paper/05b_prior_factorial.toml` | `results/paper/05b_prior_factorial/` | `metrics.csv`, `manifest.json` |
| 3.5 / Appendix 5 forgiveness / trust repair | `configs/paper/05c_forgiveness.toml` | `results/paper/05c_forgiveness/` | `metrics.csv`, `manifest.json` |

The exact manuscript source tables and final paper figures live under
`docs/manuscript/source_tables/` and `docs/manuscript/figures/`.

## Analysis Route

For Sections 3.1--3.4, each config `[analysis]` block names the primary
analysis settings used by `run.py`. For the profile suite, raw trajectories are
converted into compact profile metrics and manuscript figures with:

```bash
python scripts/analysis/phenotype_artifacts.py --help
python scripts/analysis/make_paper_figures.py --help
```

Use `results/paper/manifest.json` and `docs/results/findings.md` for the
experiment descriptions. Additional controls remain under
`configs/diagnostics/`; the heterogeneous-volatility follow-up remains under
`configs/future/` and `results/future/`.

The binary H4 partner-choice confirmation is an additional diagnostic experiment under
`configs/diagnostics/h4_social_allocation/partner_choice_confirm.toml` and
`results/diagnostics/social_allocation/`. It is not part of the paper suite;
paper Section 3.3 uses the graded `03_partner_selection` config.

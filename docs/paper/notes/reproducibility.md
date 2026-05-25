# Supplement: Reproducibility

## Environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Core runtime dependency:

```text
inferactively-pymdp==1.0.0
```

See `pyproject.toml` for the full dependency list.

## Verification Gate

Run before generating or refreshing evidence:

```bash
python -m pytest tests/ -q
python -m ruff check .
python -m mypy
git diff --check
```

## Running Experiments

The maintained trust specs live under `configs/trust/hypotheses/`. Batch output
layout:

```text
results/<batch_name>/<hypothesis_id>/<experiment_id>/
  results.csv
  results_partial.csv
  checkpoint_manifest.json
  config.toml
  batch_metadata.json
  analysis/
```

Example:

```bash
python scripts/experiment/run.py --config configs/trust/hypotheses/h3_stress_response/betrayal_choice.toml --output-dir results --batch-name h3_stress_response --workers 1
```

## Analyzing Results

```bash
python scripts/analysis/analyze.py --results <path>/results.csv --output-dir <path>/analysis
```

Stable output tables include:

- `final_round_summary.csv`
- `pairwise_payoff_tests.csv`
- `hypothesis_tests.json`
- `hypothesis_summary.csv`
- `affective_movement_summary.csv`
- `deployment_dissociation_summary.csv`
- `partner_choice_summary.csv`
- `phenotype_validation_summary.csv`
- `evidence_effect_summary.csv`
- betrayal summaries when scheduled switch events are present

## Paper Artifacts

Use `docs/paper/figures_tables.md` to map paper figures and tables to analysis
artifacts. Avoid regenerating figures from partial or legacy result directories.

## Current Verification Snapshot

The documentation cleanup and analysis-code fixes were checked with:

```text
python -m pytest tests/ -q -> 343 passed, 7 skipped
python -m ruff check . -> pass
python -m mypy -> pass
git diff --check -> pass
```

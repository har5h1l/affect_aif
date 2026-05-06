# Results Directory

`results/` is reserved for local experiment outputs and analysis artifacts from the supported CLI workflows.

Supported experiment runs write batch outputs under:

```text
results/<card_root>/<config_slug>/
```

Use card roots such as `h0_openness_gate`, `h1_model_fitness`,
`h2_deployment`, `h3_stress_response`, `h4_social_choice`, and
`h5_perturbation_phenotypes`.

Typical experiment outputs include:

- `results.csv`
- `results_partial.csv`
- `config.json`
- `batch_metadata.json`
- `gifs/` when `--make-gifs` is used

The supported experiment CLI writes CSV results. Downstream analysis commands may read CSV or parquet, but parquet is not emitted by `scripts/experiment/run.py` or `scripts/experiment/preliminary.py`.

This repository tracks only scaffolding for the directory. Generated outputs remain untracked.

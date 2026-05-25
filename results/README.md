# Results Directory

`results/` is reserved for local experiment outputs and analysis artifacts from the supported CLI workflows.

Generated outputs follow the experiment config envelope. Do not create
`results/paper/`; paper-facing interpretation belongs in `docs/paper/` and
`docs/results/`.

Supported experiment runs write batch outputs under:

```text
results/<batch_name>/<hypothesis_id>/<experiment_id>/
```

Use descriptive batch names such as `updated_h0_h5_20260517_w2`,
`confirm_h0_h1_h2_h4_20260518`, or
`h3_precision_sensitivity_20260522`.

Current promoted or follow-up batches:

- `updated_h0_h5_20260517_w2/`: May 18 promoted H0-H5 artifacts for H0-H4 and
  most H5 experiments.
- `updated_h0_h5_20260518_remainder/`: May 18 H5 affect-sensitivity
  remainder.
- `confirm_h0_h1_h2_h4_20260518/`: latest H0/H1/H2/H4 confirmation artifacts.
- `confirm_h1_h3_split_20260519/`: targeted 30-seed H1/H3 confirmation.
- `h3_precision_sensitivity_20260522/`: H3 abrupt/gradual precision-sensitivity
  follow-up.
- `h3_reallocation_followup_20260519/`: small H3 split-readout pilot retained
  as exploratory context.

Typical experiment outputs include:

- `results.csv`
- `results_partial.csv`
- `config.toml`
- `batch_metadata.json`
- `checkpoint_manifest.json`
- `gifs/` when `--make-gifs` is used

Local cleanup policy: keep current/provenance-bearing batches and remove
superseded pilot, incomplete, or detached local outputs after their findings are
either documented or intentionally discarded. Generated outputs remain
untracked.

The supported experiment CLI writes CSV results. Downstream analysis commands may read CSV or parquet, but parquet is not emitted by `scripts/experiment/run.py` or `scripts/experiment/preliminary.py`.

This repository tracks only scaffolding for the directory.

# Results Directory

`results/` is reserved for local experiment outputs and analysis artifacts from the supported CLI workflows.

Supported experiment runs write batch outputs under:

```text
results/<batch_name>/<hypothesis_id>/<experiment_id>/
```

Use descriptive batch names such as `updated_h0_h5_20260517_w2`,
`confirm_h0_h1_h2_h4_20260518`, or
`h3_reallocation_followup_20260519`.

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

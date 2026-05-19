# Results Directory

`results/` is reserved for local experiment outputs and analysis artifacts from the supported CLI workflows.

Active local evidence copies are kept at top level. Older pilots and partial
attempts are moved under `results/archive/` so the visible surface contains only
the latest promoted or follow-up batches per hypothesis family.

Current top-level batches:

- `updated_h0_h5_20260517_w2/`: May 18 promoted H0-H5 analysis artifacts for
  H0-H4 and most H5 experiments
- `updated_h0_h5_20260518_remainder/`: May 18 promoted H5 affect-sensitivity
  remainder
- `h3_reallocation_followup_20260519/`: small May 19 H3 split-readout pilot

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

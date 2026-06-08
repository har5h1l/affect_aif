# Paper Result Provenance

Tracked paper result folders under `results/paper/` contain compact summaries,
manifests, and source-table style metrics. Full raw trajectories are preserved
outside git under matching `raw/` paths locally and on `server`.

Every paper manifest should point to current `configs/paper/` TOML files and
use `raw_results_policy = "gitignored_retained_locally_and_on_server"`.

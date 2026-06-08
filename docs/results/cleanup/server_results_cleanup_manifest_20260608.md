# Server Results Cleanup Manifest - 2026-06-08

This manifest records the cleanup applied to
`/Users/server/repos/affect_aif/results/` on 2026-06-08. It documents file
organization only; it does not reinterpret results.

## Preflight

- Mango process registry: no watched processes.
- Remote tmux: no sessions.
- Remote process scan: no active `affect_aif` experiment or analysis process
  outside the inspection command itself.
- Server git state before cleanup: `master...origin/master` with untracked
  `docs/manuscript/figures/fig_forgiveness.pdf` and
  `docs/manuscript/source_tables/exp_c_forgiveness/metrics.csv`.

## Final Top-Level Layout

- `results/paper/`
- `results/diagnostics/`
- `results/archive/`

No top-level historical experiment directories remain on the server.

## Paper Raw Runs

- `results/paper/model_fitness/raw/`
- `results/paper/betrayal_adaptation/raw/`
- `results/paper/alpha_sweep/raw/`
- `results/paper/prior_factorial/raw/`
- `results/paper/forgiveness/raw/`
- `results/paper/mixed_volatility/raw/`

Compact local README, manifest, summary, metrics, and source-table files were
rsynced into `results/paper/` next to these ignored full-data raw directories.

## Diagnostic Raw Runs

- `results/diagnostics/spine_smoke/raw/`
- `results/diagnostics/precision_sensitivity/raw/`
- `results/diagnostics/social_allocation/raw/`
- `results/diagnostics/policy_openness/raw/`
- `results/diagnostics/locality/raw/`
- `results/diagnostics/h5_candidate_fix/raw/`
- `results/diagnostics/h7_hesp_surprise/raw/`

Compact local README, manifest, and summary files were rsynced into
`results/diagnostics/`. Some diagnostic folders are summary-only in the public
surface because the underlying raw evidence is shared through
`results/diagnostics/spine_smoke/raw/`.

## Archive Buckets

- `results/archive/pre_fix/`
- `results/archive/incomplete/`
- `results/archive/dryruns/`
- `results/archive/logs/`
- `results/archive/batches/`

These are retained for provenance and finality checks, not for paper evidence.

## Removed Junk

Deleted from the server tree:

- all `checkpoint_manifest.json`
- all `results_partial.csv`
- all `corrupt_checkpoint_*` directories

Post-cleanup verification found no `checkpoint_manifest.json` or
`results_partial.csv` under `results/`.

## Size Snapshot

- `results/paper/`: about 1.4 GB
- `results/diagnostics/`: about 425 MB
- `results/archive/`: about 814 MB

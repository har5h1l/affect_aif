# Server Results Cleanup Manifest - 2026-06-11

This manifest records the targeted cleanup applied to
`/Users/server/repos/affect_aif/results/` on 2026-06-11. It documents file
organization only; it does not reinterpret results.

## Preflight

- Mango process registry: no watched processes.
- Remote tmux: one unrelated SocialLearning session
  `sl-h5-fair-self-20260611-105511`; no affect_aif tmux session.
- Remote process scan: no active `affect_aif`, `scripts/experiment`, or
  `scripts/analysis` process.
- Server archive size before cleanup: `results/archive/pre_fix/` was about
  806 MB.
- `results/archive/` is gitignored except for `.gitkeep`.

## Removed Complete Outdated Payload

Deleted from the server tree:

- `results/archive/pre_fix/`

Reason: this bucket was documented as runs from older model semantics or
bounded-error mechanisms. It was complete historical data, not current paper
evidence, and overlapped with the current paper/diagnostic/future layout in a
way that could confuse manuscript provenance.

## Retained

- `results/paper/`: current paper-facing summaries and retained raw payloads.
- `results/diagnostics/`: retained diagnostic provenance.
- `results/future/`: future-extension payloads.
- `results/archive/incomplete/`, `results/archive/dryruns/`,
  `results/archive/logs/`, and `results/archive/batches/`: small audit or
  operational provenance buckets.
- Small legacy compatibility archive folders such as
  `results/archive/pre_fix_h0_h5_20260517_w2/` were left in place because they
  are compact and not the large complete raw-data payload.

## Paper Raw Sync Repair

The same pass repaired a server/local mismatch in current paper data. Before
repair, server manifests for paper cards 01--04 pointed at stale nested raw
paths, and server was missing canonical `raw/results.csv` files for 01--04.
Copied the current local canonical raw files and compact source tables to the
matching server paths:

- `results/paper/01_predictability_value/raw/results.csv`
- `results/paper/02_deployment_ablation/raw/results.csv`
- `results/paper/03_partner_selection/raw/results.csv`
- `results/paper/04_betrayal_adaptation/raw/results.csv`
- `results/paper/01_predictability_value/source_tables/`
- `results/paper/02_deployment_ablation/source_tables/`
- `results/paper/03_partner_selection/source_tables/`
- `results/paper/04_betrayal_adaptation/source_tables/`

Post-sync audit found all seven paper manifests point to existing
`raw/results.csv` files on server, with row counts 18000, 2400, 1800, 14400,
64000, 72000, and 24000 for paper cards 01--05c respectively.

## Post-Cleanup Check

Run after deletion:

```bash
du -sh results/archive/* 2>/dev/null | sort -hr
find results/archive/pre_fix -maxdepth 1 -print
```

Observed remaining archive buckets:

```text
7.3M    results/archive/incomplete
296K    results/archive/pre_fix_h0_h5_20260517_w2
252K    results/archive/logs
108K    results/archive/pre_fix_h0_h5_20260518_remainder
96K     results/archive/incomplete_h3_reallocation_followup_20260519
20K     results/archive/batches
12K     results/archive/dryruns
0B      results/archive/aborted_open_social_confirm_20260525
```

`results/archive/pre_fix/` no longer exists on the server after cleanup.

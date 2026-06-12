# Experiments

This directory explains how the runnable experiment surface is organized.
The command-line entry point is `scripts/experiment/run.py`; notebooks call the
same runner rather than maintaining a separate execution path.

Use these files by task:

- `running.md`: commands, output layout, dry-runs, worker guidance, and analysis.
- `configs.md`: TOML schema, config families, and the maintained config list.
- `paper.md`: paper reproduction suite and how each config maps to the paper.
- `diagnostics.md`: smoke checks, reviewer controls, and informative non-paper probes.

Conceptual claims live in `docs/overview/core/hypotheses.md`. This folder maps those
claims to concrete TOML files and result folders.

The current paper and notebook route uses `experiments/trust/`: one focal
active-inference agent interacting with scripted environment-side partners.
`experiments/multifocal/` is a tested reciprocal AIF-vs-AIF extension, but it
is not wired into `scripts/experiment/run.py`, not listed under `configs/`, and
not used for paper evidence.

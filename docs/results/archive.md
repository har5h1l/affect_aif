# Results Archive Policy

`results/archive/` is ignored by git except for `.gitkeep`. It is for
historical, incomplete, dry-run, or superseded material that should not clutter
the public evidence route.

Archive material can be useful for provenance, but it is not current evidence.
Current paper evidence must live under `results/paper/`; retained non-paper
diagnostics must live under `results/diagnostics/`.

Historical per-run notes that refer to removed config paths are intentionally
kept out of the public docs route. Preserve them only outside the tracked
current evidence route unless they are rewritten against present-day configs
and result cards.

## Archive Buckets

Archive material is organized into:

- `pre_fix/`: runs from older model semantics or bounded-error mechanisms.
- `incomplete/`: runs without finality, preserved only for audit history.
- `dryruns/`: dry-run manifests and command checks.
- `logs/`: operational logs not needed in the public result cards.
- `batches/`: older batch folders retained for provenance.

Local archive content may be smaller than a full private evidence mirror.

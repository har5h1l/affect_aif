# Results Archive Policy

`results/archive/` is ignored by git except for `.gitkeep`. It is for
historical, incomplete, dry-run, or superseded material that should not clutter
the public evidence route.

Archive material can be useful for provenance, but it is not current evidence.
Current paper evidence must live under `results/paper/`; retained non-paper
diagnostics must live under `results/diagnostics/`.

## Archive Buckets

The server cleanup organized archive material into:

- `pre_fix/`: runs from older model semantics or bounded-error mechanisms.
- `incomplete/`: runs without finality, preserved only for audit history.
- `dryruns/`: dry-run manifests and command checks.
- `logs/`: operational logs not needed in the public result cards.
- `batches/`: older batch folders retained for provenance.

Local archive content may be smaller than the server archive. The cleanup
manifests in `docs/results/cleanup/` record what was moved or deleted.

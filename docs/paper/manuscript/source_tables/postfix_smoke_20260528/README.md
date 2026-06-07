# Post-Fix Smoke Source Tables

These compact tables were copied from the server-only result root:

```text
results/log_surprisal_spine_smoke_postfix_20260528/
```

They are small analysis artifacts for manuscript review. Row-level experiment
outputs remain on `server` under `results/`.

Use these tables as diagnostic smoke provenance only. They are superseded by
reviewed higher-seed tables where those exist. The key correction from the
analysis is that H1 preserves the surprise-over-reward model-fitness readout
after active-encounter alignment:

- local affect: `|corr(precision, surprise)| = 0.976`
- local affect: `|corr(precision, payoff)| = 0.721`
- local affect partial readout controlling active payoff and encounter count:
  `0.951` versus `0.172`
- local affect partial surprise-minus-reward effect row:
  `0.7795`

H5 smoke values are superseded by the 30-seed confirmation table at
`../h5_evidence_effect_summary.csv`. Do not use the smoke-scale H5 payoff or
accuracy values in manuscript prose.

The raw H1 exposure diagnostic remains useful because partner beta is
associated with both mean surprisal and mean payoff when grouped by selected
partner/seed. Use the corrected active-aligned and partial-correlation readouts
for H1 confirmation, and redesign only if confirmation remains confounded.

# Post-Fix Smoke Source Tables

These compact tables were copied from the server-only result root:

```text
results/diagnostics/spine_smoke/raw/
```

They are small analysis artifacts for manuscript review. Row-level experiment
outputs remain on `server` under `results/`.

Use these tables as current smoke evidence only. The key correction from the
analysis is that H1 preserves the surprise-over-reward model-fitness readout
after active-encounter alignment:

- local affect: `|corr(precision, surprise)| = 0.976`
- local affect: `|corr(precision, payoff)| = 0.721`
- local affect partial readout controlling active payoff and encounter count:
  `0.951` versus `0.172`
- local affect partial surprise-minus-reward effect row:
  `0.7795`

H5 remains the strongest post-fix behavioral anchor at smoke scale:

- local affect mean payoff: `1322.3`
- no-affect / tracked-only mean payoff: `1225.0`

The raw H1 exposure diagnostic remains useful because partner beta is
associated with both mean surprisal and mean payoff when grouped by selected
partner/seed. Use the corrected active-aligned and partial-correlation readouts
for H1 confirmation, and redesign only if confirmation remains confounded.

# Section-by-section comparison

This is the short technical read for cross-referencing the manuscript. The
[claim and ablation ledger](claim-and-ablation-ledger.md) owns the complete
claim-by-claim status and exact ablation boundaries. Values here are computed
from the corresponding raw tables. Between-packet changes are descriptive
because the shared-action correction changes behavior. Reported intervals
compare affect with its control within a packet across matched seeds.

## 3.1 Predictability rather than realized payoff — retained

| Packet | Partial r: precision vs surprise | Partial r: precision vs payoff |
|---|---:|---:|
| Historical manuscript | -0.940 | 0.023 |
| Shared action, squared charge | -0.710 | -0.018 |
| Shared action, linear charge | -0.660 | 0.094 |

The magnitude of the precision--surprise association remains larger than the
precision--payoff association in every packet. The exact correlations change,
so the historical manuscript values should not be copied into an update.

## 3.2 Deployment through beta-to-gamma — retained and stronger

The comparison is affect minus tracked-only; negative entropy means sharper
policy commitment under affect.

| Packet | Entropy difference (nats) | Beta-range difference |
|---|---:|---:|
| Historical manuscript | -0.238 | 0.022 |
| Shared action, squared charge | -0.518 | -0.005 |
| Shared action, linear charge | -0.770 | -0.043 |

The behavioral deployment result remains and grows after the action correction
and again under the linear charge. The beta tracker continues to move under
the tracked-only ablation; the central distinction is whether that tracker is
allowed to sharpen policy selection.

## 3.3 Partner selection — allocation claim needs revision

The historical packet showed an affect-minus-no-affect shift away from
cooperators (-3.83 percentage points, 95% paired bootstrap interval -6.85 to
-1.13) and toward exploiters (+4.20 points, 1.73 to 7.00). That pattern is not
stable under the corrected action contract:

- Squared charge: the cooperator and exploiter differences are smaller and
  both intervals include zero; the only clear shift is lower reciprocator
  selection (-2.42 points, -3.88 to -1.03).
- Linear charge: all four selected-type allocation intervals include zero.

Affect still changes policy entropy and can alter partner selection. It does
not currently support a stable cooperator-versus-exploiter allocation story.
The conservative manuscript revision is to retain partner-choice/deployment
language and remove the type-specific allocation interpretation unless a new
pre-specified analysis is added.

## 3.4 Abrupt betrayal — lower entropy strengthens; outcome claims stay scoped

All values are affect minus no-affect.

| Packet | Entropy | Joint accuracy | Cumulative payoff |
|---|---:|---:|---:|
| Historical manuscript | -0.375 | +0.106 | +13.75 |
| Shared action, squared charge | -1.443 | +0.087 | +29.57 |
| Shared action, linear charge | -2.149 | +0.158 | +58.15 |

The entropy result is clear under both within-packet analyses: the paired 95%
interval is -1.73 to -1.14 for shared-action squared and -2.38 to -1.90 for
linear. The accuracy effect remains positive. In the shared-action squared
packet, its paired interval excludes zero (+0.017 to +0.153) but the
independent-seed interval includes zero (-0.046 to +0.219); payoff has the
same sensitivity. For linear, both paired and independent-seed intervals are
positive for accuracy and payoff, but this remains one 30-seed simulation
regime rather than a general payoff-improvement claim.

## 3.5 Gain and profile dynamics — mechanism retained; labels/rankings revise

Gain and beta amplitude remain monotonic in the betrayal sweep (Spearman
rho = 1.0 in all three packets). The overall amplitude at alpha = 8 is 1.210
in the historical packet, 0.920 with shared-action squared charge, and 0.675
with linear charge. Thus the gain-to-amplitude relationship is stable, while
its scale is not.

The detailed profile ordering changes. The highest mean betrayal payoff is the
default reference in the historical packet, but naive-high-alpha after the
shared-action correction and under linear charge. The largest beta range is
naive-high-alpha historically and with squared charge, but cautious-high-alpha
with linear charge. Do not retain named profile rankings or failure-mode prose
until the profile and forgiveness tables are refreshed together.

## Final paper-facing decision

Shared action plus linear charge is the promoted camera-ready model. Sections
3.1, 3.2, and 3.4 retain their core interpretations with refreshed values and
seed-level uncertainty. Section 3.3 remains in the paper as a descriptive
partner-choice readout, but the stable allocation-preference story is removed.
Section 3.5 retains the gain mechanism and reports the corrected profile order.

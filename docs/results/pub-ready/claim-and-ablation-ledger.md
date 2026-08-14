# Claim and ablation ledger

This is the authoritative detailed read for `docs/results/pub-ready/`. It
separates a structural correction from genuine ablations, then records the
status of every substantive claim in manuscript Results Sections 3.1--3.5.

## Contract and interpretation rules

- **Historical manuscript packet** means `results/paper/`; it is the submitted
  result packet, not the corrected baseline.
- **Shared action, squared charge** is the main correction baseline.
- **Shared action, linear charge** is a matched charge-rule sensitivity run.
- A **retain** claim has the same qualitative read in both corrected packets.
- A **strengthen** claim has the same read with a larger or clearer effect.
- A **revise** claim has lost a necessary pattern, changed rank/order, or needs
  materially narrower wording.
- A **defer** claim is not adjudicated by the currently summarized comparison
  and must not be carried forward as if it were freshly verified.

Cross-packet values are descriptive: changing the action contract changes
policy construction and trajectories. Seed-paired and independent-seed
intervals are used only for contrasts *within* a packet.

## What is an ablation here?

| Axis | Contrast | What changes | What it can support | What it cannot support |
|---|---|---|---|---|
| Action contract | Historical manuscript vs shared action, squared charge | Factorized controls become one shared six-valued behavioral action. | Whether the manuscript result survives the corrected behavioral contract. | A clean causal effect size for the fix; behavior changes wholesale. |
| Charge rule | Shared action, squared vs shared action, linear | The active beta-update charge is squared surprisal or linear surprisal. | Sensitivity of the corrected result to the Eq. 2 nonlinearity. | A claim that linear is universally better or the required paper equation. |
| Deployment | Full affect vs tracked-only (`lesioned`) | Both track beta; only full affect maps beta to gamma during policy selection. | Whether beta-to-gamma deployment, rather than tracking alone, changes policy commitment. | A direct improvement in the partner-state update. |
| Locality | Full affect vs shared beta (`global_beta`) | Partner-local beta evidence is pooled into one tracker. | Whether relationship-local precision differs from pooled precision. | A generic payoff comparison; payoff is not the designed endpoint. |
| Entire affect layer | Full affect vs no affect | Beta tracking and beta-to-gamma deployment are present or absent. | The total behavioral consequence of the affect layer in this regime. | Which internal component caused the effect. |
| Epistemic value | Full affect vs no epistemic | The policy scorer includes or excludes epistemic value. | Dependence on epistemic policy terms in the deployment setting. | A test of affect itself; both conditions retain the affect layer. |
| Gain | Alpha sweep | Only `alpha_charge` varies. | Whether affective gain controls beta-dynamic amplitude. | A monotonic payoff benefit. |
| Prior x gain | Prior factorial | Initial beta prior and gain vary jointly. | How prior/gain configurations organize computational profiles. | Stable named profile rankings across structural/model changes. |
| Repair protocol | Forgiveness suite | A betrayed partner is reverted at the scheduled repair round. | Whether reengagement, beta recovery, and payoff recovery can dissociate. | A clinical or human-behavior claim. |

## Variant dictionary

| Variant ID | Runtime meaning | Appears in |
|---|---|---|
| `affect` | Partner-local beta tracker and beta-to-gamma deployment. | 3.1--3.4 |
| `global_beta` | One pooled beta tracker; partner POMDP beliefs remain separate. | 3.1--3.4 |
| `lesioned` | Tracked-only: beta updates, but policy precision remains at its baseline value. | 3.2 and 3.4 |
| `no_affect` | No beta tracker or beta-to-gamma modulation. | 3.1, 3.3, 3.4, 3.5 |
| `no_epistemic` | Full affect with epistemic policy value removed. | 3.2 |
| `alpha_*` | Full affect with the named beta-update gain. | 3.5 gain sweep |
| `*_low_alpha`, `*_high_alpha`, `default_reference` | Prior-by-gain profile variants. | 3.5 prior factorial and forgiveness |

## Claim ledger: Section 3.1

| ID | Manuscript claim | Evidence contrast | Status | Corrected evidence | Paper-facing boundary |
|---|---|---|---|---|---|
| 3.1-A | Partner-local precision tracks predictability more strongly than realized payoff. | `affect`, partial precision--surprise vs precision--payoff correlation. | **Retain** | Historical: -0.940 vs +0.023; shared squared: -0.710 vs -0.018; shared linear: -0.660 vs +0.094. | Say the surprise association remains larger in magnitude; replace all historical coefficients. |
| 3.1-B | Pooling beta evidence weakens the relationship-local predictability signal. | `affect` vs `global_beta`. | **Retain, narrower** | Surprise correlation is attenuated under pooled beta in all packets: -0.940 to -0.496, -0.710 to -0.490, and -0.660 to -0.454. | Retain the locality claim. |
| 3.1-C | Under pooled beta, payoff and surprise become comparably associated with precision. | `global_beta`, payoff vs surprise correlation. | **Revise** | This held historically (-0.496 surprise, +0.535 payoff) but not after the correction (-0.490/-0.018 squared; -0.454/+0.072 linear). | Do not retain the payoff-entanglement explanation. |
| 3.1-D | Payoff does not isolate the mechanism. | Local vs pooled beta payoff in the predictability run. | **Retain, wording revise** | Payoff is not the designed discriminator; however, the historical near-tie does not persist identically under every corrected packet. | Do not quote the old "nearly tied" sentence without refreshed values. |

## Claim ledger: Section 3.2

| ID | Manuscript claim | Evidence contrast | Status | Corrected evidence | Paper-facing boundary |
|---|---|---|---|---|---|
| 3.2-A | The beta tracker can move without policy deployment. | `lesioned` retains beta updating while gamma is fixed. | **Retain** | The tracked-only condition still produces beta dynamics in both corrected runs. | This is the cleanest mechanism ablation. |
| 3.2-B | Full affect lowers policy entropy relative to tracked-only. | `affect - lesioned`, mean policy entropy. | **Strengthen** | -0.238 historical, -0.518 shared squared, -0.770 shared linear nats. | Negative means sharper commitment. This is a lead claim. |
| 3.2-C | The tracker range is comparable in full and tracked-only conditions. | `affect - lesioned`, beta range. | **Retain, approximate** | Differences are +0.022, -0.005, and -0.043 respectively. | Do not present exact historical equality as invariant. |
| 3.2-D | Entropy changes without improving payoff. | `affect` vs `lesioned`, cumulative payoff. | **Revise** | Means are 1,997.7 vs 1,966.8 under shared squared and 2,003.3 vs 1,966.8 under linear. | The deployment ablation supports policy commitment, not a universal no-payoff-difference claim. |
| 3.2-E | This is a calibration/deployment layer rather than an inference-improvement mechanism. | Design of `lesioned` contrast. | **Retain as mechanism interpretation** | The ablation localizes the entropy effect to beta-to-gamma deployment, but it does not independently prove that partner-state inference is unchanged in every downstream regime. | Avoid saying the ablation proves zero inference consequence. |

## Claim ledger: Section 3.3

| ID | Manuscript claim | Evidence contrast | Status | Corrected evidence | Paper-facing boundary |
|---|---|---|---|---|---|
| 3.3-A | Affect lowers partner-choice policy entropy. | `affect - no_affect`. | **Strengthen** | -0.238 historical, -0.518 shared squared, -0.770 shared linear nats. | Retain as the principal partner-choice result. |
| 3.3-B | Affect produces a more balanced allocation, with less cooperator and more exploiter selection. | Selected-type allocation, `affect - no_affect`. | **Revise** | Historical cooperator -3.83 pp and exploiter +4.20 pp; both corrected squared intervals include zero; all linear allocation intervals include zero. | Remove the cooperator-versus-exploiter or balanced-allocation story. |
| 3.3-C | Affect reshapes engagement without guaranteed payoff improvement. | `affect - no_affect`, payoff and selection behavior. | **Retain, narrow** | Engagement/entropy changes remain. Mean payoff changes by packet and is not a general endpoint. | Describe changed commitment/engagement, not stable type-specific allocation or global payoff gain. |

## Claim ledger: Section 3.4

| ID | Manuscript claim | Evidence contrast | Status | Corrected evidence | Paper-facing boundary |
|---|---|---|---|---|---|
| 3.4-A | Partner-local affect maintains lower policy entropy after abrupt betrayal. | `affect - no_affect`, 30 matched seeds. | **Strengthen** | -0.375 historical, -1.443 shared squared, -2.149 shared linear nats. Paired intervals exclude zero in both corrected packets. | Lead with entropy. |
| 3.4-B | Joint accuracy is higher under affect. | `affect - no_affect`, mean joint accuracy. | **Retain with inference caveat** | +0.106 historical, +0.087 shared squared, +0.158 shared linear. Squared: paired interval +0.017 to +0.153, independent-seed interval -0.046 to +0.219. Linear: both intervals are positive. | State both inferential contracts for squared; do not call accuracy an independent mechanism replication. |
| 3.4-C | Payoff is positive but uncertain. | `affect - no_affect`, cumulative payoff. | **Revise** | +13.75 historical, +29.57 shared squared, +58.15 shared linear. Squared remains inference-sensitive; linear is positive under both current bootstrap contracts. | Linear is one regime/sensitivity result, not a generic payoff-improvement claim. |
| 3.4-D | Accuracy is a downstream consequence of altered engagement, not a direct beta-state inference improvement. | Relation to the tracked-only deployment ablation. | **Retain as interpretation** | The deployment ablation supports this reading, but it is not a direct intervention on the partner-state update. | Keep the downstream/inference distinction explicit. |
| 3.4-E | Betrayal exposes a timing problem in accumulated social confidence. | Scheduled switch with persistent beta dynamics. | **Retain, qualitative** | The lower-entropy effect survives and strengthens. | Avoid attaching it to the retired allocation story. |

## Claim ledger: Section 3.5

| ID | Manuscript claim | Evidence contrast | Status | Corrected evidence | Paper-facing boundary |
|---|---|---|---|---|---|
| 3.5-A | Gain controls the amplitude of beta dynamics. | Alpha sweep across `alpha_*` variants. | **Retain** | Spearman rho(alpha, beta range) = 1.0 in every packet. At alpha 8, range is 1.210 historical, 0.920 squared, 0.675 linear. | Retain monotonicity; refresh the numeric scale. |
| 3.5-B | Larger gain does not imply monotonic payoff improvement. | Alpha sweep payoff ordering. | **Retain, refresh table** | Amplitude and payoff remain distinct readouts; detailed payoff values change with the correction/charge rule. | Do not reuse historical alpha-payoff endpoints. |
| 3.5-C | The default profile is highest payoff and named profiles have the stated failure-mode order. | Prior-by-gain betrayal factorial. | **Revise** | Historical top payoff: default reference. Corrected squared and linear top payoff: naive-high-alpha. Largest beta range also changes under linear. | Retire named ranking/failure-mode prose until refreshed tables are approved. |
| 3.5-D | Reengagement and confidence/payoff recovery can dissociate. | Forgiveness repair protocol. | **Defer for refreshed table** | The forgiveness raw runs are complete, but the claim depends on detailed profile and recovery metrics whose ordering changed across packets. | Recompute and review the compact forgiveness table before reusing exact examples. |

## What can be said now

1. Partner-local affective precision still tracks predictability more strongly
   than realized payoff.
2. Its clearest behavioral channel remains beta-to-gamma policy deployment,
   with a larger entropy reduction under the corrected action contract and
   under the linear sensitivity run.
3. The specific cooperator-versus-exploiter allocation interpretation does not
   survive and should not be used.
4. Under abrupt betrayal, lower policy entropy is robust; accuracy and payoff
   require the stated inferential and scope caveats.
5. Gain controls beta-dynamic amplitude, but detailed profile labels, ranks,
   and forgiveness examples are not ready to carry forward unchanged.

## Promotion gate

Do not replace the manuscript source tables or `docs/results/current.md` from
this ledger alone. Promotion requires an author decision on the action
correction, a canonical inference contract for the betrayal readout, refreshed
source tables/figures for each retained claim, and separate treatment of the
linear charge as either sensitivity analysis or a new model equation.


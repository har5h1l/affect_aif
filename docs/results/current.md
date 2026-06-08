# Current Results

## Current Evidence Surface

The current paper-facing read uses the post-fix log-surprisal mechanism, the
centered agent-choice selector, the completed H5 confirmation, and reviewed
Exp A-D phenotype artifacts. Pre-May-27 bounded-error results, bounded-surprise
diagnostics, and pre-fix smoke outputs are historical provenance only.

Current provenance:

- Post-fix smoke baseline:
  `results/diagnostics/spine_smoke/raw/`
- H5 confirmation:
  `results/paper/betrayal_adaptation/raw/h5/betrayal_reallocation_confirm/`
- H1 confirmation:
  `results/paper/model_fitness/raw/h1/reliability_vs_reward_confirm/`
- Paper source tables:
  `docs/manuscript/source_tables/`

## Current Read

The central result is conditional, not global: affective precision changes
policy entropy, partner choice, and action deployment when the policy space is
open, but it is not monotonically payoff-improving. The mechanism is best read
as partner-specific model-fitness precision that gates how decisively existing
beliefs are deployed into action.

H5 now has a 30-seed confirmation. Partner-local affect lowers policy entropy
relative to no-affect (`8.36` vs `8.74`) and raises joint partner-type accuracy
(`0.372` vs `0.266`). The payoff difference is small and uncertain (`1185.9`
vs `1172.1`; paired bootstrap interval `-25.2` to `53.2`). The older
three-seed payoff--accuracy tradeoff story is obsolete.

Exp A-D now support a phenotype-style, non-monotonic profile story. Gain
controls beta movement, but higher gain does not simply improve reward. Exp C
forgiveness separates reengagement from confidence restoration: no-affect and
cautious-low-alpha profiles reengage most, while payoff recovery remains near
baseline across profiles. Exp D mixed volatility supports a boundary condition,
not the older strong sensitivity-specificity claim.

H1 now has a 30-seed confirmation. Partner-local precision tracks action
surprisal more strongly than realized payoff after active-encounter controls
(`0.882` vs `0.130` partial absolute association). Shared beta preserves the
ordering with weaker specificity (`0.380` vs `0.049`). Payoff favors no-affect
in this probe (`542.1` vs `483.5` local), so H1 supports model-fitness tracking
rather than reward improvement.

## Hypothesis Scorecard

| Card | Current status | Evidence read |
|---|---|---|
| H0 Openness Gate | Diagnostic support | Shallow/binary regimes leave little room for affect; graded/open policy spaces reveal entropy/deployment effects. Do not use broad payoff language. |
| H1 Model Fitness | Confirmation support | Partner-local precision tracks surprise more strongly than payoff after active-encounter controls; payoff does not favor affect, so this is model-fitness evidence rather than reward evidence. |
| H2 Deployment | Supported narrowly | Tracked-only matches no-affect while full affect lowers entropy, localizing the effect to beta-to-gamma deployment rather than extra belief evidence. |
| H3 Locality | Signal-quality support | Partner-local beta preserves a cleaner surprise-over-payoff readout than shared beta in the focal-switch probe; behavioral necessity is not established. |
| H4 Social Choice | Diagnostic support | Partner-choice behavior reorganizes before payoff separates; keep allocation language narrow unless confirmation-scale seeds are added. |
| H5 Betrayal | Confirmation support | Lower entropy and higher joint accuracy under partner-local affect; payoff advantage is small/uncertain. Temporal dependency, not generic reward improvement. |
| H6 / Exp A-D Phenotypes | Supported as computational profiles | Alpha and prior shape confidence amplitude, reengagement, false positives, and payoff non-monotonically. No clinical-validation claim. |

## Claims To Use

- Affective precision tracks behavioral predictability/model fitness rather
  than partner value.
- Its behavioral effect is metacognitive deployment: precision changes action
  confidence, not the content of partner-state beliefs.
- Partner-locality improves interpretability of the reliability signal; shared
  beta attenuates the signal, while universal behavioral necessity remains a
  narrower reviewer-driven question.
- Abrupt betrayal is a boundary condition showing action sharpening under
  temporal change, with payoff effects dependent on portfolio structure.
- Phenotype results are computational analogues of trust-calibration profiles,
  not human or clinical validation.

## Claims To Avoid

- Affect globally improves reward.
- H5 confirms payoff improvement with lower accuracy.
- Partner-local beta is behaviorally necessary under all task structures.
- Exp A-D validate clinical categories.
- Pre-fix or bounded-error numbers as current manuscript evidence.

## Interpretation Guard

The user approved interpretation updates for Exp C, H5, and H1 on June 6,
2026. For future new outputs, ask before rewriting result interpretation docs
unless the user explicitly requests the update in that turn.

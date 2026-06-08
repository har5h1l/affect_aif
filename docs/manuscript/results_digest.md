# Results Digest For Current Draft

## Inclusion Decision

Use the reviewed paper source tables in this folder for current manuscript
claims. The post-fix three-seed log-surprisal smoke remains diagnostic
provenance for early H-card readouts; old bounded-error, bounded-surprise, and
pre-fix smoke outputs must not be promoted as current evidence.

Current confirmation / manuscript-scale surfaces:

| Evidence family | Source | Scale | Manuscript status |
|---|---|---:|---|
| H5 abrupt betrayal | `source_tables/h5_evidence_effect_summary.csv` | 30 seeds | interpreted |
| Exp A alpha sweep | `source_tables/exp_a_alpha_sweep/metrics.csv` | 20 seeds | interpreted |
| Exp B prior factorial | `source_tables/exp_b_prior_factorial/metrics.csv` | 20 seeds | interpreted |
| Exp C forgiveness | `source_tables/exp_c_forgiveness/metrics.csv` | 20 seeds | interpreted |
| Exp D mixed volatility | `source_tables/exp_d_mixed_volatility/metrics.csv` | 20 seeds | interpreted narrowly |
| H1 model fitness | `source_tables/h1_model_fitness_confirm/` | 30 seeds | interpreted |
| H4 partner choice | `source_tables/h4_partner_choice_summary.csv` | 5 seeds | interpreted at current scale |

## Current Read

### R1: H1 confirms model-fitness tracking, not reward gain

The 30-seed confirmation reached structural finality at 90/90 groups x 200
rounds. Partner-local precision tracks action surprisal more strongly than
realized payoff: absolute active-encounter partial associations are `0.882`
versus `0.130`. Shared beta preserves the ordering but is weaker (`0.380`
versus `0.049`). Payoff moves in the opposite direction (`483.5` local,
`517.6` shared, `542.1` no-affect), so H1 should be written as a
model-fitness dissociation, not a reward advantage.

### R2: Open-regime deployment changes without stable payoff gain

H0/H2 diagnostic read:

- Affect: payoff `1851.3`, entropy `8.59`.
- No-affect/tracked-only: payoff `1864.2`, entropy `8.79` (identical on both metrics).

Interpretation: the beta-to-gamma path changes policy entropy, while payoff
does not support a broad reward-improvement claim in this open graded readout.

### R3: Locality is signal quality, not universal behavioral necessity

H1 confirmation read:

- Local beta partials: surprise `0.882`, reward `0.130`.
- Shared/global beta partials: surprise `0.380`, reward `0.049`.
- Payoff: local `483.5`, shared/global `517.6`, no-affect `542.1`.

Interpretation: local beta is the cleaner partner-specific signal in this
probe, while payoff does not establish a universal behavioral advantage for
local beta.

### R4: H5 confirmation supports action sharpening, not a payoff headline

H5 abrupt-betrayal confirmation (P0 stance switch at round 31; 30 seeds):

- Policy entropy: affect `8.36`, no-affect `8.74`; interval for the difference
  is negative (`-0.62` to `-0.14`) --- lead result.
- Joint accuracy: affect `0.372`, no-affect `0.266`; interval for the
  difference is positive (`0.034` to `0.185`).
- Total payoff: affect `1185.9`, no-affect `1172.1`; paired bootstrap interval
  for the difference crosses zero (`-25.2` to `53.2`).
- Reallocation diagnostic (not in main-text numbers): post-switch reencounters
  with P0 are higher under affect (`5.67` vs `1.33`; CI `0.97` to `8.03`).

Interpretation: open with accumulated confidence as liability under change;
lead with entropy, then joint accuracy, then uncertain payoff as the correct
readout for a calibration mechanism (not a power failure). Hand off to §3.6 on
revision speed via precision gain and prior model fitness. Do not write H5 as
generic recovery, generic reward improvement, or an accuracy cost.

### R4b: Partner-choice sharpening without payoff separation

H4 partner-choice read (`h4_partner_choice_summary.csv`, 5 seeds):

- Policy entropy: affect `3.99`, no-affect `4.83`.
- Cooperator selection: affect `36.6%`, no-affect `34.8%`.
- Exploiter selection: affect `13.8%`, no-affect `16.2%`.
- Total payoff: affect `393.6`, no-affect `393.2`.

Interpretation: the $\beta_k \rightarrow \gamma_k$ pathway reaches partner
selection; allocation shifts directionally toward predictable partners without
a cumulative-payoff advantage, consistent with the Section 3.1 dissociation.
Not yet confirmed at the 30-seed scale stated in Appendix protocols.

### R5: Phenotype program supports non-monotonic profile effects

The 20-seed Exp A-D program is written as computational profile evidence,
not clinical validation. §3.6 now opens with a four-experiment orienting
frame (gain sweep, gain-prior factorial, forgiveness, mixed volatility) and
closes with trade-off synthesis rather than a monotonic payoff ranking.

- Exp A: $\beta_k$ range scales monotonically with $\alpha$ (0.147--1.218 in
  betrayal) but payoff does not (betrayal 1914.6--1986.2; open graded
  1906.3--1987.7).
- Exp B: four profiles each isolate a failure mode (diffuse naive-stubborn,
  low-payoff avoidant-rigid at 1889, post-betrayal liability in
  anxious-reactive, balanced default at 1991).
- Exp C: reengagement (no-affect 0.593, cautious-low 0.630) dissociates from
  payoff recovery (0.996--1.033); round-121 reversion per appendix protocol.
- Exp D: high-$\alpha$ raises payoff (2054) while worsening discrimination
  ($-0.089$) and false positives toward P0 (0.484).
- Human-behavior disclaimer moved to Discussion §4 (profile paragraph).

## Claims To Use Now

- Partner-local affective precision is a model-fitness / reliability signal,
  not a partner-value signal.
- Its clearest behavioral channel is metacognitive deployment through
  beta-to-gamma action sharpening.
- H5 confirms that abrupt change activates the deployment channel, but payoff
  effects remain portfolio- and regime-dependent.
- Exp A-D define computational trust-calibration profiles from gain and prior
  structure.
- The corrected agent-choice path uses centered precision logits.

## Claims To Avoid

- Do not claim affect globally improves payoff.
- Do not claim local affect wins in the open graded regime.
- Do not claim partner-local beta is behaviorally necessary in all settings.
- Do not describe H5 confirmation as payoff improvement with lower accuracy.
- Do not claim H6 or Exp A-D validate clinical phenotypes.
- Do not reuse old bounded-error numbers or pre-fix smoke numbers as current
  manuscript evidence.

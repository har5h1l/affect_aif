# Current Results

Canonical interpreted evidence for the active architecture. Manuscript prose
lives in `docs/manuscript/sections/`; compact CSVs for paper-figure
regeneration live in `docs/manuscript/source_tables/`.

## Inclusion Decision

Use the reviewed paper source tables for current manuscript claims. Old
bounded-error, bounded-surprise, pre-fix smoke, and non-paper outputs must
not be promoted as current paper evidence.

| Evidence family | Source table | Scale | Manuscript status |
|---|---|---:|---|
| H5 abrupt betrayal | `docs/manuscript/source_tables/h5_evidence_effect_summary.csv` | 30 seeds | interpreted |
| Exp A alpha sweep | `docs/manuscript/source_tables/exp_a_alpha_sweep/metrics.csv` | 20 seeds | interpreted |
| Exp B prior factorial | `docs/manuscript/source_tables/exp_b_prior_factorial/metrics.csv` | 20 seeds | interpreted |
| Exp C forgiveness | `docs/manuscript/source_tables/exp_c_forgiveness/metrics.csv` | 20 seeds | interpreted |
| H4 partner choice | `docs/manuscript/source_tables/h4_partner_choice_summary.csv` | 5 seeds | interpreted at current scale |

## Provenance

The current paper-facing read uses the post-fix log-surprisal mechanism, the
centered agent-choice selector, the completed H5 confirmation, and reviewed
Exp A-C profile artifacts.

- H5 confirmation:
  `results/paper/04_betrayal_adaptation/raw/betrayal_adaptation/betrayal_adaptation/`
- Paper result cards: `results/paper/manifest.json` and `docs/results/paper.md`
- Paper source tables: `docs/manuscript/source_tables/`

## Central Read

The central result is conditional, not global: affective precision changes
policy entropy, partner choice, and action deployment when the policy space is
open, but it is not monotonically payoff-improving. The mechanism is best read
as partner-specific confidence calibration that gates how decisively existing
beliefs are deployed into graded trust-game actions.

## Evidence Reads

### R1: Open-regime deployment changes without stable payoff gain

Open graded read:

- Affect: payoff `1851.3`, entropy `8.59`.
- No-affect/tracked-only: payoff `1864.2`, entropy `8.79` (identical on both metrics).

Interpretation: the beta-to-gamma path changes policy entropy, while payoff
does not support a broad reward-improvement claim in this open graded readout.

### R2: H5 confirmation supports action sharpening, not a payoff headline

H5 abrupt-betrayal confirmation (P0 stance switch at round 31; 30 seeds):

- Policy entropy: affect `8.36`, no-affect `8.74`; interval for the difference
  is negative (`-0.62` to `-0.14`) --- lead result.
- Joint accuracy: affect `0.372`, no-affect `0.266`; interval for the
  difference is positive (`0.034` to `0.185`).
- Total payoff: affect `1185.9`, no-affect `1172.1`; paired bootstrap interval
  for the difference crosses zero (`-25.2` to `53.2`).
- Reallocation support readout (not in main-text numbers): post-switch reencounters
  with P0 are higher under affect (`5.67` vs `1.33`; CI `0.97` to `8.03`).

Interpretation: open with accumulated confidence as liability under change;
lead with entropy, then joint accuracy, then uncertain payoff as the correct
readout for a calibration mechanism (not a power failure). Hand off to §3.6 on
revision speed via precision gain and prior model fitness. Do not write H5 as
generic recovery, generic reward improvement, or an accuracy cost.

### R3: Partner-choice sharpening without payoff separation

H4 partner-choice read (`h4_partner_choice_summary.csv`, 5 seeds):

- Policy entropy: affect `3.99`, no-affect `4.83`.
- Cooperator selection: affect `36.6%`, no-affect `34.8%`.
- Exploiter selection: affect `13.8%`, no-affect `16.2%`.
- Total payoff: affect `393.6`, no-affect `393.2`.

Interpretation: the $\beta_k \rightarrow \gamma_k$ pathway reaches partner
selection; allocation shifts directionally toward predictable partners without
a cumulative-payoff advantage.
Not yet confirmed at the 30-seed scale stated in Appendix protocols.

### R4: Phenotype program supports non-monotonic profile effects

The 20-seed Exp A-C program is written as computational profile evidence,
not clinical validation. §3.6 opens with a three-experiment orienting
frame (gain sweep, gain-prior factorial, forgiveness) and closes with
trade-off synthesis rather than a monotonic payoff ranking.

- Exp A: $\beta_k$ range scales monotonically with $\alpha$ (0.147--1.218 in
  betrayal) but payoff does not (betrayal 1914.6--1986.2; open graded
  1906.3--1987.7).
- Exp B: four profiles each isolate a failure mode (diffuse naive-stubborn,
  low-payoff avoidant-rigid at 1889, post-betrayal liability in
  anxious-reactive, balanced default at 1991).
- Exp C: reengagement (no-affect 0.593, cautious-low 0.630) dissociates from
  payoff recovery (0.996--1.033); round-121 reversion per appendix protocol.
- Mixed-volatility analyses are future-facing and are not reported as
  manuscript evidence.
- Human-behavior disclaimer belongs in Discussion §4 (profile paragraph).

## Hypothesis Scorecard

| Card | Current status | Evidence read |
|---|---|---|
| Graded Openness | Supported narrowly | Open graded policy spaces reveal entropy/deployment effects. Do not use broad payoff language. |
| Deployment | Supported narrowly | Tracked-only matches no-affect while full affect lowers entropy, localizing the effect to beta-to-gamma deployment rather than extra belief evidence. |
| H4 Social Choice | Diagnostic support | Partner-choice behavior reorganizes before payoff separates; keep allocation language narrow unless confirmation-scale seeds are added. |
| H5 Betrayal | Confirmation support | Lower entropy and higher joint accuracy under partner-local affect; payoff advantage is small/uncertain. Temporal dependency, not generic reward improvement. |
| H6 / Exp A-C Profiles | Supported as computational profiles | Alpha and prior shape confidence amplitude, reengagement, commitment errors, and payoff non-monotonically. No clinical-validation claim. |

## Claims To Use

- Its clearest behavioral channel is metacognitive deployment through
  beta-to-gamma action sharpening.
- H5 confirms that abrupt change activates the deployment channel, but payoff
  effects remain portfolio- and regime-dependent.
- Exp A-C define computational trust-calibration profiles from gain and prior
  structure.
- The corrected agent-choice path uses centered precision logits.

## Claims To Avoid

- Do not claim affect globally improves payoff.
- Do not claim local affect wins in the open graded regime.
- Do not claim partner-local beta is behaviorally necessary in all settings.
- Do not describe H5 confirmation as payoff improvement with lower accuracy.
- Do not claim H6 or Exp A-C validate clinical phenotypes.
- Do not reuse old bounded-error numbers or pre-fix smoke numbers as current
  manuscript evidence.

## Interpretation Guard

The user approved interpretation updates for Exp C and H5 on June 6, 2026. For
future new outputs, ask before rewriting result interpretation docs unless the
user explicitly requests the update in that turn.

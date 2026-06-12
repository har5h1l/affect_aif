# Current Results

Canonical interpreted evidence for the active architecture. Manuscript prose
lives in `docs/manuscript/sections/`; compact CSVs for paper-figure generation
live in `docs/manuscript/source_tables/`.

## Inclusion Decision

Use the reviewed paper source tables for current manuscript claims. Old
bounded-error, bounded-surprise, pre-fix smoke, and non-paper outputs must
not be promoted as current paper evidence.

| Evidence family | Source table | Scale | Manuscript status |
|---|---|---:|---|
| Predictability over payoff | `docs/manuscript/source_tables/h1_model_fitness_confirm/model_fitness_correlation_summary.csv` | 30 seeds | interpreted |
| H5 abrupt betrayal | `docs/manuscript/source_tables/h5_evidence_effect_summary.csv` | 30 seeds | interpreted |
| Alpha sweep | `docs/manuscript/source_tables/alpha_sweep/metrics.csv` | 20 seeds | interpreted |
| Prior factorial | `docs/manuscript/source_tables/prior_factorial/metrics.csv` | 20 seeds | interpreted |
| Forgiveness | `docs/manuscript/source_tables/forgiveness/metrics.csv` | 20 seeds | interpreted |
| H2 deployment ablation | `docs/manuscript/source_tables/h2_deployment_pathway_summary.csv` | 30 seeds | interpreted |
| H4 partner choice | `docs/manuscript/source_tables/h4_partner_choice_summary.csv` | 30 seeds | interpreted |

## Provenance

The current paper-facing read uses the post-fix log-surprisal mechanism, the
centered agent-choice selector, the completed H5 confirmation, and reviewed
Exp A-C profile artifacts.

- H5 confirmation:
  `results/paper/04_betrayal_adaptation/raw/results.csv`
- H2 deployment confirmation:
  `results/paper/02_deployment_ablation/raw/results.csv`
- H4 graded partner-choice confirmation:
  `results/paper/03_partner_selection/raw/results.csv`
- Binary H4 confirmation diagnostic:
  `results/diagnostics/social_allocation/raw/partner_choice_confirm_20260609/h4/partner_choice_confirm/`
- Paper result cards: `results/paper/manifest.json` and `docs/results/paper.md`
- Manuscript source-table and figure map: `docs/results/provenance.md`

## Central Read

The central result is conditional, not global: affective precision changes
policy entropy, partner choice, and action deployment when the policy space is
open, but it is not monotonically payoff-improving. The mechanism is best read
as partner-specific confidence calibration that gates how decisively existing
beliefs are deployed into graded trust-game actions.

## Evidence Reads

### R1: Open-regime deployment changes without stable payoff gain

Open graded read:

- Affect: payoff `1868.3`, entropy `8.60`, beta range `1.34`.
- Tracked-only: payoff `1866.2`, entropy `8.83`, beta range `1.34`.

Interpretation: the beta-to-gamma path changes policy entropy, while payoff
does not support a broad reward-improvement claim in this open graded readout.
Tracked-only confirms that beta can update without the deployment effect when
the beta-to-gamma pathway is cut.

### R2: H5 confirmation supports action sharpening, not a payoff headline

H5 abrupt-betrayal confirmation (P0 stance switch at round 31; 30 seeds):

- Policy entropy: affect `8.36`, no-affect `8.74`; interval for the difference
  is negative (`-0.63` to `-0.16`) --- lead result.
- Joint accuracy: affect `0.372`, no-affect `0.266`; interval for the
  difference is positive (`0.024` to `0.188`).
- Total payoff: affect `1185.9`, no-affect `1172.1`; paired bootstrap interval
  for the difference crosses zero (`-21.6` to `52.0`).
- Time-course support readout: post-switch P0 engagement remains higher under
  affect than no-affect while policy entropy stays lower; tracked-only keeps a
  beta trajectory without the same deployment pathway.

Interpretation: open with accumulated confidence as liability under change;
lead with entropy, then joint accuracy, then uncertain payoff as the correct
readout for a calibration mechanism (not a power failure). Hand off to §3.6 on
revision speed via precision gain and prior model fitness. Do not write H5 as
generic recovery, generic reward improvement, or an accuracy cost.

### R3: Partner-choice sharpening without payoff separation

Graded H4 partner-choice paper read (`h4_partner_choice_summary.csv`, 30 seeds;
selected-type percentages pooled from
`results/paper/03_partner_selection/raw/results.csv` by `true_partner_type`):

- Policy entropy: affect `8.60`, no-affect `8.83`.
- Selected-type allocation, affect vs no-affect: cooperator `25.3%` vs
  `29.2%`, exploiter `25.5%` vs `21.3%`, reciprocator `23.7%` vs `22.5%`,
  random `25.5%` vs `27.1%`.
- Total payoff: affect `1868.3`, no-affect `1866.2`.

Interpretation: the $\beta_k \rightarrow \gamma_k$ pathway reaches partner
selection; allocation is reorganised without a simple cooperator-seeking
headline or cumulative-payoff advantage. The completed 30-seed binary H4
confirmation is retained as diagnostic boundary evidence only and does not
replace these graded paper numbers.

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
| Deployment | Supported narrowly | Tracked-only preserves beta movement while full affect lowers entropy, localizing the effect to beta-to-gamma deployment rather than extra belief evidence. |
| H4 Social Choice | Paper readout supported narrowly; binary confirmation diagnostic only | Graded partner-choice behavior reorganizes before payoff separates; keep allocation language narrow and avoid a one-type preference headline. The binary H4 confirmation is not a paper regime. |
| H5 Betrayal | Confirmation support | Lower entropy and higher joint accuracy under partner-local affect; payoff advantage is small/uncertain. Temporal dependency, not generic reward improvement. |
| Exp A-C Profiles | Supported as computational profiles | Alpha and prior shape confidence amplitude, reengagement, commitment errors, and payoff non-monotonically. No clinical-validation claim. |

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
- Do not claim Exp A-C validate clinical phenotypes.
- Do not reuse old bounded-error numbers or pre-fix smoke numbers as current
  manuscript evidence.

## Interpretation Guard

The user approved interpretation updates for Exp C and H5 on June 6, 2026. For
future new outputs, ask before rewriting result interpretation docs unless the
user explicitly requests the update in that turn.

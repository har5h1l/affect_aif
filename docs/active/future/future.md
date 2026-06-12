# Future Work

## Reciprocal AIF Partners

Current paper experiments use one focal active-inference agent against
environment-side scripted partners. The reciprocal extension lives in
`experiments/multifocal/`: each participant is built from the same native trust
runtime and paired through a turn-taking trust game.

Status:

- Implemented as a prototype with `MultiFocalConfig`, `MultiFocalRunner`, and
  `joint_resolve`.
- Covered by dedicated unit and lightweight end-to-end tests.
- Example JSON configs live under `experiments/multifocal/configs/`.
- Not wired into `scripts/experiment/run.py`.
- Not part of `configs/paper/`, `configs/demo/`, or `configs/diagnostics/`.
- Not used in the manuscript or paper result summaries.

Useful next steps:

1. Decide whether reciprocal AIF-vs-AIF is a manuscript extension, a separate
   follow-up project, or a supplemental demonstration.
2. Add a public runner path only after the output schema and analysis questions
   are settled.
3. Move or mirror its configs into `configs/future/multifocal/` if it becomes a
   supported public surface.
4. Add result cards under `docs/results/diagnostics.md` or a future-result doc
   only after real outputs have been reviewed.

## Empirical Validation And Human Fitting

The current paper is simulation evidence for a mechanism, not a human-behavior
or clinical-validation claim. A natural next project is to fit the model to
iterated trust-game behavior and ask whether profile parameters explain stable
individual differences.

Candidate fitted parameters:

- `alpha_charge`: how quickly prediction error changes affective precision.
- `beta_persistence`: how sticky partner confidence is across observations.
- `initial_beta` or `initial_beta_prior`: prior model-fitness expectations.
- policy-precision coupling: how strongly beta-derived confidence changes
  action commitment.

Good first empirical targets are the dissociations already emphasized in the
paper: predictability over value, deployment over inference, and partner-local
over shared confidence. Clinical-adjacent labels should remain computational
profile descriptions unless a separate validation study supports stronger
claims.

## Model Architecture Extensions

- Embed beta as a proper hidden state rather than an external tracker, allowing
  agents to form expectations about future action confidence.
- Add volatility or change-detection logic that discounts stale confidence
  after structured prediction-error shifts.
- Add structure learning: persistent low precision could trigger search for a
  better partner model rather than only lowering policy precision.
- Add richer theory-of-mind partner models while keeping affective precision as
  the confidence/deployment layer rather than the content of partner inference.

## Heterogeneous Volatility Extension

The mixed-volatility config is implemented under
`configs/future/mixed_volatility.toml`, but it is not part of the current paper
evidence. The issue is not that the environment is weak. The issue is that once
it appears in the appendix it stops being merely extra: readers can reasonably
ask what the discrimination index measures, why higher gain can improve payoff
while worsening discrimination, what P0 confidence-drop metrics mean, whether
that contradicts the main calibration claim, and whether the paper has become a
volatility-learning paper.

Treat this as a real follow-up extension. A future version should define the
volatility-learning question explicitly, add a change-detection account, and
decide whether payoff, discrimination, stable-partner confidence retention, or
adaptation speed is the primary target before reporting the results.

## Task And Evaluation Extensions

- Add noisy observations, larger action spaces, delayed reward, coalition or
  group structure, and richer partner dynamics.
- Add a supported benchmark/evaluation arena only if there is a concrete
  baseline question. The old benchmark branch explored trust-task baseline
  comparisons against agents such as random, tit-for-tat, Pavlov, and grim
  trigger, but it should stay future-facing rather than returning to the public
  paper reproduction surface.
- If revived, benchmarks should be separate from paper experiments, with their
  own result cards and no implication that they are manuscript evidence unless
  explicitly run and reviewed.

# Manuscript Outline

## Working Title

Partner-Specific Affective Precision Gates Social Policy Deployment in
Multi-Agent Active Inference

## Abstract Skeleton

Active-inference accounts of affect model valence as inference over expected
action precision. We extend this account to social interaction by factorizing
affective precision over partners in a repeated trust game. Each partner is
modeled with an official `pymdp` POMDP over type, stance, and own action, while
an external HESP-style beta tracker updates from partner-action prediction
error and modulates policy precision. Across current-architecture diagnostic
simulations, partner-local precision is behaviorally active when the policy
posterior has room to move, supports a corrected surprise-over-reward readout
at smoke scale, and changes deployment even when partner beliefs remain
similar. Under abrupt betrayal, the same precision channel becomes a candidate
positive behavioral anchor and a boundary condition requiring confirmation.
These results motivate affective precision as a partner-local model-fitness
signal, not as a generic reward booster, while leaving publication-grade H1/H5
confirmation as planned work.

## Introduction

1. Active inference treats perception and action as inference under a
   generative model.
2. Hesp et al. model affective valence through expected action precision and
   model fitness.
3. Social interaction creates a natural factorization problem: agents do not
   have one social model, they have partner-specific models.
4. The paper asks whether partner-specific affective precision helps deploy
   social knowledge, and when it fails.

## Theory

### Core Mechanism

```text
partner prediction reliability
  -> partner-specific beta / precision
  -> policy posterior shift
  -> action or partner-choice behavior
  -> payoff, reallocation, or misdeployment
```

### Key Distinction

Precision is not partner liking, reward, or a literal trust scalar. A reliable
exploiter can have high model-fitness precision because the agent can predict
and avoid or defect against them confidently.

## Model

- Runtime: official `inferactively-pymdp==1.0.0`.
- Hidden state factors: partner type, partner stance, own action.
- Observations: partner action and payoff.
- Control: partner-local factorized stance and own-action controls; partner
  selection is evaluated outside each partner-local POMDP.
- Affect: external per-partner beta tracker, with
  `gamma_k = gamma_base / E[beta_k]`.
- Lesion: beta updates continue but policy precision is decoupled.

## Experiments

Use the H0-H6 behavior-card spine:

- H0: openness gate
- H1: model fitness
- H2: deployment
- H3: locality / global precision
- H4: social allocation
- H5: timescale / volatility
- H6: perturbation phenotypes

Primary current diagnostic results should be reported from:

- `results/log_surprisal_spine_smoke_postfix_20260528/`
- `docs/paper/manuscript/results_digest.md`
- `docs/active/progress.md`

Historical bounded-error and pre-log-surprisal notes are provenance only, not
current manuscript evidence.

## Results

### Result 1: Policy Openness Gates Affect

Report H0 graded choice and contrast with saturated or stress regimes. Emphasize
that openness permits movement but does not guarantee payoff improvement.

### Result 2: Precision Tracks Model Fitness, Not Reward

Use the corrected post-fix H1 smoke as a mechanism diagnostic, not as final
publication evidence. The manuscript should show precision-surprise and
precision-payoff associations only after confirmation-scale active-encounter
and partial-correlation readouts are complete, or after the controlled H1
diagnostic ladder resolves any reward/exposure confound.

### Result 3: Affect Changes Deployment

Use H2 lesion/open-regime results. Show similar belief accuracy with different
policy entropy and payoff.

### Result 4: Social Choice Moves Before Payoff

Use H4. Show partner selection and entropy changes even when total payoff is
flat.

### Result 5: Locality Separates Signal Quality From Necessity

Use H3 locality/global-beta results. Show partner-local beta as a cleaner
partner-specific model-fitness signal, while avoiding a behavioral necessity
claim unless Exp D or a higher-seed H3 run shows cross-partner interference.

### Result 6: Volatility Reveals Boundary Conditions

Use H5 betrayal results. Show abrupt betrayal as the priority behavioral
confirmation target and keep recovery/payoff claims conditional until
confirmation-scale reruns complete.

### Result 7: Perturbation Phenotypes Separate Dynamically

Use H6 and Exp A-D only after final outputs are reviewed. Emphasize beta
dynamics and policy/choice readouts rather than clinical validity.

## Discussion

Main interpretation:

- Affect is computational infrastructure for social policy deployment.
- The precision channel is useful because it compresses model fitness by
  partner.
- The same channel can be dangerous under sudden model mismatch.

Position against alternatives:

- Not reward averaging.
- Not just deeper planning.
- Not literal trust.
- Not a validated clinical model.

## Limitations

- Simulation-only.
- Scripted partner behaviors in the primary trust task.
- Global-beta ablation is discovery-scale only; partner-local beta remains an
  interpretable model-fitness implementation, not yet a proven behavioral
  necessity.
- H5 payoff effects are smoke-scale until confirmation.
- H1 remains smoke-supported but needs the active confirmation/diagnostic
  ladder before carrying the model-fitness claim.

## Conclusion

Partner-local affective precision is a plausible computational bridge between
social model fitness and action deployment. The current evidence supports the
mechanism and its boundary condition, while leaving human validation and
broader model comparison for future work.

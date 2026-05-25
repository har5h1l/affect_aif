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
error and modulates policy precision. Across current-architecture simulations,
partner-local precision is behaviorally active when the policy posterior has
room to move, tracks prediction reliability more than payoff, and changes
deployment even when partner beliefs remain similar. Under abrupt betrayal,
however, the same precision channel can sharpen a wrong post-switch model and
reduce payoff. These results support affective precision as a partner-local
model-fitness signal, not as a generic reward booster.

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

Use the H0-H5 behavior-card spine:

- H0: openness gate
- H1: model fitness
- H2: deployment
- H3: stress response
- H4: social choice
- H5: perturbation phenotypes

Primary results should be reported from:

- `docs/results/runs/2026-05-18-h0-h5-rerun.md`
- `docs/results/runs/2026-05-21-h1-h3-confirmation.md`
- `docs/results/runs/2026-05-24-h3-precision-sensitivity.md`

## Results

### Result 1: Policy Openness Gates Affect

Report H0 graded choice and contrast with saturated or stress regimes. Emphasize
that openness permits movement but does not guarantee payoff improvement.

### Result 2: Precision Tracks Model Fitness, Not Reward

Use the 30-seed H1 confirmation as the primary mechanism result. Show
precision-surprise and precision-payoff associations.

### Result 3: Affect Changes Deployment

Use H2 lesion/open-regime results. Show similar belief accuracy with different
policy entropy and payoff.

### Result 4: Social Choice Moves Before Payoff

Use H4. Show partner selection and entropy changes even when total payoff is
flat.

### Result 5: Stress Reveals Misdeployment

Use H3 confirmation and precision sensitivity. Show abrupt betrayal as a
failure mode, and gradual betrayal as less harmful for default affect.

### Result 6: Perturbation Phenotypes Separate Dynamically

Use H5 as secondary evidence. Emphasize beta dynamics and policy/choice
readouts rather than clinical validity.

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
- No global-beta ablation yet.
- H5 payoff effects are underpowered.
- H3 stress result is task-regime dependent.

## Conclusion

Partner-local affective precision is a plausible computational bridge between
social model fitness and action deployment. The current evidence supports the
mechanism and its boundary condition, while leaving human validation and
broader model comparison for future work.

# Experimentation Plan: Affect as Computational Infrastructure for Social Inference

## Testing Per-Partner Affective Precision in Multi-Agent Active Inference

## Current Trust-Game Status

The supported experiment surface has moved to the action-dependent stance model
described in `docs/theory/pomdp_spec.md` and `docs/design/implementation.md`.

- Ground-truth partners now have a fixed type and an evolving stance.
- The agent jointly infers `type × stance` and plans with action-dependent stance transitions.
- The trust-game generative model now uses two observation modalities (`o_action`, `o_payoff`) over latent `type × stance`, with `own_action` tracked separately.
- The default affective path uses the discrete HESP beta filter (`DiscreteBetaState`, `initial_beta=1.0`, beta levels `[0.5, 0.67, 1.0, 1.5, 2.0]`).
- Policy inference is performed by official `pymdp.Agent` instances built from `tasks.trust.pomdp`; affect modulates partner-local policy precision as `gamma_k = gamma_base / E[beta_k]`.
- The primary maintained experiment surface is now TOML specs under `configs/trust/hypotheses/`.
- Planning horizon, affect mode, lesions, no-epistemic variants, and clinical-like perturbations are explicit `[[variants]]` rather than numeric conditions or presets.
- Scheduled betrayal should be expressed via `scheduled_stance_switches`, not `scheduled_type_switches`, unless the experiment is explicitly about exogenous type volatility.

### Future-work experiment surfaces

The following require new implementation and tests before they become runnable
surface:

- **Variational beta** — a variational auxiliary state would be new code.
- **CoGames policy bridge** — CvC integration should add a policy class under
  `benchmarks/cvc/` when that track unfreezes.

---

## 1. Overview

This document frames the supported trust-game program around chronological
behavior cards.

The central claim is conditional and behavioral: per-partner affective precision
is a model-fitness signal, and it becomes visible only when the policy space has
room for precision to change selection. Whole-run payoff is therefore a
downstream readout, not the first diagnostic.

The current card order is:

1. **H0 Openness Gate**: can precision move policy here?
2. **H1 Model Fitness**: does precision track predictability rather than reward?
3. **H2 Deployment**: can the agent use what it knows?
4. **H3 Stress Response**: do volatility windows amplify the mechanism?
5. **H4 Social Choice**: does precision guide approach, avoidance, probing, and
   return?
6. **H5 Perturbation Phenotypes**: do clinical-like parameter changes first
   separate in precision dynamics, then behavior?

---

## 2. POMDP Structure

### 2.1 State Space Factorization

The generative model is best understood as a single hidden-state inference problem plus an auxiliary affective summary:

**Level 1 — Trial State** $s^{(1)}_t$
The current-round game context is task-given:
- which partner is currently interacting
- the partner's action on this trial: {Cooperate, Defect}

This is directly observed in the main experiments (or noisily observed in later variants — see Section 3.3). It is not treated as a latent factor in the shipped binary-action setup.

**Level 2 — Partner Type** $s^{(2)}_k$
Each partner's latent strategy type, drawn from:
- **Cooperator**: cooperates with probability 0.9
- **Reciprocator**: mirrors the agent's previous action with probability 0.85
- **Exploiter**: cooperates initially (first 3-5 rounds) then defects with probability 0.85
- **Random**: cooperates with probability 0.5

Types are stable within blocks but switch at geometrically-distributed intervals (expected block length ~20 rounds). The agent does not observe type switches directly.

**Level 3 — Affective State** $\beta_k$ (for affective agents only)
A discrete HESP-style auxiliary state per partner representing the **rate parameter** of expected policy precision. Default levels are `[0.5, 0.67, 1.0, 1.5, 2.0]`, with `\beta_k = 1.0` as the baseline prior. Lower beta means higher expected precision and more decisive policy selection when precision modulation is enabled.

### 2.2 Observation Model (A matrix)

Observations consist of:
- **Partner action**: Cooperate or Defect (observed directly)
- **Own payoff**: determined by the game payoff matrix (observed directly)

For the basic version, observations are noise-free — the agent sees exactly what the partner did. A later variant can add observational noise (misreading partner actions) to test whether affective precision also aids robustness to sensory uncertainty.

The A matrix maps hidden states (partner type × context) to observations (partner action × payoff):

$$P(o_t | s^{(1)}_t, s^{(2)}_k) = \text{determined by type-specific cooperation probabilities}$$

### 2.3 Transition Model (B matrix)

**Level 1 transitions**: depend on the agent's action and partner's type.

**Level 2 transitions**: partner types are mostly stable (identity transition with probability 0.95) but switch with probability 0.05 per trial to a uniformly random new type. This creates the volatility that makes the task nontrivial.

$$P(s^{(2)}_{k,t+1} | s^{(2)}_{k,t}) = (1 - p_{\text{switch}}) \cdot \mathbb{I}[s' = s] + p_{\text{switch}} \cdot \text{Uniform}(S^{(2)})$$

Important implementation note: this stochastic type switching is separate from the exploiter's internal `switch_round`. `p_switch` governs when a partner changes latent type altogether; `switch_round` only governs when an **exploiter-type** partner changes from its early cooperative phase to its later exploitative phase after repeated interactions.

**Level 3 transitions (affective state)**: in the default path, beta updates via a discrete predict-then-correct filter over the HESP beta levels using interoceptive observations derived from surprise.

### 2.4 Preference Model (C matrix)

The agent has prior preferences over observations defined by the payoff matrix of a Trust Game variant:

|  | Partner Cooperates | Partner Defects |
|---|---|---|
| **Agent Cooperates** | +3 / +3 (mutual cooperation) | -1 / +5 (sucker's payoff) |
| **Agent Defects** | +5 / -1 (temptation) | +1 / +1 (mutual defection) |

Prior preferences are specified as a log-probability vector over observations:

$$\ln P(o) \propto \text{payoff}(o)$$

This creates the standard tension: mutual cooperation is collectively optimal but unilateral cooperation is individually risky. The agent prefers high payoffs, so cooperation is preferred *when the partner is expected to cooperate* and defection is preferred otherwise.

### 2.5 Policy Space and Planning Horizon

**Actions**: {Cooperate, Defect} per round, for each partner interaction.

**Planning horizon**: varies by explicit variant (`planning_horizon`).
- Deeper planners can evaluate up to 8 steps ahead in benchmark comparisons.
- Shallow planners use shorter horizons such as 1 or 2 steps.

**Policy evaluation**: official `pymdp.Agent.infer_policies(...)` computes the policy posterior over the task-local policy set built by `tasks.trust.pomdp`. The repository-owned code constructs the matrices and partner-local priors, but policy inference itself is native pymdp rather than a custom rollout engine. For affective runtimes, the external beta tracker sets the active partner's precision before inference as `gamma_k = gamma_base / E[beta_k]`; no separate shallow-EFE multiplier is applied.

### 2.6 Affective State Update (Level 3 Implementation)

After each trial with partner $k$, the external beta tracker is updated from the partner-action prediction error:

```
# After observing partner k's action at time t:
prediction = E[o_t | current posterior over s^(2)_k]
actual = o_t
surprise_k = 1 - prediction[actual]               # unsigned surprise of what happened
sq_surprise = surprise_k^2

# Affective charge: positive if model is accurate, negative if not
charge = alpha * (sigma_0^2 - sq_surprise)

# Discrete predict-then-correct beta update
prior_beta = T_beta @ q(beta_k)
q(beta_k) = normalize(likelihood(charge | beta_k) * prior_beta)
E_beta_k = dot(q(beta_k), beta_levels)

# Policy precision for the next decision involving partner k
gamma_k = gamma_base / E_beta_k
```

Parameters:
- `beta_persistence = 0.8` — persistence in the tridiagonal beta transition matrix; higher values make precision estimates more inertial
- $\alpha = 3.0$ — charge sensitivity; expands the sigmoid operating range so correct vs. incorrect predictions separate betas materially
- $\sigma_0^2$ — baseline expected squared surprise; default `0.25` matches a random binary partner because $(1 - 0.5)^2 = 0.25$
- `initial_beta = 1.0` and beta levels `[0.5, 0.67, 1.0, 1.5, 2.0]` define the default discrete support

The beta state remains outside the POMDP hidden-state factors. It is a task-local HESP precision tracker used to set native pymdp policy precision before the next partner-local `infer_policies(...)` call.

---

## 3. Environment and Task

### 3.1 Multi-Partner Trust Game

The agent interacts with $K = 4$ partners over $N = 200$ rounds. Each round:

1. A partner is selected (either randomly assigned or agent-chosen — see Variant 3.4)
2. The agent and partner choose Cooperate or Defect (the implementation evaluates the agent's action first inside the simulation loop, but because both actions are resolved against the same round payoff matrix with no within-round reaction term, this is strategically equivalent to simultaneous choice)
3. Payoffs are determined by the Trust Game matrix
4. The agent observes the partner's action and updates beliefs

Partners' hidden types switch according to the geometric distribution ($p_{\text{switch}} = 0.05$ per trial). The agent must learn partner types, track changes, and choose actions to maximize cumulative payoff.

### 3.2 Why This Task

This task is chosen to satisfy several requirements:

- **Multi-partner**: forces the agent to maintain separate models (and potentially separate affective states) for each partner, stressing computational resources.
- **Sequential and volatile**: partner types change, so the agent must continuously update rather than converging to a fixed strategy. This is where partner-specific confidence signals and post-switch adaptation should matter most.
- **Social structure**: the Trust Game payoff matrix creates a genuine social dilemma where understanding partner types is essential for good decisions.
- **Minimal**: 2 actions, 4 partner types, 4 partners — small enough for exact
  or near-exact POMDP solutions at depth 8.

### 3.3 Task Variants

**Variant A: Fixed partner assignment (baseline)**
Each round, the partner is randomly assigned. The agent has no choice over who to interact with — only what action to take. This isolates the cooperate/defect decision from partner selection.

**Variant B: Partner selection**
Each round, the agent chooses which of the 4 partners to interact with, then chooses cooperate/defect. This adds a second action dimension and tests whether affective states also guide partner selection (approach trustworthy partners, avoid or probe untrustworthy ones). Partner selection is where affect should have the strongest effect — choosing who to engage with is a higher-level decision that benefits most from compressed interaction summaries.

**Variant C: Noisy observations**
Partner actions are observed with 10% noise (cooperation misread as defection and vice versa). This tests whether affective inertia provides robustness to observational noise — the slow affective state should smooth over misperceptions that would destabilize a fast belief-only system.

**Variant D: Correlated partners (for structure learning extension)**
Two of the four partners are secretly correlated — partner C copies partner B's action with 90% probability. This tests whether affective signals can detect structural relationships: the agent should notice that its model of C is suspiciously well-predicted by its model of B, signaling coalition structure. This variant connects to the BMR/structure learning direction.

**Variant E: Betrayal stress test**
Use agent-chosen partners, disable stochastic type switches (`p_switch = 0`), seed a clearly cooperative partner at the start of the episode, then force a scheduled switch from `cooperator` to `exploiter` mid-episode. The key readout is payoff, action choice, and inferred-type accuracy in the first 5-10 encounters after the betrayal event. This is the cleanest way to separate precision tracking from reward averaging, because the partner's past reward history remains attractive while the predictive model becomes sharply wrong.
The repository now treats this as the primary diagnostic benchmark for variant comparison because it is the most direct test of whether per-partner beta dynamics do computational work beyond cached value.

---

## 4. Experiment Specs And Variants

Maintained trust experiments use the hierarchy:

```text
hypothesis -> experiment -> scenario -> variants -> sweeps -> replications -> rounds
```

Core variant fields include:

- `affect = "none"` for the base runtime
- `affect = "precision"` for the normal discrete-beta precision runtime
- `affect = "tracked_only"` for the lesion where beta updates continue but policy precision remains at baseline
- `planning_horizon`
- `epistemic_value`
- affect hyperparameters such as `alpha_charge`, `sigma_0_sq`, `initial_beta`,
  `beta_persistence`, and explicit `beta_levels`

Reward averaging and variational beta are not part of the runnable supported
surface.

---

## 5. Behavior Cards and Predictions

The canonical hypothesis surface is the behavior-card spine in
`docs/theory/hypotheses.md`. The cards are ordered by the agent's causal
timeline: first check whether precision can move policy, then test what the
signal tracks, whether it is partner-local, and how it affects behavior under
normal choice, stress, and perturbation regimes.

### H0: Openness Gate

**Prediction:** Affect can only change behavior when the policy posterior has
room to move.

**Expected behavior:** In saturated binary regimes, beta or `precision_k` may
move without changing action. In shallow, graded, volatile, noisy, or
agent-choice regimes, affect should shift the policy posterior and may change
action or partner selection.

**Primary metrics:**
- `q_pi_entropy`
- `G_spread`
- best-vs-second-best EFE gap
- policy-posterior shift, for example `KL(q_pi_affect || q_pi_no_affect)`

**Failure mode:** Affect has no behavioral effect even when H0 diagnostics show
an open policy regime, or effect sizes are unrelated to policy openness.

### H1: Model Fitness

**Prediction:** Per-partner precision tracks predictive reliability more than
reward history.

**Expected behavior:** Reliable cooperators and reliable exploiters should both
produce high precision. Volatile allies and random partners should produce low
or unstable precision. A predictable exploiter should be confidently avoided,
defected against, or disengaged from, not treated as rewarding.

**Primary metrics:**
- `precision_k = 1 / E[beta_k]`
- predictive accuracy or predictive log score
- surprise
- partner reward
- partial models such as `precision_k ~ predictive_accuracy + reward`

**Failure mode:** Precision mostly tracks average payoff, collapsing the
mechanism into cached value.

### H2: Deployment

**Prediction:** Lesioning the beta-to-policy pathway should preserve partner
inference while impairing action deployment.

**Expected behavior:** Lesioned agents should infer type and stance about as well
as affective agents, but should be worse at choosing partners, recovering after
betrayal, or selecting cooperate/defect actions in open policy regimes.

**Primary metrics:**
- type/stance belief accuracy
- predictive log score
- `KL(q_s_affect || q_s_lesion)`
- `KL(q_pi_affect || q_pi_lesion)`
- payoff, recovery latency, and partner-choice shift

**Failure mode:** Lesion damages inference itself, or lesion and affect behave
identically when H0 indicates that precision could have changed policy.

### H3: Stress Response

**Prediction:** Betrayal, stance shifts, noisy observation, or partner volatility
should amplify affect's behavioral role.

**Expected behavior:** Around a hostile switch, the affective agent should show a
surprise spike, precision drop for the affected partner, faster policy change,
and faster recovery or reallocation.

**Primary metrics:**
- post-switch payoff windows
- surprise spike
- partner-specific precision reaction time
- recovery latency
- partner reallocation
- belief recalibration

**Failure mode:** Affect effects are not amplified by volatility, or whole-run
and post-switch effects are both flat.

### H4: Social Choice

**Prediction:** Partner-specific precision should guide approach, avoidance,
probing, and return in agent-choice settings.

**Expected behavior:** Partner choice should be systematically related to both
precision and expected value. High precision does not always imply approach: a
reliable exploiter should be avoided or defected against, while uncertain
partners may be probed when epistemic value is useful.

**Primary metrics:**
- selection entropy
- `P(select k)` as a function of `precision_k x expected_payoff_k`
- avoidance of reliable exploiters
- probing rate for uncertain partners
- return latency to recovered partners

**Failure mode:** Partner choice is unrelated to partner-local precision.

### H5: Perturbation Phenotypes

**Prediction:** Clinical-like variants should separate first in beta/precision
dynamics and only then in behavior, and mainly in open policy regimes.

**Expected behavior:** Alexithymia-like settings blunt precision updates;
borderline-like settings create fast precision swings; depression-like settings
start low-confidence; slow-updating settings lag after real changes.

**Primary metrics:**
- precision mean, variance, autocorrelation, and reaction time
- partner-selection entropy
- action-flip rate
- post-betrayal recovery latency
- payoff after precision dynamics are confirmed

**Failure mode:** Behavior differs without the intended precision dynamics, or
precision dynamics do not differentiate.

### Future Work: Predictive Model Comparison

Predictive scoring of affective versus non-affective generative models remains
future work. It should be evaluated on matched observation sequences and kept
separate from the main H0-H5 behavior-card spine. A separate variational beta
model would require new implementation and tests; the supported runtime uses a
task-local discrete beta tracker outside the POMDP state space.

### Future Work: Global-Beta Ablation

Partner-specific beta is part of the current architecture. A future optional
ablation can compare it with a single shared beta state, but that comparison is
not part of the current core hypothesis spine.

---

## 6. Implementation Plan

### 6.1 Framework

Primary implementation uses official `inferactively-pymdp==1.0.0` for active-inference policy inference. Project-owned trust-game modules construct the POMDP matrices, wrap `pymdp.Agent`, and maintain affective beta as an external per-partner precision tracker that modulates policy evaluation without becoming part of the generative model.

Reference implementation: Hesp et al.'s "Deeply Felt Affect" code (https://github.com/CasperHesp/deeplyfeltaffect) for the single-agent affective architecture. This will be extended to the multi-partner setting.

### 6.2 Simulation Parameters

| Parameter | Value | Justification |
|---|---|---|
| Partners ($K$) | 4 | Large enough for meaningful partner selection, small enough for tractable computation |
| Rounds ($N$) | 200 | Long enough for multiple type switches and learning |
| Type switch probability ($p_{\text{switch}}$) | 0.05/trial | Expected block length ~20 rounds |
| Partner types | 4 (Cooperator, Reciprocator, Exploiter, Random) | Covers key strategic diversity |
| Deep planning horizon | 8 | Sufficient for ~optimal play in this game |
| Shallow planning horizon | 2 | Minimal deliberation |
| Intermediate planning horizons | 3, 4 | Additional explicit variant depth-comparison points |
| Beta persistence | 0.8 | Tridiagonal persistence for the discrete beta posterior; higher values make beta less reactive |
| Beta levels | `[0.5, 0.67, 1.0, 1.5, 2.0]` | HESP-style inverse-beta support for partner-local precision |
| Policy precision | `gamma_base / E[beta_k]` | Native pymdp policy precision set before each partner-local policy inference |
| Replications per variant | 100 | Sufficient for reliable statistics |

### 6.3 Analysis Plan

Primary analysis follows the H0-H5 behavior cards rather than whole-run payoff
alone.

**Gate analysis first**:
- policy entropy, `G_spread`, and best-vs-second-best EFE gap
- policy-posterior shifts where matched comparisons are available
- stratification of behavioral effects by policy-space openness

**Mechanism analyses**:
- H1: regress or correlate `precision_k = 1 / E[beta_k]` against predictive
  accuracy, surprise, and reward
- H2: compare belief accuracy and predictive log score against policy and
  behavior shifts in lesioned runs

**Behavior analyses**:
- H3: use post-switch windows and recovery latencies, not whole-run payoff alone
- H4: model partner selection as a function of precision and expected value
- H5: verify beta/precision dynamics before interpreting payoff or action
  differences

**Supplementary analyses**:
- cumulative payoff ANOVA and pairwise tests remain useful summaries, but they
  are downstream of the mechanism and gate checks
- sensitivity sweeps over `alpha_charge`, `sigma_0_sq`, `beta_persistence`,
  `initial_beta`, and `p_switch`

**Execution workflow note**:
- `scripts/experiment/run.py` accepts repeated `--config` flags and a shared
  `--workers` pool so multiple TOML experiment specs can be queued in one
  invocation.
- Outputs are written per experiment under
  `<output-dir>/<batch-name>/<hypothesis-id>/<experiment-id>/results.csv`; use
  the layout in `docs/experiments/manifest.md`.
- Current maintained specs are listed in `docs/experiments/manifest.md`.

### 6.4 Visualizations

Key figures should mirror the behavior cards:

1. **Openness gate**: `q_pi_entropy`, `G_spread`, and EFE gap by horizon and
   task regime.
2. **Model fitness**: `precision_k = 1 / E[beta_k]` against predictive accuracy,
   surprise, and reward for stable-good, stable-bad, volatile, and random
   partners.
3. **Deployment dissociation**: belief accuracy versus behavior for affective
   and lesioned runs; the expected pattern is similar beliefs but different
   policy or choice behavior.
4. **Stress response**: post-switch windows for surprise, precision, payoff, and
   recovery latency.
5. **Social choice**: partner-selection probability as a function of precision
   and expected value.
7. **Perturbation phenotypes**: beta/precision mean, variance, autocorrelation,
   and reaction time before payoff interpretation.

### 6.5 Implementation Timeline (Completed)

These phases describe the original build sequence. For future research phases (theory tightening, variational beta, clinical sensitivity, model comparison, richer tasks, human data), see the Phase Roadmap in Section 8.5.

| Phase | Tasks | Duration | Status |
|---|---|---|---|
| Build 1 | Implement basic multi-partner POMDP in the repository's JAX-first stack | 2 weeks | Done |
| Build 2 | Implement affective state and partner-local precision modulation | 1-2 weeks | Done |
| Build 3 | Implement lesion and reward-comparison variants | 1 week | Done |
| Build 4 | Run primary simulations (Variant A, explicit variants, 100 replications) | 1 week | Done |
| Build 5 | Analysis and visualization of primary results | 1 week | Done |
| Build 6 | Run Variants B, C, D | 2 weeks | Partial (B, E done) |
| Build 7 | Sensitivity analyses and parameter sweeps | 1 week | Partial (horizon sweep done) |
| Build 8 | Write-up | 2-3 weeks | In progress |

### 6.6 Current Empirical Status

Current evidence requires completed runs on the native pymdp,
apashea-aligned, factorized-control architecture, with provenance recorded under
`docs/results/`. Partial outputs can motivate experiment design, but completed
current-architecture runs are required for current evidence.

Current pre-run scorecard:

| Card | Current reading | Status |
|---|---|---|
| H0 Openness Gate | Must be checked before interpreting any payoff or choice null; saturated binary regimes can hide precision effects. | Verification rerun pending |
| H1 Model Fitness | Needs a stable-good/stable-bad/volatile/random test that dissociates predictability from reward. | Config exists; rerun pending |
| H2 Deployment | Lesion tests should focus on open policy regimes and compare beliefs against policy/behavior shifts. | Config exists; rerun pending |
| H3 Stress Response | Betrayal should be read in post-switch windows, not whole-run payoff alone. | Config exists; rerun pending |
| H4 Social Choice | Agent-choice mode is likely the clearest behavioral readout; choice/reweighting is primary and payoff is secondary. | Config exists; rerun pending |
| H5 Perturbation Phenotypes | Clinical-like variants are exploratory; beta/precision dynamics must separate before behavior is interpreted. | Configs exist; rerun pending |

Interpretation guardrails:

- Do not update result-interpretation docs from new outputs without user
  approval.
- Interpret behavioral nulls through H0 before weakening a mechanism claim.

For the current run queue, see `docs/state/current/next_runs.md`.

---

## 7. Outcome Interpretation Rules

Until current-architecture reruns are complete, this section records how to
interpret future outcomes rather than claiming resolved results.

### 7.1 Positive Mechanism Pattern

The strongest pattern would show the full chain:

```text
predictive reliability -> precision_k -> policy shift -> behavior
```

This requires more than payoff. H1 should show precision tracking predictive
accuracy rather than reward. H0 should show the policy space is open. H2-H4
should then show policy, action, recovery, or partner-choice shifts.

### 7.2 Gate-Limited Null

If beta/precision moves but policy entropy is near zero and behavior is flat,
the result supports the H0 gate rather than falsifying the whole mechanism. The
next step is a more open regime, not a stronger payoff claim.

### 7.3 Mechanism Null

If H0 diagnostics show an open policy regime and affect still does not shift
policy, action, recovery, or partner choice, then the deployment mechanism needs
reframing.

### 7.4 Reward-Collapse Failure

If precision mostly tracks average payoff, the theory collapses toward cached
value. H1 is the protection against that failure.

### 7.5 Optional Factorization Failure

If a global beta ablation performs as well as per-partner beta, the strong
multi-agent factorization claim should be weakened until a task demonstrates
partner-local advantage. This is future model comparison, not a current H0-H5
failure condition.

---

## 8. Extensions and Future Directions

### 8.1 From Simulated Affect to Fitted Behavior (Phase 8: Human Data)

Fit the model to human behavioral data from multi-partner trust games. Estimate `beta_persistence` (affective timescale), `alpha_charge` (prediction-error gain), `initial_beta` (precision prior), and the policy-precision channel as individual-difference parameters. Test whether estimated affective parameters correlate with self-reported emotional awareness, interoceptive accuracy, or alexithymia scores.

### 8.2 Bridge to Structure Learning (Phase 7: Richer Tasks)

Implement Bayesian Model Reduction triggered by persistent low $\beta_k$. When the affective state for partner $k$ remains below a threshold despite ongoing parameter learning, launch BMR over alternative social model structures (partner types, coalition structures, domain-specific reliability). Test whether this accelerates discovery of non-trivial social structures compared to untriggered BMR.

**Critical analysis warning**: The trigger-based BMR formulation needs reformulation before it can be used for predictive model comparison. Using affect thresholds to trigger structural changes conflates the affective signal with the model selection process, making it impossible to cleanly evaluate whether affect improves predictive score. A cleaner approach would separate the BMR machinery from the affective trigger and compare triggered vs. untriggered BMR as competing model-selection strategies, rather than embedding the trigger in the generative model itself.

### 8.3 Developmental Bootstrapping (Phase 7: Richer Tasks)

Initialize agents with no prior knowledge and simulate the full developmental trajectory: from exploration-heavy behavior (all partners are novel → low precision → high epistemic drive) through gradual affective differentiation (partners become differentially predictable) to a mature state with stable partner-specific affective profiles. Compare the learning trajectory to developmental findings on children's trust calibration.

**Critical analysis warning**: Learning rate modulation based on $\beta$ (e.g., increasing learning rate when precision is low) creates a positive feedback loop risk: low $\beta$ increases learning rate, which increases belief volatility, which increases surprise, which further lowers $\beta$. Any extension that couples $\beta$ to the learning dynamics must include stability analysis or damping to prevent runaway oscillation. The supported discrete beta path is safer than a raw feedback loop because it keeps the precision signal in a bounded posterior update rather than feeding directly into learning-rate control.

### 8.4 Clinical Parameter Sensitivity Analysis (Phase 5)

Vary model parameters to probe clinically relevant behavioral signatures:
- **Alexithymia** ($\alpha \to 0$): attenuated affective charge, near-flat beta trajectories
- **Borderline patterns** (high $\alpha$ + low beta persistence): intense, volatile affective states
- **Depression** (low $\beta_0$): chronically low precision estimates, reduced engagement
- **Anxiety**: increased epistemic drive weighting when $\beta_k$ is low (uncertainty triggers excessive information-seeking)

**Critical analysis warning**: These are sensitivity analyses, not a unified clinical framework. The parameter-to-phenotype mappings are illustrative and should not be interpreted as validated clinical models. The configs exist for H5 Perturbation Phenotypes, but moving from sensitivity analysis to clinical modeling requires: (a) fitting to human behavioral data, (b) formal model comparison showing the affective model outperforms simpler alternatives on clinical populations, and (c) demonstrating that the parameter variations are identifiable from behavioral data alone rather than being degenerate with other model parameters.

### 8.5 Graded Investment Trust Game

The graded investment trust game replaces the binary cooperate/defect action with 6 investment levels (0%, 20%, 40%, 60%, 80%, 100% of endowment), creating 24 actions per step (6 levels × 4 partners). This produces q_pi_entropy ~5.8 (vs <0.01 in binary), activating the precision modulation channel that was structurally inert in the binary game due to softmax saturation.

**Current status**: Graded configs exist in the maintained experiment surface as
H0 precision-channel tests.

### 8.6 Phase Roadmap

| Phase | Description | Dependencies | Status |
|---|---|---|---|
| Phase 3 | Theory tightening: formalize the H0-H5 behavior cards and expected behavior | Current docs | In progress |
| Phase 4 | Discrete beta: supported task-local `DiscreteBetaState` | Phase 3 | Supported native helper |
| Phase 5 | Clinical sensitivity: rerun perturbation phenotypes after H0-H5 are checked | H0-H5 reruns | Planned |
| Phase 6 | Model comparison: predictive log score comparison outside the main H0-H5 spine | Phase 4 | Future work |
| Phase 7 | Richer tasks: graded action spaces, noisy observations, structure learning | Phase 3 | Maintained configs; rerun pending |
| Phase 8 | Human data: fit to behavioral data, estimate individual-difference parameters | Phases 5-7 | Planned |

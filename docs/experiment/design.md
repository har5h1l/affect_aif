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
4. **H3 Locality / Global Precision**: does partner-local beta preserve cleaner
   model-fitness signals than a shared global tracker?
5. **H4 Social Allocation**: does precision guide approach, avoidance, probing,
   and return?
6. **H5 Timescale / Volatility**: when does social change outrun confidence
   calibration?
7. **H6 Perturbation Phenotypes**: do clinical-like parameter changes first
   separate in precision dynamics, then behavior?
8. **H7 Signal Source**: does partner-action surprisal remain cleaner than
   exploratory joint action-plus-payoff surprisal?
9. **H8 Observation Noise / Robustness**: does beta inertia stabilize or slow
   behavior under noisy social observations?

---

## 2. POMDP Structure

### 2.1 State Space Factorization

The supported trust-game generative model is the `type x stance x own_action`
POMDP specified in `docs/theory/pomdp_spec.md`.

**Partner type** is the partner's latent behavioral category: cooperator,
reciprocator, exploiter, or random. Type can drift stochastically when
`p_switch > 0`, and explicit scheduled type switches remain supported only for
experiments about exogenous type volatility.

**Partner stance** is the partner's disposition toward the focal agent:
trusting, neutral, or hostile. Stance is hidden, action-dependent, and is the
supported surface for betrayal-style experiments via `scheduled_stance_switches`.

**Own action** is a deterministic bookkeeping factor over the action or
investment level chosen by the focal agent. It lets the payoff modality remain
a standard pymdp likelihood conditioned on `own_action x type x stance`.

The affective beta state is not a hidden factor in this POMDP. It is a
per-partner auxiliary precision tracker outside the generative model.

### 2.2 Observation Model (A matrix)

Observations consist of:
- **Partner action**: Cooperate or Defect (observed directly)
- **Own payoff**: determined by the game payoff matrix (observed directly)

For the basic version, observations are noise-free — the agent sees exactly what the partner did. A later variant can add observational noise (misreading partner actions) to test whether affective precision also aids robustness to sensory uncertainty.

The A matrices map hidden `type x stance x own_action` states to observations:
partner action is generated from the `type x stance` cooperation table, and
payoff is generated from `own_action x type x stance` with the partner action
marginalized through that table.

### 2.3 Transition Model (B matrix)

**Type transitions** are mostly stable, with optional stochastic drift:

$$P(s^{(2)}_{k,t+1} | s^{(2)}_{k,t}) = (1 - p_{\text{switch}}) \cdot \mathbb{I}[s' = s] + p_{\text{switch}} \cdot \text{Uniform}(S^{(2)})$$

**Stance transitions** are action-dependent. Cooperating tends to build or
repair trust; defecting tends to push stance toward hostile. Scheduled stance
switches are applied at the start of configured rounds for betrayal tests.

**Own-action transitions** are deterministic on the executed own-action control.

**Affective beta transitions** are handled outside the POMDP by a discrete
predict-then-correct filter over HESP beta levels. The tracker reads partner
action prediction error and then modulates the next policy precision.

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

**Actions**: binary games use cooperate/defect; graded games use configured
investment levels. In both modes, partner-local pymdp policies use factorized
stance and own-action controls. Agent-choice runs evaluate each partner-local
agent and perform partner selection in `tasks.trust.runtime.select_decision`.

**Planning horizon**: varies by explicit variant (`planning_horizon`).
- Deeper planners can evaluate up to 8 steps ahead in benchmark comparisons.
- Shallow planners use shorter horizons such as 1 or 2 steps.

**Policy evaluation**: official `pymdp.Agent.infer_policies(...)` computes the policy posterior over the task-local policy set built by `tasks.trust.pomdp`. The repository-owned code constructs the matrices and partner-local priors, but policy inference itself is native pymdp rather than a custom rollout engine. For affective runtimes, the external beta tracker sets each partner's precision before inference as `gamma_k = gamma_base / E[beta_k]`; no separate shallow-EFE multiplier is applied.

### 2.6 Affective State Update

After each trial with partner $k$, the external beta tracker is updated from the partner-action prediction error:

```
# After observing partner k's action at time t:
prediction = E[o_t | current posterior over partner-local type x stance]
actual = o_t
surprise_k = -log(prediction[actual])             # Hesp-style surprisal
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
- $\sigma_0^2$ — baseline expected squared surprise; default `(-log 0.5)^2` matches a maximally uninformative binary prediction.
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
Use agent-chosen partners, disable stochastic type switches (`p_switch = 0`),
seed a clearly cooperative/trusting partner at the start of the episode, then
force a scheduled hostile stance switch mid-episode. The key readouts are
post-switch action deployment, partner avoidance/reallocation, return latency,
payoff conditional on re-encounter, and low-entropy wrong-belief or wrong-action
deployment. Whole-run payoff remains a downstream diagnostic rather than the
stress-response claim by itself.
The repository now treats this as the primary diagnostic benchmark for whether
per-partner beta dynamics do computational work beyond cached value and where
that work can become maladaptive under volatility.

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

**Controlled diagnostic path:** The first confirmation read remains the
corrected active-encounter analysis on the current H1 setup. If reward,
surprise, and encounter count remain coupled, use a balanced-exposure reliability
spine before adding seeds: random assignment, fixed partner roster, custom
partner action probabilities for reliable cooperator, reliable exploiter,
random, and stance-sensitive partners, and the corrected partial-correlation
readouts. The manuscript-consistent diagnostic is the graded spine; the stricter
reward-neutral binary spine is an escalation test that removes partner-dependent
reward entirely. Passing the strict diagnostic but failing the graded spine
would identify a task-design/readout confound rather than a failure of the
affective precision mechanism.

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

### H3: Locality / Global Precision

**Prediction:** Partner-local beta preserves relationship-specific
model-fitness evidence better than a shared global beta tracker.

**Expected behavior:** Local beta should preserve the strongest partner-level
precision-surprise signature. Global beta may produce useful aggregate behavior,
but should mix evidence across partners and can perturb decisions about
untouched partners after a localized shock.

**Primary metrics:**
- global beta versus partner-local beta or terminal signal
- partner-level precision-surprise and precision-payoff associations
- selected-partner distribution
- policy entropy and payoff conditional on selected partner
- cross-partner interference after a localized switch

**Failure mode:** Global beta matches partner-local beta on signal quality,
allocation, and post-shock interference, suggesting the current partner-local
implementation is interpretable but not necessary under this task design.

### H4: Social Allocation

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

### H5: Timescale / Volatility

**Prediction:** Betrayal, stance shifts, noisy observation, or partner volatility
should amplify affect's behavioral role. The sign of that role depends on
whether partner beliefs and beta stay temporally aligned.

**Expected behavior:** Around a hostile switch, the affective agent should show a
surprise spike, precision drop for the affected partner, faster policy change,
and either faster recovery/reallocation or a diagnosable misdeployment boundary
condition when precision sharpens a wrong post-switch model.

**Primary metrics:**
- post-switch payoff windows
- surprise spike
- partner-specific precision reaction time
- recovery latency
- partner reallocation
- return latency to the switched partner
- payoff conditional on re-encounter
- low-entropy wrong action or wrong-belief deployment
- belief recalibration

**Failure mode:** Affect effects are not amplified by volatility across both
recovery/reallocation readouts and misdeployment readouts.

### H6: Perturbation Phenotypes

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

### H7: Signal Source

**Prediction:** Partner-action surprisal should preserve the model-fitness
dissociation better than joint action-plus-payoff surprisal.

**Expected behavior:** A joint signal may become more reward-like because payoff
is downstream of both partner action and the focal agent's action. Partner-action
surprisal should keep a predictable exploiter high precision despite low payoff.

**Current status:** Exploratory. The supported runtime uses partner-action
surprisal; joint surprisal would require explicit implementation and tests.

### H8: Observation Noise / Robustness

**Prediction:** Beta inertia can stabilize behavior under noisy observations,
but may slow adaptation if noise resembles real partner change.

**Expected behavior:** Moderate observation noise should reduce the reliability
of trial-level beliefs. A useful affective channel should dampen action churn
without erasing real stance-switch responses.

**Current status:** Exploratory. Observation noise is supported in scenario
configs, but this lane is not required for the manuscript argument.

### Future Work: Predictive Model Comparison

Predictive scoring of affective versus non-affective generative models remains
future work. It should be evaluated on matched observation sequences and kept
separate from the main H0-H8 behavior-card spine. A separate variational beta
model would require new implementation and tests; the supported runtime uses a
task-local discrete beta tracker outside the POMDP state space.

### Global-Beta Ablation

Partner-specific beta is part of the current architecture. The supported
`global_beta` condition compares it with a single shared beta state while
keeping partner-local POMDP beliefs intact. The current core H0-H6 configs now
include this condition where relevant, and focused H3 configs retain the
cross-partner interference diagnostics.

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
| Replications per variant | Declared per TOML spec | Current post-fix evidence uses three-seed smoke for H0-H6 plus targeted diagnostics; confirmation-scale reruns should use 30+ seeds when promoted to manuscript claims |

### 6.3 Analysis Plan

Primary analysis follows the H0-H8 behavior cards rather than whole-run payoff
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
- H3: compare local beta and global beta on partner-level signal quality and
  cross-partner interference after localized shocks
- H4: model partner selection as a function of precision and expected value;
  flat payoff can still accompany meaningful approach, avoidance, or probing
  changes
- H5: use pre-switch, acute post-switch, and post-acute tail phase summaries,
  post-switch windows, return/reallocation summaries, recovery latencies, and
  low-entropy wrong-deployment summaries; whole-run payoff is a downstream
  diagnostic, not the timescale claim by itself
- H6: verify beta/precision range, volatility, autocorrelation, action churn,
  partner-selection entropy, and recovery timing before interpreting payoff or
  clinical-like labels

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
- Analysis outputs include generic final-round, movement, deployment,
  partner-choice, and phenotype-validation summaries. Betrayal-style runs also
  write post-switch windows, phase summaries, detection/recovery latency, and
  per-encounter trajectories.
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

### 6.5 Implementation Timeline

These phases describe the original build sequence and current documentation
phase. Older phase labels are historical; current empirical claims use the H0-H8
behavior cards and the provenance recorded in `docs/results/`.

| Phase | Tasks | Duration | Status |
|---|---|---|---|
| Build 1 | Implement basic multi-partner trust-task POMDP | 2 weeks | Done |
| Build 2 | Implement affective state and partner-local precision modulation | 1-2 weeks | Done |
| Build 3 | Implement lesion, no-affect, and clinical-like perturbation variants | 1 week | Done |
| Build 4 | Cut over to official `inferactively-pymdp==1.0.0` and factorized controls | 1 week | Done |
| Build 5 | Run current H0-H8 queue and targeted confirmation runs | 1 week | Historical pre-log-surprisal queue done; post-fix confirmations pending |
| Build 6 | Analysis and result documentation | 1 week | Current active-document surface maintained |
| Build 7 | Write-up stabilization and phenotype experiments | 2-3 weeks | Current phase |

### 6.6 Current Empirical Status

Current evidence comes from completed runs on the native pymdp,
factorized-control architecture, with provenance recorded in
`docs/results/current.md`, `docs/results/runs/`, and the active handoff under
`docs/active/`. Pre-log-surprisal confirmations remain historical context; the
post-fix log-surprisal H0-H6 run is smoke evidence, not publication-grade
confirmation.

Current scorecard:

| Card | Current reading | Status |
|---|---|---|
| H0 Openness Gate | Affect has little room in shallow binary settings, but lowers entropy and can improve payoff in graded choice. Open policy space is necessary but not sufficient; graded betrayal shows lower entropy with worse payoff. | Supported with caveat |
| H1 Model Fitness | Corrected active-encounter and partial-correlation smoke readouts show surprise-over-reward dominance; confirmation or controlled diagnostic escalation is still required before manuscript use. | Smoke-supported; confirm |
| H2 Deployment | In the open graded-choice regime, affect and lesion/no-affect have similar belief accuracy while affect changes entropy and payoff. | Supported |
| H3 Locality / Global Precision | Discovery runs show local beta preserves a cleaner model-fitness signal than global beta, but global beta can have higher aggregate payoff in small probes. | Open decomposition |
| H4 Social Allocation | Affect changes partner-selection distribution and policy entropy while payoff is essentially flat. | Supported behaviorally |
| H5 Timescale / Volatility | Confirmation and sensitivity runs show abrupt shocks can produce precision-driven misdeployment, while gradual shocks are less harmful. | Boundary condition confirmed |
| H6 Perturbation Phenotypes | Clinical-like variants separate in beta range, entropy, partner selection, and payoff ordering, but five-seed payoff tests are underpowered. | Supported for dynamics |
| H7 Signal Source | Partner-action surprisal is canonical; joint action-plus-payoff surprise is future work. | Exploratory |
| H8 Observation Noise / Robustness | Observation-noise configs are possible but not part of current manuscript evidence. | Exploratory |

Interpretation guardrails:

- Do not update result-interpretation docs from new outputs without user
  approval.
- Interpret behavioral nulls through H0 before weakening a mechanism claim.
- Treat H3 as a stress boundary-condition result, not as a clean affective
  recovery win.

The immediate run queue is governed by `docs/active/progress.md`: Exp A-D are
currently running to fill the phenotype section, and H5/H1 confirmation follows
only after those runs complete or the user explicitly approves a different
sequence.

---

## 7. Outcome Interpretation Rules

This section records how to interpret current and future outcomes without
collapsing the mechanism into a simple payoff story.

### 7.1 Positive Mechanism Pattern

The strongest pattern would show the full chain:

```text
predictive reliability -> precision_k -> policy shift -> behavior
```

This requires more than payoff. H1 should show precision tracking predictive
accuracy rather than reward. H0 should show the policy space is open. H2-H5
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
partner-local advantage. This is a current H3 model-comparison readout, not an
H0-H8 failure condition.

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
- **Depression** (high initial beta): chronically low policy precision, reduced engagement
- **Anxiety**: increased epistemic drive weighting when $\beta_k$ is low (uncertainty triggers excessive information-seeking)

**Critical analysis warning**: These are sensitivity analyses, not a unified clinical framework. The parameter-to-phenotype mappings are illustrative and should not be interpreted as validated clinical models. The configs exist for H6 Perturbation Phenotypes, but moving from sensitivity analysis to clinical modeling requires: (a) fitting to human behavioral data, (b) formal model comparison showing the affective model outperforms simpler alternatives on clinical populations, and (c) demonstrating that the parameter variations are identifiable from behavioral data alone rather than being degenerate with other model parameters.

### 8.5 Graded Investment Trust Game

The graded investment trust game replaces the binary cooperate/defect action with 6 investment levels (0%, 20%, 40%, 60%, 80%, 100% of endowment), creating 24 actions per step (6 levels × 4 partners). This produces q_pi_entropy ~5.8 (vs <0.01 in binary), activating the precision modulation channel that was structurally inert in the binary game due to softmax saturation.

**Current status**: Graded configs exist in the maintained experiment surface as
H0 precision-channel tests.

### 8.6 Phase Roadmap

| Phase | Description | Dependencies | Status |
|---|---|---|---|
| Phase 3 | Theory tightening: formalize the H0-H8 behavior cards and expected behavior | Current docs | Done |
| Phase 4 | Discrete beta: supported task-local `DiscreteBetaState` | Phase 3 | Done |
| Phase 5 | Historical H0-H8 run queue and targeted confirmation | Phase 4 | Superseded as manuscript evidence by log-surprisal/post-fix queue |
| Phase 6 | Write-up stabilization and public documentation cleanup | Phase 5 | Current |
| Phase 7 | Confirmation-scale log-surprisal reruns and phenotype evidence | Phase 6 | Current |
| Phase 8 | Human data: fit behavioral data and estimate individual-difference parameters | Stable manuscript | Future |

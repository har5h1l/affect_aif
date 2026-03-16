# Future Work: Phases 4–8

Phase 3 (theory tightening) is the current focus: revising the narrative around orthogonal augmentation, documenting the confirmed H3 boundary condition, and flagging the engineering-approximation status of the current beta update rule. The phases below outline the research trajectory once Phase 3 stabilizes.

---

## §1: Phase 4 — Variational β Reformulation

**Goal:** Formalize β as a discrete hidden state within the generative model, extending the current continuous EMA update (grounded in Hesp et al.'s variational precision dynamics) to a full Bayesian inference scheme where β is subject to the same categorical inference machinery as partner-type estimation.

**Approach:**

1. Discretize β into a set of hidden-state levels (e.g., β ∈ {0.1, 0.3, 0.5, 0.7, 0.9}).
2. Define a likelihood function P(ε|β) mapping prediction-error magnitudes to β levels — high β predicts small errors; low β predicts large errors.
3. Define transition dynamics P(β_t|β_{t-1}) encoding the prior expectation that precision changes smoothly across trials.
4. Apply standard Bayesian hidden-state update: the agent infers β at each trial the same way it infers partner type.

This makes β a first-class hidden state within the generative model, formalizing the continuous EMA dynamics of Hesp et al. into a discrete inference scheme subject to the same variational machinery as every other hidden state.

**Key challenge:** Choosing the discretization granularity and likelihood parameterization that recovers the qualitative behavior of the current EMA rule (smooth tracking, appropriate responsiveness to betrayal events) without introducing pathological inference artifacts.

**Entry condition:** Phase 3 paper draft is stable.

**Status: Not Implemented.**

---

## §2: Phase 5 — Clinical Parameter Sensitivity Analysis

**Goal:** Systematic sensitivity analysis of affective parameters, interpreted through a clinical lens. This is an exploration of the existing parameter space, not a unified clinical framework.

**Approach:** Define parameter configurations that map onto clinically relevant profiles, run each against the standard trust-game conditions, and compare behavioral signatures against predictions.

**Parameter configurations:**

| Profile | Parameters | Prediction |
|---|---|---|
| **Alexithymia** | α_charge = 0.1 (blunted affective charging, slow precision updates) | Minimal behavioral difference from non-affective baseline — the affective channel is present but functionally inert. |
| **Borderline** | α_charge = 12.0, λ_smooth = 0.5 (rapid, volatile precision swings) | Over-reactive to single betrayals, unstable partner preferences, oscillating cooperation patterns. |
| **Depression** | initial_β = 0.2 (persistently low precision on social outcomes) | Under-weighting social information, slow to capitalize on cooperative partners, flattened preference structure. |

**Analysis design:** Each configuration is compared against the non-affect baseline (Condition 4) for within-config comparison, and cross-compared against the default affective agent (Condition 2) to assess whether the parameter manipulation shifts behavior in the predicted direction.

**Falsification criteria:** If parameter changes do not produce the predicted behavioral signatures, the affective mechanism lacks the claimed sensitivity to these parameter dimensions. This would narrow the scope of clinical interpretation the model can support.

**Entry condition:** Phase 4 preferred (principled parameter space) but can proceed with Phase 3 parameters as a preliminary pass.

**Status: Preliminary Analysis Complete. Current trust game is too unambiguous for clinical differentiation.**

### Preliminary Empirical Findings

A systematic exploration across four experimental designs (current params, precision modulation, short horizon, extreme params) with both `affect_modulates_precision` ON and OFF found that:

1. **The affective mechanism is a binary augmentation.** Having mu-weighted terminal values provides ~10% payoff improvement over no-affect baselines, but the benefit is invariant to the specific beta dynamics. Whether beta is frozen at 0.5 (alexithymia), swings from 0.08–0.99 (extreme borderline), or starts at 0.01 (extreme depression), the aggregate payoff difference from default C2 is at most 0.5% (3 points out of 576).

2. **Softmax saturation nullifies precision modulation.** The median EFE gap between the best and second-best policy is 10.83, making the softmax effectively a hard argmax. Policy precision scaling via `gamma * (1 + beta)` is structurally inert at these magnitudes — 91.5% of rounds have q_π entropy < 0.01.

3. **Beta recovery is too fast for persistent deficits.** Depression (β₀=0.01) recovers to default levels by round 25. The deficit is entirely early-game and does not accumulate enough to produce a meaningful total-payoff difference.

4. **Only two conditions reach statistical significance** (out of 18 comparisons): extreme depression with precision OFF (t=-2.67, p<0.01) and extreme borderline with precision ON (t=-2.75, p<0.01). Neither survives Bonferroni correction, and both have negligible effect sizes (Cohen's d < 0.05).

Full results: `results/clinical_sensitivity_synthesis.md`.

### Revised Path Forward

For clinical sensitivity analysis to produce meaningful differentiation, the analysis needs at least one of:

1. **More ambiguous environments (Phase 7 prerequisite).** The current trust game with 4 partners and binary actions creates an EFE landscape where the optimal policy is almost always unambiguous. Larger action spaces, multiple equilibria, or partial observability would create decision points where precision differences can flip policy selection.

2. **Observation-level precision modulation.** Beta currently affects terminal values and (optionally) policy sharpness. Neither channel produces differentiation because the EFE landscape is too steep. An alternative where beta modulates the *observation model precision* — affecting how the agent learns about partners, not just how it acts — could make beta dynamics functionally relevant at the belief-update level.

3. **Slower recovery dynamics (Phase 4 prerequisite).** The current EMA rule allows rapid beta recovery. A variational β formulation with appropriate transition dynamics could enforce slower timescale recovery, making clinical initial conditions persist longer.

The implication is that Phase 5 should be **deferred until Phase 7 (richer tasks)** provides an environment where clinical differentiation is architecturally possible, rather than attempting further parameter sweeps in the current task.

---

## §3: Phase 6 — Bayesian Model Comparison

**Goal:** Formal model evidence comparison between affective and non-affective generative models using Bayes factors.

**Approach:** Compute marginal likelihood (model evidence) for affective vs. non-affective models given observed partner behavior sequences, then compare using Bayes factors. This replaces the current frequentist pairwise tests with a question better suited to the problem: not "do conditions differ?" but "which generative model best accounts for the data?"

**Why not Bayesian Model Reduction (BMR)?** The original BMR proposal for this project was conceptually broken — it conflated model selection with parameter estimation. BMR works by starting with a full model and testing whether reduced (nested) models explain the data equally well. In this context, the affective and non-affective models are not cleanly nested in a way that makes trigger-based BMR coherent. Marginal likelihood comparison is the correct tool.

**Key challenge:** Ensuring fair comparison. The affective model has additional parameters (α, λ, β₀), so it must be penalized for complexity. Marginal likelihood naturally incorporates an Occam factor, but the computation must be done carefully — approximation quality matters.

**Entry condition:** Phase 4 (variational β) is a prerequisite. Model comparison is most meaningful when β is formalized as a discrete hidden state with an explicit likelihood contribution, enabling clean computation of marginal model evidence.

**Status: Not Implemented, requires Phase 4.**

---

## §4: Phase 7 — Richer Task Environments

**Goal:** Test whether per-partner metacognitive precision tracking provides orthogonal augmentation in more complex social settings, beyond the current trust game.

**Extensions:**

- **Larger action spaces.** Move beyond binary share/keep to graded investment decisions, testing whether precision tracking scales to continuous or multi-level actions.
- **More partners.** Scale from 3 to N partners, testing whether the per-partner tracking mechanism degrades gracefully or hits capacity limits.
- **Partial observability.** Add observation noise (misreading partner actions), testing whether precision tracking aids robustness to sensory uncertainty in addition to social uncertainty.
- **Richer temporal structure.** Multi-round games with longer causal chains between action and outcome, where planning depth should matter more and the augmentation claim faces a harder test.

Each extension targets a specific dimension of generalizability. The central question is whether the orthogonal-augmentation result (affect helps at every planning depth, planning depth alone does not recover the benefit) holds outside the trust-game family.

**Entry condition:** Single-agent paper is in draft or published.

**Status: Not Implemented.**

---

## §5: Phase 8 — Human Data Fitting

**Goal:** Fit model parameters to individual human participants' trust game behavior, validating whether the model's parameter space maps onto real human variation.

**Approach:**

1. Obtain trust-game behavioral data from healthy participants and (ideally) vmPFC-lesioned patients.
2. Estimate individual-difference parameters (α_charge, λ_smooth, β₀) from each participant's action sequences using maximum-likelihood or variational Bayesian fitting.
3. Test whether the affect-on/affect-off model distinction predicts the patient/control behavioral split.
4. Examine whether fitted parameter values cluster in ways that correspond to known individual differences (e.g., trait empathy, interoceptive accuracy scores).

**Key challenge:** The model must be computationally efficient enough to run many fitting iterations per participant, and the parameter space must be identifiable — distinct parameter settings must produce distinguishably different behavior.

**Entry condition:** Phases 4–5 at minimum. Fitting requires a principled parameter space (Phase 4) and confidence that the parameter space is behaviorally sensitive (Phase 5).

**Status: Not Implemented.**

---

## Cross-Phase Dependencies

```
Phase 3 (theory tightening) ← current
    │
    ▼
Phase 4 (variational β)
    │
    ├──▶ Phase 7 (richer tasks)  ← can begin after Phase 4
    │        │
    │        ▼
    │    Phase 5 (clinical sensitivity) ← requires Phase 7 environments
    │        │
    │        ▼
    │    Phase 6 (model comparison) ← requires Phase 4
    │
    └──▶ Phase 8 (human data)    ← requires Phases 5–7
```

**Updated dependency rationale:** The preliminary clinical sensitivity analysis (Phase 5 preliminary pass) demonstrated that the current trust game's EFE landscape is too unambiguous for clinical parameter perturbations to produce behavioral differentiation. Phase 5 therefore now depends on Phase 7 (richer tasks) providing environments where the EFE landscape has enough ambiguity for precision differences to flip policy selection. Phase 7 has been elevated to the critical path.

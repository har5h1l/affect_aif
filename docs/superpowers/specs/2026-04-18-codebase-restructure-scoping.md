# codebase restructure — scoping document

date: 2026-04-18
status: scoping (split-off point — sub-projects spawn from here)
parent session: brainstorming triggered by user observation that andrew pescia's reference implementation has a much simpler core than ours

---

## why this doc exists

andrew's pymdp-fork notebook (now `notebooks/04_apashea_trust_spec.ipynb`) showed that the core agent code can be small. our codebase has accumulated:

- a tightly-coupled `agent/inference/` that mixes generic active inference machinery with trust-game-specific rollout
- two parallel generative-model classes (`TrustGameModel`, `GradedTrustGameModel`) that already share 99% of code via `_BaseTrustGameModel`
- 24 experiment configs, ~30% of which are stale, broken, or redundant
- 5 non-aif baselines + 3 aif variants, with at least one wrapper (`AIFPolicy`) that is a `NotImplementedError` stub
- 15 doc files with significant drift from code (jax-first language, removed `o_intero` modality still mentioned, broken cross-links to renamed files)

before any more experiments are run we want to:

1. settle the codebase structure (extract a generic `aif/` package)
2. unify the generative model around andrew's canonical spec with documented extensions
3. decide which agents (aif and baseline) are essential vs archive
4. prune experiment configs and reconcile hypothesis labels
5. rewrite docs around the new structure

this doc is the **split-off point**. the work is too big for a single design conversation. five sub-projects are scoped below, each with a self-contained prompt that can be dropped into a fresh session.

---

## current state (synthesis of parallel audits)

audit transcripts are in this conversation. key facts feeding each sub-project:

### model surface (feeds B, A)

- `TrustGameModel` and `GradedTrustGameModel` already inherit from `_BaseTrustGameModel`; only `_init_payoffs` differs. **already 99% unified — needs one merged class with a `payoff_mode` switch.**
- factorized controls landed: `num_controls = [1,2,2]` (random assignment) or `[N,2,2]` (agent_choice). `B` third dimension is `prod(num_controls) = 4`, not 2 as in andrew's strict §4.
- `infer_joint_posterior` uses **only `A[0]`** — payoff modality is dropped from belief update. this is a divergence from andrew's spec §11.
- `C[1]` log-softmax decision is intentional (kept over andrew's raw softmax) and documented in MISSION.
- graded variant uses interpolated `cooperation_evidence_strength` for stance dynamics rather than two discrete slices.

### code structure (feeds A)

- pure-generic candidates for an `aif/` package (~850–1100 LOC, ~20 import-edit sites):
  - `aif/backend.py` ← `agent/inference/backend.py`
  - `aif/maths.py` ← `agent/inference/maths.py`
  - `aif/utils.py` ← `agent/inference/utils.py`
  - `aif/efe.py` ← `agent/inference/efe.py`
  - `aif/policies.py` ← `agent/inference/policies.py`
  - `aif/learning.py` ← `agent/inference/learning.py`
  - `aif/runtime.py` ← `agent/inference/runtime.py`
  - `aif/affect/beta.py` ← `agent/affect/beta.py` (rename `partner` → `entity`)
  - `aif/affect/interoception.py` ← `agent/affect/interoception.py`
  - generic bits of `rollout.py`: `generate_observation_sequences`, `gamma_per_policy`
- trust-specific (stays project-side):
  - `decision_step_trust_game`, `_rollout_policy_trust_game_*`, `_decode_action`, `_decode_policy_timestep`, `_partner_action_distribution`, etc.
  - **all of `BaseAgent`** as currently implemented — should be split into `aif.Agent` (generic shell) + `TrustGameAgent(aif.Agent)` (trust wiring)
  - all of `agent/model/*`
- `rollout.py` is ~15–18% generic / ~82–85% trust — needs split

### agent inventory (feeds C)

- aif: `BaseAgent`, `AffectiveAgent`, `LesionedAgent`. `LesionedAgent` has two modes (`decouple`, `freeze`); **`freeze` is referenced by zero configs**.
- baselines (in `benchmark/baselines.py`): `RandomAgent`, `TitForTatAgent`, `WinStayLoseShiftAgent`, `PavlovAgent`, `GrimTriggerAgent`, `QLearningAgent`. all referenced by at least one benchmark config except as noted below.
- ghosts (resolved in sub-project C, 2026-04-18):
  - ~~`AIFPolicy`~~ removed from tree; document future CoGames bridge when CvC unfreezes
  - ~~`reward_average`~~ removed from analysis/factory surface; H5 contrast uses `tau4_no_affect`
  - ~~`variational_beta` preset / `beta_mode` ghost~~ removed from `PRESET_CONDITIONS` and config
- cvc/cogames stack: `cvc_scoring_policy.py`, `cvc_affect_policy.py`, `cvc_policy.py`, plus 5 cvc configs and ~10 test files. MISSION says **do not touch** for current reframe.

### experiments + hypotheses (feeds D)

- 24 configs categorized: 4 smoke, 5 hypothesis (h1, h2, h4, h5, shallow), 1 sensitivity, 2 clinical, 2 graded, 8 trust-benchmark, 2 cvc.
- **h5 naming conflict**: `analysis/hypotheses.py` `H5 = precision_vs_reward` (uses `reward_average` agent kind, which is broken). `docs/experiment/design.md` `H5 = partner selection` (corresponds to `h5_partner_selection.json`). these are different hypotheses with the same label.
- benchmark betrayal trio (`benchmark_betrayal.json`, `benchmark_betrayal_fair.json`, `benchmark_betrayal_comprehensive.json`) differ only in rounds/switch timing — candidates to merge into one parameterized config.
- `benchmark_default.json` and `benchmark_resource_sharing.json` overlap heavily.
- `STATE.md` blockers: shallow_affect_confirm needs rerun on new generative model; h5_selection and clinical_betrayal partials incomplete; clinical_phenotypes never produced csv.

### docs (feeds E)

- 15 doc files; ~40% have stale content
- specific stale items:
  - "jax-first" language in `CLAUDE.md`, `docs/experiment/design.md` §6.1, `docs/design/partner_stance.md` §8, `docs/design/implementation.md`
  - `o_intero` modality and `beta`-as-pomdp-factor mentioned in `README.md`, `docs/design/implementation.md`, `docs/experiment/design.md` §2, `docs/theory/theory.md` (contradicts pomdp_spec.md v4)
  - broken links: `docs/action-dependent-partner-design.md` (now `docs/design/partner_stance.md`), `docs/results_tracking.md` (now `docs/experiment/results.md`)
  - `AGENTS.md` condition table does not match current 1–8 + 9–10
  - `CLAUDE.md` source layout uses old top-level `agent/` paths
- duplications: stance design described in 5 places; cli docs in 3 places; empirical narrative in 4 places
- missing: factorized controls, `log_policy_prior`, dirichlet learning flags, conditions 9–10, `aif/` module decision

---

## decomposition into sub-projects

```
B. generative model unification ──┐
                                  ├──→ A. aif/ extraction ──┬──→ C. agent inventory ──┐
                                  │                          │                          ├──→ D. experiment + hypothesis pruning ──→ E. doc rewrite
                                  │                          └──→ F. multi-focal runtime ┘
                                  └──→ (no other deps)
```

**recommended order**: brainstorm B+A together as one combined session (they're tightly coupled — class location is part of the module split). then **F (multi-focal-agent runtime)** and **C (agent inventory)** can run in parallel — both depend only on B+A. then D (which needs both C's agent decisions and F's new configs to survey), then E. cvc stack is treated as out-of-scope by all sub-projects per MISSION.

| sub-project | what it decides | depends on | est. effort |
|---|---|---|---|
| **B+A** combined | canonical model class + `aif/` module split | nothing | 1–2 sessions design + 2–3 days code |
| **F** new | multi-focal-agent runner (M `TrustGameAgent`s interacting), pairing rules, joint game resolution | B+A merged | 1 session design + 2–3 days code |
| **C** | which agents stay, which archive | B+A merged | 1 session design + half day code |
| **D** | which configs survive, hypothesis label cleanup, h5 rename | B+A, C, F | 1 session design + half day code |
| **E** | doc rewrite to ≤10 files | A, B, C, D, F | 1 session design + 1 day writing |

---

## per-sub-project prompts

each prompt below is self-contained. drop into a fresh cursor/claude session. each prompt:

- references this scoping doc as authoritative context
- includes the key audit findings the session needs
- specifies the deliverable (a brainstorming session ending in a `docs/superpowers/specs/<date>-<topic>-design.md`, then a writing-plans session producing an implementation plan)

---

### prompt 1 — sub-projects B + A combined: canonical generative model + `aif/` module extraction

```
i want to brainstorm two coupled changes to the affect_aif codebase as one design:

(B) consolidate `TrustGameModel` and `GradedTrustGameModel` into one canonical class
(A) extract a generic `aif/` package from `agent/inference/`, leaving project-specific
    code in a renamed project module

read the scoping doc first:
  docs/superpowers/specs/2026-04-18-codebase-restructure-scoping.md

specifically the "current state" sub-sections "model surface" and "code structure",
and the "decomposition" + "per-sub-project prompts" sections.

key facts from the audit you need:

1. `_BaseTrustGameModel` already holds 99% of the model code. `TrustGameModel` and
   `GradedTrustGameModel` differ only in `_init_payoffs`. unification is mostly a
   matter of adding a `payoff_mode` constructor arg.
2. andrew pescia's canonical spec lives in `docs/theory/pomdp_spec.md` v4. core
   structure: F=3 (s_type, s_stance, s_own), M=2 (o_action, o_payoff), beta external.
   we have intentional documented divergences from his spec: log-softmax C[1],
   factorized controls [1,2,2] / [N,2,2], optional dirichlet learning, optional
   graded payoff levels.
3. there is a known bug: `infer_joint_posterior` uses only `A[0]` — payoff modality
   is dropped from belief update. fixing or documenting this is in scope.
4. proposed `aif/` extraction (from audit): backend, maths, utils, efe, policies,
   learning, runtime, affect/beta, affect/interoception, plus generic bits of
   rollout (`generate_observation_sequences`, `gamma_per_policy`). ~850–1100 LOC,
   ~20 import edit sites.
5. `BaseAgent` is currently fully trust-specific. proposed split: `aif.Agent`
   (generic shell holding A/B/C/D, policies, optional pA/pB) + `TrustGameAgent`
   (multi-partner joint beliefs, decision_step_trust_game, factorized env wiring).
6. `rollout.py` is ~15% generic / ~85% trust — split needed.

questions you need to answer in the brainstorming:
- do we merge into one `TrustGameModel` class with `payoff_mode` switch, or keep two?
- where does `TrustGameModel` live after the split? (`affect_aif/trust/model.py`?
  `aif/examples/`? something else?)
- what is the project module called after `aif/` is extracted?
  (`affect_aif/`? `trust/`? `app/`?)
- what is the public surface of `aif.Agent`? what does its constructor take?
- do we fix the `infer_joint_posterior` payoff drop now, or document and defer?
- does `aif/affect/` belong in the generic package, or is it project-side?
  (audit says: machinery is generic; only naming conventions are social.)
- backwards compat: do we keep import shims at old `agent/inference/*` paths
  during migration, or do a hard switch?

apply the brainstorming skill (it should auto-load from the manually-attached set).
present the design in sections, get my approval after each. write the final spec to
`docs/superpowers/specs/<today>-aif-extraction-design.md` and commit it.

then invoke writing-plans to produce an implementation plan. do NOT start
implementing. stop after the plan is written and committed.

cvc / cogames code is out of scope per MISSION — leave it untouched.
```

---

### prompt 1.5 — sub-project F: multi-focal-agent runtime

```
i want to brainstorm a new experiment runtime where M focal active-inference
agents play the trust game with each other (rather than one focal AIF agent
+ N scripted partners as today). this is a NEW experimental capability built
on top of the post-B+A codebase, not a refactor.

assume sub-projects B + A are already merged. you can rely on:
  - aif.Agent (stateful container, no step loop)
  - aif.infer_states / infer_policies / sample_action / update_pA / update_pB
  - trust.TrustGameAgent (focal agent with N internal per-partner aif.Agents)
  - trust.AffectiveAgent, trust.LesionedAgent
  - trust.TrustGameModel (canonical, payoff_mode={binary, graded})
  - trust.rollout.decode_raw_action_to_partner_and_social

read the parent scoping doc first:
  docs/superpowers/specs/2026-04-18-codebase-restructure-scoping.md

and the B+A spec (which proves the design supports multi-focal by composition):
  docs/superpowers/specs/2026-04-18-aif-extraction-design.md
  (specifically the "multi-focal-agent compatibility" appendix)

key design facts that motivate this sub-project:

1. pomdp_spec.md v4 §1 explicitly describes the system as "N agents interact
   in a repeated trust game with turn-taking" — multi-focal-agent is the
   canonical setup, but the current codebase only implements one focal AIF
   agent + scripted/baseline partners.
2. multi-focal is NOT behaviorally equivalent to N separate "single AIF agent
   vs scripted partners" games. when AIF agents play each other, beliefs
   co-evolve, emergent dynamics arise (cooperation buildup, defection
   cascades, mutual modeling), and the game has a 2-level mind-modeling
   structure that scripted partners cannot produce.
3. the B+A design is provably compatible: spawn M trust.TrustGameAgent
   instances, route observations between them. zero changes needed in aif/
   or trust/ — all the new code is in experiment/ and configs/.

scope (new code):
  - experiment/multi_focal_runner.py (~150 LOC)
  - experiment/pairing.py (round-robin, all-pairs, random, mutual-selection
    in agent_choice mode; ~50 LOC)
  - experiment/joint_resolution.py (resolve M chosen actions into per-pair
    payoffs and the (partner_action, payoff) observations each agent receives;
    ~100 LOC)
  - new config schema: list of M agent specs (mixed types allowed —
    AffectiveAgent + LesionedAgent + TrustGameAgent in one experiment),
    pairing rule, game length
  - tests for emergent dynamics (cooperation can emerge, defection can
    cascade), tests for asymmetric agent populations (~200 LOC)
  - 2-3 sanity-check experiments wired to configs/ for sub-project D to
    review

questions to answer in the brainstorming:
  - pairing rule menu: which pairings do we support and what are the
    semantics? (round-robin, all-pairs, random, mutual-selection)
  - mutual-selection in agent_choice mode: what if A picks B but B picks C?
    options: A's pick wins / round skipped / all picks resolve concurrently /
    other. need a clear default.
  - does an agent model itself? convention is num_partners = M-1 (no self),
    but if you want self-modeling for some experiments, num_partners = M.
  - heterogeneous populations: how does the config schema express "1
    AffectiveAgent + 3 TrustGameAgent + 1 LesionedAgent(decouple)"?
  - should we support mixed-pomdp populations (some agents using a different
    TrustGameModel — e.g., different preference temperature)? probably yes;
    how does the runner construct per-agent models?
  - turn-taking vs simultaneous moves: in this trust-game variant, do all
    agents act each round simultaneously (each pair plays in parallel), or
    is there a single "active pair" per round?
  - logging: per-agent metrics × M agents per round → analysis schema
    needs design. probably one row per (round, agent_idx).
  - graded payoff mode (TrustGameModel payoff_mode='graded') in multi-focal:
    do both agents pick from the same investment-level set? do they get
    asymmetric payoffs? probably standardize to symmetric.
  - heterogeneous learning settings (one agent has learn_A=True, others not)
    — does this work cleanly under the per-partner-private learning
    semantics from B+A decision #9? confirm yes.

apply the brainstorming skill. present the design in sections, get my
approval after each. write the final spec to
`docs/superpowers/specs/<today>-multi-focal-runtime-design.md` and commit it.

then invoke writing-plans to produce an implementation plan. do NOT start
implementing. stop after the plan is written and committed.

cvc / cogames code is out of scope per MISSION — leave it untouched. baseline
scripted partners (TitForTat, Random, etc.) stay as-is for the existing
single-focal experiments; this sub-project does not retire them.
```

---

### prompt 2 — sub-project C: agent inventory cleanup

```
i want to brainstorm which agent classes (active inference and baselines) we keep,
which we move to archive/, and which need fixing. assume sub-projects B+A are
already merged (canonical TrustGameModel + aif/ extraction in place).

read the scoping doc first:
  docs/superpowers/specs/2026-04-18-codebase-restructure-scoping.md

specifically the "agent inventory" sub-section under "current state".

audit findings to act on:

1. AIF agents (3): BaseAgent, AffectiveAgent, LesionedAgent
   - LesionedAgent has two modes: `decouple`, `freeze`
   - `freeze` is used by zero configs — archive or document why we keep it
2. baselines (6 in benchmark/baselines.py): Random, TitForTat, WinStayLoseShift,
   Pavlov, GrimTrigger, QLearning. all used by at least one config except
   inconsistent inclusion (pavlov omitted from default/comprehensive/noisy;
   grim_trigger omitted from default/noisy).
3. broken / ghost agents:
   - `AIFPolicy` (benchmark/aif_policy.py): NotImplementedError stub, zero configs
   - `reward_average` listed in benchmark JSONs but rejected by factory.py and
     missing from AGENT_REGISTRY — must be either implemented or removed
     everywhere
   - `variational_beta` preset in PRESET_CONDITIONS but factory.py does not
     branch on spec.beta_mode — ghost preset
4. coverage gaps:
   - no "uniform-prior random partner" baseline as a focal AIF agent (one
     option andrew's spec implies)
   - lesion mode `freeze` vs `decouple`: do we want a third "freeze_planning_only"?

questions for the design:
- final keep/archive list for AIF agents
- final keep/archive list for baselines (be explicit; consolidate inconsistent
  benchmark-config inclusion)
- `reward_average`: implement properly, or strip from configs + analysis +
  hypotheses entirely? (this also affects sub-project D — h5 naming)
- `variational_beta`: same question
- new `aif.Agent` base class lives in `aif/` after sub-project A — does
  `BaseAgent`/`TrustGameAgent` rename in this sub-project, or was it already
  done in A? (check what A delivered)
- baselines: do they stay in `benchmark/baselines.py` or move to
  `aif/examples/baselines.py` since they implement the agent protocol?

apply the brainstorming skill. present the design in sections. write final spec
to `docs/superpowers/specs/<today>-agent-inventory-design.md`, commit, then
invoke writing-plans. do not start implementing.

leave cvc policy adapters (cvc_scoring_policy, cvc_affect_policy, cvc_policy)
untouched per MISSION.
```

---

### prompt 3 — sub-project D: experiment configs + hypothesis cleanup

```
i want to brainstorm pruning the experiment-config surface and reconciling
hypothesis labels. assume sub-projects B+A, F, and C are done. (F may have
added new multi-focal-agent configs — survey them as part of the inventory.)

read the scoping doc first:
  docs/superpowers/specs/2026-04-18-codebase-restructure-scoping.md

specifically the "experiments + hypotheses" sub-section under "current state",
plus conductor/STATE.md for the live blocker list.

audit findings to act on:

1. 24 configs total, categorized in the scoping doc. recommended action is
   roughly: keep 11 core science configs, merge 5 (betrayal trio + default/
   resource_sharing pair), demote rest to tier-2 / archive.
2. hypothesis label conflict: `analysis/hypotheses.py` H5 ("precision_vs_reward",
   uses broken `reward_average`) vs `docs/experiment/design.md` H5 ("partner
   selection", maps to `h5_partner_selection.json`). these are different
   hypotheses with the same label. naming must be fixed.
3. design.md hypothesis numbering does not match hypotheses.py numbering
   (design H1 ≈ code H2, design H2 ≈ code H1, etc.) — full reconciliation
   needed.
4. STATE.md blockers (the new generative model invalidates prior runs):
   - shallow_affect_confirm: needs rerun on new model
   - h5_selection: detached run incomplete
   - clinical_betrayal: detached run incomplete
   - clinical_phenotypes: never produced csv
5. CvC configs (5 of 24) are infrastructure / side track per MISSION.

questions for the design:
- final keep/merge/archive list with explicit paths
- how to merge benchmark betrayal trio into one parameterized config
- hypothesis renaming: what does H5 mean canonically? (rename code-side
  test to h5_partner_selection? add new H6 for precision_vs_reward?)
  reconcile hypotheses.py with design.md
- if `reward_average` is gone (decision from sub-project C), what happens
  to the precision-vs-reward hypothesis — kill it or replace its baseline?
- which configs need rerun after the apashea-aligned generative model
  changes — full priority order with rationale
- per-config seed/round counts — rationalize across the surviving set
- new "core experiment manifest" doc that lists exactly what produces the
  paper's figures

apply the brainstorming skill. present the design in sections. write final spec
to `docs/superpowers/specs/<today>-experiment-pruning-design.md`, commit, then
invoke writing-plans. do not start implementing.
```

---

### prompt 4 — sub-project E: documentation rewrite

```
i want to brainstorm rewriting the docs around the post-restructure codebase.
assume sub-projects A, B, C, D, F are all done — code, agents, configs,
hypotheses, and the multi-focal-agent runtime are stable.

read the scoping doc first:
  docs/superpowers/specs/2026-04-18-codebase-restructure-scoping.md

specifically the "docs" sub-section under "current state".

audit findings to act on:

1. 15 doc files today; recommended consolidation to ~10 (see scoping doc
   "recommended doc tree").
2. specific stale content to fix:
   - "jax-first" language in CLAUDE.md, docs/experiment/design.md §6.1,
     docs/design/partner_stance.md §8, docs/design/implementation.md
     (we are numpy-first with optional jax)
   - `o_intero` modality and `beta`-as-pomdp-factor in README, design/
     implementation.md, experiment/design.md §2, theory/theory.md
     (contradict pomdp_spec.md v4 which has external beta)
   - broken cross-links: `docs/action-dependent-partner-design.md` (now
     `docs/design/partner_stance.md`), `docs/results_tracking.md` (now
     `docs/experiment/results.md`)
   - AGENTS.md condition table does not match current 1–8 + 9–10
   - CLAUDE.md source layout uses old top-level paths
3. duplications to consolidate:
   - stance design described in 5 files
   - cli docs in 3 files
   - empirical narrative in 4 files
4. missing content to add:
   - factorized controls
   - log_policy_prior
   - dirichlet learning flags (learn_A, learn_B, learn_E) — note shift to
     per-partner private learning (B+A decision #9)
   - conditions 9–10 (tau3 pair)
   - aif/ module structure (new from sub-project A)
   - canonical model class (new from sub-project B)
   - multi-focal-agent runtime (new from sub-project F): pairing rules,
     joint game resolution, heterogeneous populations, mutual-selection
     semantics

questions for the design:
- final doc tree: confirm or revise the ≤10-file recommendation
- one canonical pomdp doc, or split spec vs theory? (audit suggests keeping
  pomdp_spec as appendix inside theory for the strict-10 cap)
- where does the aif/ package get its own doc? in-package README, or a
  section in engineering/implementation.md?
- audience separation: README (users), AGENTS/CLAUDE (agents), docs/
  (researchers + maintainers) — confirm
- what gets fully rewritten vs surgically edited
- which existing docs move to archive/ as historical record

apply the brainstorming skill. present the design in sections. write final spec
to `docs/superpowers/specs/<today>-doc-rewrite-design.md`, commit, then invoke
writing-plans. do not start implementing.
```

---

## cross-cutting decisions (resolve in the first session, propagate to others)

these come up in multiple sub-projects. resolve them in sub-project B+A and record the decision in this scoping doc afterward:

1. **project module name after `aif/` extraction.** options: `affect_aif/`, `trust/`, `app/`. affects every sub-project's import paths.
2. **canonical agent base class location and name.** `aif.Agent` is the working name. confirm.
3. **import-shim strategy during migration.** keep `agent.inference.*` re-exports for one release? hard switch? affects test suite + external notebooks.
4. **canonical `TrustGameModel` class name and home.** if merged via `payoff_mode`, what does the public class look like, and does it live in `aif/examples/` or in the project module?
5. **stance on the `infer_joint_posterior` payoff-drop bug.** fix in sub-project B or document and defer to a separate task.

---

## what is explicitly out of scope across all sub-projects

- cvc / cogames / observatory stack (`benchmark/cvc_*.py`, `benchmark/cogames_adapter.py`, `configs/benchmark_cvc_*.json`, `tests/test_cvc_*.py`, `tests/test_observatory_*.py`). per `conductor/MISSION.md`, do not touch. revisit in a separate scoping doc when the trust-game work is stable.
- the paper itself (`docs/paper/main.tex`). update only after sub-project E lands the new doc structure.
- new experimental hypotheses. this restructure is about cleanup, not new science. new hypotheses go through their own brainstorming.

---

## handoff

each session should, on completion:

1. commit its design spec to `docs/superpowers/specs/`
2. commit its implementation plan (from writing-plans) to `docs/superpowers/plans/`
3. append a one-line entry under "completed sub-projects" below
4. NOT start implementation in the same session — implementation runs in a fresh executing-plans session per the superpowers skill

### completed sub-projects

- **C (agent inventory / honest surface)** — 2026-04-18: removed `variational_beta` preset and `ConditionSpec.beta_mode`; dropped unused `ExperimentConfig.beta_mode` (legacy key stripped in `from_dict`); removed `reward_average` factory branch; retargeted analysis H5 post-switch contrast to `tau4_no_affect`; renamed betrayal pivot columns; deleted `benchmark/aif_policy.py`, `tests/test_benchmark_aif_policy.py`, and dead `tests/test_affect.py`; docs updated (`design.md` future-work section, `theory.md`, `README`, `AGENTS`, `implementation`, `benchmark` ops).
- **F (multi-focal-agent runtime)** — 2026-04-18: added `experiment/multi_focal_runner.py` (turn-taking single focal per round, simultaneous-moves resolution, `RoundProtocol` extension seam for future all-pairs), `experiment/joint_resolution.py`, `experiment/multi_focal_config.py` (heterogeneous `agents: [...]` schema), and `create_agents_from_multi_focal_config` in `experiment/factory.py`. Four configs: `multifocal_smoke.json`, `multifocal_homogeneous_affective.json`, `multifocal_clinical_mix.json`, `multifocal_assortative_choice.json` for sub-project D inventory. Deterministic regression + unit tests in default `pytest`; full N1/N2/N3 emergent battery marked `slow` — run `RUN_SLOW_TESTS=1 pytest tests/test_multi_focal_emergent.py -m slow`. No changes to `aif/` or `trust/`. Documented divergence from `pomdp_spec.md` §12 step 4 (simultaneous moves) as decision F4. Design: `docs/superpowers/specs/2026-04-18-multi-focal-runtime-design.md`; plan: `docs/superpowers/plans/2026-04-18-multi-focal-runtime-plan.md`.

# pymdp Hard Cutover Design

> Historical implementation-planning artifact. Runtime claims here describe the pre-cutover migration context, not the supported public architecture. Current supported runtime is official `inferactively-pymdp==1.0.0` with task-local trust and affect wrappers.


## Decision

Migrate the supported active-inference runtime to official
`inferactively-pymdp==1.0.0` and remove the custom `aif/` engine from supported
execution. This is a hard cutover, not a compatibility layer and not an optional
backend system.

The project-specific code should focus on trust-game semantics, affective
precision tracking, experiments, logging, and analysis. `pymdp` should own
state inference, policy inference, policy sampling, and reusable active
inference machinery.

## Reference Material

- `notebooks/references/apashea_trust_spec.ipynb` is the project-specific
  matrix and workflow reference.
- Apashea's `pymdp` fork is reference material for helper ideas only.
- Official `inferactively-pymdp==1.0.0` is the runtime target.

The Apashea notebook demonstrates the desired shape:

- construct standard A/B/C/D/E matrices for the trust model
- instantiate `pymdp.Agent`
- use factorized controls with `control_fac_idx=[1, 2]`
- run state inference, policy inference, action sampling, and optional learning
- extract policy diagnostics and Bayesian-model-averaged current beliefs

We should port only the helper ideas we need, not depend on the fork.

## Goals

- Eliminate custom active-inference code as a source of repeated agent errors.
- Keep affect as the project's novelty layer.
- Keep the experiment/config/analysis surface recognizable.
- Make the POMDP implementation match the documented standard A/B/C/D/E form.
- Prefer maintained upstream code over local reimplementation.
- Avoid legacy compatibility shims.

## Non-goals

- Preserve `aif/` as a reusable core.
- Maintain a dual backend.
- Keep old custom EFE, rollout, or policy-sampling implementations alive.
- Match every historical result bit-for-bit.
- Vendor Apashea's fork as a dependency.
- Retain deprecated compatibility imports, wrappers, aliases, or tests.
- Preserve deprecated documentation that describes removed runtime paths as
  runnable or supported.

## Legacy and Deprecated Code Removal Policy

This migration removes legacy code completely. Deprecated code should not be
kept behind flags, aliases, import fallbacks, or "temporary" compatibility
wrappers.

Remove:

- the custom `aif.Agent` runtime
- custom `aif` state inference
- custom `aif` policy inference and EFE calculation
- custom sophisticated-rollout planner
- custom policy construction and action sampling used only by the old engine
- custom Dirichlet learning helpers if official `pymdp` or the new trust wrapper
  replaces them
- tests whose only purpose is validating the removed custom core
- docs that frame `aif/` as the supported implementation
- roadmap entries that say no `pymdp` migration path is active

Retain only code that is still part of the new architecture:

- trust-game generative model construction
- trust environments and payoff semantics
- per-partner affective precision tracking
- experiment configs and runners
- logging and analysis surfaces that still describe active outputs
- small generic numeric helpers only when they are not active-inference engine
  code and are still imported by supported modules

If a symbol is retained only to avoid updating callers, remove the symbol and
update the callers instead.

## Target Architecture

```text
official pymdp
  -> state inference
  -> policy inference
  -> policy sampling
  -> active-inference utilities

tasks/trust/models
  -> construct trust-game A/B/C/D/E matrices
  -> construct policies and labels
  -> expose pymdp-ready model bundle

tasks/trust/agents
  -> wrap one pymdp.Agent per tracked partner
  -> maintain per-partner beliefs and diagnostics
  -> route observations/actions between env and pymdp

tasks/trust/affect
  -> DiscreteBetaState / precision tracker
  -> beta-to-gamma or beta-to-policy modulation
  -> clinical/lesion parameter variants

tasks/trust/envs
  -> trust-game generative process
  -> scheduled stance switches
  -> partner assignment and payoff resolution

experiments/trust
  -> conditions
  -> config parsing
  -> runner
  -> logging
  -> analysis entry points
```

## Target Codebase Structure

After the cutover, the supported runtime tree should read as task code built on
official `pymdp`, not as a local active-inference framework.

```text
affect_aif/
├── tasks/
│   └── trust/
│       ├── affect.py              # per-partner beta / precision tracking
│       ├── agents/
│       │   ├── base.py            # pymdp-backed TrustGameAgent
│       │   ├── affective.py       # affect modulation on top of pymdp
│       │   └── lesioned.py        # lesion variants
│       ├── models/
│       │   └── trust_game.py      # A/B/C/D/E and policy construction
│       ├── envs/                  # trust-game generative process
│       ├── rollout.py             # delete unless reduced to pymdp glue
│       ├── payoffs.py
│       ├── stance.py
│       └── types.py
├── experiments/
│   ├── trust/                     # configs, runner, logger, factory
│   └── multifocal/                # adapt to pymdp-backed agents
├── analysis/                      # dataframe/statistics/figures
├── scripts/                       # canonical experiment/analysis CLIs
├── docs/                          # updated runtime and theory docs
└── tests/                         # trust/affect/experiment tests only
```

The top-level `aif/` package should be removed unless a tiny non-runtime module
survives temporarily during a single patch. The end state should not expose
`import aif` as a supported package.

## Runtime Flow

Each `TrustGameAgent` should become a thin task wrapper around `pymdp.Agent`.

Per round:

1. Select active partner context.
2. Use the partner-specific `pymdp.Agent` state as the current generative model
   state.
3. Infer policies through official `pymdp`.
4. Apply affective modulation for affective variants.
5. Sample or deterministically select the current-timestep action.
6. Step the trust-game environment.
7. Convert environment outcome to `pymdp` observation indices.
8. Run state inference for the active partner.
9. Update per-partner affect from social prediction error.
10. Optionally update supported learning parameters if enabled.
11. Log the same experiment-facing metrics where still meaningful.

## Affect Layer

Move affect code out of `aif.affect`.

Recommended module:

```text
tasks/trust/affect.py
```

Keep or port:

- `DiscreteBetaState`
- beta levels `[0.5, 0.67, 1.0, 1.5, 2.0]`
- HESP inverse-beta precision convention
- surprise signal `1 - P(observed partner action)`
- clinical parameter variants
- lesion modes

The affect layer should not reimplement POMDP inference. It should read
diagnostics from the `pymdp` wrapper and adjust precision/policy modulation.

## Helper Ideas to Port from Apashea

Port minimal equivalents only if official `pymdp` does not expose them directly:

- `infer_policies_info`: policy posterior plus negative EFE, expected utility,
  and information gain diagnostics.
- `compute_current_qs_bma`: Bayesian-model-averaged current beliefs from
  policy-conditioned MMP beliefs.
- `sample_action_timestep_dependent`: choose the action for timestep 0 of the
  selected policy.
- `update_A_MMP_distributional`: only if parameter learning remains supported
  in the MVP.
- `update_E`: only if policy-prior learning remains supported in the MVP.
- `update_gamma`: only if official `pymdp` lacks the needed precision update
  hook and precision modulation remains active.

Do not port plotting helpers, broad notebook utilities, or fork-specific
monitoring unless they directly support the experiment runner.

## Files Expected to Change

Primary implementation:

- `pyproject.toml` or dependency files: add/pin `inferactively-pymdp==1.0.0`
- `tasks/trust/models/trust_game.py`: emit `pymdp`-ready arrays and policies
- `tasks/trust/agents/base.py`: rewrite around `pymdp.Agent`
- `tasks/trust/agents/affective.py`: use task-local affect state
- `tasks/trust/agents/lesioned.py`: adapt lesion behavior to new affect layer
- `tasks/trust/rollout.py`: remove or replace with `pymdp` helper calls
- `experiments/trust/factory.py`: instantiate rewritten agents
- `experiments/trust/logger.py`: adapt diagnostics if field sources change
- `experiments/multifocal/*`: adapt only where it calls agent internals

Deletion or unsupported surface removal:

- `aif/agent.py`
- `aif/inference.py`
- `aif/efe.py`
- `aif/runtime.py`
- `aif/policies.py`
- `aif/learning.py`
- `aif/backend.py`
- most custom-core tests under `tests/test_aif_*`

Possible retained/relocated code:

- `aif/affect/beta.py` -> `tasks/trust/affect.py`
- small numeric helpers if not provided by `numpy`, `jax`, or `pymdp`

Docs:

- `docs/theory/apashea_alignment.md`
- `docs/theory/pomdp_spec.md`
- `docs/design/implementation.md`
- `docs/experiment/design.md`
- `docs/state/current/mission.md`
- `README.md`

## Documentation Updates

Documentation must change in the same cutover so agents and humans do not
continue following obsolete runtime instructions.

Update:

- `README.md`: install/setup should include `inferactively-pymdp==1.0.0`; the
  supported workflow should say the trust agent is `pymdp`-backed.
- `docs/state/current/mission.md`: replace the reusable custom `aif/` core
  mission with the hard cutover to official `pymdp`.
- `docs/state/decisions/architecture.md`: record that the project no longer
  owns the active-inference engine.
- `docs/theory/apashea_alignment.md`: state that Apashea's notebook/fork is a
  reference and official `pymdp` is the runtime.
- `docs/theory/pomdp_spec.md`: keep A/B/C/D/E definitions but remove language
  saying matrices are implemented without embedding `pymdp`.
- `docs/design/implementation.md`: describe `pymdp.Agent` wrapping,
  per-partner affect, and removed legacy surfaces.
- `docs/experiment/design.md`: describe condition behavior in terms of
  `pymdp` policy inference plus external affective modulation.
- `docs/future/roadmap.md`: remove or revise any decision that says no `pymdp`
  migration path is active.
- `notebooks/README.md`: clarify that the Apashea notebook is a historical and
  mathematical reference, not a runtime dependency.

Remove or rewrite:

- references to `aif.Agent` as supported runtime code
- references to `aif.affect.beta.DiscreteBetaState`; use the new trust-local
  affect module path
- troubleshooting commands or explanations that target deleted custom-core
  tests
- old architecture diagrams that show `aif/` as the reusable core

## Test Strategy

Because this is a hard cutover, remove tests whose only purpose is preserving
custom `aif` behavior.

Keep or rewrite tests around:

- trust model matrix shapes and normalization
- factorized controls and policy labels
- agent can infer, choose action, observe outcome
- affect beta updates from prediction error
- lesion modes affect decision influence but not state inference
- experiment runner smoke test writes expected schema
- betrayal switch semantics
- multifocal round loop if still in scope

Do not require bit-for-bit historical parity with the old custom engine.

## Migration Phases

### Phase 1: Dependency and model bundle

- Add official `inferactively-pymdp==1.0.0`.
- Convert `TrustGameModel` output into official `pymdp` inputs.
- Add a small internal model-bundle object if useful.

### Phase 2: Agent rewrite

- Rewrite `TrustGameAgent` around `pymdp.Agent`.
- Preserve public methods used by environments/runners:
  - `choose_partner_and_action`
  - `plan_and_act`
  - `observe_outcome`
  - diagnostic attributes used by logger

This is not a backend shim; it is the new agent implementation.

### Phase 3: Affect relocation

- Move beta state into trust-local affect module.
- Wire affective and lesioned agents onto the new `pymdp` wrapper.
- Recreate only the diagnostics needed for experiment logs.

### Phase 4: Remove custom core

- Delete unsupported `aif/` runtime modules.
- Remove or rewrite custom-core tests.
- Update docs to make `pymdp` the committed runtime engine.

### Phase 5: Smoke and experiment readiness

- Run lightweight smoke only after implementation is complete and explicitly
  approved for verification.
- Then schedule full reruns separately.

## Risks

- Official `pymdp==1.0.0` may differ substantially from the older notebook
  fork API.
- MMP and sophisticated-inference hooks may expose diagnostics differently than
  Apashea's helper functions.
- Existing logger fields may need renaming or reduced detail.
- Some old experiment claims may stop being comparable after the engine swap.

## Risk Handling

- Treat the Apashea notebook as a model-construction reference, not a runtime
  contract.
- Use official `pymdp` docs/API as source of truth for active-inference calls.
- Prefer deleting unsupported diagnostics over rebuilding large local inference
  internals.
- Update theory and implementation docs in the same cutover.
- Ask before updating result-interpretation docs from new outputs.

## Acceptance Criteria

- The supported trust-game runner no longer imports custom `aif` inference,
  EFE, rollout, policy, or learning code.
- `TrustGameAgent`, `AffectiveAgent`, and `LesionedAgent` run through official
  `pymdp`.
- Affective precision tracking remains per-partner and external to the POMDP.
- Configs and scripts remain the canonical experiment surface.
- Docs state that official `pymdp` is the runtime engine.
- Legacy custom-core tests are removed or rewritten around the new behavior.
- Deprecated runtime modules, imports, docs, tests, aliases, and compatibility
  wrappers are removed rather than retained behind flags.
- The final supported codebase structure is task/experiment/analysis oriented,
  with no supported top-level custom active-inference engine package.

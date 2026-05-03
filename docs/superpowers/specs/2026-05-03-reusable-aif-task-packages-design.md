# Reusable AIF Core + Task Packages Design

date: 2026-05-03
status: approved design - ready for implementation planning after user review
branch: analysis/post-restructure-reframe
scope: repository architecture, experiment surface, docs/state, scripts, notebooks, and merge-readiness sequencing

---

## Why this doc exists

The project has moved past the old "affect compensates for shallow planning" story. The current scientific center is a Hesp et al. extension:

> Extend Hesp et al.'s single-agent affect-as-expected-action-precision account into multi-agent active inference by factorizing affective model-fitness estimates over social partners, then testing when those partner-specific precision signals improve action deployment, partner selection, and recovery under social uncertainty.

Recent apashea-aligned model work clarified the trust-game generative model, factorized controls, policy priors, and optional learning hooks. That integration also made old result narratives, old H-numbering, old demos, and several archive/paper artifacts stale. The repo now needs a second grounding pass:

- keep `aif/` as a reusable, JAX-oriented active-inference core
- move domain semantics into task packages
- delete unsupported legacy surfaces after salvaging useful content
- make docs/state the steering wheel for agents and humans
- make scripts the only canonical way to run experiments
- rerun experiments only after the architecture and hypothesis surface are clean

This spec captures the approved design direction. It is not an implementation plan.

---

## Fundamental principles

1. **Hesp extension first.** The project exists to extend Hesp-style affective precision into multi-agent social inference. Every hypothesis, experiment, and doc should serve that spine.

2. **Reusable JAX-based `aif/` core.** `aif/` remains JAX-based and reusable. Public core numerical functions should use `jax.numpy`/JAX-compatible arrays, pass randomness through explicit PRNG keys where randomness exists, avoid hidden NumPy RNG in core inference/planning paths, and preserve a small stable API for task packages. Pandas and NumPy remain fine for logging, analysis, CLI surfaces, fixtures, and compatibility wrappers, but not as the conceptual center of `aif/`.

3. **Task packages own domain semantics.** Trust-specific concepts belong under `tasks/trust/`: partners, stances, betrayal, payoffs, scripted baselines, trust environments, trust rollout, and trust evaluation.

4. **Clear dependency direction.** Higher layers depend on lower layers:

```text
scripts -> experiments -> tasks -> aif
```

`aif/` cannot import from tasks, experiments, analysis, or benchmarks. Task packages should not import experiment runners or result-file code.

5. **No legacy junk drawer.** Salvage useful material into current docs, then delete unsupported files. Keep references only when they actively explain current math or decisions, such as the apashea notebook.

6. **Docs are the steering wheel.** `docs/state/` becomes the agent/human cockpit: current mission, blockers, decisions, next runs, and handoffs. Historical result interpretation moves into `docs/results/`, not random state logs.

7. **Hypotheses before experiments.** Configs and analyses must map to current hypotheses. If an experiment does not answer one of the current Hesp-extension questions, delete it or explicitly mark it future work.

8. **Small public surfaces.** Each package exposes a small, intentional API. Internal helpers stay internal. Broad `__init__` re-export surfaces are allowed only when stable and tested.

9. **Results need provenance.** Every current result should record config, config hash or copied config, commit, branch, seed count, run date, analysis function, and current-vs-historical status.

10. **External benchmarks are separate.** CvC/CoGames can live under `benchmarks/`, but trust-task baselines are part of `tasks/trust/evaluation/`, not a separate "trust benchmark" concept.

11. **Behavior-preserving moves first.** File moves should preserve behavior and tests first. Scientific changes happen as explicit follow-up commits, not hidden inside import churn.

---

## Target architecture

The target repository shape is:

```text
aif/
  agent.py
  inference.py
  learning.py
  policies.py
  efe.py
  runtime.py
  affect/

tasks/
  trust/
    agents/
      base.py
      affective.py
      lesioned.py
    envs/
      binary.py
      graded.py
      partners.py
    models/
      trust_game.py
    evaluation/
      baselines.py
      arena.py
    rollout.py
    payoffs.py
    stance.py
    types.py

experiments/
  trust/
    runner.py
    batch.py
    config.py
    logger.py
    factory.py
    conditions.py
  multifocal/
    runner.py
    config.py
    joint_resolution.py

analysis/
  hypotheses.py
  metrics.py
  plots.py
  statistics.py

benchmarks/
  cvc/
  shared/

scripts/
  experiment/
  analysis/
  benchmark/

docs/
  theory/
  experiments/
  results/
  design/
  state/
  operations/
```

### Package boundaries

`aif/` is reusable active-inference machinery. It contains no trust-game vocabulary.

The target `aif/` public surface is JAX-based:

- public numerical APIs accept and return JAX-compatible arrays
- randomness is explicit via PRNG keys in public policy-sampling APIs
- core inference, EFE, learning, and policy helpers avoid hidden global RNG state
- NumPy compatibility, when needed, is kept at boundaries or tests rather than inside core algorithms
- task packages depend on a small stable API rather than internal helpers

`tasks/trust/` is the trust task package. It imports `aif/` and owns all trust-game semantics: payoff matrices, partner types, stance dynamics, binary and graded environments, trust-specific rollout, affective and lesioned trust agents, and the trust-task evaluation arena.

`experiments/` is orchestration. It owns configs, runner glue, logging, batch execution, and multi-focal experiment loops. It should be thin over `tasks/`.

`analysis/` consumes result tables. It should not drive task code.

`benchmarks/` is reserved for external or cross-task benchmark infrastructure, especially CvC/CoGames. The old "trust benchmark" is renamed/reframed as the trust-task evaluation arena under `tasks/trust/evaluation/`.

### Why `trust/` should not stay at root

Root-level `trust/` makes the trust task feel like a peer of the reusable core. In the target architecture, trust is one task package using the core. Moving it under `tasks/trust/` makes future tasks natural and keeps the import story honest.

### Why `env/` should not stay at root

The current `env/` package is trust-specific. It should move to `tasks/trust/envs/`. If future tasks need environments, they should live under their own task packages, not a shared root package that quietly mixes domains.

---

## Hypothesis surface

The old H1-H5/H7 labels are replaced by hypotheses that follow directly from the Hesp-to-multi-agent extension.

### H1: Model fitness, not reward

Per-partner affect tracks how reliable the agent's model of a partner is, not how rewarding that partner is. Reliable cooperators and reliable adversaries can both produce high model-fitness signals. Volatile partners should produce low or unstable signals.

### H2: Partner factorization

Per-partner affect should preserve social structure that a global affect signal collapses. Multi-agent environments require knowing which partner is predictable, not merely whether the world is globally predictable.

### H3: Deployment, not knowledge

Lesioning affect should preserve partner inference while impairing action deployment. The Damasio-style dissociation is: partner type or stance beliefs remain intact, but payoff, recovery, or partner choice worsens.

### H4: Social volatility

Affect should matter most under betrayal, stance shifts, partner volatility, noisy observations, or changing partner pools. Stable tasks may under-express the mechanism.

### H5: Partner selection

Per-partner affect should guide whom the agent chooses, avoids, probes, or returns to in agent-choice settings.

### H6: Policy-space regime

Affect only changes behavior when the policy posterior has room to move. Saturated binary settings can hide the mechanism. Shallow horizons, graded action spaces, volatile environments, and multi-partner choices should expose it more strongly.

### H7: Clinical perturbations

Clinical-like regimes are perturbations of affective precision dynamics: frozen precision, volatile precision, low-baseline precision, or slow-updating precision. They should separate by task regime, not as global traits that behave identically everywhere.

### Engineering objectives

Two useful outputs are not core hypotheses:

- **E1: Trust-task evaluation arena.** AIF agents versus scripted baselines. This is a task evaluation surface, not a separate trust benchmark.
- **E2: Multi-focal emergent dynamics.** AIF agents interacting with each other. This remains descriptive until a specific hypothesis is promoted.

---

## Experiment surface

Configs should live with the experiment family they serve:

```text
experiments/trust/configs/
  smoke.json
  h1_model_fitness.json
  h2_partner_factorization.json
  h3_lesion_deployment.json
  h4_betrayal_volatility.json
  h5_partner_selection.json
  h6_shallow_policy_regime.json
  h6_graded_policy_regime.json
  h7_clinical_betrayal.json
  h7_clinical_phenotypes.json
  e1_arena.json

experiments/multifocal/configs/
  smoke.json
  e2_homogeneous.json
  e2_clinical_mix.json
  e2_assortative.json
```

Rules:

- Every supported config maps to one hypothesis or engineering objective.
- Old `h1_*`, `h2_*`, `benchmark_*`, and clinical names are renamed if still supported or deleted if not.
- The reward-average control survives only if it answers H1, namely model fitness versus reward. It is no longer a central hypothesis by itself.
- Pre-apashea or pre-restructure results must be marked historical and not compared as if current.
- New experiment interpretation does not update docs until results exist and the user approves interpretation changes.

---

## Scripts and canonical runs

Scripts are the canonical execution surface. Notebooks are not.

Target script layout:

```text
scripts/
  experiment/
    run.py
    smoke.py
    inspect.py

  analysis/
    analyze.py
    summarize.py
    visualize.py

  benchmark/
    run_cvc.py
    package_cvc.py
```

Rules:

- Scripts stay thin and call package APIs.
- No experiment logic lives in scripts.
- Scripts refuse to overwrite completed results unless passed an explicit flag.
- Partial outputs are first-class: either resumable or clearly marked incomplete.
- Batch names should be stable and meaningful.
- Every canonical run writes provenance.

Canonical output shape:

```text
results/<batch_name>/
  manifest.json
  <config_slug>/
    config.json
    results.csv
    results_partial.csv
    analysis/
      summary.json
      figures/
```

Every meaningful run also gets:

```text
docs/results/runs/<batch_name>.md
```

That docs entry records purpose, config, commit, branch, seed count, run date, analysis outputs, and interpretation status.

---

## Verification strategy

This restructure changes a lot of names, paths, and boundaries, so tests are not a final checkbox. They are part of the migration design.

### Unit tests

Each package move or extraction should carry focused unit tests for the surface it touches:

- `aif/`: inference, policy construction, EFE, learning updates, beta dynamics, PRNG behavior, and public API imports
- `tasks/trust/`: payoff encoding/decoding, stance transitions, model matrix shapes, environment step semantics, partner observations, affective/lesioned agent behavior, and trust-specific rollout helpers
- `experiments/`: config parsing, condition mapping, factory construction, logger schema, batch metadata, partial-output behavior, and multi-focal round resolution
- `analysis/`: hypothesis metrics, model-fitness versus reward controls, post-switch windows, partner-selection summaries, and result provenance parsing
- `scripts/`: argument parsing, path resolution, overwrite protection, and dry-run/inspect behavior
- `docs/state` and docs links: current mission/state files exist, no broken markdown links, no stale H-number surfaces outside explicitly historical docs

Every moved public import should be covered either by a direct import test or by a higher-level construction test. Import-boundary tests should assert that `aif/` does not import `tasks`, `experiments`, `analysis`, or `benchmarks`.

### Lightweight end-to-end tests

Add end-to-end tests that prove wiring works without running full experiments:

- instantiate each supported trust config and construct its model/env/agent objects
- run one or two rounds for representative no-affect, affective, lesioned, and clinical presets
- run one tiny multi-focal round loop and assert schema shape
- run the experiment script in smoke/dry-run mode and assert output manifests/provenance
- run analysis on a tiny synthetic or tiny generated result table
- exercise partial-output inspection without launching a long batch
- verify package discovery from an editable install or equivalent build metadata

These tests should be fast enough for normal `pytest`. Slow statistical/emergent tests can stay gated, but the core code-moving confidence should come from always-on unit and lightweight e2e coverage.

### Verification gates

Each implementation phase should end with:

```bash
python -m pytest tests/ -q
python -m ruff check .
python -m mypy
git diff --check
```

When a phase changes docs, also run doc-link and stale-label validators once they exist.

---

## Notebooks and references

No new notebooks are part of this restructure.

Target layout:

```text
notebooks/
  references/
    apashea_trust_spec.ipynb
```

Rules:

- Keep notebook 4 as a reference because it explains the apashea math choices and selective deviations.
- Delete notebooks 1-3 rather than preserving stale demos.
- Do not rebuild tutorials or diagnostics yet.
- If future notebooks are added, they inspect or explain results. They are not the canonical way to produce results.

---

## Docs and state

Docs become the canonical project memory.

Target docs layout:

```text
docs/
  README.md

  theory/
    README.md
    goals.md
    hypotheses.md
    pomdp_spec.md
    apashea_alignment.md

  experiments/
    README.md
    trust/
      protocol.md
      configs.md
      analysis.md
    multifocal/
      protocol.md
      configs.md

  results/
    README.md
    current.md
    historical_findings.md
    runs/

  design/
    aif.md
    task_packages.md
    trust.md
    benchmarks.md

  state/
    README.md
    current/
      mission.md
      next_runs.md
      blockers.md
    decisions/
      architecture.md
      experiments.md
    handoffs/

  operations/
    cli.md
    mango.md
```

### Deletion policy

No archive junk drawer. For outdated files:

1. salvage useful content into current docs
2. keep a clearly named reference only if it explains current math or decisions
3. delete the old file

Specific decisions:

- `docs/paper/`: salvage useful theory/results language, then delete. The paper will be rewritten later from current docs.
- `conductor/MISSION.md` and `conductor/STATE.md`: disperse useful content into `docs/state/`, then delete `conductor/` if nothing current remains.
- old notebooks: delete 1-3, keep the apashea reference.
- old configs/scripts/code: delete if unsupported.

### `docs/state/` purpose

`docs/state/` is the context steering wheel for agents. It answers:

- What is the active mission?
- What is blocked?
- What should run next?
- What decisions are already settled?
- What results are current versus historical?
- What did the last session hand off?

---

## Merge-readiness before the big restructure

Before merging the current branch to the repo's primary branch (`master`), keep the patch narrow:

- Add `aif*` and current task packages to `pyproject.toml`.
- Fix `ruff`.
- Fix `mypy`.
- Fix `git diff --check`.
- Fix only the highest-risk broken links.
- Run `pytest`, `ruff`, and `mypy`.
- Merge.

Do not mix the big folder restructure into the merge-readiness patch.

Known current checks from the context pass:

- `pytest tests/ -q`: 338 passed, 13 skipped, 2 scipy warnings.
- `ruff`: currently failing with mechanical/import/type-style issues.
- `mypy`: currently failing with 6 errors.
- `git diff --check`: currently failing on trailing whitespace in superpowers docs.
- `pyproject.toml`: currently omits `aif*` and `trust*` from package discovery.

---

## Execution sequence

### Phase 0: Merge-readiness patch

Make the current branch shippable without moving the world.

### Phase 1: Context reset

Create `docs/state/`, salvage current mission/state/paper content, delete stale sources, and rewrite theory goals/hypotheses around the Hesp extension.

### Phase 2: Experiment surface cleanup

Replace old hypothesis drift with the approved H1-H7 surface. Rename or delete configs. Add a manifest mapping hypothesis to config to analysis output.

### Phase 3: Code topology

Move `trust/` and `env/` into `tasks/trust/`. Move trust-task baselines/evaluation out of top-level `benchmark/`. Move experiment orchestration into `experiments/trust/` and `experiments/multifocal/`. Update imports directly and delete old paths unless a one-commit shim is truly necessary.

This phase should be behavior-preserving except for import paths and file locations. It should not quietly change numerical semantics, RNG behavior, or experiment interpretation.

### Phase 4: JAX core hardening

After topology is stable, harden `aif/` as a JAX-based reusable core. Convert remaining public numerical core surfaces to JAX-compatible arrays and explicit PRNG-key APIs where needed. Keep this separate from file moves so numerical changes have their own tests, tolerances, and review.

Verification expectations for this phase:

- public `aif/` numerical APIs work with `jax.numpy` arrays
- policy sampling takes explicit PRNG keys and avoids hidden RNG state
- JAX/NumPy parity tests cover representative inference, EFE, learning, and beta paths
- task-level behavior tests define acceptable numerical tolerances
- no trust-specific imports enter `aif/`

### Phase 5: Scripts and benchmarks

Split scripts into experiment, analysis, and benchmark folders. Move/adapt CvC code to follow the new `benchmarks/cvc/` structure, but do not make CvC functionality a blocker for this restructure. If CvC tests already pass, keep them passing; if the track is stale or environment-dependent, isolate it behind explicit tests/docs so it does not block the trust-task cleanup.

### Phase 6: Sync primary workspace

After local verification and merge, sync the cleaned primary branch/workspace on Mango's main MacBook Air server using the project Mango workflow. Do not add deployment/orchestration scripts to this repo; use Mango as the external sync/run tool and record the sync status in `docs/state/`.

### Phase 7: Rerun experiments

After architecture, hypothesis cleanup, and Mango sync, rerun priority experiments:

1. shallow affect / tau 1-3
2. partner selection
3. betrayal / stance switch
4. clinical perturbations
5. graded precision-channel tests
6. multi-focal descriptive runs

---

## Implementation choices

The following choices are settled for the implementation plan:

1. Keep the name `analysis/hypotheses.py`, but rewrite it around the new Hesp-extension hypotheses rather than the old drifted H1-H5 suite.
2. Prefer direct import updates and deletion of old paths. Use compatibility shims only when needed to keep an intermediate commit testable, and delete them before the phase is considered complete.
3. Adapt CvC code to the new `benchmarks/cvc/` structure, but do not treat CvC runtime success as a blocker for the trust/AIF restructure.
4. Move to plural `experiments/` as the target package. Temporary `experiment/` shims are allowed only as short-lived migration scaffolding.
5. Result index entries should be generated by scripts when possible, with manual interpretation added afterward by the researcher/agent.
6. Mango sync is part of completion: after local verification and merge, sync on the Mango main MacBook Air server and record status under `docs/state/`.

---

## Acceptance criteria

The restructure is done when:

- `aif/` is a reusable, JAX-oriented core with no task imports.
- Public `aif/` numerical APIs are JAX-compatible, use explicit PRNG-key APIs for randomness, and avoid hidden NumPy RNG in core inference/planning paths.
- Trust-game code lives under `tasks/trust/`.
- The old root `trust/` and `env/` packages are gone or are temporary shims with a deletion date.
- Trust-task evaluation is no longer described as a separate "trust benchmark."
- Docs state the Hesp-extension project goal clearly.
- Current hypotheses H1-H7 are documented and mapped to configs.
- `docs/state/` replaces conductor state as the agent steering surface.
- `docs/paper/` has been salvaged and deleted.
- Only the apashea reference notebook remains.
- Supported scripts are organized by execution role.
- New canonical runs write provenance and docs result entries.
- Unit tests cover moved public surfaces and import boundaries.
- Lightweight end-to-end tests cover config construction, tiny runs, script smoke/dry-run behavior, analysis on tiny results, and provenance output without running full experiments.
- CvC code follows the new `benchmarks/cvc/` structure without blocking trust-task verification.
- The cleaned branch/workspace is synced on Mango's main MacBook Air server and the sync status is recorded in `docs/state/`.
- Full verification passes: tests, lint, type checks, and doc-link checks if added.

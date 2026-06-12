# Future Work

> **Paper boundary.** The current manuscript is mechanism evidence for
> partner-local affective precision as a relationship-specific
> confidence/deployment signal. Evidence is limited to one focal active-inference
> agent interacting with scripted environment-side partners in a graded
> multi-partner trust game. Everything below is future-facing, exploratory, or
> implemented-but-not-paper-evidence. None of it supports or extends the current
> paper's result claims unless explicitly rerun, reviewed, and promoted into the
> paper reproduction surface.

## Manuscript Evidence Hygiene (Near-Term Doc Maintenance)

Treat `results/paper/` as canonical for promoted paper runs. Before adding new
interpreted claims, reconcile:

1. `docs/results/current.md` and `docs/manuscript/notes/figures_tables.md`
2. each paper section → `results/paper/<id>/` → promoted `docs/manuscript/source_tables/` copy
3. `scripts/analysis/make_paper_figures.py`, `analysis/phenotypes/`, and appendix protocol text in `docs/manuscript/appendix/`

Remove or relocate stale compact CSVs and dead figure-builder fallbacks that
could silently repoint figures to superseded diagnostics (for example old H3
locality probes when `h1_model_fitness_confirm/` is the §3.1 canonical source).
Do not refresh interpreted result numbers without checking
`docs/results/current.md`.

**Artifact traceability** (partially in place):

- Eq. 1--4 → implementation: `docs/overview/core/equation_traceability.md`
- Figure → source table → builder: `docs/results/provenance.md`
- Remaining: per-run manifests that pin config, commit, seed, and analysis entry
  point; deterministic unit tests for payoff, transition, beta, and entropy
  calculations; and a single documented command that regenerates all manuscript
  figures from promoted `results/paper/` batches.

Active handoff: `docs/handoffs/2026-06-11-manuscript-source-tables-cleanup.md`.

## Future Analysis And Evaluation Roadmap

Compact index of candidate analyses and extensions. Implement new metrics under
`analysis/` and `scripts/analysis/`; round-level fields already exist in
`experiments/trust/logger.py` (`betas`, `local_betas`, `prediction_errors`,
`predictive_log_lik`, `q_pi_entropy`, `payoff`, partner-selection fields).

### Calibration Diagnostics (Deferred)

Add after the current manuscript packet stabilizes. All are analysis-only until
reviewed and documented in `docs/results/diagnostics.md`:

- **Response NLL:** per-round predictive log likelihood (already logged as
  `predictive_log_lik`); aggregate by variant, partner, and epoch.
- **Brier score:** squared error between predicted partner-action probabilities
  and realized actions.
- **Calibration curves:** reliability diagrams binned by predicted probability;
  compare affect variants on sharpness vs calibration, not payoff alone.
- **Locality leakage:** whether partner-*k* `beta` (and derived `gamma`) correlates
  with non-*k* partners' surprisal or payoff; should stay weak if locality holds.
  Complements H3 locality probes in `configs/diagnostics/`.
- **Confidence hysteresis:** area under `beta` trajectories after betrayal and
  repair epochs; compare profiles that differ in revision speed vs reengagement.

### Other Derived Diagnostics From Existing Logs

- **Overcommitment and calibration cost:** post-switch payoff loss per unit entropy
  reduction relative to no-affect. Pairs with confidence hysteresis (above) and
  reallocation efficiency (below) to quantify the cost of stale confidence.
- **Reallocation efficiency:** payoff recovery per unit reduction in betrayed-partner
  selection; ties to agent-choice H4 probes and betrayal-boundary runs.
- **Deployment mediation:** path from partner-response surprisal → `beta` → `gamma`
  → `q_pi_entropy` / payoff via lagged or structural summaries on logged
  trajectories; distinct from partner-state inference accuracy. Natural companion
  visualization: mediation diagrams from surprisal through beta and gamma to
  entropy and payoff.

### Parameter Recovery And Seed-Matched Replay (Deferred)

- **Parameter recovery:** fit `alpha_charge`, `beta_persistence`,
  `initial_beta` / `initial_beta_prior`, and gamma coupling to synthetic or
  human iterated trust-game time series; verify identifiable recovery on known
  ground-truth variants before human fitting claims.
- **Seed-matched replay:** permute partner labels or replay identical seeds across
  affect variants to confirm metrics are not artefactual; pair with label
  invariance checks on allocation and calibration readouts.

### Statistical And Visualization Extensions (Deferred)

Complement the metrics above with readouts that make calibration and deployment
costs visible:

- signed coefficient plots with uncertainty intervals
- partner-wise calibration plots (extends reliability diagrams above)
- beta heatmaps over partner × round
- betrayal-repair hysteresis loops (visual companion to confidence hysteresis)
- mediation diagrams for the surprisal → beta → gamma → entropy/payoff path

### Construct Validity And Task Limits

Treat the graded trust game as a controlled proxy, not a complete measure of
human trust. A future empirical/theory note should connect the task to
trust-game construct-validity work and document limits such as social-preference
confounds, interpersonal risk, and paradigm stability before stronger human or
clinical claims.

### Architectural Extensions

- Embed `beta` as a proper hidden state rather than an auxiliary tracker
  (`DiscreteBetaState` today); allow expectations over future action confidence.
- **Richer response modalities:** test whether partner-response likelihood
  surprisal generalizes beyond binary cooperate/defect by adding graded
  reciprocity, delayed reciprocity, noisy communication acts, or richer
  observation alphabets.
- Add volatility or changepoint detection that discounts stale confidence after
  structured prediction-error shifts (see `configs/future/mixed_volatility.toml`
  as an exploratory environment, not a paper probe).
- Split precision into within-partner commitment precision versus cross-partner
  choice precision instead of a single `gamma_k` readout.
- Add structure learning so persistent low confidence can trigger search for a
  better partner model, not only lower policy precision.
- Extend from scripted partners to reciprocal active-inference partners in
  `experiments/multifocal/` (prototype only; see below).

### Empirical And External Benchmark Extensions

Keep all of the following outside the current paper unless explicitly rerun,
reviewed, and promoted:

- Fit `alpha_charge`, `beta_persistence`, `initial_beta` / `initial_beta_prior`,
  and gamma coupling to human iterated trust-game time series.
- Test whether predictability/value, deployment/inference, and
  reengagement/confidence-restoration dissociations appear in humans.
- **External generalization benchmarks:** closest-domain iterated trust data;
  zero-shot partner generalization environments; human-proxy coordination
  benchmarks; and larger mixed-motive social-dilemma suites.
- Treat clinical or attachment-style labels only as computational profile
  hypotheses unless separately validated (see phenotype configs and
  `analysis/phenotypes/`).

Status: analysis-only; not manuscript evidence until reviewed and documented in
`docs/results/`.

### Non-Goals For The Current Paper

- Do not treat mixed-volatility (`configs/future/mixed_volatility.toml`) as
  manuscript evidence.
- Do not claim payoff improvement as the main criterion for the mechanism; the
  paper targets calibration and deployment signatures.
- Do not claim clinical validation from profile perturbations.
- Do not claim reciprocal multi-agent AIF results (`experiments/multifocal/`)
  are part of the paper.

---

## Reciprocal AIF Partners (Deferred Public Docs)

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
- **No reciprocal-AIF public docs until promotion:** do not add overview,
  experiment, or result cards for multifocal runs until the prototype becomes a
  supported public surface.

Promotion checklist before public docs:

1. Decide whether reciprocal AIF-vs-AIF is a manuscript extension, a separate
   follow-up project, or a supplemental demonstration.
2. Add a public runner path only after the output schema and analysis questions
   are settled.
3. Move or mirror configs into `configs/future/multifocal/` when promoted.
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

See **Architectural Extensions** in the evaluation roadmap above for the
supported list. Additional theory-facing items:

- richer theory-of-mind partner models while keeping affective precision as the
  confidence/deployment layer rather than the content of partner inference
- delayed reward, coalition or group structure, and richer partner dynamics
  beyond the current graded binary-response surface

## Heterogeneous Volatility Extension

The mixed-volatility config is implemented under
`configs/future/mixed_volatility.toml`, but it is not part of the current paper
evidence and must not be cited as supporting the present manuscript. Compact
outputs belong under `results/future/mixed_volatility/`; do not regenerate
manuscript `source_tables/` or figures from this config unless a future study
explicitly promotes it.

The issue is not that the environment is weak. The issue is that once it appears
in the appendix it stops being merely extra: readers can reasonably ask what
the discrimination index measures, why higher gain can improve payoff while
worsening discrimination, what P0 confidence-drop metrics mean, whether that
contradicts the main calibration claim, and whether the paper has become a
volatility-learning paper.

Treat this as a real follow-up extension. A future version should define the
volatility-learning question explicitly, add a change-detection account, and
decide whether payoff, discrimination, stable-partner confidence retention, or
adaptation speed is the primary target before reporting the results.

## Anonymous Public Release Packaging (Deferred)

Before distributing a public branch or zip:

- Hide or clearly mark non-paper maintainer scratch: `docs/active/`, `AGENTS.md`,
  `docs/superpowers/`, `docs/handoffs/`, `docs/manuscript/notes/`,
  `docs/results/cleanup/`.
- Keep `docs/overview/core/`, `docs/experiments/`, `docs/results/current.md`,
  `docs/results/provenance.md`, `configs/paper/`, and `docs/manuscript/` as the
  paper reproduction surface.
- Do not imply `configs/future/` probes are manuscript evidence.

## Task And Evaluation Extensions

Noisy observations and larger action spaces are covered under **Richer response
modalities** above. External benchmark candidates are listed under **Empirical
And External Benchmark Extensions**.

If a supported benchmark/evaluation arena is revived, it needs a concrete
baseline question. The old benchmark branch explored trust-task baseline
comparisons against agents such as random, tit-for-tat, Pavlov, and grim
trigger. Any revival should stay separate from paper experiments, with its own
result cards and no implication that it is manuscript evidence unless explicitly
run and reviewed.

# H6 Follow-Up And Paper Consolidation Design

## Purpose

Advance the trust-task manuscript on four coordinated lanes without letting
exploratory evidence overrun the current claim boundaries.

The next phase should answer whether partner-local affective precision is doing
work beyond a shared model-fitness tracker, improve the ablation map only after
the current global-beta discovery outputs are reviewed, make paper figures
reproducible from source tables, and revise the manuscript so it reads as a
scientific argument rather than an internal hypothesis scorecard.

## Context

The current interpreted evidence is H0-H5 on the supported
`inferactively-pymdp==1.0.0` trust-task runtime. The H6 global-beta condition,
locality/interference smoke config, and analysis hooks already exist. A
one-worker discovery run is active under:

```text
results/h6_global_beta_discovery_20260525/
```

The active docs explicitly keep H6 as discovery evidence until the user reviews
the results. Do not update manuscript interpretation or `docs/results/current.md`
from H6 outputs without that review.

## Lane A: H6 Manuscript Evidence Gate

### Goal

Convert the current H6 discovery batch into a concise evidence memo and a
claim recommendation for user review, not immediate manuscript text or result
documentation.

### Procedure

When the current run finishes, verify that each probe has a final
`results.csv`, not only `results_partial.csv`:

- `global_beta_model_fitness_probe`
- `global_beta_deployment_probe`
- `global_beta_partner_choice_probe`
- `global_beta_betrayal_probe`
- `lesion_family_probe`

Run standalone analysis on every completed result directory:

```bash
python scripts/analysis/analyze.py \
  --results results/h6_global_beta_discovery_20260525/h6/<experiment_id>/results.csv \
  --output-dir results/h6_global_beta_discovery_20260525/h6/<experiment_id>/analysis
```

Inspect at minimum:

- `final_round_summary.csv`
- `affective_movement_summary.csv`
- `partner_choice_summary.csv`
- `evidence_effect_summary.csv`
- `model_fitness_correlation_summary.csv`
- `deployment_dissociation_summary.csv`
- `cross_partner_interference_summary.csv`
- `global_vs_local_beta_summary.csv`
- betrayal reallocation and misdeployment summaries for switch probes

### Recommendation Rules

Recommend promoting locality only if `global_beta` produces measurable
cross-partner interference: shared beta/gamma changes spill into untouched
partners, selection or entropy shifts after a localized switch, or reallocation
is blurrier than `local_beta`.

Recommend softening locality if `global_beta` matches `local_beta` across
model-fitness, deployment, partner-choice, and betrayal readouts. In that case,
the manuscript should describe partner-local beta as an interpretable
implementation rather than a demonstrated necessity.

Do not use payoff alone as the H6 criterion. Stop after the recommendation memo;
the user must approve before any H6 interpretation is promoted into
`docs/results/current.md`, active result docs, or manuscript prose.

## Lane B: Mechanism Mapping

### Goal

Map which parts of the affective-precision channel matter: beta learning,
deployment into gamma, lag, noise, asymmetric surprise, and shock timing.

### Sequence

Lane B planning can proceed in parallel with Lane A, but new mechanism configs
or runtime changes should wait until the existing H6 discovery outputs and
logging are clean. If they are clean, add one tiny graded-betrayal smoke with
three seeds and `--workers 1`:

- `local_beta`
- `global_beta`
- `tracked_only`
- `frozen_beta`
- `delayed_deployment`

Only after that smoke is interpretable, add a second three-seed smoke for:

- `noisy_beta`
- `asymmetric_charge`
- `joint_surprise_beta`
- one early and one late shock timing variant

### Required Readouts

Report dynamics before payoff:

- beta range and beta trajectory
- deployed `gamma_used`
- gamma source: local, global, frozen, delayed, or fixed
- raw prediction error or surprise feeding beta
- partner selection entropy and choice churn
- post-shock return latency
- wrong-type-on-return or other misdeployment readouts
- untouched-partner entropy/payoff after a shock elsewhere

Stop and ask before full runs or interpretation changes if `global_beta` matches
`local_beta`, if `tracked_only` diverges unexpectedly from `no_affect`, or if
shock timing reverses the qualitative story.

## Lane C: Figure And Review Infrastructure

### Goal

Make the manuscript figures reproducible from canonical source tables and
reduce manual figure drift.

### Current Coverage

`scripts/analysis/make_paper_figures.py` already generates:

- deployment and social-choice summary
- shock-shape summary
- perturbation phenotype summary

It does not yet regenerate the H1 model-fitness dissociation or the H3 betrayal
boundary figure from source tables.

### Required Additions

Use canonical source tables under
`docs/paper/manuscript/source_tables/`. Add script-generated PNG/PDF outputs
for:

- H1 model-fitness dissociation from
  `docs/paper/manuscript/source_tables/h1_evidence_effect_summary.csv` and
  `docs/paper/manuscript/source_tables/h1_model_fitness_correlation_summary.csv`
- H3 betrayal boundary from
  `docs/paper/manuscript/source_tables/h3_evidence_effect_summary.csv`,
  `docs/paper/manuscript/source_tables/h3_betrayal_reallocation_summary.csv`,
  and
  `docs/paper/manuscript/source_tables/h3_betrayal_misdeployment_summary.csv`

The script should fail clearly on missing files or columns and print a manifest
of generated assets. Statistical annotations may use existing source-table
values; do not recompute experiments inside the figure script.

## Lane D: Manuscript Prose Cleanup

### Goal

Remove dev-facing hypothesis-table or scorecard framing from the paper. The
paper should state the scientific argument directly in prose.

### Scope

Edit only manuscript text files under `docs/paper/manuscript/` unless a local
compile or figure reference requires a small adjacent update. Do not change
code, configs, result source tables, or H6 interpretation.

### Writing Direction

Results should present observations, effect directions, uncertainty, and figure
references. Discussion should state what the pattern means, where it is
bounded, and what remains untested.

Replace internal H0-H5 table framing with prose such as:

- model-fitness dissociation: precision tracks surprise more than reward
- deployment: precision changes action policy in open regimes despite similar
  belief accuracy
- social choice: precision shifts partner selection before payoff separates
- betrayal: abrupt shocks expose misdeployment risk rather than simple recovery
- perturbations: dynamics separate phenotypes more clearly than payoff

Do not claim H6/global-beta results in the manuscript until the user approves
the H6 evidence read.

## Cross-Lane Coordination

- Lane A may read H6 results but should not edit manuscript claims.
- Lane B may plan in parallel, but may add configs or code only after Lane A
  establishes that current H6 outputs and logging are clean.
- Lane C may edit figure scripts and figure documentation, but not manuscript
  interpretation.
- Lane D may edit prose using existing H0-H5 evidence only.
- Keep run commands at `--workers 1`.
- Do not launch runs expected to exceed 30 minutes without explicit approval.
- Fix the stale docs-state test that still expects `docs/active/handoff.md`;
  the current active docs say the live handoff is the state/progress/blockers
  surface.

## Verification

Use the smallest relevant checks for each lane, then the shared gate before a
commit:

```bash
.venv/bin/python -m pytest tests/ -q
.venv/bin/python -m ruff check .
.venv/bin/python -m mypy
git diff --check
```

For manuscript prose changes, also compile the manuscript using the command
documented in `docs/paper/manuscript/README.md` or the local manuscript build
file.

## Deliverables

- H6 evidence memo for user review
- mechanism-mapping implementation plan and small smoke configs if approved by
  H6 diagnostics
- expanded paper figure-generation script and generated-file manifest
- revised manuscript prose without internal hypothesis-table framing
- updated active/progress docs only for provenance, not interpretation, unless
  the user explicitly approves an interpretation update

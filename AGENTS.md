# AGENTS.md — System Documentation

This document provides comprehensive system documentation for AI agents operating on the affect_aif codebase. It covers architecture, module interfaces, experiment pipeline, and operational procedures.

## Documentation First

- Read `docs/active/README.md`, `docs/active/state.md`,
  `docs/active/progress.md`, and `docs/active/blockers.md` before taking over
  a research or restructure task.
- Read `docs/handoffs/` only when a handoff is named, linked, newly created,
  or directly matched to the task. Handoffs are task-specific transfer packets,
  not part of the default active-doc read order.
- Read `docs/overview/hypotheses.md`, `docs/overview/pomdp.md`, and
  `docs/overview/affective_precision.md` before
  changing computational claims, affect dynamics, terminal values, or the
  interpretation of results.
- Read `docs/experiments/configs.md`, `docs/experiments/running.md`, and
  `docs/experiments/paper.md` before changing task design, configs, variants,
  metrics, or sensitivity sweeps.
- Read `README.md` before changing setup, entry points, or repo layout.

## Graphify Context First

- For any non-trivial codebase task, use Graphify for orientation before broad raw-file exploration. Start with the Graphify MCP server when available (for example `god_nodes` and `shortest_path` around user-named concepts), then use the graph results to choose which files to inspect.
- Before architecture or codebase-navigation questions, read `graphify-out/GRAPH_REPORT.md` if it exists.
- If `graphify-out/wiki/index.md` exists, navigate from there before opening many raw files.
- Treat Graphify as the map and raw files/tests as the source of truth for exact behavior, edits, and line references.
- If Graphify is missing, stale, or unavailable, say so explicitly and continue with targeted raw-file search.
- After modifying code structure, refresh the graph:

```bash
$(cat graphify-out/.graphify_python 2>/dev/null || printf python3) -c "from graphify.watch import _rebuild_code; from pathlib import Path; _rebuild_code(Path('.'))"
```

## Required Follow-Through

- If code behavior changes, update the relevant docs in the same change.
- If experiment assumptions change, update both theory-facing and experiment-facing docs.
- If configs or scripts change, update the README or implementation notes so the runnable workflow stays accurate.
- If tests reveal a theory/code mismatch, fix both the implementation and the docs before closing the task.

## Learned User Preferences

- Before updating result-interpretation docs from new experiment outputs, ask the user first.
- When the user asks about branch state, merge readiness, or pruning stale remote branches, run git (fetch or prune as needed) and summarise concrete outputs instead of only listing commands.
- For active-doc-driven research, treat `docs/active/state.md` as the source of truth for phase autonomy; do not default to “blocked” framing when the mission tells the agent to proceed or to choose the next phase.
- For manuscript work, keep pending experiment work in `docs/active`; use confirmed results and placeholders in the manuscript, do not invent results or alter core technical content, do not state that experiments still need to run, strip all internal draft/process language (e.g., submission strategy, pending confirmation, smoke, post-fix), and write in direct computational-paper style with American English (behavior, modeling, formalize, characterize). Result-led phrasing; avoid meta-commentary such as "this paper argues," "central contribution," or defensive "not X but Y" unless necessary. When the user supplies numbered exact LaTeX edits, apply them verbatim in order without unsolicited style or wording changes. When compressing Methods, keep the payoff table, scripted-partners disclaimer, and core equations in main text; replace appendix duplicates with cross-references rather than repeating equations. For Results subsections: open on findings or live questions, not Methods-style setup; use "by construction" for design-guaranteed mechanism claims (not "expected to track"); state analytic rationale before numbers and interpret tables/bootstrap CIs explicitly; own adverse or null payoff results without hedging; section closers forward-handoff to the next question; multi-experiment sections need an orienting sentence mapping experiments to questions; place human-behavior disclaimers in Discussion limitations, not Results openings. When the user supplies critique plus suggested rewrite for Results, apply the rewrite (LaTeX-adapted) after verifying numbers against `docs/results/current.md` and source tables, and sync `docs/manuscript/notes/claims_and_evidence.md` and `docs/manuscript/notes/figures_tables.md`.
- In manuscript prose, use partner-local β_k versus shared β (not "global beta"); β_k is inverse precision (higher β_k = lower confidence, lower β_k = higher γ_k); describe reliability via q(β_k), β_k-derived policy precision γ_k, or confidence signal—not raw β_k increasing with reliability; use "exploratory diagnostic" not "smoke" or "post-fix" in reader-facing text.
- Manuscript figure captions describe plotted panels only; soften partner-allocation and other unshown behavioral claims; use exact statistics and reviewer-proof wording.
- In manuscript main text, use profile/profile-style language by default; say "profile-style parameter variation" not "perturbations" in reader-facing text; reserve "phenotype" for appendix experiment names and table labels. For clinical-adjacent claims, use "computational profile", "computational analogue", or "phenotype-inspired computational variants" — not clinical validation, diagnosis, or "clinical-style".
- When manuscript framing changes, update supporting manuscript docs under
  `docs/manuscript/` to match; do not silently rewrite `docs/results/`
  interpretation. Frame the paper around social metacognition — separating partner-type inference, theory-of-mind, and model-fitness/confidence — not merely extending Hesp-style affective precision to trust games; in the abstract, tie metacognition to affective precision as a relationship-specific signal rather than social metacognition broadly.
- Frame the paper as a first-step relationship-specific confidence-calibration mechanism, not a general payoff-improvement claim; strongest evidence is predictability-over-value, deployment-over-inference, and partner-local-over-shared dissociations; treat payoff as a downstream consequence of calibration interacting with task structure. Do not overclaim behavioral superiority for partner-local β; the shared-β section is a mechanistic relational-specificity test, and a direct mixed-volatility local-vs-shared behavioral comparison remains future work; use conditional phrasing for tests not yet run (e.g., "would compare" not "compares"). In Discussion, contrast volatility models (belief update rate) with the present mechanism (action-expression strength via γ_k).
- When syncing to mango while remote experiments are running, do not stop or disrupt active sessions.
- Prefer hard renames without legacy code paths or deprecation aliases.

## Learned Workspace Facts

- Use `.venv` in project root; venv should auto-activate when in this folder (direnv with `.envrc`).
- Recommended paper reproduction route: `python scripts/experiment/run.py`
  with the `configs/paper/` files listed in `docs/experiments/paper.md`, using
  `--workers 1` unless the user explicitly authorizes more workers. Retained
  probes and reviewer controls live under `configs/diagnostics/`.
- Random-assignment specs are weak discriminators for the current hypothesis spine; use agent-choice scheduled-stance-switch specs for stress-response results.
- Official `inferactively-pymdp==1.0.0` is the supported runtime. Do not reintroduce a custom active-inference engine; keep affect and trust logic in task modules.
- State inference (partner-type belief updating) is handled by official
  `pymdp.Agent` instances created from `tasks.trust.pomdp` templates and logged
  as matrix-based belief updates.
- Paper reproduction configs are under `configs/paper/`, demo configs under
  `configs/demo/`, and diagnostic/smoke configs under `configs/diagnostics/`.
  The old benchmark integration is not part of the active public surface.
- Remote VMs, sync, and merge flows for this project use `mango` (CLI at
  `~/Desktop/mango/`, available globally). Key commands: `mango run affect_aif
  --cloud` to launch, `mango stop affect_aif --remote` to stop, and
  `mango cloud sync push/fetch affect_aif` to sync code/results (`sync push` is
  rsync and does not delete remote-only files under `results/`). Do not add
  orchestration or deployment scripts to this repo.
- Manuscript PDF builds in `docs/manuscript/` via `pdflatex` -> `bibtex` ->
  `pdflatex` x 2; output is `main.pdf`. Supplementary code link
  (`https://github.com/har5h1l/affect_aif`, placeholder for anonymous review)
  belongs in Appendix C (`appendix/appendix_c_protocols.tex`) after seed
  counts; update URL upon acceptance.
- Phenotype experiment summaries for the paper live in
  `docs/manuscript/source_tables/` with figures in `docs/manuscript/figures/`.
- Confirmed betrayal result (30-seed): partner-local affect lowers policy entropy and raises joint partner-type accuracy; payoff advantage is small with bootstrap CI crossing zero — not a payoff–accuracy tradeoff.
- Paper-support docs live under `docs/manuscript/`: `README.md`, `notes/`,
  LaTeX sections/appendix files, source tables, and figures. Interpreted
  evidence and headline numbers live in `docs/results/current.md`.
- Before changing manuscript statistics, verify against
  `docs/results/current.md` and `docs/manuscript/source_tables/`;
  after number changes, sync `docs/results/current.md`,
  `notes/claims_and_evidence.md`, and `notes/figures_tables.md`.

---

## Architecture

### Module Dependency Graph

```
affect_aif/
├── inferactively-pymdp==1.0.0  # Supported active-inference runtime dependency
├── tasks/
│   └── trust/             # Trust-task package
│       ├── envs/          # Binary and graded trust-game environments
│       ├── pomdp.py       # Native trust POMDP template and pymdp.Agent construction
│       ├── runtime.py     # PartnerBank and procedural plan/update helpers
│       ├── affect.py      # External HESP beta tracking
│       ├── evaluation/    # Trust-task evaluation arena and baselines
│       ├── payoffs.py     # Trust-game payoff and action encoding helpers
│       ├── stance.py      # Stance dynamics
│       └── types.py       # Partner type metadata
├── experiments/
│   ├── trust/             # Focal-agent paper experiments; depends on tasks.trust
│   │   ├── config.py      # ExperimentConfig runtime dataclass
│   │   ├── spec.py        # TOML ExperimentSpec and variant expansion
│   │   ├── runner.py      # ExperimentRunner for expanded variant runs
│   │   ├── batch.py       # BatchExperimentRunner (multi-config parallel)
│   │   ├── logger.py      # MetricLogger (per-round recording)
│   │   ├── progress.py    # ProgressReporter
│   │   └── factory.py     # Agent/model/environment factories
│   └── multifocal/        # Tested future AIF-vs-AIF extension, not paper evidence
│       ├── config.py      # Parses heterogeneous `agents: [...]` multi-focal JSON
│       ├── runner.py      # Multi-focal runtime
│       └── joint_resolution.py # Pairwise payoff obs from actions
├── analysis/              # Depends on: nothing (operates on DataFrames)
│   ├── metrics.py         # Summary statistics, betrayal analysis, movement
│   ├── statistics.py      # ANOVA, pairwise tests
│   ├── hypotheses.py      # Current Hesp-extension hypothesis helpers
│   ├── plots.py           # Matplotlib figure generation
│   └── visualization.py   # GIF generation
└── configs/               # Trust and trust-benchmark TOML configurations
```

### Experiment Variants

Trust experiments are declared as TOML specs under `configs/paper/` for the
current paper and `configs/diagnostics/` for retained probes. Each spec
expands explicit `[[variants]]` instead of numeric condition IDs or presets.

Core maintained variant knobs:

| Field | Examples | Meaning |
|----|------|-------|
| `affect` | `none`, `precision`, `tracked_only` | Runtime affect mode |
| `planning_horizon` | `1`, `2`, `4`, `8` | Native pymdp policy horizon |
| `epistemic_value` | `true`, `false` | Whether policy inference uses information gain |
| `alpha_charge`, `initial_beta`, `beta_persistence`, `beta_levels` | numeric / arrays | Affective precision dynamics |

### Experiment Pipeline Flow

```
TOML ExperimentSpec → expanded variant runs → ExperimentRunner
    │
    ├── run_all()                   # All expanded variant runs
    │   └── run_replication()       # Single variant × single seed
    │       ├── create_native_runtime_from_run() # Trust POMDP template + PartnerBank
    │       ├── _create_env()       # TrustGameEnv or GradedTrustGameEnv
    │       └── _run_episode()      # Main loop: infer policies → step → update
    │
    └── save_results()              # DataFrame → CSV
         │
         ▼
    scripts/analysis/analyze.py     # Post-hoc analysis
    ├── final_round_summary()
    ├── cumulative_payoff_anova()
    ├── pairwise_payoff_tests()
    ├── run_all_hypothesis_tests()
    ├── affective_movement_summary()
    └── save_all_figures()
```

### Native Runtime Lifecycle (per round)

```
select_decision(...)
    ├── Pick the active partner or evaluate each partner-local pymdp.Agent
    ├── Set partner-specific gamma from external beta when enabled
    ├── Call official pymdp.Agent.infer_policies(...)
    ├── Select a policy/action
    └── Return a Decision with raw env action and diagnostics

env.step(action)
    ├── Decode action → (partner_idx, agent_action)
    ├── Partner responds according to type strategy
    ├── Compute payoff
    └── Return observation dict

update_partner_after_observation(...)
    ├── Call official pymdp.Agent.infer_states(...)
    ├── Store partner-local posterior and next prior snapshots
    ├── [Affective] update external beta from prediction error
    └── Log snapshot fields for analysis
```

## Configuration System

Trust specs live in `configs/paper/`, `configs/demo/`, and
`configs/diagnostics/`. Multi-focal configs currently live in
`experiments/multifocal/configs/` as future-work JSON prototypes; they are
tested, but they are not executable through `scripts/experiment/run.py` and are
not used for paper evidence. `ExperimentConfig` is now an internal runtime
adapter derived from expanded TOML runs. Key runtime fields:

### Game Structure
- `payoff_mode`: "binary" | "graded"
- `num_partners`: default 4
- `num_rounds`: default 200
- `assignment_mode`: "random" | "agent_choice"
- `scheduled_stance_switches`: list of stance-shift events for betrayal-style scenarios

### Agent Parameters
- `planning_horizon`: planning depth, supplied by each variant before runtime construction
- `alpha_charge`: prediction error scaling (3.0)
- `sigma_0_sq`: prior variance (0.25)
- `initial_beta`: starting precision prior (1.0)
- `beta_num_levels`: number of discrete beta support points (default 5)
- `beta_persistence`: transition persistence for the beta posterior (0.8)
- `gamma`: base policy precision before partner-local beta modulation

### Run Parameters
- `replications`: seeds per variant in TOML experiment metadata
- `random_seed`: base seed
- `[[sweeps]]`: optional explicit variant-parameter expansion

## Analysis Outputs

`scripts/analysis/analyze.py --results <csv> --output-dir <dir>` produces:

| File | Contents |
|------|----------|
| `final_round_summary.csv` | Per-seed cumulative payoffs and accuracy |
| `pairwise_payoff_tests.csv` | All variant pairs: t-stat, p-value, Cohen's d |
| `hypothesis_tests.json` | Structured hypothesis test results |
| `hypothesis_summary.csv` | One-row-per-hypothesis overview |
| `affective_movement_summary.csv` | Beta / precision-signal range per seed |
| `statistics_summary.txt` | ANOVA + movement + betrayal summaries |
| `betrayal_*.csv` | (if switch events) Post-switch window analysis |
| `*.png` | Figures: payoff distributions, beta trajectories, etc. |

## Key Invariants

1. **Sophisticated inference**: Policy evaluation uses observation-branching, not mean-field rollout
2. **Native pymdp boundary**: policy/state inference stays inside official `pymdp.Agent`; task code only constructs matrices and manages partner-local beta/gamma
3. **Focal AIF, scripted partners**: reported trust experiments use a focal active-inference agent against environment-side parameterized partner policies; partners do not run `pymdp.Agent` or affective precision (see `docs/overview/pomdp.md`)
4. **Deterministic seeds**: `random_seed + replication_index` ensures reproducibility
5. **Variant equality**: same-horizon no-affect and tracked-only variants should match when precision is decoupled
6. **Binary saturation**: EFE gaps ~10.83 in binary game → softmax is hard argmax → precision modulation inert
7. **Graded activation**: q_pi_entropy ~5.8 in graded game → precision modulation channel active

## Troubleshooting

### Tests fail after code change
```bash
python -m pytest tests/ -v --tb=short
.venv/bin/python -m pytest tests/test_package_surface.py tests/test_supported_surface.py -q  # supported package surface
```

### Experiment produces unexpected results
1. Run with `--verbose --verbosity-mode stage_stream` for per-round tracing
2. Check beta/gamma traces and `q_pi_entropy` in the per-round results
3. Check current state in `docs/active/blockers.md`
4. Compare against current and historical status in `docs/results/`

### Analysis script errors
- Check CSV has expected columns: `variant_id`, `seed`, `round`, and `payoff`
- Filter or group by `variant_id` for hypothesis comparisons

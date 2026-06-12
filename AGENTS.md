# AGENTS.md - affect_aif Agent Guide

This file is the compact routing surface for agents working in this repository.
Use it to find the right context; do not treat it as a replacement for the
task-specific docs it points to.

## First Context

- For non-trivial codebase work, use Graphify before broad raw-file browsing:
  read `graphify-out/GRAPH_REPORT.md` when present, ask the Graphify MCP for
  high-connectivity nodes or paths around the named concept, then inspect the
  raw files and tests that matter.
- Before research, restructure, docs, experiment, result, or manuscript work,
  read `docs/active/README.md`, `docs/active/state.md`,
  `docs/active/progress.md`, and `docs/active/blockers.md`.
- Read `docs/handoffs/` only when a handoff is named, linked, newly created, or
  directly matched to the task. Handoffs are transfer packets, not default
  context.
- Read local `AGENTS.md` files as you enter subtrees; they narrow the rules for
  docs, configs, experiments, analysis, scripts, results, and manuscript work.

## Context By Task

- Setup, package surface, or repo layout: `README.md`, `pyproject.toml`,
  `scripts/README.md`, and `configs/README.md`.
- Computational claims, affect dynamics, terminal values, or result
  interpretation: `docs/overview/README.md`,
  `docs/overview/core/hypotheses.md`, `docs/overview/core/pomdp.md`, and
  `docs/overview/core/affective_precision.md`.
- Experiment design, config schema, variants, metrics, sweeps, or run
  procedures: `docs/experiments/README.md`,
  `docs/experiments/configs.md`, `docs/experiments/running.md`, and
  `docs/experiments/paper.md`.
- Diagnostic or future-only probes: `docs/experiments/diagnostics.md`,
  `docs/overview/extensions/future.md`, `configs/diagnostics/`, and
  `configs/future/`.
- Interpreted results, evidence boundaries, or provenance:
  `docs/results/README.md`, `docs/results/current.md`,
  `docs/results/paper.md`, and `docs/results/diagnostics.md`.
- Manuscript work: `docs/manuscript/README.md`,
  `docs/manuscript/notes/claims_and_evidence.md`,
  `docs/manuscript/notes/figures_tables.md`,
  `docs/results/current.md`, and the source tables under
  `docs/manuscript/source_tables/`.
- Debugging failing runs: start with `docs/active/blockers.md`,
  `docs/experiments/running.md`, the relevant config, the relevant runner or
  analysis module, and the smallest focused test.
- Public notebooks and demos: `notebooks/`, `docs/reproduce.md`,
  `configs/demo/`, and the matching `scripts/` entry points.

## Required Follow-Through

- If code behavior changes, update the relevant docs in the same change.
- If experiment assumptions change, update both theory-facing and
  experiment-facing docs.
- If configs, scripts, or supported entry points change, update `README.md`,
  `configs/README.md`, `scripts/README.md`, or `docs/experiments/` as
  appropriate.
- If result numbers, evidence tiers, or manuscript statistics change, verify
  against `docs/results/current.md` and source tables before editing prose; do
  not refresh interpreted result docs from new outputs without user approval.
- If tests reveal a theory/code mismatch, fix both the implementation and the
  docs before closing the task.
- After code structure changes, refresh Graphify:

```bash
$(cat graphify-out/.graphify_python 2>/dev/null || printf python3) -c "from graphify.watch import _rebuild_code; from pathlib import Path; _rebuild_code(Path('.'))"
```

## Coding Standard

- Prefer hard renames and direct replacements. Do not add backward-compatibility
  aliases, legacy code paths, wrapper scripts, old config names, or deprecation
  shims unless the user explicitly asks for a compatibility bridge.
- Keep the supported runtime boundary: official `inferactively-pymdp==1.0.0`
  handles policy and state inference; project code constructs matrices, task
  dynamics, affective precision state, logging, and analysis.
- Keep `tasks/trust/` independent of `experiments/` and `analysis/`.
  Experiment orchestration belongs in `experiments/trust/`; post-hoc work
  belongs in `analysis/` and `scripts/analysis/`.
- Preserve deterministic seeded behavior: runtime seeds derive from the config
  seed plus replication index unless the spec explicitly says otherwise.
- Use explicit TOML `[[variants]]` and documented sweeps. Do not revive numeric
  condition IDs, old presets, or the removed external benchmark integration.
- Keep public/manuscript surfaces graded-only unless the user reopens binary
  evidence. Binary outputs are diagnostic provenance.

## Server And Mango

- Development and light verification can happen anywhere, including local
  checkout work.
- Long experiments, sweeps, training jobs, simulator episodes, and expensive
  reproductions run on `server`, outside the Codex app-server process tree.
- Use the Mango workflow for server execution, repo sync, readiness, and
  process visibility. Before an expensive run, use `mango host preflight`; run
  in detached `tmux`; register with `mango process add`.
- Do not add orchestration or deployment scripts to this repo to replace Mango.
- Do not stop, clean, restart, or overwrite server-side runs/results unless the
  user explicitly authorizes that action and the live Mango/tmux/process state
  has been checked.

## Verification

- For behavior changes, prefer the smallest focused pytest first, then broaden
  to the gate in `docs/active/progress.md` when risk warrants it.
- Before scheduling full evidence runs, run the current verification gate from
  `docs/active/progress.md`.
- For docs-only routing changes, at minimum run `git diff --check` and the
  focused docs/link tests when available.

## Learned User Preferences

- Prefer minimal targeted manuscript edits with exact proposed diffs; compress prose rather than add filler.
- When manuscript layout work is in scope, visually inspect the compiled PDF for float gaps and page breaks before declaring it done.
- Preserve default LLNCS section/subsection spacing; do not over-compact headings with titlesec or custom titlespacing.
- Use "payoff" not "value" for measured outcome quantities in manuscript prose.
- Avoid over-prescriptive manuscript unit tests that ban ordinary wording (e.g. word deny lists).
- In affective-precision manuscript prose, distinguish the present mechanism from Hesp et al.; frame the signal as partner-response likelihood surprisal, not a policy-inference quantity or reward tracking.
- Prefer minimal equation or setup clarifications over full rewrites when reviewer feedback allows.

## Learned Workspace Facts

- Rebuild the manuscript PDF with `pdflatex` → `bibtex` → `pdflatex` → `pdflatex` in `docs/manuscript/`.
- Manuscript appendix layout: A = environment generative process, B = focal-agent POMDP, C = affective-precision update and policy selection, D = simulation protocols and metrics, E = extended profile and robustness results.
- Policy entropy documentation must match planner enumeration in `tasks/trust/pomdp.py`: graded runs use `num_controls=[1,6,6]` (36^4 factorized policies, capped at `max_policies=4096`); partner-choice conditions tile per-partner policies across partners. Do not cite max-entropy parentheticals without verifying this math.
- Manuscript float layout: Results figures use `[H]` with `\FloatBarrier`; put `\clearpage` only once before `\appendix` in `main.tex`, not before each appendix section.
- Appendix formatting in `macros.tex`: `\appendixfigure` height cap, `\Needspace` before dense tables, and inline `\(...\)` for short mid-sentence set definitions in appendices A/B (avoid mid-sentence `\[...\]` display math).

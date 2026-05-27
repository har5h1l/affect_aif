# affect_aif

Repository for trust-task wrappers, experiment runners, logging, and analysis built on official `inferactively-pymdp==1.0.0`.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

The supported developer workflow uses the editable install above.

## Supported Workflow

See [docs/active/README.md](docs/active/README.md) for current project state,
[docs/theory/goals.md](docs/theory/goals.md) and
[docs/theory/hypotheses.md](docs/theory/hypotheses.md) for the active
Hesp-extension framing, [docs/operations/cli.md](docs/operations/cli.md) for
the command-line reference, and [docs/results/README.md](docs/results/README.md)
for result status and provenance rules. See [docs/paper/README.md](docs/paper/README.md)
for the paper-facing claim, outline, literature, figure, and limitation packet.

The supported trust-game runtime is built on official `inferactively-pymdp==1.0.0`.
Project code owns trust-game model construction, affective precision tracking,
experiments, logging, and analysis.

The supported trust-game workflow uses the action-dependent, factorized-control
partner redesign:
- partner behavior depends on latent `type × stance`
- stance changes are action-dependent and can also be scheduled explicitly with `scheduled_stance_switches`
- binary trust games use factorized controls for partner, stance, and own action
- the trust-game generative model exposes `o_action` and `o_payoff` observations over latent `type × stance`, with `own_action` tracked as a separate control/state factor
- the default affective path uses the discrete HESP beta filter (`DiscreteBetaState`, `initial_beta=1.0`) driven by partner-action surprisal, `-log P(observed action)`
- the current hypothesis surface is the H0-H6 behavior-card spine in [docs/theory/hypotheses.md](docs/theory/hypotheses.md)
- runnable experiment specs are TOML files under `configs/`; trust specs live in `configs/trust/...`, benchmark specs in `configs/benchmark/...`, and each file declares a shared hypothesis/experiment/scenario/variant envelope with `experiment.family`

Common entry points:

```bash
python scripts/experiment/run.py --config configs/trust/hypotheses/h3_stress_response/betrayal_choice.toml --output-dir results --batch-name h3_stress_response --workers 1
python scripts/experiment/preliminary.py --replications 5 --output results/preliminary.csv
python scripts/analysis/analyze.py --results results/h3_stress_response/h3/betrayal_choice/results.csv --output-dir results/h3_stress_response/h3/betrayal_choice/analysis
python scripts/analysis/visualize.py --results results/h3_stress_response/h3/betrayal_choice/results.csv --output-dir results/h3_stress_response/h3/betrayal_choice/gifs
python scripts/analysis/model_comparison.py --results results/h3_stress_response/h3/betrayal_choice/results.csv --output-dir results/h3_stress_response/h3/betrayal_choice/model_comparison
python scripts/benchmark/run.py --config configs/benchmark/e1_arena/default.toml
python scripts/benchmark/analyze.py --results results/benchmark/benchmark_results.csv
```

## Repository Layout

- `inferactively-pymdp==1.0.0`: supported active-inference runtime dependency
- `tasks/trust/`: native trust POMDP templates, procedural pymdp runtime helpers, affect tracking, environments, and evaluation arena
- `experiments/trust/`: trust experiment spec parser, runtime adapters, and runner surface
- `experiments/multifocal/`: multi-focal trust experiment configuration and runtime
- `analysis/`: result loading, metrics, and visualization helpers
- `benchmarks/core/`: shared benchmark runner/config/comparison helpers
- `configs/`: public runnable TOML specs grouped by family (`trust/`, `benchmark/`)
- `docs/`: theory, experiment, implementation, results, and state notes
- `scripts/README.md`: supported CLI wrappers
- `tests/README.md`: supported verification surface

## Supported Surface

- The main package exposes the supported runner/config entry points at the top level.
- The trust-task evaluation arena is the supported task-comparison surface.
- The supported affective path is task-local precision tracking around official `pymdp` agents.
- Future-work experiment surfaces are documented in [docs/experiment/design.md](docs/experiment/design.md).

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

See [docs/state/README.md](docs/state/README.md) for current project state,
[docs/theory/goals.md](docs/theory/goals.md) and
[docs/theory/hypotheses.md](docs/theory/hypotheses.md) for the active
Hesp-extension framing, [docs/operations/cli.md](docs/operations/cli.md) for
the command-line reference, and [docs/results/README.md](docs/results/README.md)
for result status and provenance rules.

The supported trust-game runtime is built on official `inferactively-pymdp==1.0.0`.
Project code owns trust-game model construction, affective precision tracking,
experiments, logging, and analysis.

The supported trust-game workflow uses the action-dependent, apashea-aligned
partner redesign:
- partner behavior depends on latent `type × stance`
- stance changes are action-dependent and can also be scheduled explicitly with `scheduled_stance_switches`
- binary trust games use factorized controls for partner, stance, and own action
- the trust-game generative model exposes `o_action` and `o_payoff` observations over latent `type × stance`, with `own_action` tracked as a separate control/state factor
- the default affective path uses the discrete HESP beta filter (`DiscreteBetaState`, `initial_beta=1.0`)
- the current hypothesis surface is the H0-H5 behavior-card spine in [docs/theory/hypotheses.md](docs/theory/hypotheses.md)
- lesion, no-epistemic, and clinical runs are named presets (`lesioned`, `no_epistemic`, `alexithymia`, `borderline`, `depression`)

Common entry points:

```bash
python scripts/experiment/run.py --config experiments/trust/configs/h0_shallow_policy_regime.json --output-dir results --batch-name h0_openness_gate --workers 12
python scripts/experiment/preliminary.py --replications 5 --output results/preliminary.csv
python scripts/analysis/analyze.py --results results/h0_openness_gate/h0_shallow_policy_regime/results.csv --output-dir results/h0_openness_gate/h0_shallow_policy_regime/analysis
python scripts/analysis/visualize.py --results results/h0_openness_gate/h0_shallow_policy_regime/results.csv --output-dir results/h0_openness_gate/h0_shallow_policy_regime/gifs
python scripts/analysis/model_comparison.py --results results/h0_openness_gate/h0_shallow_policy_regime/results.csv --output-dir results/h0_openness_gate/h0_shallow_policy_regime/model_comparison
python scripts/benchmark/run_cvc.py --config configs/benchmark_default.json
python scripts/benchmark/analyze.py --results results/benchmark/benchmark_results.csv
```

## Repository Layout

- `inferactively-pymdp==1.0.0`: supported active-inference runtime dependency
- `tasks/trust/`: native trust POMDP templates, procedural pymdp runtime helpers, affect tracking, environments, and evaluation arena
- `experiments/trust/`: trust experiment configuration, conditions, and runner surface
- `experiments/multifocal/`: multi-focal trust experiment configuration and runtime
- `analysis/`: result loading, metrics, and visualization helpers
- `benchmarks/core/`: shared benchmark runner/config/comparison helpers
- `benchmarks/cvc/`: experimental CvC backend, policies, packaging, and Observatory client
- `configs/`: external benchmark and CvC JSON configurations
- `docs/`: theory, experiment, implementation, results, and state notes
- `scripts/README.md`: supported CLI wrappers
- `tests/README.md`: supported verification surface

## Supported Surface

- The main package exposes the supported runner/config entry points at the top level.
- The trust-task evaluation arena is the supported task-comparison surface; the local CvC path remains a separate experimental integration.
- The supported affective path is task-local precision tracking around official `pymdp` agents.
- Future-work experiment surfaces are documented in [docs/experiment/design.md](docs/experiment/design.md).

# affect_aif

Repository for reusable active-inference primitives, trust-task packages, experiment runners, and analysis scripts.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

`requirements.txt` remains available for compatibility, but the supported developer workflow uses the editable install above.

## Supported Workflow

See [docs/state/README.md](docs/state/README.md) for current project state,
[docs/theory/goals.md](docs/theory/goals.md) and
[docs/theory/hypotheses.md](docs/theory/hypotheses.md) for the active
Hesp-extension framing, [docs/operations/cli.md](docs/operations/cli.md) for
the command-line reference, and [docs/results/README.md](docs/results/README.md)
for result status and provenance rules.

The supported trust-game workflow uses the action-dependent, apashea-aligned
partner redesign:
- partner behavior depends on latent `type × stance`
- stance changes are action-dependent and can also be scheduled explicitly with `scheduled_stance_switches`
- binary trust games use factorized controls for partner, stance, and own action
- the trust-game generative model exposes `o_action` and `o_payoff` observations over latent `type × stance`, with `own_action` tracked as a separate control/state factor
- the default affective path uses the discrete HESP beta filter (`DiscreteBetaState`, `initial_beta=1.0`)
- the current hypothesis surface is H1-H7 in [docs/theory/hypotheses.md](docs/theory/hypotheses.md)
- lesion, no-epistemic, and clinical runs are named presets (`lesioned`, `no_epistemic`, `alexithymia`, `borderline`, `depression`)

Common entry points:

```bash
python scripts/run_experiment.py --config experiments/trust/configs/h6_shallow_policy_regime.json --output-dir results --batch-name h6_shallow_policy_regime --workers 12
python scripts/run_preliminary.py --replications 5 --output results/preliminary.csv
python scripts/run_analysis.py --results results/h6_shallow_policy_regime/h6_shallow_policy_regime/results.csv --output-dir results/h6_shallow_policy_regime/h6_shallow_policy_regime/figures
python scripts/run_visualization.py --results results/h6_shallow_policy_regime/h6_shallow_policy_regime/results.csv --output-dir results/h6_shallow_policy_regime/h6_shallow_policy_regime/gifs
python scripts/run_model_comparison.py --results results/h6_shallow_policy_regime/h6_shallow_policy_regime/results.csv --output-dir results/h6_shallow_policy_regime/h6_shallow_policy_regime/model_comparison
python scripts/run_benchmark.py --config configs/benchmark_default.json
python scripts/analyze_benchmark.py --results results/benchmark/benchmark_results.csv
```

## Repository Layout

- `aif/`: generic active-inference primitives
- `tasks/trust/`: canonical trust-game model, rollout helpers, agents, environments, and evaluation arena
- `experiments/trust/`: trust experiment configuration, conditions, and runner surface
- `experiments/multifocal/`: multi-focal trust experiment configuration and runtime
- `analysis/`: result loading, metrics, and visualization helpers
- `benchmark/`: external benchmark backends and comparison helpers
- `configs/`: external benchmark and CvC JSON configurations
- `docs/`: theory, experiment, implementation, results, and state notes
- `scripts/README.md`: supported CLI wrappers
- `tests/README.md`: supported verification surface

## Compatibility Notes

- The main package exposes the supported runner/config entry points at the top level.
- The trust-task evaluation arena is the supported task-comparison surface; the local CvC path and the scripted gridworld adapter remain separate compatibility paths.
- The discrete-beta prototype is archived; the supported affective path uses `aif.affect.beta.DiscreteBetaState`.
- Removed experiment surfaces (variational beta preset, `benchmark/aif_policy.py`) are not loaded by the runtime; see `docs/experiment/design.md` for future-work notes.
- Historical paper/archive/conductor findings are documented in [docs/results/historical_findings.md](docs/results/historical_findings.md) and are not current evidence unless rerun on the current architecture.

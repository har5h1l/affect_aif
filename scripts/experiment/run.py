"""CLI entry point for running batched experiments."""

# ruff: noqa: E402

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = str(Path(__file__).resolve().parent)
if sys.path and str(Path(sys.path[0]).resolve()) == SCRIPT_DIR:
    sys.path.pop(0)

import argparse
import json
import os
import subprocess

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def _ensure_writable_matplotlib_cache() -> None:
    if "MPLCONFIGDIR" in os.environ:
        return
    cache_dir = Path(os.environ.get("TMPDIR", "/tmp")) / "affect_aif_matplotlib"
    cache_dir.mkdir(parents=True, exist_ok=True)
    os.environ["MPLCONFIGDIR"] = str(cache_dir)


def _early_jax_cache_dir(argv: list[str] | None = None) -> str | None:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--jax-cache-dir")
    parsed, _ = parser.parse_known_args(argv)
    return parsed.jax_cache_dir or os.environ.get("AFFECT_AIF_JAX_CACHE_DIR")


def _configure_jax_compilation_cache(argv: list[str] | None = None) -> None:
    raw_cache_dir = _early_jax_cache_dir(argv)
    if not raw_cache_dir:
        return
    cache_dir = Path(raw_cache_dir).expanduser()
    cache_dir.mkdir(parents=True, exist_ok=True)
    os.environ["JAX_ENABLE_COMPILATION_CACHE"] = "true"
    os.environ["JAX_COMPILATION_CACHE_DIR"] = str(cache_dir)
    os.environ.setdefault("JAX_PERSISTENT_CACHE_MIN_COMPILE_TIME_SECS", "0")
    os.environ.setdefault("JAX_PERSISTENT_CACHE_MIN_ENTRY_SIZE_BYTES", "0")


_ensure_writable_matplotlib_cache()
_configure_jax_compilation_cache()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run one or more affect_aif experiments.")
    parser.add_argument(
        "--config",
        action="append",
        required=True,
        help="Path to a TOML experiment spec. Repeat to queue multiple specs.",
    )
    parser.add_argument("--output-dir", default="results", help="Root directory for batch output folders.")
    parser.add_argument("--batch-name", help="Stable card-root or batch output subdirectory.")
    parser.add_argument(
        "--workers", type=int, default=os.cpu_count() or 1, help="Shared worker count across the whole batch."
    )
    parser.add_argument("--verbose", action="store_true", help="Print experiment progress.")
    parser.add_argument(
        "--checkpoint-interval",
        type=int,
        default=1,
        help="Save partial results after this many completed replications per config.",
    )
    parser.add_argument(
        "--jax-cache-dir",
        help="Enable JAX persistent compilation caching in this directory for repeated same-shape runs.",
    )
    parser.add_argument(
        "--verbosity-mode",
        default="stage_stream",
        choices=["stage_stream"],
        help="Structured progress output mode for single-worker single-config runs.",
    )
    parser.add_argument(
        "--make-gifs", action="store_true", help="Generate one GIF per primary variant run after saving results."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate configs and write a batch manifest without running experiments.",
    )
    return parser


def _git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"
    return result.stdout.strip() or "unknown"


def _write_dry_run_manifest(args) -> int:
    from experiments.trust.batch import default_batch_id
    from experiments.trust.spec import load_experiment_specs

    batch_id = args.batch_name or default_batch_id()
    batch_dir = Path(args.output_dir) / batch_id
    batch_dir.mkdir(parents=True, exist_ok=True)

    config_entries = []
    for raw_path in args.config:
        config_path = Path(raw_path).resolve()
        for spec in load_experiment_specs(config_path):
            runs = spec.expand_runs()
            config_entries.append(
                {
                    "path": str(config_path),
                    "name": spec.experiment.id,
                    "family": spec.experiment.family,
                    "hypothesis_id": spec.hypothesis.id,
                    "experiment_id": spec.experiment.id,
                    "rounds": spec.experiment.rounds,
                    "replications": spec.experiment.replications,
                    "variants": [variant.id for variant in spec.variants],
                    "sweeps": [sweep.parameter for sweep in spec.sweeps],
                    "expanded_runs": len(runs),
                    "runtime_profile": spec.runtime.profile,
                    "analysis_auto": spec.analysis.auto,
                }
            )

    manifest_path = batch_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "batch_name": batch_id,
                "batch_id": batch_id,
                "git_commit": _git_commit(),
                "output_dir": str(batch_dir.resolve()),
                "workers": int(args.workers),
                "dry_run": True,
                "configs": config_entries,
            },
            indent=2,
        )
    )
    print(f"Dry-run manifest written to {manifest_path}")
    return 0


def _serial_single_config_run(args) -> int:
    from experiments.trust.batch import default_batch_id
    from experiments.trust.runner import ExperimentRunner
    from experiments.trust.spec import load_experiment_specs

    batch_id = args.batch_name or default_batch_id()
    config_path = str(Path(args.config[0]).resolve())
    loaded_specs = load_experiment_specs(config_path)
    if len(loaded_specs) != 1:
        return _batch_run(args)
    batch_dir = Path(args.output_dir) / batch_id
    spec = loaded_specs[0]
    if spec.experiment.family != "trust":
        raise ValueError("Only trust-family specs are executable through scripts/experiment/run.py.")
    config_name = spec.experiment.id
    config_dir = batch_dir / spec.hypothesis.id / spec.experiment.id
    results_path = config_dir / "results.csv"
    config_copy_path = config_dir / "config.toml"
    metadata_path = config_dir / "batch_metadata.json"
    runner = ExperimentRunner.from_spec(spec)
    config_dir.mkdir(parents=True, exist_ok=True)
    results = runner.run_all(
        config_path=config_path,
        config_name=config_name,
        batch_id=batch_id,
        checkpoint_path=str(config_dir / "results_partial.csv"),
        checkpoint_interval=args.checkpoint_interval,
    )
    runner.save_results(results, str(results_path))
    config_copy_path.write_text(Path(config_path).read_text(encoding="utf-8"), encoding="utf-8")
    metadata_path.write_text(
        json.dumps(
            {
                "batch_id": batch_id,
                "config_path": config_path,
                "config_name": config_name,
                "hypothesis_id": spec.hypothesis.id,
                "experiment_id": spec.experiment.id,
                "results_path": str(results_path),
                "runtime_profile": spec.runtime.profile,
                "workers": 1,
            },
            indent=2,
        )
    )
    if spec.analysis.auto:
        from analysis.configured import run_configured_analysis

        run_configured_analysis(spec, results_path, config_dir)
    print(f"Saved {len(results)} rows to {results_path}")
    return 0


def _batch_run(args) -> int:
    from experiments.trust.batch import BatchExperimentRunner, default_batch_id
    from experiments.trust.spec import load_experiment_specs

    for raw_path in args.config:
        for spec in load_experiment_specs(raw_path):
            if spec.experiment.family != "trust":
                raise ValueError("Only trust-family specs are executable through scripts/experiment/run.py.")
    batch_id = args.batch_name or default_batch_id()
    runner = BatchExperimentRunner(
        config_paths=args.config,
        output_root=args.output_dir,
        batch_id=batch_id,
        workers=args.workers,
        make_gifs=bool(args.make_gifs),
        verbose=bool(args.verbose),
        checkpoint_interval=args.checkpoint_interval,
    )
    result = runner.run_all()
    print(f"Saved batch outputs to {result.batch_dir}")
    for state in result.config_states:
        rows = len(state.primary_rows)
        print(f"{state.config_name}: {rows} rows -> {state.output_dir / 'results.csv'}")
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("--workers must be at least 1.")
    if args.checkpoint_interval < 1:
        parser.error("--checkpoint-interval must be at least 1.")
    if args.dry_run:
        return _write_dry_run_manifest(args)
    if len(args.config) == 1 and int(args.workers) == 1:
        return _serial_single_config_run(args)
    return _batch_run(args)


if __name__ == "__main__":
    raise SystemExit(main())

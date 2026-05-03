"""Compatibility wrapper for the canonical experiment runner."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


def _load_canonical() -> ModuleType:
    script_path = Path(__file__).resolve().parent / "experiment" / "run.py"
    spec = importlib.util.spec_from_file_location("scripts_experiment_run", script_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load canonical experiment runner at {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_CANONICAL = _load_canonical()
build_parser = _CANONICAL.build_parser


def main() -> int:
    return int(_CANONICAL.main())


if __name__ == "__main__":
    raise SystemExit(main())

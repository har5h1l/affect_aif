"""Compatibility wrapper for the canonical analysis runner."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


def _load_canonical() -> ModuleType:
    script_path = Path(__file__).resolve().parent / "analysis" / "analyze.py"
    spec = importlib.util.spec_from_file_location("scripts_analysis_analyze", script_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load canonical analysis runner at {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_CANONICAL = _load_canonical()
build_parser = _CANONICAL.build_parser
_hypothesis_summary_frame = _CANONICAL._hypothesis_summary_frame


def main(argv: list[str] | None = None) -> int:
    return int(_CANONICAL.main(argv))


if __name__ == "__main__":
    raise SystemExit(main())

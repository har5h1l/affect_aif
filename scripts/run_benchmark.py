"""Compatibility wrapper for the canonical CvC benchmark runner."""

from __future__ import annotations

import runpy
from pathlib import Path


def main() -> int:
    module = runpy.run_path(str(Path(__file__).resolve().parent / "benchmark" / "run_cvc.py"))
    result = module["main"]()
    return 0 if result is None else int(result)


if __name__ == "__main__":
    raise SystemExit(main())

"""Run or dry-run the canonical trust smoke config."""

# ruff: noqa: E402

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = str(Path(__file__).resolve().parent)
if sys.path and str(Path(sys.path[0]).resolve()) == SCRIPT_DIR:
    sys.path.pop(0)

import argparse
import subprocess


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Exercise the trust smoke experiment CLI.")
    parser.add_argument("--output-dir", default="results", help="Root directory for output folders.")
    parser.add_argument("--batch-name", default="smoke", help="Batch output folder name.")
    parser.add_argument(
        "--run",
        action="store_true",
        help="Run the smoke experiment instead of writing a dry-run manifest.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    cmd = [
        sys.executable,
        str(root / "scripts" / "experiment" / "run.py"),
        "--config",
        str(root / "configs" / "trust" / "smoke" / "smoke.toml"),
        "--output-dir",
        args.output_dir,
        "--batch-name",
        args.batch_name,
        "--workers",
        "1",
    ]
    if not args.run:
        cmd.append("--dry-run")
    return subprocess.run(cmd, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())

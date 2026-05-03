"""Create a submission-shaped bundle for a CvC policy spec."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from benchmarks.cvc.packaging import write_policy_bundle


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Package a local CvC policy spec.")
    parser.add_argument("--policy-spec", required=True, help="Policy spec, for example class=benchmarks.cvc.policy.X.")
    parser.add_argument("--output-dir", required=True, help="Bundle output directory.")
    parser.add_argument("--setup-script", help="Optional setup script path recorded in policy_spec.json.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    spec_path = write_policy_bundle(args.output_dir, args.policy_spec, setup_script=args.setup_script)
    print(f"Wrote policy bundle spec to {spec_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

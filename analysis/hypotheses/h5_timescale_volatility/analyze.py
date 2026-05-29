"""H5 timescale/volatility configured analysis entrypoint."""

from pathlib import Path

from experiments.trust.spec import AnalysisSpec


def run(*, results_path: str | Path, output_dir: str | Path, analysis: AnalysisSpec) -> None:
    from analysis.hypotheses._generic import run as generic_run

    generic_run(results_path=results_path, output_dir=output_dir, analysis=analysis)

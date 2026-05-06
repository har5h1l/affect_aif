"""Shared configured-analysis entrypoint for hypothesis packages."""

from __future__ import annotations

from pathlib import Path

from experiments.trust.spec import AnalysisSpec


def run(*, results_path: str | Path, output_dir: str | Path, analysis: AnalysisSpec) -> None:
    """Write the current first-pass configured analysis outputs."""

    from analysis.configured import write_configured_analysis_outputs

    write_configured_analysis_outputs(Path(results_path), Path(output_dir), analysis)

"""Config-aware analysis dispatch for TOML experiment specs."""

from __future__ import annotations

import importlib
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pandas as pd

from analysis.core.loading import load_configured_results
from analysis.hypotheses import run_all_hypothesis_tests
from analysis.metrics import (
    affective_movement_summary,
    betrayal_misdeployment_summary,
    betrayal_phase_summary,
    deployment_dissociation_summary,
    final_round_summary,
    has_switch_events,
    model_fitness_correlation_summary,
    partner_choice_summary,
    partner_model_fitness_summary,
    phenotype_validation_summary,
)
from analysis.plots import save_all_figures
from experiments.trust.spec import AnalysisSpec, ExperimentSpec


def run_configured_analysis(spec: ExperimentSpec, results_path: str | Path, output_dir: str | Path) -> None:
    """Run the generic configured analyzer for an experiment spec."""

    if not spec.analysis.auto:
        return
    analysis_dir = Path(output_dir) / "analysis"
    module = importlib.import_module(f"analysis.hypotheses.{spec.analysis.primary}.analyze")
    module.run(results_path=Path(results_path), output_dir=analysis_dir, analysis=spec.analysis)


def write_configured_analysis_outputs(results_path: Path, output_dir: Path, analysis: AnalysisSpec) -> None:
    """Write stable raw/report folders for configured analysis."""

    del analysis

    raw_dir = output_dir / "raw"
    figures_dir = output_dir / "figures"
    report_dir = output_dir / "report"
    raw_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    results = load_configured_results(results_path)
    try:
        save_all_figures(results, str(figures_dir))
    except (KeyError, ValueError) as exc:
        (figures_dir / "skipped_figures.txt").write_text(f"Skipped figures: {exc}\n", encoding="utf-8")

    try:
        summary = final_round_summary(results)
    except (KeyError, ValueError):
        group_cols = [col for col in ("hypothesis_id", "experiment_id", "variant_id", "seed") if col in results.columns]
        if group_cols and {"round", "payoff"} <= set(results.columns):
            summary = (
                results.sort_values(group_cols + ["round"])
                .groupby(group_cols, as_index=False)
                .agg(total_payoff=("payoff", "sum"), final_round=("round", "max"))
            )
        else:
            summary = pd.DataFrame({"rows": [len(results)]})
    summary.to_csv(raw_dir / "final_round_summary.csv", index=False)

    hypotheses: dict[str, Any]
    try:
        hypotheses = run_all_hypothesis_tests(results)
    except (KeyError, ValueError):
        hypotheses = {"status": "not_run"}
    (raw_dir / "hypothesis_tests.json").write_text(json.dumps(hypotheses, indent=2), encoding="utf-8")

    try:
        movement = affective_movement_summary(results)
    except (KeyError, ValueError):
        movement = pd.DataFrame()
    movement.to_csv(raw_dir / "affective_movement_summary.csv", index=False)

    raw_builders: list[tuple[str, Callable[[pd.DataFrame], pd.DataFrame]]] = [
        ("deployment_dissociation_summary.csv", deployment_dissociation_summary),
        ("partner_model_fitness_summary.csv", partner_model_fitness_summary),
        ("model_fitness_correlation_summary.csv", model_fitness_correlation_summary),
        ("partner_choice_summary.csv", partner_choice_summary),
        ("phenotype_validation_summary.csv", phenotype_validation_summary),
    ]
    for filename, builder in raw_builders:
        try:
            frame = builder(results)
        except (KeyError, ValueError):
            frame = pd.DataFrame()
        frame.to_csv(raw_dir / filename, index=False)

    try:
        switch_events_present = has_switch_events(results)
    except (KeyError, ValueError):
        switch_events_present = False
    if switch_events_present:
        try:
            betrayal_phases = betrayal_phase_summary(results, pre_window=20, acute_window=10)
        except (KeyError, ValueError):
            betrayal_phases = pd.DataFrame()
        betrayal_phases.to_csv(raw_dir / "betrayal_phase_summary.csv", index=False)
        try:
            betrayal_misdeployment = betrayal_misdeployment_summary(results, window=10)
        except (KeyError, ValueError):
            betrayal_misdeployment = pd.DataFrame()
        betrayal_misdeployment.to_csv(raw_dir / "betrayal_misdeployment_summary.csv", index=False)
    (report_dir / "summary.md").write_text(
        "# Analysis Summary\n\nConfigured analysis outputs generated.\n",
        encoding="utf-8",
    )

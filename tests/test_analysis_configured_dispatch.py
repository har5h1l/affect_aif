from __future__ import annotations

import importlib

import pandas as pd
from experiment_spec_helpers import write_example_toml

from analysis.configured import run_configured_analysis
from experiments.trust.spec import ExperimentSpec


def test_auto_analysis_writes_raw_outputs(tmp_path):
    spec = ExperimentSpec.from_toml(write_example_toml(tmp_path / "betrayal_choice.toml"))
    output_dir = tmp_path / "results" / "h5" / "betrayal_choice"
    output_dir.mkdir(parents=True)
    results_path = output_dir / "results.csv"
    pd.DataFrame(
        [
            {
                "hypothesis_id": "h5",
                "experiment_id": "betrayal_choice",
                "variant_id": "affect",
                "seed": 42,
                "round": 0,
                "payoff": 1.0,
                "inferred_joint_correct": True,
            }
        ]
    ).to_csv(results_path, index=False)

    run_configured_analysis(spec, results_path, output_dir)

    assert (output_dir / "analysis" / "raw").exists()
    assert (output_dir / "analysis" / "figures").exists()
    assert (output_dir / "analysis" / "report").exists()
    assert (output_dir / "analysis" / "report" / "summary.md").exists()
    assert (output_dir / "analysis" / "raw" / "deployment_dissociation_summary.csv").exists()
    assert (output_dir / "analysis" / "raw" / "partner_model_fitness_summary.csv").exists()
    assert (output_dir / "analysis" / "raw" / "model_fitness_correlation_summary.csv").exists()
    assert (output_dir / "analysis" / "raw" / "partner_choice_summary.csv").exists()
    assert (output_dir / "analysis" / "raw" / "phenotype_validation_summary.csv").exists()


def test_hypothesis_analysis_modules_are_importable():
    module_names = [
        "analysis.hypotheses.h0_policy_openness.analyze",
        "analysis.hypotheses.h1_model_fitness.analyze",
        "analysis.hypotheses.h2_deployment.analyze",
        "analysis.hypotheses.h3_locality.analyze",
        "analysis.hypotheses.h4_social_allocation.analyze",
        "analysis.hypotheses.h5_timescale_volatility.analyze",
        "analysis.hypotheses.h6_perturbation.analyze",
    ]

    for module_name in module_names:
        module = importlib.import_module(module_name)
        assert callable(module.run)

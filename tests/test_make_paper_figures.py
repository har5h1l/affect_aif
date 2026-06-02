from __future__ import annotations

import pandas as pd
import pytest

from scripts.analysis import make_paper_figures


def _write_source_tables(source_dir):
    source_dir.mkdir()
    pd.DataFrame(
        [
            {
                "readout": "final",
                "metric": "total_payoff",
                "treatment_variant": "affect",
                "reference_variant": "no_affect",
                "treatment_mean": 534.6,
                "reference_mean": 542.1,
                "difference": -7.5,
                "bootstrap_ci_low": -27.9,
                "bootstrap_ci_high": 13.8,
            },
            {
                "readout": "model_fitness",
                "metric": "abs_corr_precision_surprise_minus_reward",
                "treatment_variant": "affect",
                "reference_variant": "",
                "treatment_mean": 0.096,
                "reference_mean": "",
                "difference": 0.096,
                "bootstrap_ci_low": 0.027,
                "bootstrap_ci_high": 0.164,
            },
            {
                "readout": "model_fitness",
                "metric": "abs_partial_corr_precision_surprise_minus_reward",
                "treatment_variant": "affect",
                "reference_variant": "",
                "treatment_mean": 0.779,
                "reference_mean": "",
                "difference": 0.779,
                "bootstrap_ci_low": "",
                "bootstrap_ci_high": "",
            },
        ]
    ).to_csv(source_dir / "h1_evidence_effect_summary.csv", index=False)
    pd.DataFrame(
        [
            {
                "variant_id": "affect",
                "alignment": "active_encounter",
                "corr_precision_surprise": -0.70,
                "corr_precision_reward": -0.42,
                "abs_corr_precision_surprise": 0.70,
                "abs_corr_precision_reward": 0.42,
                "partial_corr_precision_surprise": -0.95,
                "partial_corr_precision_reward": 0.17,
                "abs_partial_corr_precision_surprise": 0.95,
                "abs_partial_corr_precision_reward": 0.17,
                "surprise_dominates_reward": True,
                "partial_surprise_dominates_reward": True,
            }
        ]
    ).to_csv(source_dir / "h1_model_fitness_correlation_summary.csv", index=False)
    pd.DataFrame(
        [
            {
                "readout": "final",
                "metric": "total_payoff",
                "treatment_variant": "affect",
                "reference_variant": "no_affect",
                "treatment_mean": 1136.1,
                "reference_mean": 1172.1,
                "difference": -36.0,
                "bootstrap_ci_low": -63.7,
                "bootstrap_ci_high": -10.9,
            },
            {
                "readout": "final",
                "metric": "mean_q_pi_entropy",
                "treatment_variant": "affect",
                "reference_variant": "no_affect",
                "treatment_mean": 8.38,
                "reference_mean": 8.74,
                "difference": -0.36,
                "bootstrap_ci_low": -0.45,
                "bootstrap_ci_high": -0.26,
            },
            {
                "readout": "betrayal_reallocation",
                "metric": "reencounters",
                "treatment_variant": "affect",
                "reference_variant": "no_affect",
                "treatment_mean": 4.4,
                "reference_mean": 6.1,
                "difference": -1.7,
                "bootstrap_ci_low": -4.5,
                "bootstrap_ci_high": 1.0,
            },
            {
                "readout": "betrayal_reallocation",
                "metric": "mean_payoff_on_reencounter",
                "treatment_variant": "affect",
                "reference_variant": "no_affect",
                "treatment_mean": 8.76,
                "reference_mean": 8.91,
                "difference": -0.15,
                "bootstrap_ci_low": -0.57,
                "bootstrap_ci_high": 0.26,
            },
            {
                "readout": "betrayal_misdeployment",
                "metric": "wrong_type_rate",
                "treatment_variant": "affect",
                "reference_variant": "no_affect",
                "treatment_mean": 0.24,
                "reference_mean": 0.17,
                "difference": 0.07,
                "bootstrap_ci_low": -0.11,
                "bootstrap_ci_high": 0.26,
            },
        ]
    ).to_csv(source_dir / "h3_evidence_effect_summary.csv", index=False)


def test_new_paper_figures_generate_manifest(tmp_path, capsys):
    source_dir = tmp_path / "source_tables"
    output_dir = tmp_path / "figures"
    _write_source_tables(source_dir)

    generated = [
        *make_paper_figures.model_fitness_figure(source_dir, output_dir),
        *make_paper_figures.betrayal_boundary_figure(source_dir, output_dir),
    ]
    make_paper_figures.print_manifest(generated)

    assert {path.name for path in generated} == {
        "fig_model_fitness_beta_reward_divergence.png",
        "fig_model_fitness_beta_reward_divergence.pdf",
        "fig_betrayal_boundary_summary.png",
        "fig_betrayal_boundary_summary.pdf",
    }
    assert all(path.exists() for path in generated)
    out = capsys.readouterr().out
    assert "Generated paper figure files:" in out
    assert "fig_model_fitness_beta_reward_divergence.png" in out
    assert "fig_betrayal_boundary_summary.pdf" in out


def test_new_paper_figures_fail_on_missing_required_column(tmp_path):
    source_dir = tmp_path / "source_tables"
    output_dir = tmp_path / "figures"
    _write_source_tables(source_dir)
    broken = pd.read_csv(source_dir / "h1_model_fitness_correlation_summary.csv").drop(
        columns=["abs_partial_corr_precision_reward"]
    )
    broken.to_csv(source_dir / "h1_model_fitness_correlation_summary.csv", index=False)

    with pytest.raises(ValueError, match="missing required columns.*abs_partial_corr_precision_reward"):
        make_paper_figures.model_fitness_figure(source_dir, output_dir)

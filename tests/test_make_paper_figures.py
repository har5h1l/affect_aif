from __future__ import annotations

import pandas as pd
import pytest

from scripts.analysis import make_paper_figures


def _write_source_tables(source_dir):
    source_dir.mkdir()
    pd.DataFrame(
        [
            {
                "variant_id": "local_beta",
                "abs_corr_precision_surprise": 0.943,
                "abs_corr_precision_payoff": 0.110,
                "total_payoff": 946.8,
            },
            {
                "variant_id": "global_beta",
                "abs_corr_precision_surprise": 0.149,
                "abs_corr_precision_payoff": 0.043,
                "total_payoff": 976.2,
            },
            {
                "variant_id": "no_affect",
                "abs_corr_precision_surprise": float("nan"),
                "abs_corr_precision_payoff": float("nan"),
                "total_payoff": 950.7,
            },
        ]
    ).to_csv(source_dir / "h3_locality_probe_summary.csv", index=False)
    pd.DataFrame(
        [
            {
                "readout": "final",
                "metric": "total_payoff",
                "treatment_variant": "affect",
                "reference_variant": "no_affect",
                "treatment_mean": 1322.3,
                "reference_mean": 1225.0,
                "difference": 97.3,
                "bootstrap_ci_low": 29.8,
                "bootstrap_ci_high": 164.8,
            },
            {
                "readout": "final",
                "metric": "mean_q_pi_entropy",
                "treatment_variant": "affect",
                "reference_variant": "no_affect",
                "treatment_mean": 7.47,
                "reference_mean": 8.68,
                "difference": -1.21,
                "bootstrap_ci_low": -1.82,
                "bootstrap_ci_high": -0.52,
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
    ).to_csv(source_dir / "h5_evidence_effect_summary.csv", index=False)


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
    broken = pd.read_csv(source_dir / "h3_locality_probe_summary.csv").drop(
        columns=["abs_corr_precision_payoff"]
    )
    broken.to_csv(source_dir / "h3_locality_probe_summary.csv", index=False)

    with pytest.raises(ValueError, match="missing required columns.*abs_corr_precision_payoff"):
        make_paper_figures.model_fitness_figure(source_dir, output_dir)

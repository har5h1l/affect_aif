from __future__ import annotations

import fitz
import pandas as pd
import pytest

from scripts.analysis import make_paper_figures


def _write_source_tables(source_dir):
    source_dir.mkdir()
    confirm_dir = source_dir / "h1_model_fitness_confirm"
    confirm_dir.mkdir()
    pd.DataFrame(
        [
            {
                "variant_id": "affect",
                "abs_partial_corr_precision_surprise": 0.940,
                "abs_partial_corr_precision_reward": 0.023,
                "abs_corr_precision_surprise": 0.945,
                "abs_corr_precision_reward": 0.367,
            },
            {
                "variant_id": "global_beta",
                "abs_partial_corr_precision_surprise": 0.496,
                "abs_partial_corr_precision_reward": 0.535,
                "abs_corr_precision_surprise": 0.583,
                "abs_corr_precision_reward": 0.379,
            },
        ]
    ).to_csv(confirm_dir / "model_fitness_correlation_summary.csv", index=False)
    pd.DataFrame(
        [
            {"variant_id": "affect", "seed": 1, "total_payoff": 1977.2},
            {"variant_id": "global_beta", "seed": 1, "total_payoff": 1973.4},
            {"variant_id": "no_affect", "seed": 1, "total_payoff": 1905.9},
        ]
    ).to_csv(confirm_dir / "final_round_summary.csv", index=False)
    pd.DataFrame(
        [
            {
                "variant_id": "affect",
                "total_payoff": 1851.3,
                "mean_q_pi_entropy": 8.59,
            },
            {
                "variant_id": "no_affect",
                "total_payoff": 1864.2,
                "mean_q_pi_entropy": 8.79,
            },
            {
                "variant_id": "tracked_only",
                "total_payoff": 1864.2,
                "mean_q_pi_entropy": 8.79,
            },
        ]
    ).to_csv(source_dir / "h2_deployment_contrast_summary.csv", index=False)
    pd.DataFrame(
        [
            {
                "variant_id": "affect",
                "baseline_variant": "lesioned",
                "total_payoff": 1851.3,
                "mean_q_pi_entropy": 8.59,
                "beta_range": 1.32,
                "delta_entropy_vs_tracked": -0.21,
                "delta_payoff_vs_tracked": -12.8,
                "n_seeds": 3,
            },
            {
                "variant_id": "lesioned",
                "baseline_variant": "lesioned",
                "total_payoff": 1864.2,
                "mean_q_pi_entropy": 8.79,
                "beta_range": 1.34,
                "delta_entropy_vs_tracked": 0.0,
                "delta_payoff_vs_tracked": 0.0,
                "n_seeds": 3,
            },
        ]
    ).to_csv(source_dir / "h2_deployment_pathway_summary.csv", index=False)
    pd.DataFrame(
        [
            {
                "readout": "final",
                "metric": "total_payoff",
                "treatment_variant": "affect",
                "reference_variant": "no_affect",
                "treatment_mean": 1185.9,
                "reference_mean": 1172.1,
                "difference": 13.8,
                "bootstrap_ci_low": -25.2,
                "bootstrap_ci_high": 53.2,
            },
            {
                "readout": "final",
                "metric": "mean_q_pi_entropy",
                "treatment_variant": "affect",
                "reference_variant": "no_affect",
                "treatment_mean": 8.36,
                "reference_mean": 8.74,
                "difference": -0.38,
                "bootstrap_ci_low": -0.62,
                "bootstrap_ci_high": -0.14,
            },
            {
                "readout": "final",
                "metric": "mean_joint_accuracy",
                "treatment_variant": "affect",
                "reference_variant": "no_affect",
                "treatment_mean": 0.372,
                "reference_mean": 0.266,
                "difference": 0.106,
                "bootstrap_ci_low": 0.034,
                "bootstrap_ci_high": 0.185,
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
    pd.DataFrame(
        [
            {
                "variant_id": variant,
                "round_bin_start": round_bin,
                "round_bin_end": round_bin + 9,
                "n_seeds": 3,
                "p0_selection_mean": 0.18 if variant == "affect" else 0.10,
                "p0_selection_ci_low": 0.02,
                "p0_selection_ci_high": 0.40,
                "mean_q_pi_entropy_mean": 8.2 if variant == "affect" else 8.7,
                "mean_q_pi_entropy_ci_low": 7.9,
                "mean_q_pi_entropy_ci_high": 9.0,
                "p0_beta_mean": 1.1 if variant != "no_affect" else float("nan"),
                "p0_beta_ci_low": 0.8 if variant != "no_affect" else float("nan"),
                "p0_beta_ci_high": 1.4 if variant != "no_affect" else float("nan"),
                "mean_payoff_mean": 9.8,
                "mean_payoff_ci_low": 9.2,
                "mean_payoff_ci_high": 10.4,
            }
            for variant in ["affect", "no_affect", "lesioned"]
            for round_bin in [0, 10, 20, 30]
        ]
    ).to_csv(source_dir / "h5_betrayal_timecourse_summary.csv", index=False)


def test_new_paper_figures_generate_manifest(tmp_path, capsys):
    source_dir = tmp_path / "source_tables"
    output_dir = tmp_path / "figures"
    _write_source_tables(source_dir)

    generated = [
        *make_paper_figures.model_fitness_figure(source_dir, output_dir),
        *make_paper_figures.deployment_social_figure(source_dir, output_dir),
        *make_paper_figures.betrayal_boundary_figure(source_dir, output_dir),
    ]
    make_paper_figures.print_manifest(generated)

    assert {path.name for path in generated} == {
        "fig_deployment_social_summary.png",
        "fig_deployment_social_summary.pdf",
        "fig_betrayal_boundary_summary.png",
        "fig_betrayal_boundary_summary.pdf",
        "fig_model_fitness_beta_reward_divergence.png",
        "fig_model_fitness_beta_reward_divergence.pdf",
    }
    assert all(path.exists() for path in generated)
    out = capsys.readouterr().out
    assert "Generated paper figure files:" in out
    assert "fig_model_fitness_beta_reward_divergence.png" in out
    assert "fig_deployment_social_summary.png" in out
    assert "fig_betrayal_boundary_summary.pdf" in out


def test_paper_figure_pdfs_embed_beta_labels(tmp_path):
    source_dir = tmp_path / "source_tables"
    output_dir = tmp_path / "figures"
    _write_source_tables(source_dir)

    make_paper_figures.deployment_social_figure(source_dir, output_dir)
    pdf_text = fitz.open(output_dir / "fig_deployment_social_summary.pdf")[0].get_text().replace("\n", " ")
    assert "βk tracker movement" in pdf_text
    assert "mean within-episode" in pdf_text
    assert "βk range" in pdf_text


def test_new_paper_figures_fail_on_missing_required_column(tmp_path):
    source_dir = tmp_path / "source_tables"
    output_dir = tmp_path / "figures"
    _write_source_tables(source_dir)
    broken = pd.read_csv(source_dir / "h2_deployment_pathway_summary.csv").drop(columns=["beta_range"])
    broken.to_csv(source_dir / "h2_deployment_pathway_summary.csv", index=False)

    with pytest.raises(ValueError, match="missing required columns.*beta_range"):
        make_paper_figures.deployment_social_figure(source_dir, output_dir)


def test_model_fitness_figure_requires_current_confirm_tables(tmp_path):
    source_dir = tmp_path / "source_tables"
    output_dir = tmp_path / "figures"
    _write_source_tables(source_dir)
    (source_dir / "h1_model_fitness_confirm" / "model_fitness_correlation_summary.csv").unlink()

    with pytest.raises(FileNotFoundError, match="h1_model_fitness_confirm/model_fitness_correlation_summary.csv"):
        make_paper_figures.model_fitness_figure(source_dir, output_dir)

from __future__ import annotations

import fitz
import matplotlib.pyplot as plt
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
                "abs_partial_corr_precision_surprise": 0.660,
                "abs_partial_corr_precision_reward": 0.094,
                "abs_partial_corr_precision_surprise_ci_low": 0.492,
                "abs_partial_corr_precision_surprise_ci_high": 0.766,
                "abs_partial_corr_precision_reward_ci_low": 0.000,
                "abs_partial_corr_precision_reward_ci_high": 0.291,
                "abs_corr_precision_surprise": 0.660,
                "abs_corr_precision_reward": 0.094,
            },
            {
                "variant_id": "global_beta",
                "abs_partial_corr_precision_surprise": 0.454,
                "abs_partial_corr_precision_reward": 0.072,
                "abs_partial_corr_precision_surprise_ci_low": 0.275,
                "abs_partial_corr_precision_surprise_ci_high": 0.619,
                "abs_partial_corr_precision_reward_ci_low": 0.000,
                "abs_partial_corr_precision_reward_ci_high": 0.390,
                "abs_corr_precision_surprise": 0.454,
                "abs_corr_precision_reward": 0.072,
            },
        ]
    ).to_csv(confirm_dir / "model_fitness_correlation_summary.csv", index=False)
    pd.DataFrame(
        [
            {
                "variant_id": "affect",
                "seed": 1,
                "total_payoff": 1977.2,
                "total_payoff_ci_low": 1900.0,
                "total_payoff_ci_high": 2050.0,
            },
            {
                "variant_id": "global_beta",
                "seed": 1,
                "total_payoff": 1973.4,
                "total_payoff_ci_low": 1900.0,
                "total_payoff_ci_high": 2050.0,
            },
            {
                "variant_id": "no_affect",
                "seed": 1,
                "total_payoff": 1905.9,
                "total_payoff_ci_low": 1850.0,
                "total_payoff_ci_high": 1960.0,
            },
        ]
    ).to_csv(confirm_dir / "final_round_summary.csv", index=False)
    pd.DataFrame(
        [
            {
                "variant_id": "affect",
                "total_payoff": 1851.3,
                "total_payoff_ci_low": 1800.0,
                "total_payoff_ci_high": 1905.0,
                "mean_q_pi_entropy": 6.887,
                "mean_q_pi_entropy_ci_low": 6.70,
                "mean_q_pi_entropy_ci_high": 7.08,
            },
            {
                "variant_id": "no_affect",
                "total_payoff": 1864.2,
                "total_payoff_ci_low": 1810.0,
                "total_payoff_ci_high": 1910.0,
                "mean_q_pi_entropy": 7.657,
                "mean_q_pi_entropy_ci_low": 7.45,
                "mean_q_pi_entropy_ci_high": 7.86,
            },
            {
                "variant_id": "tracked_only",
                "total_payoff": 1864.2,
                "mean_q_pi_entropy": 7.657,
            },
        ]
    ).to_csv(source_dir / "h2_deployment_contrast_summary.csv", index=False)
    pd.DataFrame(
        [
            {
                "variant_id": "affect",
                "baseline_variant": "lesioned",
                "total_payoff": 1851.3,
                "total_payoff_ci_low": 1800.0,
                "total_payoff_ci_high": 1905.0,
                "mean_q_pi_entropy": 6.887,
                "mean_q_pi_entropy_ci_low": 6.70,
                "mean_q_pi_entropy_ci_high": 7.08,
                "beta_range": 1.32,
                "beta_range_ci_low": 1.20,
                "beta_range_ci_high": 1.44,
                "delta_entropy_vs_tracked": -0.21,
                "delta_payoff_vs_tracked": -12.8,
                "delta_entropy_vs_tracked_difference": -0.21,
                "delta_entropy_vs_tracked_bootstrap_ci_low": -0.32,
                "delta_entropy_vs_tracked_bootstrap_ci_high": -0.10,
                "delta_payoff_vs_tracked_difference": -12.8,
                "delta_payoff_vs_tracked_bootstrap_ci_low": -27.0,
                "delta_payoff_vs_tracked_bootstrap_ci_high": 2.0,
                "n_seeds": 3,
            },
            {
                "variant_id": "lesioned",
                "baseline_variant": "lesioned",
                "total_payoff": 1864.2,
                "total_payoff_ci_low": 1810.0,
                "total_payoff_ci_high": 1910.0,
                "mean_q_pi_entropy": 7.657,
                "mean_q_pi_entropy_ci_low": 7.45,
                "mean_q_pi_entropy_ci_high": 7.86,
                "beta_range": 1.34,
                "beta_range_ci_low": 1.22,
                "beta_range_ci_high": 1.46,
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
                "treatment_mean": 4.886,
                "reference_mean": 7.034,
                "difference": -2.149,
                "bootstrap_ci_low": -2.379,
                "bootstrap_ci_high": -1.895,
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
                "mean_q_pi_entropy_mean": 4.886 if variant == "affect" else 7.034,
                "mean_q_pi_entropy_ci_low": 4.55 if variant == "affect" else 6.75,
                "mean_q_pi_entropy_ci_high": 5.20 if variant == "affect" else 7.35,
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


def test_betrayal_effect_source_contains_only_headline_final_rows(tmp_path, monkeypatch):
    summary = pd.DataFrame(
        [
            {"readout": "final", "metric": "total_payoff", "difference": 58.15},
            {"readout": "final", "metric": "mean_q_pi_entropy", "difference": -2.149},
            {"readout": "final", "metric": "mean_joint_accuracy", "difference": 0.158},
            {"readout": "final", "metric": "mean_stance_accuracy", "difference": 0.166},
            {"readout": "model_fitness", "metric": "generic_diagnostic", "difference": 0.5},
            {"readout": "betrayal_reallocation", "metric": "reencounters", "difference": 0.3},
        ]
    )
    monkeypatch.setattr(make_paper_figures, "load_results_table", lambda _: pd.DataFrame({"x": [1]}))
    monkeypatch.setattr(make_paper_figures, "evidence_effect_summary", lambda *args, **kwargs: summary)

    output_path = tmp_path / "h5_evidence_effect_summary.csv"
    make_paper_figures.build_betrayal_effect_source(tmp_path / "results.csv", output_path)
    generated = pd.read_csv(output_path)

    assert set(generated["readout"]) == {"final"}
    assert set(generated["metric"]) == {
        "total_payoff",
        "mean_q_pi_entropy",
        "mean_joint_accuracy",
        "mean_stance_accuracy",
    }


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


def test_main_generates_only_current_main_figures(tmp_path, capsys, monkeypatch):
    source_dir = tmp_path / "source_tables"
    output_dir = tmp_path / "figures"
    _write_source_tables(source_dir)
    monkeypatch.setattr(
        "sys.argv",
        [
            "make_paper_figures.py",
            "--source-dir",
            str(source_dir),
            "--output-dir",
            str(output_dir),
        ],
    )

    assert make_paper_figures.main() == 0
    assert {path.name for path in output_dir.iterdir()} == {
        "fig_deployment_social_summary.png",
        "fig_deployment_social_summary.pdf",
        "fig_betrayal_boundary_summary.png",
        "fig_betrayal_boundary_summary.pdf",
        "fig_model_fitness_beta_reward_divergence.png",
        "fig_model_fitness_beta_reward_divergence.pdf",
    }
    assert "fig_phenotype_dynamics_summary" not in capsys.readouterr().out


def test_paper_figure_pdfs_embed_beta_labels(tmp_path):
    source_dir = tmp_path / "source_tables"
    output_dir = tmp_path / "figures"
    _write_source_tables(source_dir)

    make_paper_figures.deployment_social_figure(source_dir, output_dir)
    pdf_text = fitz.open(output_dir / "fig_deployment_social_summary.pdf")[0].get_text().replace("\n", " ")
    assert "βk tracker movement" in pdf_text
    assert "Policy entropy (nats)" in pdf_text
    assert "Cumulative payoff" in pdf_text
    assert "95% CI" not in pdf_text
    assert "Tracking requires deployment" not in pdf_text
    assert "Payoff nearly matched" not in pdf_text


def test_main_figures_use_lncs_text_width():
    expected_width = 12.2 / 2.54
    assert make_paper_figures.LNCS_TEXT_WIDTH_IN == pytest.approx(expected_width)
    assert make_paper_figures.MAIN_FIGURE_SIZE == pytest.approx((expected_width, 1.62))
    assert make_paper_figures.BETRAYAL_FIGURE_SIZE == pytest.approx((expected_width, 1.62))


def test_bar_value_labels_clear_confidence_whiskers():
    fig, ax = plt.subplots()
    intervals = [(0.49, 0.77), (0.00, 0.29)]
    make_paper_figures._bar(
        ax,
        ["surprisal", "payoff"],
        [0.66, 0.09],
        title="test",
        ylabel="test",
        ci_bounds=intervals,
    )
    assert all(text.get_position()[1] > high for text, (_, high) in zip(ax.texts, intervals, strict=True))
    assert all(tick.get_rotation() == 0 for tick in ax.get_xticklabels())
    plt.close(fig)


def test_new_paper_figures_fail_on_missing_required_column(tmp_path):
    source_dir = tmp_path / "source_tables"
    output_dir = tmp_path / "figures"
    _write_source_tables(source_dir)
    broken = pd.read_csv(source_dir / "h2_deployment_pathway_summary.csv").drop(columns=["beta_range"])
    broken.to_csv(source_dir / "h2_deployment_pathway_summary.csv", index=False)

    with pytest.raises(ValueError, match="missing required columns.*beta_range"):
        make_paper_figures.deployment_social_figure(source_dir, output_dir)


def test_paper_figures_reject_missing_confidence_interval_columns(tmp_path):
    source_dir = tmp_path / "source_tables"
    output_dir = tmp_path / "figures"
    _write_source_tables(source_dir)
    correlation_path = source_dir / "h1_model_fitness_confirm" / "model_fitness_correlation_summary.csv"
    pd.read_csv(correlation_path).drop(columns=["abs_partial_corr_precision_surprise_ci_low"]).to_csv(
        correlation_path,
        index=False,
    )

    with pytest.raises(ValueError, match="missing required columns.*abs_partial_corr_precision_surprise_ci_low"):
        make_paper_figures.model_fitness_figure(source_dir, output_dir)


def test_model_fitness_figure_requires_current_confirm_tables(tmp_path):
    source_dir = tmp_path / "source_tables"
    output_dir = tmp_path / "figures"
    _write_source_tables(source_dir)
    (source_dir / "h1_model_fitness_confirm" / "model_fitness_correlation_summary.csv").unlink()

    with pytest.raises(FileNotFoundError, match="h1_model_fitness_confirm/model_fitness_correlation_summary.csv"):
        make_paper_figures.model_fitness_figure(source_dir, output_dir)


def test_canonical_result_validation_rejects_entropy_above_policy_ceiling(tmp_path):
    ceiling = make_paper_figures.EXPECTED_MAX_ENTROPY
    path = tmp_path / "results.csv"
    pd.DataFrame(
        [
            {
                "variant_id": variant,
                "seed": seed,
                "charge_transform": "none" if variant == "no_affect" else "linear",
                "per_partner_policy_count": 1296,
                "candidate_policy_count": 5184,
                "max_q_pi_entropy": ceiling,
                "q_pi_entropy": ceiling + (1e-4 if variant == "affect" and seed == 0 else 0.0),
            }
            for variant in ["affect", "no_affect"]
            for seed in range(30)
        ]
    ).to_csv(path, index=False)

    with pytest.raises(ValueError, match="policy entropy above"):
        make_paper_figures._validate_canonical_linear_results(path)

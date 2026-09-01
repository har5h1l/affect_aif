"""Build manuscript figures from copied paper source tables."""

# ruff: noqa: E402,I001

from __future__ import annotations

import argparse
import ast
import math
import sys
from pathlib import Path

SCRIPT_DIR = str(Path(__file__).resolve().parent)
if sys.path and str(Path(sys.path[0]).resolve()) == SCRIPT_DIR:
    sys.path.pop(0)
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analysis.figure_style import apply_manuscript_figure_style
from analysis.metrics import (
    affective_movement_summary,
    BOOTSTRAP_ITERATIONS,
    BOOTSTRAP_SEED,
    evidence_effect_summary,
    model_fitness_correlation_summary,
    paired_seed_contrast,
    seed_bootstrap_mean_ci,
)
from cli.common import load_results_table

VARIANT_LABELS = {
    "affect": r"local $\beta$",
    "local_beta": r"local $\beta$",
    "no_affect": "no affect",
    "tracked_only": "tracked only",
    "lesioned": "tracked only",
    "tracked-only": "tracked only",
    "no_epistemic": "no epistemic",
    "global_beta": r"shared $\beta$",
    "affect_default": r"local $\beta$",
    "affect_combined_caution": "combined caution",
    "low_gain": "low gain",
    "high_gain": "high gain",
    "cautious_prior": "cautious prior",
}
EXPECTED_POLICIES_PER_PARTNER = 1_296
EXPECTED_COMBINED_CANDIDATES = 5_184
EXPECTED_MAX_ENTROPY = math.log(EXPECTED_COMBINED_CANDIDATES)
# LNCS uses a 12.2 cm text block. Generate at final publication width so
# embedded lettering is not reduced below its configured point size.
LNCS_TEXT_WIDTH_IN = 12.2 / 2.54
MAIN_FIGURE_SIZE = (LNCS_TEXT_WIDTH_IN, 1.50)
BETRAYAL_FIGURE_SIZE = (LNCS_TEXT_WIDTH_IN, 1.50)


def _read(source_dir: Path, filename: str) -> pd.DataFrame:
    path = source_dir / filename
    if not path.exists():
        raise FileNotFoundError(f"Required source table not found: {path}")
    return pd.read_csv(path)


def _read_required(source_dir: Path, filename: str, columns: set[str]) -> pd.DataFrame:
    frame = _read(source_dir, filename)
    missing = sorted(columns.difference(frame.columns))
    if missing:
        raise ValueError(f"{filename} missing required columns: {', '.join(missing)}")
    return frame


def _save(fig: plt.Figure, output_dir: Path, stem: str) -> list[Path]:
    apply_manuscript_figure_style()
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for suffix in (".png", ".pdf"):
        path = output_dir / f"{stem}{suffix}"
        fig.savefig(path, bbox_inches="tight", pad_inches=0.02, dpi=300)
        paths.append(path)
    plt.close(fig)
    return paths


def _label(values: list[str]) -> list[str]:
    return [VARIANT_LABELS.get(value, value.replace("_", " ")) for value in values]


def _bar_label(values: list[str]) -> list[str]:
    labels = _label(values)
    wrapped = {
        r"local $\beta$": "local\n$\\beta$",
        r"shared $\beta$": "shared\n$\\beta$",
        "no affect": "no\naffect",
        "tracked only": "tracked\nonly",
    }
    return [wrapped.get(label, label) for label in labels]


def _bar(
    ax: plt.Axes,
    labels: list[str],
    values: list[float],
    *,
    title: str,
    ylabel: str,
    ci_bounds: list[tuple[float, float]] | None = None,
    show_values: bool = True,
    headroom: float = 1.18,
) -> None:
    colors = ["#2f6f9f", "#c47f2c", "#5f8f5f", "#7a6aa8", "#8c8c8c"]
    yerr = None
    if ci_bounds is not None:
        if len(ci_bounds) != len(values):
            raise ValueError("ci_bounds must have one interval per bar")
        lows, highs = zip(*ci_bounds, strict=True)
        yerr = np.asarray(
            [
                np.maximum(np.asarray(values, dtype=float) - np.asarray(lows, dtype=float), 0.0),
                np.maximum(np.asarray(highs, dtype=float) - np.asarray(values, dtype=float), 0.0),
            ]
        )
    bars = ax.bar(
        range(len(values)),
        values,
        color=colors[: len(values)],
        width=0.68,
        yerr=yerr,
        capsize=2 if yerr is not None else 0,
        error_kw={"elinewidth": 0.8, "capthick": 0.8},
    )
    ax.set_xticks(range(len(values)), _bar_label(labels), rotation=0, ha="center")
    ax.set_ylabel(ylabel)
    ax.set_title(title, pad=2)
    ax.tick_params(axis="both", pad=1)
    ax.spines[["top", "right"]].set_visible(False)
    span = max(values) - min(values) if values else 0
    offset = 0.03 * span if span else 0.02
    if values and min(values) >= 0:
        interval_highs = [high for _, high in ci_bounds] if ci_bounds is not None else []
        upper = max([*values, *interval_highs])
        ax.set_ylim(0, upper * headroom if upper else 1.0)
    if not show_values:
        return
    for index, (bar, value) in enumerate(zip(bars, values, strict=True)):
        va = "bottom" if value >= 0 else "top"
        interval_edge = ci_bounds[index][1 if value >= 0 else 0] if ci_bounds is not None else value
        text_y = interval_edge + offset if value >= 0 else interval_edge - offset
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            text_y,
            f"{value:.2f}" if abs(value) < 20 else f"{value:.0f}",
            ha="center",
            va=va,
            fontsize=8,
        )


def _numeric_array(value: object) -> list[float]:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return []
    try:
        parsed = ast.literal_eval(str(value))
    except (SyntaxError, ValueError):
        return []
    if not isinstance(parsed, list):
        return []
    out = []
    for item in parsed:
        try:
            number = float(item)
        except (TypeError, ValueError):
            continue
        if math.isfinite(number):
            out.append(number)
    return out


def _p0_beta(value: object) -> float:
    values = _numeric_array(value)
    return values[0] if values else np.nan


def _mean_ci(values: pd.Series) -> pd.Series:
    """Return a 10,000-resample seed-bootstrap interval for a seed mean."""
    finite = values.dropna().astype(float)
    if finite.empty:
        return pd.Series({"mean": np.nan, "ci_low": np.nan, "ci_high": np.nan})
    return pd.Series(
        {
            "mean": float(finite.mean()),
            "ci_low": seed_bootstrap_mean_ci(finite, BOOTSTRAP_ITERATIONS, BOOTSTRAP_SEED)[0],
            "ci_high": seed_bootstrap_mean_ci(finite, BOOTSTRAP_ITERATIONS, BOOTSTRAP_SEED)[1],
        }
    )


def _line_with_band(
    ax: plt.Axes,
    frame: pd.DataFrame,
    *,
    x_col: str,
    mean_col: str,
    low_col: str,
    high_col: str,
    label: str,
    color: str,
) -> None:
    x = frame[x_col].astype(float).to_numpy()
    mean = frame[mean_col].astype(float).to_numpy()
    low = frame[low_col].astype(float).to_numpy()
    high = frame[high_col].astype(float).to_numpy()
    ax.plot(x, mean, label=label, color=color, linewidth=1.3)
    if np.isfinite(low).any() and np.isfinite(high).any():
        ax.fill_between(x, low, high, color=color, alpha=0.14, linewidth=0)


def _validate_canonical_linear_results(results_path: Path) -> None:
    """Reject noncanonical, squared-charge, incomplete, or entropy-invalid paper data."""

    required = {
        "variant_id",
        "seed",
        "charge_transform",
        "per_partner_policy_count",
        "candidate_policy_count",
        "max_q_pi_entropy",
        "q_pi_entropy",
    }
    frame = pd.read_csv(results_path, usecols=lambda column: column in required, low_memory=False)
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"{results_path} missing canonical provenance columns: {', '.join(missing)}")
    transforms = set(frame["charge_transform"].dropna().astype(str))
    if not transforms <= {"linear", "none"} or "linear" not in transforms:
        raise ValueError(f"{results_path} is not a corrected-linear result table: {sorted(transforms)}")
    if set(frame["per_partner_policy_count"].dropna().astype(int)) != {EXPECTED_POLICIES_PER_PARTNER}:
        raise ValueError(f"{results_path} does not use 1,296 policies per partner")
    if set(frame["candidate_policy_count"].dropna().astype(int)) != {EXPECTED_COMBINED_CANDIDATES}:
        raise ValueError(f"{results_path} does not use 5,184 combined policy candidates")
    entropy_ceiling = frame["max_q_pi_entropy"].astype(float)
    if not np.allclose(entropy_ceiling, EXPECTED_MAX_ENTROPY, atol=1e-10, rtol=0.0):
        raise ValueError(f"{results_path} has an unexpected policy-entropy ceiling")
    if (frame["q_pi_entropy"].astype(float) > entropy_ceiling + 1e-10).any():
        raise ValueError(f"{results_path} contains policy entropy above its recorded maximum")
    seed_counts = frame.groupby("variant_id")["seed"].nunique()
    if seed_counts.empty or not (seed_counts == 30).all():
        raise ValueError(f"{results_path} does not contain 30 complete seeds per variant: {seed_counts.to_dict()}")


def _seed_variant_summary(results: pd.DataFrame) -> pd.DataFrame:
    """Aggregate canonical figure metrics to one value per variant and simulation seed."""

    seed_rows = []
    for (variant_id, seed), group in results.groupby(["variant_id", "seed"], sort=True):
        beta_values = [value for row in group["betas"] for value in _numeric_array(row)]
        seed_rows.append(
            {
                "variant_id": str(variant_id),
                "seed": int(seed),
                "total_payoff": float(group["payoff"].sum()),
                "mean_q_pi_entropy": float(group["q_pi_entropy"].mean()),
                "beta_range": float(max(beta_values) - min(beta_values)) if beta_values else np.nan,
            }
        )
    return pd.DataFrame(seed_rows)


def _with_seed_mean_intervals(seed_summary: pd.DataFrame, metrics: list[str]) -> pd.DataFrame:
    rows = []
    for variant_id, group in seed_summary.groupby("variant_id", sort=True):
        row: dict[str, float | int | str] = {"variant_id": str(variant_id), "n_seeds": int(len(group))}
        for metric in metrics:
            low, high = seed_bootstrap_mean_ci(group[metric], BOOTSTRAP_ITERATIONS, BOOTSTRAP_SEED)
            row[metric] = float(group[metric].mean())
            row[f"{metric}_ci_low"] = low
            row[f"{metric}_ci_high"] = high
            row[f"{metric}_bootstrap_iterations"] = BOOTSTRAP_ITERATIONS
            row[f"{metric}_bootstrap_seed"] = BOOTSTRAP_SEED
            row[f"{metric}_bootstrap_method"] = "seed_mean_percentile"
        rows.append(row)
    return pd.DataFrame(rows)


def build_deployment_pathway_source(results_path: Path, output_path: Path) -> Path:
    results = pd.read_csv(
        results_path,
        usecols=["variant_id", "seed", "round", "payoff", "q_pi_entropy", "betas"],
        low_memory=False,
    )
    seed_summary = _seed_variant_summary(results)
    movement = affective_movement_summary(results)[["variant_id", "seed", "beta_range"]]
    seed_summary = seed_summary.drop(columns="beta_range").merge(
        movement,
        on=["variant_id", "seed"],
        how="left",
        validate="one_to_one",
    )
    tracked_variant = "tracked_only" if "tracked_only" in set(seed_summary["variant_id"]) else "lesioned"
    summary = _with_seed_mean_intervals(
        seed_summary,
        ["total_payoff", "mean_q_pi_entropy", "beta_range"],
    )
    treatment = seed_summary.loc[seed_summary["variant_id"] == "affect"]
    reference = seed_summary.loc[seed_summary["variant_id"] == tracked_variant]
    for metric, output_name in (
        ("mean_q_pi_entropy", "delta_entropy_vs_tracked"),
        ("beta_range", "delta_beta_range_vs_tracked"),
        ("total_payoff", "delta_payoff_vs_tracked"),
    ):
        contrast = paired_seed_contrast(
            treatment,
            reference,
            value_column=metric,
            iterations=BOOTSTRAP_ITERATIONS,
            random_seed=BOOTSTRAP_SEED,
        )
        for key, value in contrast.items():
            summary.loc[summary["variant_id"] == "affect", f"{output_name}_{key}"] = value
    summary.insert(1, "baseline_variant", tracked_variant)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(output_path, index=False)
    effect_rows = []
    for metric, prefix in (
        ("policy_entropy", "delta_entropy_vs_tracked"),
        ("beta_range", "delta_beta_range_vs_tracked"),
        ("cumulative_payoff", "delta_payoff_vs_tracked"),
    ):
        affect_row = summary.loc[summary["variant_id"] == "affect"].iloc[0]
        effect_rows.append(
            {
                "metric": metric,
                "treatment_variant": "affect",
                "reference_variant": tracked_variant,
                "treatment_mean": affect_row[f"{prefix}_treatment_mean"],
                "reference_mean": affect_row[f"{prefix}_reference_mean"],
                "paired_difference": affect_row[f"{prefix}_difference"],
                "paired_ci_low": affect_row[f"{prefix}_bootstrap_ci_low"],
                "paired_ci_high": affect_row[f"{prefix}_bootstrap_ci_high"],
                "n_pairs": int(affect_row[f"{prefix}_n_pairs"]),
                "bootstrap_method": affect_row[f"{prefix}_bootstrap_method"],
            }
        )
    pd.DataFrame(effect_rows).to_csv(output_path.with_name("h2_deployment_contrast_summary.csv"), index=False)
    return output_path


def build_partner_selection_source(results_path: Path, output_path: Path) -> Path:
    """Build paired entropy, payoff, and selected-type summaries for Section 3.3."""

    results = pd.read_csv(
        results_path,
        usecols=["variant_id", "seed", "payoff", "q_pi_entropy", "true_partner_type"],
        low_memory=False,
    )
    variants = set(results["variant_id"].astype(str))
    if not {"affect", "no_affect"} <= variants:
        raise ValueError("partner-selection source requires affect and no_affect variants")
    rows = []
    seed_rows = []
    partner_types = ["cooperator", "exploiter", "reciprocator", "random"]
    for (variant_id, seed), group in results.groupby(["variant_id", "seed"], sort=True):
        row = {
            "variant_id": str(variant_id),
            "seed": int(seed),
            "policy_entropy": float(group["q_pi_entropy"].mean()),
            "cumulative_payoff": float(group["payoff"].sum()),
        }
        normalized_types = group["true_partner_type"].astype(str).str.lower()
        for partner_type in partner_types:
            row[f"selection_share_{partner_type}"] = float((normalized_types == partner_type).mean())
        seed_rows.append(row)
    seed_summary = pd.DataFrame(seed_rows)
    treatment = seed_summary.loc[seed_summary["variant_id"] == "affect"]
    reference = seed_summary.loc[seed_summary["variant_id"] == "no_affect"]
    metrics = ["policy_entropy", "cumulative_payoff", *[f"selection_share_{kind}" for kind in partner_types]]
    for metric in metrics:
        contrast = paired_seed_contrast(
            treatment,
            reference,
            value_column=metric,
            iterations=BOOTSTRAP_ITERATIONS,
            random_seed=BOOTSTRAP_SEED,
        )
        rows.append(
            {
                "metric": metric,
                "true_partner_type": (
                    metric.removeprefix("selection_share_") if metric.startswith("selection_share_") else ""
                ),
                "treatment_variant": "affect",
                "reference_variant": "no_affect",
                "treatment_mean": contrast["treatment_mean"],
                "reference_mean": contrast["reference_mean"],
                "difference": contrast["difference"],
                "bootstrap_ci_low": contrast["bootstrap_ci_low"],
                "bootstrap_ci_high": contrast["bootstrap_ci_high"],
                "paired_dz": contrast["paired_dz"],
                "n_pairs": contrast["n_pairs"],
                "bootstrap_iterations": contrast["bootstrap_iterations"],
                "bootstrap_seed": contrast["bootstrap_seed"],
                "bootstrap_method": contrast["bootstrap_method"],
            }
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output_path, index=False)
    return output_path


def build_model_fitness_source(results_path: Path, output_dir: Path) -> list[Path]:
    """Build Figure 1's correlation and payoff tables from corrected-linear results."""

    results = load_results_table(results_path)
    correlation = model_fitness_correlation_summary(
        results,
        bootstrap_iterations=BOOTSTRAP_ITERATIONS,
        random_seed=BOOTSTRAP_SEED,
    )
    seed_summary = _seed_variant_summary(results)
    payoff = _with_seed_mean_intervals(seed_summary, ["total_payoff"])
    output_dir.mkdir(parents=True, exist_ok=True)
    correlation_path = output_dir / "model_fitness_correlation_summary.csv"
    payoff_path = output_dir / "final_round_summary.csv"
    correlation.to_csv(correlation_path, index=False)
    payoff.to_csv(payoff_path, index=False)
    return [correlation_path, payoff_path]


def build_betrayal_timecourse_source(results_path: Path, output_path: Path, *, bin_width: int = 10) -> Path:
    results = pd.read_csv(
        results_path,
        usecols=[
            "variant_id",
            "seed",
            "round",
            "payoff",
            "q_pi_entropy",
            "betas",
            "selected_partner",
        ],
        low_memory=False,
    )
    results["round_bin_start"] = (results["round"] // bin_width) * bin_width
    results["p0_selection"] = (results["selected_partner"] == 0).astype(float)
    results["p0_beta"] = results["betas"].apply(_p0_beta)
    by_seed = (
        results.groupby(["variant_id", "seed", "round_bin_start"], as_index=False)
        .agg(
            p0_selection=("p0_selection", "mean"),
            mean_q_pi_entropy=("q_pi_entropy", "mean"),
            p0_beta=("p0_beta", "mean"),
            mean_payoff=("payoff", "mean"),
        )
        .sort_values(["variant_id", "seed", "round_bin_start"])
    )
    rows = []
    for (variant_id, round_bin_start), group in by_seed.groupby(["variant_id", "round_bin_start"], sort=True):
        row = {
            "variant_id": str(variant_id),
            "round_bin_start": int(round_bin_start),
            "round_bin_end": int(round_bin_start + bin_width - 1),
            "n_seeds": int(group["seed"].nunique()),
            "bootstrap_iterations": BOOTSTRAP_ITERATIONS,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "bootstrap_method": "seed_mean_percentile",
        }
        for metric in ["p0_selection", "mean_q_pi_entropy", "p0_beta", "mean_payoff"]:
            stats = _mean_ci(group[metric])
            row[f"{metric}_mean"] = stats["mean"]
            row[f"{metric}_ci_low"] = stats["ci_low"]
            row[f"{metric}_ci_high"] = stats["ci_high"]
        rows.append(row)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output_path, index=False)
    return output_path


def build_betrayal_effect_source(results_path: Path, output_path: Path) -> Path:
    results = load_results_table(results_path)
    summary = evidence_effect_summary(
        results,
        bootstrap_iterations=BOOTSTRAP_ITERATIONS,
        random_seed=BOOTSTRAP_SEED,
    )
    headline_metrics = {
        "total_payoff",
        "mean_q_pi_entropy",
        "mean_joint_accuracy",
        "mean_stance_accuracy",
    }
    summary = summary.loc[
        (summary["readout"] == "final") & summary["metric"].isin(headline_metrics)
    ].copy()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(output_path, index=False)
    return output_path


def refresh_figure_source_tables(results_root: Path, source_dir: Path) -> list[Path]:
    h1 = results_root / "01_predictability_value/raw/results.csv"
    h2 = results_root / "02_deployment_ablation/raw/results.csv"
    h4 = results_root / "03_partner_selection/raw/results.csv"
    h5 = results_root / "04_betrayal_adaptation/raw/results.csv"
    for path in (h1, h2, h4, h5):
        if not path.exists():
            raise FileNotFoundError(f"Required canonical paper result not found: {path}")
        _validate_canonical_linear_results(path)
    return [
        *build_model_fitness_source(h1, source_dir / "h1_model_fitness_confirm"),
        build_deployment_pathway_source(
            h2,
            source_dir / "h2_deployment_pathway_summary.csv",
        ),
        build_partner_selection_source(
            h4,
            source_dir / "h4_partner_choice_summary.csv",
        ),
        build_betrayal_timecourse_source(
            h5,
            source_dir / "h5_betrayal_timecourse_summary.csv",
        ),
        build_betrayal_effect_source(
            h5,
            source_dir / "h5_evidence_effect_summary.csv",
        ),
    ]


def model_fitness_figure(source_dir: Path, output_dir: Path) -> list[Path]:
    locality = _read_required(
        source_dir,
        "h1_model_fitness_confirm/model_fitness_correlation_summary.csv",
        {
            "variant_id",
            "abs_partial_corr_precision_surprise",
            "abs_partial_corr_precision_reward",
            "abs_partial_corr_precision_surprise_ci_low",
            "abs_partial_corr_precision_surprise_ci_high",
            "abs_partial_corr_precision_reward_ci_low",
            "abs_partial_corr_precision_reward_ci_high",
        },
    )
    payoff = _read_required(
        source_dir,
        "h1_model_fitness_confirm/final_round_summary.csv",
        {"variant_id", "total_payoff", "total_payoff_ci_low", "total_payoff_ci_high"},
    )
    locality = locality.copy()
    locality["plot_variant_id"] = locality["variant_id"]
    locality["plot_abs_surprise"] = locality["abs_partial_corr_precision_surprise"]
    locality["plot_abs_reward"] = locality["abs_partial_corr_precision_reward"]
    payoff_rows = payoff[["variant_id", "total_payoff", "total_payoff_ci_low", "total_payoff_ci_high"]].copy()
    payoff_rows = payoff_rows.rename(columns={"variant_id": "plot_variant_id"})
    local_id = "affect"

    local = locality.loc[locality["plot_variant_id"] == local_id].iloc[0]
    shared = locality.loc[locality["plot_variant_id"] == "global_beta"].iloc[0]

    fig, axes = plt.subplots(1, 3, figsize=MAIN_FIGURE_SIZE)
    _bar(
        axes[0],
        ["surprisal", "payoff"],
        [
            float(local["plot_abs_surprise"]),
            float(local["plot_abs_reward"]),
        ],
        title=r"partner-local $\beta$",
        ylabel=r"$|r_{\mathrm{partial}}|$",
        ci_bounds=[
            (
                float(local["abs_partial_corr_precision_surprise_ci_low"]),
                float(local["abs_partial_corr_precision_surprise_ci_high"]),
            ),
            (
                float(local["abs_partial_corr_precision_reward_ci_low"]),
                float(local["abs_partial_corr_precision_reward_ci_high"]),
            ),
        ],
    )
    axes[0].set_ylim(0, 1.05)

    _bar(
        axes[1],
        ["surprisal", "payoff"],
        [
            float(shared["plot_abs_surprise"]),
            float(shared["plot_abs_reward"]),
        ],
        title=r"shared $\beta$",
        ylabel="",
        ci_bounds=[
            (
                float(shared["abs_partial_corr_precision_surprise_ci_low"]),
                float(shared["abs_partial_corr_precision_surprise_ci_high"]),
            ),
            (
                float(shared["abs_partial_corr_precision_reward_ci_low"]),
                float(shared["abs_partial_corr_precision_reward_ci_high"]),
            ),
        ],
    )
    axes[1].set_ylim(0, 1.05)

    _bar(
        axes[2],
        payoff_rows["plot_variant_id"].tolist(),
        payoff_rows["total_payoff"].tolist(),
        title="Payoff",
        ylabel="payoff",
        ci_bounds=list(zip(payoff_rows["total_payoff_ci_low"], payoff_rows["total_payoff_ci_high"], strict=True)),
    )

    fig.subplots_adjust(left=0.10, right=0.99, bottom=0.24, top=0.86, wspace=0.42)
    return _save(fig, output_dir, "fig_model_fitness_beta_reward_divergence")


def betrayal_boundary_figure(source_dir: Path, output_dir: Path) -> list[Path]:
    timecourse = _read_required(
        source_dir,
        "h5_betrayal_timecourse_summary.csv",
        {
            "variant_id",
            "round_bin_start",
            "p0_selection_mean",
            "p0_selection_ci_low",
            "p0_selection_ci_high",
            "mean_q_pi_entropy_mean",
            "mean_q_pi_entropy_ci_low",
            "mean_q_pi_entropy_ci_high",
            "p0_beta_mean",
            "p0_beta_ci_low",
            "p0_beta_ci_high",
        },
    )

    fig, axes = plt.subplots(1, 3, figsize=BETRAYAL_FIGURE_SIZE, sharex=True)
    colors = {"affect": "#2f6f9f", "no_affect": "#8c8c8c", "lesioned": "#5f8f5f"}
    for variant in ["affect", "no_affect"]:
        rows = timecourse[timecourse["variant_id"] == variant].sort_values("round_bin_start")
        _line_with_band(
            axes[0],
            rows,
            x_col="round_bin_start",
            mean_col="p0_selection_mean",
            low_col="p0_selection_ci_low",
            high_col="p0_selection_ci_high",
            label=VARIANT_LABELS[variant],
            color=colors[variant],
        )
    for variant in ["affect", "lesioned"]:
        rows = timecourse[timecourse["variant_id"] == variant].sort_values("round_bin_start")
        _line_with_band(
            axes[1],
            rows,
            x_col="round_bin_start",
            mean_col="p0_beta_mean",
            low_col="p0_beta_ci_low",
            high_col="p0_beta_ci_high",
            label=VARIANT_LABELS[variant],
            color=colors[variant],
        )
    for variant in ["affect", "no_affect"]:
        rows = timecourse[timecourse["variant_id"] == variant].sort_values("round_bin_start")
        _line_with_band(
            axes[2],
            rows,
            x_col="round_bin_start",
            mean_col="mean_q_pi_entropy_mean",
            low_col="mean_q_pi_entropy_ci_low",
            high_col="mean_q_pi_entropy_ci_high",
            label=VARIANT_LABELS[variant],
            color=colors[variant],
        )

    for ax in axes:
        ax.axvline(31, color="#555555", linestyle="--", linewidth=0.9)
        ax.set_xlabel("round", labelpad=1)
        ax.tick_params(axis="both", pad=1)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_title("Betrayed selection", pad=2)
    axes[0].set_ylabel("P0 selection")
    axes[1].set_title(r"Posterior mean $\beta_k$", pad=2)
    axes[1].set_ylabel(r"P0 mean $\beta_k$")
    axes[2].set_title("Policy entropy", pad=2)
    axes[2].set_ylabel("entropy")
    legend_kwargs = {
        "frameon": False,
        "fontsize": 8,
        "handlelength": 1.3,
        "handletextpad": 0.35,
        "borderpad": 0.1,
        "labelspacing": 0.2,
    }
    axes[0].legend(**legend_kwargs)
    axes[1].legend(**legend_kwargs)
    fig.subplots_adjust(left=0.09, right=0.99, bottom=0.24, top=0.88, wspace=0.45)
    return _save(fig, output_dir, "fig_betrayal_boundary_summary")


def deployment_social_figure(source_dir: Path, output_dir: Path) -> list[Path]:
    h2 = _read_required(
        source_dir,
        "h2_deployment_pathway_summary.csv",
        {
            "variant_id",
            "baseline_variant",
            "total_payoff",
            "total_payoff_ci_low",
            "total_payoff_ci_high",
            "mean_q_pi_entropy",
            "mean_q_pi_entropy_ci_low",
            "mean_q_pi_entropy_ci_high",
            "beta_range",
            "beta_range_ci_low",
            "beta_range_ci_high",
            "delta_entropy_vs_tracked_difference",
            "delta_entropy_vs_tracked_bootstrap_ci_low",
            "delta_entropy_vs_tracked_bootstrap_ci_high",
            "delta_payoff_vs_tracked_difference",
            "delta_payoff_vs_tracked_bootstrap_ci_low",
            "delta_payoff_vs_tracked_bootstrap_ci_high",
        },
    )
    tracked_variant = str(h2["baseline_variant"].dropna().iloc[0])
    order = ["affect", tracked_variant]
    h2 = h2.set_index("variant_id").loc[order]

    fig, axes = plt.subplots(1, 3, figsize=MAIN_FIGURE_SIZE)
    _bar(
        axes[0],
        order,
        h2["beta_range"].tolist(),
        title=r"$\beta_k$ tracker movement",
        ylabel="",
        ci_bounds=list(zip(h2["beta_range_ci_low"], h2["beta_range_ci_high"], strict=True)),
        headroom=1.35,
    )
    _bar(
        axes[1],
        order,
        h2["mean_q_pi_entropy"].tolist(),
        title="Policy entropy (nats)",
        ylabel="",
        ci_bounds=list(
            zip(h2["mean_q_pi_entropy_ci_low"], h2["mean_q_pi_entropy_ci_high"], strict=True)
        ),
        headroom=1.35,
    )
    _bar(
        axes[2],
        order,
        h2["total_payoff"].tolist(),
        title="Cumulative payoff",
        ylabel="",
        ci_bounds=list(zip(h2["total_payoff_ci_low"], h2["total_payoff_ci_high"], strict=True)),
        headroom=1.35,
    )
    fig.subplots_adjust(left=0.10, right=0.99, bottom=0.24, top=0.86, wspace=0.42)
    return _save(fig, output_dir, "fig_deployment_social_summary")


def print_manifest(paths: list[Path]) -> None:
    print("Generated paper figure files:")
    for path in paths:
        print(f"  - {path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir",
        default="docs/manuscript/source_tables",
        help="Directory containing manuscript source CSV tables.",
    )
    parser.add_argument(
        "--output-dir",
        default="docs/manuscript/figures",
        help="Directory for generated manuscript figures.",
    )
    parser.add_argument(
        "--results-root",
        default="results/paper",
        help="Paper results root used when refreshing figure source tables.",
    )
    parser.add_argument(
        "--refresh-source-tables",
        action="store_true",
        help="Refresh compact figure source tables from results/paper raw CSVs before plotting.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    source_dir = Path(args.source_dir)
    output_dir = Path(args.output_dir)
    if args.refresh_source_tables:
        refreshed = refresh_figure_source_tables(Path(args.results_root), source_dir)
        for path in refreshed:
            print(f"Refreshed source table: {path}")
    apply_manuscript_figure_style()
    generated = [
        *model_fitness_figure(source_dir, output_dir),
        *deployment_social_figure(source_dir, output_dir),
        *betrayal_boundary_figure(source_dir, output_dir),
    ]
    print_manifest(generated)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

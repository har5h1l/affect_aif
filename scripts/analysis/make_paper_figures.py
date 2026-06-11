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

VARIANT_LABELS = {
    "affect": "local beta",
    "local_beta": "local beta",
    "no_affect": "no affect",
    "tracked_only": "tracked only",
    "lesioned": "tracked only",
    "tracked-only": "tracked only",
    "no_epistemic": "no epistemic",
    "global_beta": "shared beta",
    "affect_default": "local beta",
    "affect_combined_caution": "combined caution",
    "low_gain": "low gain",
    "high_gain": "high gain",
    "cautious_prior": "cautious prior",
}


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


def _bar(ax: plt.Axes, labels: list[str], values: list[float], *, title: str, ylabel: str) -> None:
    colors = ["#2f6f9f", "#c47f2c", "#5f8f5f", "#7a6aa8", "#8c8c8c"]
    bars = ax.bar(range(len(values)), values, color=colors[: len(values)], width=0.68)
    ax.set_xticks(range(len(values)), _label(labels), rotation=20, ha="right")
    ax.set_ylabel(ylabel)
    ax.set_title(title, pad=8)
    ax.spines[["top", "right"]].set_visible(False)
    span = max(values) - min(values) if values else 0
    offset = 0.03 * span if span else 0.02
    for bar, value in zip(bars, values, strict=True):
        va = "bottom" if value >= 0 else "top"
        text_y = bar.get_height() + offset if value >= 0 else bar.get_height() - offset
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            text_y,
            f"{value:.2f}" if abs(value) < 20 else f"{value:.1f}",
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
    finite = values.dropna().astype(float)
    if finite.empty:
        return pd.Series({"mean": np.nan, "ci_low": np.nan, "ci_high": np.nan})
    return pd.Series(
        {
            "mean": float(finite.mean()),
            "ci_low": float(finite.quantile(0.025)),
            "ci_high": float(finite.quantile(0.975)),
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
    ax.plot(x, mean, label=label, color=color, linewidth=1.8)
    if np.isfinite(low).any() and np.isfinite(high).any():
        ax.fill_between(x, low, high, color=color, alpha=0.14, linewidth=0)


def build_deployment_pathway_source(results_path: Path, output_path: Path) -> Path:
    results = pd.read_csv(
        results_path,
        usecols=["variant_id", "seed", "round", "payoff", "q_pi_entropy", "betas"],
        low_memory=False,
    )
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
    seed_summary = pd.DataFrame(seed_rows)
    tracked_variant = "tracked_only" if "tracked_only" in set(seed_summary["variant_id"]) else "lesioned"
    tracked = seed_summary[seed_summary["variant_id"] == tracked_variant][
        ["seed", "total_payoff", "mean_q_pi_entropy"]
    ].rename(
        columns={
            "total_payoff": "tracked_total_payoff",
            "mean_q_pi_entropy": "tracked_mean_q_pi_entropy",
        }
    )
    seed_summary = seed_summary.merge(tracked, on="seed", how="left")
    seed_summary["delta_entropy_vs_tracked"] = (
        seed_summary["mean_q_pi_entropy"] - seed_summary["tracked_mean_q_pi_entropy"]
    )
    seed_summary["delta_payoff_vs_tracked"] = seed_summary["total_payoff"] - seed_summary["tracked_total_payoff"]
    summary = (
        seed_summary.groupby("variant_id", as_index=False)
        .agg(
            total_payoff=("total_payoff", "mean"),
            mean_q_pi_entropy=("mean_q_pi_entropy", "mean"),
            beta_range=("beta_range", "mean"),
            delta_entropy_vs_tracked=("delta_entropy_vs_tracked", "mean"),
            delta_payoff_vs_tracked=("delta_payoff_vs_tracked", "mean"),
            n_seeds=("seed", "nunique"),
        )
        .sort_values("variant_id")
    )
    summary.insert(1, "baseline_variant", tracked_variant)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(output_path, index=False)
    return output_path


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


def refresh_figure_source_tables(results_root: Path, source_dir: Path) -> list[Path]:
    return [
        build_deployment_pathway_source(
            results_root / "02_deployment_ablation/raw/results.csv",
            source_dir / "h2_deployment_pathway_summary.csv",
        ),
        build_betrayal_timecourse_source(
            results_root / "04_betrayal_adaptation/raw/results.csv",
            source_dir / "h5_betrayal_timecourse_summary.csv",
        ),
    ]


def model_fitness_figure(source_dir: Path, output_dir: Path) -> list[Path]:
    confirm_path = source_dir / "h1_model_fitness_confirm" / "model_fitness_correlation_summary.csv"
    if confirm_path.exists():
        locality = _read_required(
            source_dir,
            "h1_model_fitness_confirm/model_fitness_correlation_summary.csv",
            {
                "variant_id",
                "abs_partial_corr_precision_surprise",
                "abs_partial_corr_precision_reward",
                "abs_corr_precision_surprise",
                "abs_corr_precision_reward",
            },
        )
        payoff = _read_required(
            source_dir,
            "h1_model_fitness_confirm/final_round_summary.csv",
            {"variant_id", "total_payoff"},
        )
        locality = locality.copy()
        locality["plot_variant_id"] = locality["variant_id"]
        locality["plot_abs_surprise"] = locality["abs_partial_corr_precision_surprise"]
        locality["plot_abs_reward"] = locality["abs_partial_corr_precision_reward"]
        payoff_rows = (
            payoff.groupby("variant_id", as_index=False)["total_payoff"]
            .mean()
            .rename(columns={"variant_id": "plot_variant_id"})
        )
        local_id = "affect"
    else:
        locality = _read_required(
            source_dir,
            "h3_locality_probe_summary.csv",
            {
                "variant_id",
                "abs_corr_precision_surprise",
                "abs_corr_precision_payoff",
                "total_payoff",
            },
        )
        locality = locality.copy()
        locality["plot_variant_id"] = locality["variant_id"]
        locality["plot_abs_surprise"] = locality["abs_corr_precision_surprise"]
        locality["plot_abs_reward"] = locality["abs_corr_precision_payoff"]
        payoff_rows = locality.dropna(subset=["total_payoff"])
        local_id = "local_beta"

    local = locality.loc[locality["plot_variant_id"] == local_id].iloc[0]
    shared = locality.loc[locality["plot_variant_id"] == "global_beta"].iloc[0]

    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.0))
    _bar(
        axes[0],
        ["surprisal", "payoff"],
        [
            float(local["plot_abs_surprise"]),
            float(local["plot_abs_reward"]),
        ],
        title=r"partner-local $\beta$",
        ylabel="absolute partial correlation",
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
        ylabel="absolute partial correlation",
    )
    axes[1].set_ylim(0, 1.05)

    _bar(
        axes[2],
        payoff_rows["plot_variant_id"].tolist(),
        payoff_rows["total_payoff"].tolist(),
        title="Analysis-window payoff",
        ylabel="analysis-window payoff",
    )

    fig.suptitle("Predictability versus realized payoff", y=1.04, fontsize=12)
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

    fig, axes = plt.subplots(1, 3, figsize=(11.2, 3.0), sharex=True)
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
        ax.set_xlabel("round")
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_title("Betrayed-partner selection", pad=8)
    axes[0].set_ylabel("P0 selection rate")
    axes[1].set_title(r"Betrayed-partner $E_q[\beta_k]$", pad=8)
    axes[1].set_ylabel(r"mean P0 $E_q[\beta_k]$")
    axes[2].set_title("Policy entropy", pad=8)
    axes[2].set_ylabel("mean entropy")
    axes[0].legend(frameon=False, fontsize=8)
    axes[1].legend(frameon=False, fontsize=8)
    fig.suptitle("Betrayal time course", y=1.04, fontsize=12)
    return _save(fig, output_dir, "fig_betrayal_boundary_summary")


def deployment_social_figure(source_dir: Path, output_dir: Path) -> list[Path]:
    h2 = _read_required(
        source_dir,
        "h2_deployment_pathway_summary.csv",
        {
            "variant_id",
            "baseline_variant",
            "beta_range",
            "delta_entropy_vs_tracked",
            "delta_payoff_vs_tracked",
        },
    )
    tracked_variant = str(h2["baseline_variant"].dropna().iloc[0])
    order = ["affect", tracked_variant]
    h2 = h2.set_index("variant_id").loc[order]

    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.0))
    _bar(
        axes[0],
        order,
        h2["beta_range"].tolist(),
        title=r"$\beta_k$ tracker movement",
        ylabel=r"mean $\beta_k$ range",
    )
    _bar(
        axes[1],
        order,
        h2["delta_entropy_vs_tracked"].tolist(),
        title="Deployment changes entropy",
        ylabel=r"$\Delta$ entropy vs tracked-only",
    )
    axes[1].axhline(0, color="#555555", linewidth=0.8)
    axes[1].set_ylim(min(-0.24, float(h2["delta_entropy_vs_tracked"].min()) - 0.03), 0.05)
    _bar(
        axes[2],
        order,
        h2["delta_payoff_vs_tracked"].tolist(),
        title="Payoff not improved",
        ylabel=r"$\Delta$ payoff vs tracked-only",
    )
    axes[2].axhline(0, color="#555555", linewidth=0.8)
    axes[2].set_ylim(min(-14.5, float(h2["delta_payoff_vs_tracked"].min()) - 1.0), 2.0)

    fig.suptitle("Tracking requires deployment", y=1.04, fontsize=12)
    fig.tight_layout()
    return _save(fig, output_dir, "fig_deployment_social_summary")


def phenotype_figure(source_dir: Path, output_dir: Path) -> list[Path]:
    dynamics = _read(source_dir, "h6_perturbation_dynamics_summary.csv")
    betrayal = _read(source_dir, "h6_perturbation_betrayal_summary.csv")
    order = ["affect", "low_gain", "high_gain", "cautious_prior"]
    frames = []
    for label, frame in (("open", dynamics), ("betrayal", betrayal)):
        summary = frame.groupby("variant_id", as_index=False).agg(
            beta_range=("beta_range", "mean"),
            beta_std=("beta_std", "mean"),
            action_flip_rate=("action_flip_rate", "mean"),
            total_payoff=("total_payoff", "mean"),
        )
        summary["regime"] = label
        frames.append(summary)
    data = pd.concat(frames, ignore_index=True)

    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.0))
    width = 0.36
    x = np.arange(len(order))
    for offset, regime in ((-width / 2, "open"), (width / 2, "betrayal")):
        values = data[data["regime"] == regime].set_index("variant_id").loc[order]
        axes[0].bar(x + offset, values["beta_range"], width=width, label=regime)
        axes[1].bar(x + offset, values["action_flip_rate"], width=width, label=regime)
        axes[2].bar(x + offset, values["total_payoff"], width=width, label=regime)
    for ax, title, ylabel in zip(
        axes,
        [r"$\beta_k$ range", "Investment churn", "Payoff"],
        [r"mean $\beta_k$ range", "investment churn", "payoff"],
        strict=True,
    ):
        ax.set_xticks(x, _label(order), rotation=20, ha="right")
        ax.set_title(title, pad=8)
        ax.set_ylabel(ylabel)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].legend(frameon=False, fontsize=8)
    fig.suptitle("Precision-dynamics perturbation controls", y=1.04, fontsize=12)
    return _save(fig, output_dir, "fig_phenotype_dynamics_summary")


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
        *phenotype_figure(source_dir, output_dir),
    ]
    print_manifest(generated)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

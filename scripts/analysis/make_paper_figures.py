"""Build manuscript figures from copied paper source tables."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

VARIANT_LABELS = {
    "affect": "local beta",
    "local_beta": "local beta",
    "no_affect": "no affect",
    "lesioned": "tracked only",
    "tracked_only": "tracked only",
    "no_epistemic": "no epistemic",
    "global_beta": "global beta",
    "affect_default": "local beta",
    "affect_combined_caution": "combined caution",
    "alexithymia": "low gain",
    "borderline": "high gain",
    "depression": "cautious prior",
}


def _read(source_dir: Path, filename: str) -> pd.DataFrame:
    return pd.read_csv(source_dir / filename)


def _save(fig: plt.Figure, output_dir: Path, stem: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for suffix in (".png", ".pdf"):
        fig.savefig(output_dir / f"{stem}{suffix}", bbox_inches="tight", dpi=300)
    plt.close(fig)


def _label(values: list[str]) -> list[str]:
    return [VARIANT_LABELS.get(value, value.replace("_", " ")) for value in values]


def _bar(ax: plt.Axes, labels: list[str], values: list[float], *, title: str, ylabel: str) -> None:
    colors = ["#2f6f9f", "#c47f2c", "#5f8f5f", "#7a6aa8", "#8c8c8c"]
    bars = ax.bar(range(len(values)), values, color=colors[: len(values)], width=0.68)
    ax.set_xticks(range(len(values)), _label(labels), rotation=20, ha="right")
    ax.set_ylabel(ylabel)
    ax.set_title(title, pad=8)
    ax.spines[["top", "right"]].set_visible(False)
    for bar, value in zip(bars, values, strict=True):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.2f}" if abs(value) < 20 else f"{value:.1f}",
            ha="center",
            va="bottom",
            fontsize=8,
        )


def deployment_social_figure(source_dir: Path, output_dir: Path) -> None:
    h2 = _read(source_dir, "h2_deployment_dissociation_summary.csv")
    h4 = _read(source_dir, "h4_partner_choice_summary.csv")

    order = ["affect", "lesioned", "no_epistemic"]
    h2 = h2.set_index("variant_id").loc[order]
    choice = (
        h4.groupby(["variant_id", "selected_partner"], as_index=False)
        .agg(selection_rate=("selection_rate", "mean"))
        .pivot(index="selected_partner", columns="variant_id", values="selection_rate")
        .sort_index()
    )

    fig, axes_grid = plt.subplots(2, 2, figsize=(7.2, 5.4))
    axes = axes_grid.ravel()
    _bar(
        axes[0],
        order,
        h2["total_payoff"].tolist(),
        title="Open-regime payoff",
        ylabel="total payoff",
    )
    _bar(
        axes[1],
        order,
        h2["mean_q_pi_entropy"].tolist(),
        title="Policy entropy",
        ylabel="mean entropy",
    )
    x = np.arange(len(order))
    axes[2].plot(x, h2["mean_joint_accuracy"], marker="o", label="joint")
    axes[2].plot(x, h2["mean_stance_accuracy"], marker="o", label="stance")
    axes[2].set_xticks(x, _label(order), rotation=20, ha="right")
    axes[2].set_ylim(0, 1)
    axes[2].set_title("Belief readouts", pad=8)
    axes[2].set_ylabel("accuracy")
    axes[2].legend(frameon=False, fontsize=8)
    axes[2].spines[["top", "right"]].set_visible(False)

    partners = choice.index.to_numpy()
    width = 0.34
    axes[3].bar(partners - width / 2, choice["affect"], width=width, label="local beta", color="#2f6f9f")
    axes[3].bar(partners + width / 2, choice["no_affect"], width=width, label="no affect", color="#c47f2c")
    axes[3].set_xticks(partners, [f"P{int(item)}" for item in partners])
    axes[3].set_ylim(0, max(choice.max()) + 0.08)
    axes[3].set_title("Partner choice", pad=8)
    axes[3].set_ylabel("selection rate")
    axes[3].legend(frameon=False, fontsize=8)
    axes[3].spines[["top", "right"]].set_visible(False)

    fig.suptitle("Deployment and social choice", y=1.01, fontsize=12)
    fig.tight_layout()
    _save(fig, output_dir, "fig_deployment_social_summary")


def shock_shape_figure(source_dir: Path, output_dir: Path) -> None:
    abrupt = _read(source_dir, "h3_abrupt_sensitivity_final_round_summary.csv")
    gradual = _read(source_dir, "h3_gradual_sensitivity_final_round_summary.csv")
    order = ["no_affect", "affect_default", "affect_combined_caution"]
    rows = []
    for label, frame in (("abrupt", abrupt), ("gradual", gradual)):
        summary = frame[frame["variant_id"].isin(order)].groupby("variant_id", as_index=False).agg(
            total_payoff=("total_payoff", "mean"),
            mean_q_pi_entropy=("mean_q_pi_entropy", "mean"),
        )
        summary["shock"] = label
        rows.append(summary)
    data = pd.concat(rows, ignore_index=True)

    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.0))
    width = 0.25
    x = np.arange(2)
    for idx, variant in enumerate(order):
        values = [
            float(data[(data["shock"] == shock) & (data["variant_id"] == variant)]["total_payoff"].iloc[0])
            for shock in ("abrupt", "gradual")
        ]
        axes[0].bar(x + (idx - 1) * width, values, width=width, label=VARIANT_LABELS[variant])
    axes[0].set_xticks(x, ["abrupt", "gradual"])
    axes[0].set_ylabel("total payoff")
    axes[0].set_title("Payoff by shock shape", pad=8)
    axes[0].legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=3)
    axes[0].spines[["top", "right"]].set_visible(False)

    for idx, variant in enumerate(order):
        values = [
            float(data[(data["shock"] == shock) & (data["variant_id"] == variant)]["mean_q_pi_entropy"].iloc[0])
            for shock in ("abrupt", "gradual")
        ]
        axes[1].bar(x + (idx - 1) * width, values, width=width, label=VARIANT_LABELS[variant])
    axes[1].set_xticks(x, ["abrupt", "gradual"])
    axes[1].set_ylabel("mean entropy")
    axes[1].set_title("Policy entropy", pad=8)
    axes[1].spines[["top", "right"]].set_visible(False)

    deltas = []
    labels = []
    for shock in ("abrupt", "gradual"):
        base = float(data[(data["shock"] == shock) & (data["variant_id"] == "no_affect")]["total_payoff"].iloc[0])
        for variant in ("affect_default", "affect_combined_caution"):
            value = float(data[(data["shock"] == shock) & (data["variant_id"] == variant)]["total_payoff"].iloc[0])
            deltas.append(value - base)
            labels.append(f"{shock}\n{VARIANT_LABELS[variant]}")
    axes[2].axhline(0, color="#555555", linewidth=0.8)
    axes[2].bar(range(len(deltas)), deltas, color=["#2f6f9f", "#7a6aa8", "#2f6f9f", "#7a6aa8"])
    axes[2].set_xticks(range(len(deltas)), labels, rotation=25, ha="right")
    axes[2].set_ylabel("payoff delta vs no affect")
    axes[2].set_title("Penalty is timing-specific", pad=8)
    axes[2].spines[["top", "right"]].set_visible(False)

    fig.suptitle("Shock shape and precision sensitivity", y=1.04, fontsize=12)
    _save(fig, output_dir, "fig_shock_shape_summary")


def phenotype_figure(source_dir: Path, output_dir: Path) -> None:
    dynamics = _read(source_dir, "h5_clinical_dynamics_phenotype_validation_summary.csv")
    betrayal = _read(source_dir, "h5_clinical_betrayal_phenotype_validation_summary.csv")
    order = ["affect", "alexithymia", "borderline", "depression"]
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
        ["Beta range", "Action churn", "Total payoff"],
        ["mean range", "flip rate", "payoff"],
        strict=True,
    ):
        ax.set_xticks(x, _label(order), rotation=20, ha="right")
        ax.set_title(title, pad=8)
        ax.set_ylabel(ylabel)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].legend(frameon=False, fontsize=8)
    fig.suptitle("Precision-dynamics perturbation phenotypes", y=1.04, fontsize=12)
    _save(fig, output_dir, "fig_phenotype_dynamics_summary")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir",
        default="docs/paper/manuscript/source_tables",
        help="Directory containing manuscript source CSV tables.",
    )
    parser.add_argument(
        "--output-dir",
        default="docs/paper/manuscript/figures",
        help="Directory for generated manuscript figures.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    source_dir = Path(args.source_dir)
    output_dir = Path(args.output_dir)
    plt.rcParams.update(
        {
            "font.size": 9,
            "axes.titlesize": 9,
            "axes.labelsize": 8,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 8,
        }
    )
    deployment_social_figure(source_dir, output_dir)
    shock_shape_figure(source_dir, output_dir)
    phenotype_figure(source_dir, output_dir)
    print(f"Wrote paper figures to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

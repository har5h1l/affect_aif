"""Generate paper figures from experiment results."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def parse_list_col(series: pd.Series) -> list[list[float]]:
    """Parse a column of stringified lists into actual lists."""
    out = []
    for val in series:
        if isinstance(val, str):
            out.append(ast.literal_eval(val))
        elif isinstance(val, list):
            out.append(val)
        else:
            out.append([float(val)])
    return out


def figure_beta_trajectory(c2_df: pd.DataFrame, output_path: str):
    """Figure 1: Beta trajectory under betrayal for partner 0 (the betrayer).

    Shows mean +/- SE across seeds, with betrayal switch marked.
    """
    fig, ax = plt.subplots(figsize=(7, 3.5))

    # Extract beta for partner 0 across rounds for each seed
    seeds = sorted(c2_df["seed"].unique())
    rounds = sorted(c2_df["round"].unique())

    beta_matrix = np.full((len(seeds), len(rounds)), np.nan)
    for i, seed in enumerate(seeds):
        seed_df = c2_df[c2_df["seed"] == seed].sort_values("round")
        betas_list = parse_list_col(seed_df["betas"])
        for j, (_, row_betas) in enumerate(zip(seed_df["round"], betas_list, strict=False)):
            if j < len(rounds):
                beta_matrix[i, j] = row_betas[0]  # Partner 0

    mean_beta = np.nanmean(beta_matrix, axis=0)
    se_beta = np.nanstd(beta_matrix, axis=0) / np.sqrt(len(seeds))
    rounds_arr = np.array(rounds)

    ax.fill_between(rounds_arr, mean_beta - se_beta, mean_beta + se_beta, alpha=0.25, color="#2196F3")
    ax.plot(rounds_arr, mean_beta, color="#1565C0", linewidth=1.8, label=r"$\beta_0$ (betrayer)")

    # Mark betrayal switch
    ax.axvline(x=31, color="#D32F2F", linestyle="--", linewidth=1.2, alpha=0.8)
    ax.annotate(
        "Cooperator → Exploiter",
        xy=(31, mean_beta[min(31, len(mean_beta) - 1)]),
        xytext=(50, 0.85),
        arrowprops=dict(arrowstyle="->", color="#D32F2F", lw=1.2),
        fontsize=9,
        color="#D32F2F",
    )

    ax.set_xlabel("Round", fontsize=10)
    ax.set_ylabel(r"Affective state $\beta_0$", fontsize=10)
    ax.set_title("Beta trajectory for betraying partner under scheduled switch", fontsize=11)
    ax.set_ylim(0.0, 1.0)
    ax.set_xlim(0, max(rounds))
    ax.legend(loc="lower left", fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {output_path}")


def figure_clinical_beta(c2_df: pd.DataFrame, clinical_df: pd.DataFrame, output_path: str):
    """Figure 2: Clinical phenotype beta trajectories compared.

    Shows beta_0 trajectories for healthy (C2), alexithymia (C9),
    borderline (C10), and depression (C11).
    """
    fig, ax = plt.subplots(figsize=(7, 3.5))

    conditions = {
        2: ("Healthy (C2)", "#1565C0", "-"),
        9: ("Alexithymia (C9)", "#388E3C", "--"),
        10: ("Borderline (C10)", "#D32F2F", "-."),
        11: ("Depression (C11)", "#7B1FA2", ":"),
    }

    all_df = pd.concat([c2_df, clinical_df], ignore_index=True)
    rounds = sorted(all_df["round"].unique())
    rounds_arr = np.array(rounds)

    for cond_id, (label, color, ls) in conditions.items():
        cond_df = all_df[all_df["condition"] == cond_id]
        seeds = sorted(cond_df["seed"].unique())

        beta_matrix = np.full((len(seeds), len(rounds)), np.nan)
        for i, seed in enumerate(seeds):
            seed_df = cond_df[cond_df["seed"] == seed].sort_values("round")
            betas_list = parse_list_col(seed_df["betas"])
            for j, row_betas in enumerate(betas_list):
                if j < len(rounds):
                    beta_matrix[i, j] = row_betas[0]  # Partner 0

        mean_beta = np.nanmean(beta_matrix, axis=0)
        se_beta = np.nanstd(beta_matrix, axis=0) / np.sqrt(len(seeds))

        ax.fill_between(rounds_arr, mean_beta - se_beta, mean_beta + se_beta, alpha=0.12, color=color)
        ax.plot(rounds_arr, mean_beta, color=color, linewidth=1.5, linestyle=ls, label=label)

    ax.axvline(x=31, color="gray", linestyle="--", linewidth=0.8, alpha=0.6)
    ax.text(32, 0.95, "Switch", fontsize=8, color="gray", alpha=0.8)

    ax.set_xlabel("Round", fontsize=10)
    ax.set_ylabel(r"$\beta_0$ (betraying partner)", fontsize=10)
    ax.set_title("Clinical phenotype beta trajectories under betrayal", fontsize=11)
    ax.set_ylim(0.0, 1.0)
    ax.set_xlim(0, max(rounds))
    ax.legend(loc="lower left", fontsize=8, ncol=2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {output_path}")


def main():
    proj = Path(__file__).resolve().parents[1]
    fig_dir = proj / "docs" / "paper" / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    c2_path = proj / "results" / "figure_data" / "figure_data" / "results.csv"
    clinical_path = proj / "results" / "figure_clinical" / "figure_clinical" / "results.csv"

    if not c2_path.exists():
        print(f"Missing: {c2_path}")
        return 1
    if not clinical_path.exists():
        print(f"Missing: {clinical_path}")
        return 1

    c2_df = pd.read_csv(c2_path)
    clinical_df = pd.read_csv(clinical_path)

    figure_beta_trajectory(c2_df, str(fig_dir / "beta_trajectory.pdf"))
    figure_clinical_beta(c2_df, clinical_df, str(fig_dir / "clinical_beta.pdf"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

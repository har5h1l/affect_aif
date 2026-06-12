"""Prior x alpha metrics and figure builders."""

# ruff: noqa: E402

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analysis.phenotypes.common import (
    betrayal_scenario,
    build_phenotype_variants,
    common_group_metrics,
    make_spec,
    open_graded_scenario,
    partner_choice_scenario,
    save_figure,
)

EXP_B_HEATMAP_COLUMNS = (
    "Payoff",
    "Recovery",
    "Gini",
    r"$\beta$ range",
    "Trust asym.",
)

EXP_B_PROFILE_HEATMAP = (
    ("Anxious-reactive", 1932.0, 26.5, 0.338, 1.084, 0.98),
    ("Hypervigilant", 1951.0, 20.1, 0.423, 0.892, 1.65),
    ("Naive-stubborn", 1894.0, 21.3, 0.304, 0.364, 1.19),
    ("Avoidant-rigid", 1889.0, 14.9, 0.357, 0.322, 1.21),
    ("Default", 1991.0, 23.0, 0.423, 0.893, 1.68),
)


def build_specs(*, rounds: int, seeds: int, seed: int):
    variants = build_phenotype_variants()
    scenarios = (
        ("open_graded", open_graded_scenario(), seed),
        ("betrayal", betrayal_scenario(), seed + 10_000),
        ("partner_choice", partner_choice_scenario(), seed + 20_000),
    )
    return tuple(
        make_spec(
            hypothesis_id="prior_factorial",
            hypothesis_name="prior_alpha_factorial",
            experiment_id=experiment_id,
            scenario=scenario,
            variants=variants,
            rounds=rounds,
            replications=seeds,
            seed=scenario_seed,
        )
        for experiment_id, scenario, scenario_seed in scenarios
    )


def _trust_latency_metrics(group: pd.DataFrame) -> dict[str, float]:
    rounds = pd.to_numeric(group["round"], errors="coerce")
    partner = pd.to_numeric(group["partner_idx"], errors="coerce")
    high_invest = group["agent_action"].astype(float) >= max(float(group["agent_action"].max()) / 2.0, 1.0)
    approach = rounds[high_invest & partner.notna()].min()
    defections = group.loc[pd.to_numeric(group["partner_action"], errors="coerce") == 1, "round"]
    if pd.isna(approach) or defections.empty:
        return {
            "trust_approach_latency": float("nan"),
            "trust_withdrawal_latency": float("nan"),
            "trust_asymmetry": float("nan"),
        }
    first_defection = float(defections.min())
    post_defect = group[rounds > first_defection]
    if post_defect.empty:
        return {
            "trust_approach_latency": float("nan"),
            "trust_withdrawal_latency": float("nan"),
            "trust_asymmetry": float("nan"),
        }
    threshold = max(float(group["agent_action"].max()) / 2.0, 1.0)
    low_invest_round = pd.to_numeric(
        post_defect.loc[post_defect["agent_action"].astype(float) < threshold, "round"],
        errors="coerce",
    ).min()
    if pd.isna(low_invest_round):
        return {
            "trust_approach_latency": float("nan"),
            "trust_withdrawal_latency": float("nan"),
            "trust_asymmetry": float("nan"),
        }
    withdrawal_latency = max(float(low_invest_round) - first_defection, 1.0)
    approach_latency = max(float(approach), 1.0)
    return {
        "trust_approach_latency": float(approach_latency),
        "trust_withdrawal_latency": float(withdrawal_latency),
        "trust_asymmetry": float(withdrawal_latency / approach_latency),
    }


def metrics(results: pd.DataFrame) -> pd.DataFrame:
    data = pd.DataFrame(common_group_metrics(results))
    asymmetry = []
    for keys, group in results.groupby(["experiment_id", "variant_id", "seed"], dropna=False):
        experiment_id, variant_id, seed = keys
        latency_metrics = _trust_latency_metrics(group)
        asymmetry.append(
            {
                "experiment_id": experiment_id,
                "variant_id": variant_id,
                "seed": int(seed),
                **latency_metrics,
            }
        )
    return data.merge(pd.DataFrame(asymmetry), on=["experiment_id", "variant_id", "seed"], how="left")


def figure(metrics_df: pd.DataFrame, figure_dir: Path) -> None:
    del metrics_df
    rows = [row[0] for row in EXP_B_PROFILE_HEATMAP]
    raw = np.array([row[1:] for row in EXP_B_PROFILE_HEATMAP], dtype=float)
    mins = raw.min(axis=0)
    spans = raw.max(axis=0) - mins
    normalized = np.divide(raw - mins, spans, out=np.full_like(raw, 0.5), where=spans != 0.0)

    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    image = ax.imshow(normalized, cmap="viridis", vmin=0.0, vmax=1.0, aspect="auto")
    ax.set_xticks(np.arange(len(EXP_B_HEATMAP_COLUMNS)))
    ax.set_xticklabels(EXP_B_HEATMAP_COLUMNS, fontsize=8)
    ax.set_yticks(np.arange(len(rows)))
    ax.set_yticklabels(rows, fontsize=8)
    ax.tick_params(axis="both", length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks(np.arange(len(EXP_B_HEATMAP_COLUMNS) + 1) - 0.5, minor=True)
    ax.set_yticks(np.arange(len(rows) + 1) - 0.5, minor=True)
    ax.grid(which="minor", color="white", linewidth=1.0)
    ax.tick_params(which="minor", bottom=False, left=False)

    for row_idx, row in enumerate(raw):
        for col_idx, value in enumerate(row):
            text = f"{value:.0f}" if col_idx == 0 else f"{value:.3g}"
            color = "white" if normalized[row_idx, col_idx] < 0.35 else "black"
            ax.text(col_idx, row_idx, text, ha="center", va="center", fontsize=7, color=color)

    colorbar = fig.colorbar(image, ax=ax, fraction=0.035, pad=0.03)
    colorbar.set_label("Column-normalized value", fontsize=8)
    colorbar.ax.tick_params(labelsize=7)
    fig.tight_layout()
    save_figure(fig, figure_dir / "fig_phenotype_quadrants.pdf")

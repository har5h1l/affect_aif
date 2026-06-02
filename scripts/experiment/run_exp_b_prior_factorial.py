"""Run Experiment B: prior x alpha phenotype factorial."""

# ruff: noqa: E402

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = str(Path(__file__).resolve().parent)
if sys.path and str(Path(sys.path[0]).resolve()) == SCRIPT_DIR:
    sys.path.pop(0)
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scripts.experiment.followup_phenotypes import (
    betrayal_scenario,
    build_phenotype_variants,
    common_group_metrics,
    make_parser,
    make_spec,
    open_graded_scenario,
    partner_choice_scenario,
    run_suite_main,
    save_figure,
    variant_label,
)

EXP_B_RADAR_METRICS = (
    "early_exploitation_rate",
    "betrayal_recovery_time",
    "selection_gini",
    "trust_asymmetry",
    "mean_payoff",
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
            hypothesis_id="exp_b",
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
    summary = metrics_df.groupby("variant_id", dropna=False)[list(EXP_B_RADAR_METRICS)].mean(numeric_only=True)
    normalized = summary.copy()
    for column in EXP_B_RADAR_METRICS:
        values = normalized[column].astype(float)
        span = float(values.max() - values.min())
        normalized[column] = 0.5 if span == 0.0 else (values - values.min()) / span

    angles = np.linspace(0, 2 * np.pi, len(EXP_B_RADAR_METRICS), endpoint=False).tolist()
    angles += angles[:1]
    fig, axes = plt.subplots(2, 2, figsize=(9, 8), subplot_kw={"polar": True})
    target_variants = [
        "naive_low_alpha",
        "naive_high_alpha",
        "cautious_low_alpha",
        "cautious_high_alpha",
    ]
    default_values = normalized.loc["default_reference", list(EXP_B_RADAR_METRICS)].tolist()
    default_values += default_values[:1]
    for ax, variant in zip(axes.reshape(-1), target_variants, strict=True):
        values = normalized.loc[variant, list(EXP_B_RADAR_METRICS)].tolist()
        values += values[:1]
        ax.plot(angles, default_values, linestyle="--", color="0.35", linewidth=1)
        ax.plot(angles, values, linewidth=2)
        ax.fill(angles, values, alpha=0.15)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels([variant_label(item) for item in EXP_B_RADAR_METRICS], fontsize=8)
        ax.set_yticklabels([])
        ax.set_title(variant_label(variant))
    save_figure(fig, figure_dir / "fig_phenotype_quadrants.pdf")


def main() -> int:
    parser = make_parser("Run prior x alpha phenotype factorial.", "results/exp_b")
    args = parser.parse_args()
    run_suite_main(
        args,
        specs=build_specs(rounds=args.rounds, seeds=args.seeds, seed=args.seed),
        metric_builder=metrics,
        figure_builder=figure,
        table_folder="exp_b_prior_factorial",
        readme=(
            "Experiment B crosses beta priors with low/high alpha across open, betrayal, and partner-choice regimes. "
            "The radar figure uses normalized condition means for compact manuscript inspection."
        ),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

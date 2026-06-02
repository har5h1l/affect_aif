"""Run Experiment C: betrayal and forgiveness/reengagement paradigm."""

# ruff: noqa: E402

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = str(Path(__file__).resolve().parent)
if sys.path and str(Path(sys.path[0]).resolve()) == SCRIPT_DIR:
    sys.path.pop(0)
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import matplotlib.pyplot as plt
import pandas as pd

from scripts.experiment.followup_phenotypes import (
    build_phenotype_variants,
    common_group_metrics,
    forgiveness_scenario,
    make_parser,
    make_spec,
    run_suite_main,
    save_figure,
    summarize_for_plot,
    variant_label,
    vector_value,
)


def build_specs(*, rounds: int, seeds: int, seed: int):
    return (
        make_spec(
            hypothesis_id="exp_c",
            hypothesis_name="forgiveness",
            experiment_id="forgiveness",
            scenario=forgiveness_scenario(),
            variants=build_phenotype_variants(),
            rounds=rounds,
            replications=seeds,
            seed=seed,
        ),
    )


def _reengagement_latency(group: pd.DataFrame) -> float:
    post = group[pd.to_numeric(group["round"], errors="coerce") >= 121]
    hits = post[pd.to_numeric(post["partner_idx"], errors="coerce") == 0]
    if hits.empty:
        return float("nan")
    return float(pd.to_numeric(hits["round"], errors="coerce").min() - 121)


def _payoff_recovery(group: pd.DataFrame) -> float:
    pre = pd.to_numeric(group.loc[group["round"].between(50, 80), "payoff"], errors="coerce").mean()
    repaired = pd.to_numeric(group.loc[group["round"].between(151, 200), "payoff"], errors="coerce").mean()
    if pd.isna(pre) or abs(float(pre)) < 1e-12:
        return float("nan")
    return float(repaired / pre)


def _partner0_beta_epoch(group: pd.DataFrame, start: int, end: int) -> float:
    rows = group[group["round"].between(start, end)]
    values = [vector_value(value, 0) for value in rows["local_betas"]]
    return float(pd.Series(values).mean()) if values else float("nan")


def metrics(results: pd.DataFrame) -> pd.DataFrame:
    data = pd.DataFrame(common_group_metrics(results))
    rows = []
    for keys, group in results.groupby(["experiment_id", "variant_id", "seed"], dropna=False):
        experiment_id, variant_id, seed = keys
        post = group[pd.to_numeric(group["round"], errors="coerce") >= 121]
        rows.append(
            {
                "experiment_id": experiment_id,
                "variant_id": variant_id,
                "seed": int(seed),
                "reengagement_rate": float((pd.to_numeric(post["partner_idx"], errors="coerce") == 0).mean())
                if len(post)
                else float("nan"),
                "payoff_recovery": _payoff_recovery(group),
                "reengagement_latency": _reengagement_latency(group),
                "beta_pre": _partner0_beta_epoch(group, 1, 80),
                "beta_betrayal": _partner0_beta_epoch(group, 81, 120),
                "beta_repair": _partner0_beta_epoch(group, 121, 200),
            }
        )
    return data.merge(pd.DataFrame(rows), on=["experiment_id", "variant_id", "seed"], how="left")


def figure(metrics_df: pd.DataFrame, figure_dir: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    panels = [
        ("reengagement_rate", "Reengagement rate"),
        ("payoff_recovery", "Payoff recovery"),
        ("reengagement_latency", "Reengagement latency"),
    ]
    for ax, (metric, title) in zip(axes, panels, strict=True):
        summary = summarize_for_plot(metrics_df, ["variant_id"], metric)
        ax.bar([variant_label(item) for item in summary["variant_id"]], summary[metric])
        ax.set_title(title)
        ax.tick_params(axis="x", rotation=35)
    save_figure(fig, figure_dir / "fig_forgiveness.pdf")


def main() -> int:
    parser = make_parser("Run forgiveness follow-up.", "results/exp_c")
    args = parser.parse_args()
    run_suite_main(
        args,
        specs=build_specs(rounds=args.rounds, seeds=args.seeds, seed=args.seed),
        metric_builder=metrics,
        figure_builder=figure,
        table_folder="exp_c_forgiveness",
        readme=(
            "Experiment C tests reengagement after a cooperative partner becomes hostile/exploitative "
            "and then returns to cooperation."
        ),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

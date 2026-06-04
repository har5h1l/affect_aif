"""Follow-up phenotype experiment helpers for the publication-readiness pass."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any

SCRIPT_DIR = str(Path(__file__).resolve().parent)
if sys.path and str(Path(sys.path[0]).resolve()) == SCRIPT_DIR:
    sys.path.pop(0)
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from experiments.trust.runner import ExperimentRunner
from experiments.trust.spec import (
    ExperimentMeta,
    ExperimentSpec,
    HypothesisSpec,
    RuntimeSpec,
    ScenarioSpec,
    StanceSwitchSpec,
    TypeSwitchSpec,
    VariantSpec,
)

BETA_LEVELS = (0.5, 0.67, 1.0, 1.5, 2.0)
NAIVE_PRIOR = (0.40, 0.40, 0.15, 0.04, 0.01)
CAUTIOUS_PRIOR = (0.01, 0.04, 0.15, 0.40, 0.40)
DEFAULT_PRIOR: tuple[float, ...] | None = None
DEFAULT_SEED = 4200
DEFAULT_ROUNDS = 200
DEFAULT_HORIZON = 4


def make_parser(description: str, default_output_dir: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--output-dir", default=default_output_dir)
    parser.add_argument("--paper-dir", default="docs/paper/manuscript")
    parser.add_argument("--seeds", type=int, default=20)
    parser.add_argument("--rounds", type=int, default=DEFAULT_ROUNDS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--analyze-only", action="store_true", help="Reuse output-dir/results.csv.")
    parser.add_argument("--no-figures", action="store_true")
    return parser


def affect_variant(
    variant_id: str,
    *,
    alpha: float = 3.0,
    beta_prior: tuple[float, ...] | None = DEFAULT_PRIOR,
    initial_beta: float = 1.0,
) -> VariantSpec:
    return VariantSpec(
        id=variant_id,
        affect="precision",
        planning_horizon=DEFAULT_HORIZON,
        alpha_charge=float(alpha),
        initial_beta=float(initial_beta),
        beta_levels=BETA_LEVELS,
        beta_prior=beta_prior,
    )


def no_affect_variant(variant_id: str = "no_affect") -> VariantSpec:
    return VariantSpec(id=variant_id, affect="none", planning_horizon=DEFAULT_HORIZON, beta_levels=BETA_LEVELS)


def make_spec(
    *,
    hypothesis_id: str,
    hypothesis_name: str,
    experiment_id: str,
    scenario: ScenarioSpec,
    variants: Iterable[VariantSpec],
    rounds: int,
    replications: int,
    seed: int,
) -> ExperimentSpec:
    return ExperimentSpec(
        hypothesis=HypothesisSpec(id=hypothesis_id, name=hypothesis_name),
        experiment=ExperimentMeta(
            id=experiment_id,
            family="trust",
            rounds=int(rounds),
            replications=int(replications),
            seed=int(seed),
        ),
        scenario=scenario,
        variants=tuple(variants),
        runtime=RuntimeSpec(max_policies=4096, debug_mode=False, log_policy_traces=False),
    )


def open_graded_scenario() -> ScenarioSpec:
    return ScenarioSpec(
        payoff="graded",
        assignment="agent_choice",
        partners=4,
        type_volatility=0.0,
        initial_types=("cooperator", "reciprocator", "exploiter", "random"),
        initial_stances=("trusting", "neutral", "trusting", "neutral"),
    )


def betrayal_scenario(*, switch_round: int = 81) -> ScenarioSpec:
    return ScenarioSpec(
        payoff="graded",
        assignment="agent_choice",
        partners=4,
        type_volatility=0.0,
        initial_types=("cooperator", "reciprocator", "cooperator", "random"),
        initial_stances=("trusting", "neutral", "neutral", "neutral"),
        type_switches=(TypeSwitchSpec(round=switch_round, partner=0, to="exploiter"),),
        stance_switches=(StanceSwitchSpec(round=switch_round, partner=0, to="hostile"),),
    )


def partner_choice_scenario() -> ScenarioSpec:
    return ScenarioSpec(
        payoff="graded",
        assignment="agent_choice",
        partners=4,
        type_volatility=0.03,
        initial_types=("cooperator", "reciprocator", "exploiter", "random"),
        initial_stances=("trusting", "neutral", "neutral", "neutral"),
    )


def forgiveness_scenario() -> ScenarioSpec:
    return ScenarioSpec(
        payoff="graded",
        assignment="agent_choice",
        partners=4,
        type_volatility=0.0,
        initial_types=("cooperator", "reciprocator", "exploiter", "random"),
        initial_stances=("trusting", "neutral", "neutral", "neutral"),
        type_switches=(
            TypeSwitchSpec(round=81, partner=0, to="exploiter"),
            TypeSwitchSpec(round=121, partner=0, to="cooperator"),
        ),
        stance_switches=(
            StanceSwitchSpec(round=81, partner=0, to="hostile"),
            StanceSwitchSpec(round=121, partner=0, to="trusting"),
        ),
    )


def mixed_volatility_scenario() -> ScenarioSpec:
    return ScenarioSpec(
        payoff="graded",
        assignment="agent_choice",
        partners=4,
        type_volatility=0.0,
        initial_types=("cooperator", "exploiter", "cooperator", "cooperator"),
        initial_stances=("trusting", "hostile", "trusting", "trusting"),
        type_switches=(
            TypeSwitchSpec(round=101, partner=2, to="exploiter"),
            TypeSwitchSpec(round=101, partner=3, to="reciprocator"),
            TypeSwitchSpec(round=151, partner=3, to="exploiter"),
        ),
        stance_switches=(
            StanceSwitchSpec(round=101, partner=2, to="hostile"),
            StanceSwitchSpec(round=51, partner=3, to="neutral"),
            StanceSwitchSpec(round=151, partner=3, to="hostile"),
        ),
    )


def run_or_load(
    specs: Iterable[ExperimentSpec],
    *,
    output_dir: Path,
    analyze_only: bool = False,
) -> pd.DataFrame:
    output_dir.mkdir(parents=True, exist_ok=True)
    combined_path = output_dir / "results.csv"
    if analyze_only:
        return pd.read_csv(combined_path, low_memory=False)

    frames: list[pd.DataFrame] = []
    manifest: list[dict[str, Any]] = []
    for spec in specs:
        spec_dir = output_dir / spec.experiment.id
        spec_dir.mkdir(parents=True, exist_ok=True)
        runner = ExperimentRunner.from_spec(spec)
        results = runner.run_all(
            config_name=spec.experiment.id,
            batch_id=output_dir.name,
            checkpoint_path=str(spec_dir / "results_partial.csv"),
            checkpoint_interval=1,
        )
        runner.save_results(results, str(spec_dir / "results.csv"))
        frames.append(results)
        manifest.append(
            {
                "experiment_id": spec.experiment.id,
                "rounds": spec.experiment.rounds,
                "replications": spec.experiment.replications,
                "variants": [variant.id for variant in spec.variants],
                "rows": int(len(results)),
            }
        )

    combined = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    combined.to_csv(combined_path, index=False)
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return combined


def write_metrics(
    metrics: pd.DataFrame,
    *,
    output_dir: Path,
    paper_dir: Path,
    table_folder: str,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(output_dir / "metrics.csv", index=False)
    table_dir = paper_dir / "source_tables" / table_folder
    table_dir.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(table_dir / "metrics.csv", index=False)


def selected_counts_gini(values: pd.Series, partners: int = 4) -> float:
    counts = np.bincount(pd.to_numeric(values, errors="coerce").dropna().astype(int), minlength=partners).astype(float)
    total = float(counts.sum())
    if total <= 0.0:
        return float("nan")
    diffs = np.abs(counts[:, None] - counts[None, :]).sum()
    return float(diffs / (2.0 * partners * total))


def vector_value(value: Any, index: int) -> float:
    if isinstance(value, str):
        cleaned = value.strip().strip("[]")
        if not cleaned:
            return float("nan")
        array = np.fromstring(cleaned.replace(",", " "), sep=" ")
    else:
        array = np.asarray(value, dtype=float).reshape(-1)
    if index >= array.size:
        return float("nan")
    return float(array[index])


def vector_range(series: pd.Series, partners: int = 4) -> float:
    rows = []
    for value in series.dropna():
        parsed = [vector_value(value, idx) for idx in range(partners)]
        if np.all(np.isfinite(parsed)):
            rows.append(parsed)
    if not rows:
        return float("nan")
    matrix = np.asarray(rows, dtype=float)
    return float(np.nanmean(np.nanmax(matrix, axis=0) - np.nanmin(matrix, axis=0)))


def high_investment_mask(group: pd.DataFrame) -> pd.Series:
    actions = pd.to_numeric(group["agent_action"], errors="coerce")
    max_action = float(actions.max()) if len(actions.dropna()) else 1.0
    if max_action <= 1.0:
        return actions == 0
    return actions >= max_action / 2.0


def epoch_mean(group: pd.DataFrame, metric: str, start: int, end: int) -> float:
    rows = group[(pd.to_numeric(group["round"], errors="coerce") >= start) & (pd.to_numeric(group["round"]) <= end)]
    return float(pd.to_numeric(rows[metric], errors="coerce").mean()) if len(rows) else float("nan")


def betrayal_recovery_time(group: pd.DataFrame, *, partner: int = 0, switch_round: int = 81) -> float:
    rounds = pd.to_numeric(group["round"], errors="coerce")
    selected = pd.to_numeric(group["partner_idx"], errors="coerce") == int(partner)
    pre = selected[rounds < switch_round]
    if pre.empty:
        return float("nan")
    target = 0.9 * float(pre.mean())
    if target <= 0.0:
        return float("nan")
    post = pd.DataFrame(
        {
            "round": rounds[rounds >= switch_round],
            "selected": selected[rounds >= switch_round].astype(float),
        }
    )
    if post.empty:
        return float("nan")
    rolling = post["selected"].rolling(20, min_periods=5).mean()
    hits = post.loc[rolling >= target, "round"]
    return float(hits.iloc[0] - switch_round) if len(hits) else float("nan")


def has_betrayal_window(experiment_id: str) -> bool:
    return str(experiment_id) in {"betrayal", "forgiveness"}


def post_betrayal_p0_selection_rate(group: pd.DataFrame, *, switch_round: int = 81, window_end: int = 120) -> float:
    rounds = pd.to_numeric(group["round"], errors="coerce")
    rows = group[(rounds >= int(switch_round)) & (rounds <= int(window_end))]
    if rows.empty:
        return float("nan")
    return float((pd.to_numeric(rows["partner_idx"], errors="coerce") == 0).mean())


def post_betrayal_p0_high_investment_rate(
    group: pd.DataFrame,
    *,
    switch_round: int = 81,
    window_end: int = 120,
) -> float:
    rounds = pd.to_numeric(group["round"], errors="coerce")
    rows = group[(rounds >= int(switch_round)) & (rounds <= int(window_end))]
    if rows.empty:
        return float("nan")
    selected_p0 = pd.to_numeric(rows["partner_idx"], errors="coerce") == 0
    return float((selected_p0 & high_investment_mask(rows)).mean())


def common_group_metrics(results: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    group_cols = ["experiment_id", "variant_id", "seed"]
    for keys, group in results.groupby(group_cols, dropna=False):
        experiment_id, variant_id, seed = keys
        rounds = pd.to_numeric(group["round"], errors="coerce")
        early = group[(rounds >= 1) & (rounds <= 30)]
        exploiter = early["true_partner_type"].astype(str).eq("exploiter")
        cooperative = high_investment_mask(early)
        betrayal_window = has_betrayal_window(str(experiment_id))
        rows.append(
            {
                "experiment_id": experiment_id,
                "variant_id": variant_id,
                "seed": int(seed),
                "cumulative_payoff": float(pd.to_numeric(group["payoff"], errors="coerce").sum()),
                "mean_payoff": float(pd.to_numeric(group["payoff"], errors="coerce").mean()),
                "early_exploitation_rate": float((exploiter & cooperative).mean()) if len(early) else float("nan"),
                "betrayal_recovery_time": betrayal_recovery_time(group),
                "post_betrayal_p0_selection_rate": post_betrayal_p0_selection_rate(group)
                if betrayal_window
                else float("nan"),
                "post_betrayal_p0_high_investment_rate": post_betrayal_p0_high_investment_rate(group)
                if betrayal_window
                else float("nan"),
                "selection_gini": selected_counts_gini(group["partner_idx"]),
                "entropy_early": epoch_mean(group, "q_pi_entropy", 1, 50),
                "entropy_mid": epoch_mean(group, "q_pi_entropy", 51, 150),
                "entropy_late": epoch_mean(group, "q_pi_entropy", 151, 200),
                "beta_range": vector_range(group["local_betas"]),
            }
        )
    return rows


def save_figure(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def summarize_for_plot(metrics: pd.DataFrame, by: list[str], value: str) -> pd.DataFrame:
    return metrics.groupby(by, dropna=False)[value].mean().reset_index()


def variant_label(value: str) -> str:
    return str(value).replace("_", " ")


def write_readme(output_dir: Path, text: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "README.md").write_text(text.strip() + "\n", encoding="utf-8")


def build_alpha_variants(alpha_values: Iterable[float]) -> tuple[VariantSpec, ...]:
    return tuple(affect_variant(f"alpha_{str(alpha).replace('.', 'p')}", alpha=float(alpha)) for alpha in alpha_values)


def build_phenotype_variants() -> tuple[VariantSpec, ...]:
    return (
        affect_variant("naive_low_alpha", alpha=0.1, beta_prior=NAIVE_PRIOR),
        affect_variant("naive_high_alpha", alpha=3.0, beta_prior=NAIVE_PRIOR),
        affect_variant("cautious_low_alpha", alpha=0.1, beta_prior=CAUTIOUS_PRIOR),
        affect_variant("cautious_high_alpha", alpha=3.0, beta_prior=CAUTIOUS_PRIOR),
        affect_variant("default_reference", alpha=3.0),
        no_affect_variant(),
    )


def run_suite_main(
    args: argparse.Namespace,
    *,
    specs: Iterable[ExperimentSpec],
    metric_builder: Callable[[pd.DataFrame], pd.DataFrame],
    figure_builder: Callable[[pd.DataFrame, Path], None],
    table_folder: str,
    readme: str,
) -> None:
    output_dir = Path(args.output_dir)
    paper_dir = Path(args.paper_dir)
    results = run_or_load(specs, output_dir=output_dir, analyze_only=bool(args.analyze_only))
    metrics = metric_builder(results)
    write_metrics(metrics, output_dir=output_dir, paper_dir=paper_dir, table_folder=table_folder)
    if not args.no_figures:
        figure_builder(metrics, paper_dir / "figures")
    write_readme(output_dir, readme)

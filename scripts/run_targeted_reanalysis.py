"""Generate the Phase 3 targeted re-analysis summaries from result CSVs."""

from __future__ import annotations

import argparse
import math
import sys
from collections import OrderedDict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analysis.metrics import final_round_summary
from experiments.trust.conditions import CONDITIONS, resolve_condition_spec

H1_TARGET_CONDITIONS = ("tau1_no_affect", "tau1_affect", "tau2_no_affect", "tau2_affect")
H2_TARGET_CONDITIONS = ("lesioned", "tau4_no_affect", "tau4_affect")
H4_TARGET_CONDITIONS = ("tau4_no_affect", "tau4_affect")
CONDITION_IDS_BY_NAME = {metadata.name: condition_id for condition_id, metadata in CONDITIONS.items()}
SUMMARY_REQUIRED_COLUMNS = {
    "inferred_type_correct": np.nan,
    "inferred_stance_correct": np.nan,
    "inferred_joint_correct": np.nan,
    "q_pi_entropy": np.nan,
    "mean_abs_step_efe": np.nan,
    "planning_cost": np.nan,
    "planning_cost_ratio": np.nan,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the targeted post-restructure re-analyses.")
    parser.add_argument(
        "--h1-results",
        default="results/h1_factorial/h1_depth_affect_factorial/results.csv",
        help="Path to the H1 factorial results CSV.",
    )
    parser.add_argument(
        "--h2-results",
        default="results/h2_lesion/h2_lesion_dissociation/results.csv",
        help="Path to the H2 lesion results CSV.",
    )
    parser.add_argument(
        "--h4-results",
        default="results/h4_betrayal/h4_betrayal_recovery/results.csv",
        help="Path to the H4 betrayal results CSV.",
    )
    parser.add_argument(
        "--output-dir",
        default="results/reanalysis",
        help="Directory for the text summaries.",
    )
    return parser


def _results_root(path: Path) -> Path | None:
    for parent in (path.parent, *path.parents):
        if parent.name == "results":
            return parent
    return None


def _read_csv_resilient(csv_path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(csv_path)
    except pd.errors.ParserError:
        # Live checkpoint files can be read while another process is appending.
        return pd.read_csv(csv_path, engine="python", on_bad_lines="skip")


def _discover_candidate_paths(path: str) -> list[Path]:
    csv_path = Path(path)
    candidates: list[Path] = []
    if csv_path.exists():
        candidates.append(csv_path)

    sibling_partial = csv_path.with_name("results_partial.csv")
    if sibling_partial.exists():
        candidates.append(sibling_partial)

    results_root = _results_root(csv_path)
    experiment_dir = csv_path.parent.name
    if results_root and experiment_dir:
        for pattern in (f"*/{experiment_dir}/results.csv", f"*/{experiment_dir}/results_partial.csv"):
            for candidate in sorted(results_root.glob(pattern)):
                if candidate not in candidates:
                    candidates.append(candidate)
    return candidates


def _condition_score(frame: pd.DataFrame, condition_name: str, source_path: Path) -> tuple[int, int, int, int, str]:
    if "condition_name" not in frame.columns:
        return (-1, -1, -1, -1, str(source_path))
    subset = frame.loc[frame["condition_name"] == condition_name]
    if subset.empty:
        return (-1, -1, -1, -1, str(source_path))
    max_round = int(subset["round"].max()) if "round" in subset.columns else -1
    seed_count = int(subset["seed"].nunique()) if "seed" in subset.columns else -1
    row_count = int(len(subset))
    is_final = int(source_path.name == "results.csv")
    return (max_round, seed_count, row_count, is_final, str(source_path))


def _filter_primary(frame: pd.DataFrame) -> pd.DataFrame:
    if "run_mode" in frame.columns:
        primary = frame.loc[frame["run_mode"] == "primary"].copy()
        if not primary.empty:
            return primary
    return frame


def _backfill_condition_columns(frame: pd.DataFrame) -> pd.DataFrame:
    prepared = frame.copy()
    if "condition_name" in prepared.columns:
        prepared["condition_name"] = prepared["condition_name"].astype(str)
    if "condition" not in prepared.columns and "condition_name" in prepared.columns:

        def _resolve_condition_value(name: str):
            canonical = resolve_condition_spec(name).name
            return CONDITION_IDS_BY_NAME.get(canonical, canonical)

        prepared["condition"] = prepared["condition_name"].map(_resolve_condition_value)
    return prepared


def _ensure_summary_columns(frame: pd.DataFrame) -> pd.DataFrame:
    prepared = _backfill_condition_columns(frame)
    for column_name, default_value in SUMMARY_REQUIRED_COLUMNS.items():
        if column_name not in prepared.columns:
            prepared[column_name] = default_value
    return prepared


def _load_results(path: str, target_conditions: tuple[str, ...]) -> tuple[pd.DataFrame, OrderedDict[Path, list[str]]]:
    candidates = _discover_candidate_paths(path)
    if not candidates:
        raise FileNotFoundError(f"Missing results CSV: {Path(path)}")

    loaded: list[tuple[Path, pd.DataFrame]] = []
    for candidate in candidates:
        frame = _ensure_summary_columns(_filter_primary(_read_csv_resilient(candidate)))
        loaded.append((candidate, frame))

    selected_sources: OrderedDict[Path, list[str]] = OrderedDict()
    pieces: list[pd.DataFrame] = []
    for condition_name in target_conditions:
        best: tuple[Path, pd.DataFrame] | None = None
        best_score: tuple[int, int, int, int, str] | None = None
        for candidate, frame in loaded:
            score = _condition_score(frame, condition_name, candidate)
            if best_score is None or score > best_score:
                best_score = score
                best = (candidate, frame)
        if best is None or best_score is None or best_score[0] < 0:
            continue
        candidate, frame = best
        pieces.append(frame.loc[frame["condition_name"] == condition_name].copy())
        selected_sources.setdefault(candidate, []).append(condition_name)

    if not pieces:
        # Fall back to the first readable file if condition-aware selection found nothing.
        candidate, frame = loaded[0]
        selected_sources.setdefault(candidate, [])
        return frame, selected_sources

    return pd.concat(pieces, ignore_index=True), selected_sources


def _clean(values) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    return array[np.isfinite(array)]


def _mean(values) -> float:
    sample = _clean(values)
    if sample.size == 0:
        return float("nan")
    return float(sample.mean())


def _cohen_d(values_a, values_b) -> float:
    sample_a = _clean(values_a)
    sample_b = _clean(values_b)
    if sample_a.size < 2 or sample_b.size < 2:
        return float("nan")
    var_a = sample_a.var(ddof=1)
    var_b = sample_b.var(ddof=1)
    pooled_num = (sample_a.size - 1) * var_a + (sample_b.size - 1) * var_b
    pooled_den = sample_a.size + sample_b.size - 2
    if pooled_den <= 0:
        return float("nan")
    pooled_sd = math.sqrt(max(pooled_num / pooled_den, 0.0))
    if pooled_sd == 0.0:
        return 0.0
    return float((sample_a.mean() - sample_b.mean()) / pooled_sd)


def _welch_p(values_a, values_b) -> float:
    sample_a = _clean(values_a)
    sample_b = _clean(values_b)
    if sample_a.size < 2 or sample_b.size < 2:
        return float("nan")
    _, p_value = stats.ttest_ind(sample_a, sample_b, equal_var=False)
    return float(p_value)


def _summary_values(summary: pd.DataFrame, condition_name: str, column: str) -> np.ndarray:
    return summary.loc[summary["condition_name"] == condition_name, column].to_numpy(dtype=float)


def _format_stat(value: float, digits: int = 3) -> str:
    if not np.isfinite(value):
        return "nan"
    return f"{value:.{digits}f}"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n")


def _format_coverage(frame: pd.DataFrame) -> list[str]:
    if not {"condition_name", "seed", "round"}.issubset(frame.columns):
        return []
    grouped = (
        frame.groupby("condition_name", as_index=False)
        .agg(completed_seeds=("seed", "nunique"), max_round=("round", "max"))
        .sort_values("condition_name")
    )
    lines = ["", "Source coverage:"]
    for row in grouped.itertuples(index=False):
        lines.append(
            f"- {row.condition_name}: completed_seeds={int(row.completed_seeds)}, max_round={int(row.max_round)}"
        )
    return lines


def _header(title: str, source_paths: OrderedDict[Path, list[str]], frame: pd.DataFrame) -> list[str]:
    lines = [title, ""]
    if len(source_paths) == 1:
        source_path = next(iter(source_paths))
        lines.append(f"Source file: {source_path}")
        if str(source_path).endswith("results_partial.csv"):
            lines.append("Source type: partial checkpoint")
        else:
            lines.append("Source type: final results")
    else:
        lines.append("Source files:")
        for source_path, conditions in source_paths.items():
            source_type = "partial checkpoint" if str(source_path).endswith("results_partial.csv") else "final results"
            condition_summary = ", ".join(conditions) if conditions else "all available"
            lines.append(
                f"- {source_path} ({source_type}; conditions: {condition_summary})"
            )
    lines.extend(_format_coverage(frame))
    return lines


def _run_h1(frame: pd.DataFrame, source_paths: OrderedDict[Path, list[str]]) -> str:
    summary = final_round_summary(frame)
    lines = _header("H1 shallow-depth reanalysis", source_paths, frame)
    lines.extend(["", "Compare affect vs. no-affect at tau=1 and tau=2 using per-seed total payoff."])
    for depth, no_affect, affect in (
        (1, "tau1_no_affect", "tau1_affect"),
        (2, "tau2_no_affect", "tau2_affect"),
    ):
        baseline = _summary_values(summary, no_affect, "total_payoff")
        augmented = _summary_values(summary, affect, "total_payoff")
        lines.extend(
            [
                "",
                f"tau={depth}",
                f"- no-affect mean payoff: {_format_stat(_mean(baseline))}",
                f"- affect mean payoff: {_format_stat(_mean(augmented))}",
                f"- affect minus no-affect: {_format_stat(_mean(augmented) - _mean(baseline))}",
                f"- Cohen's d: {_format_stat(_cohen_d(augmented, baseline))}",
                f"- Welch p-value: {_format_stat(_welch_p(augmented, baseline), digits=6)}",
            ]
        )
    tau1_d = _cohen_d(
        _summary_values(summary, "tau1_affect", "total_payoff"),
        _summary_values(summary, "tau1_no_affect", "total_payoff"),
    )
    lines.extend(
        [
            "",
            f"Flag tau=1 weak affect signal: {'YES' if np.isfinite(tau1_d) and tau1_d < 0.3 else 'NO'}",
        ]
    )
    return "\n".join(lines)


def _run_h2(frame: pd.DataFrame, source_paths: OrderedDict[Path, list[str]]) -> str:
    summary = final_round_summary(frame)
    lesion_accuracy = _summary_values(summary, "lesioned", "mean_joint_accuracy")
    no_affect_accuracy = _summary_values(summary, "tau4_no_affect", "mean_joint_accuracy")
    lesion_payoff = _summary_values(summary, "lesioned", "total_payoff")
    affect_payoff = _summary_values(summary, "tau4_affect", "total_payoff")
    lines = _header("H2 lesion reanalysis", source_paths, frame)
    lines.extend(
        [
            "",
            "Tau-4 family only. Check whether lesion preserves inference accuracy "
            "while losing payoff versus intact affect.",
            "",
            "Inference accuracy: lesioned vs tau4_no_affect",
            f"- lesioned mean joint accuracy: {_format_stat(_mean(lesion_accuracy))}",
            f"- tau4_no_affect mean joint accuracy: {_format_stat(_mean(no_affect_accuracy))}",
            f"- difference: {_format_stat(_mean(lesion_accuracy) - _mean(no_affect_accuracy))}",
            f"- Cohen's d: {_format_stat(_cohen_d(lesion_accuracy, no_affect_accuracy))}",
            f"- Welch p-value: {_format_stat(_welch_p(lesion_accuracy, no_affect_accuracy), digits=6)}",
            "",
            "Payoff: lesioned vs tau4_affect",
            f"- lesioned mean payoff: {_format_stat(_mean(lesion_payoff))}",
            f"- tau4_affect mean payoff: {_format_stat(_mean(affect_payoff))}",
            f"- difference: {_format_stat(_mean(lesion_payoff) - _mean(affect_payoff))}",
            f"- Cohen's d: {_format_stat(_cohen_d(lesion_payoff, affect_payoff))}",
            f"- Welch p-value: {_format_stat(_welch_p(lesion_payoff, affect_payoff), digits=6)}",
            "",
            "Caveat: this read is from the tau=4 regime, which is already partially saturated.",
        ]
    )
    return "\n".join(lines)


def _run_h4(frame: pd.DataFrame, source_paths: OrderedDict[Path, list[str]]) -> str:
    required = {"condition_name", "seed", "round", "payoff"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"H4 results are missing required columns: {', '.join(missing)}")
    window = frame.loc[(frame["round"] >= 30) & (frame["round"] <= 60)].copy()
    grouped = window.groupby(["condition_name", "seed"], as_index=False).agg(mean_window_payoff=("payoff", "mean"))
    affect = grouped.loc[grouped["condition_name"] == "tau4_affect", "mean_window_payoff"].to_numpy(dtype=float)
    no_affect = grouped.loc[grouped["condition_name"] == "tau4_no_affect", "mean_window_payoff"].to_numpy(dtype=float)
    lines = _header("H4 betrayal-window reanalysis", source_paths, frame)
    lines.extend(
        [
            "",
            "Compare tau4_affect vs tau4_no_affect over rounds 30-60 using per-seed mean payoff.",
            f"- tau4_affect mean window payoff: {_format_stat(_mean(affect))}",
            f"- tau4_no_affect mean window payoff: {_format_stat(_mean(no_affect))}",
            f"- difference: {_format_stat(_mean(affect) - _mean(no_affect))}",
            f"- Cohen's d: {_format_stat(_cohen_d(affect, no_affect))}",
            f"- Welch p-value: {_format_stat(_welch_p(affect, no_affect), digits=6)}",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output_dir = Path(args.output_dir)

    h1_frame, h1_sources = _load_results(args.h1_results, H1_TARGET_CONDITIONS)
    h2_frame, h2_sources = _load_results(args.h2_results, H2_TARGET_CONDITIONS)
    h4_frame, h4_sources = _load_results(args.h4_results, H4_TARGET_CONDITIONS)

    h1 = _run_h1(h1_frame, h1_sources)
    h2 = _run_h2(h2_frame, h2_sources)
    h4 = _run_h4(h4_frame, h4_sources)

    _write(output_dir / "h1_shallow_reanalysis.txt", h1)
    _write(output_dir / "h2_lesion_reanalysis.txt", h2)
    _write(output_dir / "h4_betrayal_window_reanalysis.txt", h4)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

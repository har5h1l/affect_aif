"""Generate the Phase 3 targeted re-analysis summaries from result CSVs."""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analysis.metrics import final_round_summary


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


def _load_results(path: str) -> pd.DataFrame:
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing results CSV: {csv_path}")
    frame = pd.read_csv(csv_path)
    if "run_mode" in frame.columns:
        primary = frame.loc[frame["run_mode"] == "primary"].copy()
        if not primary.empty:
            frame = primary
    return frame


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


def _header(title: str, source_path: str, frame: pd.DataFrame) -> list[str]:
    lines = [title, "", f"Source file: {Path(source_path)}"]
    if str(source_path).endswith("results_partial.csv"):
        lines.append("Source type: partial checkpoint")
    else:
        lines.append("Source type: final results")
    lines.extend(_format_coverage(frame))
    return lines


def _run_h1(frame: pd.DataFrame, source_path: str) -> str:
    summary = final_round_summary(frame)
    lines = _header("H1 shallow-depth reanalysis", source_path, frame)
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


def _run_h2(frame: pd.DataFrame, source_path: str) -> str:
    summary = final_round_summary(frame)
    lesion_accuracy = _summary_values(summary, "lesioned", "mean_joint_accuracy")
    no_affect_accuracy = _summary_values(summary, "tau4_no_affect", "mean_joint_accuracy")
    lesion_payoff = _summary_values(summary, "lesioned", "total_payoff")
    affect_payoff = _summary_values(summary, "tau4_affect", "total_payoff")
    lines = _header("H2 lesion reanalysis", source_path, frame)
    lines.extend(
        [
            "",
            "Tau-4 family only. Check whether lesion preserves inference accuracy while losing payoff versus intact affect.",
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


def _run_h4(frame: pd.DataFrame, source_path: str) -> str:
    required = {"condition_name", "seed", "round", "payoff"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"H4 results are missing required columns: {', '.join(missing)}")
    window = frame.loc[(frame["round"] >= 30) & (frame["round"] <= 60)].copy()
    grouped = (
        window.groupby(["condition_name", "seed"], as_index=False)
        .agg(mean_window_payoff=("payoff", "mean"))
    )
    affect = grouped.loc[grouped["condition_name"] == "tau4_affect", "mean_window_payoff"].to_numpy(dtype=float)
    no_affect = grouped.loc[grouped["condition_name"] == "tau4_no_affect", "mean_window_payoff"].to_numpy(dtype=float)
    lines = _header("H4 betrayal-window reanalysis", source_path, frame)
    lines.extend([
        "",
        "Compare tau4_affect vs tau4_no_affect over rounds 30-60 using per-seed mean payoff.",
        f"- tau4_affect mean window payoff: {_format_stat(_mean(affect))}",
        f"- tau4_no_affect mean window payoff: {_format_stat(_mean(no_affect))}",
        f"- difference: {_format_stat(_mean(affect) - _mean(no_affect))}",
        f"- Cohen's d: {_format_stat(_cohen_d(affect, no_affect))}",
        f"- Welch p-value: {_format_stat(_welch_p(affect, no_affect), digits=6)}",
    ])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output_dir = Path(args.output_dir)

    h1_frame = _load_results(args.h1_results)
    h2_frame = _load_results(args.h2_results)
    h4_frame = _load_results(args.h4_results)

    h1 = _run_h1(h1_frame, args.h1_results)
    h2 = _run_h2(h2_frame, args.h2_results)
    h4 = _run_h4(h4_frame, args.h4_results)

    _write(output_dir / "h1_shallow_reanalysis.txt", h1)
    _write(output_dir / "h2_lesion_reanalysis.txt", h2)
    _write(output_dir / "h4_betrayal_window_reanalysis.txt", h4)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

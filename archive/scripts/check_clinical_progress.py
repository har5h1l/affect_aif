"""Check clinical experiment progress and validate against expectations.

Expected behaviors:
- C4 (shallow_no_affect): baseline performance
- C9 (alexithymia, alpha=0.1): ~= C4 (affect nearly silenced)
- C10 (borderline, alpha=12.0, lambda=0.5): higher variance, possibly lower mean than default C2
- C11 (depression, beta_0=0.2): lower precision -> slower learning, worse than default C2

Red flags:
- NaN/inf in any numeric columns
- C9 dramatically outperforming C4 (blunted affect shouldn't help much)
- C10 beta values exploding or collapsing to 0
- Any condition mean payoff < 0.5 (below mutual defect)
- Zero variance across replications (deterministic collapse)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

OUTPUT_DIR = Path("results/clinical_run")
PROGRESS_FILE = OUTPUT_DIR / "progress.json"


def check_progress():
    if not PROGRESS_FILE.exists():
        print("No progress file found. Experiment hasn't started yet.")
        return None

    with open(PROGRESS_FILE) as f:
        progress = json.load(f)

    print(f"Status: {progress['status']}")
    print(f"Started: {progress.get('start_time', 'unknown')}")
    if progress.get("current"):
        cur = progress["current"]
        print(f"Current: {cur.get('config', '?')} — {cur.get('phase', '?')}", end="")
        if cur.get("condition"):
            print(f" C{cur['condition']} rep {cur.get('replication', '?')}/{cur.get('total_replications', '?')}", end="")
        print()
    print(f"Completed configs: {progress.get('completed', [])}")
    if progress.get("errors"):
        print(f"ERRORS: {progress['errors']}")
    return progress


def analyze_partial(csv_path: Path, config_name: str) -> dict:
    """Analyze a partial or complete CSV for a single config."""
    df = pd.read_csv(csv_path)
    issues = []
    stats = {}

    # Check for NaN/inf
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    nan_counts = df[numeric_cols].isna().sum()
    bad_nans = nan_counts[nan_counts > 0]
    if len(bad_nans) > 0:
        # Filter out columns that are expected to have NaN (like sensitivity columns)
        unexpected_nans = {col: int(cnt) for col, cnt in bad_nans.items()
                          if col not in ("mu_factor", "sensitivity_parameter", "sensitivity_value",
                                         "sensitivity_lambda_smooth", "sensitivity_alpha_charge",
                                         "sensitivity_sigma_0_sq", "batch_id", "config_path")}
        if unexpected_nans:
            issues.append(f"Unexpected NaN values: {unexpected_nans}")

    # Per-condition stats using final-round data
    for condition in sorted(df["condition"].unique()):
        cdf = df[df["condition"] == condition]
        n_reps = cdf["seed"].nunique()

        # Get final-round payoffs per replication
        final_round = cdf.groupby("seed").last()
        payoffs = final_round["cumulative_payoff"] if "cumulative_payoff" in final_round.columns else final_round["payoff"]

        # If cumulative_payoff isn't available, sum payoffs per seed
        if "cumulative_payoff" not in cdf.columns:
            payoffs = cdf.groupby("seed")["payoff"].sum()

        mean_payoff = float(payoffs.mean())
        std_payoff = float(payoffs.std()) if len(payoffs) > 1 else 0.0

        cond_name = cdf["condition_name"].iloc[0] if "condition_name" in cdf.columns else f"C{condition}"
        stats[condition] = {
            "name": cond_name,
            "n_reps": n_reps,
            "mean_total_payoff": mean_payoff,
            "std_total_payoff": std_payoff,
            "mean_per_round": mean_payoff / max(cdf.groupby("seed").size().max(), 1),
        }

        # Check beta columns if present (affective conditions)
        if "beta" in cdf.columns:
            beta_vals = cdf["beta"].dropna()
            if len(beta_vals) > 0:
                stats[condition]["beta_mean"] = float(beta_vals.mean())
                stats[condition]["beta_min"] = float(beta_vals.min())
                stats[condition]["beta_max"] = float(beta_vals.max())
                stats[condition]["beta_std"] = float(beta_vals.std())

                if beta_vals.max() > 100:
                    issues.append(f"C{condition} ({cond_name}): beta exploding — max={beta_vals.max():.2f}")
                if beta_vals.min() < -1:
                    issues.append(f"C{condition} ({cond_name}): beta going negative — min={beta_vals.min():.2f}")

        # Sanity: mean per-round payoff should be > 0.5 (above mutual defect of 1.0 for 200 rounds)
        if stats[condition]["mean_per_round"] < 0.5:
            issues.append(f"C{condition} ({cond_name}): very low mean payoff/round={stats[condition]['mean_per_round']:.3f}")

        # Zero variance check
        if n_reps >= 5 and std_payoff < 0.001:
            issues.append(f"C{condition} ({cond_name}): near-zero payoff variance (deterministic collapse?)")

    # Cross-condition checks
    if config_name == "clinical_alexithymia" and 4 in stats and 9 in stats:
        c4_mean = stats[4]["mean_total_payoff"]
        c9_mean = stats[9]["mean_total_payoff"]
        if c4_mean > 0:
            ratio = c9_mean / c4_mean
            if ratio > 1.15:
                issues.append(f"UNEXPECTED: alexithymia (C9) outperforms baseline (C4) by {(ratio-1)*100:.1f}% — blunted affect shouldn't help this much")
            stats["c9_vs_c4_ratio"] = ratio

    if config_name == "clinical_borderline" and 4 in stats and 10 in stats:
        c4_std = stats[4].get("std_total_payoff", 0)
        c10_std = stats[10].get("std_total_payoff", 0)
        if c10_std > 0 and c4_std > 0:
            stats["c10_vs_c4_variance_ratio"] = c10_std / c4_std

    if config_name == "clinical_depression" and 4 in stats and 11 in stats:
        c4_mean = stats[4]["mean_total_payoff"]
        c11_mean = stats[11]["mean_total_payoff"]
        if c4_mean > 0:
            stats["c11_vs_c4_ratio"] = c11_mean / c4_mean

    return {"config": config_name, "stats": stats, "issues": issues}


def print_report(analysis: dict):
    print(f"\n{'='*60}")
    print(f"Config: {analysis['config']}")
    print(f"{'='*60}")

    for cond in sorted(k for k in analysis["stats"] if isinstance(k, int)):
        s = analysis["stats"][cond]
        if True:
            print(f"  C{cond} ({s['name']}): {s['n_reps']} reps, "
                  f"mean_payoff={s['mean_total_payoff']:.1f} ± {s['std_total_payoff']:.1f}, "
                  f"per_round={s['mean_per_round']:.3f}")
            if "beta_mean" in s:
                print(f"    beta: mean={s['beta_mean']:.3f}, range=[{s['beta_min']:.3f}, {s['beta_max']:.3f}], std={s['beta_std']:.3f}")

    # Cross-condition comparisons
    for key in ("c9_vs_c4_ratio", "c10_vs_c4_variance_ratio", "c11_vs_c4_ratio"):
        if key in analysis["stats"]:
            print(f"  {key}: {analysis['stats'][key]:.3f}")

    if analysis["issues"]:
        print(f"\n  *** ISSUES ({len(analysis['issues'])}) ***")
        for issue in analysis["issues"]:
            print(f"    - {issue}")
    else:
        print(f"\n  No issues detected.")


def main():
    progress = check_progress()
    if progress is None:
        return

    print()
    any_data = False
    seen = set()
    for csv_path in sorted(OUTPUT_DIR.glob("*_partial.csv")) + sorted(OUTPUT_DIR.glob("clinical_*.csv")):
        config_name = csv_path.stem.replace("_partial", "")
        if config_name in seen:
            continue
        seen.add(config_name)
        analysis = analyze_partial(csv_path, config_name)
        print_report(analysis)
        any_data = True

    if not any_data:
        print("No result CSVs found yet. Experiment may still be in calibration phase.")


if __name__ == "__main__":
    main()

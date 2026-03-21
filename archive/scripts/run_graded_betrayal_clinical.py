"""Run graded betrayal clinical sensitivity: alex, borderline, depression + C2 baseline.

The graded game provides ambiguous EFE landscapes (q_pi_entropy ~5.8)
and betrayal amplifies precision dynamics differences. This combination
should maximize between-clinical differentiation.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from affect_aif.experiment.config import ExperimentConfig
from affect_aif.experiment.runner import ExperimentRunner

CLINICAL_CONFIGS = [
    ("alexithymia", "affect_aif/configs/graded_betrayal_clinical_alexithymia.json", 9),
    ("borderline", "affect_aif/configs/graded_betrayal_clinical_borderline.json", 10),
    ("depression", "affect_aif/configs/graded_betrayal_clinical_depression.json", 11),
]

OUTPUT_DIR = Path("results/graded_betrayal_clinical")
PROGRESS_FILE = OUTPUT_DIR / "progress.json"


def save_progress(progress: dict):
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2, default=str)


def run_baseline(replications: int, rounds: int) -> pd.DataFrame:
    """Run graded betrayal with C2 + C4 as normal-affect baseline."""
    print("=" * 60)
    print("Running graded betrayal C2 + C4 baseline")
    print("=" * 60)

    config = ExperimentConfig.from_json("affect_aif/configs/graded_betrayal_stress.json")
    config.num_replications = replications
    config.num_rounds = rounds
    config.conditions = [2, 4]
    config.run_sensitivity = False

    runner = ExperimentRunner(config)
    if runner.needs_mu_calibration():
        mu = runner.calibrate_mu(enforce_minimum=True)
        print(f"  Derived mu: {mu:.6f}")

    records: list[dict] = []
    for condition in config.conditions:
        for rep in range(replications):
            seed = config.random_seed + rep
            recs = runner.run_replication(
                condition=condition,
                replication=rep,
                seed=seed,
                config_path="affect_aif/configs/graded_betrayal_stress.json",
                config_name="graded_betrayal_baseline",
            )
            records.extend(recs)
            if (rep + 1) % 5 == 0 or rep == replications - 1:
                pd.DataFrame(records).to_csv(OUTPUT_DIR / "baseline_partial.csv", index=False)
                print(f"  C{condition} rep {rep+1}/{replications} — {len(records)} rows")

    df = pd.DataFrame(records)
    df.to_csv(OUTPUT_DIR / "baseline.csv", index=False)
    return df


def run_clinical(replications: int, rounds: int) -> dict[str, pd.DataFrame]:
    """Run all three clinical configs."""
    results = {}
    for name, config_path, cond in CLINICAL_CONFIGS:
        print(f"\n{'='*60}")
        print(f"Running graded betrayal clinical: {name} (C{cond})")
        print(f"{'='*60}")

        config = ExperimentConfig.from_json(config_path)
        config.num_replications = replications
        config.num_rounds = rounds
        config.run_sensitivity = False

        runner = ExperimentRunner(config)
        if runner.needs_mu_calibration():
            mu = runner.calibrate_mu(enforce_minimum=True)
            print(f"  Derived mu: {mu:.6f}")

        records: list[dict] = []
        for condition in config.conditions:
            for rep in range(replications):
                seed = config.random_seed + rep
                save_progress({"status": "running", "config": name, "condition": condition, "rep": rep})
                recs = runner.run_replication(
                    condition=condition,
                    replication=rep,
                    seed=seed,
                    config_path=config_path,
                    config_name=name,
                )
                records.extend(recs)
                if (rep + 1) % 5 == 0 or rep == replications - 1:
                    pd.DataFrame(records).to_csv(OUTPUT_DIR / f"{name}_partial.csv", index=False)
                    print(f"  C{condition} rep {rep+1}/{replications} — {len(records)} rows")

        df = pd.DataFrame(records)
        df.to_csv(OUTPUT_DIR / f"{name}.csv", index=False)
        results[name] = df

    return results


def analyze(baseline_df: pd.DataFrame, clinical_dfs: dict[str, pd.DataFrame]):
    """Compare clinical variants against normal C2, with window analysis."""
    print(f"\n{'='*60}")
    print("GRADED BETRAYAL CLINICAL SENSITIVITY ANALYSIS")
    print(f"{'='*60}")

    def seed_payoffs(df: pd.DataFrame, condition: int) -> pd.Series:
        cdf = df[df["condition"] == condition]
        return cdf.groupby("seed")["payoff"].sum()

    def window_payoffs(df: pd.DataFrame, condition: int, start: int, end: int) -> pd.Series:
        cdf = df[(df["condition"] == condition) & (df["round"] >= start) & (df["round"] < end)]
        return cdf.groupby("seed")["payoff"].sum()

    c2_normal = seed_payoffs(baseline_df, 2)
    c4_baseline = seed_payoffs(baseline_df, 4)

    print(f"\nOverall baselines:")
    print(f"  C4 (no affect):      {c4_baseline.mean():.2f} +/- {c4_baseline.std():.2f}")
    print(f"  C2 (normal affect):  {c2_normal.mean():.2f} +/- {c2_normal.std():.2f}")

    clinical_conditions = {
        "alexithymia": (9, "C9 alexithymia (alpha=0.1)"),
        "borderline": (10, "C10 borderline (alpha=12, lambda=0.5)"),
        "depression": (11, "C11 depression (beta0=0.2)"),
    }

    # Window analysis: pre-betrayal, betrayal, post-betrayal, recovery
    windows = [
        ("pre", 20, 30),
        ("betrayal", 30, 40),
        ("impact", 40, 50),
        ("recovery", 60, 70),
        ("late", 100, 110),
    ]

    overall_rows = []
    window_rows = []

    for name, (cond, label) in clinical_conditions.items():
        if name not in clinical_dfs:
            continue
        clin = seed_payoffs(clinical_dfs[name], cond)
        clin_c4 = seed_payoffs(clinical_dfs[name], 4)

        # vs C2 normal (paired by seed)
        common = sorted(set(c2_normal.index) & set(clin.index))
        if len(common) > 1:
            diff = clin.loc[common] - c2_normal.loc[common]
            diff_std = diff.std()
            if diff_std > 0:
                t, p = stats.ttest_rel(clin.loc[common], c2_normal.loc[common])
                d = float(diff.mean() / diff_std)
            else:
                t, p, d = 0.0, 1.0, 0.0
        else:
            t, p, d = 0.0, 1.0, 0.0

        # vs own C4
        common_c4 = sorted(set(clin.index) & set(clin_c4.index))
        if len(common_c4) > 1:
            diff_c4 = clin.loc[common_c4] - clin_c4.loc[common_c4]
            diff_c4_std = diff_c4.std()
            if diff_c4_std > 0:
                t_c4, p_c4 = stats.ttest_rel(clin.loc[common_c4], clin_c4.loc[common_c4])
                d_c4 = float(diff_c4.mean() / diff_c4_std)
            else:
                t_c4, p_c4, d_c4 = 0.0, 1.0, 0.0
        else:
            t_c4, p_c4, d_c4 = 0.0, 1.0, 0.0

        overall_rows.append({
            "variant": label,
            "mean_payoff": float(clin.mean()),
            "std": float(clin.std()),
            "vs_c2_diff": float(clin.mean() - c2_normal.mean()),
            "vs_c2_d": d,
            "vs_c2_p": float(p),
            "vs_c4_diff": float(clin.mean() - clin_c4.mean()),
            "vs_c4_d": d_c4,
            "vs_c4_p": float(p_c4),
        })

        print(f"\n  {label}:")
        print(f"    Total payoff: {clin.mean():.2f} +/- {clin.std():.2f}")
        print(f"    vs C2 normal: diff={clin.mean() - c2_normal.mean():+.2f}, d={d:.3f}, p={p:.4f}")
        print(f"    vs own C4:    diff={clin.mean() - clin_c4.mean():+.2f}, d={d_c4:.3f}, p={p_c4:.4f}")

        # Window analysis
        for wname, wstart, wend in windows:
            clin_w = window_payoffs(clinical_dfs[name], cond, wstart, wend)
            c2_w = window_payoffs(baseline_df, 2, wstart, wend)
            common_w = sorted(set(c2_w.index) & set(clin_w.index))
            if len(common_w) > 1:
                diff_w = clin_w.loc[common_w] - c2_w.loc[common_w]
                diff_w_std = diff_w.std()
                if diff_w_std > 0:
                    t_w, p_w = stats.ttest_rel(clin_w.loc[common_w], c2_w.loc[common_w])
                    d_w = float(diff_w.mean() / diff_w_std)
                else:
                    t_w, p_w, d_w = 0.0, 1.0, 0.0
            else:
                t_w, p_w, d_w = 0.0, 1.0, 0.0

            window_rows.append({
                "variant": label,
                "window": wname,
                "window_start": wstart,
                "window_end": wend,
                "clin_mean": float(clin_w.mean()) if len(clin_w) > 0 else np.nan,
                "c2_mean": float(c2_w.mean()) if len(c2_w) > 0 else np.nan,
                "diff": float(clin_w.mean() - c2_w.mean()) if len(common_w) > 0 else np.nan,
                "d": d_w,
                "p": float(p_w),
            })

    # Print window analysis
    print(f"\n  Window analysis (clinical vs C2 normal):")
    print(f"  {'Variant':<30} {'Window':<12} {'Clin':<8} {'C2':<8} {'Diff':<8} {'d':<8} {'p':<8}")
    for r in window_rows:
        print(f"  {r['variant']:<30} {r['window']:<12} {r['clin_mean']:<8.2f} {r['c2_mean']:<8.2f} {r['diff']:+<8.2f} {r['d']:<8.3f} {r['p']:<8.4f}")

    # Between-clinical differentiation
    clinical_means = {r["variant"]: r["mean_payoff"] for r in overall_rows}
    if len(clinical_means) >= 2:
        vals = list(clinical_means.values())
        spread = max(vals) - min(vals)
        print(f"\n  Between-clinical spread: {spread:.2f} points")

    # Save
    pd.DataFrame(overall_rows).to_csv(OUTPUT_DIR / "overall_analysis.csv", index=False)
    pd.DataFrame(window_rows).to_csv(OUTPUT_DIR / "window_analysis.csv", index=False)
    print(f"\nSaved analysis to {OUTPUT_DIR}")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--replications", type=int, default=50)
    parser.add_argument("--rounds", type=int, default=120)
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    save_progress({"status": "starting", "start_time": time.strftime("%Y-%m-%d %H:%M:%S")})

    baseline_df = run_baseline(args.replications, args.rounds)
    clinical_dfs = run_clinical(args.replications, args.rounds)
    analyze(baseline_df, clinical_dfs)

    save_progress({"status": "complete", "end_time": time.strftime("%Y-%m-%d %H:%M:%S")})


if __name__ == "__main__":
    main()

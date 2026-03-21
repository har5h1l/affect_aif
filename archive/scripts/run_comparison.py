"""Run default C2 baseline + cross-config comparison against clinical results."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from affect_aif.experiment.config import ExperimentConfig
from affect_aif.experiment.runner import ExperimentRunner

OUTPUT_DIR = Path("results/clinical_run")
CLINICAL_DIR = OUTPUT_DIR  # clinical CSVs already here
PROGRESS_FILE = OUTPUT_DIR / "comparison_progress.json"
REPLICATIONS = 20
ROUNDS = 200


def save_progress(progress: dict):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2, default=str)


def run_default_baseline():
    """Run default config with C2 + C4 to establish normal affective baseline."""
    print("=" * 60)
    print("Phase 1: Running default C2 + C4 baseline")
    print("=" * 60)

    config = ExperimentConfig.from_json("affect_aif/configs/default.json")
    config.num_replications = REPLICATIONS
    config.num_rounds = ROUNDS
    config.conditions = [2, 4]
    config.run_sensitivity = False

    runner = ExperimentRunner(config)

    progress = {
        "status": "running_baseline",
        "start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "phase": "default_baseline",
        "errors": [],
    }
    save_progress(progress)

    if runner.needs_mu_calibration():
        mu = runner.calibrate_mu(enforce_minimum=True)
        print(f"  Derived mu: {mu:.6f}")
        progress["mu"] = mu

    records: list[dict] = []
    for condition in config.conditions:
        for rep in range(REPLICATIONS):
            seed = config.random_seed + rep
            progress["current"] = {
                "condition": condition,
                "replication": rep,
                "total": REPLICATIONS,
            }
            save_progress(progress)

            try:
                recs = runner.run_replication(
                    condition=condition,
                    replication=rep,
                    seed=seed,
                    config_path="affect_aif/configs/default.json",
                    config_name="default",
                )
                records.extend(recs)

                if (rep + 1) % 5 == 0 or rep == REPLICATIONS - 1:
                    pd.DataFrame(records).to_csv(OUTPUT_DIR / "default_baseline_partial.csv", index=False)
                    print(f"  C{condition} rep {rep+1}/{REPLICATIONS} — {len(records)} rows saved")

            except Exception as e:
                error_msg = f"default C{condition} rep {rep}: {e}"
                print(f"  ERROR: {error_msg}")
                progress["errors"].append(error_msg)
                save_progress(progress)

    df = pd.DataFrame(records)
    df.to_csv(OUTPUT_DIR / "default_baseline.csv", index=False)
    print(f"  Saved {len(records)} rows to default_baseline.csv")
    return df


def run_comparison(baseline_df: pd.DataFrame):
    """Compare default C2 against all clinical conditions."""
    print("\n" + "=" * 60)
    print("Phase 2: Cross-config comparison")
    print("=" * 60)

    progress = {"status": "comparing", "phase": "comparison"}
    save_progress(progress)

    # Load clinical results
    clinical_dfs = {}
    for fname in ["clinical_alexithymia.csv", "clinical_borderline.csv", "clinical_depression.csv"]:
        path = CLINICAL_DIR / fname
        if path.exists():
            clinical_dfs[fname.replace(".csv", "")] = pd.read_csv(path)
        else:
            print(f"  WARNING: {path} not found, skipping")

    # Extract per-seed total payoffs
    def seed_payoffs(df: pd.DataFrame, condition: int) -> pd.Series:
        cdf = df[df["condition"] == condition]
        return cdf.groupby("seed")["payoff"].sum()

    # Default baselines
    c2_default = seed_payoffs(baseline_df, 2)
    c4_default = seed_payoffs(baseline_df, 4)

    results = []

    # C2 (default affect) vs C4 (no affect)
    results.append({
        "comparison": "C2_default vs C4",
        "condition": "C2 (default α=3.0, λ=0.6, β₀=0.5)",
        "mean_payoff": float(c2_default.mean()),
        "std_payoff": float(c2_default.std()),
        "baseline_mean": float(c4_default.mean()),
        "diff": float(c2_default.mean() - c4_default.mean()),
        "ratio": float(c2_default.mean() / c4_default.mean()) if c4_default.mean() > 0 else np.nan,
    })

    # Each clinical variant vs C2 default (the key comparison)
    clinical_conditions = {
        "clinical_alexithymia": (9, "C9 (alexithymia α=0.1)"),
        "clinical_borderline": (10, "C10 (borderline α=12, λ=0.5)"),
        "clinical_depression": (11, "C11 (depression β₀=0.2)"),
    }

    for config_name, (cond, label) in clinical_conditions.items():
        if config_name not in clinical_dfs:
            continue
        clin_payoffs = seed_payoffs(clinical_dfs[config_name], cond)

        # Paired comparison with C2 default (same seeds)
        common = sorted(set(c2_default.index) & set(clin_payoffs.index))
        if common:
            paired_diff = clin_payoffs.loc[common] - c2_default.loc[common]
            t_stat = float(paired_diff.mean() / paired_diff.std() * np.sqrt(len(common))) if paired_diff.std() > 0 else 0.0
        else:
            paired_diff = pd.Series([0.0])
            t_stat = 0.0

        results.append({
            "comparison": f"{label} vs C2_default",
            "condition": label,
            "mean_payoff": float(clin_payoffs.mean()),
            "std_payoff": float(clin_payoffs.std()),
            "baseline_mean": float(c2_default.mean()),
            "diff": float(clin_payoffs.mean() - c2_default.mean()),
            "ratio": float(clin_payoffs.mean() / c2_default.mean()) if c2_default.mean() > 0 else np.nan,
            "paired_diff_mean": float(paired_diff.mean()),
            "paired_diff_std": float(paired_diff.std()),
            "t_stat": t_stat,
            "n_paired": len(common),
        })

        # Also vs its own C4
        clin_c4 = seed_payoffs(clinical_dfs[config_name], 4)
        results.append({
            "comparison": f"{label} vs own C4",
            "condition": label,
            "mean_payoff": float(clin_payoffs.mean()),
            "std_payoff": float(clin_payoffs.std()),
            "baseline_mean": float(clin_c4.mean()),
            "diff": float(clin_payoffs.mean() - clin_c4.mean()),
            "ratio": float(clin_payoffs.mean() / clin_c4.mean()) if clin_c4.mean() > 0 else np.nan,
        })

    comparison_df = pd.DataFrame(results)
    comparison_df.to_csv(OUTPUT_DIR / "comparison_results.csv", index=False)

    # Print report
    print("\n" + "=" * 60)
    print("COMPARISON RESULTS")
    print("=" * 60)
    print(f"\nDefault baselines (20 reps × 200 rounds):")
    print(f"  C4 (no affect):      {c4_default.mean():.1f} ± {c4_default.std():.1f}")
    print(f"  C2 (default affect): {c2_default.mean():.1f} ± {c2_default.std():.1f}")
    print(f"  C2/C4 ratio:         {c2_default.mean()/c4_default.mean():.3f}")

    print(f"\nClinical variants vs C2 default (the deficit story):")
    for r in results:
        if "vs C2_default" in r["comparison"]:
            print(f"\n  {r['condition']}:")
            print(f"    Payoff: {r['mean_payoff']:.1f} ± {r['std_payoff']:.1f}")
            print(f"    vs C2:  {r['diff']:+.1f} ({r['ratio']:.3f}x)")
            if "t_stat" in r:
                print(f"    Paired: {r['paired_diff_mean']:+.1f} ± {r['paired_diff_std']:.1f} (t={r['t_stat']:.2f}, n={r['n_paired']})")

    # Write summary
    summary_path = OUTPUT_DIR / "comparison_summary.md"
    with open(summary_path, "w") as f:
        f.write("# Clinical Sensitivity Analysis: Comparison Results\n\n")
        f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Replications: {REPLICATIONS}, Rounds: {ROUNDS}\n\n")
        f.write("## Baselines\n\n")
        f.write(f"| Condition | Mean Payoff | Std |\n")
        f.write(f"|-----------|------------|-----|\n")
        f.write(f"| C4 (no affect) | {c4_default.mean():.1f} | {c4_default.std():.1f} |\n")
        f.write(f"| C2 (default affect, α=3.0, λ=0.6, β₀=0.5) | {c2_default.mean():.1f} | {c2_default.std():.1f} |\n\n")
        f.write("## Clinical Variants vs Default C2\n\n")
        f.write("| Variant | Payoff | vs C2 Diff | Ratio | t-stat | Interpretation |\n")
        f.write("|---------|--------|-----------|-------|--------|----------------|\n")
        for r in results:
            if "vs C2_default" in r["comparison"]:
                t = r.get("t_stat", 0)
                sig = "***" if abs(t) > 3.29 else "**" if abs(t) > 2.54 else "*" if abs(t) > 1.73 else "ns"
                interp = "deficit" if r["diff"] < 0 else "no deficit" if abs(r["diff"]) < 10 else "better?"
                f.write(f"| {r['condition']} | {r['mean_payoff']:.1f}±{r['std_payoff']:.1f} | {r['diff']:+.1f} | {r['ratio']:.3f} | {t:.2f} {sig} | {interp} |\n")
        f.write("\n## Interpretation\n\n")
        f.write("Clinical variants are compared against the **default C2** (normal affective agent) to assess\n")
        f.write("whether parameter perturbations consistent with clinical phenotypes produce measurable deficits.\n")
        f.write("Significance levels: * p<0.05, ** p<0.01, *** p<0.001 (one-tailed paired t-test)\n")

    print(f"\nSaved comparison_results.csv and comparison_summary.md to {OUTPUT_DIR}")

    progress["status"] = "complete"
    progress["end_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
    save_progress(progress)


def main():
    baseline_df = run_default_baseline()
    run_comparison(baseline_df)


if __name__ == "__main__":
    main()

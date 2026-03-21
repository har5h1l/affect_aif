"""Test affect_modulates_precision=True to see if clinical parameters differentiate.

Hypothesis: When beta modulates policy precision (not just terminal values),
clinical parameter perturbations should produce measurable deficits because:
- Alexithymia (frozen beta=0.5): constant 1.5x → stable but can't adapt precision per partner
- Borderline (volatile beta): swings 1.14x-1.94x → over/under-confident decisions
- Depression (low start beta=0.2): starts at 1.2x → indecisive early → misses cooperators
- Default C2 (beta=0.5→0.53): moderate 1.5x → well-calibrated
"""

from __future__ import annotations

import copy
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from affect_aif.experiment.config import ExperimentConfig
from affect_aif.experiment.runner import ExperimentRunner

OUTPUT_DIR = Path("results/precision_modulation_run")
PROGRESS_FILE = OUTPUT_DIR / "progress.json"
REPLICATIONS = 20
ROUNDS = 200


def save_progress(progress: dict):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2, default=str)


def run_config(config_path: str, config_name: str, conditions: list[int], progress: dict) -> pd.DataFrame:
    """Run a config with affect_modulates_precision=True."""
    print(f"\n{'='*60}")
    print(f"Running: {config_name} (affect_modulates_precision=True)")
    print(f"{'='*60}")

    config = ExperimentConfig.from_json(config_path)
    config.num_replications = REPLICATIONS
    config.num_rounds = ROUNDS
    config.conditions = conditions
    config.run_sensitivity = False
    config.affect_modulates_precision = True  # THE KEY CHANGE

    runner = ExperimentRunner(config)

    progress["current"] = {"config": config_name, "phase": "calibration"}
    save_progress(progress)

    if runner.needs_mu_calibration():
        mu = runner.calibrate_mu(enforce_minimum=True)
        print(f"  Derived mu: {mu:.6f}")

    records: list[dict] = []
    for condition in conditions:
        for rep in range(REPLICATIONS):
            seed = config.random_seed + rep
            progress["current"] = {
                "config": config_name,
                "condition": condition,
                "replication": rep,
                "total": REPLICATIONS,
            }
            save_progress(progress)

            try:
                recs = runner.run_replication(
                    condition=condition, replication=rep, seed=seed,
                    config_path=config_path, config_name=config_name,
                )
                records.extend(recs)

                if (rep + 1) % 5 == 0 or rep == REPLICATIONS - 1:
                    pd.DataFrame(records).to_csv(OUTPUT_DIR / f"{config_name}_partial.csv", index=False)
                    print(f"  C{condition} rep {rep+1}/{REPLICATIONS} — {len(records)} rows")

            except Exception as e:
                msg = f"{config_name} C{condition} rep {rep}: {e}"
                print(f"  ERROR: {msg}")
                progress["errors"].append(msg)
                save_progress(progress)

    df = pd.DataFrame(records)
    df.to_csv(OUTPUT_DIR / f"{config_name}.csv", index=False)
    return df


def compare_all(dfs: dict[str, pd.DataFrame]):
    """Compare all conditions with precision modulation enabled."""
    import ast

    print(f"\n{'='*60}")
    print("PRECISION MODULATION COMPARISON")
    print(f"{'='*60}")

    def seed_payoffs(df, cond):
        return df[df["condition"] == cond].groupby("seed")["payoff"].sum()

    def beta_stats(df, cond):
        cdf = df[df["condition"] == cond]
        if "betas" not in cdf.columns:
            return None
        all_b = np.array(cdf["betas"].apply(ast.literal_eval).tolist())
        return {
            "mean": float(all_b.mean()),
            "std": float(all_b.std()),
            "min": float(all_b.min()),
            "max": float(all_b.max()),
        }

    # Get C2 default as reference
    c2_payoffs = seed_payoffs(dfs["default_precision"], 2)
    c4_payoffs = seed_payoffs(dfs["default_precision"], 4)

    print(f"\nBaselines (affect_modulates_precision=True):")
    print(f"  C4 (no affect):      {c4_payoffs.mean():.1f} ± {c4_payoffs.std():.1f}")
    print(f"  C2 (default affect): {c2_payoffs.mean():.1f} ± {c2_payoffs.std():.1f}")
    print(f"  C2/C4 ratio:         {c2_payoffs.mean()/c4_payoffs.mean():.3f}")

    c2_beta = beta_stats(dfs["default_precision"], 2)
    if c2_beta:
        print(f"  C2 beta: mean={c2_beta['mean']:.3f}, range=[{c2_beta['min']:.3f}, {c2_beta['max']:.3f}]")

    results = []
    clinical_map = {
        "alexithymia_precision": (9, "C9 alexithymia (α=0.1)"),
        "borderline_precision": (10, "C10 borderline (α=12, λ=0.5)"),
        "depression_precision": (11, "C11 depression (β₀=0.2)"),
    }

    print(f"\nClinical variants vs C2 default (precision modulation ON):")
    for config_name, (cond, label) in clinical_map.items():
        if config_name not in dfs:
            continue
        clin = seed_payoffs(dfs[config_name], cond)
        common = sorted(set(c2_payoffs.index) & set(clin.index))
        paired = clin.loc[common] - c2_payoffs.loc[common]
        t = float(paired.mean() / paired.std() * np.sqrt(len(common))) if paired.std() > 0 else 0

        bs = beta_stats(dfs[config_name], cond)
        beta_str = f"beta=[{bs['min']:.3f},{bs['max']:.3f}]" if bs else ""

        print(f"\n  {label}:")
        print(f"    Payoff: {clin.mean():.1f} ± {clin.std():.1f}")
        print(f"    vs C2:  {paired.mean():+.1f} (t={t:.2f}, n={len(common)}) {beta_str}")

        sig = "***" if abs(t) > 3.29 else "**" if abs(t) > 2.54 else "*" if abs(t) > 1.73 else "ns"
        results.append({
            "condition": label, "payoff": f"{clin.mean():.1f}±{clin.std():.1f}",
            "diff_vs_c2": f"{paired.mean():+.1f}", "t_stat": f"{t:.2f}", "sig": sig,
            "beta_range": f"[{bs['min']:.3f},{bs['max']:.3f}]" if bs else "",
        })

    # Also compare with precision OFF results
    print(f"\n{'='*60}")
    print("COMPARISON: Precision ON vs OFF")
    print(f"{'='*60}")

    off_dir = Path("results/clinical_run")
    if (off_dir / "default_baseline.csv").exists():
        off_default = pd.read_csv(off_dir / "default_baseline.csv")
        c2_off = seed_payoffs(off_default, 2)
        c4_off = seed_payoffs(off_default, 4)
        print(f"\n  Precision OFF: C2={c2_off.mean():.1f}, C4={c4_off.mean():.1f}, ratio={c2_off.mean()/c4_off.mean():.3f}")
        print(f"  Precision ON:  C2={c2_payoffs.mean():.1f}, C4={c4_payoffs.mean():.1f}, ratio={c2_payoffs.mean()/c4_payoffs.mean():.3f}")
        print(f"  Precision modulation effect on C2: {c2_payoffs.mean() - c2_off.mean():+.1f}")

    # Save summary
    summary_df = pd.DataFrame(results)
    summary_df.to_csv(OUTPUT_DIR / "comparison_results.csv", index=False)

    with open(OUTPUT_DIR / "summary.md", "w") as f:
        f.write("# Precision Modulation Experiment Results\n\n")
        f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"affect_modulates_precision = **True**\n\n")
        f.write("## Key Question\n")
        f.write("Does enabling precision modulation (beta scales gamma) make clinical\n")
        f.write("parameter perturbations produce measurable deficits vs default C2?\n\n")
        f.write("## Results\n\n")
        f.write(f"| Condition | Payoff | vs C2 | t | sig | beta range |\n")
        f.write(f"|-----------|--------|-------|---|-----|------------|\n")
        f.write(f"| C2 default | {c2_payoffs.mean():.1f}±{c2_payoffs.std():.1f} | — | — | — | [{c2_beta['min']:.3f},{c2_beta['max']:.3f}] |\n")
        for r in results:
            f.write(f"| {r['condition']} | {r['payoff']} | {r['diff_vs_c2']} | {r['t_stat']} | {r['sig']} | {r['beta_range']} |\n")
        f.write(f"\nC4 baseline: {c4_payoffs.mean():.1f}±{c4_payoffs.std():.1f}\n")

    print(f"\nSaved results to {OUTPUT_DIR}")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    progress = {
        "status": "running",
        "start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "completed": [],
        "errors": [],
    }
    save_progress(progress)

    dfs = {}

    # Default config with C2 + C4
    dfs["default_precision"] = run_config(
        "affect_aif/configs/default.json", "default_precision", [2, 4], progress
    )
    progress["completed"].append("default_precision")

    # Clinical configs
    for config_path, name, conditions in [
        ("affect_aif/configs/clinical_alexithymia.json", "alexithymia_precision", [4, 9]),
        ("affect_aif/configs/clinical_borderline.json", "borderline_precision", [4, 10]),
        ("affect_aif/configs/clinical_depression.json", "depression_precision", [4, 11]),
    ]:
        dfs[name] = run_config(config_path, name, conditions, progress)
        progress["completed"].append(name)

    compare_all(dfs)

    progress["status"] = "complete"
    progress["end_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
    save_progress(progress)


if __name__ == "__main__":
    main()

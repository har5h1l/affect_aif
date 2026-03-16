"""Test clinical sensitivity with extreme parameter perturbations (200 rounds).

Extreme params:
- Alexithymia: alpha_charge=0.001 (virtually zero charge)
- Borderline: alpha_charge=20.0, lambda_smooth=0.3 (maximally volatile)
- Depression: initial_beta=0.01 (near-zero starting precision)

Tests both precision ON and OFF at 200 rounds.
"""

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

OUTPUT_DIR = Path("results/extreme_params_run")
PROGRESS_FILE = OUTPUT_DIR / "progress.json"
REPLICATIONS = 20
ROUNDS = 200


def save_progress(progress: dict):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2, default=str)


def run_with_overrides(config_path: str, config_name: str, conditions: list[int],
                       precision_on: bool, overrides: dict, progress: dict) -> pd.DataFrame:
    tag = "prec_ON" if precision_on else "prec_OFF"
    full_name = f"{config_name}_{tag}"
    print(f"\n  Running {full_name}")

    config = ExperimentConfig.from_json(config_path)
    config.num_replications = REPLICATIONS
    config.num_rounds = ROUNDS
    config.conditions = conditions
    config.run_sensitivity = False
    config.affect_modulates_precision = precision_on

    # Apply extreme overrides
    for key, value in overrides.items():
        setattr(config, key, value)
    if overrides:
        print(f"    Overrides: {overrides}")

    runner = ExperimentRunner(config)

    if runner.needs_mu_calibration():
        mu = runner.calibrate_mu(enforce_minimum=True)
        print(f"    Derived mu: {mu:.6f}")

    records: list[dict] = []
    for condition in conditions:
        for rep in range(REPLICATIONS):
            seed = config.random_seed + rep
            progress["current"] = {
                "config": full_name, "condition": condition,
                "replication": rep, "total": REPLICATIONS,
            }
            save_progress(progress)
            try:
                recs = runner.run_replication(
                    condition=condition, replication=rep, seed=seed,
                    config_path=config_path, config_name=full_name,
                )
                records.extend(recs)
            except Exception as e:
                msg = f"{full_name} C{condition} rep {rep}: {e}"
                print(f"    ERROR: {msg}")
                progress["errors"].append(msg)
                save_progress(progress)

    df = pd.DataFrame(records)
    df.to_csv(OUTPUT_DIR / f"{full_name}.csv", index=False)
    print(f"    Saved {len(records)} rows")
    return df


def analyze(dfs: dict[str, pd.DataFrame]):
    def seed_payoffs(df, cond):
        return df[df["condition"] == cond].groupby("seed")["payoff"].sum()

    print(f"\n{'='*65}")
    print(f"EXTREME PARAMS RESULTS ({ROUNDS} rounds, {REPLICATIONS} reps)")
    print(f"{'='*65}")

    for precision_label, tag in [("Precision OFF", "prec_OFF"), ("Precision ON", "prec_ON")]:
        print(f"\n--- {precision_label} ---")

        c2_key = f"default_{tag}"
        if c2_key not in dfs:
            continue
        c2 = seed_payoffs(dfs[c2_key], 2)
        c4 = seed_payoffs(dfs[c2_key], 4)

        print(f"  C4 (no affect):      {c4.mean():.1f} ± {c4.std():.1f}")
        print(f"  C2 (default affect): {c2.mean():.1f} ± {c2.std():.1f}")
        print(f"  C2/C4 ratio:         {c2.mean()/c4.mean():.3f}")

        for label, config_key, cond in [
            ("C9 extreme alexithymia (α=0.001)", f"extreme_alex_{tag}", 9),
            ("C10 extreme borderline (α=20,λ=0.3)", f"extreme_border_{tag}", 10),
            ("C11 extreme depression (β₀=0.01)", f"extreme_depress_{tag}", 11),
        ]:
            if config_key not in dfs:
                continue
            clin = seed_payoffs(dfs[config_key], cond)
            common = sorted(set(c2.index) & set(clin.index))
            if not common:
                print(f"  {label}: no common seeds for pairing")
                continue
            paired = clin.loc[common] - c2.loc[common]
            t = float(paired.mean() / paired.std() * np.sqrt(len(common))) if paired.std() > 0 else 0
            sig = "***" if abs(t) > 3.29 else "**" if abs(t) > 2.54 else "*" if abs(t) > 1.73 else "ns"
            print(f"  {label}:")
            print(f"    Payoff: {clin.mean():.1f} ± {clin.std():.1f}  vs C2: {paired.mean():+.1f} (t={t:.2f} {sig})")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    progress = {
        "status": "running", "start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "experiment": "extreme_params",
        "completed": [], "errors": [],
    }
    save_progress(progress)

    dfs = {}

    # Default C2+C4 baseline (same for both precision modes)
    for precision_on in [False, True]:
        tag = "prec_ON" if precision_on else "prec_OFF"
        dfs[f"default_{tag}"] = run_with_overrides(
            "affect_aif/configs/default.json", "default", [2, 4],
            precision_on=precision_on, overrides={}, progress=progress,
        )
        progress["completed"].append(f"default_{tag}")
        save_progress(progress)

    # Extreme clinical variants
    extreme_configs = [
        ("affect_aif/configs/clinical_alexithymia.json", "extreme_alex", [4, 9],
         {"alpha_charge": 0.001}),
        ("affect_aif/configs/clinical_borderline.json", "extreme_border", [4, 10],
         {"alpha_charge": 20.0, "lambda_smooth": 0.3}),
        ("affect_aif/configs/clinical_depression.json", "extreme_depress", [4, 11],
         {"initial_beta": 0.01}),
    ]

    for config_path, name, conditions, overrides in extreme_configs:
        for precision_on in [False, True]:
            tag = "prec_ON" if precision_on else "prec_OFF"
            dfs[f"{name}_{tag}"] = run_with_overrides(
                config_path, name, conditions,
                precision_on=precision_on, overrides=overrides, progress=progress,
            )
            progress["completed"].append(f"{name}_{tag}")
            save_progress(progress)

    analyze(dfs)

    progress["status"] = "complete"
    progress["end_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
    save_progress(progress)
    print("\nDone.")


if __name__ == "__main__":
    main()

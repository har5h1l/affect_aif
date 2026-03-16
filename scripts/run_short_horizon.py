"""Test clinical sensitivity with short horizon (50 rounds) where recovery can't wash out deficits.

Hypothesis: Depression (β₀=0.2) should show deficit because beta can't recover in 50 rounds.
Alexithymia should still be flat. Borderline might be worse (volatile decisions compound in short games).
Tests both precision ON and OFF.
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

OUTPUT_DIR = Path("results/short_horizon_run")
PROGRESS_FILE = OUTPUT_DIR / "progress.json"
REPLICATIONS = 20
ROUNDS = 50  # KEY CHANGE: short horizon


def save_progress(progress: dict):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2, default=str)


def run_config(config_path: str, config_name: str, conditions: list[int],
               precision_on: bool, progress: dict) -> pd.DataFrame:
    tag = "prec_ON" if precision_on else "prec_OFF"
    full_name = f"{config_name}_{tag}"
    print(f"\n  Running {full_name} (conditions {conditions})")

    config = ExperimentConfig.from_json(config_path)
    config.num_replications = REPLICATIONS
    config.num_rounds = ROUNDS
    config.conditions = conditions
    config.run_sensitivity = False
    config.affect_modulates_precision = precision_on

    runner = ExperimentRunner(config)

    if runner.needs_mu_calibration():
        # Calibrate with ROUNDS rounds, not 200
        mu = runner.calibrate_mu(enforce_minimum=True)
        progress["current"] = {"config": full_name, "mu": mu}
        save_progress(progress)

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
                progress["errors"].append(f"{full_name} C{condition} rep {rep}: {e}")
                save_progress(progress)

    df = pd.DataFrame(records)
    df.to_csv(OUTPUT_DIR / f"{full_name}.csv", index=False)
    print(f"    Saved {len(records)} rows")
    return df


def analyze(dfs: dict[str, pd.DataFrame]):
    def seed_payoffs(df, cond):
        return df[df["condition"] == cond].groupby("seed")["payoff"].sum()

    print(f"\n{'='*65}")
    print(f"SHORT HORIZON RESULTS ({ROUNDS} rounds, {REPLICATIONS} reps)")
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
            ("C9 alexithymia", f"alexithymia_{tag}", 9),
            ("C10 borderline", f"borderline_{tag}", 10),
            ("C11 depression", f"depression_{tag}", 11),
        ]:
            if config_key not in dfs:
                continue
            clin = seed_payoffs(dfs[config_key], cond)
            common = sorted(set(c2.index) & set(clin.index))
            paired = clin.loc[common] - c2.loc[common]
            t = float(paired.mean() / paired.std() * np.sqrt(len(common))) if paired.std() > 0 else 0
            sig = "***" if abs(t) > 3.29 else "**" if abs(t) > 2.54 else "*" if abs(t) > 1.73 else "ns"
            print(f"  {label}: {clin.mean():.1f} ± {clin.std():.1f}  vs C2: {paired.mean():+.1f} (t={t:.2f} {sig})")

    # Save summary
    with open(OUTPUT_DIR / "summary.txt", "w") as f:
        f.write(f"Short horizon ({ROUNDS} rounds) clinical sensitivity results\n")
        f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("See experiment log for full details.\n")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    progress = {
        "status": "running", "start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "experiment": "short_horizon", "rounds": ROUNDS,
        "completed": [], "errors": [],
    }
    save_progress(progress)

    configs = [
        ("affect_aif/configs/default.json", "default", [2, 4]),
        ("affect_aif/configs/clinical_alexithymia.json", "alexithymia", [4, 9]),
        ("affect_aif/configs/clinical_borderline.json", "borderline", [4, 10]),
        ("affect_aif/configs/clinical_depression.json", "depression", [4, 11]),
    ]

    dfs = {}
    for config_path, name, conditions in configs:
        for precision_on in [False, True]:
            tag = "prec_ON" if precision_on else "prec_OFF"
            full_name = f"{name}_{tag}"
            dfs[full_name] = run_config(config_path, name, conditions, precision_on, progress)
            progress["completed"].append(full_name)
            save_progress(progress)

    analyze(dfs)

    progress["status"] = "complete"
    progress["end_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
    save_progress(progress)
    print("\nDone.")


if __name__ == "__main__":
    main()

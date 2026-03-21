"""Run clinical configs incrementally, saving after each replication for live monitoring."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from affect_aif.experiment.config import ExperimentConfig
from affect_aif.experiment.runner import ExperimentRunner

CONFIGS = [
    "affect_aif/configs/clinical_alexithymia.json",
    "affect_aif/configs/clinical_borderline.json",
    "affect_aif/configs/clinical_depression.json",
]

REPLICATIONS = 20
ROUNDS = 200
OUTPUT_DIR = Path("results/clinical_run")
PROGRESS_FILE = OUTPUT_DIR / "progress.json"


def save_progress(progress: dict):
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2, default=str)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    all_records: list[dict] = []
    progress = {
        "status": "starting",
        "start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "configs": CONFIGS,
        "replications": REPLICATIONS,
        "rounds": ROUNDS,
        "completed": [],
        "current": None,
        "errors": [],
    }
    save_progress(progress)

    for config_path in CONFIGS:
        config_name = Path(config_path).stem
        print(f"\n{'='*60}")
        print(f"Starting config: {config_name}")
        print(f"{'='*60}")

        config = ExperimentConfig.from_json(config_path)
        config.num_replications = REPLICATIONS
        config.num_rounds = ROUNDS
        config.run_sensitivity = False

        runner = ExperimentRunner(config)

        # Calibrate mu
        progress["current"] = {"config": config_name, "phase": "calibration"}
        save_progress(progress)

        if runner.needs_mu_calibration():
            mu = runner.calibrate_mu(enforce_minimum=True)
            print(f"  Derived mu: {mu:.6f}")
            progress["current"]["mu"] = mu

        # Run replications incrementally
        config_records: list[dict] = []
        for condition in config.conditions:
            for rep in range(REPLICATIONS):
                seed = config.random_seed + rep
                progress["current"] = {
                    "config": config_name,
                    "phase": "running",
                    "condition": condition,
                    "replication": rep,
                    "total_replications": REPLICATIONS,
                }
                save_progress(progress)

                try:
                    records = runner.run_replication(
                        condition=condition,
                        replication=rep,
                        seed=seed,
                        config_path=config_path,
                        config_name=config_name,
                    )
                    config_records.extend(records)

                    # Save incremental CSV after every 5 replications
                    if (rep + 1) % 5 == 0 or rep == REPLICATIONS - 1:
                        partial_df = pd.DataFrame(config_records)
                        partial_df.to_csv(OUTPUT_DIR / f"{config_name}_partial.csv", index=False)
                        print(f"  C{condition} rep {rep+1}/{REPLICATIONS} done — saved partial ({len(config_records)} rows)")

                except Exception as e:
                    error_msg = f"{config_name} C{condition} rep {rep}: {e}"
                    print(f"  ERROR: {error_msg}")
                    progress["errors"].append(error_msg)
                    save_progress(progress)

        # Save final config results
        if config_records:
            final_df = pd.DataFrame(config_records)
            final_df.to_csv(OUTPUT_DIR / f"{config_name}.csv", index=False)
            all_records.extend(config_records)
            print(f"  Saved {len(config_records)} rows to {config_name}.csv")

        progress["completed"].append(config_name)
        save_progress(progress)

    # Save combined results
    if all_records:
        combined = pd.DataFrame(all_records)
        combined.to_csv(OUTPUT_DIR / "all_clinical.csv", index=False)

    progress["status"] = "complete"
    progress["end_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
    save_progress(progress)
    print(f"\nAll done. {len(all_records)} total rows saved.")


if __name__ == "__main__":
    main()

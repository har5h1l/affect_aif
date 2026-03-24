"""Phase 5: Clinical sensitivity analysis across game environments.

Runs clinical phenotypes (alexithymia, borderline, depression) alongside
healthy affect (C2) and no-affect baseline (C4) in games where precision
tracking matters (Stag Hunt, optionally graded trust game).

Each phenotype requires its own config-level parameter overrides, so we
run them sequentially and merge results for cross-condition analysis.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from affect_aif.experiment.config import ExperimentConfig
from affect_aif.experiment.runner import ExperimentRunner

# Stag Hunt payoffs
SH_PAYOFFS = {
    "mutual_coop": (5.0, 5.0),
    "sucker": (0.0, 2.0),
    "temptation": (2.0, 0.0),
    "mutual_defect": (2.0, 2.0),
}

# Clinical phenotype parameter overrides (relative to healthy defaults)
CLINICAL_PHENOTYPES = {
    "healthy": {
        "conditions": [2, 4],
        "alpha_charge": 3.0,
        "lambda_smooth": 0.6,
        "initial_beta": 0.5,
    },
    "alexithymia": {
        "conditions": [9],
        "alpha_charge": 0.1,
        "lambda_smooth": 0.6,
        "initial_beta": 0.5,
    },
    "borderline": {
        "conditions": [10],
        "alpha_charge": 12.0,
        "lambda_smooth": 0.5,
        "initial_beta": 0.5,
    },
    "depression": {
        "conditions": [11],
        "alpha_charge": 3.0,
        "lambda_smooth": 0.6,
        "initial_beta": 0.2,
    },
}

# Scenario templates
SCENARIOS = {
    "sh_default": {
        "num_rounds": 200,
        "p_switch": 0.05,
        "assignment_mode": "random",
        "observation_noise": 0.0,
        "calibration_episodes": 20,
    },
    "sh_betrayal": {
        "num_rounds": 120,
        "p_switch": 0.0,
        "assignment_mode": "agent_choice",
        "observation_noise": 0.1,
        "initial_partner_types": ["cooperator", "reciprocator", "cooperator", "random"],
        "scheduled_type_switches": [{"round": 31, "partner_idx": 0, "to_type": "exploiter"}],
        "calibration_episodes": 10,
    },
}


def build_config(
    scenario_name: str,
    phenotype_name: str,
    num_replications: int,
    random_seed: int,
) -> ExperimentConfig:
    """Build an ExperimentConfig for a specific scenario + phenotype."""
    scenario = SCENARIOS[scenario_name]
    phenotype = CLINICAL_PHENOTYPES[phenotype_name]

    params = {
        "experiment_name": f"{scenario_name}_{phenotype_name}",
        "num_partners": 4,
        "num_rounds": scenario["num_rounds"],
        "p_switch": scenario["p_switch"],
        "assignment_mode": scenario["assignment_mode"],
        "observation_noise": scenario.get("observation_noise", 0.0),
        "correlation_pairs": [],
        "correlation_strength": 0.9,
        **SH_PAYOFFS,
        "gamma": 1.0,
        "lr": 0.1,
        "action_sampling": "marginal",
        "affect_modulates_precision": False,
        "use_parameter_learning": False,
        "deep_horizon": 8,
        "shallow_horizon": 2,
        "max_policies": 4096,
        "sigma_0_sq": 0.25,
        "mu": None,
        "lesion_mode": "decouple",
        "num_replications": num_replications,
        "random_seed": random_seed,
        "conditions": phenotype["conditions"],
        "partner_types": ["cooperator", "reciprocator", "exploiter", "random"],
        "run_sensitivity": False,
        # Phenotype-specific parameters
        "alpha_charge": phenotype["alpha_charge"],
        "lambda_smooth": phenotype["lambda_smooth"],
        "initial_beta": phenotype["initial_beta"],
    }

    if "initial_partner_types" in scenario:
        params["initial_partner_types"] = scenario["initial_partner_types"]
    if "scheduled_type_switches" in scenario:
        params["scheduled_type_switches"] = scenario["scheduled_type_switches"]
    if "calibration_episodes" in scenario:
        params["calibration_episodes"] = scenario["calibration_episodes"]

    return ExperimentConfig.from_dict(params)


def run_phenotype(
    scenario_name: str,
    phenotype_name: str,
    num_replications: int,
    random_seed: int,
    output_dir: Path,
) -> pd.DataFrame:
    """Run a single phenotype and save incremental results."""
    config = build_config(scenario_name, phenotype_name, num_replications, random_seed)
    runner = ExperimentRunner(config)

    if runner.needs_mu_calibration():
        mu = runner.calibrate_mu(enforce_minimum=True)
        print(f"  {phenotype_name}: derived mu = {mu:.6f}")

    all_records: list[dict] = []
    for condition in config.conditions:
        for rep in range(num_replications):
            seed = random_seed + rep
            records = runner.run_replication(
                condition=condition,
                replication=rep,
                seed=seed,
                config_name=f"{scenario_name}_{phenotype_name}",
            )
            all_records.extend(records)

            # Checkpoint after each replication
            partial_path = output_dir / f"{scenario_name}_{phenotype_name}_partial.csv"
            pd.DataFrame(all_records).to_csv(partial_path, index=False)

    # Add phenotype label
    for row in all_records:
        row["phenotype"] = phenotype_name
        row["scenario"] = scenario_name

    df = pd.DataFrame(all_records)
    final_path = output_dir / f"{scenario_name}_{phenotype_name}.csv"
    df.to_csv(final_path, index=False)
    print(f"  {phenotype_name}: {len(df)} rows -> {final_path}")
    return df


def analyze_results(combined: pd.DataFrame, output_dir: Path):
    """Compute clinical sensitivity statistics."""
    from scipy import stats

    results = []

    for scenario in combined["scenario"].unique():
        scenario_df = combined[scenario == combined["scenario"]]

        # Get per-episode payoffs
        episode_payoffs = (
            scenario_df.groupby(["phenotype", "condition", "seed"])["payoff"]
            .sum()
            .reset_index()
        )

        # Get healthy C2 as reference
        healthy_c2 = episode_payoffs[
            (episode_payoffs["phenotype"] == "healthy") & (episode_payoffs["condition"] == 2)
        ]["payoff"].values

        # Get no-affect C4 as floor
        noaffect_c4 = episode_payoffs[
            (episode_payoffs["phenotype"] == "healthy") & (episode_payoffs["condition"] == 4)
        ]["payoff"].values

        for phenotype in ["alexithymia", "borderline", "depression"]:
            condition_map = {"alexithymia": 9, "borderline": 10, "depression": 11}
            cond = condition_map[phenotype]
            clinical_payoffs = episode_payoffs[
                (episode_payoffs["phenotype"] == phenotype) & (episode_payoffs["condition"] == cond)
            ]["payoff"].values

            if len(clinical_payoffs) == 0 or len(healthy_c2) == 0:
                continue

            # Clinical vs healthy
            t_ch, p_ch = stats.ttest_ind(clinical_payoffs, healthy_c2)
            d_ch = (healthy_c2.mean() - clinical_payoffs.mean()) / np.sqrt(
                (healthy_c2.std() ** 2 + clinical_payoffs.std() ** 2) / 2
            )

            # Clinical vs no-affect
            t_cn, p_cn = stats.ttest_ind(clinical_payoffs, noaffect_c4)
            d_cn = (clinical_payoffs.mean() - noaffect_c4.mean()) / np.sqrt(
                (clinical_payoffs.std() ** 2 + noaffect_c4.std() ** 2) / 2
            )

            results.append({
                "scenario": scenario,
                "phenotype": phenotype,
                "condition": cond,
                "clinical_mean": clinical_payoffs.mean(),
                "healthy_mean": healthy_c2.mean(),
                "noaffect_mean": noaffect_c4.mean(),
                "d_vs_healthy": d_ch,
                "p_vs_healthy": p_ch,
                "d_vs_noaffect": d_cn,
                "p_vs_noaffect": p_cn,
                "n_clinical": len(clinical_payoffs),
                "n_healthy": len(healthy_c2),
            })

    results_df = pd.DataFrame(results)
    results_path = output_dir / "clinical_sensitivity_stats.csv"
    results_df.to_csv(results_path, index=False)

    print("\n" + "=" * 70)
    print("CLINICAL SENSITIVITY RESULTS")
    print("=" * 70)
    for _, row in results_df.iterrows():
        print(f"\n{row['scenario']} | {row['phenotype']} (C{row['condition']})")
        print(f"  Payoff: {row['clinical_mean']:.1f} (clinical) vs {row['healthy_mean']:.1f} (healthy) vs {row['noaffect_mean']:.1f} (no-affect)")
        print(f"  vs healthy: d = {row['d_vs_healthy']:.3f}, p = {row['p_vs_healthy']:.4f}")
        print(f"  vs no-affect: d = {row['d_vs_noaffect']:.3f}, p = {row['p_vs_noaffect']:.4f}")

    return results_df


def compute_beta_dynamics(combined: pd.DataFrame, output_dir: Path):
    """Extract beta trajectory statistics per phenotype."""
    if "beta_mean" not in combined.columns:
        print("No beta_mean column — skipping beta dynamics analysis.")
        return None

    beta_stats = []
    for (scenario, phenotype, condition), group in combined.groupby(
        ["scenario", "phenotype", "condition"]
    ):
        beta_vals = group["beta_mean"].dropna()
        if len(beta_vals) == 0:
            continue
        beta_stats.append({
            "scenario": scenario,
            "phenotype": phenotype,
            "condition": condition,
            "beta_mean": beta_vals.mean(),
            "beta_std": beta_vals.std(),
            "beta_range": beta_vals.max() - beta_vals.min(),
            "beta_final_mean": group.groupby("seed")["beta_mean"].last().mean(),
        })

    if beta_stats:
        beta_df = pd.DataFrame(beta_stats)
        beta_df.to_csv(output_dir / "clinical_beta_dynamics.csv", index=False)
        print("\nBeta dynamics:")
        for _, row in beta_df.iterrows():
            print(f"  {row['scenario']} | {row['phenotype']} C{row['condition']}: "
                  f"mean={row['beta_mean']:.3f}, std={row['beta_std']:.3f}, range={row['beta_range']:.3f}")
        return beta_df
    return None


def main():
    parser = argparse.ArgumentParser(description="Phase 5: Clinical sensitivity analysis")
    parser.add_argument("--replications", type=int, default=5, help="Seeds per condition")
    parser.add_argument("--output-dir", default="results/clinical_sensitivity", help="Output directory")
    parser.add_argument("--seed", type=int, default=42, help="Base random seed")
    parser.add_argument(
        "--scenarios",
        nargs="+",
        default=["sh_default", "sh_betrayal"],
        choices=list(SCENARIOS.keys()),
        help="Scenarios to run",
    )
    parser.add_argument(
        "--phenotypes",
        nargs="+",
        default=list(CLINICAL_PHENOTYPES.keys()),
        choices=list(CLINICAL_PHENOTYPES.keys()),
        help="Phenotypes to run",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save run metadata
    metadata = {
        "start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "replications": args.replications,
        "seed": args.seed,
        "scenarios": args.scenarios,
        "phenotypes": args.phenotypes,
    }
    (output_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    all_dfs = []
    for scenario in args.scenarios:
        print(f"\n{'='*60}")
        print(f"Scenario: {scenario}")
        print(f"{'='*60}")

        for phenotype in args.phenotypes:
            print(f"\nRunning {phenotype}...")
            df = run_phenotype(scenario, phenotype, args.replications, args.seed, output_dir)
            all_dfs.append(df)

    if all_dfs:
        combined = pd.concat(all_dfs, ignore_index=True)
        combined.to_csv(output_dir / "all_clinical.csv", index=False)
        print(f"\nCombined: {len(combined)} rows -> {output_dir / 'all_clinical.csv'}")

        stats_df = analyze_results(combined, output_dir)
        compute_beta_dynamics(combined, output_dir)

        metadata["end_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
        metadata["total_rows"] = len(combined)
        (output_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()

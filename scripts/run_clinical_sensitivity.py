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

from experiment.config import ExperimentConfig
from experiment.runner import ExperimentRunner

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
        "initial_beta": 0.5,
    },
    "alexithymia": {
        "conditions": [9],
        "alpha_charge": 0.1,
        "initial_beta": 0.5,
    },
    "borderline": {
        "conditions": [10],
        "alpha_charge": 12.0,
        "initial_beta": 0.5,
    },
    "depression": {
        "conditions": [11],
        "alpha_charge": 3.0,
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
    },
    "sh_betrayal": {
        "num_rounds": 120,
        "p_switch": 0.0,
        "assignment_mode": "agent_choice",
        "observation_noise": 0.1,
        "initial_partner_types": ["cooperator", "reciprocator", "cooperator", "random"],
        "scheduled_type_switches": [{"round": 31, "partner_idx": 0, "to_type": "exploiter"}],
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
        "use_parameter_learning": False,
        "deep_horizon": 8,
        "shallow_horizon": 2,
        "max_policies": 4096,
        "sigma_0_sq": 0.25,
        "lesion_mode": "decouple",
        "num_replications": num_replications,
        "random_seed": random_seed,
        "conditions": phenotype["conditions"],
        "partner_types": ["cooperator", "reciprocator", "exploiter", "random"],
        "run_sensitivity": False,
        # Phenotype-specific parameters
        "alpha_charge": phenotype["alpha_charge"],
        "initial_beta": phenotype["initial_beta"],
    }

    if "initial_partner_types" in scenario:
        params["initial_partner_types"] = scenario["initial_partner_types"]
    if "scheduled_type_switches" in scenario:
        params["scheduled_type_switches"] = scenario["scheduled_type_switches"]

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


def analyze_betrayal_windows(combined: pd.DataFrame, output_dir: Path):
    """Analyze clinical phenotype differences across betrayal windows.

    Windows: pre-betrayal (20-29), impact (30-39), early-recovery (40-49),
    late-recovery (60-79), late (90-119).
    """
    from scipy import stats

    betrayal_data = combined[combined["scenario"].str.contains("betrayal")]
    if len(betrayal_data) == 0:
        print("No betrayal data — skipping window analysis.")
        return None

    windows = {
        "pre_betrayal": (20, 29),
        "impact": (30, 39),
        "early_recovery": (40, 49),
        "late_recovery": (60, 79),
        "late": (90, 119),
    }

    results = []
    for window_name, (start, end) in windows.items():
        window_data = betrayal_data[
            (betrayal_data["round"] >= start) & (betrayal_data["round"] <= end)
        ]
        if len(window_data) == 0:
            continue

        window_payoffs = (
            window_data.groupby(["phenotype", "condition", "seed"])["payoff"]
            .mean()
            .reset_index()
        )

        healthy_c2 = window_payoffs[
            (window_payoffs["phenotype"] == "healthy") & (window_payoffs["condition"] == 2)
        ]["payoff"].values

        for phenotype in ["alexithymia", "borderline", "depression"]:
            cond = {"alexithymia": 9, "borderline": 10, "depression": 11}[phenotype]
            clinical = window_payoffs[
                (window_payoffs["phenotype"] == phenotype) & (window_payoffs["condition"] == cond)
            ]["payoff"].values

            if len(clinical) < 2 or len(healthy_c2) < 2:
                continue

            pooled_std = np.sqrt((healthy_c2.std() ** 2 + clinical.std() ** 2) / 2)
            d = (healthy_c2.mean() - clinical.mean()) / pooled_std if pooled_std > 0 else 0
            _, p = stats.ttest_ind(clinical, healthy_c2)

            results.append({
                "window": window_name,
                "phenotype": phenotype,
                "condition": cond,
                "clinical_mean": clinical.mean(),
                "healthy_mean": healthy_c2.mean(),
                "d_vs_healthy": d,
                "p_vs_healthy": p,
            })

    if results:
        df = pd.DataFrame(results)
        df.to_csv(output_dir / "clinical_betrayal_windows.csv", index=False)
        print("\nBetrayal window analysis (d vs healthy C2):")
        for window_name in windows:
            wdf = df[df["window"] == window_name]
            if len(wdf) == 0:
                continue
            parts = []
            for _, row in wdf.iterrows():
                sig = "*" if row["p_vs_healthy"] < 0.05 else ""
                parts.append(f"{row['phenotype']}={row['d_vs_healthy']:+.2f}{sig}")
            print(f"  {window_name}: {', '.join(parts)}")
        return df
    return None


def compute_clinical_bayes_factors(combined: pd.DataFrame, output_dir: Path):
    """Compute Bayes factors: each clinical phenotype vs healthy C2."""
    if "cumulative_log_evidence" not in combined.columns:
        print("No log-evidence column — skipping BF analysis.")
        return None

    results = []
    for scenario in combined["scenario"].unique():
        sdf = combined[scenario == combined["scenario"]]

        # Get final-round log-evidence per episode
        final_rounds = sdf.groupby(["phenotype", "condition", "seed"]).last().reset_index()

        healthy_le = final_rounds[
            (final_rounds["phenotype"] == "healthy") & (final_rounds["condition"] == 2)
        ]["cumulative_log_evidence"].values

        noaffect_le = final_rounds[
            (final_rounds["phenotype"] == "healthy") & (final_rounds["condition"] == 4)
        ]["cumulative_log_evidence"].values

        for phenotype in ["alexithymia", "borderline", "depression"]:
            cond = {"alexithymia": 9, "borderline": 10, "depression": 11}[phenotype]
            clinical_le = final_rounds[
                (final_rounds["phenotype"] == phenotype) & (final_rounds["condition"] == cond)
            ]["cumulative_log_evidence"].values

            if len(clinical_le) < 2 or len(healthy_le) < 2:
                continue

            # BF: clinical vs healthy (positive = clinical better)
            bf_vs_healthy = (clinical_le.mean() - healthy_le.mean()) / np.log(10)
            # BF: clinical vs no-affect
            bf_vs_noaffect = (clinical_le.mean() - noaffect_le.mean()) / np.log(10) if len(noaffect_le) > 0 else float("nan")

            results.append({
                "scenario": scenario,
                "phenotype": phenotype,
                "condition": cond,
                "log10_bf_vs_healthy": bf_vs_healthy,
                "log10_bf_vs_noaffect": bf_vs_noaffect,
                "mean_le_clinical": clinical_le.mean(),
                "mean_le_healthy": healthy_le.mean(),
                "mean_le_noaffect": noaffect_le.mean() if len(noaffect_le) > 0 else float("nan"),
            })

    if results:
        bf_df = pd.DataFrame(results)
        bf_df.to_csv(output_dir / "clinical_bayes_factors.csv", index=False)
        print("\nBayes factors (log10 BF, positive = clinical better):")
        for _, row in bf_df.iterrows():
            strength = "decisive" if abs(row["log10_bf_vs_healthy"]) > 2 else \
                       "strong" if abs(row["log10_bf_vs_healthy"]) > 1 else \
                       "substantial" if abs(row["log10_bf_vs_healthy"]) > 0.5 else "anecdotal"
            print(f"  {row['scenario']} | {row['phenotype']}: "
                  f"vs healthy = {row['log10_bf_vs_healthy']:+.2f} ({strength}), "
                  f"vs no-affect = {row['log10_bf_vs_noaffect']:+.2f}")
        return bf_df
    return None


def _parse_betas(betas_str: str, partner_idx: int) -> float:
    """Extract active partner's beta from serialized array."""
    import ast
    try:
        betas = ast.literal_eval(betas_str)
        return float(betas[partner_idx])
    except (ValueError, IndexError, TypeError):
        return float("nan")


def compute_beta_dynamics(combined: pd.DataFrame, output_dir: Path):
    """Extract beta trajectory statistics per phenotype."""
    if "betas" not in combined.columns:
        print("No betas column — skipping beta dynamics analysis.")
        return None

    # Parse active partner beta
    combined = combined.copy()
    if "partner_idx" in combined.columns:
        combined["active_beta"] = combined.apply(
            lambda row: _parse_betas(str(row["betas"]), int(row["partner_idx"])), axis=1
        )
    else:
        combined["active_beta"] = combined["betas"].apply(
            lambda x: _parse_betas(str(x), 0)
        )

    beta_stats = []
    for (scenario, phenotype, condition), group in combined.groupby(
        ["scenario", "phenotype", "condition"]
    ):
        beta_vals = group["active_beta"].dropna()
        if len(beta_vals) == 0:
            continue

        # Per-episode beta volatility (std within each episode)
        per_ep_std = group.groupby("seed")["active_beta"].std().mean()

        beta_stats.append({
            "scenario": scenario,
            "phenotype": phenotype,
            "condition": condition,
            "beta_mean": beta_vals.mean(),
            "beta_std": beta_vals.std(),
            "beta_volatility": per_ep_std,
            "beta_range": beta_vals.max() - beta_vals.min(),
            "beta_final_mean": group.groupby("seed")["active_beta"].last().mean(),
        })

    if beta_stats:
        beta_df = pd.DataFrame(beta_stats)
        beta_df.to_csv(output_dir / "clinical_beta_dynamics.csv", index=False)
        print("\nBeta dynamics:")
        for _, row in beta_df.iterrows():
            print(f"  {row['scenario']} | {row['phenotype']} C{row['condition']}: "
                  f"mean={row['beta_mean']:.3f}, volatility={row['beta_volatility']:.3f}, range={row['beta_range']:.3f}")
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
        compute_clinical_bayes_factors(combined, output_dir)
        analyze_betrayal_windows(combined, output_dir)
        compute_beta_dynamics(combined, output_dir)

        metadata["end_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
        metadata["total_rows"] = len(combined)
        (output_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()

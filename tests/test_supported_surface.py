import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd

import tasks.trust as trust
from experiments.trust.conditions import (
    get_condition_metadata,
    get_condition_name,
    get_preset_condition,
    normalize_condition_name,
)
from experiments.trust.config import ExperimentConfig
from experiments.trust.runner import ExperimentRunner
from tasks.trust import AffectiveAgent, LesionedAgent, TrustGameAgent

REPO_ROOT = Path(__file__).resolve().parents[1]


def _build_model(config):
    from tasks.trust.models import TrustGameModel

    return TrustGameModel(config)


def _load_script_module(script_name: str):
    script_path = REPO_ROOT / "scripts" / script_name
    module_name = script_name.replace("/", "_").replace(".py", "")
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_config_legacy_beta_alias_loads_but_serializes_canonical(tmp_path):
    config = ExperimentConfig.from_dict({"num_beta_levels": 7, "num_rounds": 2, "num_replications": 1})
    assert config.beta_num_levels == 7

    output_path = tmp_path / "config.json"
    config.to_json(output_path)
    payload = json.loads(output_path.read_text())
    assert payload["beta_num_levels"] == 7
    assert "num_beta_levels" not in payload


def test_condition_metadata_and_presets_normalize_current_names():
    metadata = get_condition_metadata(6)
    assert metadata.name == "tau4_affect"
    assert get_condition_name(6) == "tau4_affect"
    assert get_preset_condition("no_epistemic").name == "no_epistemic"
    assert normalize_condition_name("no_epistemic") == "no_epistemic"


def test_runner_no_epistemic_preset_builds_affective_agent():
    config = ExperimentConfig(
        payoff_mode="binary",
        num_rounds=2,
        num_replications=1,
        conditions=[],
        presets=["no_epistemic"],
        random_seed=0,
    )
    runner = ExperimentRunner(config)
    model = _build_model(config)
    agent = runner._create_agent(condition="no_epistemic", model=model, seed=0)

    assert isinstance(agent, trust.AffectiveAgent)
    assert trust.TrustGameAgent is TrustGameAgent
    assert trust.AffectiveAgent is AffectiveAgent
    assert trust.LesionedAgent is LesionedAgent
    assert set(trust.__all__) >= {"TrustGameAgent", "AffectiveAgent", "LesionedAgent"}


def test_supported_cli_scripts_parse_and_run_smoke(tmp_path):
    run_experiment = _load_script_module("experiment/run.py")
    run_analysis = _load_script_module("analysis/analyze.py")
    run_model_comparison = _load_script_module("analysis/model_comparison.py")
    run_preliminary = _load_script_module("experiment/preliminary.py")
    run_targeted_reanalysis = _load_script_module("analysis/targeted_reanalysis.py")
    run_visualization = _load_script_module("analysis/visualize.py")

    config = ExperimentConfig(
        payoff_mode="binary",
        num_rounds=2,
        num_replications=1,
        random_seed=0,
        conditions=[1, 2],
        run_sensitivity=False,
    )
    config_path = tmp_path / "tiny.json"
    config.to_json(config_path)

    assert run_preliminary.build_parser().parse_args(
        ["--config", str(config_path), "--replications", "1", "--rounds", "2"]
    )
    assert run_targeted_reanalysis.build_parser().parse_args(["--output-dir", "out"])
    assert run_visualization.build_parser().parse_args(["--results", "x.csv", "--output-dir", "out"])
    assert run_model_comparison.build_parser().parse_args(["--results", "x.csv", "--output-dir", "out"])

    batch_name = "smoke_batch"
    sys.argv = [
        "scripts/experiment/run.py",
        "--config",
        str(config_path),
        "--output-dir",
        str(tmp_path / "results"),
        "--batch-name",
        batch_name,
        "--workers",
        "1",
    ]
    assert run_experiment.main() == 0

    results_path = tmp_path / "results" / batch_name / "tiny" / "results.csv"
    partial_path = tmp_path / "results" / batch_name / "tiny" / "results_partial.csv"
    config_copy_path = tmp_path / "results" / batch_name / "tiny" / "config.json"
    metadata_path = tmp_path / "results" / batch_name / "tiny" / "batch_metadata.json"
    figures_dir = tmp_path / "figures"
    model_dir = tmp_path / "model"
    assert results_path.exists()
    assert partial_path.exists()
    assert config_copy_path.exists()
    assert metadata_path.exists()
    assert run_analysis.main(["--results", str(results_path), "--output-dir", str(figures_dir)]) == 0
    assert run_model_comparison.main(["--results", str(results_path), "--output-dir", str(model_dir)]) == 0
    assert (figures_dir / "final_round_summary.csv").exists()
    assert (model_dir / "model_comparison_report.json").exists()


def test_targeted_reanalysis_cli_writes_requested_outputs(tmp_path):
    run_targeted_reanalysis = _load_script_module("analysis/targeted_reanalysis.py")

    h1_rows = []
    for seed in (0, 1):
        h1_rows.extend(
            [
                {
                    "condition": 1,
                    "condition_name": "tau1_no_affect",
                    "seed": seed,
                    "round": 0,
                    "payoff": 10 + seed,
                    "inferred_type_correct": 1.0,
                    "inferred_stance_correct": 1.0,
                    "inferred_joint_correct": 1.0,
                    "q_pi_entropy": 0.5,
                    "mean_abs_step_efe": 1.0,
                    "planning_cost": 1.0,
                    "planning_cost_ratio": 1.0,
                },
                {
                    "condition": 2,
                    "condition_name": "tau1_affect",
                    "seed": seed,
                    "round": 0,
                    "payoff": 14 + seed,
                    "inferred_type_correct": 1.0,
                    "inferred_stance_correct": 1.0,
                    "inferred_joint_correct": 1.0,
                    "q_pi_entropy": 0.5,
                    "mean_abs_step_efe": 1.0,
                    "planning_cost": 1.0,
                    "planning_cost_ratio": 1.0,
                },
                {
                    "condition": 3,
                    "condition_name": "tau2_no_affect",
                    "seed": seed,
                    "round": 0,
                    "payoff": 11 + seed,
                    "inferred_type_correct": 1.0,
                    "inferred_stance_correct": 1.0,
                    "inferred_joint_correct": 1.0,
                    "q_pi_entropy": 0.5,
                    "mean_abs_step_efe": 1.0,
                    "planning_cost": 1.0,
                    "planning_cost_ratio": 1.0,
                },
                {
                    "condition": 4,
                    "condition_name": "tau2_affect",
                    "seed": seed,
                    "round": 0,
                    "payoff": 15 + seed,
                    "inferred_type_correct": 1.0,
                    "inferred_stance_correct": 1.0,
                    "inferred_joint_correct": 1.0,
                    "q_pi_entropy": 0.5,
                    "mean_abs_step_efe": 1.0,
                    "planning_cost": 1.0,
                    "planning_cost_ratio": 1.0,
                },
            ]
        )
    h2_rows = []
    for seed in (0, 1):
        h2_rows.extend(
            [
                {
                    "condition": 5,
                    "condition_name": "tau4_no_affect",
                    "seed": seed,
                    "round": 0,
                    "payoff": 10 + seed,
                    "inferred_type_correct": 1.0,
                    "inferred_stance_correct": 0.8,
                    "inferred_joint_correct": 0.8,
                    "q_pi_entropy": 0.5,
                    "mean_abs_step_efe": 1.0,
                    "planning_cost": 1.0,
                    "planning_cost_ratio": 1.0,
                },
                {
                    "condition": 6,
                    "condition_name": "tau4_affect",
                    "seed": seed,
                    "round": 0,
                    "payoff": 16 + seed,
                    "inferred_type_correct": 1.0,
                    "inferred_stance_correct": 0.9,
                    "inferred_joint_correct": 0.9,
                    "q_pi_entropy": 0.5,
                    "mean_abs_step_efe": 1.0,
                    "planning_cost": 1.0,
                    "planning_cost_ratio": 1.0,
                },
                {
                    "condition": 99,
                    "condition_name": "lesioned",
                    "seed": seed,
                    "round": 0,
                    "payoff": 12 + seed,
                    "inferred_type_correct": 1.0,
                    "inferred_stance_correct": 0.85,
                    "inferred_joint_correct": 0.85,
                    "q_pi_entropy": 0.5,
                    "mean_abs_step_efe": 1.0,
                    "planning_cost": 1.0,
                    "planning_cost_ratio": 1.0,
                },
            ]
        )
    h4_rows = []
    for seed in (0, 1):
        for round_idx in range(30, 61):
            h4_rows.extend(
                [
                    {"condition_name": "tau4_no_affect", "seed": seed, "round": round_idx, "payoff": 1.0 + seed},
                    {"condition_name": "tau4_affect", "seed": seed, "round": round_idx, "payoff": 2.0 + seed},
                ]
            )

    h1_path = tmp_path / "h1.csv"
    h2_path = tmp_path / "h2.csv"
    h4_path = tmp_path / "h4.csv"
    pd.DataFrame(h1_rows).to_csv(h1_path, index=False)
    pd.DataFrame(h2_rows).to_csv(h2_path, index=False)
    pd.DataFrame(h4_rows).to_csv(h4_path, index=False)

    out_dir = tmp_path / "reanalysis"
    assert (
        run_targeted_reanalysis.main(
            [
                "--h1-results",
                str(h1_path),
                "--h2-results",
                str(h2_path),
                "--h4-results",
                str(h4_path),
                "--output-dir",
                str(out_dir),
            ]
        )
        == 0
    )

    assert (out_dir / "h1_shallow_reanalysis.txt").exists()
    assert (out_dir / "h2_lesion_reanalysis.txt").exists()
    assert (out_dir / "h4_betrayal_window_reanalysis.txt").exists()
    h1_text = (out_dir / "h1_shallow_reanalysis.txt").read_text()
    h2_text = (out_dir / "h2_lesion_reanalysis.txt").read_text()
    h4_text = (out_dir / "h4_betrayal_window_reanalysis.txt").read_text()
    assert "tau=1" in h1_text
    assert "Source file:" in h1_text
    assert "completed_seeds=" in h1_text
    assert "lesioned vs tau4_affect" in h2_text
    assert "Source type: final results" in h2_text
    assert "rounds 30-60" in h4_text


def test_targeted_reanalysis_falls_back_to_partial_checkpoints_and_tolerates_live_tail(tmp_path):
    run_targeted_reanalysis = _load_script_module("analysis/targeted_reanalysis.py")

    results_root = tmp_path / "results"
    h1_main = results_root / "h1_factorial" / "h1_depth_affect_factorial"
    h1_setsid = results_root / "h1_factorial_setsid_20260416" / "h1_depth_affect_factorial"
    h2_dir = tmp_path / "inputs" / "h2"
    h4_dir = tmp_path / "inputs" / "h4"
    h1_main.mkdir(parents=True)
    h1_setsid.mkdir(parents=True)
    h2_dir.mkdir(parents=True)
    h4_dir.mkdir(parents=True)

    (h1_main / "results_partial.csv").write_text(
        "\n".join(
            [
                "condition_name,seed,round,payoff,inferred_joint_correct",
                "tau1_no_affect,0,199,10,1.0",
                "tau1_no_affect,1,199,11,1.0",
                "tau2_no_affect,0,199,12,1.0",
                'tau2_no_affect,1,199,"unterminated',
            ]
        )
        + "\n"
    )
    pd.DataFrame(
        [
            {"condition_name": "tau1_affect", "seed": 0, "round": 199, "payoff": 15, "inferred_joint_correct": 1.0},
            {"condition_name": "tau1_affect", "seed": 1, "round": 199, "payoff": 16, "inferred_joint_correct": 1.0},
            {"condition_name": "tau2_affect", "seed": 0, "round": 199, "payoff": 17, "inferred_joint_correct": 1.0},
        ]
    ).to_csv(h1_setsid / "results_partial.csv", index=False)

    h2_path = h2_dir / "h2.csv"
    pd.DataFrame(
        [
            {"condition_name": "tau4_no_affect", "seed": 0, "round": 199, "payoff": 10, "inferred_joint_correct": 0.8},
            {"condition_name": "tau4_affect", "seed": 0, "round": 199, "payoff": 16, "inferred_joint_correct": 0.9},
            {"condition_name": "lesioned", "seed": 0, "round": 199, "payoff": 12, "inferred_joint_correct": 0.8},
            {"condition_name": "tau4_no_affect", "seed": 1, "round": 199, "payoff": 11, "inferred_joint_correct": 0.8},
            {"condition_name": "tau4_affect", "seed": 1, "round": 199, "payoff": 17, "inferred_joint_correct": 0.9},
            {"condition_name": "lesioned", "seed": 1, "round": 199, "payoff": 13, "inferred_joint_correct": 0.8},
        ]
    ).to_csv(h2_path, index=False)

    h4_path = h4_dir / "h4.csv"
    h4_rows = []
    for seed in (0, 1):
        for round_idx in range(30, 61):
            h4_rows.extend(
                [
                    {"condition_name": "tau4_no_affect", "seed": seed, "round": round_idx, "payoff": 1.0 + seed},
                    {"condition_name": "tau4_affect", "seed": seed, "round": round_idx, "payoff": 2.0 + seed},
                ]
            )
    pd.DataFrame(h4_rows).to_csv(h4_path, index=False)

    out_dir = tmp_path / "reanalysis"
    h1_missing_final = results_root / "h1_factorial" / "h1_depth_affect_factorial" / "results.csv"
    assert (
        run_targeted_reanalysis.main(
            [
                "--h1-results",
                str(h1_missing_final),
                "--h2-results",
                str(h2_path),
                "--h4-results",
                str(h4_path),
                "--output-dir",
                str(out_dir),
            ]
        )
        == 0
    )

    h1_text = (out_dir / "h1_shallow_reanalysis.txt").read_text()
    assert "Source files:" in h1_text
    assert str(h1_main / "results_partial.csv") in h1_text
    assert str(h1_setsid / "results_partial.csv") in h1_text
    assert "tau1_affect" in h1_text
    assert "tau2_no_affect" in h1_text


def test_historical_archive_surface_is_removed():
    supported_scripts = {
        "experiment/run.py",
        "experiment/preliminary.py",
        "experiment/smoke.py",
        "experiment/inspect.py",
        "analysis/analyze.py",
        "analysis/summarize.py",
        "analysis/visualize.py",
        "analysis/model_comparison.py",
        "analysis/targeted_reanalysis.py",
        "benchmark/analyze.py",
        "benchmark/run_cvc.py",
        "benchmark/package_cvc.py",
        "cvc/list_missions.py",
        "cvc/obs_diagnostic.py",
    }
    top_level_scripts = {path.name for path in (REPO_ROOT / "scripts").glob("*.py")}
    all_scripts = {str(path.relative_to(REPO_ROOT / "scripts")) for path in (REPO_ROOT / "scripts").rglob("*.py")}
    cli_doc = (REPO_ROOT / "docs" / "operations" / "cli.md").read_text()
    historical_doc = (REPO_ROOT / "docs" / "results" / "historical_findings.md").read_text()

    assert top_level_scripts == set()
    assert supported_scripts <= all_scripts
    for script_name in supported_scripts:
        assert script_name in cli_doc
    for deleted_name in {
        "run_experiment.py",
        "run_analysis.py",
        "run_visualization.py",
        "run_benchmark.py",
        "analyze_benchmark.py",
        "analyze_benchmark_paper.py",
        "analyze_clinical_results.py",
        "run_clinical_sensitivity.py",
        "generate_paper_figures.py",
    }:
        assert deleted_name not in all_scripts
    assert not (REPO_ROOT / "archive").exists()
    assert "archive/configs/" not in cli_doc
    assert "run_precision_modulation.py" in historical_doc

import importlib.util
import json
import sys
from pathlib import Path

from affect_aif.agent.affective_agent import AffectiveAgent
from affect_aif.experiment.conditions import get_condition_metadata, get_condition_name, normalize_condition_name
from affect_aif.experiment.config import ExperimentConfig
from affect_aif.experiment.runner import ExperimentRunner
from affect_aif.generative_model.model import TrustGameModel

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_script_module(script_name: str):
    script_path = REPO_ROOT / "scripts" / script_name
    spec = importlib.util.spec_from_file_location(script_name.replace(".py", ""), script_path)
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


def test_condition_metadata_normalizes_legacy_alias():
    metadata = get_condition_metadata(12)
    assert metadata.name == "variational_affective"
    assert get_condition_name(12) == "variational_affective"
    assert normalize_condition_name("discrete_affective_shallow") == "variational_affective"


def test_runner_condition_12_uses_variational_affective_agent():
    config = ExperimentConfig(num_rounds=2, num_replications=1, calibration_episodes=1, conditions=[12], random_seed=0)
    runner = ExperimentRunner(config)
    model = TrustGameModel(config)
    agent = runner._create_agent(condition=12, model=model, seed=0)

    assert isinstance(agent, AffectiveAgent)
    assert agent.beta_mode == "variational"


def test_supported_cli_wrappers_parse_and_run_smoke(tmp_path):
    run_experiment = _load_script_module("run_experiment.py")
    run_analysis = _load_script_module("run_analysis.py")
    run_model_comparison = _load_script_module("run_model_comparison.py")
    run_preliminary = _load_script_module("run_preliminary.py")
    run_visualization = _load_script_module("run_visualization.py")

    config = ExperimentConfig(
        num_rounds=2,
        num_replications=1,
        calibration_episodes=1,
        random_seed=0,
        conditions=[1, 2],
        run_sensitivity=False,
    )
    config_path = tmp_path / "tiny.json"
    config.to_json(config_path)

    assert run_preliminary.build_parser().parse_args(
        ["--config", str(config_path), "--replications", "1", "--rounds", "2"]
    )
    assert run_visualization.build_parser().parse_args(["--results", "x.csv", "--output-dir", "out"])
    assert run_model_comparison.build_parser().parse_args(["--results", "x.csv", "--output-dir", "out"])

    batch_name = "smoke_batch"
    sys.argv = [
        "run_experiment.py",
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
    figures_dir = tmp_path / "figures"
    model_dir = tmp_path / "model"
    assert results_path.exists()
    assert run_analysis.main(["--results", str(results_path), "--output-dir", str(figures_dir)]) == 0
    assert run_model_comparison.main(["--results", str(results_path), "--output-dir", str(model_dir)]) == 0
    assert (figures_dir / "final_round_summary.csv").exists()
    assert (model_dir / "model_comparison_report.json").exists()


def test_archive_boundary_is_explicit():
    supported_scripts = {path.name for path in (REPO_ROOT / "scripts").glob("*.py")}
    archived_scripts = {path.name for path in (REPO_ROOT / "archive" / "scripts").glob("*.py")}
    pyproject_text = (REPO_ROOT / "pyproject.toml").read_text()
    cli_doc = (REPO_ROOT / "docs" / "cli.md").read_text()

    assert supported_scripts == {
        "analyze_benchmark.py",
        "analyze_benchmark_paper.py",
        "analyze_clinical_results.py",
        "cvc_list_missions.py",
        "cvc_obs_diagnostic.py",
        "run_analysis.py",
        "run_benchmark.py",
        "run_clinical_sensitivity.py",
        "run_experiment.py",
        "run_model_comparison.py",
        "run_preliminary.py",
        "run_visualization.py",
    }
    assert "run_precision_modulation.py" in archived_scripts
    assert 'extend-exclude = ["archive"]' in pyproject_text
    assert "archive/configs/" in cli_doc

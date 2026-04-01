import importlib.util
import json
import sys
from pathlib import Path

from affect_aif.agent.affective_agent import AffectiveAgent
from affect_aif.experiment.conditions import (
    get_condition_metadata,
    get_condition_name,
    get_preset_condition,
    normalize_condition_name,
)
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


def test_condition_metadata_and_presets_normalize_current_names():
    metadata = get_condition_metadata(6)
    assert metadata.name == "tau4_affect"
    assert get_condition_name(6) == "tau4_affect"
    assert get_preset_condition("variational_beta").name == "variational_beta"
    assert normalize_condition_name("variational_beta") == "variational_beta"


def test_runner_variational_beta_preset_uses_variational_affective_agent():
    config = ExperimentConfig(
        num_rounds=2,
        num_replications=1,
        calibration_episodes=1,
        conditions=[],
        presets=["variational_beta"],
        random_seed=0,
    )
    runner = ExperimentRunner(config)
    model = TrustGameModel(config)
    agent = runner._create_agent(condition="variational_beta", model=model, seed=0)

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


def test_archive_boundary_is_explicit():
    supported_scripts = {
        "run_experiment.py",
        "run_preliminary.py",
        "run_analysis.py",
        "run_visualization.py",
        "run_model_comparison.py",
    }
    all_scripts = {path.name for path in (REPO_ROOT / "scripts").glob("*.py")}
    archived_scripts = {path.name for path in (REPO_ROOT / "archive" / "scripts").glob("*.py")}
    pyproject_text = (REPO_ROOT / "pyproject.toml").read_text()
    cli_doc = (REPO_ROOT / "docs" / "cli.md").read_text()

    assert supported_scripts <= all_scripts
    assert "analyze_benchmark.py" in all_scripts
    assert "analyze_benchmark.py" not in supported_scripts
    for script_name in supported_scripts:
        assert script_name in cli_doc
    assert "run_precision_modulation.py" in archived_scripts
    assert 'extend-exclude = ["archive"]' in pyproject_text
    assert "archive/configs/" in cli_doc

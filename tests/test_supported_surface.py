import importlib.util
import json
import subprocess
import sys
from pathlib import Path

from experiment_spec_helpers import write_example_toml
from runtime_helpers import build_runtime

import tasks.trust as trust
import tasks.trust.affect
import tasks.trust.pomdp
import tasks.trust.runtime
from experiments.trust.config import ExperimentConfig
from experiments.trust.spec import ExperimentSpec, load_experiment_specs

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_supported_trust_runtime_imports_are_exposed():
    assert tasks.trust.affect.DiscreteBetaState is trust.DiscreteBetaState
    assert tasks.trust.pomdp.build_trust_pomdp_template is trust.build_trust_pomdp_template
    assert tasks.trust.runtime.PartnerBank is trust.PartnerBank


def _load_script_module(script_name: str):
    script_path = REPO_ROOT / "scripts" / script_name
    module_name = script_name.replace("/", "_").replace(".py", "")
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_config_uses_canonical_beta_level_name():
    config = ExperimentConfig.from_dict({"beta_num_levels": 7, "num_rounds": 2, "num_replications": 1})
    assert config.beta_num_levels == 7


def test_toml_spec_surface_uses_explicit_variants():
    spec = ExperimentSpec.from_toml(REPO_ROOT / "configs/diagnostics/h5_timescale_volatility/betrayal_choice.toml")
    assert [variant.id for variant in spec.variants] == ["no_affect", "affect", "lesioned", "global_beta"]
    assert {run.variant_id for run in spec.expand_runs()} == {"no_affect", "affect", "lesioned", "global_beta"}


def test_no_epistemic_variant_disables_information_gain():
    config = ExperimentConfig(payoff_mode="binary", num_rounds=2, num_replications=1, random_seed=0)
    runtime = build_runtime(config, variant_id="no_epistemic", affect="none", epistemic_value=False)

    assert runtime.agent_kind == "base"
    assert runtime.affect_mode == "none"
    assert runtime.partner_bank.beta is None
    assert all(agent.use_states_info_gain is False for agent in runtime.partner_bank.agents)
    assert set(trust.__all__) >= {"TrustPomdpTemplate", "PartnerBank", "build_trust_pomdp_template"}


def test_supported_cli_scripts_parse_and_run_smoke(tmp_path):
    run_experiment = _load_script_module("experiment/run.py")
    run_analysis = _load_script_module("analysis/analyze.py")
    run_model_comparison = _load_script_module("analysis/model_comparison.py")
    run_visualization = _load_script_module("analysis/visualize.py")

    config_path = REPO_ROOT / "configs" / "diagnostics" / "smoke" / "trust_smoke.toml"

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

    results_path = tmp_path / "results" / batch_name / "smoke" / "smoke" / "results.csv"
    partial_path = tmp_path / "results" / batch_name / "smoke" / "smoke" / "results_partial.csv"
    config_copy_path = tmp_path / "results" / batch_name / "smoke" / "smoke" / "config.toml"
    metadata_path = tmp_path / "results" / batch_name / "smoke" / "smoke" / "batch_metadata.json"
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


def test_run_cli_dry_run_reports_toml_manifest(tmp_path):
    run_experiment = _load_script_module("experiment/run.py")
    config_path = write_example_toml(tmp_path / "betrayal_choice.toml")

    sys.argv = [
        "scripts/experiment/run.py",
        "--config",
        str(config_path),
        "--output-dir",
        str(tmp_path / "results"),
        "--batch-name",
        "dry",
        "--workers",
        "1",
        "--dry-run",
    ]

    assert run_experiment.main() == 0
    manifest = json.loads((tmp_path / "results" / "dry" / "manifest.json").read_text())
    assert manifest["configs"][0]["hypothesis_id"] == "h5"
    assert manifest["configs"][0]["experiment_id"] == "betrayal_choice"
    assert manifest["configs"][0]["family"] == "trust"
    assert manifest["configs"][0]["variants"] == ["affect", "no_affect"]


def test_experiment_run_dry_run_reports_families(tmp_path):
    run_experiment = _load_script_module("experiment/run.py")

    sys.argv = [
        "scripts/experiment/run.py",
        "--config",
        "configs/diagnostics/smoke/trust_smoke.toml",
        "--output-dir",
        str(tmp_path / "results"),
        "--batch-name",
        "dry",
        "--dry-run",
    ]

    assert run_experiment.main() == 0
    manifest = json.loads((tmp_path / "results" / "dry" / "manifest.json").read_text())
    assert [(entry["family"], entry["experiment_id"]) for entry in manifest["configs"]] == [
        ("trust", "smoke"),
    ]


def test_core_hypothesis_experiments_exist():
    expected = [
        "configs/paper/01_predictability_value.toml",
        "configs/paper/02_deployment_ablation.toml",
        "configs/paper/03_partner_selection.toml",
        "configs/paper/04_betrayal_adaptation.toml",
        "configs/paper/05a_alpha_sweep.toml",
        "configs/paper/05b_prior_factorial.toml",
        "configs/paper/05c_forgiveness.toml",
        "configs/diagnostics/h0_policy_openness/shallow_binary.toml",
        "configs/diagnostics/h0_policy_openness/graded_choice.toml",
        "configs/diagnostics/h0_policy_openness/graded_betrayal.toml",
        "configs/diagnostics/h1_model_fitness/reliability_vs_reward.toml",
        "configs/diagnostics/h1_model_fitness/reliability_vs_reward_confirm.toml",
        "configs/diagnostics/h1_model_fitness/reliability_spine_graded_reward_matched_diagnostic.toml",
        "configs/diagnostics/h2_deployment/lesion_open_regime.toml",
        "configs/diagnostics/h3_locality/global_beta_focal_switch_probe.toml",
        "configs/diagnostics/h4_social_allocation/partner_choice.toml",
        "configs/diagnostics/h5_timescale_volatility/betrayal_choice.toml",
        "configs/diagnostics/h6_perturbation/perturbation_betrayal.toml",
        "configs/diagnostics/h6_perturbation/perturbation_dynamics.toml",
        "configs/diagnostics/h6_perturbation/affect_sensitivity.toml",
        "configs/diagnostics/smoke/trust_smoke.toml",
        "configs/demo/01_predictability_value.toml",
        "configs/demo/02_deployment_ablation.toml",
        "configs/demo/03_partner_selection.toml",
        "configs/demo/04_betrayal_adaptation.toml",
        "configs/demo/05a_alpha_sweep.toml",
        "configs/demo/05b_prior_factorial.toml",
        "configs/demo/05c_forgiveness.toml",
    ]
    assert not (REPO_ROOT / "experiments" / "trust" / "hypotheses").exists()
    for raw_path in expected:
        path = REPO_ROOT / raw_path
        assert path.exists(), raw_path
        assert load_experiment_specs(path), raw_path


def test_public_paper_and_demo_configs_are_graded_only():
    public_configs = [
        *sorted((REPO_ROOT / "configs" / "paper").glob("*.toml")),
        *sorted((REPO_ROOT / "configs" / "demo").glob("*.toml")),
    ]
    assert public_configs
    for path in public_configs:
        payload = path.read_text(encoding="utf-8")
        assert 'payoff = "binary"' not in payload, str(path.relative_to(REPO_ROOT))
        assert 'payoff = "graded"' in payload, str(path.relative_to(REPO_ROOT))


def test_removed_script_surface_stays_out_of_supported_cli():
    primary_scripts = {
        "experiment/run.py",
        "experiment/inspect.py",
        "analysis/analyze.py",
    }
    retained_diagnostic_scripts = {
        "analysis/summarize.py",
        "analysis/visualize.py",
        "analysis/model_comparison.py",
        "analysis/phenotype_artifacts.py",
    }
    top_level_scripts = {path.name for path in (REPO_ROOT / "scripts").glob("*.py")}
    all_scripts = {str(path.relative_to(REPO_ROOT / "scripts")) for path in (REPO_ROOT / "scripts").rglob("*.py")}
    cli_doc = (REPO_ROOT / "docs" / "experiments" / "running.md").read_text()

    assert top_level_scripts == set()
    assert primary_scripts <= all_scripts
    assert retained_diagnostic_scripts <= all_scripts
    assert "experiment/smoke.py" not in all_scripts
    assert "experiment/paper.py" not in all_scripts
    assert "experiment/preliminary.py" not in all_scripts
    assert "benchmark/run.py" not in all_scripts
    assert "benchmark/analyze.py" not in all_scripts
    for script_name in primary_scripts:
        assert script_name in cli_doc


def test_run_cli_is_public_experiment_running_help_surface():
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "experiment" / "run.py"), "--help"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "--config" in result.stdout
    assert "--dry-run" in result.stdout

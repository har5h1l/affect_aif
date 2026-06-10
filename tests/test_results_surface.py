import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


PUBLIC_RESULT_DIRS = [
    REPO_ROOT / "results/paper/01_predictability_value",
    REPO_ROOT / "results/paper/02_deployment_ablation",
    REPO_ROOT / "results/paper/03_partner_selection",
    REPO_ROOT / "results/paper/04_betrayal_adaptation",
    REPO_ROOT / "results/paper/05a_alpha_sweep",
    REPO_ROOT / "results/paper/05b_prior_factorial",
    REPO_ROOT / "results/paper/05c_forgiveness",
]

PUBLIC_DIAGNOSTIC_DIRS = [
    REPO_ROOT / "results/diagnostics/policy_openness",
    REPO_ROOT / "results/diagnostics/deployment",
    REPO_ROOT / "results/diagnostics/locality",
    REPO_ROOT / "results/diagnostics/model_fitness",
    REPO_ROOT / "results/diagnostics/social_allocation",
]

PUBLIC_FUTURE_DIRS = [
    REPO_ROOT / "results/future/mixed_volatility",
]


REQUIRED_MANIFEST_FIELDS = {
    "name",
    "category",
    "status",
    "config_paths",
    "source_run_paths",
    "raw_results_policy",
    "tracked_summary_files",
    "paper_use",
}


def test_public_paper_result_directories_have_required_artifacts():
    for result_dir in PUBLIC_RESULT_DIRS:
        assert (result_dir / "README.md").exists(), result_dir
        manifest_path = result_dir / "manifest.json"
        assert manifest_path.exists(), result_dir
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert REQUIRED_MANIFEST_FIELDS <= set(manifest), result_dir
        assert manifest["category"] == "paper"
        assert manifest["tracked_summary_files"], result_dir
        for relative_path in manifest["tracked_summary_files"]:
            assert (result_dir / relative_path).exists(), result_dir / relative_path


def test_raw_result_files_are_not_tracked_in_public_scaffold():
    for result_dir in PUBLIC_RESULT_DIRS:
        assert not (result_dir / "results.csv").exists(), result_dir
        assert not (result_dir / "results_partial.csv").exists(), result_dir
        assert not (result_dir / "checkpoint_manifest.json").exists(), result_dir


def test_public_diagnostic_result_directories_have_required_artifacts():
    for result_dir in PUBLIC_DIAGNOSTIC_DIRS:
        assert (result_dir / "README.md").exists(), result_dir
        manifest_path = result_dir / "manifest.json"
        assert manifest_path.exists(), result_dir
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert REQUIRED_MANIFEST_FIELDS <= set(manifest), result_dir
        assert manifest["category"] == "diagnostic"
        assert manifest["tracked_summary_files"], result_dir
        for relative_path in manifest["tracked_summary_files"]:
            assert (result_dir / relative_path).exists(), result_dir / relative_path


def test_public_future_result_directories_have_required_artifacts():
    for result_dir in PUBLIC_FUTURE_DIRS:
        assert (result_dir / "README.md").exists(), result_dir
        manifest_path = result_dir / "manifest.json"
        assert manifest_path.exists(), result_dir
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert REQUIRED_MANIFEST_FIELDS <= set(manifest), result_dir
        assert manifest["category"] == "future"
        assert manifest["paper_use"] == "not_paper_evidence"
        assert manifest["tracked_summary_files"], result_dir
        for relative_path in manifest["tracked_summary_files"]:
            assert (result_dir / relative_path).exists(), result_dir / relative_path


def test_paper_result_manifests_point_to_current_configs():
    suite_manifest = json.loads((REPO_ROOT / "results/paper/manifest.json").read_text(encoding="utf-8"))
    assert [section["slug"] for section in suite_manifest["sections"]] == [
        "01_predictability_value",
        "02_deployment_ablation",
        "03_partner_selection",
        "04_betrayal_adaptation",
        "05a_alpha_sweep",
        "05b_prior_factorial",
        "05c_forgiveness",
    ]
    for result_dir in PUBLIC_RESULT_DIRS:
        manifest = json.loads((result_dir / "manifest.json").read_text(encoding="utf-8"))
        assert all(path.startswith("configs/paper/") for path in manifest["config_paths"])
        assert all(path.startswith("results/paper/") for path in manifest["source_run_paths"])
        payload = json.dumps(manifest)
        assert "configs/paper_reproduce" not in payload
        assert "results/exp_" not in payload
        assert "results/log_surprisal_" not in payload
        assert manifest["raw_results_policy"] == "gitignored_retained_locally_and_on_server"


def test_diagnostic_result_manifests_point_to_current_configs():
    for result_dir in PUBLIC_DIAGNOSTIC_DIRS:
        manifest = json.loads((result_dir / "manifest.json").read_text(encoding="utf-8"))
        assert all(path.startswith("configs/diagnostics/") for path in manifest["config_paths"])
        assert manifest["paper_use"] == "not_paper_evidence"


def test_future_result_manifests_point_to_future_configs():
    for result_dir in PUBLIC_FUTURE_DIRS:
        manifest = json.loads((result_dir / "manifest.json").read_text(encoding="utf-8"))
        assert all(path.startswith("configs/future/") for path in manifest["config_paths"])
        assert all(path.startswith("results/future/") for path in manifest["source_run_paths"])
        assert manifest["paper_use"] == "not_paper_evidence"


def test_raw_and_archive_are_gitignored():
    paths = [
        "results/paper/05a_alpha_sweep/raw/results.csv",
        "results/paper/01_predictability_value/raw/predictability_value/predictability_value/results.csv",
        "results/archive/pre_fix_h0_h5_20260517_w2/run.log",
    ]
    for path in paths:
        subprocess.run(["git", "check-ignore", "-q", path], cwd=REPO_ROOT, check=True)

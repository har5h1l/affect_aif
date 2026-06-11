import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _notebook_text(path: Path) -> str:
    payload = json.loads(path.read_text())
    return "\n".join("".join(cell.get("source", "")) for cell in payload.get("cells", []))


def _notebook_code_cell(path: Path, needle: str) -> str:
    payload = json.loads(path.read_text())
    for cell in payload.get("cells", []):
        source = "".join(cell.get("source", ""))
        if cell.get("cell_type") == "code" and needle in source:
            return source
    raise AssertionError(f"{path.name} should contain code cell with {needle!r}")


def test_public_notebooks_load_and_use_current_paths():
    notebooks = [
        ROOT / "notebooks" / "demo.ipynb",
        ROOT / "notebooks" / "reproduce.ipynb",
    ]

    for path in notebooks:
        payload = json.loads(path.read_text())
        assert payload["nbformat"] == 4
        assert payload.get("cells")
        text = _notebook_text(path)
        assert "scripts/experiment/run.py" in text
        assert "configs/paper_reproduce" not in text
        assert "configs/benchmark" not in text
        assert "scripts/benchmark" not in text
        assert "binary" not in text.lower()
        assert "/Users/" not in text
        assert "Open In Colab" in text
        assert 'AFFECT_AIF_BRANCH", "master"' in text


def test_reproduce_notebook_is_colab_and_results_aware():
    text = _notebook_text(ROOT / "notebooks" / "reproduce.ipynb")

    assert "Path(\"/content\").exists()" in text
    assert "configs/paper/01_predictability_value.toml" in text
    assert "configs/paper/05a_alpha_sweep.toml" in text
    assert "results/paper/01_predictability_value/raw/predictability_value/predictability_value/results.csv" in text
    assert "results/paper/05a_alpha_sweep/raw/results.csv" in text
    assert "scripts/analysis/phenotype_artifacts.py" in text
    assert "google.colab" in text
    assert "drive.mount" in text
    assert "RUN_EXPERIMENTS = True" in text
    assert "MATERIALIZE_RESULTS = True" in text
    assert "RUN_FULL" not in text
    assert "Skipping missing" not in text
    assert "run_required" in text
    assert "shutil.rmtree" in text


def test_demo_notebook_runs_demo_configs_and_analysis():
    text = _notebook_text(ROOT / "notebooks" / "demo.ipynb")

    assert "Run this notebook from the affect_aif repo root" not in text
    assert "detect_accelerator" in text
    assert "SELECTED_DEMOS" in text
    assert "run_demo(" in text
    assert "show_demo(" in text
    assert "guided public walkthrough" in text
    assert "What To Look For" in text
    assert "Appendix-Level Extensions" in text
    assert "mechanism_snapshot" in text
    assert "plot_profile_metrics" in text
    assert "plot_timecourse" in text
    assert "interpretation_card" in text
    assert "configs/demo/01_predictability_value.toml" in text
    assert "configs/demo/02_deployment_ablation.toml" in text
    assert "configs/demo/03_partner_selection.toml" in text
    assert "configs/demo/04_betrayal_adaptation.toml" in text
    assert "configs/demo/05a_alpha_sweep.toml" in text
    assert "configs/demo/05b_prior_factorial.toml" in text
    assert "configs/demo/05c_forgiveness.toml" in text
    assert "RUN_OPTIONAL_DEMOS = True" in text
    assert (
        'SELECTED_DEMOS = ["predictability_value", "deployment_ablation", "partner_selection", '
        '"betrayal_adaptation", "alpha_sweep", "prior_factorial", "forgiveness"]'
    ) in text
    assert "scripts/analysis/analyze.py" in text
    assert 'OUTPUT_ROOT = Path("outputs")' in text
    assert 'DEMO_BATCH_PREFIX = "notebook_demo"' in text
    assert "Predictability-Value Demo: Run And Analyze" in text
    assert "Deployment-Ablation Demo: Run And Analyze" in text
    assert "Partner-Selection Demo: Run And Analyze" in text
    assert "Betrayal-Adaptation Demo: Run And Analyze" in text
    assert "Alpha-Sweep Demo: Run And Analyze" in text
    assert "Appendix-Level Extensions" in text
    assert "Prior-Factorial Demo: Run And Analyze" in text
    assert "Forgiveness Demo: Run And Analyze" in text
    assert text.count("= run_demo(") == 7
    assert text.count("show_demo(") >= 6
    assert text.count("show_appendix_demo(") >= 4


def test_public_notebooks_do_not_store_local_outputs():
    for path in [ROOT / "notebooks" / "demo.ipynb", ROOT / "notebooks" / "reproduce.ipynb"]:
        payload = json.loads(path.read_text())
        for index, cell in enumerate(payload.get("cells", [])):
            if cell.get("cell_type") != "code":
                continue
            assert cell.get("outputs", []) == [], f"{path.name} cell {index} stores execution output"
            assert cell.get("execution_count") is None, f"{path.name} cell {index} stores execution count"


def test_demo_notebook_sanitizes_markdown_repo_urls():
    bootstrap_source = _notebook_code_cell(ROOT / "notebooks" / "demo.ipynb", "def sanitize_repo_url")
    tree = ast.parse(bootstrap_source)
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "sanitize_repo_url"]
    clone_functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "clone_repo"]

    assert functions, "demo bootstrap should sanitize copied Markdown links before git clone"
    assert clone_functions, "demo bootstrap should show git clone diagnostics instead of a bare CalledProcessError"
    assert '(repo_dir / ".git").exists()' in bootstrap_source
    assert "shutil.rmtree(repo_dir)" in bootstrap_source
    assert "capture_output=True" in bootstrap_source
    assert "Git clone failed." in bootstrap_source
    module = ast.Module(body=functions, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace: dict[str, object] = {}
    exec(compile(module, "demo-bootstrap-sanitizer", "exec"), namespace)
    sanitize_repo_url = namespace["sanitize_repo_url"]

    assert sanitize_repo_url("https://github.com/har5h1l/affect_aif.git") == "https://github.com/har5h1l/affect_aif.git"
    assert sanitize_repo_url("<https://github.com/har5h1l/affect_aif.git>") == "https://github.com/har5h1l/affect_aif.git"
    assert (
        sanitize_repo_url("[https://github.com/har5h1l/affect_aif.git](https://github.com/har5h1l/affect_aif.git)")
        == "https://github.com/har5h1l/affect_aif.git"
    )


def test_demo_notebook_prefers_existing_repo_root_before_clone():
    bootstrap_source = _notebook_code_cell(ROOT / "notebooks" / "demo.ipynb", "def find_repo_root")
    tree = ast.parse(bootstrap_source)
    functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}

    assert "find_repo_root" in functions
    assert "existing_root = find_repo_root(Path.cwd())" in bootstrap_source
    assert "if existing_root is not None:" in bootstrap_source
    assert "os.chdir(existing_root)" in bootstrap_source
    assert "scripts/experiment/run.py" in bootstrap_source

    module = ast.Module(body=[functions["find_repo_root"]], type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {"Path": Path}
    exec(compile(module, "demo-bootstrap-root-finder", "exec"), namespace)
    find_repo_root = namespace["find_repo_root"]

    assert find_repo_root(ROOT) == ROOT
    assert find_repo_root(ROOT / "notebooks") == ROOT


def test_reproduce_notebook_is_split_by_paper_experiment():
    text = _notebook_text(ROOT / "notebooks" / "reproduce.ipynb")

    for heading in [
        "Predictability-Value: Run And Analyze",
        "Deployment Ablation: Run And Analyze",
        "Partner Selection: Run And Analyze",
        "Betrayal Adaptation: Run And Analyze",
        "Exp A Alpha Sweep: Run And Analyze",
        "Exp B Prior Factorial: Run And Analyze",
        "Exp C Forgiveness: Run And Analyze",
    ]:
        assert heading in text


def test_manuscript_surface_does_not_expose_binary_regime():
    manuscript_paths = [
        path
        for path in (ROOT / "docs" / "manuscript").rglob("*")
        if path.is_file() and path.suffix.lower() not in {".pdf", ".png", ".aux"}
    ]
    assert manuscript_paths
    for path in manuscript_paths:
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        assert "binary" not in text, str(path.relative_to(ROOT))

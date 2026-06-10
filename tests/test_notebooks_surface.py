import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _notebook_text(path: Path) -> str:
    payload = json.loads(path.read_text())
    return "\n".join("".join(cell.get("source", "")) for cell in payload.get("cells", []))


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

    assert "configs/demo/01_predictability_value.toml" in text
    assert "configs/demo/02_deployment_ablation.toml" in text
    assert "configs/demo/03_partner_selection.toml" in text
    assert "configs/demo/04_betrayal_adaptation.toml" in text
    assert "configs/demo/05a_alpha_sweep.toml" in text
    assert "configs/demo/05b_prior_factorial.toml" in text
    assert "configs/demo/05c_forgiveness.toml" in text
    assert "RUN_OPTIONAL_DEMOS = False" in text
    assert "Set RUN_OPTIONAL_DEMOS = True" in text
    assert "scripts/analysis/analyze.py" in text
    assert "outputs/notebook_demo" in text
    assert "Predictability-Value Demo: Run And Analyze" in text
    assert "Deployment-Ablation Demo: Run And Analyze" in text
    assert "Partner-Selection Demo: Run And Analyze" in text
    assert "Betrayal-Adaptation Demo: Run And Analyze" in text
    assert "Alpha-Sweep Demo: Run And Analyze" in text
    assert "Optional Prior-Factorial Demo: Run And Analyze" in text
    assert "Optional Forgiveness Demo: Run And Analyze" in text


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

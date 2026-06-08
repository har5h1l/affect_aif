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
        assert "/Users/" not in text
        assert "Open In Colab" in text
        assert 'AFFECT_AIF_BRANCH", "main"' in text


def test_reproduce_notebook_is_colab_and_results_aware():
    text = _notebook_text(ROOT / "notebooks" / "reproduce.ipynb")

    assert "Path(\"/content\").exists()" in text
    assert "configs/paper/alpha_sweep.toml" in text
    assert "results/paper/alpha_sweep/raw/results.csv" in text
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

    assert "configs/demo/model_fitness.toml" in text
    assert "configs/demo/betrayal_adaptation.toml" in text
    assert "configs/demo/alpha_sweep.toml" in text
    assert "scripts/analysis/analyze.py" in text
    assert "outputs/notebook_demo" in text

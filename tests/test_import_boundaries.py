from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_aif_does_not_import_higher_layers():
    forbidden = (
        "tasks.",
        "experiments.",
        "analysis.",
        "trust.",
        "env.",
        "experiment.",
    )
    offenders = []
    for path in (ROOT / "aif").rglob("*.py"):
        text = path.read_text()
        for token in forbidden:
            if f"import {token}" in text or f"from {token}" in text:
                offenders.append(f"{path.relative_to(ROOT)} imports {token}")
    assert offenders == []


def test_tasks_do_not_import_higher_layers():
    forbidden = ("experiments.", "analysis.")
    offenders = []
    for path in (ROOT / "tasks").rglob("*.py"):
        text = path.read_text()
        for token in forbidden:
            if f"import {token}" in text or f"from {token}" in text:
                offenders.append(f"{path.relative_to(ROOT)} imports {token}")
    assert offenders == []


def test_trust_baselines_live_under_task_evaluation():
    from tasks.trust.evaluation.baselines import RandomAgent

    assert RandomAgent is not None

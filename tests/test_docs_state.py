import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_docs_state_steering_wheel_exists():
    required = [
        "docs/state/README.md",
        "docs/state/current/mission.md",
        "docs/state/current/next_runs.md",
        "docs/state/current/blockers.md",
        "docs/state/decisions/architecture.md",
        "docs/state/decisions/experiments.md",
    ]
    missing = [path for path in required if not (ROOT / path).exists()]
    assert missing == []


def test_current_docs_do_not_use_old_hypothesis_story():
    paths = [
        ROOT / "README.md",
        ROOT / "AGENTS.md",
        ROOT / "docs/theory/goals.md",
        ROOT / "docs/theory/hypotheses.md",
    ]
    forbidden = ["affect compensates for shallow planning", "deep planner as gold standard"]
    offenders = []
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text().lower()
        for phrase in forbidden:
            if phrase in text:
                offenders.append(f"{path.relative_to(ROOT)}: {phrase}")
    assert offenders == []


def test_top_level_doc_links_exist():
    checked = [
        ROOT / "README.md",
        ROOT / "AGENTS.md",
        ROOT / "scripts" / "README.md",
        ROOT / "docs" / "operations" / "cli.md",
    ]
    pattern = re.compile(r"\[[^\]]+\]\(([^)]+\.md)(?:#[^)]+)?\)")
    missing = []
    for path in checked:
        text = path.read_text()
        for match in pattern.finditer(text):
            target = match.group(1)
            if target.startswith("http"):
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                missing.append(f"{path.relative_to(ROOT)} -> {target}")
    assert missing == []

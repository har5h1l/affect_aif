import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_docs_state_steering_wheel_exists():
    required = [
        "docs/active/README.md",
        "docs/active/state.md",
        "docs/active/progress.md",
        "docs/active/blockers.md",
        "docs/overview/README.md",
        "docs/overview/core/pomdp.md",
        "docs/overview/core/affective_precision.md",
        "docs/overview/core/hypotheses.md",
        "docs/experiments/README.md",
        "docs/experiments/running.md",
        "docs/experiments/configs.md",
        "docs/experiments/paper.md",
        "docs/experiments/diagnostics.md",
        "docs/overview/extensions/future.md",
        "docs/results/README.md",
        "docs/results/paper.md",
        "docs/results/diagnostics.md",
        "docs/results/archive.md",
        "docs/manuscript/README.md",
    ]
    missing = [path for path in required if not (ROOT / path).exists()]
    assert missing == []


def test_top_level_doc_links_exist():
    checked = [
        ROOT / "README.md",
        ROOT / "AGENTS.md",
        ROOT / "scripts" / "README.md",
        ROOT / "docs" / "experiments" / "running.md",
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

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


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

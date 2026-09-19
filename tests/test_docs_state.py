import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_public_docs_route_exists():
    required = [
        "docs/guide/README.md",
        "docs/guide/reproduce.md",
        "docs/guide/configs.md",
        "docs/guide/notebooks.md",
        "docs/guide/running.md",
        "docs/guide/diagnostics.md",
        "docs/results/README.md",
        "docs/results/findings.md",
        "docs/results/provenance.md",
        "docs/results/diagnostics.md",
        "docs/manuscript/main.tex",
    ]
    missing = [path for path in required if not (ROOT / path).exists()]
    assert missing == []


def test_top_level_doc_links_exist():
    checked = [
        ROOT / "README.md",
        ROOT / "docs" / "README.md",
        ROOT / "scripts" / "README.md",
        *sorted((ROOT / "docs" / "guide").glob("*.md")),
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


def test_appendix_protocol_round_counts_match_current_paper_configs():
    appendix = (ROOT / "docs/manuscript/main.tex").read_text()

    assert "Locality probe & graded partner choice & 200 & 30" in appendix
    assert "Locality probe & graded partner choice & 100 & 30" not in appendix

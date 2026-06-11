from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_model_hypotheses_lists_current_hypothesis_spine():
    manifest = ROOT / "docs/overview/core/hypotheses.md"
    assert manifest.exists()
    text = manifest.read_text()
    for label in ["H0", "H1", "H2", "H3", "H4", "H5", "H6"]:
        assert f"| {label} " in text or f"## {label}" in text

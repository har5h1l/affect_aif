from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_experiment_manifest_lists_current_hypotheses():
    manifest = ROOT / "docs/experiments/manifest.md"
    assert manifest.exists()
    text = manifest.read_text()
    for label in ["H1", "H2", "H3", "H4", "H5", "H6", "H7", "E1", "E2"]:
        assert f"| {label} " in text or f"## {label}" in text

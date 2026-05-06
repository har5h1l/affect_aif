"""Minimal report rendering helpers."""

from __future__ import annotations

from pathlib import Path


def write_markdown_summary(path: str | Path, title: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(f"# {title}\n", encoding="utf-8")

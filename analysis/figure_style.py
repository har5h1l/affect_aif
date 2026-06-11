"""Matplotlib defaults for manuscript figure PDFs."""

from __future__ import annotations

import matplotlib.pyplot as plt


def apply_manuscript_figure_style() -> None:
    """Use TrueType PDF fonts so Greek symbols (e.g. beta) survive LaTeX inclusion."""
    plt.rcParams.update(
        {
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "font.size": 9,
            "axes.titlesize": 9,
            "axes.labelsize": 8,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 8,
        }
    )

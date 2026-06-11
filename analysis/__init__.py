"""Analysis helpers for experiment outputs."""

from importlib import import_module

__all__ = ["build_run_gifs", "load_results"]


def __getattr__(name: str):
    if name in __all__:
        visualization = import_module("analysis.visualization")
        return getattr(visualization, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

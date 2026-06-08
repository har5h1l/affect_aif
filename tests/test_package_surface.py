import importlib
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 import fallback
    import tomli as tomllib

from setuptools import find_packages

ROOT = Path(__file__).resolve().parents[1]


def test_current_runtime_packages_are_discovered_by_pyproject():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())
    include = pyproject["tool"]["setuptools"]["packages"]["find"]["include"]
    assert "tasks*" in include
    assert "experiments*" in include
    assert "benchmarks*" not in include
    assert "trust*" not in include
    assert "env*" not in include
    assert "experiment*" not in include
    packages = set(find_packages(where=str(ROOT), include=include))
    assert "tasks.trust" in packages
    assert "tasks.trust.envs" in packages
    assert "tasks.trust.evaluation" in packages
    assert "experiments.trust" in packages
    assert "experiments.multifocal" in packages
    assert "benchmark" not in packages

    importlib.import_module("tasks.trust.affect")
    importlib.import_module("tasks.trust.pomdp")
    importlib.import_module("tasks.trust.runtime")

from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 compatibility
    import tomli as tomllib

from setuptools import find_packages

ROOT = Path(__file__).resolve().parents[1]


def test_current_runtime_packages_are_discovered_by_pyproject():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())
    include = pyproject["tool"]["setuptools"]["packages"]["find"]["include"]
    assert "aif*" in include
    assert "trust*" in include
    packages = set(find_packages(where=str(ROOT), include=include))
    assert "aif" in packages
    assert "aif.affect" in packages
    assert "trust" in packages

from __future__ import annotations

import ast
from copy import deepcopy
from pathlib import Path

import numpy as np
import pytest

import aif
from aif import construct_policies, log_stable, obj_array, softmax
from aif import runtime as aif_runtime


ROOT = Path(__file__).resolve().parents[1]
AIF_DIR = ROOT / "aif"
AGENT_INFERENCE_DIR = ROOT / "agent" / "inference"
MOVED_MODULES = ("backend", "efe", "learning", "maths", "policies", "runtime", "utils")


class _InferenceImportRewriter(ast.NodeTransformer):
    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.ImportFrom:
        if node.module and node.module.startswith("agent.inference."):
            rewritten = "aif." + node.module.removeprefix("agent.inference.")
            return ast.copy_location(
                ast.ImportFrom(module=rewritten, names=node.names, level=node.level),
                node,
            )
        return node


def _parse_module(path: Path) -> ast.Module:
    return ast.parse(path.read_text(), filename=str(path))


def _find_function(module_ast: ast.Module, name: str) -> ast.FunctionDef:
    for node in module_ast.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"Function {name!r} not found")


def _normalize_ast(module_ast: ast.Module) -> ast.Module:
    normalized = _InferenceImportRewriter().visit(deepcopy(module_ast))
    return ast.fix_missing_locations(normalized)


def _normalized_source(module_ast: ast.Module) -> str:
    return ast.unparse(_normalize_ast(module_ast))


def _expected_module_source(module_name: str) -> str:
    module_ast = _parse_module(AGENT_INFERENCE_DIR / f"{module_name}.py")
    if module_name == "runtime":
        rollout_ast = _parse_module(AGENT_INFERENCE_DIR / "rollout.py")
        module_ast.body.append(deepcopy(_find_function(rollout_ast, "generate_observation_sequences")))
    return _normalized_source(module_ast)


def _actual_module_source(module_name: str) -> str:
    return _normalized_source(_parse_module(AIF_DIR / f"{module_name}.py"))


@pytest.mark.parametrize("module_name", MOVED_MODULES)
def test_moved_modules_match_normalized_source_contract(module_name: str):
    assert _actual_module_source(module_name) == _expected_module_source(module_name)


def test_aif_top_level_surface_is_minimal_and_explicit():
    assert aif.__all__ == ["softmax", "log_stable", "obj_array", "construct_policies"]

    namespace = {}
    exec("from aif import *", namespace)
    exported = {name for name in namespace if not name.startswith("__")}
    assert exported == set(aif.__all__)
    assert aif.softmax is softmax
    assert aif.log_stable is log_stable
    assert aif.obj_array is obj_array
    assert aif.construct_policies is construct_policies


def test_top_level_reexports_smoke():
    probs = softmax(np.array([0.0, 1.0]), backend="numpy")
    np.testing.assert_allclose(probs.sum(), 1.0)
    np.testing.assert_array_equal(obj_array(2).shape, (2,))
    assert np.isfinite(log_stable(np.array([0.0]), backend="numpy")).all()
    assert construct_policies([2, 3], planning_horizon=2, max_policies=5, rng=np.random.default_rng(0)).shape == (
        5,
        2,
        2,
    )


def test_runtime_smoke():
    np.testing.assert_array_equal(
        aif_runtime.generate_observation_sequences(4),
        np.array(
            [
                [0, 0, 0],
                [0, 0, 1],
                [0, 1, 0],
                [0, 1, 1],
                [1, 0, 0],
                [1, 0, 1],
                [1, 1, 0],
                [1, 1, 1],
            ]
        ),
    )

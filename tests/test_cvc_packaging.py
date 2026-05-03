"""Tests for submission-shaped local CvC policy packaging."""

import importlib
import json

from benchmarks.cvc.packaging import write_policy_bundle


def test_cvc_package_imports_without_runtime_execution():
    module = importlib.import_module("benchmarks.cvc.packaging")
    assert module is not None


def test_write_policy_bundle_uses_same_policy_spec_shape_for_local_and_future_submit(tmp_path):
    bundle_dir = tmp_path / "bundle"
    spec = "class=benchmarks.cvc.policy.TeammateReliabilityPolicy"

    write_policy_bundle(bundle_dir, policy_spec=spec)

    payload = json.loads((bundle_dir / "policy_spec.json").read_text())
    assert payload["class_path"] == "benchmarks.cvc.policy.TeammateReliabilityPolicy"
    assert payload["init_kwargs"] == {}

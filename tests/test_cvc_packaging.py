"""Tests for submission-shaped local CvC policy packaging."""

import json

from affect_aif.benchmark.cvc_packaging import write_policy_bundle


def test_write_policy_bundle_uses_same_policy_spec_shape_for_local_and_future_submit(tmp_path):
    bundle_dir = tmp_path / "bundle"
    spec = "class=affect_aif.benchmark.cvc_policy.TeammateReliabilityPolicy"

    write_policy_bundle(bundle_dir, policy_spec=spec)

    payload = json.loads((bundle_dir / "policy_spec.json").read_text())
    assert payload["class_path"] == "affect_aif.benchmark.cvc_policy.TeammateReliabilityPolicy"
    assert payload["init_kwargs"] == {}

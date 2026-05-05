from __future__ import annotations

import numpy as np

from experiments.trust.config import ExperimentConfig
from tasks.trust.pomdp import build_trust_pomdp_template


def test_binary_model_exports_pymdp_bundle_shapes() -> None:
    bundle = build_trust_pomdp_template(ExperimentConfig(payoff_mode="binary"), planning_horizon=1)

    assert len(bundle.A) == 2
    assert len(bundle.B) == 3
    assert bundle.A[0].shape == (2, 4, 3, 2)
    assert bundle.A[1].shape == (4, 4, 3, 2)
    assert bundle.B[0].shape == (4, 4, 1)
    assert bundle.B[1].shape == (3, 3, 2)
    assert bundle.B[2].shape == (2, 2, 2)
    assert bundle.control_fac_idx == (1, 2)


def test_binary_model_pymdp_bundle_is_normalized() -> None:
    bundle = build_trust_pomdp_template(ExperimentConfig(payoff_mode="binary"), planning_horizon=1)

    for A_m in bundle.A:
        np.testing.assert_allclose(A_m.sum(axis=0), 1.0)
    for B_f in bundle.B:
        np.testing.assert_allclose(B_f.sum(axis=0), 1.0)


def test_policies_have_pymdp_shape() -> None:
    bundle = build_trust_pomdp_template(ExperimentConfig(payoff_mode="binary"), planning_horizon=2)

    assert bundle.policies.ndim == 3
    assert bundle.policies.shape[1] == 2
    assert bundle.policies.shape[2] == 3


def test_truncated_pymdp_policies_without_rng_are_deterministic() -> None:
    first = build_trust_pomdp_template(ExperimentConfig(payoff_mode="binary"), planning_horizon=3, max_policies=5)
    second = build_trust_pomdp_template(ExperimentConfig(payoff_mode="binary"), planning_horizon=3, max_policies=5)

    np.testing.assert_array_equal(first.policies, second.policies)


def test_truncated_pymdp_policies_with_seeded_rng_are_reproducible() -> None:
    seed = 123

    first = build_trust_pomdp_template(
        ExperimentConfig(payoff_mode="binary"),
        planning_horizon=3,
        max_policies=5,
        rng=np.random.default_rng(seed),
    )
    second = build_trust_pomdp_template(
        ExperimentConfig(payoff_mode="binary"),
        planning_horizon=3,
        max_policies=5,
        rng=np.random.default_rng(seed),
    )

    np.testing.assert_array_equal(first.policies, second.policies)

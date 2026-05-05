from __future__ import annotations

import jax.numpy as jnp
import numpy as np

from experiments.trust.config import ExperimentConfig
from tasks.trust.pomdp import build_trust_pomdp_template, create_partner_agents, create_pymdp_agent


def test_template_exports_jax_arrays_and_expected_shapes() -> None:
    template = build_trust_pomdp_template(
        ExperimentConfig(payoff_mode="binary", num_partners=4),
        planning_horizon=2,
    )

    assert len(template.A) == 2
    assert len(template.B) == 3
    assert template.A[0].shape == (2, 4, 3, 2)
    assert template.A[1].shape == (4, 4, 3, 2)
    assert template.B[0].shape == (4, 4, 1)
    assert template.B[1].shape == (3, 3, 2)
    assert template.B[2].shape == (2, 2, 2)
    assert template.control_fac_idx == (1, 2)
    assert all(isinstance(array, jnp.ndarray) for array in template.A)
    assert all(isinstance(array, jnp.ndarray) for array in template.B)
    assert all(isinstance(array, jnp.ndarray) for array in template.C)
    assert all(isinstance(array, jnp.ndarray) for array in template.D)
    assert isinstance(template.E, jnp.ndarray)
    assert isinstance(template.policies, jnp.ndarray)


def test_template_preserves_probability_normalization() -> None:
    template = build_trust_pomdp_template(
        ExperimentConfig(payoff_mode="binary", num_partners=4),
        planning_horizon=2,
    )

    for A_m in template.A:
        np.testing.assert_allclose(np.asarray(A_m).sum(axis=0), 1.0)
    for B_f in template.B:
        np.testing.assert_allclose(np.asarray(B_f).sum(axis=0), 1.0)
    np.testing.assert_allclose(np.asarray(template.E).sum(), 1.0)


def test_template_can_create_official_pymdp_agents() -> None:
    template = build_trust_pomdp_template(
        ExperimentConfig(payoff_mode="binary", num_partners=3),
        planning_horizon=1,
    )

    agent = create_pymdp_agent(template, gamma=1.0)
    partner_agents = create_partner_agents(template, num_partners=3, gamma=1.0)

    assert agent.__class__.__module__.startswith("pymdp.")
    assert len(partner_agents) == 3
    assert all(partner.__class__.__module__.startswith("pymdp.") for partner in partner_agents)

from __future__ import annotations

import jax.numpy as jnp
import numpy as np

from experiments.trust.config import ExperimentConfig
from tasks.trust.pomdp import build_trust_pomdp_template, create_pymdp_agent


def test_binary_model_exports_pymdp_bundle_shapes() -> None:
    bundle = build_trust_pomdp_template(ExperimentConfig(payoff_mode="binary"), planning_horizon=1)

    assert len(bundle.A) == 2
    assert len(bundle.B) == 3
    assert bundle.A[0].shape == (2, 4, 3, 2)
    assert bundle.A[1].shape == (4, 4, 3, 2)
    assert bundle.B[0].shape == (4, 4)
    assert bundle.B[1].shape == (3, 3, 2)
    assert bundle.B[2].shape == (2, 2, 2)
    assert bundle.num_controls == (2,)
    assert bundle.B_action_dependencies == ((), (0,), (0,))


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
    assert bundle.policies.shape[2] == 1


def test_graded_policies_match_transition_factor_count_for_pymdp() -> None:
    bundle = build_trust_pomdp_template(
        ExperimentConfig(payoff_mode="graded", assignment_mode="agent_choice"),
        planning_horizon=2,
    )
    agent = create_pymdp_agent(bundle, gamma=1.0)

    assert len(bundle.B) == 3
    assert bundle.policies.shape == (36, 2, 1)
    qs = [jnp.asarray(np.asarray(factor).squeeze()[None, None, :]) for factor in agent.D]
    q_pi, _scores = agent.infer_policies(qs)
    assert np.asarray(q_pi).shape == (1, 36)
    lowered = np.asarray(agent.policies.policy_arr)
    assert lowered.shape == (36, 2, 3)
    assert np.all(lowered[:, :, 1] == lowered[:, :, 2])


def test_graded_horizon_four_has_the_manuscript_policy_count() -> None:
    bundle = build_trust_pomdp_template(
        ExperimentConfig(payoff_mode="graded", assignment_mode="agent_choice"),
        planning_horizon=4,
    )

    assert bundle.num_controls == (6,)
    assert bundle.policies.shape == (6**4, 4, 1)
    combined_candidates = bundle.num_partners * len(bundle.policies)
    assert combined_candidates == 4 * 6**4
    assert np.isclose(np.log(len(bundle.policies)), 7.16703787691222)
    assert np.isclose(np.log(combined_candidates), 8.55333223803211)

import numpy as np

from agent.inference.rollout import gamma_per_policy


def test_gamma_per_policy_uses_inverse_beta_expectation():
    first_partners = np.asarray([0, 1, 0, 1], dtype=int)
    precision_signal = np.asarray([0.5, 2.0], dtype=float)

    gamma_values = gamma_per_policy(
        gamma_base=1.0,
        first_partners=first_partners,
        precision_signal=precision_signal,
    )

    np.testing.assert_allclose(gamma_values, np.asarray([2.0, 0.5, 2.0, 0.5]))

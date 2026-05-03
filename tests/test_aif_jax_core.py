from __future__ import annotations

import jax
import jax.numpy as jnp
import numpy as np
import pytest

import aif


def test_softmax_accepts_jax_array():
    values = jnp.array([1.0, 2.0, 3.0])

    result = aif.softmax(values)

    assert hasattr(result, "shape")
    assert result.shape == (3,)
    assert jnp.isclose(result.sum(), 1.0)


def test_sample_action_accepts_explicit_jax_key():
    q_pi = jnp.array([0.25, 0.75])
    key = jax.random.PRNGKey(0)

    action = aif.sample_action(q_pi, rng=key)

    assert int(action) in {0, 1}


def test_sample_action_requires_explicit_key_for_q_pi_path():
    q_pi = jnp.array([0.25, 0.75])

    with pytest.raises(ValueError, match="explicit JAX PRNG key"):
        aif.sample_action(q_pi)


def test_softmax_numpy_and_jax_parity():
    values = np.array([0.1, 0.2, 0.3])

    np_result = np.asarray(aif.softmax(values))
    jax_result = np.asarray(aif.softmax(jnp.asarray(values)))

    np.testing.assert_allclose(np_result, jax_result)

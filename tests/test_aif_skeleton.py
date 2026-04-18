from __future__ import annotations

import numpy as np

from agent.inference import backend as old_backend
from agent.inference import efe as old_efe
from agent.inference import learning as old_learning
from agent.inference import maths as old_maths
from agent.inference import policies as old_policies_mod
from agent.inference import rollout as old_rollout
from agent.inference import runtime as old_runtime
from agent.inference import utils as old_utils

from aif import construct_policies
from aif import log_stable, obj_array, softmax
from aif import backend as new_backend
from aif import efe as new_efe
from aif import learning as new_learning
from aif import runtime as new_runtime
from aif import utils as new_utils


def test_maths_softmax_and_log_stable_match_old_module():
    x = np.array([1.0, 2.0, 3.0])
    np.testing.assert_allclose(softmax(x), old_maths.softmax(x))
    np.testing.assert_allclose(log_stable(x), old_maths.log_stable(x))


def test_utils_obj_array_matches_old_module():
    new_arr = obj_array(3)
    old_arr = old_utils.obj_array(3)

    assert new_arr.dtype == old_arr.dtype == object
    assert new_arr.shape == old_arr.shape == (3,)


def test_backend_get_xp_numpy_matches_old_module():
    assert new_backend.get_xp("numpy") is old_backend.get_xp("numpy")


def test_policies_construct_policies_matches_old_module_on_seeded_input():
    rng_new = np.random.default_rng(123)
    rng_old = np.random.default_rng(123)
    new_value = construct_policies([2, 3], planning_horizon=2, max_policies=5, rng=rng_new)
    old_value = old_policies_mod.construct_policies([2, 3], planning_horizon=2, max_policies=5, rng=rng_old)
    np.testing.assert_array_equal(new_value, old_value)


def test_efe_compute_expected_free_energy_matches_old_module():
    A = np.empty(1, dtype=object)
    A[0] = np.array([[0.8, 0.2], [0.2, 0.8]])
    B = np.empty(1, dtype=object)
    B[0] = np.stack(
        [
            np.array([[0.9, 0.1], [0.1, 0.9]]),
            np.array([[0.7, 0.3], [0.3, 0.7]]),
        ],
        axis=-1,
    )
    C = np.empty(1, dtype=object)
    C[0] = np.array([0.1, 0.9])
    qs = np.empty(1, dtype=object)
    qs[0] = np.array([0.6, 0.4])
    policy = np.array([0, 1], dtype=int)

    new_value = new_efe.compute_expected_free_energy(A, B, C, qs, policy)
    old_value = old_efe.compute_expected_free_energy(A, B, C, qs, policy)
    assert new_value == old_value


def test_learning_update_likelihood_dirichlet_matches_old_module():
    qA = np.empty(1, dtype=object)
    qA[0] = np.array([[1.0, 2.0], [3.0, 4.0]])
    qs = np.empty(1, dtype=object)
    qs[0] = np.array([0.25, 0.75])
    obs = [1]

    new_value = new_learning.update_likelihood_dirichlet(qA, obs, qs, learning_rate=2.0)
    old_value = old_learning.update_likelihood_dirichlet(qA, obs, qs, learning_rate=2.0)
    np.testing.assert_array_equal(new_value[0], old_value[0])


def test_runtime_resolve_device_cpu_matches_old_module():
    new_device = new_runtime.resolve_device("cpu")
    old_device = old_runtime.resolve_device("cpu")

    assert type(new_device) is type(old_device)
    assert new_device.platform == old_device.platform
    assert str(new_device) == str(old_device)


def test_runtime_generate_observation_sequences_matches_old_rollout_helper():
    new_value = new_runtime.generate_observation_sequences(4)
    old_value = old_rollout.generate_observation_sequences(4)
    np.testing.assert_array_equal(new_value, old_value)

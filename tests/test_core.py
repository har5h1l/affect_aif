import numpy as np

from affect_aif.core.control import construct_policies
from affect_aif.core.maths import entropy, normalize, softmax


def test_softmax_sums_to_one():
    values = softmax(np.array([1.0, 2.0, 3.0]), backend="numpy")
    assert np.isclose(values.sum(), 1.0)


def test_softmax_temperature():
    cold = softmax(np.array([0.0, 1.0]), tau=0.1, backend="numpy")
    hot = softmax(np.array([0.0, 1.0]), tau=2.0, backend="numpy")
    assert cold[1] > hot[1]


def test_entropy_uniform_is_log_n():
    value = entropy(np.array([0.25, 0.25, 0.25, 0.25]), backend="numpy")
    assert np.isclose(value, np.log(4.0))


def test_normalize():
    values = normalize(np.array([2.0, 3.0]), axis=0, backend="numpy")
    assert np.allclose(values, np.array([0.4, 0.6]))


def test_construct_policies_binary_horizon_two():
    policies = construct_policies([2], planning_horizon=2)
    assert policies.shape == (4, 2)
    assert {tuple(row) for row in policies.tolist()} == {(0, 0), (0, 1), (1, 0), (1, 1)}

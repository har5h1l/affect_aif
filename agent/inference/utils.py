"""Construction helpers for object-array POMDP representations."""

from __future__ import annotations

from itertools import product

import numpy as np

from agent.inference.maths import normalize


def obj_array(num_elements: int) -> np.ndarray:
    """Create a NumPy object array."""

    return np.empty(num_elements, dtype=object)


def obj_array_zeros(shape_list: list[tuple[int, ...]]) -> np.ndarray:
    """Create an object array filled with zero arrays."""

    arr = obj_array(len(shape_list))
    for idx, shape in enumerate(shape_list):
        arr[idx] = np.zeros(shape, dtype=float)
    return arr


def obj_array_uniform(shape_list: list[int]) -> np.ndarray:
    """Create an object array of uniform categorical distributions."""

    arr = obj_array(len(shape_list))
    for idx, size in enumerate(shape_list):
        arr[idx] = np.full(size, 1.0 / size, dtype=float)
    return arr


def random_A_matrix(
    num_obs: list[int],
    num_states: list[int],
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Generate random column-normalized observation likelihood arrays."""

    rng = rng or np.random.default_rng()
    arr = obj_array(len(num_obs))
    for modality, obs_size in enumerate(num_obs):
        shape = (obs_size, *num_states)
        sample = rng.random(shape)
        arr[modality] = normalize(sample, axis=0, backend="numpy")
    return arr


def random_B_matrix(
    num_states: list[int],
    num_controls: list[int],
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Generate random column-normalized transition arrays."""

    rng = rng or np.random.default_rng()
    arr = obj_array(len(num_states))
    for factor, state_size in enumerate(num_states):
        control_size = num_controls[min(factor, len(num_controls) - 1)]
        sample = rng.random((state_size, state_size, control_size))
        for action in range(control_size):
            sample[:, :, action] = normalize(sample[:, :, action], axis=0, backend="numpy")
        arr[factor] = sample
    return arr


def onehot(index: int, size: int) -> np.ndarray:
    """Construct a one-hot vector."""

    out = np.zeros(size, dtype=float)
    out[index] = 1.0
    return out


def enumerate_factorized_actions(num_controls: list[int]) -> list[tuple[int, ...]]:
    """Enumerate all instantaneous actions for factorized control."""

    return list(product(*[range(n) for n in num_controls]))

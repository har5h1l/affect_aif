"""Expected free energy helpers for non-JAX paths."""

from __future__ import annotations

import numpy as np

from aif.maths import entropy, normalize, spm_dot


def _precompute_ambiguity(A: np.ndarray) -> list[np.ndarray]:
    ambiguity = []
    for modality in range(len(A)):
        a_m = np.asarray(A[modality], dtype=float)
        hidden_shape = a_m.shape[1:]
        flat = a_m.reshape(a_m.shape[0], -1)
        ent = np.asarray(entropy(flat, backend="numpy")).reshape(hidden_shape)
        ambiguity.append(ent)
    return ambiguity


def compute_expected_free_energy(
    A: np.ndarray,
    B: np.ndarray,
    C: np.ndarray,
    qs: np.ndarray,
    policy: np.ndarray,
    use_utility: bool = True,
    use_information_gain: bool = True,
) -> float:
    """Compute standard expected free energy for a single policy."""

    state_belief = np.asarray(qs[0], dtype=float).copy()
    total = 0.0
    ambiguity = _precompute_ambiguity(A)

    actions = policy if policy.ndim == 1 else policy[:, 0]
    transition = np.asarray(B[0], dtype=float)

    for action in actions:
        state_belief = transition[:, :, int(action)] @ state_belief
        state_belief = normalize(state_belief, axis=0, backend="numpy").squeeze()

        if use_utility:
            for modality in range(len(A)):
                q_o = spm_dot(A[modality], state_belief, backend="numpy")
                total += float(-np.sum(q_o * np.asarray(C[modality], dtype=float)))

        if use_information_gain:
            for ambiguity_m in ambiguity:
                total += float(-np.sum(state_belief * ambiguity_m.reshape(-1)))

    return total


def compute_efe_all_policies(
    A: np.ndarray,
    B: np.ndarray,
    C: np.ndarray,
    qs: np.ndarray,
    policies: np.ndarray,
    use_utility: bool = True,
    use_information_gain: bool = True,
) -> np.ndarray:
    """Compute expected free energy for a collection of policies."""

    values = np.zeros(len(policies), dtype=float)
    for idx, policy in enumerate(policies):
        values[idx] = compute_expected_free_energy(
            A=A,
            B=B,
            C=C,
            qs=qs,
            policy=np.asarray(policy),
            use_utility=use_utility,
            use_information_gain=use_information_gain,
        )
    return values


def compute_efe_with_terminal_value(
    A: np.ndarray,
    B: np.ndarray,
    C: np.ndarray,
    qs: np.ndarray,
    policies: np.ndarray,
    terminal_values: np.ndarray,
    planning_horizon: int,
    use_utility: bool = True,
    use_information_gain: bool = True,
) -> np.ndarray:
    """Add a per-policy EFE adjustment to standard expected free energy."""

    del planning_horizon
    base = compute_efe_all_policies(
        A=A,
        B=B,
        C=C,
        qs=qs,
        policies=policies,
        use_utility=use_utility,
        use_information_gain=use_information_gain,
    )
    return base + np.asarray(terminal_values, dtype=float)

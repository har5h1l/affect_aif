"""Payoff definitions and helpers for the trust game."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np

COOPERATE = 0
DEFECT = 1
ACTION_NAMES = {COOPERATE: "cooperate", DEFECT: "defect"}
PAYOFF_LEVELS = (-1.0, 1.0, 3.0, 5.0)


def build_payoff_matrix(
    mutual_coop: tuple[float, float] = (3.0, 3.0),
    sucker: tuple[float, float] = (-1.0, 5.0),
    temptation: tuple[float, float] = (5.0, -1.0),
    mutual_defect: tuple[float, float] = (1.0, 1.0),
) -> np.ndarray:
    """Return a 2x2x2 payoff tensor indexed by agent action and partner action."""

    matrix = np.zeros((2, 2, 2), dtype=float)
    matrix[COOPERATE, COOPERATE] = mutual_coop
    matrix[COOPERATE, DEFECT] = sucker
    matrix[DEFECT, COOPERATE] = temptation
    matrix[DEFECT, DEFECT] = mutual_defect
    return matrix


def build_graded_payoff_matrix(
    num_levels: int = 6,
    endowment: float = 10.0,
    multiplier: float = 3.0,
) -> np.ndarray:
    """Return a (num_levels, 2, 2) payoff tensor for graded investment trust game.

    Indexed by (investment_level, partner_action, player).
    """

    matrix = np.zeros((num_levels, 2, 2), dtype=float)
    for i in range(num_levels):
        matrix[i, COOPERATE, 0] = endowment - i + multiplier * i / 2
        matrix[i, DEFECT, 0] = endowment - i
        matrix[i, COOPERATE, 1] = multiplier * i / 2
        matrix[i, DEFECT, 1] = multiplier * i
    return matrix


def infer_payoff_levels(payoff_matrix: np.ndarray) -> tuple[float, ...]:
    """Extract sorted unique agent payoff levels from a payoff tensor."""

    levels = sorted({float(payoff_matrix[a, p, 0]) for a in range(payoff_matrix.shape[0]) for p in range(2)})
    return tuple(levels)


def payoff_to_index(payoff: float, payoff_levels: Iterable[float] = PAYOFF_LEVELS) -> int:
    """Map a payoff value to its discrete index."""

    levels = tuple(float(level) for level in payoff_levels)
    try:
        return levels.index(float(payoff))
    except ValueError as exc:  # pragma: no cover - defensive
        raise KeyError(f"Payoff {payoff} is not present in levels {levels}.") from exc


def payoff_distribution(
    agent_action: int,
    partner_action_probs: np.ndarray,
    payoff_matrix: np.ndarray,
    payoff_levels: Iterable[float],
) -> np.ndarray:
    """Return the categorical distribution over own payoff observations."""

    dist = np.zeros(len(tuple(payoff_levels)), dtype=float)
    levels = tuple(float(level) for level in payoff_levels)
    for partner_action, prob in enumerate(np.asarray(partner_action_probs, dtype=float)):
        payoff = float(payoff_matrix[agent_action, partner_action, 0])
        dist[levels.index(payoff)] += prob
    return dist


def expected_agent_payoff(
    agent_action: int,
    partner_action_probs: np.ndarray,
    payoff_matrix: np.ndarray,
) -> float:
    """Expected own payoff under a partner-action distribution."""

    probs = np.asarray(partner_action_probs, dtype=float)
    payoffs = payoff_matrix[agent_action, :, 0]
    return float(np.dot(probs, payoffs))


def num_actions(num_partners: int, assignment_mode: str, num_social_actions: int = 2) -> int:
    """Number of available actions under the current task variant."""

    if assignment_mode == "agent_choice":
        return num_social_actions * num_partners
    return num_social_actions


def encode_action(
    partner_idx: int,
    social_action: int,
    num_partners: int,
    assignment_mode: str,
    num_social_actions: int = 2,
) -> int:
    """Encode a partner-selection plus social action into a flat action index."""

    if assignment_mode == "agent_choice":
        return num_social_actions * partner_idx + social_action
    return social_action


def decode_action(
    action: int,
    num_partners: int,
    assignment_mode: str,
    active_partner: int | None = None,
    num_social_actions: int = 2,
) -> tuple[int, int]:
    """Decode a flat action into partner index and social action."""

    if assignment_mode == "agent_choice":
        return action // num_social_actions, action % num_social_actions
    if active_partner is None:
        raise ValueError("active_partner is required when assignment_mode is not 'agent_choice'.")
    return active_partner, action


def factorized_num_controls(num_partners: int, assignment_mode: str, num_social_actions: int) -> list[int]:
    """Return control-factor sizes for the current trust-task action surface."""

    if int(num_social_actions) != 2:
        return [num_actions(num_partners, assignment_mode, num_social_actions)]
    if assignment_mode == "agent_choice":
        return [int(num_partners), 2, 2]
    return [1, 2, 2]


def decode_instantaneous_index(idx: int, num_controls: list[int]) -> tuple[int, ...]:
    """Map flat index to control tuple (first factor slowest, last fastest — matches itertools.product)."""

    idx = int(idx)
    if len(num_controls) == 1:
        return (idx,)
    out: list[int] = []
    for n in reversed(num_controls):
        n = int(n)
        out.append(idx % n)
        idx //= n
    return tuple(reversed(out))


def encode_instantaneous_index(controls: tuple[int, ...], num_controls: list[int]) -> int:
    """Inverse of decode_instantaneous_index."""

    idx = 0
    for c, n in zip(controls, num_controls, strict=True):
        idx = idx * int(n) + int(c)
    return int(idx)


def encode_env_action_factorized(
    partner_idx: int,
    stance_action: int,
    own_action: int,
    assignment_mode: str,
    num_partners: int,
    num_controls: list[int],
) -> int:
    """Encode policy row for env.step. random: own_action only. agent_choice: partner*4 + stance*2 + own."""

    if len(num_controls) == 1:
        if assignment_mode == "agent_choice":
            return encode_action(
                int(partner_idx),
                int(stance_action),
                int(num_partners),
                assignment_mode,
                num_social_actions=2,
            )
        return int(own_action)
    if assignment_mode == "agent_choice":
        return int(partner_idx) * 4 + int(stance_action) * 2 + int(own_action)
    return int(own_action)


def decode_env_agent_action(
    agent_action: int,
    num_partners: int,
    assignment_mode: str,
    active_partner: int | None,
    num_social_actions: int,
    factorized: bool,
) -> tuple[int, int]:
    """Decode env.step input to (partner_idx, own_action) for payoff and agent.observe_outcome."""

    if not factorized:
        return decode_action(
            int(agent_action),
            num_partners,
            assignment_mode,
            active_partner=active_partner,
            num_social_actions=num_social_actions,
        )
    if assignment_mode == "agent_choice":
        partner_idx = int(agent_action) // 4
        rem = int(agent_action) % 4
        own_action = rem % 2
        return partner_idx, own_action
    if active_partner is None:
        raise ValueError("active_partner is required when assignment_mode is not 'agent_choice'.")
    return int(active_partner), int(agent_action)

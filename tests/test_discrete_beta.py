"""Tests for discrete Bayesian beta precision tracking."""

from __future__ import annotations

import numpy as np
import pytest

from tasks.trust.affect import (
    DiscreteBetaState,
    _build_transition_matrix,
)


class TestTransitionMatrix:
    def test_column_stochastic(self):
        B = _build_transition_matrix(5, 0.8)
        np.testing.assert_allclose(B.sum(axis=0), 1.0, atol=1e-10)

    def test_tridiagonal(self):
        B = _build_transition_matrix(5, 0.8)
        for i in range(5):
            for j in range(5):
                if abs(i - j) > 1:
                    assert B[i, j] == 0.0, f"B[{i},{j}] should be zero"

    def test_diagonal_dominance(self):
        B = _build_transition_matrix(5, 0.8)
        for j in range(5):
            assert B[j, j] >= 0.8, f"Diagonal B[{j},{j}] should be >= persistence"

    def test_boundary_fold(self):
        B = _build_transition_matrix(5, 0.8)
        # At boundaries, the out-of-bounds probability folds back
        assert B[0, 0] > B[1, 1]  # boundary has more self-transition
        assert B[4, 4] > B[3, 3]

    def test_symmetric(self):
        """Transition matrix should be symmetric for interior states."""
        B = _build_transition_matrix(5, 0.8)
        # Interior: up and down transitions should be equal
        for j in range(1, 4):
            np.testing.assert_allclose(B[j - 1, j], B[j + 1, j], atol=1e-10)


class TestDiscreteBetaState:
    def test_initial_state(self):
        state = DiscreteBetaState(num_entities=4, initial_beta=1.0)
        betas = state.get_all_betas()
        assert betas.shape == (4,)
        np.testing.assert_allclose(betas, 1.0, atol=0.1)

    def test_low_surprise_decreases_beta(self):
        """Observing low surprise should decrease HESP beta toward higher precision."""
        state = DiscreteBetaState(num_entities=1, initial_beta=1.0)
        beta_before = state.get_beta(0)
        for _ in range(5):
            state.update(entity=0, surprise=0.0)
        beta_after = state.get_beta(0)
        assert beta_after < beta_before, "Low surprise should decrease beta"

    def test_high_surprise_increases_beta(self):
        """Observing high surprise should increase HESP beta toward lower precision."""
        state = DiscreteBetaState(num_entities=1, initial_beta=0.5)
        beta_before = state.get_beta(0)
        state.update(entity=0, surprise=1.0)
        beta_after = state.get_beta(0)
        assert beta_after > beta_before, "High surprise should increase beta"

    def test_beta_bounded(self):
        """Beta should stay within the defined level range."""
        state = DiscreteBetaState(num_entities=1, initial_beta=0.5, beta_levels=[0.1, 0.5, 0.9])
        # Many high-surprise updates
        for _ in range(50):
            state.update(entity=0, surprise=1.0)
        assert state.get_beta(0) >= 0.1
        assert state.get_beta(0) <= 0.9

    def test_per_partner_independence(self):
        """Updates to one partner should not affect another."""
        state = DiscreteBetaState(num_entities=2, initial_beta=1.0)
        state.update(entity=0, surprise=0.0)
        beta_0 = state.get_beta(0)
        beta_1 = state.get_beta(1)
        assert beta_0 != beta_1, "Only updated partner should change"
        np.testing.assert_allclose(beta_1, 1.0, atol=0.1)

    def test_belief_is_valid_distribution(self):
        state = DiscreteBetaState(num_entities=1, initial_beta=0.5)
        state.update(entity=0, surprise=0.3)
        belief = state.get_belief(0)
        assert all(belief >= 0), "Belief should be non-negative"
        np.testing.assert_allclose(belief.sum(), 1.0, atol=1e-10)

    def test_belief_entropy_increases_from_point_prior_under_new_evidence(self):
        """A point prior should spread once observations push beta away from baseline."""
        state = DiscreteBetaState(num_entities=1, initial_beta=1.0)
        initial_entropy = state.get_belief_entropy(0)
        # Consistently accurate predictions push the posterior off the baseline state.
        for _ in range(10):
            state.update(entity=0, surprise=0.0)
        final_entropy = state.get_belief_entropy(0)
        assert final_entropy > initial_entropy, "Evidence should spread a delta prior into a non-trivial posterior"

    def test_reset(self):
        state = DiscreteBetaState(num_entities=2, initial_beta=1.0)
        state.update(entity=0, surprise=0.0)
        state.reset()
        betas = state.get_all_betas()
        np.testing.assert_allclose(betas, 1.0, atol=0.1)

    def test_history_tracking(self):
        state = DiscreteBetaState(num_entities=1, initial_beta=0.5)
        for _ in range(5):
            state.update(entity=0, surprise=0.2)
        history = state.get_history(0)
        assert len(history) == 6  # initial + 5 updates


@pytest.mark.skip(
    reason="AffectiveState removed — superseded by DiscreteBetaState; correspondence tests no longer applicable"
)
class TestDiscreteContinuousCorrespondence:
    """Test that continuous beta and inverse discrete beta track precision similarly."""

    def test_both_increase_on_low_surprise(self):
        pass

    def test_both_decrease_on_high_surprise(self):
        pass

    def test_same_direction_on_betrayal_pattern(self):
        pass

    def test_rank_correlation(self):
        pass


class TestDiscreteAffectiveAgent:
    """Integration test: discrete agent runs through the experiment machinery."""

    def test_no_epistemic_preset_is_registered(self):
        from experiments.trust.conditions import get_preset_condition

        assert get_preset_condition("no_epistemic").name == "no_epistemic"

    def test_discrete_agent_instantiation(self):
        from tasks.trust import AffectiveAgent
        from tasks.trust.models import TrustGameModel

        config = {
            "num_partners": 4,
            "p_switch": 0.05,
            "assignment_mode": "random",
            "payoff_mode": "binary",
            "mutual_coop": (3.0, 3.0),
            "sucker": (-1.0, 5.0),
            "temptation": (5.0, -1.0),
            "mutual_defect": (1.0, 1.0),
        }
        model = TrustGameModel(config)
        # DiscreteAffectiveAgent is absorbed into AffectiveAgent (discrete mode is default)
        agent = AffectiveAgent(
            model=model,
            planning_horizon=2,
            num_levels=5,
            persistence=0.8,
            sigma_0_sq=0.25,
            initial_beta=0.5,
        )
        # Should be able to plan
        action = agent.plan_and_act(active_partner=0)
        assert isinstance(action, int)
        assert 0 <= action < agent.num_actions

        # Check that beta beliefs are available
        beliefs = agent.affect.get_all_beliefs()
        assert beliefs.shape == (4, 5)
        np.testing.assert_allclose(beliefs.sum(axis=1), 1.0, atol=1e-6)

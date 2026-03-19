"""Tests for Phase 4: discrete hidden-state beta formulation."""

from __future__ import annotations

import numpy as np
import pytest

from affect_aif.agent.affect.discrete_state import (
    DiscreteBetaState,
    _build_likelihood_matrix,
    _build_transition_matrix,
)
from affect_aif.agent.affect.state import AffectiveState


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


class TestLikelihoodMatrix:
    def test_column_probabilities(self):
        levels = np.linspace(0.1, 0.9, 5)
        A = _build_likelihood_matrix(5, levels)
        np.testing.assert_allclose(A.sum(axis=0), 1.0, atol=1e-10)

    def test_monotonicity(self):
        """P(low_surprise | beta) should increase with beta level."""
        levels = np.linspace(0.1, 0.9, 5)
        A = _build_likelihood_matrix(5, levels)
        for i in range(4):
            assert A[0, i] < A[0, i + 1], "P(low_surprise) should increase with level"


class TestDiscreteBetaState:
    def test_initial_state(self):
        state = DiscreteBetaState(num_partners=4, initial_beta=0.5)
        betas = state.get_all_betas()
        assert betas.shape == (4,)
        np.testing.assert_allclose(betas, 0.5, atol=0.1)

    def test_low_surprise_increases_beta(self):
        """Observing low surprise (accurate prediction) should increase beta."""
        state = DiscreteBetaState(num_partners=1, initial_beta=0.5)
        beta_before = state.get_beta(0)
        state.update(partner_idx=0, predicted_action_probs=[0.9, 0.1], observed_action=0)
        beta_after = state.get_beta(0)
        assert beta_after > beta_before, "Low surprise should increase beta"

    def test_high_surprise_decreases_beta(self):
        """Observing high surprise (poor prediction) should decrease beta."""
        state = DiscreteBetaState(num_partners=1, initial_beta=0.5)
        beta_before = state.get_beta(0)
        state.update(partner_idx=0, predicted_action_probs=[0.1, 0.9], observed_action=0)
        beta_after = state.get_beta(0)
        assert beta_after < beta_before, "High surprise should decrease beta"

    def test_beta_bounded(self):
        """Beta should stay within the defined level range."""
        state = DiscreteBetaState(num_partners=1, initial_beta=0.5, beta_min=0.1, beta_max=0.9)
        # Many high-surprise updates
        for _ in range(50):
            state.update(partner_idx=0, predicted_action_probs=[0.1, 0.9], observed_action=0)
        assert state.get_beta(0) >= 0.1
        assert state.get_beta(0) <= 0.9

    def test_per_partner_independence(self):
        """Updates to one partner should not affect another."""
        state = DiscreteBetaState(num_partners=2, initial_beta=0.5)
        state.update(partner_idx=0, predicted_action_probs=[0.9, 0.1], observed_action=0)
        beta_0 = state.get_beta(0)
        beta_1 = state.get_beta(1)
        assert beta_0 != beta_1, "Only updated partner should change"
        np.testing.assert_allclose(beta_1, 0.5, atol=0.1)

    def test_belief_is_valid_distribution(self):
        state = DiscreteBetaState(num_partners=1, initial_beta=0.5)
        state.update(partner_idx=0, predicted_action_probs=[0.7, 0.3], observed_action=0)
        belief = state.get_belief(0)
        assert all(belief >= 0), "Belief should be non-negative"
        np.testing.assert_allclose(belief.sum(), 1.0, atol=1e-10)

    def test_belief_entropy_decreases_with_evidence(self):
        """Entropy should decrease as evidence accumulates."""
        state = DiscreteBetaState(num_partners=1, initial_beta=0.5)
        initial_entropy = state.get_belief_entropy(0)
        # Consistently good predictions → evidence for high beta
        for _ in range(10):
            state.update(partner_idx=0, predicted_action_probs=[0.9, 0.1], observed_action=0)
        final_entropy = state.get_belief_entropy(0)
        assert final_entropy < initial_entropy, "Consistent evidence should reduce uncertainty"

    def test_reset(self):
        state = DiscreteBetaState(num_partners=2, initial_beta=0.5)
        state.update(partner_idx=0, predicted_action_probs=[0.9, 0.1], observed_action=0)
        state.reset()
        betas = state.get_all_betas()
        np.testing.assert_allclose(betas, 0.5, atol=0.1)

    def test_history_tracking(self):
        state = DiscreteBetaState(num_partners=1, initial_beta=0.5)
        for _ in range(5):
            state.update(partner_idx=0, predicted_action_probs=[0.8, 0.2], observed_action=0)
        history = state.get_history(0)
        assert len(history) == 6  # initial + 5 updates


class TestDiscreteContinuousCorrespondence:
    """Test that discrete and continuous beta formulations track qualitatively."""

    def _simulate_continuous(self, surprises: list[float]) -> list[float]:
        state = AffectiveState(num_partners=1, initial_beta=0.5)
        betas = [state.get_beta(0)]
        for surprise_val in surprises:
            prob_observed = 1.0 - surprise_val
            state.update(partner_idx=0, predicted_action_probs=[prob_observed, 1 - prob_observed], observed_action=0)
            betas.append(state.get_beta(0))
        return betas

    def _simulate_discrete(self, surprises: list[float]) -> list[float]:
        state = DiscreteBetaState(num_partners=1, initial_beta=0.5)
        betas = [state.get_beta(0)]
        for surprise_val in surprises:
            prob_observed = 1.0 - surprise_val
            state.update(partner_idx=0, predicted_action_probs=[prob_observed, 1 - prob_observed], observed_action=0)
            betas.append(state.get_beta(0))
        return betas

    def test_both_increase_on_low_surprise(self):
        """Both formulations should increase beta on consistently low surprise."""
        surprises = [0.1] * 10
        cont = self._simulate_continuous(surprises)
        disc = self._simulate_discrete(surprises)
        assert cont[-1] > cont[0], "Continuous should increase"
        assert disc[-1] > disc[0], "Discrete should increase"

    def test_both_decrease_on_high_surprise(self):
        """Both formulations should decrease beta on consistently high surprise."""
        surprises = [0.9] * 10
        cont = self._simulate_continuous(surprises)
        disc = self._simulate_discrete(surprises)
        assert cont[-1] < cont[0], "Continuous should decrease"
        assert disc[-1] < disc[0], "Discrete should decrease"

    def test_same_direction_on_betrayal_pattern(self):
        """Both should show same direction of change on a betrayal sequence."""
        # Low surprise (cooperative) then high surprise (betrayal)
        surprises = [0.1] * 15 + [0.9] * 5
        cont = self._simulate_continuous(surprises)
        disc = self._simulate_discrete(surprises)
        # Both should rise then fall
        assert cont[15] > cont[0], "Continuous should rise during cooperation"
        assert disc[15] > disc[0], "Discrete should rise during cooperation"
        assert cont[-1] < cont[15], "Continuous should fall after betrayal"
        assert disc[-1] < disc[15], "Discrete should fall after betrayal"

    def test_rank_correlation(self):
        """Discrete and continuous trajectories should be rank-correlated."""
        from scipy.stats import spearmanr

        rng = np.random.default_rng(42)
        surprises = rng.uniform(0.05, 0.95, size=30).tolist()
        cont = self._simulate_continuous(surprises)
        disc = self._simulate_discrete(surprises)
        rho, p = spearmanr(cont, disc)
        assert rho > 0.0, f"Trajectories should be positively correlated (rho={rho:.3f})"


class TestDiscreteAffectiveAgent:
    """Integration test: discrete agent runs through the experiment machinery."""

    def test_condition_12_creates_discrete_agent(self):
        from affect_aif.experiment.conditions import get_condition_name
        assert get_condition_name(12) == "discrete_affective_shallow"

    def test_discrete_agent_instantiation(self):
        from affect_aif.agent.discrete_affective_agent import DiscreteAffectiveAgent
        from affect_aif.generative_model.model import TrustGameModel

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
        matrices = model.get_matrices()
        agent = DiscreteAffectiveAgent(
            A=matrices[0],
            B=matrices[1],
            C=matrices[2],
            D=matrices[3],
            model=model,
            planning_horizon=2,
            num_partners=4,
            num_beta_levels=5,
            beta_persistence=0.8,
            sigma_0_sq=0.25,
            initial_beta=0.5,
            mu=1.0,
        )
        # Should be able to plan
        action = agent.plan_and_act(active_partner=0)
        assert isinstance(action, int)
        assert 0 <= action < agent.num_actions

        # Check that terminal signal uses discrete betas
        signal = agent.terminal_signal()
        assert signal.shape == (4,)

        # Check that beta beliefs are available
        beliefs = agent.get_beta_beliefs()
        assert beliefs.shape == (4, 5)
        np.testing.assert_allclose(beliefs.sum(axis=1), 1.0, atol=1e-6)

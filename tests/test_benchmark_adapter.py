"""Tests for the benchmark adapter and interaction tracking.

Tests for InteractionTracker and ObservationEncoder run without external deps.
Tests for CoGamesTrustAdapter use the simulated gridworld fallback.
"""

import numpy as np
import pytest

from affect_aif.benchmark.interaction_tracker import InteractionEvent, InteractionTracker
from affect_aif.benchmark.observation_encoder import ObservationEncoder
from affect_aif.benchmark.cogames_adapter import CoGamesTrustAdapter
from affect_aif.benchmark.scenarios import RESOURCE_SHARING, get_scenario, list_scenarios
from affect_aif.benchmark.scripted_partners import (
    CooperatorPartner,
    ExploiterPartner,
    RandomPartner,
    ReciprocatorPartner,
    create_partner,
)


class TestInteractionTracker:
    def test_classify_cooperative_behavior(self):
        tracker = InteractionTracker(num_partners=4, ticks_per_round=1)
        tracker.record_event(InteractionEvent(tick=0, partner_idx=0, event_type="share", resource_delta=1.0))
        tracker.record_event(InteractionEvent(tick=0, partner_idx=0, event_type="receive", resource_delta=2.0))
        action, confidence = tracker.classify_partner_behavior(0)
        assert action == 0  # cooperate
        assert confidence > 0

    def test_classify_hostile_behavior(self):
        tracker = InteractionTracker(num_partners=4, ticks_per_round=1)
        tracker.record_event(InteractionEvent(tick=0, partner_idx=0, event_type="attack", resource_delta=-1.0))
        tracker.record_event(InteractionEvent(tick=0, partner_idx=0, event_type="steal", resource_delta=-2.0))
        action, confidence = tracker.classify_partner_behavior(0)
        assert action == 1  # defect

    def test_no_events_defaults_to_defect(self):
        tracker = InteractionTracker(num_partners=4, ticks_per_round=1)
        action, confidence = tracker.classify_partner_behavior(0)
        assert action == 1
        assert confidence == 0.0

    def test_round_summary_clears_events(self):
        tracker = InteractionTracker(num_partners=4, ticks_per_round=1)
        tracker.record_event(InteractionEvent(tick=0, partner_idx=0, event_type="share", resource_delta=1.0))
        summary = tracker.summarize_round(primary_partner=0)
        assert summary.partner_idx == 0
        assert len(tracker._round_events[0]) == 0  # cleared after summary

    def test_cumulative_history(self):
        tracker = InteractionTracker(num_partners=4, ticks_per_round=1)
        tracker.record_event(InteractionEvent(tick=0, partner_idx=0, event_type="share"))
        tracker.summarize_round(primary_partner=0)
        tracker.record_event(InteractionEvent(tick=1, partner_idx=0, event_type="share"))
        tracker.summarize_round(primary_partner=0)
        assert tracker.get_partner_cooperation_history(0) == 1.0

    def test_reset_clears_all(self):
        tracker = InteractionTracker(num_partners=4, ticks_per_round=1)
        tracker.record_event(InteractionEvent(tick=0, partner_idx=0, event_type="share"))
        tracker.summarize_round(primary_partner=0)
        tracker.reset()
        assert tracker.get_partner_cooperation_history(0) == 0.5  # back to neutral


class TestObservationEncoder:
    def test_encode_produces_valid_observation(self):
        from affect_aif.benchmark.interaction_tracker import RoundSummary
        encoder = ObservationEncoder(payoff_levels=[-1.0, 1.0, 3.0, 5.0])
        summary = RoundSummary(
            partner_idx=0, partner_action=0, agent_action=0,
            resource_delta=3.0
        )
        obs = encoder.encode(summary)
        assert len(obs) == 2
        assert obs[0] in {0, 1}
        assert 0 <= obs[1] < 4

    def test_payoff_to_index_nearest(self):
        encoder = ObservationEncoder(payoff_levels=[-1.0, 1.0, 3.0, 5.0])
        assert encoder.payoff_to_index(3.0) == 2
        assert encoder.payoff_to_index(-1.0) == 0
        assert encoder.payoff_to_index(4.0) == 2 or encoder.payoff_to_index(4.0) == 3  # nearest


class TestScriptedPartners:
    def test_cooperator_mostly_shares(self):
        partner = CooperatorPartner(partner_idx=0, seed=0, p_share=0.9)
        actions = [partner.decide() for _ in range(100)]
        assert actions.count("share") > 70

    def test_reciprocator_mirrors(self):
        partner = ReciprocatorPartner(partner_idx=0, seed=0, noise=0.0)
        assert partner.decide() == "share"  # cooperate initially
        partner.observe_focal_action("attack")
        assert partner.decide() == "attack"  # mirror defection

    def test_exploiter_switches(self):
        partner = ExploiterPartner(partner_idx=0, seed=0, switch_round=5, p_share_early=1.0, p_share_late=0.0)
        for _ in range(5):
            assert partner.decide() == "share"
            partner.observe_focal_action("share")
        # After switch
        assert partner.decide() == "attack"

    def test_create_partner_factory(self):
        for type_name in ["cooperator", "reciprocator", "exploiter", "random"]:
            partner = create_partner(type_name, partner_idx=0, seed=0)
            assert partner.decide() in {"share", "attack"}

    def test_create_partner_unknown_type(self):
        with pytest.raises(ValueError, match="Unknown partner type"):
            create_partner("nonexistent", partner_idx=0)


class TestScenarios:
    def test_list_scenarios(self):
        names = list_scenarios()
        assert "resource_sharing" in names
        assert "betrayal_arena" in names

    def test_get_scenario(self):
        scenario = get_scenario("resource_sharing")
        assert scenario.num_partners == 4
        assert scenario.num_rounds == 100

    def test_unknown_scenario_raises(self):
        with pytest.raises(ValueError, match="Unknown scenario"):
            get_scenario("nonexistent")


class TestCoGamesTrustAdapter:
    def test_reset_returns_valid_context(self):
        adapter = CoGamesTrustAdapter(scenario="resource_sharing", seed=0)
        context = adapter.reset()
        assert "active_partner" in context
        assert "true_types" in context
        assert len(context["true_types"]) == 4

    def test_step_returns_valid_result(self):
        adapter = CoGamesTrustAdapter(scenario="resource_sharing", seed=0)
        adapter.reset()
        result = adapter.step(agent_action=0)  # cooperate
        assert "partner_idx" in result
        assert "partner_action" in result
        assert "agent_action" in result
        assert "agent_payoff" in result
        assert "observation" in result
        assert "true_partner_type" in result
        assert len(result["observation"]) == 2

    def test_step_payoffs_match_trust_game_structure(self):
        adapter = CoGamesTrustAdapter(scenario="resource_sharing", seed=0)
        adapter.reset()
        result = adapter.step(0)
        assert result["agent_payoff"] in {-1.0, 1.0, 3.0, 5.0}

    def test_full_episode(self):
        adapter = CoGamesTrustAdapter(scenario="resource_sharing", seed=42)
        context = adapter.reset()
        payoffs = []
        for _ in range(20):
            result = adapter.step(agent_action=0)
            payoffs.append(result["agent_payoff"])
        summary = adapter.get_episode_summary()
        assert summary["num_rounds"] == 20
        assert np.isclose(summary["cumulative_payoff"], sum(payoffs))

    def test_reproducible_with_same_seed(self):
        adapter1 = CoGamesTrustAdapter(scenario="resource_sharing", seed=123)
        adapter2 = CoGamesTrustAdapter(scenario="resource_sharing", seed=123)

        adapter1.reset()
        adapter2.reset()

        for _ in range(10):
            r1 = adapter1.step(0)
            r2 = adapter2.step(0)
            assert r1["partner_action"] == r2["partner_action"]
            assert r1["agent_payoff"] == r2["agent_payoff"]

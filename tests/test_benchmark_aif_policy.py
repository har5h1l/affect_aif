"""Tests for CoGames policy wrappers used by the benchmark package."""

import pytest

from benchmark.aif_policy import AIFPolicy


class _DummyAgent:
    def reset(self):
        pass

    def observe_outcome(self, **kwargs):
        pass

    def plan_and_act(self, active_partner):
        return 0

    def get_metrics(self):
        return {}


def test_aif_policy_extract_events_hard_fails_without_real_cogames_mapping():
    policy = AIFPolicy(agent=_DummyAgent())
    with pytest.raises(NotImplementedError, match="Requires real CoGames environment"):
        policy._extract_events({})


def test_aif_policy_translate_action_hard_fails_without_real_cogames_mapping():
    policy = AIFPolicy(agent=_DummyAgent())
    with pytest.raises(NotImplementedError, match="Requires real CoGames environment"):
        policy._translate_action(0)

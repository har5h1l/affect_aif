"""Construction-time validation of the multi-focal runner (F8, F10, F5)."""

from __future__ import annotations

import numpy as np
import pytest

from experiment.factory import create_agents_from_multi_focal_config
from experiment.multi_focal_config import MultiFocalConfig
from experiment.multi_focal_runner import MultiFocalRunner


def _make_runner(agents_spec, payoff_mode="binary", num_rounds=200):
    cfg = MultiFocalConfig.from_dict(
        {"experiment_name": "x", "payoff_mode": payoff_mode, "num_rounds": num_rounds, "agents": agents_spec}
    )
    agents = create_agents_from_multi_focal_config(cfg, seed=0)
    return MultiFocalRunner(cfg, agents, rng=np.random.default_rng(0))


def test_construction_succeeds_with_2_agents():
    r = _make_runner([{"kind": "base"}, {"kind": "base"}])
    assert r.M == 2


def test_construction_succeeds_with_4_agents():
    r = _make_runner([{"kind": "base"}] * 4)
    assert r.M == 4
    for a in r.agents:
        assert a.num_partners == 3


def test_unknown_round_mode_rejected_at_config():
    with pytest.raises(ValueError, match="all_pairs"):
        MultiFocalConfig.from_dict(
            {
                "experiment_name": "x",
                "round_mode": "all_pairs",
                "agents": [{"kind": "base"}, {"kind": "base"}],
            }
        )


def test_run_zero_rounds_returns_empty():
    r = _make_runner([{"kind": "base"}, {"kind": "base"}], num_rounds=0)
    assert r.run() == []

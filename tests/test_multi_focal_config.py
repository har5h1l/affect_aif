"""Tests for multi-focal config parsing + agent factory (F)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from experiment.factory import create_agents_from_multi_focal_config
from experiment.multi_focal_config import MultiFocalConfig

_GOOD = {
    "experiment_name": "x",
    "agents": [
        {"kind": "base"},
        {"kind": "affective"},
        {"kind": "lesioned", "lesion_mode": "decouple"},
    ],
}


def test_good_config_parses():
    cfg = MultiFocalConfig.from_dict(_GOOD)
    assert cfg.num_agents() == 3
    assert cfg.payoff_mode == "binary"
    assert cfg.round_mode == "turn_taking"


def test_unknown_kind_raises():
    bad = dict(_GOOD)
    bad["agents"] = [{"kind": "ghost"}, {"kind": "base"}]
    with pytest.raises(ValueError, match="kind"):
        MultiFocalConfig.from_dict(bad)


def test_too_few_agents_raises():
    bad = dict(_GOOD)
    bad["agents"] = [{"kind": "base"}]
    with pytest.raises(ValueError, match=">= 2"):
        MultiFocalConfig.from_dict(bad)


def test_unknown_round_mode_raises():
    bad = dict(_GOOD)
    bad["round_mode"] = "all_pairs"
    with pytest.raises(ValueError, match="all_pairs"):
        MultiFocalConfig.from_dict(bad)


def test_payoff_mode_mismatch_in_overrides_raises():
    bad = dict(_GOOD)
    bad["agents"] = [
        {"kind": "base", "model_overrides": {"payoff_mode": "graded"}},
        {"kind": "base"},
    ]
    with pytest.raises(ValueError, match="payoff_mode"):
        MultiFocalConfig.from_dict(bad)


def test_factory_builds_M_agents_with_correct_num_partners():
    cfg = MultiFocalConfig.from_dict(_GOOD)
    agents = create_agents_from_multi_focal_config(cfg, seed=0)
    assert len(agents) == 3
    for a in agents:
        assert a.num_partners == 2
    assert agents[0]._kind_label == "base"
    assert agents[1]._kind_label == "affective"
    assert agents[2]._kind_label == "lesioned"


def test_all_multifocal_configs_load_and_validate():
    paths = sorted(Path(".").glob("configs/multifocal_*.json"))
    assert len(paths) >= 4, f"expected >= 4 configs, found {len(paths)}: {paths}"
    for p in paths:
        raw = json.loads(p.read_text())
        cfg = MultiFocalConfig.from_dict(raw)
        assert cfg.num_agents() >= 2, f"{p}: M={cfg.num_agents()}"


def test_factory_label_override():
    cfg = MultiFocalConfig.from_dict(
        {
            "experiment_name": "x",
            "agents": [
                {"kind": "affective", "_label": "healthy"},
                {"kind": "affective", "_label": "alexithymia", "alpha_charge": 0.5},
            ],
        }
    )
    agents = create_agents_from_multi_focal_config(cfg, seed=0)
    assert agents[0]._kind_label == "healthy"
    assert agents[1]._kind_label == "alexithymia"

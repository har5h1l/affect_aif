"""Emergent-dynamics checks for multi-focal runs.

Full N1/N2/N3 statistical suites are marked ``@pytest.mark.slow`` (~15+ minutes
combined with default planning); run::

    RUN_SLOW_TESTS=1 pytest tests/test_multi_focal_emergent.py -m slow

Default ``pytest tests/`` still executes the fast smoke test below.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from experiments.multifocal.config import MultiFocalConfig
from experiments.multifocal.runner import MultiFocalRunner
from experiments.trust.factory import create_agents_from_multi_focal_config


def _build(agents_spec, num_rounds=200, seed=42, assignment_mode="random"):
    cfg = MultiFocalConfig.from_dict(
        {
            "experiment_name": "emerge",
            "round_mode": "turn_taking",
            "focal_selection": "round_robin",
            "assignment_mode": assignment_mode,
            "num_rounds": num_rounds,
            "random_seed": seed,
            "payoff_mode": "binary",
            "agents": agents_spec,
        }
    )
    agents = create_agents_from_multi_focal_config(cfg, seed=seed)
    return MultiFocalRunner(cfg, agents, rng=np.random.default_rng(seed)).run()


def _coop_rate_last_quartile(rows: list[dict]) -> float:
    df = pd.DataFrame(rows)
    last_quartile = df["round"] >= int(0.75 * df["round"].max())
    actions = df.loc[last_quartile, "selected_action"]
    return float((actions == 0).mean())


def test_clinical_mix_short_run_completes():
    """Always-on smoke: heterogeneous agents, few rounds, no exceptions."""
    spec = [
        {"kind": "affective", "planning_horizon": 2, "alpha_charge": 3.0, "_label": "healthy"},
        {"kind": "affective", "planning_horizon": 2, "alpha_charge": 0.5, "_label": "alexithymia"},
        {"kind": "lesioned", "planning_horizon": 2, "lesion_mode": "decouple", "_label": "lesioned"},
    ]
    rows = _build(spec, num_rounds=8, seed=0)
    assert len(rows) == 8 * 2
    kinds = {r["agent_kind"] for r in rows}
    assert kinds == {"healthy", "alexithymia", "lesioned"}


@pytest.mark.slow
def test_n1_cooperation_emerges_among_4_affectives():
    spec = [{"kind": "affective", "planning_horizon": 8, "alpha_charge": 3.0}] * 4
    rates = []
    for seed in [42, 43, 44, 45, 46]:
        rows = _build(spec, num_rounds=200, seed=seed)
        rates.append(_coop_rate_last_quartile(rows))
    assert np.mean(rates) > 0.55, f"mean cooperation rate {np.mean(rates):.3f} below 0.55; rates={rates}"
    assert sum(r > 0.5 for r in rates) >= 4, f"only {sum(r > 0.5 for r in rates)}/5 seeds above 0.5"


@pytest.mark.slow
def test_n2_defection_cascade_from_lesioned_agent():
    spec_baseline = [{"kind": "affective", "planning_horizon": 8, "alpha_charge": 3.0}] * 4
    spec_cascade = [
        {"kind": "lesioned", "planning_horizon": 8, "lesion_mode": "decouple"},
        {"kind": "affective", "planning_horizon": 8, "alpha_charge": 3.0},
        {"kind": "affective", "planning_horizon": 8, "alpha_charge": 3.0},
        {"kind": "affective", "planning_horizon": 8, "alpha_charge": 3.0},
    ]
    base_rates, cas_rates = [], []
    for seed in [42, 43, 44]:
        base_rates.append(_coop_rate_last_quartile(_build(spec_baseline, num_rounds=200, seed=seed)))
        cas_rates.append(_coop_rate_last_quartile(_build(spec_cascade, num_rounds=200, seed=seed)))
    assert np.mean(cas_rates) < np.mean(base_rates), (
        f"defection cascade not observed: cascade={np.mean(cas_rates):.3f}, baseline={np.mean(base_rates):.3f}"
    )


@pytest.mark.slow
def test_n3_assortative_pairing_in_agent_choice():
    spec = [
        {"kind": "affective", "planning_horizon": 8, "_label": "deep"},
        {"kind": "affective", "planning_horizon": 8, "_label": "deep"},
        {"kind": "base", "planning_horizon": 2, "_label": "shallow"},
        {"kind": "base", "planning_horizon": 2, "_label": "shallow"},
    ]
    deep_picks_deep = []
    for seed in [42, 43, 44]:
        rows = _build(spec, num_rounds=300, seed=seed, assignment_mode="agent_choice")
        df = pd.DataFrame(rows)
        last_quartile = df["round"] >= int(0.75 * df["round"].max())
        deep_focals = df.loc[last_quartile & df["is_focal_this_round"] & (df["agent_kind"] == "deep")].copy()
        engaged_kinds = []
        for _, r in deep_focals.iterrows():
            engaged_row = df[
                (df["round"] == r["round"])
                & (df["agent_global_idx"] == r["engaged_partner_global_idx"])
                & (~df["is_focal_this_round"])
            ]
            if not engaged_row.empty:
                engaged_kinds.append(engaged_row.iloc[0]["agent_kind"])
        if engaged_kinds:
            deep_picks_deep.append(np.mean([k == "deep" for k in engaged_kinds]))
    assert deep_picks_deep, "no deep-focal rows in last quartile across any seed (test setup error)"
    assert np.mean(deep_picks_deep) > 0.5, f"deep agents do not preferentially pick deep partners: {deep_picks_deep}"

"""Tests for betrayal-specific benchmark wiring."""

from benchmark.benchmark_config import BenchmarkConfig
from benchmark.benchmark_runner import BenchmarkRunner


def test_trust_backend_uses_betrayal_arena_default_switch():
    config = BenchmarkConfig.from_dict(
        {
            "backends": ["trust"],
            "agents": ["random"],
            "num_replications": 1,
            "num_rounds": 100,
            "random_seed": 7,
            "backend_configs": {
                "trust": {
                    "scenario": "betrayal_arena",
                }
            },
        }
    )

    results = BenchmarkRunner(config).run_all()

    assert (results["scheduled_switch_partner_ids"] != "").any()
    assert (results["type_switched"]).any()
    assert "scheduled_type" in set(results["switch_kind"])
    assert "stochastic" not in set(results["switch_kind"])

    switched_rows = results[results["switch_kind"] == "scheduled_type"]
    assert list(switched_rows["step"]) == [49]
    assert list(switched_rows["true_partner_type"]) == ["exploiter"]


def test_trust_backend_passes_scheduled_switches_through_to_results():
    config = BenchmarkConfig.from_dict(
        {
            "backends": ["trust"],
            "agents": ["random"],
            "num_replications": 1,
            "num_rounds": 20,
            "random_seed": 7,
            "backend_configs": {
                "trust": {
                    "scenario": "betrayal_arena",
                    "assignment_mode": "agent_choice",
                    "num_partners": 1,
                    "p_switch": 0.0,
                    "initial_partner_types": ["cooperative"],
                    "scheduled_type_switches": [{"partner_idx": 0, "round": 10, "to_type": "exploiter"}],
                }
            },
        }
    )

    results = BenchmarkRunner(config).run_all()

    assert (results["scheduled_switch_partner_ids"] != "").any()
    assert (results["type_switched"]).any()
    assert "scheduled_type" in set(results["switch_kind"])
    assert "stochastic" not in set(results["switch_kind"])

    switched_rows = results[results["switch_kind"] == "scheduled_type"]
    assert list(switched_rows["step"]) == [9]
    assert list(switched_rows["true_partner_type"]) == ["exploiter"]

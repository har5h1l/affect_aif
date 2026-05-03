"""Tests for benchmark configuration and agent specs."""

from benchmark.benchmark_config import AgentSpec, BenchmarkConfig


def test_legacy_boolean_environment_flags_are_mapped_to_backends():
    config = BenchmarkConfig.from_dict(
        {
            "scenario": "resource_sharing",
            "agents": ["tau4_affect", "random"],
            "run_trust_game": True,
            "run_gridworld": False,
        }
    )

    assert config.backends == ["trust"]
    assert [agent.backend for agent in config.agents] == ["trust", "trust"]
    assert [agent.implementation for agent in config.agents] == ["tau4_affect", "random"]


def test_agent_specs_accept_explicit_policy_specs_for_cvc_backend():
    config = BenchmarkConfig.from_dict(
        {
            "backends": ["cvc_local"],
            "agents": [
                {
                    "name": "teammate_reliability",
                    "backend": "cvc_local",
                    "kind": "policy_spec",
                    "policy_spec": "class=benchmarks.cvc.policy.TeammateReliabilityPolicy",
                }
            ],
            "backend_configs": {"cvc_local": {"mission": "machina_1"}},
        }
    )

    assert len(config.agents) == 1
    agent = config.agents[0]
    assert isinstance(agent, AgentSpec)
    assert agent.backend == "cvc_local"
    assert agent.kind == "policy_spec"
    assert agent.policy_spec == "class=benchmarks.cvc.policy.TeammateReliabilityPolicy"

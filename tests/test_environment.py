from affect_aif.environment.partner import Partner
from affect_aif.environment.trust_game import TrustGameEnv
from affect_aif.experiment.config import ExperimentConfig
from affect_aif.generative_model.model import TrustGameModel


def test_cooperator_mostly_cooperates():
    model = TrustGameModel(ExperimentConfig())
    lookup = {partner.type_name: partner for partner in model.partner_types}
    partner = Partner(partner_idx=0, type_name="cooperator", type_lookup=lookup, rng=model.config.get("rng", None) or __import__("numpy").random.default_rng(0))
    actions = [partner.sample_action() for _ in range(200)]
    assert sum(actions) < 60


def test_exploiter_switches_strategy():
    model = TrustGameModel(ExperimentConfig())
    lookup = {partner.type_name: partner for partner in model.partner_types}
    partner = Partner(partner_idx=0, type_name="exploiter", type_lookup=lookup, rng=__import__("numpy").random.default_rng(1))
    early_prob = partner.type_impl.get_action_probability(agent_last_action=0, round_number=0)
    late_prob = partner.type_impl.get_action_probability(agent_last_action=0, round_number=10)
    assert early_prob > late_prob


def test_environment_step_fields():
    cfg = ExperimentConfig(num_rounds=2)
    env = TrustGameEnv(cfg, seed=0)
    context = env.reset()
    assert "active_partner" in context
    result = env.step(0)
    assert {"partner_idx", "true_partner_type", "agent_payoff", "observation"}.issubset(result)


def test_environment_applies_scheduled_type_switches():
    cfg = ExperimentConfig(
        num_partners=1,
        num_rounds=2,
        assignment_mode="random",
        p_switch=0.0,
        partner_types=["cooperator", "exploiter"],
        initial_partner_types=["cooperator"],
        scheduled_type_switches=[{"round": 2, "partner_idx": 0, "to_type": "exploiter"}],
    )
    env = TrustGameEnv(cfg, seed=0)
    env.reset()

    first = env.step(0)
    second = env.step(0)

    assert first["true_partner_type"] == "cooperator"
    assert second["true_partner_type"] == "exploiter"
    assert second["type_switched"] is True


def test_environment_uses_partner_interface_methods():
    cfg = ExperimentConfig(num_partners=1, num_rounds=1, p_switch=0.0)
    env = TrustGameEnv(cfg, seed=0)
    env.reset()

    class StubPartner:
        type_name = "cooperator"
        last_partner_action = 0

        def __init__(self):
            self.plan_calls = []
            self.outcome_calls = []

        def plan_and_act(self, correlation_action=None, correlation_strength=0.9):
            self.plan_calls.append((correlation_action, correlation_strength))
            self.last_partner_action = 0
            return 0

        def observe_outcome(self, agent_action, partner_action=None, partner_payoff=None, agent_payoff=None):
            self.outcome_calls.append((agent_action, partner_action, partner_payoff, agent_payoff))

        def maybe_switch_type(self, available_types, p_switch):
            return False

        def force_type_switch(self, new_type):
            self.type_name = new_type

    stub = StubPartner()
    env.partners[0] = stub
    result = env.step(0)

    assert stub.plan_calls == [(None, cfg.correlation_strength)]
    assert stub.outcome_calls == [(0, 0, result["partner_payoff"], result["agent_payoff"])]

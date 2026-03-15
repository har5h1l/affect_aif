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

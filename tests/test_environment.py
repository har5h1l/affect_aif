from experiments.trust.config import ExperimentConfig
from tasks.trust.envs import GradedTrustGameEnv, Partner, TrustGameEnv
from tasks.trust.pomdp import build_trust_pomdp_template


def _build_model(config):
    return build_trust_pomdp_template(config, planning_horizon=1)


def test_cooperator_mostly_cooperates():
    model = _build_model(ExperimentConfig(payoff_mode="binary"))
    lookup = {partner.type_name: partner for partner in model.partner_types}
    partner = Partner(
        partner_idx=0,
        type_name="cooperator",
        stance_name="neutral",
        type_lookup=lookup,
        rng=__import__("numpy").random.default_rng(0),
    )
    actions = [partner.sample_action() for _ in range(200)]
    assert sum(actions) < 80


def test_exploiter_is_more_cooperative_when_trusting_than_hostile():
    model = _build_model(ExperimentConfig(payoff_mode="binary"))
    lookup = {partner.type_name: partner for partner in model.partner_types}
    partner = Partner(
        partner_idx=0,
        type_name="exploiter",
        stance_name="neutral",
        type_lookup=lookup,
        rng=__import__("numpy").random.default_rng(1),
    )
    trusting_prob = partner.type_impl.get_action_probability("trusting")
    hostile_prob = partner.type_impl.get_action_probability("hostile")
    assert trusting_prob > hostile_prob


def test_environment_step_fields():
    cfg = ExperimentConfig(payoff_mode="binary", num_rounds=2)
    env = TrustGameEnv(cfg, seed=0)
    context = env.reset()
    assert "active_partner" in context
    result = env.step(0)
    assert {"partner_idx", "true_partner_type", "agent_payoff", "observation"}.issubset(result)


def test_environment_applies_scheduled_type_switches():
    cfg = ExperimentConfig(
        payoff_mode="binary",
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


def test_environment_applies_scheduled_stance_switches():
    cfg = ExperimentConfig(
        payoff_mode="binary",
        num_partners=1,
        num_rounds=2,
        assignment_mode="random",
        p_switch=0.0,
        partner_types=["cooperator"],
        initial_partner_types=["cooperator"],
        initial_partner_stances=["neutral"],
        scheduled_stance_switches=[{"round": 2, "partner_idx": 0, "to_stance": "hostile"}],
    )
    env = TrustGameEnv(cfg, seed=0)
    env.reset()

    first = env.step(0)
    second = env.step(0)

    assert first["true_partner_stance"] == "neutral"
    assert second["true_partner_stance"] == "hostile"
    assert second["stance_switched"] is True


def test_environment_uses_partner_interface_methods():
    cfg = ExperimentConfig(payoff_mode="binary", num_partners=1, num_rounds=1, p_switch=0.0)
    env = TrustGameEnv(cfg, seed=0)
    env.reset()

    class StubPartner:
        type_name = "cooperator"
        stance_name = "neutral"
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


def test_type_switch_preserves_partner_stance():
    cfg = ExperimentConfig(
        payoff_mode="binary",
        num_partners=1,
        num_rounds=1,
        assignment_mode="random",
        p_switch=0.0,
        partner_types=["cooperator", "random"],
        initial_partner_types=["cooperator"],
        initial_partner_stances=["hostile"],
        scheduled_type_switches=[{"round": 1, "partner_idx": 0, "to_type": "random"}],
    )
    env = TrustGameEnv(cfg, seed=0)
    env.reset()

    first = env.step(0)

    assert first["true_partner_type"] == "random"
    assert first["true_partner_stance"] == "hostile"


def test_graded_environment_step():
    cfg = ExperimentConfig(
        payoff_mode="graded",
        num_investment_levels=6,
        num_partners=4,
        num_rounds=10,
        assignment_mode="agent_choice",
        p_switch=0.0,
    )
    env = GradedTrustGameEnv(cfg, seed=0)
    context = env.reset()
    assert context["active_partner"] is None  # agent_choice mode

    # Action 5 = partner 0, investment level 5 (6*0 + 5)
    result = env.step(5)
    assert result["partner_idx"] == 0
    assert result["agent_action"] == 5
    expected_payoff = env.model.payoff_matrix[5, result["partner_action"], 0]
    assert result["agent_payoff"] == expected_payoff

    # Action 6 = partner 1, investment level 0 (6*1 + 0)
    result2 = env.step(6)
    assert result2["partner_idx"] == 1
    assert result2["agent_action"] == 0
    expected_payoff2 = env.model.payoff_matrix[0, result2["partner_action"], 0]
    assert result2["agent_payoff"] == expected_payoff2


def test_graded_partner_uses_investment_strength_as_evidence():
    """Graded investment should provide stronger evidence than a zero investment."""
    cfg = ExperimentConfig(
        payoff_mode="graded",
        num_investment_levels=6,
        num_partners=1,
        num_rounds=2,
        assignment_mode="random",
        p_switch=0.0,
        partner_types=["reciprocator", "cooperator", "exploiter", "random"],
        initial_partner_types=["reciprocator"],
    )
    env = GradedTrustGameEnv(cfg, seed=0)
    env.reset()
    env.step(5)
    strong_coop_posterior = env.partners[0].agent_character_posterior.copy()
    env.step(0)
    weak_coop_posterior = env.partners[0].agent_character_posterior.copy()

    assert strong_coop_posterior[0] > 1.0 / 3.0
    assert weak_coop_posterior[0] < strong_coop_posterior[0]

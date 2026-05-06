from __future__ import annotations

from runtime_helpers import build_runtime

from experiments.trust.config import ExperimentConfig
from tasks.trust.runtime import PartnerBank


def test_factory_returns_native_runtime_without_custom_agent() -> None:
    runtime = build_runtime(
        ExperimentConfig(payoff_mode="binary", num_partners=2),
    )

    assert hasattr(runtime, "template")
    assert isinstance(runtime.partner_bank, PartnerBank)
    assert not hasattr(runtime, "plan_and_act")
    assert not hasattr(runtime, "observe_outcome")

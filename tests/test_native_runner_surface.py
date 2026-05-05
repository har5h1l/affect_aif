from __future__ import annotations

from experiments.trust.config import ExperimentConfig
from experiments.trust.factory import create_native_runtime
from tasks.trust.runtime import PartnerBank


def test_factory_returns_native_runtime_without_custom_agent() -> None:
    runtime = create_native_runtime(
        ExperimentConfig(payoff_mode="binary", num_partners=2),
        condition=1,
        seed=0,
    )

    assert hasattr(runtime, "template")
    assert isinstance(runtime.partner_bank, PartnerBank)
    assert not hasattr(runtime, "plan_and_act")
    assert not hasattr(runtime, "observe_outcome")

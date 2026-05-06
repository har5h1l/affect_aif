from __future__ import annotations

from experiments.trust.config import ExperimentConfig
from experiments.trust.factory import NativeTrustRuntime, create_native_runtime_from_variant
from experiments.trust.spec import VariantSpec


def build_runtime(
    config: ExperimentConfig | None = None,
    *,
    variant_id: str = "no_affect",
    affect: str = "none",
    planning_horizon: int = 1,
    epistemic_value: bool = True,
    seed: int = 0,
    **variant_kwargs,
) -> NativeTrustRuntime:
    variant = VariantSpec(
        id=variant_id,
        affect=affect,
        planning_horizon=planning_horizon,
        epistemic_value=epistemic_value,
        **variant_kwargs,
    )
    return create_native_runtime_from_variant(
        config or ExperimentConfig(payoff_mode="binary"),
        variant=variant,
        variant_id=variant_id,
        seed=seed,
    )

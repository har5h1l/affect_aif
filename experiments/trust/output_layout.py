"""Canonical run output directories derived from config path families."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

PROMOTED_DIAGNOSTIC_TARGETS: dict[str, str] = {
    "h0_policy_openness/graded_choice.toml": "policy_openness",
    "h2_deployment/lesion_open_regime.toml": "deployment",
    "h3_locality/global_beta_locality_probe.toml": "locality",
    "h3_locality/global_beta_focal_switch_probe.toml": "locality",
    "h1_model_fitness/reliability_vs_reward_confirm.toml": "model_fitness",
    "h4_social_allocation/partner_choice_confirm.toml": "social_allocation",
}


def _configs_relative_path(config_path: str | Path) -> Path:
    path = Path(config_path).resolve()
    parts = path.parts
    if "configs" not in parts:
        raise ValueError(f"Config path must live under configs/: {path}")
    idx = parts.index("configs")
    return Path(*parts[idx + 1 :])


def config_family(config_path: str | Path) -> str:
    rel = _configs_relative_path(config_path)
    top = rel.parts[0]
    if top in {"paper", "demo", "diagnostics", "future"}:
        return top
    raise ValueError(f"Unsupported config family for {config_path}")


def public_config_path(config_path: str | Path) -> str:
    """Return the repo-relative config path serialized into outputs."""

    try:
        return str(Path("configs") / _configs_relative_path(config_path))
    except ValueError:
        return str(config_path)


def resolve_run_output_dir(
    config_path: str | Path,
    *,
    hypothesis_id: str,
    experiment_id: str,
    suite_experiment_count: int = 1,
) -> Path:
    rel = _configs_relative_path(config_path)
    family = rel.parts[0]

    if family == "paper":
        slug = rel.stem
        base = Path("results/paper") / slug / "raw"
        if suite_experiment_count > 1:
            return base / experiment_id
        return base

    if family == "future":
        return Path("results/future") / rel.stem / "raw"

    if family == "demo":
        return Path("outputs") / "demo" / rel.stem / hypothesis_id / experiment_id

    if family == "diagnostics":
        rel_under_diag = "/".join(rel.parts[1:])
        promoted_card = PROMOTED_DIAGNOSTIC_TARGETS.get(rel_under_diag)
        if promoted_card is not None:
            return Path("results/diagnostics") / promoted_card / "raw" / hypothesis_id / experiment_id
        return Path("results/diagnostics/raw") / hypothesis_id / experiment_id

    raise ValueError(f"Unsupported config family: {family}")


def uses_canonical_output_layout(*, output_root: str | None, batch_name: str | None) -> bool:
    return output_root is None and batch_name is None


def resolve_state_output_dir(
    config_path: str | Path,
    *,
    hypothesis_id: str,
    experiment_id: str,
    suite_experiment_count: int = 1,
    output_root: str | Path | None = None,
    batch_name: str | None = None,
) -> Path:
    if uses_canonical_output_layout(output_root=output_root, batch_name=batch_name):
        return resolve_run_output_dir(
            config_path,
            hypothesis_id=hypothesis_id,
            experiment_id=experiment_id,
            suite_experiment_count=suite_experiment_count,
        )
    root = Path(output_root or "results")
    batch_id = batch_name or datetime.now().strftime("batch_%Y%m%d_%H%M%S")
    return root / batch_id / hypothesis_id / experiment_id


__all__ = [
    "PROMOTED_DIAGNOSTIC_TARGETS",
    "config_family",
    "public_config_path",
    "resolve_run_output_dir",
    "resolve_state_output_dir",
    "uses_canonical_output_layout",
]

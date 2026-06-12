from pathlib import Path

import pytest

from experiments.trust.output_layout import (
    config_family,
    public_config_path,
    resolve_run_output_dir,
    resolve_state_output_dir,
    uses_canonical_output_layout,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_config_family_classification():
    assert config_family(REPO_ROOT / "configs/paper/01_predictability_value.toml") == "paper"
    assert config_family(REPO_ROOT / "configs/diagnostics/smoke/trust_smoke.toml") == "diagnostics"
    assert config_family(REPO_ROOT / "configs/demo/01_predictability_value.toml") == "demo"
    assert config_family(REPO_ROOT / "configs/future/mixed_volatility.toml") == "future"


def test_public_config_path_is_repo_relative():
    assert public_config_path(REPO_ROOT / "configs/paper/01_predictability_value.toml") == (
        "configs/paper/01_predictability_value.toml"
    )


def test_canonical_diagnostic_output_paths():
    path = REPO_ROOT / "configs/diagnostics/h0_policy_openness/graded_choice.toml"
    assert resolve_run_output_dir(path, hypothesis_id="h0", experiment_id="graded_choice") == Path(
        "results/diagnostics/policy_openness/raw/h0/graded_choice"
    )
    smoke = REPO_ROOT / "configs/diagnostics/smoke/trust_smoke.toml"
    assert resolve_run_output_dir(smoke, hypothesis_id="smoke", experiment_id="smoke") == Path(
        "results/diagnostics/raw/smoke/smoke"
    )


def test_canonical_paper_and_future_output_paths():
    paper = REPO_ROOT / "configs/paper/01_predictability_value.toml"
    assert resolve_run_output_dir(
        paper,
        hypothesis_id="predictability_value",
        experiment_id="predictability_value",
    ) == Path("results/paper/01_predictability_value/raw")

    suite = REPO_ROOT / "configs/paper/05a_alpha_sweep.toml"
    assert resolve_run_output_dir(
        suite,
        hypothesis_id="alpha_sweep",
        experiment_id="open_graded",
        suite_experiment_count=2,
    ) == Path("results/paper/05a_alpha_sweep/raw/open_graded")

    future = REPO_ROOT / "configs/future/mixed_volatility.toml"
    assert resolve_run_output_dir(
        future,
        hypothesis_id="mixed_volatility",
        experiment_id="mixed_volatility",
    ) == Path("results/future/mixed_volatility/raw")


def test_legacy_override_keeps_batch_layout():
    path = REPO_ROOT / "configs/diagnostics/smoke/trust_smoke.toml"
    resolved = resolve_state_output_dir(
        path,
        hypothesis_id="smoke",
        experiment_id="smoke",
        output_root="outputs",
        batch_name="legacy_batch",
    )
    assert resolved == Path("outputs/legacy_batch/smoke/smoke")


def test_uses_canonical_output_layout():
    assert uses_canonical_output_layout(output_root=None, batch_name=None)
    assert not uses_canonical_output_layout(output_root="results", batch_name=None)
    assert not uses_canonical_output_layout(output_root=None, batch_name="paper")


@pytest.mark.parametrize(
    "config_path",
    sorted((REPO_ROOT / "configs").glob("**/*.toml")),
)
def test_every_maintained_config_has_canonical_family(config_path: Path):
    assert config_family(config_path) in {"paper", "demo", "diagnostics", "future"}

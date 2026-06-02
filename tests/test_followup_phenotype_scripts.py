from scripts.experiment.run_exp_d_mixed_volatility import build_specs


def test_exp_d_alpha_conditions_are_distinct_and_ordered():
    (spec,) = build_specs(rounds=10, seeds=1, seed=123)

    alphas = {variant.id: variant.alpha_charge for variant in spec.variants if variant.affect == "precision"}

    assert alphas["low_alpha"] < alphas["default_reference"] < alphas["high_alpha"]

import numpy as np

from agent.affect.interoception import affective_charge, discretize_intero


def test_affective_charge_matches_hesp_sign_convention():
    neutral = affective_charge(0.5, alpha=3.0, sigma_0_sq=0.25)
    accurate = affective_charge(0.0, alpha=3.0, sigma_0_sq=0.25)
    surprising = affective_charge(1.0, alpha=3.0, sigma_0_sq=0.25)

    assert np.isclose(neutral, 0.0)
    assert accurate > 0.0
    assert surprising < 0.0


def test_discretize_intero_maps_positive_charge_to_high_valence():
    assert discretize_intero(10.0, num_levels=5) == 4
    assert discretize_intero(0.0, num_levels=5) == 2
    assert discretize_intero(-10.0, num_levels=5) == 0

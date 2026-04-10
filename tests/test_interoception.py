import numpy as np

from agent.affect.interoception import affective_charge


def test_affective_charge_matches_hesp_sign_convention():
    neutral = affective_charge(0.5, alpha=3.0, sigma_0_sq=0.25)
    accurate = affective_charge(0.0, alpha=3.0, sigma_0_sq=0.25)
    surprising = affective_charge(1.0, alpha=3.0, sigma_0_sq=0.25)

    assert np.isclose(neutral, 0.0)
    assert accurate > 0.0
    assert surprising < 0.0

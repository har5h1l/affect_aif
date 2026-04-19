"""Generic active-inference primitives."""

from __future__ import annotations

from aif.agent import Agent
from aif.inference import infer_policies, infer_states
from aif.learning import update_pA, update_pB, update_pD, update_pE
from aif.maths import dirichlet_expected_value, log_stable, softmax
from aif.policies import construct_policies, sample_action
from aif.utils import obj_array


__all__ = ["softmax", "log_stable", "obj_array", "construct_policies"]

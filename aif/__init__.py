"""Generic active-inference primitives."""

from aif.agent import Agent
from aif.inference import infer_policies, infer_states
from aif.maths import log_stable, softmax
from aif.policies import construct_policies
from aif.utils import obj_array

__all__ = ["softmax", "log_stable", "obj_array", "construct_policies"]

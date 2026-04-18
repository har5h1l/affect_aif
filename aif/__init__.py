"""Generic active-inference primitives.

PR-1 exposes only a minimal surface from the extracted ``aif`` package:
``softmax``, ``log_stable``, ``obj_array``, and ``construct_policies``.
The package is intentionally self-contained and remains dead code until
later integration work wires it into the rest of the repository.
"""

from aif.maths import log_stable, softmax
from aif.policies import construct_policies
from aif.utils import obj_array


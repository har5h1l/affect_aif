"""Backend helpers for NumPy and JAX."""

from __future__ import annotations

from typing import Any

import numpy as np

try:
    import jax
    import jax.numpy as jnp

    HAS_JAX = True
except ImportError:  # pragma: no cover - exercised only when JAX is unavailable
    jax = None
    jnp = None
    HAS_JAX = False


DEFAULT_BACKEND = "jax" if HAS_JAX else "numpy"
Array = Any


def get_xp(backend: str | None = None):
    """Return the numerical namespace for the requested backend."""

    name = (backend or DEFAULT_BACKEND).lower()
    if name == "jax":
        if not HAS_JAX:
            raise RuntimeError("JAX backend requested but jax is not installed.")
        return jnp
    if name == "numpy":
        return np
    raise ValueError(f"Unsupported backend '{backend}'.")


def asarray(x: Any, backend: str | None = None, dtype: Any | None = None):
    """Convert a value into an array on the requested backend."""

    xp = get_xp(backend)
    return xp.asarray(x, dtype=dtype)


def to_numpy(x: Any) -> np.ndarray:
    """Convert arrays from either backend into a NumPy array."""

    if HAS_JAX and hasattr(x, "__jax_array__"):
        return np.asarray(x)
    return np.asarray(x)


def device_put(x: Any):
    """Place an array on the JAX device when available."""

    if HAS_JAX:
        return jax.device_put(x)
    return np.asarray(x)

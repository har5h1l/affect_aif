"""JAX runtime helpers for device placement and host conversion."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any

import jax
import jax.numpy as jnp
import numpy as np


DEFAULT_FLOAT_DTYPE = jnp.float32


@dataclass(frozen=True)
class RuntimeConfig:
    """Execution controls for JAX rollouts."""

    execution_device: str = "auto"
    jit_enabled: bool = True


def resolve_device(preference: str = "auto") -> jax.Device:
    """Resolve the preferred execution device."""

    choice = str(preference).lower()
    if choice == "auto":
        return jax.devices()[0]
    if choice == "cpu":
        cpu_devices = jax.devices("cpu")
        if not cpu_devices:
            raise RuntimeError("No CPU device available for JAX.")
        return cpu_devices[0]
    if choice == "gpu":
        gpu_devices = jax.devices("gpu")
        if not gpu_devices:
            raise RuntimeError("GPU execution requested but no JAX GPU device is available.")
        return gpu_devices[0]
    raise ValueError(f"Unsupported execution_device '{preference}'.")


@contextmanager
def runtime_context(config: RuntimeConfig):
    """Apply device and JIT settings for a block of work."""

    device = resolve_device(config.execution_device)
    with jax.default_device(device):
        if config.jit_enabled:
            yield device
        else:
            with jax.disable_jit():
                yield device


def as_jax(x: Any, dtype: Any | None = None) -> jax.Array:
    """Convert a host value to a device array."""

    return jnp.asarray(x, dtype=dtype or DEFAULT_FLOAT_DTYPE)


def to_numpy(x: Any) -> np.ndarray:
    """Convert a JAX value to a NumPy array on the host."""

    return np.asarray(jax.device_get(x))

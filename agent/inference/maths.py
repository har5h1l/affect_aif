"""Shared mathematical utilities for active inference."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from agent.inference.backend import asarray, get_xp


def softmax(x, tau: float = 1.0, backend: str | None = None):
    """Softmax with an optional temperature parameter."""

    xp = get_xp(backend)
    x = asarray(x, backend=backend)
    scaled = x / max(tau, 1e-12)
    shifted = scaled - xp.max(scaled, axis=-1, keepdims=True)
    exp_x = xp.exp(shifted)
    return exp_x / xp.sum(exp_x, axis=-1, keepdims=True)


def log_stable(x, eps: float = 1e-16, backend: str | None = None):
    """Numerically stable logarithm."""

    xp = get_xp(backend)
    x = asarray(x, backend=backend)
    return xp.log(x + eps)


def entropy(p, backend: str | None = None):
    """Shannon entropy."""

    xp = get_xp(backend)
    p = asarray(p, backend=backend)
    return -xp.sum(p * log_stable(p, backend=backend), axis=0)


def kl_divergence(q, p, backend: str | None = None):
    """KL divergence D_KL[q || p]."""

    xp = get_xp(backend)
    q = asarray(q, backend=backend)
    p = asarray(p, backend=backend)
    return xp.sum(q * (log_stable(q, backend=backend) - log_stable(p, backend=backend)))


def normalize(x, axis: int = 0, backend: str | None = None):
    """Normalize an array so it sums to one along the requested axis."""

    backend_name = backend or "jax"
    xp = get_xp(backend)
    x = asarray(x, backend=backend)
    total = xp.sum(x, axis=axis, keepdims=True)
    safe_total = xp.where(total == 0.0, 1.0, total)
    normalized = x / safe_total
    size = x.shape[axis]
    uniform = xp.full_like(normalized, 1.0 / size)
    mask = xp.broadcast_to(total == 0.0, normalized.shape)
    if backend_name == "jax":
        normalized = xp.where(mask, uniform, normalized)
    elif np.any(np.asarray(total == 0.0)):
        normalized = xp.where(mask, uniform, normalized)
    return normalized


def spm_dot(X, y, dims_to_omit: Sequence[int] | None = None, backend: str | None = None):
    """SPM-style dot product over state dimensions."""

    xp = get_xp(backend)
    X = asarray(X, backend=backend)

    if isinstance(y, np.ndarray) and y.dtype == object:
        qs = [asarray(elem, backend=backend) for elem in y]
    elif isinstance(y, (list, tuple)):
        qs = [asarray(elem, backend=backend) for elem in y]
    else:
        qs = [asarray(y, backend=backend)]

    dims_to_omit = set(dims_to_omit or [])
    result = X
    offset = 0
    for idx, q in enumerate(qs):
        if idx in dims_to_omit:
            continue
        axis = idx + 1 - offset
        result = xp.tensordot(result, q, axes=([axis], [0]))
        offset += 1
    return result


def spm_log(x, backend: str | None = None):
    """SPM-style stable logarithm."""

    return log_stable(x, eps=1e-16, backend=backend)


def dirichlet_expected_value(concentrations, backend: str | None = None):
    """Expected categorical probabilities under Dirichlet concentrations."""

    return normalize(concentrations, axis=0, backend=backend)

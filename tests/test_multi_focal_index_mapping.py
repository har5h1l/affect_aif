"""Round-trip tests for global<->local partner index mapping (F5)."""
from __future__ import annotations

import pytest

from experiment.multi_focal_runner import _global_partner_idx, _local_partner_idx


@pytest.mark.parametrize("M", [2, 3, 4, 5, 8])
def test_round_trip_global_to_local_to_global(M):
    for g in range(M):
        for o in range(M):
            if o == g:
                continue
            local = _local_partner_idx(g, o)
            assert 0 <= local < M - 1
            assert _global_partner_idx(g, local, M) == o


@pytest.mark.parametrize("M", [2, 3, 4, 8])
def test_round_trip_local_to_global_to_local(M):
    for g in range(M):
        for l in range(M - 1):
            o = _global_partner_idx(g, l, M)
            assert o != g
            assert _local_partner_idx(g, o) == l


def test_self_modeling_local_raises():
    with pytest.raises(ValueError, match="self-modeling"):
        _local_partner_idx(2, 2)


def test_M2_smallest_case():
    assert _local_partner_idx(0, 1) == 0
    assert _local_partner_idx(1, 0) == 0
    assert _global_partner_idx(0, 0, 2) == 1
    assert _global_partner_idx(1, 0, 2) == 0

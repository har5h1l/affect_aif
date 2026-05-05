from __future__ import annotations

import importlib.metadata as metadata


def test_official_inferactively_pymdp_is_pinned() -> None:
    assert metadata.version("inferactively-pymdp") == "1.0.0"


def test_pymdp_agent_api_is_available() -> None:
    from pymdp.agent import Agent

    assert Agent is not None

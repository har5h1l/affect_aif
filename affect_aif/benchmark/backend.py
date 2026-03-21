"""Backend contracts for the benchmark runner."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from affect_aif.benchmark.benchmark_config import AgentSpec, BenchmarkConfig


@dataclass
class BenchmarkBackendContext:
    """Mutable context shared across backends during one benchmark run."""

    shared: dict[str, Any]


class BenchmarkBackend(ABC):
    """Fixed contract implemented by each benchmark backend."""

    backend_name: str

    def __init__(self, backend_config: dict[str, Any] | None = None):
        self.backend_config = dict(backend_config or {})

    def prepare(
        self,
        config: BenchmarkConfig,
        agent_specs: list[AgentSpec],
        context: BenchmarkBackendContext,
    ) -> None:
        """Perform backend-level setup before per-agent episodes run."""

    @abstractmethod
    def run_agent(
        self,
        agent_spec: AgentSpec,
        config: BenchmarkConfig,
        seed: int,
        context: BenchmarkBackendContext,
    ) -> list[dict[str, Any]]:
        """Execute one agent/seed run and emit standardized benchmark records."""

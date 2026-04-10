"""Orchestrates benchmark runs across explicit benchmark backends."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from benchmark.backend import BenchmarkBackendContext
from benchmark.benchmark_config import BenchmarkConfig


def _load_trust_backend():
    from benchmark.trust_backend import TrustBackend

    return TrustBackend


def _load_toy_gridworld_backend():
    from benchmark.toy_gridworld_backend import ToyGridworldBackend

    return ToyGridworldBackend


def _load_cvc_backend():
    from benchmark.cvc_local_backend import CvCLocalBackend

    return CvCLocalBackend


BACKEND_REGISTRY = {
    "trust": _load_trust_backend,
    "toy_gridworld": _load_toy_gridworld_backend,
    "cvc_local": _load_cvc_backend,
}


class BenchmarkRunner:
    """Run benchmark comparisons across configured backends and agent specs."""

    def __init__(self, config: BenchmarkConfig):
        self.config = config

    def _backend_instances(self):
        instances = {}
        for backend_name in self.config.backends:
            if backend_name not in BACKEND_REGISTRY:
                raise ValueError(f"Unknown benchmark backend '{backend_name}'. Available: {sorted(BACKEND_REGISTRY)}")
            factory = BACKEND_REGISTRY[backend_name]
            backend_cls = factory() if callable(factory) and not isinstance(factory, type) else factory
            instances[backend_name] = backend_cls(self.config.backend_configs.get(backend_name, {}))
        return instances

    def run_all(self) -> pd.DataFrame:
        all_records: list[dict] = []
        context = BenchmarkBackendContext(shared={})
        backend_instances = self._backend_instances()

        for backend_name, backend in backend_instances.items():
            agent_specs = [agent for agent in self.config.agents if agent.backend == backend_name]
            if not agent_specs:
                continue

            backend.prepare(self.config, agent_specs, context)
            for agent_spec in agent_specs:
                for seed_offset in range(self.config.num_replications):
                    seed = self.config.random_seed + seed_offset
                    all_records.extend(backend.run_agent(agent_spec, self.config, seed, context))

        return pd.DataFrame(all_records)

    def save_results(self, results: pd.DataFrame, path: str | None = None):
        if path is None:
            output_dir = Path(self.config.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            path = str(output_dir / "benchmark_results.csv")
        results.to_csv(path, index=False)
        return path

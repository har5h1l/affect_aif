"""Real local CvC backend executed through a Python 3.12 worker."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from benchmark.backend import BenchmarkBackend, BenchmarkBackendContext
from benchmark.benchmark_config import AgentSpec, BenchmarkConfig
from benchmark.observatory import ObservatoryClient


class CvCLocalBackend(BenchmarkBackend):
    """Runs real CoGames/CvC episodes in a separate Python 3.12 process."""

    backend_name = "cvc_local"

    def __init__(self, backend_config: dict[str, Any] | None = None):
        super().__init__(backend_config)
        self.python_bin = str(self.backend_config.get("python_bin", "python3.12"))
        self.mission = str(self.backend_config.get("mission", "machina_1"))
        self.num_agents = int(self.backend_config.get("num_agents", 8))
        self.max_steps = int(self.backend_config.get("max_steps", 1000))
        self.max_action_time_ms = int(self.backend_config.get("max_action_time_ms", 10000))
        self.device = str(self.backend_config.get("device", "cpu"))
        self.work_dir = self.backend_config.get("work_dir")

    def prepare(
        self,
        config: BenchmarkConfig,
        agent_specs: list[AgentSpec],
        context: BenchmarkBackendContext,
    ) -> None:
        observatory_config = dict(config.observatory or {})
        observatory_config.update(dict(self.backend_config.get("observatory", {})))
        if not observatory_config:
            return

        client = ObservatoryClient(
            base_url=str(observatory_config.get("base_url", "https://api.observatory.softmax-research.net")),
            token=observatory_config.get("token"),
        )
        season_name = observatory_config.get("season")
        if season_name in {None, "default"}:
            default_season = client.discover_default_season(
                tournament_type=observatory_config.get("tournament_type", "freeplay")
            )
            season_name = None if default_season is None else default_season["name"]
        if season_name is None:
            return

        compat_report = client.validate_season_compat(season_name, expected=observatory_config.get("expected_compat"))
        pool_name = observatory_config.get("pool")
        context.shared["observatory"] = {
            "season": client.get_season(season_name),
            "compat_report": compat_report,
            "pool_config": client.get_pool_config(season_name, pool_name) if pool_name else None,
        }
        if compat_report["matches"] is False:
            raise ValueError(
                f"Observatory compat mismatch for season '{season_name}': "
                f"expected {compat_report['expected']}, got {compat_report['actual']}."
            )

    def _make_output_path(self, agent_spec: AgentSpec, seed: int) -> Path:
        if self.work_dir:
            output_dir = Path(self.work_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            return output_dir / f"cvc_local_{agent_spec.name}_{seed}.json"
        temp_dir = Path(tempfile.mkdtemp(prefix="affect_aif_cvc_"))
        return temp_dir / f"cvc_local_{agent_spec.name}_{seed}.json"

    def run_agent(
        self,
        agent_spec: AgentSpec,
        config: BenchmarkConfig,
        seed: int,
        context: BenchmarkBackendContext,
    ) -> list[dict[str, Any]]:
        if agent_spec.kind != "policy_spec" or not agent_spec.policy_spec:
            raise ValueError("CvC local backend requires agents declared with kind='policy_spec'.")

        output_path = self._make_output_path(agent_spec, seed)
        cmd = [
            self.python_bin,
            "-m",
            "benchmark.cvc_local_worker",
            "--output",
            str(output_path),
            "--agent-name",
            agent_spec.name,
            "--policy-spec",
            agent_spec.policy_spec,
            "--mission",
            self.mission,
            "--seed",
            str(seed),
            "--num-agents",
            str(self.num_agents),
            "--max-steps",
            str(self.max_steps),
            "--max-action-time-ms",
            str(self.max_action_time_ms),
            "--device",
            self.device,
        ]
        if "observatory" in context.shared:
            observatory_payload = context.shared["observatory"]
            cmd.extend(
                [
                    "--season-name",
                    observatory_payload["season"]["name"],
                ]
            )

        timeout_s = int(self.backend_config.get("timeout_s", 600))
        # Ensure the repo root is on PYTHONPATH so the worker can import benchmark
        repo_root = str(Path(__file__).resolve().parent.parent.parent)
        env = os.environ.copy()
        env["PYTHONPATH"] = repo_root + os.pathsep + env.get("PYTHONPATH", "")
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=timeout_s, env=env)
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"CvC local worker timed out after {timeout_s}s.\nCommand: {' '.join(cmd)}") from exc
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                f"CvC local worker failed.\nCommand: {' '.join(cmd)}\nstdout:\n{exc.stdout}\nstderr:\n{exc.stderr}"
            ) from exc

        return json.loads(output_path.read_text())

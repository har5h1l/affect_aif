"""Tests for the real CvC local backend orchestration."""

import json
import subprocess
from pathlib import Path

from benchmarks.core.backend import BenchmarkBackendContext
from benchmarks.core.benchmark_config import BenchmarkConfig
from benchmarks.cvc.local_backend import CvCLocalBackend


def test_cvc_local_backend_runs_python_worker_and_reads_standardized_records(monkeypatch, tmp_path):
    config = BenchmarkConfig.from_dict(
        {
            "backends": ["cvc_local"],
            "agents": [
                {
                    "name": "teammate_reliability",
                    "backend": "cvc_local",
                    "kind": "policy_spec",
                    "policy_spec": "class=benchmarks.cvc.policy.TeammateReliabilityPolicy",
                }
            ],
            "backend_configs": {
                "cvc_local": {
                    "python_bin": "python3.12",
                    "mission": "machina_1",
                    "num_agents": 8,
                    "max_steps": 250,
                    "work_dir": str(tmp_path),
                }
            },
        }
    )
    backend = CvCLocalBackend(config.backend_configs["cvc_local"])
    context = BenchmarkBackendContext(shared={})

    def fake_run(cmd, check, capture_output, text, timeout=None, env=None):
        output_path = Path(cmd[cmd.index("--output") + 1])
        output_path.write_text(
            json.dumps(
                [
                    {
                        "schema_version": 2,
                        "backend": "cvc_local",
                        "scenario": "machina_1",
                        "agent_name": "teammate_reliability",
                        "seed": 42,
                        "episode_id": "cvc_local:teammate_reliability:42",
                        "step": 250,
                        "reward": 1.5,
                    }
                ]
            )
        )
        return subprocess.CompletedProcess(cmd, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    records = backend.run_agent(config.agents[0], config, seed=42, context=context)

    assert records[0]["backend"] == "cvc_local"
    assert records[0]["reward"] == 1.5

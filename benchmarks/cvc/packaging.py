"""Helpers for writing submission-shaped policy bundles for local CvC policies."""

from __future__ import annotations

import json
from pathlib import Path


def _parse_policy_spec(policy_spec: str) -> dict:
    class_path = None
    data_path = None
    init_kwargs: dict[str, str] = {}

    for entry in [part.strip() for part in policy_spec.split(",") if part.strip()]:
        if "=" not in entry:
            raise ValueError(f"Unsupported policy entry '{entry}'. Expected key=value pairs.")
        key, value = entry.split("=", 1)
        if key == "class":
            class_path = value
        elif key == "data":
            data_path = value
        elif key.startswith("kw."):
            init_kwargs[key[3:]] = value
        else:
            raise ValueError(f"Unsupported policy entry '{key}'.")

    if not class_path:
        raise ValueError("Policy spec must include class=<module.ClassName>.")

    return {
        "class_path": class_path,
        "data_path": data_path,
        "init_kwargs": init_kwargs,
    }


def write_policy_bundle(output_dir: str | Path, policy_spec: str, setup_script: str | None = None) -> Path:
    """Write a submission-compatible policy bundle directory."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    payload = _parse_policy_spec(policy_spec)
    payload["setup_script"] = setup_script

    spec_path = output_path / "policy_spec.json"
    spec_path.write_text(json.dumps(payload, indent=2))
    return spec_path

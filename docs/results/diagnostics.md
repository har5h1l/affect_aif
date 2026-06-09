# Diagnostic Result Provenance

Diagnostic results are informative non-paper evidence. They are kept separate
from paper results so the reproduction path remains short while reviewer
controls and mechanism probes remain auditable.

## Tracked Diagnostic Cards

| Folder | Config source | Raw source | What it supports |
|---|---|---|---|
| `results/diagnostics/policy_openness/` | `configs/diagnostics/h0_policy_openness/graded_choice.toml` | `results/diagnostics/spine_smoke/raw/h0/graded_choice/results.csv` | H0 policy-openness provenance: affective precision needs a movable policy posterior. |
| `results/diagnostics/deployment/` | `configs/diagnostics/h2_deployment/lesion_open_regime.toml` | `results/diagnostics/spine_smoke/raw/h2/lesion_open_regime/results.csv` | H2 tracked-only lesion provenance: tracking and deployment are separable. |
| `results/diagnostics/locality/` | `configs/diagnostics/h3_locality/global_beta_locality_probe.toml`, `configs/diagnostics/h3_locality/global_beta_focal_switch_probe.toml` | `results/diagnostics/locality/raw/.../results.csv` | H3 locality provenance: partner-local beta gives cleaner signal routing than shared beta in probes. |

## Server-Only Diagnostic Raw Buckets

The server cleanup retained additional diagnostic raw buckets under
`results/diagnostics/`, including precision-sensitivity, social-allocation,
candidate-fix, and HESP-surprise probes. They are not tracked in git and should
not be treated as paper evidence unless a future manuscript revision explicitly
promotes them.

## Refresh Rule

Do not rewrite interpreted diagnostic prose from newly generated outputs without
explicit user approval. Structural refreshes such as manifest path corrections
are fine; new scientific claims need review.

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
| `results/diagnostics/model_fitness/` | `configs/diagnostics/h1_model_fitness/reliability_vs_reward_confirm.toml` | `results/diagnostics/model_fitness/raw/h1/reliability_vs_reward_confirm/results.csv` | Binary model-fitness provenance retained for supplementary checks; omitted from the main paper because the binary policy posterior is not an informative behavioral regime. |
| `results/diagnostics/social_allocation/` | `configs/diagnostics/h4_social_allocation/partner_choice_confirm.toml` | `results/diagnostics/social_allocation/raw/partner_choice_confirm_20260609/h4/partner_choice_confirm/results.csv` | Binary H4 partner-choice confirmation retained as boundary provenance; omitted from the main paper because the current paper partner-selection readout is graded. |

The model-fitness diagnostic uses `payoff = "binary"` and 200-round episodes.
Its payoff summaries are full-episode binary cumulative totals, not graded-game
payoffs and not active-encounter windows.

The social-allocation diagnostic also uses `payoff = "binary"` and 200-round
agent-choice episodes. It should not be used to update Section 3.3 paper
numbers, which come from `configs/paper/03_partner_selection.toml`.

## Additional Diagnostic Raw Buckets

Additional diagnostic raw buckets may exist outside git under
`results/diagnostics/`, including precision-sensitivity, candidate-fix, and
HESP-surprise probes. They are not tracked in git and should not be treated as
paper evidence unless a future manuscript revision explicitly promotes them.

## Refresh Rule

Do not rewrite interpreted diagnostic prose from newly generated outputs without
explicit user approval. Structural refreshes such as manifest path corrections
are fine; new scientific claims need review.

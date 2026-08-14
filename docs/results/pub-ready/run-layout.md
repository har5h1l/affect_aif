# Run layout and comparability

## The three packets

| Review name | Raw result root | Action contract | Charge transform | Rows | Role |
|---|---|---|---|---:|---|
| Historical manuscript packet | `results/paper/` | Earlier factorized stance/executed-action controls | Squared | 234,400 | Cross-reference for the submitted manuscript |
| Shared action, squared charge | `results/rebaseline_shared_action_policy_fix_6b7d889_local/squared_charge_20260811/` | One shared six-valued behavioral action | Squared | 234,400 | Main corrected rebaseline |
| Shared action, linear charge | `results/rebaseline_shared_action_policy_fix_6b7d889_local/linear_charge_20260812/` | Same shared action | Linear | 234,400 | Matched sensitivity analysis |

All tables have the expected row counts and no duplicate
`experiment_id, variant_id, seed, round` keys. The two corrected packets have
identical complete key sets across their ten final tables. Both enumerate
1,296 policies per partner and 5,184 partner-policy candidates. The linear
batch metadata records one worker and `charge_transform=linear`.

## What the action correction means

The historical runtime independently planned a stance-transition control and
an executed investment control. The corrected runtime treats these as one
shared six-level behavioral action, so a planned stance transition cannot
diverge from the investment actually executed. This changes the policy space
and can change trajectories; the corrected outcomes must therefore be compared
with the manuscript packet descriptively, rather than presented as a simple
replication.

## Why the directories were not physically renamed

`squared_charge_20260811` and `linear_charge_20260812` are the batch IDs
written into each run's logs, metadata, and checkpoint manifests. Moving them
would make that provenance stale. The review names above are the stable
human-facing labels; the raw run IDs remain intact for auditability.

## Config-to-table map

| Results section | Config | Historical table | Corrected table(s) |
|---|---|---|---|
| 3.1 Predictability over payoff | `configs/paper/01_predictability_value.toml` | `01_predictability_value/raw/results.csv` | `predictability_value/predictability_value/results.csv` |
| 3.2 Deployment pathway | `configs/paper/02_deployment_ablation.toml` | `02_deployment_ablation/raw/results.csv` | `deployment_ablation/deployment_ablation/results.csv` |
| 3.3 Partner selection | `configs/paper/03_partner_selection.toml` | `03_partner_selection/raw/results.csv` | `partner_selection/partner_selection/results.csv` |
| 3.4 Abrupt betrayal | `configs/paper/04_betrayal_adaptation.toml` | `04_betrayal_adaptation/raw/results.csv` | `betrayal_adaptation/betrayal_adaptation/results.csv` |
| 3.5 Gain/profile suite | `configs/paper/05a`--`05c` | `05a`--`05c` raw tables | `alpha_sweep/`, `prior_factorial/`, and `forgiveness/` final tables |


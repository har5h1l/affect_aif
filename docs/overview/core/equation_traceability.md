# Equation-To-Code Traceability

This note maps the four main-text equations in
`docs/manuscript/sections/02_method.tex` to the implementation paths that
execute them. It is a routing document: use it to audit whether manuscript math,
runtime behavior, and focused tests still agree.

## Scope

- Eq. 1--4 below refer to the main-text equations in Section 2, not the
  appendix-only equations in Appendix C.
- The beta tracker is an auxiliary runtime state outside the pymdp hidden-state
  factors. POMDP matrix construction remains in `tasks/trust/pomdp.py` and
  `tasks/trust/pomdp_matrices.py`.
- `affect = tracked_only` intentionally updates beta while holding
  `gamma_k = gamma_base`; this is a lesion of Eq. 3 deployment, not a change to
  Eq. 1--2.

## Main Trace

| Equation | Manuscript label | Code path | Notes | Focused tests |
|---|---|---|---|---|
| Eq. 1 | `eq:epsilon` | `tasks/trust.runtime.update_beta_after_observation(...)` indexes the selected partner-response probability, then calls `tasks.trust.affect.surprise_from_probability(...)`. Predicted partner-response probabilities are carried on `Decision.predicted_partner_action_probs` from `tasks.trust.runtime.select_decision(...)`. | Implements `epsilon = -log P(observed action | pre-update partner-local beliefs)`. The runtime computes this before beta update and logs the per-partner signal in `PartnerBank.latest_surprise`. | `tests/test_trust_affect.py::test_surprise_uses_negative_log_likelihood`; `tests/test_native_pymdp_affect.py::test_beta_update_uses_prediction_probability`; `tests/test_native_pymdp_affect.py::test_beta_update_logs_surprisal_signal` |
| Eq. 2 | `eq:charge` | `tasks.trust.affect.DiscreteBetaState.update(...)` calls private helper `_affective_charge(...)`; defaults come from `LOG_SURPRISE_BASELINE_SQ` and variant/config fields `alpha_charge` and `sigma_0_sq`. | Implements `phi = alpha * (sigma_0_sq - epsilon^2)`. Low surprisal produces positive charge and shifts mass toward lower beta; high surprisal produces negative charge and shifts mass toward higher beta. | `tests/test_trust_affect.py::test_log_surprise_baseline_matches_fifty_fifty_prediction`; `tests/test_trust_affect.py::test_low_surprise_decreases_beta_rate`; `tests/test_trust_affect.py::test_high_surprise_increases_beta_rate` |
| Eq. 3 | `eq:gamma_update` | `tasks.trust.affect.DiscreteBetaState.expected_beta(...)` returns posterior means; `tasks.trust.runtime.gamma_for_partner(...)` maps each mean beta to `gamma_base / E[beta_k]`; `_infer_partner_policy(...)` and `_infer_agent_choice_policies_batched(...)` set pymdp policy precision before `infer_policies(...)`. | Implements the inverse-beta convention. `affect_mode in {"none", "decouple", "fixed"}` returns `gamma_base`; `affect_mode == "global"` routes all partners through the shared beta entity. | `tests/test_native_pymdp_affect.py::test_gamma_for_partner_uses_hesp_inverse_beta`; `tests/test_native_pymdp_affect.py::test_decouple_mode_does_not_modulate_gamma`; `tests/test_native_pymdp_affect.py::test_global_mode_uses_shared_beta_for_all_partners` |
| Eq. 4 | `eq:centered_policy_scores` | `tasks.trust.runtime._agent_choice_policy_arrays(...)` computes each partner's mean policy score and returns `centers + gamma_k * (scores - centers)` as candidate logits; `select_decision(...)` softmaxes those logits across partner-policy candidates. | Implements centered cross-partner policy comparison, so `gamma_k` sharpens or flattens within-partner policy commitment without directly shifting the partner-level mean score. | `tests/test_pymdp_trust_agent.py::test_agent_choice_policy_arrays_preserve_candidate_order_and_logits`; `tests/test_pymdp_trust_agent.py::test_agent_choice_high_precision_partner_is_not_penalized_when_scores_match` |

## Supporting Runtime Wiring

- `experiments/trust/factory.py` constructs `DiscreteBetaState` from expanded
  TOML variant fields and attaches it to `PartnerBank.beta`.
- `experiments/trust/spec.py` defines the public variant knobs that flow into
  the trace: `alpha_charge`, `sigma_0_sq`, `initial_beta`, `beta_prior`,
  `beta_persistence`, `beta_levels`, and `gamma`.
- `tasks/trust/runtime.py` owns the action-perception order: policy selection,
  environment observation, partner-state update, beta update, and diagnostic
  snapshots.

## Appendix-C Filter Details

Appendix C expands the beta posterior filter used inside
`DiscreteBetaState.update(...)`:

| Appendix equation | Code path |
|---|---|
| `eq:persistence` | `_build_transition_matrix(...)` creates the tridiagonal transition; `DiscreteBetaState.update(...)` applies `self._transition @ self.posteriors[entity_idx]`. |
| `eq:pseudo_lik` | `DiscreteBetaState.update(...)` computes `log_likelihood = charge * (1 / beta_levels)` before normalization. |
| `eq:posterior_update` | `DiscreteBetaState.update(...)` multiplies normalized likelihood by the transitioned prior, renormalizes, and stores both `self.posteriors[...]` and `self.betas[...]`. |

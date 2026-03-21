# Benchmark Results Summary

## Experiments Run

| Experiment | Config | Agents | Seeds | Rounds | Key Feature |
|-----------|--------|--------|-------|--------|-------------|
| Resource Sharing (comprehensive) | `benchmark_comprehensive.json` | 12 | 50 | 200 | Full agent roster, standard conditions |
| Betrayal (comprehensive) | `benchmark_betrayal_comprehensive.json` | 10 | 50 | 200 | Partner switch at round 100, random assignment |
| Noisy Observations | `benchmark_noisy.json` | 7 | 50 | 200 | observation_noise=0.15 |
| Resource Sharing (50r) | `benchmark_resource_sharing.json` | 10 | 50 | 100 | Shorter episodes |
| Betrayal Fair (50r) | `benchmark_betrayal_fair.json` | 10 | 50 | 100 | Partner switch at round 50 |

## Key Findings

### 1. Terminal Value Augmentation Significantly Outperforms All Alternatives

Across all scenarios, agents with terminal value augmentation (affective_shallow, reward_avg_shallow) significantly outperform both:
- Baseline AIF agents at any planning depth (p < 0.003, effect size r = 0.31-0.80)
- All standard baselines (p < 10^-6, effect size r > 0.52)

| Scenario | Terminal Value Agents | Baseline AIF | Best Baseline |
|----------|---------------------|-------------|---------------|
| Resource (200r) | ~575 | ~527 | 541 (grim_trigger) |
| Betrayal (200r) | ~617 | ~568 | 589 (grim_trigger) |
| Noisy (200r) | ~573 | ~526 | 441 (random) |

### 2. Terminal Values Substitute for Planning Depth

Planning depth beyond horizon 2 provides zero additional benefit:

| Agent | Horizon | Mean Reward (200r) |
|-------|---------|-------------------|
| shallow_no_affect | 2 | 527.32 |
| intermediate_3 | 3 | 526.76 |
| intermediate_4 | 4 | 526.16 |
| deep_no_affect | 8 | 526.24 |
| affective_shallow (h=2 + terminal values) | 2 | 574.84 |

Terminal values at horizon 2 outperform pure planning at horizon 8 by ~9%.

### 3. Precision Modulation Channel Is Structurally Inert

Two independent lines of evidence:

**a. Lesion has no effect:**
- lesioned_shallow = shallow_no_affect in every scenario (identical to floating point)
- lesioned_shallow = 527.32, shallow_no_affect = 527.32 (resource sharing, 200r)

**b. Affect-based precision ≈ simple reward averaging:**
- affective_shallow ≈ reward_avg_shallow everywhere (p > 0.80, not significant)
- 574.84 vs 573.48 (resource sharing), 616.84 vs 616.44 (betrayal)

This is consistent with the known EFE softmax saturation: median EFE gap = 10.83, making any precision scaling a no-op (91.5% of rounds have policy entropy < 0.01).

### 4. Adaptation After Betrayal

All AIF agents recover type identification accuracy within 4 rounds after a partner switch. No differentiation across AIF variants:

| Agent | Pre-switch Payoff | Post-switch Payoff | Adaptation Speed |
|-------|------------------|--------------------|-----------------|
| affective_shallow | 3.74 | 2.43 | 4 rounds |
| reward_avg_shallow | 3.73 | 2.43 | 4 rounds |
| deep_no_affect | 3.49 | 2.20 | 4 rounds |
| shallow_no_affect | 3.49 | 2.20 | 4 rounds |
| grim_trigger | 3.45 | 2.43 | N/A |
| tit_for_tat | 2.37 | 1.70 | N/A |

### 5. Baseline Strategy Equivalences

In binary-action prisoner's dilemma:
- **grim_trigger = win_stay_lose_shift** (WSLS with threshold=0 is equivalent to grim trigger)
- **tit_for_tat = pavlov** (both mirror last partner action in binary PD)

### 6. Observation Noise Does Not Differentiate Mechanisms

Adding 15% observation noise degrades type ID accuracy (from ~58% to ~47%) but affects all mechanisms equally. It does not differentiate precision-based tracking from reward averaging.

## Agent Tier Structure (Stable Across All Scenarios)

| Tier | Agents | Mechanism | Typical Reward (200r) |
|------|--------|-----------|---------------------|
| 1 | affective_shallow, reward_avg_shallow | Terminal value augmentation | ~575 |
| 2a | grim_trigger, win_stay_lose_shift | Retaliatory defection | ~541 |
| 2b | shallow/deep/intermediate/lesioned_no_affect | Baseline active inference | ~527 |
| 3 | random | Uniform random | ~436 |
| 4 | tit_for_tat (=pavlov), q_learning | Cooperative/adaptive | ~421 |

## Statistical Rigor

- All pairwise comparisons use Mann-Whitney U tests with rank-biserial effect sizes
- 95% confidence intervals computed via bootstrapped standard errors
- 50 independent seeds per agent per scenario
- 37/66 pairwise comparisons significant at p < 0.05 (comprehensive)
- Tier 1 vs Tier 2b: p < 0.003, |r| > 0.31
- Tier 1 vs Tier 3+: p < 10^-11, |r| > 0.76

## Interpretation for Paper

The benchmark demonstrates that:
1. **Terminal value augmentation is a genuine computational shortcut** — it provides the benefit of deep planning at shallow computational cost
2. **The active channel is terminal values, not precision modulation** — the softmax saturation finding is confirmed by the benchmark (lesion = no-affect, affect ≈ reward_avg)
3. **For clinical differentiation to emerge, the precision channel must be de-saturated** — either by reducing EFE magnitudes or by routing beta through alternative channels (observation precision, prior weighting)
4. **The benchmark infrastructure is robust** — consistent results across scenarios, noise levels, and episode lengths

## Files

### Results
- `results/benchmark_comprehensive/` — Primary results (resource sharing, 200 rounds)
- `results/benchmark_betrayal_comprehensive/` — Primary betrayal results (200 rounds, switch at 100)
- `results/benchmark_noisy/` — Noisy observation variant
- `results/benchmark_resource_sharing/` — Shorter resource sharing (100 rounds)
- `results/benchmark_betrayal_fair/` — Shorter betrayal (100 rounds, switch at 50)

### Analysis
Each results directory contains:
- `benchmark_results.csv` — Raw per-round data
- `benchmark_report.txt` — Comparison report
- `agent_summary.csv` — Per-agent statistics with CIs
- `pairwise_tests.csv` — All pairwise Mann-Whitney U tests
- `time_series_payoff.csv` — Rolling mean payoff over rounds
- `time_series_cooperation.csv` — Rolling cooperation rate over rounds
- `adaptation_analysis.csv` — Pre/post switch analysis (betrayal only)
- `analysis_report.txt` — Full analysis text report

### Configs
- `affect_aif/configs/benchmark_comprehensive.json`
- `affect_aif/configs/benchmark_betrayal_comprehensive.json`
- `affect_aif/configs/benchmark_noisy.json`
- `affect_aif/configs/benchmark_resource_sharing.json`
- `affect_aif/configs/benchmark_betrayal_fair.json`

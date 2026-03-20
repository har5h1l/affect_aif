# Benchmarking Integration: Softmax & MettaGrid

## Investigation Summary

> **Key finding**: Softmax co-founder Adam Goldstein published active inference papers (with Chris Fields and Lars Sandved Smith: "Making the Thermodynamic Cost of Active Inference Explicit") and worked in Michael Levin's lab on active inference agents. The intellectual overlap with affect_aif is direct, not incidental.
>
> **Integration target**: CoGames (`pip install cogames`) is Softmax's high-level benchmark platform — the "Alignment League Benchmark" (ALB). It has a Python env API, CLI tools, tournament leaderboard, and policy submission. This is the right integration point, not raw MettaGrid.

### Softmax (softmax.com)

Softmax is an AI alignment research lab co-founded by Emmett Shear (Twitch), David Bloomin, and Adam Goldstein, focused on **"organic alignment"** — studying how agents learn to cooperate, specialize, and form collectively intelligent systems through multi-agent reinforcement learning.

Key relevance to affect_aif:
- They study **cooperation emergence** in multi-agent settings — directly overlapping with our trust game research
- Their research direction (how agents develop trust, betrayal, loyalty) maps closely to our per-partner metacognitive precision tracking
- David Bloomin is the creator of MettaGrid and co-authored "Neural MMO 2.0" (NeurIPS 2023)
- Funded by a16z, Lionheart Ventures, and Plural

### MettaGrid (github.com/Metta-AI/mettagrid)

MettaGrid is a high-performance C++ gridworld environment with Python bindings for studying emergent cooperation and social behaviors in multi-agent RL. Key specs:

- **Language**: C++ core with pybind11 Python bindings
- **APIs**: PufferLib adapter (`MettaGridPufferEnv`) and PettingZoo adapter (`MettaGridPettingZooEnv`)
- **Dependencies**: Python 3.12, Bazel 9.0+, C++20 compiler
- **License**: MIT
- **Author**: David Bloomin / Softmax organization

**Environment features**:
- Gridworld with agents, walls, resources, custom objects
- Resource management (energy, harvesting, capacity limits)
- Combat system (weapon/armor/defense, freeze mechanics, loot transfer)
- "Vibe" system — behavioral modes that determine interaction patterns
- Configurable via Pydantic-based YAML configs
- Procedural map generation (BSP, maze, spiral, wave function collapse)
- Handler-based event system for composable game logic

### CoGames (github.com/Metta-AI/cogames)

CoGames is Softmax's high-level benchmark platform built on MettaGrid. It provides the **Alignment League Benchmark (ALB)** — a tournament system for evaluating multi-agent cooperation.

- **Install**: `pip install cogames`
- **CLI**: `cogames play`, `cogames missions`, `cogames upload`, `cogames login`
- **API**: `CogVsClipsEnv(mission, num_agents)` with standard `reset()/step()`
- **Flagship game**: "Cogs vs Clips" — cooperative territory control with role specialization (miner, aligner, scrambler, scout)
- **Variant system**: Composable game rules that modify mechanics, victory conditions, etc.
- **Policies**: URI-based system (`class=lstm`, `class=random`, custom policy classes)
- **Tournament**: Season-based play-ins, team stages, leaderboard rankings
- **Built-in baselines**: random, LSTM, starter_agent, plus scripted policies in cogames-agents

### cogames-agents (github.com/Metta-AI/cogames-agents)

Scripted baseline policies for CoGames: role-based (miner, scout, aligner, scrambler), CogsGuard variants, teacher policies. 85% Python / 12% Nim.

### Active Inference Connection

Adam Goldstein (Softmax co-founder) published "Making the Thermodynamic Cost of Active Inference Explicit" with Chris Fields and Lars Sandved Smith. He worked in Michael Levin's lab on active inference agents before co-founding Softmax. The intellectual lineage from active inference to Softmax's "organic alignment" is direct.

### Cortex (github.com/Metta-AI/cortex)

Modular library for building recurrent backbones and agent memory systems. Relevant for understanding Softmax's agent architecture.

**Key difference from our trust game**: MettaGrid is a spatially-embedded, resource-management gridworld with continuous agent movement, combat, and open-ended dynamics. Our trust game is a structured repeated game with discrete actions (cooperate/defect) and explicit partner type inference. These are fundamentally different environment paradigms.

---

## Integration Options

### Option A: MettaGrid as a Benchmark Environment (Full Integration)

**What**: Wrap our active inference agents to operate in MettaGrid, replacing the trust game environment entirely for benchmarking.

**Approach**:
- Create an adapter layer in `affect_aif/environment/mettagrid_adapter.py` that translates MettaGrid observations/actions into our agent's expected interface
- Map MettaGrid's resource-sharing and combat interactions to cooperation/defection signals
- Run our agents (vanilla, affective, lesioned) in MettaGrid alongside RL baselines

**Pros**:
- Tests our agents in a richer, spatially-embedded environment
- Enables direct comparison with RL agents trained in the same environment
- MettaGrid's "vibe" system has conceptual overlap with our affect/precision tracking
- Publication potential: "Active inference agents in multi-agent gridworlds"

**Cons**:
- **Major engineering lift**: Our agents expect structured POMDP observations (partner type beliefs, discrete actions); MettaGrid provides pixel/feature grid observations
- Requires fundamentally rethinking the generative model — current A/B/C/D matrices don't map to gridworld dynamics
- MettaGrid requires Bazel 9.0+, C++20, Python 3.12 — heavy dependency chain
- Risk of scope creep: this is essentially a new research project, not a benchmark of the existing system

**Estimated effort**: 4-8 weeks of development

### Option B: MettaGrid-Inspired Trust Game Extension

**What**: Extract design patterns from MettaGrid to enrich our existing trust game environment while keeping our agent architecture intact.

**Approach**:
- Add resource management dynamics to the trust game (agents have "energy" budgets)
- Add spatial partner selection (agents choose who to interact with based on proximity/history)
- Add a "vibe" mechanism as an observable signal that maps to partner type
- Implement as a new environment class `affect_aif/environment/enriched_trust_game.py`

**Pros**:
- Maintains our existing agent architecture and generative model
- Adds ecological validity without breaking the POMDP structure
- Incremental: can add features one at a time
- Tests whether our findings generalize to richer dynamics

**Cons**:
- Not a direct benchmark against MettaGrid/Softmax's work
- Still a custom environment, not a standard benchmark

**Estimated effort**: 2-3 weeks

### Option C: Parallel Benchmark Track (Recommended)

**What**: Create a clean benchmarking module that runs our agents in both our trust game and a simplified MettaGrid scenario, with a common metrics framework for comparison.

**Approach**:
1. Create `affect_aif/benchmark/` module with:
   - `benchmark_runner.py` — orchestrates runs across environments
   - `mettagrid_wrapper.py` — wraps MettaGrid's PettingZoo API into our agent interface
   - `metrics.py` — common metrics (cooperation rate, partner inference accuracy, cumulative reward, social welfare)
   - `baselines.py` — simple RL baselines (random, tit-for-tat, Q-learning) for comparison

2. Design a **simplified MettaGrid scenario** focused on cooperation:
   - Small grid, 4-8 agents, resource sharing task
   - Map MettaGrid actions to {cooperate, defect, neutral}
   - Track partner-specific interaction histories

3. Run our agent suite (C1-C12) in both environments, compare:
   - Does per-partner precision tracking help in spatially-embedded settings?
   - Does the affect advantage persist outside structured trust games?
   - How do our agents compare to RL baselines on cooperation metrics?

**Pros**:
- Clean separation: benchmarking code doesn't pollute core research code
- Answers the generalizability question directly
- Provides comparison against RL baselines
- MettaGrid's PettingZoo API is the standard multi-agent interface
- Publishable: "Does metacognitive precision tracking generalize beyond trust games?"

**Cons**:
- Still requires mapping between paradigms (gridworld → POMDP)
- MettaGrid dependency adds build complexity
- Simplified MettaGrid scenario may not capture full environment richness

**Estimated effort**: 3-5 weeks

### Option D: Evaluation-Only (Lightest Touch)

**What**: Don't integrate MettaGrid into the codebase. Instead, document a comparison framework and run our agents against published MettaGrid baselines on shared metrics.

**Approach**:
- Use MettaGrid's published baseline results (Hugging Face: metta-ai/baseline.v0.5.2)
- Define shared cooperation/social welfare metrics
- Run our agents in our trust game, extract comparable metrics
- Write a comparison analysis without code integration

**Pros**:
- No new dependencies
- No engineering risk
- Can be done immediately
- Focuses effort on the current phase (Phase 3/4)

**Cons**:
- Not a direct comparison (different environments)
- Less compelling than running in the same environment
- Doesn't test generalizability

**Estimated effort**: 1 week

---

## Recommendation

**Option C (Parallel Benchmark Track)** balances rigor with feasibility. It:
- Keeps the core codebase clean (new `benchmark/` module)
- Actually tests generalizability in MettaGrid
- Provides RL baselines for comparison
- Doesn't require rearchitecting the generative model
- Produces a clear publishable result

However, this should be **Phase 5+ work** — after the current theory tightening (Phase 3) and variational beta extension (Phase 4) are complete. The current trust game results are the foundation; MettaGrid benchmarking extends the story.

If you want something sooner, **Option D** can be done in parallel with current phase work as a documentation exercise.

---

## Implementation Status (Option C Selected)

The parallel benchmark track has been implemented in `affect_aif/benchmark/`. All components work without CoGames/MettaGrid installed (optional dependencies).

### Module Structure

```
affect_aif/benchmark/
    __init__.py                  # Lazy imports, availability checks
    compat.py                    # Optional dependency guards
    baselines.py                 # RandomAgent, TitForTatAgent, WinStayLoseShiftAgent, QLearningAgent
    common_metrics.py            # cooperation_rate, cumulative_payoff, type_id_accuracy, etc.
    interaction_tracker.py       # Classifies gridworld events as cooperate/defect
    observation_encoder.py       # Gridworld state -> POMDP observation
    cogames_adapter.py           # CoGamesTrustAdapter: gridworld -> trust game interface
    scenarios.py                 # Predefined cooperation scenarios
    scripted_partners.py         # Cooperator/reciprocator/exploiter gridworld policies
    aif_policy.py                # Wraps AIF agents as CoGames-compatible policies
    benchmark_config.py          # BenchmarkConfig + agent registry
    benchmark_runner.py          # Orchestrates cross-environment runs
    comparison.py                # Transfer analysis and reporting

scripts/run_benchmark.py         # CLI entry point
```

### Usage

```bash
# Run with baselines only (no external deps needed)
python scripts/run_benchmark.py --agents random tit_for_tat --replications 5 --rounds 50

# Compare AIF agents against baselines in both environments
python scripts/run_benchmark.py --agents affective_shallow shallow_no_affect random tit_for_tat \
    --replications 10 --rounds 100 --output-dir results/benchmark

# Trust game only
python scripts/run_benchmark.py --trust-game-only --agents affective_shallow random

# From config file
python scripts/run_benchmark.py --config benchmark_config.json
```

### Available Agents

| Name | Type | Description |
|------|------|-------------|
| `deep_no_affect` | AIF (C1) | Deep planner, no affect |
| `affective_shallow` | AIF (C2) | Shallow + per-partner precision tracking |
| `lesioned_shallow` | AIF (C3) | Shallow + affect but decoupled |
| `shallow_no_affect` | AIF (C4) | Shallow baseline |
| `reward_avg_shallow` | AIF (C5) | Shallow + reward averaging |
| `alexithymia` | AIF (C9) | Blunted affect pathology |
| `borderline` | AIF (C10) | Volatile affect pathology |
| `depression` | AIF (C11) | Low baseline beta pathology |
| `random` | Baseline | Uniform random |
| `tit_for_tat` | Baseline | Mirror partner's last action |
| `win_stay_lose_shift` | Baseline | Repeat on win, switch on loss |
| `q_learning` | Baseline | Per-partner tabular Q-learner |

### Scenarios

| Name | Grid | Partners | Description |
|------|------|----------|-------------|
| `resource_sharing` | 16x16 | 4 | Standard cooperation test |
| `betrayal_arena` | 16x16 | 2 | Partner switches from cooperator to exploiter |
| `large_group` | 32x32 | 8 | Scaling test |

### Next Steps

1. **Install CoGames**: `pip install cogames` and test full gridworld integration
2. **Run first benchmark**: Compare C1/C2/C4 against baselines in both environments
3. **Tune ticks_per_round**: Sensitivity analysis of temporal bridging parameter
4. **Submit to Alignment League**: Wrap AIF policy for leaderboard submission
5. **Publish comparison**: "Does metacognitive precision tracking generalize beyond trust games?"

---

## Decision Points

1. **Which option?** A (full), B (inspired extension), C (parallel benchmark), or D (evaluation-only)
2. **When?** Now (pausing current phase work) or later (Phase 5+)
3. **MettaGrid scenario design**: If C, what cooperation scenario should we design in MettaGrid?
4. **RL baselines**: Which baselines to include for comparison?

---

## Sources

- [Softmax — Scaling Alignment](https://softmax.com/)
- [Softmax, Emmett Shear's new AI startup (LessWrong)](https://www.lesswrong.com/posts/QGQiCuE33iHFv9jkv/softmax-emmett-shear-s-new-ai-startup-focused-on-organic)
- [Core Memory: Emmett Shear Is Back](https://www.corememory.com/p/exclusive-emmett-shear-is-back-with-softmax)
- [MettaGrid on PyPI](https://pypi.org/project/mettagrid/)
- [Metta-AI/mettagrid on GitHub](https://github.com/Metta-AI/mettagrid)
- [David Bloomin's site](https://daveey.github.io/)
- [Crunchy AI: Softmax's organic alignment](https://getcoai.com/news/crunchy-ai-softmaxs-organic-alignment-approach-draws-from-nature-to-reimagine-ai-human-collaboration/)
- [Emmett Shear on AI Alignment (ODSC)](https://odsc.medium.com/emmett-shear-on-ai-alignment-agency-and-raising-a-new-intelligence-f72d9f0f106b)

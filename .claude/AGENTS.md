## Subagent Delegation

Delegate mechanical work to subagents. Keep main thread for planning and review.

| Task | Agent |
|------|-------|
| Implement from plan | `code-writer` |
| Fix diagnosed bug | `code-writer` |
| Validate build/tests | `build-validator` |
| Simplify/cleanup code | `code-simplifier` |
| Run experiments | `experiment-runner` |
| Analyze results | `results-analyzer` |
| Design approach | `code-architect` |
| Review math/algorithms | `research-reviewer` |

When a task is mechanical (plan exists, approach is clear), dispatch a subagent
instead of doing it in the main thread. This keeps context clean and costs low.

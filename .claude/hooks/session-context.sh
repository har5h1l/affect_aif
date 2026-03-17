#!/bin/bash
# SessionStart hook: injects current research phase and state into context.
# This runs at the start of every Claude session so the AI knows where we are.

PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

context=""

# Current phase from long_term_plan.md
if [ -f "$PROJECT_DIR/docs/long_term_plan.md" ]; then
    phase_info=$(grep -A 3 -i "current phase\|## Phase" "$PROJECT_DIR/docs/long_term_plan.md" 2>/dev/null | head -5)
    if [ -n "$phase_info" ]; then
        context="${context}Current research phase:\n${phase_info}\n\n"
    fi
fi

# Last few commits for recent work context
if git -C "$PROJECT_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    recent=$(git -C "$PROJECT_DIR" log --oneline -3 2>/dev/null)
    if [ -n "$recent" ]; then
        context="${context}Recent commits:\n${recent}\n\n"
    fi
fi

# Conductor state if it exists
if [ -f "$PROJECT_DIR/conductor/STATE.md" ]; then
    next_session=$(grep -A 2 "Next Session Should" "$PROJECT_DIR/conductor/STATE.md" 2>/dev/null)
    if [ -n "$next_session" ]; then
        context="${context}Conductor state:\n${next_session}\n"
    fi
fi

if [ -n "$context" ]; then
    python3 -c "
import json, sys
ctx = '''$context'''
print(json.dumps({'additionalContext': f'[Session context from hooks] {ctx}'}))
"
fi

exit 0

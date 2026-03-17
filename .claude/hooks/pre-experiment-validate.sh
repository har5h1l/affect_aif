#!/bin/bash
# PreToolUse hook: validates that tests pass before running experiments.
# Blocks experiment scripts if pytest hasn't been run in this session.

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('command',''))" 2>/dev/null)

# Only check experiment-running commands
if echo "$COMMAND" | grep -qE 'scripts/run_experiment|scripts/run_preliminary|scripts/run_clinical'; then
    # Check if there's a recent pytest result (within last 10 minutes)
    PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
    MARKER="$PROJECT_DIR/.pytest_last_run"

    if [ -f "$MARKER" ]; then
        last_run=$(stat -f %m "$MARKER" 2>/dev/null || stat -c %Y "$MARKER" 2>/dev/null)
        now=$(date +%s)
        age=$((now - last_run))
        if [ "$age" -lt 600 ]; then
            # Tests ran recently, allow
            exit 0
        fi
    fi

    # Tests haven't been validated recently
    python3 -c "
import json
print(json.dumps({
    'hookSpecificOutput': {
        'hookEventName': 'PreToolUse',
        'permissionDecision': 'deny',
        'permissionDecisionReason': 'Safety invariant: run pytest before experiments. Execute: python -m pytest tests/ -v --tb=short'
    }
}))
"
    exit 0
fi

exit 0

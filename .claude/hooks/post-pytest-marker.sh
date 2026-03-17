#!/bin/bash
# PostToolUse hook: marks when pytest was last run successfully.
# Used by pre-experiment-validate.sh to enforce "tests before experiments".

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('command',''))" 2>/dev/null)

# If pytest just ran successfully, touch the marker
if echo "$COMMAND" | grep -qE 'pytest|python -m pytest'; then
    PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
    touch "$PROJECT_DIR/.pytest_last_run"
fi

exit 0

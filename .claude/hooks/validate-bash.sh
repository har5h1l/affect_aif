#!/bin/bash
# Pre-tool hook: validates Bash commands before execution.
# Blocks destructive patterns while allowing safe research operations.

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('command',''))" 2>/dev/null)

# Block destructive commands
if echo "$COMMAND" | grep -qE 'rm -rf /|rm -rf \.|:(){:|sudo rm|git push --force|git reset --hard'; then
  python3 -c "
import json
print(json.dumps({
    'hookSpecificOutput': {
        'hookEventName': 'PreToolUse',
        'permissionDecision': 'deny',
        'permissionDecisionReason': 'Blocked: destructive command pattern detected'
    }
}))
"
  exit 0
fi

# Block accidental deletion of results
if echo "$COMMAND" | grep -qE 'rm.*results/.*\.csv|rm.*results/.*\.parquet'; then
  python3 -c "
import json
print(json.dumps({
    'hookSpecificOutput': {
        'hookEventName': 'PreToolUse',
        'permissionDecision': 'deny',
        'permissionDecisionReason': 'Blocked: cannot delete result files (safety invariant)'
    }
}))
"
  exit 0
fi

exit 0

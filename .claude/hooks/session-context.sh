#!/usr/bin/env bash
# UserPromptSubmit hook: inject session context (phase, recent commits, conductor state).

PHASE=""
if [ -f "docs/long_term_plan.md" ]; then
    PHASE="$(grep -i "current.*phase\|phase.*current" docs/long_term_plan.md 2>/dev/null | head -1 || echo "")"
fi

RECENT_COMMITS="$(git log --oneline -5 2>/dev/null || echo "no git history")"

STATE=""
if [ -f "conductor/STATE.md" ]; then
    STATE="$(head -20 conductor/STATE.md 2>/dev/null || echo "")"
fi

if [ -n "$PHASE" ] || [ -n "$STATE" ]; then
    CONTEXT="Current phase: ${PHASE:-unknown}. Recent commits: ${RECENT_COMMITS}."
    [ -n "$STATE" ] && CONTEXT="$CONTEXT Conductor state: ${STATE}"
    python3 -c "
import json, sys
ctx = sys.argv[1]
print(json.dumps({'additionalContext': ctx}))
" "$CONTEXT"
else
    echo '{}'
fi

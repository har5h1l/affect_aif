#!/usr/bin/env bash
# start_research.sh — bootstrap and launch autonomous research for affect_aif.
#
# usage:
#   ./start_research.sh                  # single conductor session
#   ./start_research.sh --loop 30m       # loop every 30 minutes
#   ./start_research.sh --loop 2h        # loop every 2 hours
#   ./start_research.sh --dry-run        # preview the prompt
#   ./start_research.sh --codex-only     # use codex instead of claude

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=========================================="
echo "  affect_aif — research launcher"
echo "=========================================="
echo ""

# 1. activate venv
if [ -f "$SCRIPT_DIR/.venv/bin/activate" ]; then
    echo "[1/4] Activating .venv..."
    source "$SCRIPT_DIR/.venv/bin/activate"
elif [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
    echo "[1/4] Activating venv..."
    source "$SCRIPT_DIR/venv/bin/activate"
else
    echo "[1/4] No venv found, using system Python."
fi

# 2. run tests (fail fast)
echo "[2/4] Running tests..."
if ! python -m pytest tests/ -v --tb=short -q 2>&1; then
    echo ""
    echo "TESTS FAILED. Fix test failures before starting autonomous research."
    exit 1
fi
echo "  All tests passed."
echo ""

# 3. show current phase
echo "[3/4] Current research state:"
if [ -f "$SCRIPT_DIR/docs/long_term_plan.md" ]; then
    grep -A 2 "Current phase" "$SCRIPT_DIR/docs/long_term_plan.md" 2>/dev/null || \
    grep -i "phase" "$SCRIPT_DIR/docs/long_term_plan.md" | head -3
fi
echo ""

# 4. launch conductor
echo "[4/4] Launching conductor..."
echo "  Steering:  conductor/MISSION.md"
echo "  State:     conductor/STATE.md"
echo "  Logs:      conductor/log/"
echo "  Stop:      Ctrl-C or set Status: PAUSED in MISSION.md"
echo ""

exec "$SCRIPT_DIR/conductor/conductor.sh" "$@"

#!/usr/bin/env bash
# conductor.sh — simple research conductor using Claude + Codex
#
# usage:
#   ./conductor.sh                      # single session
#   ./conductor.sh --loop 2h            # run every 2 hours
#   ./conductor.sh --loop 30m           # run every 30 minutes
#   ./conductor.sh --loop 2h --dry-run  # show prompt without executing
#   ./conductor.sh --codex-only         # use codex for code changes only
#
# steering:
#   edit MISSION.md to change objective
#   set Status: PAUSED in MISSION.md to stop the loop
#   edit STATE.md to inject context or correct findings

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$SCRIPT_DIR/log"
MISSION_FILE="$SCRIPT_DIR/MISSION.md"
STATE_FILE="$SCRIPT_DIR/STATE.md"

# defaults
LOOP_INTERVAL=""
DRY_RUN=false
USE_CODEX=false
CLAUDE_BIN="${CONDUCTOR_CLAUDE_BIN:-claude}"
CODEX_BIN="${CONDUCTOR_CODEX_BIN:-codex}"
CLAUDE_MODEL="${CONDUCTOR_CLAUDE_MODEL:-}"
MAX_TURNS="${CONDUCTOR_MAX_TURNS:-50}"

usage() {
    echo "usage: $0 [--loop INTERVAL] [--dry-run] [--codex-only] [--max-turns N]"
    echo ""
    echo "  --loop INTERVAL   run repeatedly (e.g., 30m, 2h, 1d)"
    echo "  --dry-run         print prompt without executing"
    echo "  --codex-only      use codex instead of claude for execution"
    echo "  --max-turns N     max tool-use turns per session (default: 50)"
    echo ""
    echo "environment:"
    echo "  CONDUCTOR_CLAUDE_BIN    claude binary (default: claude)"
    echo "  CONDUCTOR_CODEX_BIN    codex binary (default: codex)"
    echo "  CONDUCTOR_CLAUDE_MODEL  model override"
    echo "  CONDUCTOR_MAX_TURNS     max turns (default: 50)"
    exit 1
}

# parse args
while [[ $# -gt 0 ]]; do
    case "$1" in
        --loop) LOOP_INTERVAL="$2"; shift 2 ;;
        --dry-run) DRY_RUN=true; shift ;;
        --codex-only) USE_CODEX=true; shift ;;
        --max-turns) MAX_TURNS="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) echo "unknown arg: $1"; usage ;;
    esac
done

# convert interval to seconds
interval_to_seconds() {
    local val="${1%[smhd]}"
    local unit="${1: -1}"
    case "$unit" in
        s) echo "$val" ;;
        m) echo "$((val * 60))" ;;
        h) echo "$((val * 3600))" ;;
        d) echo "$((val * 86400))" ;;
        *) echo "$((val * 60))" ;; # default to minutes
    esac
}

# check if mission says PAUSED
is_paused() {
    grep -qi "^## Status" "$MISSION_FILE" && \
    grep -qi "PAUSED" <(sed -n '/^## Status/,/^##/p' "$MISSION_FILE")
}

# build the prompt for a session
build_prompt() {
    local session_id="$1"
    local timestamp
    timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

    cat << 'PROMPT_HEADER'
You are a research conductor for an active inference affect_aif project.
You have access to all tools in this Claude Code session.

Your job: read the MISSION and STATE below, then execute the mission tasks.
After completing work, update conductor/STATE.md with your findings.

Rules:
- Read MISSION.md and STATE.md first
- Read CLAUDE.md for project conventions and safety invariants
- Execute tasks in order unless blocked
- If a task requires running experiments, use the experiment scripts in scripts/
- If a task requires code/config changes, make them directly
- Write all findings to STATE.md (update Last Updated, Session Count, findings)
- Always run pytest before experiments (safety invariant)
- Small replications first (5 seeds), full runs only after smoke test passes
- If you discover something surprising, document it and stop
- Do NOT modify MISSION.md (that's the user's steering file)
- Keep STATE.md concise — findings, not narration
- Log important decisions to conductor/log/
- Never delete result files (safety invariant)

PROMPT_HEADER

    echo ""
    echo "--- MISSION (from conductor/MISSION.md) ---"
    cat "$MISSION_FILE"
    echo ""
    echo "--- STATE (from conductor/STATE.md) ---"
    cat "$STATE_FILE"
    echo ""
    echo "--- SESSION INFO ---"
    echo "Session ID: $session_id"
    echo "Timestamp: $timestamp"
    echo "Project directory: $PROJECT_DIR"
    echo ""
    echo "Begin executing the mission. Start by reading CLAUDE.md and STATE.md for current context."
}

# run a single session
run_session() {
    local session_id
    session_id="session_$(date +%Y%m%d_%H%M%S)"
    local log_file="$LOG_DIR/${session_id}.log"
    local prompt

    echo "[$session_id] starting session..."

    # check pause
    if is_paused; then
        echo "[$session_id] mission is PAUSED. skipping."
        return 0
    fi

    prompt="$(build_prompt "$session_id")"

    if $DRY_RUN; then
        echo "=== DRY RUN — prompt follows ==="
        echo "$prompt"
        echo "=== END DRY RUN ==="
        return 0
    fi

    # execute via claude or codex
    if $USE_CODEX; then
        echo "[$session_id] launching codex session..."
        echo "$prompt" | "$CODEX_BIN" exec \
            --full-auto \
            2>&1 | tee "$log_file"
    else
        local model_flag=""
        if [[ -n "$CLAUDE_MODEL" ]]; then
            model_flag="--model $CLAUDE_MODEL"
        fi

        echo "[$session_id] launching claude session..."
        "$CLAUDE_BIN" -p "$prompt" \
            --max-turns "$MAX_TURNS" \
            --allowedTools "Read,Write,Edit,Bash,Glob,Grep" \
            $model_flag \
            2>&1 | tee "$log_file"
    fi

    echo "[$session_id] session complete. log: $log_file"
}

# main
mkdir -p "$LOG_DIR"

if [[ -z "$LOOP_INTERVAL" ]]; then
    # single session
    run_session
else
    # loop mode
    interval_sec="$(interval_to_seconds "$LOOP_INTERVAL")"
    echo "conductor: running every ${LOOP_INTERVAL} (${interval_sec}s)"
    echo "conductor: edit $MISSION_FILE to steer, set Status: PAUSED to stop"
    echo ""

    while true; do
        run_session

        if is_paused; then
            echo "conductor: mission PAUSED. waiting for status change..."
            while is_paused; do
                sleep 30
            done
            echo "conductor: mission resumed."
        fi

        echo "conductor: sleeping ${LOOP_INTERVAL}..."
        sleep "$interval_sec"
    done
fi

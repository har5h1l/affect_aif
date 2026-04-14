#!/bin/bash
# Auto-generated: launch conductor session for post-restructure analysis
# Scheduled for 2026-04-15 03:00 PDT
set -e

LOGFILE="$HOME/Desktop/Active Inference/affect_aif/conductor/log/launch_3am_$(date +%Y%m%d_%H%M%S).log"
mkdir -p "$(dirname "$LOGFILE")"

exec >> "$LOGFILE" 2>&1
echo "=== mango launch at $(date) ==="

# Source shell profile for PATH (mango is global)
source "$HOME/.zshrc" 2>/dev/null || source "$HOME/.bash_profile" 2>/dev/null || true

# Push latest code to server (branch already on origin)
echo "--- syncing code to server ---"
mango cloud sync push affect_aif

# Launch conductor session on server, on branch analysis/post-restructure-reframe
echo "--- launching conductor session ---"
mango run affect_aif --cloud

echo "=== launch complete at $(date) ==="

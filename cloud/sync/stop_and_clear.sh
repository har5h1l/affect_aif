#!/usr/bin/env bash
# Stop the default experiment screen session and clear remote results.

set -euo pipefail

CLOUD_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
for ((i = 1; i <= $#; i++)); do
    if [ "${!i}" = "--provider" ] && [ $((i + 1)) -le $# ]; then
        next_index=$((i + 1))
        export CLOUD_PROVIDER_OVERRIDE="${!next_index}"
    fi
    if [ "${!i}" = "--oracle-target" ] && [ $((i + 1)) -le $# ]; then
        next_index=$((i + 1))
        export ORACLE_TARGET_OVERRIDE="${!next_index}"
    fi
done
source "$CLOUD_DIR/_provider.sh"

echo "Stopping screen session 'exp' and clearing results on VM..."
cloud_ssh "screen -S exp -X quit 2>/dev/null || true; rm -rf ${REMOTE_RESULTS}/* 2>/dev/null; echo Done: stopped run and cleared data."

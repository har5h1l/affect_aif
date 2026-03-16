#!/usr/bin/env bash
# Clear one experiment's results on the configured VM.

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

usage() {
    echo "Usage: $0 --experiment NAME"
    echo "  Clears results/NAME on the configured VM."
    exit 1
}

EXPERIMENT=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --experiment) EXPERIMENT="$2"; shift 2 ;;
        --provider) shift 2 ;;
        --oracle-target) shift 2 ;;
        --help|-h) usage ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

if [ -z "$EXPERIMENT" ]; then
    echo "Error: --experiment is required."
    usage
fi

VM_PATH="${REMOTE_RESULTS}/${EXPERIMENT}"
echo "Clearing on VM: $VM_PATH"
cloud_ssh "rm -rf ${VM_PATH} && echo Done. Removed ${VM_PATH}"

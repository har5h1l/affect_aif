#!/usr/bin/env bash
# Push local results to the configured cloud VM.

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

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

VM_RESULTS_BASE="${REMOTE_RESULTS}"
LOCAL_RESULTS_BASE="${PROJECT_ROOT}/results"
EXPERIMENT=""

usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Push local results to the configured VM.

OPTIONS:
    --vm-path PATH          Path to results on VM (default: ${REMOTE_RESULTS})
    --local-path PATH       Local path to push (default: ./results)
    --experiment NAME       Only push this experiment
    --provider NAME         Override provider for this run
    --oracle-target NAME    Override Oracle target for this run
    --help                  Show this help message

Provider comes from CLOUD_PROVIDER in .env (current: ${CLOUD_PROVIDER_LABEL}).
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --vm-path) VM_RESULTS_BASE="$2"; shift 2 ;;
        --local-path) LOCAL_RESULTS_BASE="$2"; shift 2 ;;
        --experiment) EXPERIMENT="$2"; shift 2 ;;
        --provider) shift 2 ;;
        --oracle-target) shift 2 ;;
        --help|-h) usage; exit 0 ;;
        *)
            echo -e "${RED}Error: Unknown option $1${NC}"
            usage
            exit 1
            ;;
    esac
done

if [ -n "$EXPERIMENT" ]; then
    VM_RESULTS_PATH="${VM_RESULTS_BASE}/${EXPERIMENT}"
    LOCAL_SOURCE="${LOCAL_RESULTS_BASE}/${EXPERIMENT}"
else
    VM_RESULTS_PATH="${VM_RESULTS_BASE}"
    LOCAL_SOURCE="${LOCAL_RESULTS_BASE}"
fi

if [ ! -d "$LOCAL_SOURCE" ]; then
    echo -e "${RED}Error: Local path does not exist: $LOCAL_SOURCE${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Pushing results via provider '${CLOUD_PROVIDER_LABEL}'...${NC}"
echo "  From: $LOCAL_SOURCE"
echo "  To:   $VM_RESULTS_PATH"
echo ""

cloud_ssh "mkdir -p ${VM_RESULTS_PATH%/*}"

if command -v rsync >/dev/null 2>&1; then
    echo -e "${YELLOW}Syncing with rsync...${NC}"
    cloud_rsync_to_vm "$LOCAL_SOURCE" "$VM_RESULTS_PATH"
else
    echo -e "${YELLOW}Transferring with SCP...${NC}"
    cloud_scp_to_vm "$LOCAL_SOURCE" "${VM_RESULTS_PATH%/*}/"
fi

echo ""
echo -e "${GREEN}VM now has results at: ${VM_RESULTS_PATH}${NC}"

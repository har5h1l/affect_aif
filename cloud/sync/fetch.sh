#!/usr/bin/env bash
# Fetch results from the configured cloud VM to the local machine.

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
INCREMENTAL=false
EXPERIMENT=""
ENSURE_MAIN=false
YES=false

usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Fetch experiment results from the configured VM into ./results by default.

OPTIONS:
    --vm-path PATH          Path to results on VM (default: ${REMOTE_RESULTS})
    --local-path PATH       Local path to save results (default: ./results)
    --incremental           Use rsync so only new/changed files transfer
    --experiment NAME       Only fetch this experiment (e.g. phase2_pilot)
    --ensure-main           On VM: git checkout main && git pull before fetching
    --yes                   Skip branch prompt
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
        --incremental) INCREMENTAL=true; shift ;;
        --experiment) EXPERIMENT="$2"; shift 2 ;;
        --ensure-main) ENSURE_MAIN=true; shift ;;
        --yes) YES=true; shift ;;
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
    LOCAL_RESULTS_PATH="${LOCAL_RESULTS_BASE}/${EXPERIMENT}"
else
    VM_RESULTS_PATH="${VM_RESULTS_BASE}"
    LOCAL_RESULTS_PATH="${LOCAL_RESULTS_BASE}"
fi

if [ "$ENSURE_MAIN" = true ]; then
    echo -e "${YELLOW}Ensuring VM repo is on main...${NC}"
    if ! cloud_ssh "bash -l -c 'cd ${REMOTE_REPO} && git fetch origin && git checkout main && git pull'"; then
        echo -e "${RED}✗ Failed to update VM to main.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ VM is on main${NC}"
    echo ""
fi

if [ "$YES" = false ]; then
    VM_BRANCH="$(cloud_ssh "bash -l -c 'cd ${REMOTE_REPO} && git rev-parse --abbrev-ref HEAD 2>/dev/null'" 2>/dev/null || true)"
    LOCAL_BRANCH="$(git -C "$PROJECT_ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
    if [ -z "$VM_BRANCH" ]; then
        if [ -t 0 ]; then
            echo -e "${YELLOW}Could not detect VM branch.${NC}"
            echo -n "Continue fetch into ${LOCAL_RESULTS_PATH}? [y/N] "
            read -r reply
            if [ "$reply" != "y" ] && [ "$reply" != "Y" ]; then
                echo "Aborted. Fix VM access or run with --yes to skip this prompt."
                exit 1
            fi
        else
            echo -e "${YELLOW}Could not detect VM branch. Run with --yes to fetch anyway.${NC}"
            exit 1
        fi
    elif [ -n "$LOCAL_BRANCH" ] && [ "$VM_BRANCH" != "$LOCAL_BRANCH" ]; then
        if [ -t 0 ]; then
            echo -e "${YELLOW}VM is on branch '${VM_BRANCH}', local is '${LOCAL_BRANCH}'.${NC}"
            echo -n "Continue? [y/N] "
            read -r reply
            if [ "$reply" != "y" ] && [ "$reply" != "Y" ]; then
                echo "Aborted. Run with --ensure-main or --yes."
                exit 1
            fi
        else
            echo -e "${RED}VM branch '${VM_BRANCH}' differs from local '${LOCAL_BRANCH}'.${NC}"
            echo "Run with --yes to fetch anyway, or --ensure-main to update VM to main first."
            exit 1
        fi
    else
        echo -e "${GREEN}VM branch: ${VM_BRANCH}${NC}"
    fi
    echo ""
fi

mkdir -p "$LOCAL_RESULTS_PATH"

echo ""
echo -e "${GREEN}Fetching results via provider '${CLOUD_PROVIDER_LABEL}'...${NC}"
echo "  From: $VM_RESULTS_PATH"
echo "  To:   $LOCAL_RESULTS_PATH"
echo ""

if [ "$INCREMENTAL" = true ] && command -v rsync >/dev/null 2>&1; then
    echo -e "${YELLOW}Syncing with rsync...${NC}"
    cloud_rsync_from_vm "$VM_RESULTS_PATH" "$LOCAL_RESULTS_PATH"
else
    echo -e "${YELLOW}Transferring with SCP...${NC}"
    cloud_scp_from_vm "${VM_RESULTS_PATH}/" "${LOCAL_RESULTS_PATH}/"
    NESTED="${LOCAL_RESULTS_PATH}/results"
    if [ -d "$NESTED" ]; then
        echo -e "${YELLOW}Merging ${NESTED} into ${LOCAL_RESULTS_PATH}...${NC}"
        for item in "${NESTED}"/*; do
            [ -e "$item" ] && cp -R "$item" "${LOCAL_RESULTS_PATH}/" 2>/dev/null || true
        done
        rm -rf "$NESTED"
    fi
fi

echo ""
echo -e "${GREEN}Results available at: ${LOCAL_RESULTS_PATH}${NC}"
echo "Summary:"
du -sh "${LOCAL_RESULTS_PATH}" 2>/dev/null || echo "  (check directory size manually)"
find "${LOCAL_RESULTS_PATH}" -type f 2>/dev/null | wc -l | xargs echo "  Total files:"

#!/usr/bin/env bash
# Shared env loader for cloud scripts.

CLOUD_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$CLOUD_DIR/.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env"
ENV_EXAMPLE="$PROJECT_ROOT/.env.example"

if [ ! -f "$ENV_FILE" ]; then
    if [ -f "$ENV_EXAMPLE" ]; then
        cp "$ENV_EXAMPLE" "$ENV_FILE"
        echo "Created .env from .env.example at: $ENV_FILE"
        echo "Please add your cloud credentials there and run again."
    else
        echo "Error: .env not found and .env.example not found at $ENV_EXAMPLE"
        exit 1
    fi
    exit 0
fi

set -a
source "$ENV_FILE"
set +a

export PROJECT_ROOT
export CLOUD_DIR
export CLOUD_PROVIDER_DEFAULT="${CLOUD_PROVIDER:-gcp}"
export CLOUD_AVAILABLE_PROVIDERS="${CLOUD_AVAILABLE_PROVIDERS:-gcp oracle}"
export CLOUD_PROVIDER="${CLOUD_PROVIDER_OVERRIDE:-$CLOUD_PROVIDER_DEFAULT}"
export ORACLE_TARGET_DEFAULT="${ORACLE_TARGET:-paid}"
export ORACLE_AVAILABLE_TARGETS="${ORACLE_AVAILABLE_TARGETS:-paid free}"
export ORACLE_TARGET="${ORACLE_TARGET_OVERRIDE:-$ORACLE_TARGET_DEFAULT}"

COMMON_VM_REPO_PATH="${VM_REPO_PATH:-${GCP_VM_REPO_PATH:-~/affect_aif}}"

export GCP_PROJECT_ID="${GCP_PROJECT_ID:-}"
export GCP_ZONE="${GCP_ZONE:-us-west1-a}"
export GCP_VM_NAME="${GCP_VM_NAME:-affect-aif-vm}"
export GCP_MACHINE_TYPE="${GCP_MACHINE_TYPE:-c3-standard-16}"
export GCP_DISK_SIZE="${GCP_DISK_SIZE:-50}"
export GCP_IMAGE_FAMILY="${GCP_IMAGE_FAMILY:-ubuntu-2404-lts-amd64}"
export GCP_IMAGE_PROJECT="${GCP_IMAGE_PROJECT:-ubuntu-os-cloud}"
export GCP_CONDA_ENV="${GCP_CONDA_ENV:-affect_aif}"

if [ "$CLOUD_PROVIDER" = "oracle" ]; then
    ORACLE_TARGET_KEY="$(printf "%s" "$ORACLE_TARGET" | tr '[:lower:]-' '[:upper:]_')"
    ORACLE_HOST_VAR="ORACLE_${ORACLE_TARGET_KEY}_HOST"
    ORACLE_USER_VAR="ORACLE_${ORACLE_TARGET_KEY}_USER"
    ORACLE_SSH_KEY_VAR="ORACLE_${ORACLE_TARGET_KEY}_SSH_KEY"
    ORACLE_REPO_VAR="ORACLE_${ORACLE_TARGET_KEY}_REPO_PATH"
    ORACLE_CONDA_ENV_VAR="ORACLE_${ORACLE_TARGET_KEY}_CONDA_ENV"

    export VM_HOST="${!ORACLE_HOST_VAR:-${VM_HOST:-}}"
    export VM_USER="${!ORACLE_USER_VAR:-${VM_USER:-ubuntu}}"
    export VM_SSH_KEY="${!ORACLE_SSH_KEY_VAR:-${VM_SSH_KEY:-$HOME/.ssh/oracle_key}}"
    export VM_REPO_PATH="${!ORACLE_REPO_VAR:-$COMMON_VM_REPO_PATH}"
    export REMOTE_CONDA_ENV="${!ORACLE_CONDA_ENV_VAR:-${REMOTE_CONDA_ENV:-affect_aif}}"
    export CLOUD_PROVIDER_LABEL="${CLOUD_PROVIDER}/${ORACLE_TARGET}"
else
    export VM_HOST="${VM_HOST:-}"
    export VM_USER="${VM_USER:-ubuntu}"
    export VM_SSH_KEY="${VM_SSH_KEY:-$HOME/.ssh/oracle_key}"
    export VM_REPO_PATH="$COMMON_VM_REPO_PATH"
    export REMOTE_CONDA_ENV="${REMOTE_CONDA_ENV:-$GCP_CONDA_ENV}"
    export CLOUD_PROVIDER_LABEL="$CLOUD_PROVIDER"
fi

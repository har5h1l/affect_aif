#!/usr/bin/env bash
# Provider dispatcher for cloud transport operations.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_env.sh"

case " ${CLOUD_AVAILABLE_PROVIDERS} " in
    *" ${CLOUD_PROVIDER} "*) ;;
    *)
        echo "Error: CLOUD_PROVIDER '${CLOUD_PROVIDER}' is not listed in CLOUD_AVAILABLE_PROVIDERS='${CLOUD_AVAILABLE_PROVIDERS}'."
        exit 1
        ;;
esac

if [ "$CLOUD_PROVIDER" = "oracle" ]; then
    case " ${ORACLE_AVAILABLE_TARGETS} " in
        *" ${ORACLE_TARGET} "*) ;;
        *)
            echo "Error: ORACLE_TARGET '${ORACLE_TARGET}' is not listed in ORACLE_AVAILABLE_TARGETS='${ORACLE_AVAILABLE_TARGETS}'."
            exit 1
            ;;
    esac
fi

PROVIDER_SCRIPT="$SCRIPT_DIR/providers/${CLOUD_PROVIDER}.sh"
if [ ! -f "$PROVIDER_SCRIPT" ]; then
    echo "Error: unsupported CLOUD_PROVIDER '$CLOUD_PROVIDER'"
    echo "Expected one of the provider scripts under $SCRIPT_DIR/providers/"
    exit 1
fi

export REMOTE_REPO="$VM_REPO_PATH"
export REMOTE_RESULTS="${REMOTE_REPO}/results"

source "$PROVIDER_SCRIPT"

for fn in cloud_ssh cloud_ssh_interactive cloud_scp_to_vm cloud_scp_from_vm \
    cloud_rsync_to_vm cloud_rsync_from_vm; do
    if ! command -v "$fn" >/dev/null 2>&1; then
        echo "Error: provider '$CLOUD_PROVIDER' does not define $fn"
        exit 1
    fi
done

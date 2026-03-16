#!/usr/bin/env bash
# GCP transport implementation.

cloud_gcp_require() {
    if ! command -v gcloud >/dev/null 2>&1; then
        echo "Error: gcloud command not found."
        exit 1
    fi
    if [ -z "$GCP_PROJECT_ID" ]; then
        echo "Error: GCP_PROJECT_ID is not set in .env."
        exit 1
    fi
}

cloud_gcp_ssh_host() {
    cloud_gcp_require
    gcloud compute config-ssh --project="$GCP_PROJECT_ID" >/dev/null 2>&1 || true
    printf "%s.%s.%s" "$GCP_VM_NAME" "$GCP_ZONE" "$GCP_PROJECT_ID"
}

cloud_ssh() {
    cloud_gcp_require
    if [ "$#" -eq 0 ]; then
        gcloud compute ssh "$GCP_VM_NAME" \
            --zone="$GCP_ZONE" \
            --project="$GCP_PROJECT_ID" \
            --tunnel-through-iap \
            -- bash -l -s
        return
    fi

    gcloud compute ssh "$GCP_VM_NAME" \
        --zone="$GCP_ZONE" \
        --project="$GCP_PROJECT_ID" \
        --tunnel-through-iap \
        --command="$1"
}

cloud_ssh_interactive() {
    cloud_gcp_require
    if [ "$#" -eq 0 ]; then
        gcloud compute ssh "$GCP_VM_NAME" \
            --zone="$GCP_ZONE" \
            --project="$GCP_PROJECT_ID" \
            --tunnel-through-iap
        return
    fi

    local quoted_command
    quoted_command=$(printf "%q" "$1")
    gcloud compute ssh "$GCP_VM_NAME" \
        --zone="$GCP_ZONE" \
        --project="$GCP_PROJECT_ID" \
        --tunnel-through-iap \
        -- "bash -l -c $quoted_command"
}

cloud_scp_to_vm() {
    cloud_gcp_require
    local local_path="$1"
    local remote_path="$2"
    gcloud compute scp --recurse \
        --zone="$GCP_ZONE" \
        --project="$GCP_PROJECT_ID" \
        --tunnel-through-iap \
        "$local_path" \
        "${GCP_VM_NAME}:${remote_path}"
}

cloud_scp_from_vm() {
    cloud_gcp_require
    local remote_path="$1"
    local local_path="$2"
    gcloud compute scp --recurse \
        --zone="$GCP_ZONE" \
        --project="$GCP_PROJECT_ID" \
        --tunnel-through-iap \
        "${GCP_VM_NAME}:${remote_path}" \
        "$local_path"
}

cloud_rsync_to_vm() {
    cloud_gcp_require
    if ! command -v rsync >/dev/null 2>&1; then
        echo "Error: rsync command not found."
        exit 1
    fi

    local local_path="$1"
    local remote_path="$2"
    local ssh_host
    ssh_host="$(cloud_gcp_ssh_host)"

    rsync -avz --progress "${local_path}/" "${ssh_host}:${remote_path}/"
}

cloud_rsync_from_vm() {
    cloud_gcp_require
    if ! command -v rsync >/dev/null 2>&1; then
        echo "Error: rsync command not found."
        exit 1
    fi

    local remote_path="$1"
    local local_path="$2"
    local ssh_host
    ssh_host="$(cloud_gcp_ssh_host)"

    rsync -avz --progress "${ssh_host}:${remote_path}/" "${local_path}/"
}

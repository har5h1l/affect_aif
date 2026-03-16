#!/usr/bin/env bash
# Oracle SSH transport implementation.

cloud_oracle_require() {
    if [ -z "$VM_HOST" ]; then
        echo "Error: VM_HOST is not set in .env."
        exit 1
    fi
    if ! command -v ssh >/dev/null 2>&1; then
        echo "Error: ssh command not found."
        exit 1
    fi
}

cloud_oracle_ssh_base() {
    cloud_oracle_require
    local opts=(
        -o StrictHostKeyChecking=accept-new
        -o ServerAliveInterval=30
    )
    if [ -n "$VM_SSH_KEY" ]; then
        opts+=(-i "$VM_SSH_KEY")
    fi
    printf "%s\n" "${opts[@]}"
}

cloud_ssh() {
    cloud_oracle_require
    local ssh_opts=()
    while IFS= read -r line; do
        ssh_opts+=("$line")
    done < <(cloud_oracle_ssh_base)

    if [ "$#" -eq 0 ]; then
        ssh "${ssh_opts[@]}" "${VM_USER}@${VM_HOST}" bash -l -s
        return
    fi

    ssh "${ssh_opts[@]}" "${VM_USER}@${VM_HOST}" "$1"
}

cloud_ssh_interactive() {
    cloud_oracle_require
    local ssh_opts=(-t)
    while IFS= read -r line; do
        ssh_opts+=("$line")
    done < <(cloud_oracle_ssh_base)

    if [ "$#" -eq 0 ]; then
        ssh "${ssh_opts[@]}" "${VM_USER}@${VM_HOST}"
        return
    fi

    local quoted_command
    quoted_command=$(printf "%q" "$1")
    ssh "${ssh_opts[@]}" "${VM_USER}@${VM_HOST}" "bash -l -c $quoted_command"
}

cloud_scp_to_vm() {
    cloud_oracle_require
    local local_path="$1"
    local remote_path="$2"
    local scp_opts=(-r -o StrictHostKeyChecking=accept-new)
    if [ -n "$VM_SSH_KEY" ]; then
        scp_opts+=(-i "$VM_SSH_KEY")
    fi
    scp "${scp_opts[@]}" "$local_path" "${VM_USER}@${VM_HOST}:${remote_path}"
}

cloud_scp_from_vm() {
    cloud_oracle_require
    local remote_path="$1"
    local local_path="$2"
    local scp_opts=(-r -o StrictHostKeyChecking=accept-new)
    if [ -n "$VM_SSH_KEY" ]; then
        scp_opts+=(-i "$VM_SSH_KEY")
    fi
    scp "${scp_opts[@]}" "${VM_USER}@${VM_HOST}:${remote_path}" "$local_path"
}

cloud_rsync_to_vm() {
    cloud_oracle_require
    if ! command -v rsync >/dev/null 2>&1; then
        echo "Error: rsync command not found."
        exit 1
    fi

    local local_path="$1"
    local remote_path="$2"
    local ssh_cmd="ssh -o StrictHostKeyChecking=accept-new"
    if [ -n "$VM_SSH_KEY" ]; then
        ssh_cmd="${ssh_cmd} -i ${VM_SSH_KEY}"
    fi
    rsync -avz --progress -e "$ssh_cmd" "${local_path}/" "${VM_USER}@${VM_HOST}:${remote_path}/"
}

cloud_rsync_from_vm() {
    cloud_oracle_require
    if ! command -v rsync >/dev/null 2>&1; then
        echo "Error: rsync command not found."
        exit 1
    fi

    local remote_path="$1"
    local local_path="$2"
    local ssh_cmd="ssh -o StrictHostKeyChecking=accept-new"
    if [ -n "$VM_SSH_KEY" ]; then
        ssh_cmd="${ssh_cmd} -i ${VM_SSH_KEY}"
    fi
    rsync -avz --progress -e "$ssh_cmd" "${VM_USER}@${VM_HOST}:${remote_path}/" "${local_path}/"
}

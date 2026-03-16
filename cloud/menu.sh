#!/usr/bin/env bash
# Master menu for provider-aware cloud VM workflows.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

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

reload_provider() {
    # shellcheck disable=SC1091
    source "$SCRIPT_DIR/_provider.sh"
}

reload_provider

build_remote_repo_script() {
    local command="$1"
    cat <<EOF
if [ -f "\$HOME/miniforge3/etc/profile.d/conda.sh" ]; then
    source "\$HOME/miniforge3/etc/profile.d/conda.sh"
elif [ -f "\$HOME/miniconda/etc/profile.d/conda.sh" ]; then
    source "\$HOME/miniconda/etc/profile.d/conda.sh"
fi
cd ${REMOTE_REPO} && conda activate ${REMOTE_CONDA_ENV} 2>/dev/null || true
cd ${REMOTE_REPO} && ${command}
EOF
}

build_cloud_cmd() {
    local path="$1"
    shift
    local cmd=(bash "$SCRIPT_DIR/$path" --provider "$CLOUD_PROVIDER")
    if [ "$CLOUD_PROVIDER" = "oracle" ]; then
        cmd+=(--oracle-target "$ORACLE_TARGET")
    fi
    cmd+=("$@")
    printf '%s\0' "${cmd[@]}"
}

run_cloud_cmd() {
    local path="$1"
    shift
    local cmd=()
    while IFS= read -r -d '' entry; do
        cmd+=("$entry")
    done < <(build_cloud_cmd "$path" "$@")
    "${cmd[@]}"
}

exec_cloud_cmd() {
    local path="$1"
    shift
    local cmd=()
    while IFS= read -r -d '' entry; do
        cmd+=("$entry")
    done < <(build_cloud_cmd "$path" "$@")
    exec "${cmd[@]}"
}

run_remote_repo_command() {
    local command="$1"
    build_remote_repo_script "$command" | cloud_ssh
}

sync_repo_snapshot_to_vm() {
    local archive_path
    local remote_archive="/tmp/affect-aif-bootstrap.tar.gz"
    archive_path="$(mktemp "/tmp/affect-aif-bootstrap.XXXXXX.tar.gz")"

    tar -C "$PROJECT_ROOT" \
        --exclude=".git" \
        --exclude=".env" \
        --exclude=".pytest_cache" \
        --exclude=".venv" \
        --exclude="results" \
        --exclude="conductor/log" \
        --exclude="__pycache__" \
        -czf "$archive_path" .

    cloud_scp_to_vm "$archive_path" "$remote_archive"
    cloud_ssh "mkdir -p $REMOTE_REPO && tar -xzf $remote_archive -C $REMOTE_REPO && rm -f $remote_archive"
    rm -f "$archive_path"
}

bootstrap_repo_on_vm() {
    local repo_url="$1"
    local token_prefix=""
    if [ -n "${GITHUB_TOKEN:-}" ]; then
        token_prefix=$(printf 'GITHUB_TOKEN=%q\n' "$GITHUB_TOKEN")
    fi

    cat <<EOF | cloud_ssh
set -euo pipefail
${token_prefix}
repo_url=$(printf "%q" "$repo_url")
remote_repo=$(printf "%q" "$REMOTE_REPO")

git_auth_pull() {
    if [ -n "\${GITHUB_TOKEN:-}" ] && [[ "\$repo_url" == https://github.com/* ]]; then
        auth_header=\$(printf 'x-access-token:%s' "\$GITHUB_TOKEN" | base64 | tr -d '\n')
        git -c http.extraHeader="Authorization: Basic \$auth_header" pull
    else
        git pull
    fi
}

git_auth_clone() {
    if [ -n "\${GITHUB_TOKEN:-}" ] && [[ "\$repo_url" == https://github.com/* ]]; then
        auth_header=\$(printf 'x-access-token:%s' "\$GITHUB_TOKEN" | base64 | tr -d '\n')
        git -c http.extraHeader="Authorization: Basic \$auth_header" clone "\$repo_url" "\$remote_repo"
    else
        git clone "\$repo_url" "\$remote_repo"
    fi
}

if [ -d "\$remote_repo/.git" ]; then
    cd "\$remote_repo"
    git_auth_pull
else
    git_auth_clone
fi
EOF
}

setup_on_vm() {
    local setup_script="cloud/vm/setup_${CLOUD_PROVIDER}.sh"
    local repo_url
    if [ ! -f "$SCRIPT_DIR/vm/setup_${CLOUD_PROVIDER}.sh" ]; then
        echo "Error: setup script not found for provider '${CLOUD_PROVIDER}'."
        exit 1
    fi
    repo_url="$(git -C "$PROJECT_ROOT" remote get-url origin 2>/dev/null || true)"
    if [ -z "$repo_url" ]; then
        echo "Error: could not determine git remote URL for automatic VM setup."
        exit 1
    fi
    if ! bootstrap_repo_on_vm "$repo_url"; then
        echo "Remote git bootstrap failed. Uploading local repo snapshot instead..."
        sync_repo_snapshot_to_vm
    fi
    cloud_ssh "cd $REMOTE_REPO && bash $setup_script"
}

gcp_only_required() {
    if [ "$CLOUD_PROVIDER" != "gcp" ]; then
        echo "Error: this operation is only available for CLOUD_PROVIDER=gcp."
        exit 1
    fi
}

if [ -n "${1:-}" ]; then
    while [ -n "${1:-}" ]; do
        case "$1" in
            --provider|--oracle-target)
                shift 2
                ;;
            *)
                break
                ;;
        esac
    done
fi

if [ -n "${1:-}" ]; then
    case "$1" in
        fetch)
            shift
            exec_cloud_cmd "sync/fetch.sh" "$@"
            ;;
        push)
            shift
            exec_cloud_cmd "sync/push.sh" "$@"
            ;;
        clear)
            shift
            exec_cloud_cmd "sync/clear.sh" "$@"
            ;;
        setup-on-vm)
            setup_on_vm
            exit 0
            ;;
        ssh)
            shift
            if [ "$#" -gt 0 ]; then
                cloud_ssh_interactive "$*"
            else
                cloud_ssh_interactive
            fi
            exit 0
            ;;
        run)
            shift
            if [ -z "${1:-}" ]; then
                echo "Usage: $0 run \"COMMAND\""
                exit 1
            fi
            run_remote_repo_command "$1"
            exit 0
            ;;
        create)
            shift
            gcp_only_required
            exec_cloud_cmd "vm/create.sh" "$@"
            ;;
        start)
            gcp_only_required
            gcloud compute instances start "$GCP_VM_NAME" --zone="$GCP_ZONE" --project="$GCP_PROJECT_ID"
            exit 0
            ;;
        stop)
            gcp_only_required
            gcloud compute instances stop "$GCP_VM_NAME" --zone="$GCP_ZONE" --project="$GCP_PROJECT_ID"
            exit 0
            ;;
        *)
            echo "Unknown subcommand: $1"
            echo "Usage: $0 [--provider NAME] [--oracle-target NAME] [fetch|push|clear|run|ssh|setup-on-vm|create|start|stop]"
            exit 1
            ;;
    esac
fi

select_provider() {
    echo ""
    echo "Available providers: ${CLOUD_AVAILABLE_PROVIDERS}"
    echo -n "Provider [${CLOUD_PROVIDER}]: "
    read -r new_provider
    if [ -z "$new_provider" ]; then
        return
    fi
    export CLOUD_PROVIDER_OVERRIDE="$new_provider"
    reload_provider
}

select_oracle_target() {
    if [ "$CLOUD_PROVIDER" != "oracle" ]; then
        echo "Oracle target selection is only available for CLOUD_PROVIDER=oracle."
        return
    fi
    echo ""
    echo "Available Oracle targets: ${ORACLE_AVAILABLE_TARGETS}"
    echo -n "Oracle target [${ORACLE_TARGET}]: "
    read -r new_target
    if [ -z "$new_target" ]; then
        return
    fi
    export ORACLE_TARGET_OVERRIDE="$new_target"
    reload_provider
}

show_menu() {
    local menu_label="$CLOUD_PROVIDER_LABEL"
    echo ""
    echo "=============================================="
    echo "  Cloud VM - affect_aif (${menu_label})"
    echo "=============================================="
    echo "  [p] Provider       Switch provider for this session"
    if [ "$CLOUD_PROVIDER" = "oracle" ]; then
        echo "  [t] Oracle target  Switch Oracle host target for this session"
    fi
    if [ "$CLOUD_PROVIDER" = "gcp" ]; then
        echo "  [1] Create VM      Create the GCP instance"
        echo "  [4] Start VM       Start the GCP instance"
        echo "  [6] Stop VM        Stop the GCP instance"
    fi
    echo "  [2] Fetch results  Pull results from VM -> local"
    echo "  [3] Push results   Push local results -> VM"
    echo "  [5] SSH to VM      Open provider SSH session"
    echo "  [7] Workflow       Show cloud README"
    echo "  [8] Setup on VM    Run provider setup script on VM"
    echo "  [9] Clear results  Delete one experiment's results on VM"
    echo "  [0] Exit"
    echo "=============================================="
    echo -n "Choice: "
}

fetch_submenu() {
    echo ""
    echo "  Fetch options:"
    echo "  [1] Full pull"
    echo "  [2] Incremental"
    echo "  [3] One experiment"
    echo "  [b] Back"
    echo -n "Choice: "
    read -r sub
    case "$sub" in
        1) run_cloud_cmd "sync/fetch.sh" ;;
        2) run_cloud_cmd "sync/fetch.sh" --incremental ;;
        3)
            echo -n "Experiment name: "
            read -r exp
            if [ -n "$exp" ]; then
                run_cloud_cmd "sync/fetch.sh" --experiment "$exp"
            fi
            ;;
        b) ;;
        *) echo "Invalid option." ;;
    esac
}

while true; do
    show_menu
    read -r choice
    case "$choice" in
        1)
            gcp_only_required
            run_cloud_cmd "vm/create.sh"
            ;;
        2)
            fetch_submenu
            ;;
        3)
            echo -n "Push all results, or one experiment? [a]ll or experiment name: "
            read -r push_opt
            if [ -z "$push_opt" ] || [ "$push_opt" = "a" ]; then
                run_cloud_cmd "sync/push.sh"
            else
                run_cloud_cmd "sync/push.sh" --experiment "$push_opt"
            fi
            ;;
        4)
            gcp_only_required
            gcloud compute instances start "$GCP_VM_NAME" --zone="$GCP_ZONE" --project="$GCP_PROJECT_ID"
            ;;
        5)
            echo ""
            echo "  [1] Open SSH session"
            echo "  [2] Open repo shell with env activation"
            echo -n "Choice [1]: "
            read -r ssh_opt
            if [ "$ssh_opt" = "2" ]; then
                cloud_ssh_interactive "$(build_remote_repo_script 'exec bash')"
            else
                cloud_ssh_interactive
            fi
            ;;
        6)
            gcp_only_required
            gcloud compute instances stop "$GCP_VM_NAME" --zone="$GCP_ZONE" --project="$GCP_PROJECT_ID"
            ;;
        7)
            if [ -f "$SCRIPT_DIR/README.md" ]; then
                less "$SCRIPT_DIR/README.md" || cat "$SCRIPT_DIR/README.md"
            else
                echo "README.md not found."
            fi
            ;;
        8)
            setup_on_vm
            ;;
        9)
            echo -n "Experiment to clear on VM: "
            read -r exp
            if [ -n "$exp" ]; then
                run_cloud_cmd "sync/clear.sh" --experiment "$exp"
            else
                echo "No experiment name given."
            fi
            ;;
        p|P)
            select_provider
            ;;
        t|T)
            select_oracle_target
            ;;
        0)
            echo "Bye."
            exit 0
            ;;
        *)
            echo "Invalid option."
            ;;
    esac
    echo ""
    echo -n "Press Enter to continue..."
    read -r
done

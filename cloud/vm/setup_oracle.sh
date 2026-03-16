#!/usr/bin/env bash
# VM setup script for Oracle Ubuntu images used by affect_aif research.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/../../setup.py" ]; then
    PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
else
    PROJECT_ROOT="${PROJECT_ROOT:-$HOME/affect_aif}"
fi
CONDA_ROOT="${CONDA_ROOT:-$HOME/miniforge3}"
ENV_NAME="${ENV_NAME:-affect_aif}"
NPM_PREFIX="${NPM_PREFIX:-$HOME/.local}"
NODE_MAJOR="${NODE_MAJOR:-20}"

append_if_missing() {
    local file_path="$1"
    local line="$2"
    touch "$file_path"
    if ! grep -Fqx "$line" "$file_path"; then
        printf '%s\n' "$line" >>"$file_path"
    fi
}

detect_miniforge_arch() {
    case "$(uname -m)" in
        x86_64) printf "x86_64" ;;
        aarch64|arm64) printf "aarch64" ;;
        *)
            echo "Unsupported architecture: $(uname -m)" >&2
            exit 1
            ;;
    esac
}

ensure_nodejs() {
    local node_major="0"
    if command -v node >/dev/null 2>&1; then
        node_major="$(node -p 'process.versions.node.split(".")[0]')"
    fi

    if [ "$node_major" -ge "$NODE_MAJOR" ]; then
        return
    fi

    curl -fsSL "https://deb.nodesource.com/setup_${NODE_MAJOR}.x" | sudo -E bash -
    sudo apt-get install -y nodejs
}

ensure_user_shell_path() {
    mkdir -p "$NPM_PREFIX/bin"
    export PATH="$NPM_PREFIX/bin:$PATH"
    append_if_missing "$HOME/.profile" 'export PATH="$HOME/.local/bin:$PATH"'
    append_if_missing "$HOME/.bashrc" 'export PATH="$HOME/.local/bin:$PATH"'
}

sudo apt-get update
sudo apt-get install -y \
    git \
    tmux \
    htop \
    curl \
    build-essential \
    libopenblas-dev

ensure_nodejs
ensure_user_shell_path

if [ ! -d "$CONDA_ROOT" ]; then
    MINIFORGE_ARCH="$(detect_miniforge_arch)"
    INSTALLER="Miniforge3-Linux-${MINIFORGE_ARCH}.sh"
    curl -L -o "/tmp/${INSTALLER}" \
        "https://github.com/conda-forge/miniforge/releases/latest/download/${INSTALLER}"
    bash "/tmp/${INSTALLER}" -b -p "$CONDA_ROOT"
    rm -f "/tmp/${INSTALLER}"
fi

source "$CONDA_ROOT/etc/profile.d/conda.sh"
conda config --set always_yes yes --set changeps1 no >/dev/null

if conda env list | awk '{print $1}' | grep -qx "$ENV_NAME"; then
    conda activate "$ENV_NAME"
else
    conda create -n "$ENV_NAME" python=3.11 >/dev/null
    conda activate "$ENV_NAME"
fi

python -m pip install --upgrade pip
python -m pip install -e "$PROJECT_ROOT"

# JAX CPU-only (no GPU needed for trust game sims)
python -m pip install jax jaxlib

mkdir -p "$PROJECT_ROOT/.cache/jax"

if ! command -v codex >/dev/null 2>&1; then
    npm install --global --prefix "$NPM_PREFIX" @openai/codex
fi

if ! command -v claude >/dev/null 2>&1; then
    npm install --global --prefix "$NPM_PREFIX" @anthropic-ai/claude-code
fi

# conductor systemd service
sudo tee /etc/systemd/system/conductor-affect-aif.service >/dev/null <<SERVICE
[Unit]
Description=Research Conductor - affect_aif
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$PROJECT_ROOT
ExecStart=$PROJECT_ROOT/conductor/conductor.sh --loop 30m --max-turns 50
Restart=on-failure
RestartSec=120
Environment="PATH=$NPM_PREFIX/bin:$CONDA_ROOT/envs/$ENV_NAME/bin:/usr/local/bin:/usr/bin:/bin"
Environment="HOME=$HOME"
Environment="CONDUCTOR_MAX_TURNS=50"

[Install]
WantedBy=multi-user.target
SERVICE

sudo systemctl daemon-reload
echo ""
echo "Oracle setup complete for affect_aif."
echo "  Conda env: $ENV_NAME"
echo "  Project:   $PROJECT_ROOT"
echo ""
echo "Enable conductor with: sudo systemctl enable --now conductor-affect-aif.service"
echo "Or run manually:       ./conductor/conductor.sh --loop 30m"

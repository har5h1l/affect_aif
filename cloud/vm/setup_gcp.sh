#!/usr/bin/env bash
# VM setup script for GCP Ubuntu images used by affect_aif research.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/../../setup.py" ]; then
    PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
else
    PROJECT_ROOT="${PROJECT_ROOT:-$HOME/affect_aif}"
fi
CONDA_ROOT="${CONDA_ROOT:-$HOME/miniconda}"
ENV_NAME="${ENV_NAME:-affect_aif}"

sudo apt-get update
sudo apt-get install -y git wget htop screen tmux build-essential libopenblas-dev

if [ ! -d "$CONDA_ROOT" ]; then
    wget -q "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh" \
        -O /tmp/miniconda.sh
    bash /tmp/miniconda.sh -b -p "$CONDA_ROOT"
    rm -f /tmp/miniconda.sh
fi

source "$CONDA_ROOT/etc/profile.d/conda.sh"
conda config --set always_yes yes --set changeps1 no >/dev/null

if conda env list | awk '{print $1}' | grep -qx "$ENV_NAME"; then
    conda activate "$ENV_NAME"
    python -m pip install --upgrade pip
    python -m pip install -e "$PROJECT_ROOT"
else
    conda create -n "$ENV_NAME" python=3.11 >/dev/null
    conda activate "$ENV_NAME"
    python -m pip install --upgrade pip
    python -m pip install -e "$PROJECT_ROOT"
fi

# JAX CPU-only
python -m pip install jax jaxlib

# auto-activate on login
BASHRC="$HOME/.bashrc"
if ! grep -q "conda activate $ENV_NAME" "$BASHRC" 2>/dev/null; then
    echo "source $CONDA_ROOT/etc/profile.d/conda.sh && conda activate $ENV_NAME" >> "$BASHRC"
fi

echo "GCP setup complete for affect_aif. Conda env: $ENV_NAME"

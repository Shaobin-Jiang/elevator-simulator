#!/bin/bash

(
    export PATH="$HOME/.local/bin:$PATH"

    if ! command -v uv &> /dev/null; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
    fi

    if ! command -v git &> /dev/null; then
	sudo apt install git
    fi
    git config --global http.sslVerify false

    repo="$HOME/elevator-simulator"
    if [ ! -d "$repo" ]; then
        git clone https://github.com/Shaobin-Jiang/elevator-simulator "$repo"
    fi

    cd "$repo"

    if [ ! -d .venv ]; then
        uv venv
    fi

    uv sync
    uv run controller.py
)

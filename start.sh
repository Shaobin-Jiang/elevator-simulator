#!/bin/bash

(
    export PATH="$HOME/.local/bin:$PATH"

    if ! command -v uv &> /dev/null; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
    fi

    if [ ! -d .venv ]; then
        uv venv
    fi

    uv sync
    uv run controller.py
)

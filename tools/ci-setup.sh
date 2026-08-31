#!/bin/sh
# 生成物: tools/flow.py が flow.toml から生成した。直接編集せず、flow.toml を編集して python3 tools/flow.py render を実行する
set -eu
python3 -m pip install --break-system-packages uv
uv sync --frozen

#!/bin/sh
# 生成物: tools/flow.py が flow.toml から生成した。直接編集せず、flow.toml を編集して python3 tools/flow.py render を実行する
set -eu
echo 'flow.toml が未完成: ci_setup が未決定' >&2; exit 1

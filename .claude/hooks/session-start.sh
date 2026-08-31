#!/bin/bash
# SessionStart: 決定台帳の状態をコンテキストに注入する。stdout がそのままエージェントに見える。
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; then
  echo "このリポジトリの tools/flow.py と hooks は python3（3.11 以上）を必要とするが、見つからない。"
  exit 0
fi
python3 tools/flow.py status
exit 0

#!/bin/bash
# PostToolUse (Edit|Write|MultiEdit): 整形 → Linter → 型検査を即時実行し、失敗を exit 2 でエージェントに返す。
input=$(cat)
file=$(printf '%s' "$input" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("tool_input",{}).get("file_path",""))' 2>/dev/null)
[ -z "$file" ] && exit 0
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0

# 台帳が未完成なら Makefile は stub なので何もしない（pre-write.py が製品コードの編集を止めている）
python3 tools/flow.py status >/dev/null 2>&1 || exit 0

make fmt >/dev/null 2>&1
out=$(make lint typecheck 2>&1)
if [ $? -ne 0 ]; then
  echo "lint/typecheck failed after editing $file:" >&2
  echo "$out" | tail -40 >&2
  exit 2
fi
exit 0

#!/bin/bash
# .claude/hooks/post-edit.sh
input=$(cat)
file=$(jq -r '.tool_input.file_path // empty' <<<"$input")
[ -z "$file" ] && exit 0
cd "$CLAUDE_PROJECT_DIR" || exit 0

make fmt >/dev/null 2>&1
out=$(make lint typecheck 2>&1)
if [ $? -ne 0 ]; then
  echo "lint/typecheck failed after editing $file:" >&2
  echo "$out" | tail -40 >&2
  exit 2
fi
exit 0

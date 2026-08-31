#!/bin/sh
# ハーネスの回帰テスト: hook が「落ちるべき時に落ち、通るべき時に通る」ことを、エージェントを介さずに確認する。
# 前提: flow.toml が全項目決定済みで、language = python（フィクスチャが Python のため）。
set -u
cd "$(dirname "$0")/.." || exit 1
export CLAUDE_PROJECT_DIR="$(pwd)"
hook=.claude/hooks/post-edit.sh
pre=.claude/hooks/pre-write.py
fx=.claude/hooks/fixtures
fail=0

say() { printf '%s\n' "$*"; }
run_hook() { printf '{"tool_input":{"file_path":"%s"}}' "$1" | "$2" >/dev/null 2>/tmp/selftest.err; echo $?; }

say "[1] python3 tools/flow.py check"
python3 tools/flow.py check || { say "  失敗: 台帳が未完成か生成物が食い違っている"; exit 1; }

if [ "$(python3 tools/flow.py get language)" != "python" ]; then
  say "  スキップ [2]-[4]: フィクスチャは Python 専用（language=$(python3 tools/flow.py get language)）"
  exit 0
fi

mkdir -p src
say "[2] PreToolUse が生成物 Makefile の直接編集を止める（期待 exit 2）"
rc=$(run_hook "$CLAUDE_PROJECT_DIR/Makefile" "$pre"); [ "$rc" = 2 ] || { say "  失敗: exit=$rc"; fail=1; }

say "[3] 型エラーのあるファイルがあれば PostToolUse が exit 2 を返す"
cp "$fx/typecheck_probe.py" src/_probe.py
rc=$(run_hook "$CLAUDE_PROJECT_DIR/src/_probe.py" "$hook")
if [ "$rc" = 2 ] && grep -q "error" /tmp/selftest.err; then say "  ok"; else say "  失敗: exit=$rc"; cat /tmp/selftest.err; fail=1; fi
rm -f src/_probe.py

say "[4] 対照ファイルだけなら PostToolUse が exit 0 を返す"
cp "$fx/typecheck_ok.py" src/_ok.py
rc=$(run_hook "$CLAUDE_PROJECT_DIR/src/_ok.py" "$hook")
if [ "$rc" = 0 ]; then say "  ok"; else say "  失敗: exit=$rc"; cat /tmp/selftest.err; fail=1; fi
rm -f src/_ok.py
rmdir src 2>/dev/null || true

[ "$fail" = 0 ] && say "selftest: ok（ハーネスは落ちるべき時に落ち、通るべき時に通る）"
exit $fail

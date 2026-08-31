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
python3 tools/flow.py check || { say "  FAIL: ledger incomplete or drifted"; exit 1; }

if [ "$(python3 tools/flow.py get language)" != "python" ]; then
  say "  SKIP [2]-[4]: fixtures are Python-only (language=$(python3 tools/flow.py get language))"
  exit 0
fi

mkdir -p src
say "[2] PreToolUse blocks direct edit of generated Makefile (expect 2)"
rc=$(run_hook "$CLAUDE_PROJECT_DIR/Makefile" "$pre"); [ "$rc" = 2 ] || { say "  FAIL: exit=$rc"; fail=1; }

say "[3] PostToolUse returns exit 2 with a type-error file present"
cp "$fx/typecheck_probe.py" src/_probe.py
rc=$(run_hook "$CLAUDE_PROJECT_DIR/src/_probe.py" "$hook")
if [ "$rc" = 2 ] && grep -q "error" /tmp/selftest.err; then say "  ok"; else say "  FAIL: exit=$rc"; cat /tmp/selftest.err; fail=1; fi
rm -f src/_probe.py

say "[4] PostToolUse returns exit 0 with only the control file present"
cp "$fx/typecheck_ok.py" src/_ok.py
rc=$(run_hook "$CLAUDE_PROJECT_DIR/src/_ok.py" "$hook")
if [ "$rc" = 0 ]; then say "  ok"; else say "  FAIL: exit=$rc"; cat /tmp/selftest.err; fail=1; fi
rm -f src/_ok.py
rmdir src 2>/dev/null || true

[ "$fail" = 0 ] && say "selftest: ok"
exit $fail

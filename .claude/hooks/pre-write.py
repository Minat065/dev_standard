#!/usr/bin/env python3
"""PreToolUse (Edit|Write|MultiEdit):
1. 生成物への直接編集は常に止める。
2. flow.toml に未決定がある間は、台帳・ハーネス・ドキュメント以外への書き込みを止める。
exit 2 = ブロック（stderr がエージェントに返る）。それ以外は素通り。"""

import json
import os
import sys
from pathlib import Path

root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).resolve()


def load_flow():
    sys.path.insert(0, str(root / "tools"))
    import flow

    return flow


flow = load_flow()
GENERATED = set(flow.GENERATED)
ALLOWED_WHILE_PENDING = (
    "flow.toml",
    "INVARIANTS.md",
    "README.md",
    ".claude/",
    "tools/",
    "docs/",
    ".github/",
)

try:
    data = json.load(sys.stdin)
except (json.JSONDecodeError, UnicodeDecodeError):
    sys.exit(0)

fp = data.get("tool_input", {}).get("file_path") or ""
if not fp:
    sys.exit(0)
try:
    rel = Path(fp).resolve().relative_to(root).as_posix()
except ValueError:
    sys.exit(0)  # リポジトリ外はこの hook の管轄外

if rel in GENERATED:
    print(
        f"{rel} は flow.toml からの生成物。flow.toml を編集して python3 tools/flow.py render を実行する",
        file=sys.stderr,
    )
    sys.exit(2)

pending = flow.pending()
if pending and not rel.startswith(ALLOWED_WHILE_PENDING):
    keys = ", ".join(k for k, *_ in pending)
    print(
        f"ブロック: flow.toml に未決定の項目がある（{keys}）。人間が /setup で決めるまで製品コードは書けない。"
        "flow.toml を推測で埋めないこと。",
        file=sys.stderr,
    )
    sys.exit(2)
sys.exit(0)

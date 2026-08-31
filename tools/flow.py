#!/usr/bin/env python3
"""flow.toml（決定台帳）を単一の情報源として、決定の状態確認と生成物の描画を行う。

依存は Python 3.11+ の標準ライブラリのみ。

  python3 tools/flow.py status   未決定の項目を依存順に表示。未決定があれば exit 1
  python3 tools/flow.py next     次に決めるべき1項目を表示（/setup が使う）
  python3 tools/flow.py get KEY  決定済みの値を表示
  python3 tools/flow.py render   flow.toml から生成物を書き出す（未決定なら stub を書く）
  python3 tools/flow.py check    未決定がなく、生成物が flow.toml と一致していれば exit 0

生成物（直接編集しない。PreToolUse hook が編集を止める）:
  Makefile / tools/ci-setup.sh / .claude/settings.json
"""

from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "flow.toml"

# 順序 = 依存順。先頭が決まらないと後ろは決められない。
# (key, 表示名, 問いの説明, 値の型)
DECISIONS: list[tuple[str, str, str, type]] = [
    (
        "language",
        "実装言語",
        "python / typescript / go など。以降の決定はすべてこれに依存する。",
        str,
    ),
    (
        "formatter",
        "整形コマンド",
        "ファイルを書き換えるコマンド。失敗しないこと。例: ruff format .",
        str,
    ),
    (
        "linter",
        "Linter コマンド",
        "違反があれば非0で終了するコマンド。警告を出さない設定にする。例: ruff check .",
        str,
    ),
    (
        "typechecker",
        "型検査コマンド",
        "違反があれば非0で終了するコマンド。例: mypy --strict src/",
        str,
    ),
    (
        "test_runner",
        "テストコマンド",
        "失敗があれば非0で終了するコマンド。例: pytest -q",
        str,
    ),
    (
        "ci_setup",
        "CI でのツール導入手順",
        (
            "ubuntu-latest 上で上記4コマンドを使えるようにするシェル行のリスト。"
            '例: ["pip install ruff mypy pytest"]'
        ),
        list,
    ),
    (
        "prod_cli",
        "本番に届く CLI",
        (
            "このリポジトリから本番環境へ届きうるコマンド名のリスト（kubectl, aws, terraform など）。"
            "deny リストに入る。無ければ [] と明示する。"
        ),
        list,
    ),
]

GENERATED = {
    "Makefile": lambda d: render_makefile(d),
    "tools/ci-setup.sh": lambda d: render_ci_setup(d),
    ".claude/settings.json": lambda d: render_settings(d),
}


# ---------------------------------------------------------------- ledger


def load() -> dict:
    if not LEDGER.exists():
        return {}
    with LEDGER.open("rb") as f:
        return tomllib.load(f)


def decided(ledger: dict, key: str, typ: type) -> bool:
    """決定済み = テーブルが存在し、value が型に合い、reason が空でない。
    list 型は空リストでも「無いと決めた」として決定済みと扱う。"""
    sec = ledger.get(key)
    if not isinstance(sec, dict):
        return False
    if "value" not in sec or not isinstance(sec["value"], typ):
        return False
    if typ is str and not sec["value"].strip():
        return False
    return bool(str(sec.get("reason", "")).strip())


def pending(ledger: dict | None = None) -> list[tuple[str, str, str, type]]:
    ledger = load() if ledger is None else ledger
    return [d for d in DECISIONS if not decided(ledger, d[0], d[3])]


def value(ledger: dict, key: str):
    return ledger[key]["value"]


# ---------------------------------------------------------------- render

HEADER = "生成物: tools/flow.py が flow.toml から生成した。直接編集せず、flow.toml を編集して python3 tools/flow.py render を実行する"


def stub(target: str) -> str:
    return (
        f"\t@echo 'flow.toml が未完成: `{target}` が未決定。"
        f"/setup で決めてから python3 tools/flow.py render を実行する' >&2; exit 1"
    )


def render_makefile(d: dict) -> str:
    def cmd(key: str) -> str:
        return f"\t{value(d, key)}" if decided(d, key, str) else stub(key)

    return "\n".join(
        [
            f"# {HEADER}",
            ".PHONY: fmt lint typecheck test check",
            "fmt:        ## 整形（ファイルを書き換える。失敗しない）",
            cmd("formatter"),
            "lint:       ## Linter（違反があれば非0）",
            cmd("linter"),
            "typecheck:  ## 型（違反があれば非0）",
            cmd("typechecker"),
            "test:       ## テスト（失敗があれば非0）",
            cmd("test_runner"),
            "check: fmt lint typecheck test",
            "",
        ]
    )


def render_ci_setup(d: dict) -> str:
    lines = ["#!/bin/sh", f"# {HEADER}", "set -eu"]
    if decided(d, "ci_setup", list):
        lines += [str(x) for x in value(d, "ci_setup")] or ["# 導入手順なし"]
    else:
        lines.append("echo 'flow.toml が未完成: ci_setup が未決定' >&2; exit 1")
    return "\n".join(lines) + "\n"


BASE_DENY = [
    "Read(./.env)",
    "Read(./.env.*)",
    "Read(./secrets/**)",
    "Bash(rm -rf *)",
    "Bash(git push --force *)",
    "Bash(git push -f *)",
]


def render_settings(d: dict) -> str:
    deny = list(BASE_DENY)
    if decided(d, "prod_cli", list):
        deny += [f"Bash({c} *)" for c in value(d, "prod_cli")]

    def hook(script: str, timeout: int) -> dict:
        return {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/" + script,
            "args": [],
            "timeout": timeout,
        }

    settings = {
        "permissions": {"deny": deny},
        "hooks": {
            "SessionStart": [{"hooks": [hook("session-start.sh", 30)]}],
            "PreToolUse": [
                {"matcher": "Edit|Write|MultiEdit", "hooks": [hook("pre-write.py", 30)]}
            ],
            "PostToolUse": [
                {
                    "matcher": "Edit|Write|MultiEdit",
                    "hooks": [hook("post-edit.sh", 180)],
                }
            ],
        },
    }
    return json.dumps(settings, indent=2, ensure_ascii=False) + "\n"


def rendered(d: dict) -> dict[str, str]:
    return {path: fn(d) for path, fn in GENERATED.items()}


# ---------------------------------------------------------------- commands


def cmd_status() -> int:
    p = pending()
    if not p:
        print(
            "flow.toml: 全項目が決定済み。生成物は `python3 tools/flow.py check` で一致を確認できる。"
        )
        return 0
    print(
        "flow.toml に未決定の項目がある（依存順）。この状態では flow.toml と .claude/ と tools/ と "
        "ドキュメント以外への書き込みは PreToolUse hook で止まる。"
    )
    print(
        "未決定項目は人間が /setup で回答して決める。エージェントは環境検出や推測で flow.toml を埋めない。"
    )
    for key, name, _, _ in p:
        print(f"  - {key}（{name}）")
    return 1


def cmd_next() -> int:
    p = pending()
    if not p:
        print("すべて決定済み。次は: python3 tools/flow.py render")
        return 0
    key, name, desc, typ = p[0]
    print(f"key: {key}")
    print(f"name: {name}")
    print(f"type: {'list' if typ is list else 'string'}")
    print(f"description: {desc}")
    print(f"remaining_after_this: {len(p) - 1}")
    print("record_as:")
    print(f"  [{key}]")
    print(f"  value = {'[...]' if typ is list else '"..."'}")
    print('  reason = "人間が述べた理由"')
    print('  decided_by = "回答者"')
    return 0


def cmd_get(key: str) -> int:
    d = load()
    if key not in {k for k, *_ in DECISIONS}:
        print(f"不明な項目: {key}", file=sys.stderr)
        return 2
    if not any(k == key and decided(d, k, t) for k, _, _, t in DECISIONS):
        print(f"{key}: 未決定", file=sys.stderr)
        return 1
    v = value(d, key)
    print(json.dumps(v, ensure_ascii=False) if isinstance(v, list) else v)
    return 0


def cmd_render() -> int:
    d = load()
    for path, content in rendered(d).items():
        target = ROOT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        if path.endswith(".sh"):
            target.chmod(0o755)
        print(f"生成: {path}")
    p = pending(d)
    if p:
        print(f"注意: 未決定が {len(p)} 項目あるため、その部分は stub を生成した。")
    return 0


def cmd_check() -> int:
    d = load()
    ok = True
    p = pending(d)
    if p:
        ok = False
        print("check: 未決定の項目: " + ", ".join(k for k, *_ in p))
    for path, content in rendered(d).items():
        target = ROOT / path
        if not target.exists():
            ok = False
            print(f"check: 生成物 {path} が存在しない")
        elif target.read_text(encoding="utf-8") != content:
            ok = False
            print(
                f"check: {path} が flow.toml と食い違っている（python3 tools/flow.py render を実行する）"
            )
    if ok:
        print("check: ok（未決定なし、生成物は flow.toml と一致）")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] in {"-h", "--help"}:
        print(__doc__)
        return 0
    cmd = argv[1]
    if cmd == "status":
        return cmd_status()
    if cmd == "next":
        return cmd_next()
    if cmd == "get" and len(argv) == 3:
        return cmd_get(argv[2])
    if cmd == "render":
        return cmd_render()
    if cmd == "check":
        return cmd_check()
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))

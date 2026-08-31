# dev_standard
AI駆動開発のスタンダード環境。設計は `docs/development-flow-v2.md` を参照。

## 状態
決定台帳 `flow.toml` は全項目決定済み（Python / uv / ruff / mypy --strict / pytest）。
生成物（Makefile / tools/ci-setup.sh / .claude/settings.json）は台帳と一致している。

## 日常の使い方
- `make check` … 整形・Linter・型・テストを一括実行。hook と CI も同じものを呼ぶ
- `sh tools/selftest.sh` … ハーネスが「落ちるべき時に落ち、通るべき時に通る」ことを確認
- 決定を変えるとき … `flow.toml` を編集して `python3 tools/flow.py render`。生成物の直接編集は hook と CI が止める
- 新しい決定項目が増えたとき … `tools/flow.py` の DECISIONS に追加すると、`/setup` がその項目だけを人間に問う

## 初回セットアップ（別プロジェクトにこの標準を適用するとき）
1. `flow.toml` の決定済みセクションを削除し、`claude` を起動する。SessionStart hook が未決定項目を表示する。
2. `/setup` を実行し、依存順に1問ずつ答える。決めるのは人間で、エージェントは選択肢を出すだけである。未決定の間、製品コードへの書き込みは hook で止まる。
3. 全項目が埋まると生成物が描画される。言語のプロジェクト初期化（Python なら `uv init` と `uv add --dev ...`）をしてから `make check` と `sh tools/selftest.sh` を通す。
4. GitHub でブランチ保護を有効にし、workflow `check` と Code Owner のレビューを必須にする。管理者も例外にしない。

## 構成
- `flow.toml` 決定台帳（単一の情報源。人間の回答と理由だけを書く）
- `INVARIANTS.md` このリポジトリ自身が守る不変条件
- `tools/flow.py` 台帳の状態確認と生成物の描画（Python 3.11+ 標準ライブラリのみ）
- `.claude/hooks/` SessionStart（状態注入）/ PreToolUse（未決定時と生成物の編集ブロック）/ PostToolUse（整形・Linter・型）
- `.claude/skills/setup/` `/setup` skill
- `.claude/hooks/fixtures/` hook の回帰テスト用フィクスチャ（意図的な型エラーとその対照）
- `pyproject.toml` / `uv.lock` ツールの依存を固定。CI は `uv sync --frozen` で同じものを入れる
- `src/` 製品コード（mypy --strict の対象）、`tests/` テスト

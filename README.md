# dev_standard
AI駆動開発のスタンダード環境。設計は `docs/development-flow-v2.md` を参照。

## 使い始める順序
1. `claude` を起動する。SessionStart hook が flow.toml の未決定項目を表示する。
2. `/setup` を実行する。未決定項目を依存順に1つずつ質問されるので、値と理由を答える。
   決めるのは人間で、エージェントは選択肢を出すだけである。未決定の間、製品コードへの書き込みは hook で止まる。
3. 全項目が埋まると `python3 tools/flow.py render` が Makefile / tools/ci-setup.sh / .claude/settings.json を生成する。
4. `sh tools/selftest.sh` でハーネスが「落ちるべき時に落ち、通るべき時に通る」ことを確認する。
5. GitHub でブランチ保護を有効にし、workflow `check` を必須にする。管理者も例外にしない。

## 構成
- `flow.toml` 決定台帳（単一の情報源。人間の回答だけを書く）
- `INVARIANTS.md` このリポジトリ自身が守る不変条件
- `tools/flow.py` 台帳の状態確認と生成物の描画（Python 3.11+ 標準ライブラリのみ）
- `.claude/hooks/` SessionStart（状態注入）/ PreToolUse（未決定時と生成物の編集ブロック）/ PostToolUse（整形・Linter・型）
- `.claude/skills/setup/` `/setup` skill
- `.claude/hooks/fixtures/` hook の回帰テスト用フィクスチャ（意図的な型エラーとその対照）
- 生成物: `Makefile` / `tools/ci-setup.sh` / `.claude/settings.json`

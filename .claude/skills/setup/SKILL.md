---
name: setup
description: flow.toml（決定台帳）の未決定項目を依存順に1つずつ人間に問い、回答と理由を記録し、生成物を描画する。リポジトリの初期セットアップ、または新しい決定項目が増えたときに使う。
---

# /setup — 決定台帳を人間の回答で埋める

## 役割分担
- 決めるのは人間。エージェントは選択肢を提示するだけで、値を推測で書かない。
- 環境検出（インストール済みツールなど）は「選択肢の提案」に使う。「決定」には使わない。
- 1回に1項目だけ問う。回答を得るまで次の項目に進まない。

## 手順
1. `python3 tools/flow.py next` を実行し、次に決める項目（key / description）を得る。
   「すべて決定済み」なら手順 5 へ。
2. その項目について環境を調べ、2〜4 個の選択肢を作る。
   例: language なら `python3 --version` / `node --version` / `go version` と既存ファイルの拡張子。
   例: formatter/linter/typechecker なら `which ruff mypy pyright eslint prettier tsc gofmt` の結果。
   調査結果は「事実」として短く示す（「mypy 1.19 が入っている」）。推奨はしてよいが、推奨を書き込まない。
3. 人間に1つだけ質問する。項目名、説明、選択肢、その根拠となる事実を示し、回答と**理由**を求める。
   ここでターンを終える。
4. 回答を得たら flow.toml に次の形で追記する（既存のコメント例に倣う）:
   ```
   [<key>]
   value = <回答>            # list 型は ["..."] 形式。無いなら []
   reason = "<人間が述べた理由>"
   decided_by = "<回答者>"
   ```
   人間が理由を述べなかったら理由を求める。理由が空の項目は未決定として扱われる。
   追記後、手順 1 に戻る。
5. 全項目が決定済みになったら `python3 tools/flow.py render` を実行し、
   続けて `python3 tools/flow.py check` が `check: ok` を出すことを確認する。
6. `make check` を実行し、結果を人間に報告する。ツールが未インストールなら、
   flow.toml の ci_setup の内容を手元で実行してよいか人間に確認してから実行する。

## 禁止
- flow.toml の value を、人間の回答以外の根拠で書くこと。
- 複数項目をまとめて質問すること。
- 生成物（Makefile / tools/ci-setup.sh / .claude/settings.json）を直接編集すること。

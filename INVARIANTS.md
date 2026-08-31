# INVARIANTS — dev_standard 自身が守ること

形式: 条項 / 内容 / 理由 / 機械検査 / 区分（外部規範の参照 or 自社差分）。
機械検査に落とせない部分は不変条件レーンのレビュー観点として残る。

## I-1 未決定の状態は main に入らない
- 内容: flow.toml に未決定項目がある、または生成物（Makefile / tools/ci-setup.sh / .claude/settings.json）が flow.toml と食い違うコミットは、main にマージされない。
- 理由: 未決定の空白はエージェントが推測で埋める。実例として、言語が未決定の状態でエージェントに作業させたところ、エージェントが環境から Python を推論して言語を決めた（2026-08-30）。
- 機械検査: CI の `python3 tools/flow.py check`（未決定と drift の両方を検出）。ブランチ保護で必須にする。
- 区分: 自社差分。

## I-2 flow.toml の値は人間の明示的な回答からのみ書かれる
- 内容: エージェントは環境検出や推測の結果で flow.toml を埋めない。/setup で人間が答えた値と、人間が述べた理由だけを書く。flow.toml と INVARIANTS.md の変更は CODEOWNER の approve なしにマージされない。
- 理由: 決定の責任の所在を人間に固定する。理由を書かせるのは、決定の根拠を可視で批評可能にし、暗黙知の継承経路にするため（development-flow-v2 Phase 0）。
- 機械検査: `.github/CODEOWNERS` + ブランチ保護（承認者の強制）。「推測で書いたか」は機械検査できないため、flow.toml を含む PR のレビュー観点として残る。
- 区分: 自社差分。

## I-3 生成物は直接編集されない
- 内容: Makefile / tools/ci-setup.sh / .claude/settings.json は flow.toml から生成する。直接編集は行わない。
- 理由: hook・CI・人間が同じコマンドを呼ぶことを、規約ではなく単一の生成元で保証するため。生成元が分かれると「hook で通って CI で落ちる」差が生まれる。
- 機械検査: PreToolUse hook（`.claude/hooks/pre-write.py`）がエージェントの直接編集を止める。人間の直接編集は CI の drift 検出（I-1）で止まる。
- 区分: 自社差分。

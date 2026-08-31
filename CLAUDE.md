# Commands
- check all: `make check`
- format: `make fmt` / lint: `make lint` / types: `make typecheck` / test: `make test`
- decision ledger: `python3 tools/flow.py status|next|render|check`
- initial setup: `/setup`

# Rules
- 決定（言語・ツール・本番 CLI）は flow.toml が単一の情報源。値は人間が /setup で答えたものだけを書く。推測で埋めない。
- Makefile / tools/ci-setup.sh / .claude/settings.json は生成物。編集するなら flow.toml を編集して `python3 tools/flow.py render`。
- INVARIANTS.md に触れる変更は、実装前に該当条項を人間に確認する。

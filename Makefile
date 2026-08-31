# 生成物: tools/flow.py が flow.toml から生成した。直接編集せず、flow.toml を編集して python3 tools/flow.py render を実行する
.PHONY: fmt lint typecheck test check
fmt:        ## 整形（ファイルを書き換える。失敗しない）
	uv run ruff format .
lint:       ## Linter（違反があれば非0）
	uv run ruff check .
typecheck:  ## 型（違反があれば非0）
	uv run mypy --strict src/
test:       ## テスト（失敗があれば非0）
	uv run pytest -q
check: fmt lint typecheck test

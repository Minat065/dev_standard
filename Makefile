# 生成物: tools/flow.py が flow.toml から生成した。直接編集せず、flow.toml を編集して python3 tools/flow.py render を実行する
.PHONY: fmt lint typecheck test check
fmt:        ## 整形（ファイルを書き換える。失敗しない）
	@echo 'flow.toml が未完成: `formatter` が未決定。/setup で決めてから python3 tools/flow.py render を実行する' >&2; exit 1
lint:       ## Linter（違反があれば非0）
	@echo 'flow.toml が未完成: `linter` が未決定。/setup で決めてから python3 tools/flow.py render を実行する' >&2; exit 1
typecheck:  ## 型（違反があれば非0）
	@echo 'flow.toml が未完成: `typechecker` が未決定。/setup で決めてから python3 tools/flow.py render を実行する' >&2; exit 1
test:       ## テスト（失敗があれば非0）
	@echo 'flow.toml が未完成: `test_runner` が未決定。/setup で決めてから python3 tools/flow.py render を実行する' >&2; exit 1
check: fmt lint typecheck test

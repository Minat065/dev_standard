# Makefile
fmt:        ## 整形（ファイルを書き換える。失敗しない）
	<formatter> --write .
lint:       ## Linter（失敗すると非0）
	<linter> .
typecheck:  ## 型（失敗すると非0）
	<typechecker>
test:       ## テスト（ステージ2まで空でよい）
	<test-runner>
check: fmt lint typecheck test



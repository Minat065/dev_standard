"""型チェックのパイプライン検証用サンプル（意図的に型エラーを含む）。

`make typecheck` が「落ちること」を確認するためのファイル。
各エラーには mypy が出すべきエラーコードをコメントで併記してある。
検証が終わったら削除するか、除外設定に入れること。
"""

from dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str


def double(n: int) -> int:
    return n * 2


def find_user(users: dict[int, User], user_id: int) -> User | None:
    return users.get(user_id)


# 1) 引数の型違い: int を期待しているのに str を渡す  -> [arg-type]
double("21")


# 2) 戻り値の型違い: int を宣言しているのに str を返す  -> [return-value]
def triple(n: int) -> int:
    return f"{n * 3}"


# 3) 代入の型違い: str に int を代入  -> [assignment]
label: str = 42

# 4) Optional の未処理: User | None に対して .name へ直接アクセス  -> [union-attr]
users: dict[int, User] = {1: User(id=1, name="alice")}
print(find_user(users, 2).name)

# 5) 存在しない属性  -> [attr-defined]
print(users[1].email)

# 6) 演算子の型不一致: str + int  -> [operator]
message = "count: " + len(users)

# 7) 引数の数違い  -> [call-arg]
User(id=2)

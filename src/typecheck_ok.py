"""型チェックの対照用サンプル（型エラーを含まない）。

`make typecheck` がこのファイル単体では通ることを確認するための対照群。
「常に落ちる設定になっている」偽陽性を切り分けられる。
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


def main() -> None:
    users: dict[int, User] = {1: User(id=1, name="alice")}
    print(double(21))

    user = find_user(users, 2)
    if user is None:
        print("not found")
    else:
        print(user.name)

    print(f"count: {len(users)}")


if __name__ == "__main__":
    main()

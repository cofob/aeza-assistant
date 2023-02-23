from dataclasses import dataclass
from json import dump, load
from typing import TypeVar, Type, Any
from io import TextIOWrapper

C = TypeVar("C", bound="ChatManager")


@dataclass
class Chat:
    telegram_id: int


class ChatManager:
    def __init__(self) -> None:
        self.users: dict[int, Chat] = {}

    def add_user(self, user: Chat) -> None:
        self.users[user.telegram_id] = user

    def get_user(self, telegram_id: int, default: Any = None) -> Chat:
        return self.users.get(telegram_id, default)

    def get_users(self) -> list[Chat]:
        """Very slow operation."""
        return list(self.users.values())

    def remove_user(self, telegram_id: int) -> None:
        self.users.pop(telegram_id, None)

    def update_user(self, user: Chat) -> None:
        self.users[user.telegram_id] = user

    def dump(self, file: TextIOWrapper) -> None:
        dump(self.users, file)

    @classmethod
    def load(cls: Type[C], file: TextIOWrapper) -> C:
        users = load(file)
        manager = cls()
        for user in users.values():
            manager.add_user(Chat(**user))
        return manager

from aiogram import BaseMiddleware
from aiogram.types import Message
from logging import getLogger
from random import randint

from typing import Any, Awaitable, Callable, Dict


log = getLogger(__name__)


class ArgsMiddleware(BaseMiddleware):
    def __init__(self, **kwargs: Any) -> None:
        self.data = kwargs

    async def __call__(  # type: ignore
        self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], event: Message, data: Dict[str, Any]
    ) -> Any:
        for key, value in self.data.items():
            data[key] = value

        return await handler(event, data)


class ErrorHandlerMiddleware(BaseMiddleware):
    async def __call__(  # type: ignore
        self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], event: Message, data: Dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            exception_id = randint(100000000, 999999999)

            log.exception(f"Exception ID: {exception_id}")
            log.exception(e)

            return await event.answer(
                f"Произошла ошибка. Попробуйте позже. Код ошибки {exception_id}, можете сообщить о нём на @cofob."
            )

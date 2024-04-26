from logging import getLogger
from random import randint
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy.orm import sessionmaker

from .models.chat import ChatModel

logger = getLogger(__name__)


class ErrorHandlerMiddleware(BaseMiddleware):
    async def __call__(  # type: ignore
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            exception_id = randint(100000000, 999999999)

            logger.exception(f"Exception ID: {exception_id}")
            logger.exception(e)

            return await event.answer(
                f"Произошла ошибка. Попробуйте позже. Код ошибки {exception_id}, можете сообщить о нём на @egor_aeza."
            )


class DatabaseMiddleware(BaseMiddleware):
    """Middleware that add database engine to the state."""

    def __init__(self, maker: sessionmaker) -> None:
        """Initialize middleware."""
        self.maker = maker

    async def __call__(  # type: ignore
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        """Add database engine to the state."""
        async with self.maker() as session:
            data["db"] = session
            await handler(event, data)
            await session.commit()


class ChatModelMiddleware(BaseMiddleware):
    """Middleware that add chat to the database."""

    async def __call__(  # type: ignore
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        """Add database engine to the state."""
        session = data["db"]
        try:
            chat_id = event.chat.id
        except AttributeError:
            chat_id = event.message.chat.id  # type: ignore
        chat = await ChatModel.get(session, chat_id)
        if not chat:
            chat = ChatModel(telegram_id=chat_id)
            await chat.save(session)
        data["chat_model"] = chat

        return await handler(event, data)

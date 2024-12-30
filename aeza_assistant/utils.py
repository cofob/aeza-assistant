from asyncio import sleep
from logging import getLogger
from typing import AsyncGenerator

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models.chat import ChatModel

logger = getLogger(__name__)


async def is_user_admin(bot: Bot, chat_id: int, user_id: int) -> bool:
    """Check if user is admin in chat."""
    user = await bot.get_chat_member(chat_id, user_id)
    return user.status in ["creator", "administrator"]


async def subscribed_chat_iterator(
    session: AsyncSession,
) -> AsyncGenerator[ChatModel, None]:
    """Get subscribed chats."""
    page = 0
    limit = 1000
    while True:
        query = (
            select(ChatModel)
            .where(ChatModel.is_subscribed == True)
            .offset(page * limit)
            .limit(limit)
            .order_by(ChatModel.priority.desc())
        )
        chats = (await session.execute(query)).scalars().all()
        if not chats:
            break
        for chat in chats:
            yield chat
        page += 1


async def send_notification_message(
    bot: Bot,
    chat_id: int,
    text: str,
    photo: str | None = None,
    video: str | None = None,
    message_thread_id: int | None = None,
) -> None:
    """Send a notification message to the chat."""
    if photo and video:
        raise ValueError("Cannot send both photo and video")
    logger.debug(f"Sending notification to {chat_id}")
    retry_count = 0
    while True:
        if retry_count >= 3:
            logger.error(f"Failed to send notification to {chat_id} too many times")
            break
        try:
            if photo:
                await bot.send_photo(
                    chat_id, photo, caption=text, message_thread_id=message_thread_id
                )
            elif video:
                await bot.send_video(
                    chat_id, video, caption=text, message_thread_id=message_thread_id
                )
            else:
                await bot.send_message(
                    chat_id,
                    text,
                    disable_web_page_preview=True,
                    message_thread_id=message_thread_id,
                )
        except TelegramRetryAfter as e:
            logger.info(
                f"Failed to send notification to {chat_id}, retrying in {e.retry_after} seconds"
            )
            await sleep(e.retry_after)
            retry_count += 1
            continue
        except TelegramForbiddenError:
            logger.exception(
                f"Failed to send notification to {chat_id}, probably user blocked bot"
            )
            break
        except Exception as e:
            logger.exception(f"Failed to send notification to {chat_id}")
            break
        break

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.chat import ChatModel
from ..texts import Texts
from ..utils import is_user_admin

router = Router()


@router.message(Command("set_thread"))
async def set_thread(
    message: Message, bot: Bot, db: AsyncSession, chat_model: ChatModel
) -> None:
    """Set thread handler."""
    if message.chat.type != "supergroup":
        await message.answer(Texts.only_forums)
        return
    if message.message_thread_id is None:
        await message.answer(Texts.only_forums)
        return
    if message.from_user is None:
        raise ValueError("Message.from_user is None")
    if not await is_user_admin(bot, message.chat.id, message.from_user.id):
        await message.answer(Texts.no_rights)
        return
    chat_model.forum_thread_id = message.message_thread_id
    await chat_model.save(db)
    await message.answer(Texts.forum_thread_set)


@router.message(Command("remove_thread"))
async def remove_thread(
    message: Message, bot: Bot, db: AsyncSession, chat_model: ChatModel
) -> None:
    """Remove thread handler."""
    if message.from_user is None:
        raise ValueError("Message.from_user is None")
    if not await is_user_admin(bot, message.chat.id, message.from_user.id):
        await message.answer(Texts.no_rights)
        return
    chat_model.forum_thread_id = None
    await chat_model.save(db)
    await message.answer(Texts.forum_thread_removed)

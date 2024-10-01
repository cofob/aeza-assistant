from asyncio import Queue

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.chat import ChatModel
from ..texts import Texts
from ..utils import send_notification_message, subscribed_chat_iterator

router = Router()


async def _check_is_admin(message: Message, chat_model: ChatModel) -> bool:
    if message.chat.type != "private":
        await message.answer(Texts.pm_for_command)
        return False
    if not chat_model.is_admin:
        await message.answer(Texts.not_admin)
        return False
    return True


@router.message(Command("add_admin"))
async def add_admin(message: Message, chat_model: ChatModel, db: AsyncSession) -> None:
    """Start handler."""
    if not await _check_is_admin(message, chat_model):
        return

    if not message.text:
        await message.answer("Usage: /add_admin <user_id>")
        return

    args = message.text.split()

    if len(args) < 2:
        await message.answer("Usage: /add_admin <user_id>")
        return

    user_id = int(args[1])

    new_admin_model = await ChatModel.get(db, user_id)

    if not new_admin_model:
        await message.answer("User not found")
        return

    new_admin_model.is_admin = True
    await new_admin_model.save(db)
    await message.answer("User added as admin")


@router.message(Command("remove_admin"))
async def remove_admin(
    message: Message, chat_model: ChatModel, db: AsyncSession
) -> None:
    """Start handler."""
    if not await _check_is_admin(message, chat_model):
        return

    if not message.text:
        await message.answer("Usage: /remove_admin <user_id>")
        return

    args = message.text.split()

    if len(args) < 2:
        await message.answer("Usage: /remove_admin <user_id>")
        return

    user_id = int(args[1])

    admin_model = await ChatModel.get(db, user_id)

    if not admin_model:
        await message.answer("User not found")
        return

    admin_model.is_admin = False
    await admin_model.save(db)
    await message.answer("User removed as admin")


@router.message(Command("list_admins"))
async def list_admins(
    message: Message, chat_model: ChatModel, db: AsyncSession
) -> None:
    """Start handler."""
    if not await _check_is_admin(message, chat_model):
        return

    admins = await ChatModel.get_list_by_key(db, ChatModel.is_admin, True, limit=1000)
    await message.answer("\n".join(f"id: {admin.telegram_id}" for admin in admins))


@router.message(Command("set_chat_priority"))
async def set_chat_priority(
    message: Message, chat_model: ChatModel, db: AsyncSession
) -> None:
    """Start handler."""
    if not await _check_is_admin(message, chat_model):
        return

    if not message.text:
        await message.answer("Usage: /set_chat_priority <chat_id> <priority>")
        return

    args = message.text.split()

    if len(args) < 3:
        await message.answer("Usage: /set_chat_priority <chat_id> <priority>")
        return

    chat_id = int(args[1])
    priority = int(args[2])

    requested_chat_model = await ChatModel.get(db, chat_id)

    if not requested_chat_model:
        await message.answer("Chat not found")
        return

    requested_chat_model.priority = priority
    await requested_chat_model.save(db)
    await message.answer("Chat priority set")


@router.message(Command("broadcast"))
async def broadcast(
    message: Message, bot: Bot, chat_model: ChatModel, queue: Queue, db: AsyncSession
) -> None:
    """Start handler."""
    if not await _check_is_admin(message, chat_model):
        return

    text = message.html_text

    if not text:
        await message.answer("Usage: /broadcast <message>")
        return

    if not text.startswith("/broadcast "):
        await message.answer("Usage: /broadcast <message>")
        return

    photo = None
    if message.photo:
        photo = message.photo[-1].file_id

    text = text[len("/broadcast ") :]

    async for chat in subscribed_chat_iterator(db):
        await queue.put(
            send_notification_message(
                bot,
                chat.telegram_id,
                text,
                photo=photo,
                message_thread_id=chat.forum_thread_id,
            )
        )


@router.message(Command("stats"))
async def stats(message: Message, chat_model: ChatModel, db: AsyncSession) -> None:
    """Start handler."""
    if not await _check_is_admin(message, chat_model):
        return

    total_count_query = select(func.count(ChatModel.telegram_id)).select_from(ChatModel)
    total_count = (await db.execute(total_count_query)).scalar()

    subscribed_count_query = (
        select(func.count(ChatModel.telegram_id))
        .where(ChatModel.is_subscribed == True)
        .select_from(ChatModel)
    )
    subscribed_count = (await db.execute(subscribed_count_query)).scalar()

    await message.answer(
        f"Total chat count: {total_count}\nSubscribed chat count: {subscribed_count}"
    )

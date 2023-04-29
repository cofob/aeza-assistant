from asyncio import sleep

from aiogram.filters import Command
from aiogram.types import Message

from ..keyboards.subscribe import SubscribeKeyboard
from ..models.chat import ChatModel
from ..texts import Texts
from .router import router


@router.message(Command("start"))
async def start(message: Message, chat_model: ChatModel) -> None:
    """Start handler."""
    if not chat_model.is_subscribed:
        m = await message.answer(Texts.start, reply_markup=SubscribeKeyboard.subscribe)
    else:
        m = await message.answer(
            Texts.start_subscribed, reply_markup=SubscribeKeyboard.unsubscribe
        )

    if message.chat.type != "private":
        await sleep(60)
        await m.delete()
        try:
            await message.delete()
        except Exception:
            pass


@router.message(Command("help"))
async def help(message: Message) -> None:
    """Help handler."""
    if message.chat.type != "private":
        m = await message.answer(Texts.pm_for_command)
        await sleep(15)
        await m.delete()
        try:
            await message.delete()
        except Exception:
            pass
        return
    await message.answer(Texts.help)

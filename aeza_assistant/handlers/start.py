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
        await message.answer(Texts.start, reply_markup=SubscribeKeyboard.subscribe)
    else:
        await message.answer(
            Texts.start_subscribed, reply_markup=SubscribeKeyboard.unsubscribe
        )


@router.message(Command("help"))
async def help(message: Message) -> None:
    """Help handler."""
    await message.answer(Texts.help)

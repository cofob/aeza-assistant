from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from ..callback_types.subscribe import SubscribeCallback
from ..models.chat import ChatModel
from ..texts import Texts
from .router import router


@router.message(Command("start"))
async def start(message: Message, chat_model: ChatModel) -> None:
    """Start handler."""
    if not chat_model.is_subscribed:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=Texts.subscribe,
                        callback_data=SubscribeCallback(action=True).pack(),
                    ),
                ],
            ],
        )
        await message.answer(Texts.start, reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=Texts.unsubscribe,
                        callback_data=SubscribeCallback(action=False).pack(),
                    ),
                ],
            ],
        )
        await message.answer(Texts.start_subscribed, reply_markup=keyboard)

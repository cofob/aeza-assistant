from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from ..callback_types.subscribe import SubscribeCallback
from ..texts import Texts


class SubscribeKeyboard:
    subscribe = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=Texts.subscribe,
                    callback_data=SubscribeCallback(action=True).pack(),
                ),
            ],
        ],
    )

    unsubscribe = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=Texts.unsubscribe,
                    callback_data=SubscribeCallback(action=False).pack(),
                ),
            ],
        ],
    )

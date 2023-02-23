from aiogram.filters import Command
from aiogram.types import Message

from ..state import BotState
from ..texts import Texts
from .router import router


@router.message(Command("status"))
async def status(message: Message, bot_state: BotState) -> None:
    """Start handler."""
    text = []
    for name in bot_state.current_statuses:
        text.append(
            name
            + " "
            + ("доступен" if bot_state.current_statuses[name] else "недоступен")
        )
    await message.answer("Текущий статус:\n" + ",\n".join(text) + ".")

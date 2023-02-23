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
            Texts.available.format(name)
            if bot_state.current_statuses[name]
            else Texts.unavailable.format(name)
        )
    await message.answer(Texts.current_status.format(",\n".join(text) + "."))

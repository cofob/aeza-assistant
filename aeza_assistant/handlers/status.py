from asyncio import sleep

from aiogram.filters import Command
from aiogram.types import Message

from ..constants import SORTED_GROUPS
from ..state import BotState
from ..texts import Texts
from .router import router


@router.message(Command("status"))
async def status(message: Message, bot_state: BotState) -> None:
    """Start handler."""
    if not bot_state.current_statuses:
        m = await message.answer(Texts.bot_is_loading)
    else:
        text = []
        for name in SORTED_GROUPS:
            if name not in bot_state.current_statuses:
                continue
            text.append(
                Texts.available.format(name)
                if bot_state.current_statuses[name]
                else Texts.unavailable.format(name)
            )
        m = await message.answer(Texts.current_status.format(",\n".join(text) + "."))

    if message.chat.type != "private":
        await sleep(60)
        try:
            await m.delete()
        except Exception:
            pass
        try:
            await message.delete()
        except Exception:
            pass

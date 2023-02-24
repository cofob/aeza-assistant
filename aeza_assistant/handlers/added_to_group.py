from logging import getLogger

from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.types import ChatMemberUpdated

from ..keyboards.subscribe import SubscribeKeyboard
from ..texts import Texts
from .router import router

log = getLogger(__name__)


@router.my_chat_member()
async def on_chat_member_updated(update: ChatMemberUpdated, bot: Bot) -> None:
    if update.chat.type == "private":
        return
    if (
        update.new_chat_member.status == ChatMemberStatus.MEMBER
        and update.old_chat_member.status == ChatMemberStatus.LEFT
        and update.new_chat_member.user.id == bot.id
    ):
        log.info(f"Bot was added to chat {update.chat.id}")
        await bot.send_message(
            update.chat.id,
            Texts.added_to_chat.format(username=update.new_chat_member.user.username),
            reply_markup=SubscribeKeyboard.subscribe,
        )

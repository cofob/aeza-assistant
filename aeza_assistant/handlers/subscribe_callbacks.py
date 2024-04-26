from logging import getLogger

from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from ..callback_types.subscribe import SubscribeCallback
from ..keyboards.subscribe import SubscribeKeyboard
from ..models.chat import ChatModel
from ..texts import Texts
from ..utils import is_user_admin

router = Router()

logger = getLogger(__name__)


@router.callback_query(SubscribeCallback.filter(F.action == True))
async def subscribe(
    callback_query: CallbackQuery, bot: Bot, db: AsyncSession, chat_model: ChatModel
) -> None:
    """Subscribe handler."""
    if callback_query.message is None:
        return
    if callback_query.message.chat.type != "private":
        if not await is_user_admin(
            bot, callback_query.message.chat.id, callback_query.from_user.id
        ):
            await callback_query.answer(Texts.no_rights)
            return
    logger.info("Chat %s subscribed", callback_query.message.chat.id)
    chat_model.is_subscribed = True
    await chat_model.save(db)
    await callback_query.answer(Texts.subscribed)
    if isinstance(callback_query.message, Message):
        await callback_query.message.edit_text(
            Texts.start_subscribed, reply_markup=SubscribeKeyboard.unsubscribe
        )


@router.callback_query(SubscribeCallback.filter(F.action == False))
async def unsubscribe(
    callback_query: CallbackQuery, bot: Bot, db: AsyncSession, chat_model: ChatModel
) -> None:
    """Unsubcribe handler."""
    if callback_query.message is None:
        return
    if callback_query.message.chat.type != "private":
        if not await is_user_admin(
            bot, callback_query.message.chat.id, callback_query.from_user.id
        ):
            await callback_query.answer(Texts.no_rights)
            return
    logger.info("Chat %s unsubscribed", callback_query.message.chat.id)
    chat_model.is_subscribed = False
    await chat_model.save(db)
    await callback_query.answer(Texts.unsubscribed)
    if isinstance(callback_query.message, Message):
        await callback_query.message.edit_text(
            Texts.start, reply_markup=SubscribeKeyboard.subscribe
        )

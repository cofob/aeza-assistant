from aiogram import Bot


async def is_user_admin(bot: Bot, chat_id: int, user_id: int) -> bool:
    """Check if user is admin in chat."""
    user = await bot.get_chat_member(chat_id, user_id)
    return user.status in ["creator", "administrator"]

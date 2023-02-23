"""Chat model."""

from sqlalchemy import BigInteger, Boolean, Column

from .abc import AbstractModel


class ChatModel(AbstractModel):
    """Telegram chat model."""

    __tablename__ = "chats"

    telegram_id: int = Column(BigInteger, primary_key=True)
    """Telegram chat ID."""
    is_subscribed: bool = Column(Boolean, default=False)
    """Is the chat subscribed to the bot updates?"""

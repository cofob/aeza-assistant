"""Chat model."""

from sqlalchemy import BigInteger, Boolean, Column, SmallInteger

from .abc import AbstractModel


class ChatModel(AbstractModel):
    """Telegram chat model."""

    __tablename__ = "chats"

    telegram_id: int = Column(BigInteger, primary_key=True)
    """Telegram chat ID."""
    is_subscribed: bool = Column(Boolean, default=False, nullable=False)
    """Is the chat subscribed to the bot updates?"""
    is_admin: bool = Column(Boolean, default=False, nullable=False)
    """Is the chat an admin?"""
    priority: int = Column(SmallInteger, default=0, nullable=False)
    """Chat send priority."""

from aiogram.filters.callback_data import CallbackData


class SubscribeCallback(CallbackData, prefix="sub"):
    """Callback data for subscribe callback."""

    action: bool

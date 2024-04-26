"""This module contains the router for the bot's handlers."""

from aiogram import Router

from .added_to_group import router as added_to_group_router
from .admin import router as admin_router
from .start import router as start_router
from .status import router as status_router
from .subscribe_callbacks import router as subscribe_callbacks_router

router = Router()
"""Router for the bot's handlers."""

router.include_routers(
    added_to_group_router,
    admin_router,
    start_router,
    status_router,
    subscribe_callbacks_router,
)

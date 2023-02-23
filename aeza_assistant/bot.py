"""Bot fabric."""

from logging import getLogger

from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import ClientSession

from asyncio import run, create_task

from pathlib import Path

from .handlers import router
from .middlewares import ArgsMiddleware, ErrorHandlerMiddleware
from .db import ChatManager
from .cron import Cron
from .aeza import Aeza

log = getLogger(__name__)


class BotFabric:
    """Bot fabric class."""

    def __init__(
        self,
        token: str,
        aeza_token: str,
        data_dir: str,
        session: ClientSession,
        storage: BaseStorage = MemoryStorage(),
    ) -> None:
        """Initialize bot fabric."""
        self.token = token
        self.aeza_token = aeza_token
        self.session = session
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.bot = Bot(token=self.token)
        self.aeza = Aeza(token=self.aeza_token)

        if (self.data_dir / "users.json").exists():
            with open(self.data_dir / "users.json", "r") as file:
                self.chat_db = ChatManager.load(file)
        else:
            self.chat_db = ChatManager()

        self.cron = Cron(bot=self.bot, chat_db=self.chat_db, api=self.aeza)

        # Create dispatcher
        dispatcher = Dispatcher(storage=storage)
        # Add middlewares
        dispatcher.message.middleware(ArgsMiddleware(chat_db=self.chat_db))
        dispatcher.message.middleware(ErrorHandlerMiddleware())  # must be last
        # Add handlers
        dispatcher.include_router(router.router)

        self.dispatcher = dispatcher

    async def run(self) -> None:
        create_task(self.cron.run())
        await self.dispatcher.start_polling(self.bot)

    def run_sync(self) -> None:
        run(self.run())

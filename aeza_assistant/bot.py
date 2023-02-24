"""Bot fabric."""

from asyncio import Queue, create_task, run
from logging import getLogger
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .aeza import Aeza
from .cron import Cron
from .handlers import router
from .middlewares import (
    ArgsMiddleware,
    ChatModelMiddleware,
    DatabaseMiddleware,
    ErrorHandlerMiddleware,
)
from .queue import TaskQueue
from .state import BotState

log = getLogger(__name__)


class BotFabric:
    """Bot fabric class."""

    def __init__(
        self,
        token: str,
        database_url: str,
        push_addresses: str = "",
        aeza_http_proxy: str | None = None,
        session: ClientSession = ClientSession(),
        storage: BaseStorage = MemoryStorage(),
    ) -> None:
        """Initialize bot fabric."""
        self.state = BotState(current_statuses={})
        self.queue: Queue[Any] = Queue()
        self.task_queue = TaskQueue(self.queue)

        self.engine = create_async_engine(
            database_url, future=True, pool_size=50, max_overflow=100
        )
        self.sessionmaker = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)  # type: ignore

        self.token = token
        self.session = session
        self.bot = Bot(token=self.token)
        self.aeza = Aeza(session=self.session, http_proxy=aeza_http_proxy)

        self.cron = Cron(
            bot=self.bot,
            maker=self.sessionmaker,
            api=self.aeza,
            bot_state=self.state,
            queue=self.queue,
            push_addresses=self._parse_push_addresses(push_addresses),
            session=self.session,
        )

        # Create dispatcher
        dispatcher = Dispatcher(storage=storage)
        # Add middlewares
        for event_type in ["message", "callback_query"]:
            event_handler = getattr(dispatcher, event_type)
            event_handler.middleware(ArgsMiddleware(bot_state=self.state))
            event_handler.middleware(DatabaseMiddleware(self.sessionmaker))
            event_handler.middleware(ChatModelMiddleware())
            event_handler.middleware(ErrorHandlerMiddleware())  # must be last
        # Add handlers
        dispatcher.include_router(router.router)

        self.dispatcher = dispatcher

    @staticmethod
    def _parse_push_addresses(inp: str) -> dict[str, str]:
        """Parse push addresses."""
        inp = inp.strip()
        if not inp:
            return {}
        # Format: "name1|address1,name2|address2"
        out = {}
        spl1 = inp.split(",")
        for item in spl1:
            spl2 = item.split("|")
            if len(spl2) != 2:
                raise ValueError("Invalid format")
            out[spl2[0].strip()] = spl2[1].strip()
        return out

    async def run(self) -> None:
        create_task(self.cron.run())
        await self.task_queue.start()
        await self.dispatcher.start_polling(self.bot)

    def run_sync(self) -> None:
        run(self.run())

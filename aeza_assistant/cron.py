"""Cron jobs for the bot."""

from asyncio import Queue, create_task, sleep
from logging import getLogger
from time import time

from aiogram import Bot
from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from .aeza import Aeza
from .constants import TARIFF_GROUPS
from .state import BotState
from .texts import Texts
from .utils import send_notification_message, subscribed_chat_iterator

logger = getLogger(__name__)


class Cron:
    def __init__(
        self,
        bot: Bot,
        maker: sessionmaker,
        api: Aeza,
        bot_state: BotState,
        queue: Queue,
        session: ClientSession,
        push_addresses: dict[str, str] = {},
    ) -> None:
        self.bot = bot
        self.maker = maker
        self.interval = 58
        self.notify_sleep = 60
        self.api = api
        self.queue = queue
        self.bot_state = bot_state
        self.prev_statuses: dict[str, tuple[bool, float]] = {}
        self.last_notified: dict[str, bool] = {}
        self.push_addresses = push_addresses
        self.session = session

    async def run(self) -> None:
        while True:
            logger.debug("Cron job started")
            try:
                create_task(self.job())
            except Exception as e:
                logger.exception("Cron job failed")
                logger.exception(e)
            await sleep(self.interval)

    async def send_notification(
        self, session: AsyncSession, statuses: dict[str, bool]
    ) -> None:
        """Send a notification to all subscribed chats."""
        text = Texts.state_changed.format(
            ",\n".join(
                (
                    Texts.available.format(name)
                    if status
                    else Texts.unavailable.format(name)
                )
                for name, status in statuses.items()
            )
            + "."
        )
        i = 0
        async for chat in subscribed_chat_iterator(session):
            await self.queue.put(
                send_notification_message(
                    self.bot,
                    chat.telegram_id,
                    text,
                    message_thread_id=chat.forum_thread_id,
                )
            )
        logger.info(f"Sent notification to approx ~{i} chats")

    async def send_push(self, url: str) -> None:
        async with self.session.get(url) as resp:
            logger.debug(f"Push notification for {url} sent")
            if resp.status != 200:
                logger.error(
                    f"Push notification for {url} failed with {resp.status}: {await resp.text()}"
                )

    async def job(self) -> None:
        async with self.maker() as session:
            await self._job(session)

    async def _job(self, session: AsyncSession) -> None:
        statuses = await self.api.get_product_group_statuses()
        logger.debug(f"(_job) Statuses: {statuses}")
        readable_statuses = {}
        for group_id, status in statuses.items():
            try:
                readable_statuses[TARIFF_GROUPS[group_id]] = status
            except KeyError:
                pass
        logger.debug(f"(_job) Readable statuses: {readable_statuses}")

        self.bot_state.current_statuses = readable_statuses

        curr_time = time()

        curr_statuses: dict[str, tuple[bool, float]] = {}
        changed_statuses: list[str] = []

        for name in readable_statuses:
            if name not in self.last_notified:
                self.last_notified[name] = readable_statuses[name]

        for name in readable_statuses:
            if name not in self.prev_statuses:
                logger.debug(f"New tariff group: {name}")
                self.prev_statuses[name] = (
                    readable_statuses[name],
                    curr_time,
                )
                changed_statuses.append(name)
            elif (
                name in self.prev_statuses
                and self.prev_statuses[name][0] == readable_statuses[name]
            ):
                logger.debug(f"Tariff group {name} is still {readable_statuses[name]}")
                curr_statuses[name] = (
                    readable_statuses[name],
                    self.prev_statuses[name][1],
                )
            elif (
                name in self.prev_statuses
                and self.prev_statuses[name][0] != readable_statuses[name]
            ):
                logger.info(
                    f"Tariff group {name} changed from {self.prev_statuses[name][0]} to {readable_statuses[name]}"
                )
                curr_statuses[name] = (
                    readable_statuses[name],
                    curr_time,
                )
                self.prev_statuses[name] = curr_statuses[name]
                changed_statuses.append(name)

        for name in self.prev_statuses:
            if name in self.push_addresses and self.prev_statuses[name][0]:
                create_task(self.send_push(self.push_addresses[name]))

        changed = {}

        for name in self.prev_statuses:
            status, last_change = self.prev_statuses[name]
            if (
                curr_time - last_change >= self.notify_sleep
                and self.last_notified.get(name, status) is not status
            ):
                self.last_notified[name] = status
                changed[name] = status

        if changed:
            await self.send_notification(session, changed)

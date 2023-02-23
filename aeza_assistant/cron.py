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
from .models.chat import ChatModel
from .state import BotState

log = getLogger(__name__)


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
        self.interval = 50
        self.notify_sleep = 60 * 30
        self.api = api
        self.queue = queue
        self.bot_state = bot_state
        self.prev_statuses: dict[str, tuple[bool, float]] = {}
        self.notified_statuses: dict[str, bool] = {}
        self.push_addresses = push_addresses
        self.session = session

    async def run(self) -> None:
        while True:
            log.info("Cron job started")
            session = self.maker()
            try:
                await self.job(session)
            except Exception as e:
                log.exception("Cron job failed")
                log.exception(e)
            log.info("Cron job finished")
            await sleep(self.interval)

    async def send_notification(self, session: AsyncSession, name: str, status: bool) -> None:
        chats = await ChatModel.get_list_by_key(session, ChatModel.is_subscribed, True)
        for chat in chats:
            self.queue.put_nowait(
                self.bot.send_message(
                    chat.telegram_id,
                    f"Тарифная группа {name} теперь {'включена' if status else 'выключена'}.",
                )
            )

    async def send_push(self, url: str) -> None:
        async with self.session.get(url) as resp:
            log.debug(f"Push notification for {url} sent")
            if resp.status != 200:
                log.error(f"Push notification for {url} failed with {resp.status}: {await resp.text()}")

    async def job(self, session: AsyncSession) -> None:
        statuses = await self.api.get_product_group_statuses()
        readable_statuses = {}
        for group_id, status in statuses.items():
            try:
                readable_statuses[TARIFF_GROUPS[group_id]] = status
            except KeyError:
                pass

        self.bot_state.current_statuses = readable_statuses

        curr_time = time()

        curr_statuses: dict[str, tuple[bool, float]] = {}
        changed_statuses: list[str] = []

        for name in readable_statuses:
            if name not in self.prev_statuses:
                log.debug(f"New tariff group: {name}")
                self.prev_statuses[name] = (
                    readable_statuses[name],
                    curr_time,
                )
                changed_statuses.append(name)
            elif name in self.prev_statuses and self.prev_statuses[name][0] == readable_statuses[name]:
                log.debug(f"Tariff group {name} is still {readable_statuses[name]}")
                curr_statuses[name] = (
                    readable_statuses[name],
                    self.prev_statuses[name][1],
                )
            elif name in self.prev_statuses and self.prev_statuses[name][0] != readable_statuses[name]:
                log.info(f"Tariff group {name} changed from {self.prev_statuses[name][0]} to {readable_statuses[name]}")
                curr_statuses[name] = (
                    readable_statuses[name],
                    curr_time,
                )
                self.prev_statuses[name] = curr_statuses[name]
                changed_statuses.append(name)

        for name in self.prev_statuses:
            if name in self.push_addresses and self.prev_statuses[name][0]:
                create_task(self.send_push(self.push_addresses[name]))

        for name in self.prev_statuses:
            status, last_change = self.prev_statuses[name]
            if curr_time - last_change >= self.notify_sleep and self.notified_statuses.get(name, status) != status:
                self.notified_statuses[name] = status
                log.info("Tariff is changed state for more than 1 hour, sending notification")
                await self.send_notification(session, name, status)

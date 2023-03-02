"""Cron jobs for the bot."""

from asyncio import Queue, create_task, sleep
from logging import getLogger
from time import time
from typing import Sequence

from aiogram import Bot
from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from .aeza import Aeza
from .constants import TARIFF_GROUPS
from .models.chat import ChatModel
from .state import BotState
from .texts import Texts

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
        self.interval = 45
        self.notify_sleep = 60 * 60
        self.api = api
        self.queue = queue
        self.bot_state = bot_state
        self.prev_statuses: dict[str, tuple[bool, float]] = {}
        self.last_notified: dict[str, bool] = {}
        self.push_addresses = push_addresses
        self.session = session

    async def run(self) -> None:
        while True:
            log.debug("Cron job started")
            try:
                async with self.maker() as session:
                    await self.job(session)
            except Exception as e:
                log.exception("Cron job failed")
                log.exception(e)
            await sleep(self.interval)

    async def _send_notification_message(self, chat_id: int, text: str) -> None:
        """Send a notification message to the chat."""
        log.debug(f"Sending notification to {chat_id}")
        try:
            await self.bot.send_message(chat_id, text)
        except Exception as e:
            log.exception(f"Failed to send notification to {chat_id}")
            log.exception(e)

    async def send_notification(
        self, session: AsyncSession, statuses: dict[str, bool]
    ) -> None:
        """Send a notification to all subscribed chats."""
        text = Texts.state_changed.format(
            ",\n".join(
                Texts.available.format(name)
                if status
                else Texts.unavailable.format(name)
                for name, status in statuses.items()
            )
            + "."
        )
        i = 0
        limit = 150
        chats: Sequence[ChatModel] = []
        while True:
            chats = await ChatModel.get_list_by_key(
                session, ChatModel.is_subscribed, True, limit=limit, offset=i * limit
            )
            if not chats:
                break
            for chat in chats:
                self.queue.put_nowait(
                    self._send_notification_message(chat.telegram_id, text)
                )
            i += 1
        log.info(f"Sent notification to approx ~{i * limit} chats")

    async def send_push(self, url: str) -> None:
        async with self.session.get(url) as resp:
            log.debug(f"Push notification for {url} sent")
            if resp.status != 200:
                log.error(
                    f"Push notification for {url} failed with {resp.status}: {await resp.text()}"
                )

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
            if name not in self.last_notified:
                self.last_notified[name] = readable_statuses[name]

        for name in readable_statuses:
            if name not in self.prev_statuses:
                log.debug(f"New tariff group: {name}")
                self.prev_statuses[name] = (
                    readable_statuses[name],
                    curr_time,
                )
                changed_statuses.append(name)
            elif (
                name in self.prev_statuses
                and self.prev_statuses[name][0] == readable_statuses[name]
            ):
                log.debug(f"Tariff group {name} is still {readable_statuses[name]}")
                curr_statuses[name] = (
                    readable_statuses[name],
                    self.prev_statuses[name][1],
                )
            elif (
                name in self.prev_statuses
                and self.prev_statuses[name][0] != readable_statuses[name]
            ):
                log.info(
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

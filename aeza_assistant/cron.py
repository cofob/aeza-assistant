"""Cron jobs for the bot."""

from asyncio import sleep
from logging import getLogger

from aiogram import Bot
from .db import ChatManager
from .aeza import Aeza

log = getLogger(__name__)


class Cron:
    def __init__(self, bot: Bot, chat_db: ChatManager, api: Aeza, interval: int = 300) -> None:
        self.bot = bot
        self.chat_db = chat_db
        self.interval = interval
        self.api = api

    async def run(self) -> None:
        while True:
            log.info("Cron job started")
            await self.job()
            log.info("Cron job finished")
            await sleep(self.interval)

    async def job(self) -> None:
        print(await self.api.get_product_group_statuses())

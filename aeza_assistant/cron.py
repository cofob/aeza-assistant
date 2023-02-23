"""Cron jobs for the bot."""

from asyncio import sleep
from logging import getLogger
from typing import Any

from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from .aeza import Aeza

log = getLogger(__name__)


class Cron:
    def __init__(
        self, bot: Bot, maker: sessionmaker, api: Aeza, interval: int = 300
    ) -> None:
        self.bot = bot
        self.maker = maker
        self.interval = interval
        self.api = api

    async def run(self) -> None:
        while True:
            log.info("Cron job started")
            session = self.maker()
            await self.job(session)
            log.info("Cron job finished")
            await sleep(self.interval)

    async def job(self, session: AsyncSession) -> None:
        print(await self.api.get_product_group_statuses())

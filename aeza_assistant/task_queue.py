import asyncio
from logging import getLogger
from typing import Any

logger = getLogger(__name__)


class TaskQueue:
    def __init__(self, queue: asyncio.Queue, sleep_time: float = 0.1) -> None:
        self.queue = queue
        self.sleep_time = sleep_time
        self.task: asyncio.Task[Any] | None = None

    async def worker(self) -> None:
        while True:
            task = await self.queue.get()
            try:
                await task
            except Exception as e:
                logger.exception("Exception in task queue")
                logger.exception(e)
            await asyncio.sleep(self.sleep_time)

    async def start(self) -> None:
        self.task = asyncio.create_task(self.worker())

    async def stop(self) -> None:
        if self.task is not None:
            self.task.cancel()
            await self.task

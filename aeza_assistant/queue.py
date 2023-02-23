import asyncio
from typing import Any


class TaskQueue:
    def __init__(self, queue: asyncio.Queue, sleep_time: float = 0.5) -> None:
        self.queue = queue
        self.sleep_time = sleep_time
        self.task: asyncio.Task[Any] | None = None

    async def worker(self) -> None:
        while True:
            task = await self.queue.get()
            asyncio.create_task(task)
            await asyncio.sleep(self.sleep_time)
            self.queue.task_done()

    async def start(self) -> None:
        self.task = asyncio.create_task(self.worker())

    async def stop(self) -> None:
        if self.task is not None:
            self.task.cancel()
            await self.task

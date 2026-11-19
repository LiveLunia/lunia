import asyncio
from collections.abc import Awaitable, Callable

from lunia.core.logging import get_logger

from .models import EventEnvelope

logger = get_logger(__name__)

type AsyncHandler = Callable[[EventEnvelope], Awaitable[None]]


class AsyncConsumer:
    """通过同步接收入口排队，并逐条执行异步处理器。"""

    def __init__(
        self,
        handler: AsyncHandler,
        maxsize: int = 256,
    ) -> None:
        self.handler = handler
        self.mailbox: asyncio.Queue[EventEnvelope] = asyncio.Queue(maxsize=maxsize)
        self._task: asyncio.Task[None] | None = None

    def receive(self, envelope: EventEnvelope) -> None:
        self.mailbox.put_nowait(envelope)

    def start(self) -> None:
        self._task = asyncio.create_task(self.run())

    async def run(self) -> None:
        while True:
            envelope = await self.mailbox.get()

            try:
                await self.handler(envelope)
            except Exception:
                logger.exception("消费者处理事件失败")
            finally:
                self.mailbox.task_done()

    async def stop(self) -> None:
        if self._task is None:
            return

        await self.mailbox.join()
        self._task.cancel()

        try:
            await self._task
        except asyncio.CancelledError:
            pass

        self._task = None

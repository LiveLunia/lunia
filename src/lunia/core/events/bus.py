import asyncio
from typing import Any

from .dispatcher import EventDispatcher


class EventBus:
    """Lunia 进程内事件总线"""

    def __init__(
        self,
        dispatcher: EventDispatcher,
        maxsize: int = 1024,
    ) -> None:
        self.dispatcher = dispatcher
        self.queue: asyncio.Queue[tuple[str, Any]] = asyncio.Queue(maxsize=maxsize)
        self._task: asyncio.Task[None] | None = None
        self._accepting = False

    async def start(self) -> None:
        """启动事件投递循环"""
        if self._task is not None:
            raise RuntimeError("EventBus 已经启动")

        self._accepting = True
        self._task = asyncio.create_task(
            self._run(),
            name="lunia-event-bus",
        )

    def publish(self, event_type: str, event: Any) -> None:
        """非阻塞入队；队列满时明确拒绝"""
        if not self._accepting:
            raise RuntimeError("EventBus 未运行")

        self.queue.put_nowait((event_type, event))

    async def _run(self) -> None:
        """按照入队顺序投递事件"""
        while True:
            event_type, event = await self.queue.get()

            try:
                self.dispatcher.dispatch(event_type, event)
            finally:
                self.queue.task_done()

    async def stop(self) -> None:
        """停止接收事件，排空队列后关闭循环"""
        if self._task is None:
            return

        self._accepting = False
        await self.queue.join()

        self._task.cancel()

        try:
            await self._task
        except asyncio.CancelledError:
            pass

        self._task = None

import asyncio
from typing import Any

from lunia.core.logging import get_logger

from .dispatcher import EventDispatcher

logger = get_logger(__name__)


class EventBus:
    """Lunia 进程内事件总线"""

    def __init__(
        self,
        dispatcher: EventDispatcher,
        maxsize: int = 1024,
    ) -> None:
        self.dispatcher = dispatcher
        self.queue: asyncio.Queue[tuple[str, Any]] = asyncio.Queue(maxsize=maxsize)
        self.dropped_events = 0
        self._task: asyncio.Task[None] | None = None
        self._accepting = False

    async def start(self) -> None:
        """启动事件投递循环"""
        if self._task is not None:
            raise RuntimeError("EventBus 不允许多次启动")

        self._accepting = True
        self._task = asyncio.create_task(
            self._run(),
            name="lunia-event-bus",
        )

    def _check_worker(self) -> None:
        """检查事件投递任务是否意外结束。"""
        if self._task is None:
            raise RuntimeError("EventBus 尚未启动")

        if not self._task.done():
            return

        if self._task.cancelled():
            raise RuntimeError("EventBus 投递任务已取消")

        exc = self._task.exception()
        if exc is not None:
            raise RuntimeError("EventBus 投递任务异常退出") from exc

        raise RuntimeError("EventBus 投递任务意外结束")

    def publish(self, event_type: str, event: Any) -> bool:
        """非阻塞入队；返回是否成功入队"""
        if not self._accepting:
            raise RuntimeError("EventBus 未运行")

        self._check_worker()

        try:
            self.queue.put_nowait((event_type, event))
        except asyncio.QueueFull:
            self.dropped_events += 1

            if self.dropped_events == 1 or self.dropped_events % 10 == 0:
                logger.warning(
                    "EventBus 队列已满, 拒收事件: event_type=%s, dropped_events=%d",
                    event_type,
                    self.dropped_events,
                )
            return False

        return True

    async def _run(self) -> None:
        """按照入队顺序投递事件"""
        while True:
            event_type, event = await self.queue.get()

            try:
                self.dispatcher.dispatch(event_type, event)
            finally:
                self.queue.task_done()

    async def stop(self, timeout: float = 5.0) -> None:
        """停止事件接收，排空队列并回收投递任务"""
        if self._task is None:
            return

        if timeout <= 0:
            raise ValueError("timeout 必须大于 0")

        self._accepting = False
        worker = self._task
        drain = asyncio.create_task(
            self.queue.join(),
            name="lunia-event-bus-drain",
        )

        try:
            done, _ = await asyncio.wait(
                {drain, worker},
                timeout=timeout,
                return_when=asyncio.FIRST_COMPLETED,
            )

            if worker in done:
                if worker.cancelled():
                    raise RuntimeError("EventBus 投递任务意外取消")

                exc = worker.exception()
                if exc is not None:
                    raise RuntimeError("EventBus 投递任务异常退出") from exc

                raise RuntimeError("EventBus 投递任务意外结束")

            if drain not in done:
                raise TimeoutError(
                    f"EventBus 关闭超时: {timeout}s, 剩余队列事件: {self.queue.qsize()}"
                )

        finally:
            if not drain.done():
                drain.cancel()

            await asyncio.gather(
                drain,
                return_exceptions=True,
            )

            if not worker.done():
                worker.cancel()

            await asyncio.gather(
                worker,
                return_exceptions=True,
            )

            self._task = None

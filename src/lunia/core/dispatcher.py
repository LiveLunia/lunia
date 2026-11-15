import asyncio
from collections.abc import Callable, Coroutine
from typing import Any

from .logging import get_logger

logger = get_logger(__name__)

type EventHandler = Callable[[Any], Coroutine[Any, Any, None]]


class EventDispatcher:
    """Lunia 内部事件分发器."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = {}
        self._tasks: set[asyncio.Task[None]] = set()
        self._closed = False

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """订阅指定事件."""
        handlers = self._handlers.setdefault(event_type, [])

        if handler not in handlers:
            handlers.append(handler)

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """取消订阅指定事件."""
        handlers = self._handlers.get(event_type)

        if handlers is None:
            return

        if handler in handlers:
            handlers.remove(handler)

        if not handlers:
            del self._handlers[event_type]

    def _on_task_done(self, task: asyncio.Task[None]) -> None:
        """清理已完成任务并记录异常."""
        self._tasks.discard(task)

        if task.cancelled():
            return

        exc = task.exception()
        if exc is not None:
            logger.error(
                "事件处理器执行失败.",
                exc_info=(type(exc), exc, exc.__traceback__),
            )

    def dispatch(self, event_type: str, event: Any) -> None:
        """投递事件给所有订阅者."""
        if self._closed:
            raise RuntimeError("EventDispatcher 已停止运行")

        handlers = tuple(self._handlers.get(event_type, []))

        for handler in handlers:
            task = asyncio.create_task(handler(event))
            self._tasks.add(task)
            task.add_done_callback(self._on_task_done)

    async def shutdown(self, timeout: float = 5.0) -> None:
        """等待未完成任务, 超时后取消."""
        self._closed = True
        tasks = tuple(self._tasks)
        logger.info("事件分发器正在关闭，剩余任务: %d", len(tasks))

        if not tasks:
            return

        _, pending = await asyncio.wait(
            tasks,
            timeout=timeout,
        )

        for task in pending:
            task.cancel()

        if pending:
            await asyncio.gather(
                *pending,
                return_exceptions=True,
            )

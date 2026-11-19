import asyncio

import pytest

from lunia.core.events.bus import EventBus
from lunia.core.events.dispatcher import EventDispatcher


def test_bus_fifo() -> None:
    async def scenario() -> None:
        dispatcher = EventDispatcher()
        bus = EventBus(dispatcher)

        received: list[int] = []

        dispatcher.subscribe("test", received.append)

        await bus.start()

        bus.publish("test", 1)
        bus.publish("test", 2)
        bus.publish("test", 3)

        await bus.stop()

        assert received == [1, 2, 3]

    asyncio.run(scenario())


def test_bus_rejects_when_full() -> None:
    async def scenario() -> None:
        dispatcher = EventDispatcher()
        bus = EventBus(dispatcher, maxsize=1)

        received: list[int] = []
        dispatcher.subscribe("test", received.append)

        await bus.start()

        # 中间没有 await，Bus 的投递任务还没有机会运行
        assert bus.publish("test", 1) is True
        assert bus.publish("test", 2) is False
        assert bus.dropped_events == 1

        await bus.stop()

        assert received == [1]

    asyncio.run(scenario())


def test_bus_detects_worker_failure() -> None:
    async def scenario() -> None:
        class BrokenDispatcher(EventDispatcher):
            def dispatch(self, event_type, event):
                raise ValueError("模拟投递循环故障")

        bus = EventBus(BrokenDispatcher())

        await bus.start()
        bus.publish("test", "A")

        # 让后台投递任务得到运行机会
        await asyncio.sleep(0)

        with pytest.raises(
            RuntimeError,
            match="投递任务异常退出",
        ):
            bus.publish("test", "B")

        # 暂不调用旧版 stop()：
        # 下一步要修复它对异常退出任务的等待问题。

    asyncio.run(scenario())


def test_bus_stop_is_idempotent() -> None:
    async def scenario() -> None:
        bus = EventBus(EventDispatcher())

        await bus.start()
        bus.publish("test", 1)

        await bus.stop()
        await bus.stop()

        assert bus._task is None

    asyncio.run(scenario())


def test_bus_stop_after_worker_failure() -> None:
    async def scenario() -> None:
        class BrokenDispatcher(EventDispatcher):
            def dispatch(self, event_type, event):
                raise ValueError("模拟分发故障")

        bus = EventBus(BrokenDispatcher())

        await bus.start()
        bus.publish("test", "A")
        bus.publish("test", "B")

        await asyncio.sleep(0)

        with pytest.raises(
            RuntimeError,
            match="投递任务异常退出",
        ):
            await asyncio.wait_for(bus.stop(), timeout=1)

        assert bus._task is None
        assert bus.queue.qsize() == 1

    asyncio.run(scenario())


def test_bus_stop_timeout() -> None:
    async def scenario() -> None:
        bus = EventBus(EventDispatcher())

        await bus.start()

        # 人为增加一项未完成工作，模拟无法排空
        bus.queue.put_nowait(("test", "A"))
        bus.queue.get_nowait()

        with pytest.raises(
            TimeoutError,
            match="关闭超时",
        ):
            await bus.stop(timeout=0.05)

        assert bus._task is None

    asyncio.run(scenario())

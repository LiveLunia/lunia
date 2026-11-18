import asyncio

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

"""测试napcat事件"""

import asyncio
import os

from lunia.adapters.napcat.adapter import NapCatAdapter
from lunia.adapters.napcat.client import NapCatClient
from lunia.core.events.bus import EventBus
from lunia.core.events.dispatcher import EventDispatcher
from lunia.core.logging import setup_logging


async def main() -> None:
    bus = EventBus(EventDispatcher())
    adapter = NapCatAdapter(bus)
    client = NapCatClient(
        url="ws://127.0.0.1:3799",
        token=os.environ["NAPCAT_TOKEN"],
        on_event=adapter.on_event,
    )

    await bus.start()
    try:
        await client.run()
    finally:
        await bus.stop()


if __name__ == "__main__":
    setup_logging()
    asyncio.run(main())

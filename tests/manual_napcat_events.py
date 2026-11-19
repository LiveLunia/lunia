"""测试napcat事件"""

import asyncio
import os

from lunia.adapters.napcat.adapter import NapCatAdapter
from lunia.core.events.bus import EventBus
from lunia.core.events.dispatcher import EventDispatcher
from lunia.core.logging import setup_logging


async def main() -> None:
    bus = EventBus(EventDispatcher())
    adapter = NapCatAdapter(
        adapter_id="main",
        bus=bus,
        url="ws://127.0.0.1:3799",
        token=os.environ["NAPCAT_TOKEN"],
    )

    await bus.start()
    await adapter.start()
    try:
        await adapter.run()
    finally:
        await bus.stop()


if __name__ == "__main__":
    setup_logging()
    asyncio.run(main())

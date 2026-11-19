import asyncio
import os

from lunia.adapters.napcat.adapter import NapCatAdapter
from lunia.core.events.bus import EventBus
from lunia.core.events.dispatcher import EventDispatcher
from lunia.core.events.models import EventEnvelope
from lunia.core.logging import get_logger, setup_logging
from lunia.formatters.ui import format_chat_event

logger = get_logger("lunia.test.chat_ui")


def on_chat_ui(envelope: EventEnvelope) -> None:
    """显示事件文本"""
    logger.info(format_chat_event(envelope.event))


async def main() -> None:
    dispatcher = EventDispatcher()
    bus = EventBus(dispatcher)
    adapter = NapCatAdapter(
        adapter_id="main",
        bus=bus,
        url="ws://127.0.0.1:3799",
        token=os.environ["NAPCAT_TOKEN"],
    )
    for kind in ("chat.message", "chat.poke", "chat.recall"):
        dispatcher.subscribe(kind, on_chat_ui)

    await bus.start()
    await adapter.start()
    try:
        await adapter.run()
    finally:
        await bus.stop()


if __name__ == "__main__":
    setup_logging()
    asyncio.run(main())

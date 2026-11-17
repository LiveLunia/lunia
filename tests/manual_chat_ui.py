import asyncio
import os

from lunia.adapters.napcat.adapter import NapCatAdapter
from lunia.adapters.napcat.client import NapCatClient
from lunia.core.dispatcher import EventDispatcher
from lunia.core.events import ChatEvent
from lunia.core.logging import get_logger, setup_logging
from lunia.formatters.ui import format_chat_event

logger = get_logger("lunia.test.chat_ui")


async def on_chat_ui(event: ChatEvent) -> None:
    """显示事件文本"""
    logger.info(format_chat_event(event))


async def main() -> None:
    dispatcher = EventDispatcher()
    adapter = NapCatAdapter(dispatcher)
    for kind in ("chat.message", "chat.poke", "chat.recall"):
        dispatcher.subscribe(kind, on_chat_ui)

    client = NapCatClient(
        url="ws://127.0.0.1:3799",
        token=os.environ["NAPCAT_TOKEN"],
        on_event=adapter.on_event,
    )

    try:
        await client.run()
    finally:
        await dispatcher.shutdown()


if __name__ == "__main__":
    setup_logging()
    asyncio.run(main())

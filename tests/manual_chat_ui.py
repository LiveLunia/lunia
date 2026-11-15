import asyncio
import os
from typing import Any

from lunia.adapters.napcat.client import NapCatClient
from lunia.adapters.napcat.parser import parse_chat
from lunia.core.cache import ConversationCache, UserNameCache
from lunia.core.logging import get_logger, setup_logging
from lunia.formatters.ui import format_chat_event
from lunia.resolvers.conversation import ConversationResolver

# from lunia.resolvers.username import UserNameResolver

logger = get_logger("lunia.test.chat_ui")


class TestChatClient(NapCatClient):
    """只用于真实聊天格式化测试。"""

    def __init__(self, url: str, token: str) -> None:
        super().__init__(url, token)

        self.namecache = UserNameCache()
        self.convercache = ConversationCache()
        # self.nameresolver = UserNameResolver(self.namecache)
        self.convresolver = ConversationResolver(self.convercache)

    async def _handle_message(self, data: dict[str, Any]) -> None:
        if data.get("echo") is not None:
            await super()._handle_message(data)
            return

        try:
            event = parse_chat(data)
            if event is None:
                return
            # resolved = self.nameresolver.resolve(event)
            # resolved = self.convresolver.resolve(resolved)
            formatted = format_chat_event(event)
            logger.info(formatted)

        except Exception:
            logger.exception("Chat UI 测试失败")


async def main() -> None:
    client = TestChatClient(
        url="ws://127.0.0.1:3799",
        token=os.environ["NAPCAT_TOKEN"],
    )

    await client.run()


if __name__ == "__main__":
    setup_logging()
    asyncio.run(main())

import asyncio
import os

from lunia.adapters.napcat.adapter import NapCatAdapter
from lunia.adapters.napcat.provider import NapCatUserProvider
from lunia.core.actions.models import SendMessage
from lunia.core.actions.router import ActionRouter
from lunia.core.cache import ConversationCache, UserNameCache
from lunia.core.events.bus import EventBus
from lunia.core.events.consumer import AsyncConsumer
from lunia.core.events.dispatcher import EventDispatcher
from lunia.core.events.models import EventEnvelope
from lunia.core.logging import get_logger, setup_logging
from lunia.formatters.ui import format_chat_event
from lunia.resolvers.conversation import ConversationResolver
from lunia.resolvers.username import UserNameResolver

logger = get_logger("lunia.core.runtime")


class Runtime:
    def __init__(self) -> None:
        # 1. 创建事件分发
        self.dispatcher = EventDispatcher()
        self.bus = EventBus(self.dispatcher)

        # 2. 创建 NapCat 事件适配器与连接
        self.adapter = NapCatAdapter(
            adapter_id="main",
            bus=self.bus,
            url="ws://127.0.0.1:3799",
            token=os.environ["NAPCAT_TOKEN"],
        )

        # 3. 创建缓存
        self.user_cache = UserNameCache()
        self.conver_cache = ConversationCache()

        # 4. 创建 Provider
        self.user_provider = NapCatUserProvider(self.adapter.api)

        # 5. 创建 Resolver
        self.user_resolver = UserNameResolver(
            self.user_cache,
            self.user_provider,
        )
        self.conver_resolver = ConversationResolver(
            self.conver_cache,
        )

        # 6. 创建事件消费者
        self.chat_consumer = AsyncConsumer(self.on_chat_ui)
        self.poke_consumer = AsyncConsumer(self.on_poke)
        self.message_consumer = AsyncConsumer(self.on_message)

        # 7. 订阅事件
        for kind in ("chat.message", "chat.poke", "chat.recall"):
            self.dispatcher.subscribe(kind, self.chat_consumer.receive)

        self.dispatcher.subscribe("chat.poke", self.poke_consumer.receive)

        self.dispatcher.subscribe("chat.message", self.message_consumer.receive)

        # 8. 注册 ActionRouter
        self.action_router = ActionRouter()

        self.action_router.register(
            adapter_id=self.adapter.adapter_id,
            provider=self.adapter.message_provider,
        )

    async def on_chat_ui(self, envelope: EventEnvelope) -> None:
        event = envelope.event
        await self.user_resolver.fetch_missing(event)

        resolved = self.user_resolver.resolve(event)
        resolved = self.conver_resolver.resolve(resolved)

        logger.info(format_chat_event(resolved))

    async def on_poke(self, envelope: EventEnvelope) -> None:
        event = envelope.event
        if event["kind"] != "chat.poke":
            return

        if event["payload"]["target_id"] != event["account_id"]:
            return

        user_id = event["actor_id"]

        if user_id is None or user_id == event["account_id"]:
            return

        if event["conversation_type"] == "group":
            await self.adapter.api.message.send_poke(
                group_id=event["conversation_id"],
                user_id=user_id,
            )

        elif event["conversation_type"] == "private":
            await self.adapter.api.message.send_poke(user_id=user_id)

    async def on_message(self, envelope: EventEnvelope) -> None:
        event = envelope.event
        if event["kind"] != "chat.message":
            return

        if event["actor_id"] == event["account_id"]:
            return

        text = "".join(
            segment["text"]
            for segment in event["payload"]["segments"]
            if segment["type"] == "text"
        )

        if "lunia" not in text.lower():
            return

        if envelope.adapter_id is None:
            return

        action = SendMessage(
            adapter_id=envelope.adapter_id,
            conversation_type=event["conversation_type"],
            conversation_id=event["conversation_id"],
            content="检测到关键词",
        )
        await self.action_router.execute(action)

    async def run(self) -> None:
        try:
            await self.bus.start()

            self.chat_consumer.start()
            self.poke_consumer.start()
            self.message_consumer.start()

            await self.adapter.start()
            await self.adapter.run()
        finally:
            await self.bus.stop()
            await asyncio.gather(
                self.chat_consumer.stop(),
                self.poke_consumer.stop(),
                self.message_consumer.stop(),
            )


async def main() -> None:
    setup_logging()
    runtime = Runtime()
    await runtime.run()


if __name__ == "__main__":
    asyncio.run(main())

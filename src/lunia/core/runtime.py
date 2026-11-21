import asyncio
import os

from lunia.adapters.napcat.adapter import NapCatAdapter
from lunia.adapters.napcat.provider import NapCatUserProvider
from lunia.core.actions.router import ActionRouter
from lunia.core.cache import ConversationCache, UserNameCache
from lunia.core.events.bus import EventBus
from lunia.core.events.consumer import AsyncConsumer
from lunia.core.events.dispatcher import EventDispatcher
from lunia.core.events.models import EventEnvelope
from lunia.core.logging import get_logger, setup_logging
from lunia.demo.chat import ChatDemo
from lunia.formatters.ui import format_chat_event
from lunia.llm.config import ModelConfig, ProviderConfig
from lunia.llm.manager import LLMManager
from lunia.resolvers.conversation import ConversationResolver
from lunia.resolvers.username import UserNameResolver

logger = get_logger("lunia.core.runtime")


class Runtime:
    def __init__(self) -> None:
        # 创建事件分发
        self.dispatcher = EventDispatcher()
        self.bus = EventBus(self.dispatcher)

        # 创建 NapCat 事件适配器与连接
        self.adapter = NapCatAdapter(
            adapter_id="main",
            bus=self.bus,
            url="ws://127.0.0.1:3799",
            token=os.environ["NAPCAT_TOKEN"],
        )

        # 创建缓存
        self.user_cache = UserNameCache()
        self.conver_cache = ConversationCache()

        # 创建 Provider
        self.user_provider = NapCatUserProvider(self.adapter.api)

        # 创建 Resolver
        self.user_resolver = UserNameResolver(
            self.user_cache,
            self.user_provider,
        )
        self.conver_resolver = ConversationResolver(
            self.conver_cache,
        )

        # 注册 ActionRouter
        self.action_router = ActionRouter()

        self.action_router.register(
            adapter_id=self.adapter.adapter_id,
            provider=self.adapter.message_provider,
        )

        # 注册 LLMManager
        self.llm = LLMManager(
            providers={
                "deepseek": ProviderConfig(
                    base_url="https://api.deepseek.com",
                    api_key=os.environ["DEEPSEEK_API_KEY"],
                ),
            },
            models={
                "chat": ModelConfig(
                    provider="deepseek",
                    model_id="deepseek-flash",
                ),
            },
        )

        # 创建事件消费者
        self.chat_consumer = AsyncConsumer(self.on_chat_ui)
        self.poke_consumer = AsyncConsumer(self.on_poke)
        self.chat_demo = ChatDemo(llm=self.llm, actions=self.action_router)
        self.message_consumer = AsyncConsumer(self.chat_demo.handle)

        # 订阅事件
        for kind in ("chat.message", "chat.poke", "chat.recall"):
            self.dispatcher.subscribe(kind, self.chat_consumer.receive)

        self.dispatcher.subscribe("chat.poke", self.poke_consumer.receive)

        self.dispatcher.subscribe("chat.message", self.message_consumer.receive)

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

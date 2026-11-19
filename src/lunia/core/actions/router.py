from typing import Any, Protocol

from lunia.core.events.models import ConversationType

from .models import SendMessage


class MessageProvider(Protocol):
    """提供统一的消息发送能力。"""

    async def send_message(
        self,
        conversation_type: ConversationType,
        conversation_id: str,
        content: str,
    ) -> dict[str, Any]: ...


class ActionRouter:
    """根据 Adapter 实例标识路由行动。"""

    def __init__(self) -> None:
        self._providers: dict[str, MessageProvider] = {}

    def register(
        self,
        adapter_id: str,
        provider: MessageProvider,
    ) -> None:
        """注册某个 Adapter 实例的消息能力。"""
        if adapter_id in self._providers:
            raise ValueError(f"Adapter 已注册: {adapter_id}")

        self._providers[adapter_id] = provider

    def unregister(self, adapter_id: str) -> None:
        """移除已注册的消息能力。"""
        self._providers.pop(adapter_id, None)

    async def execute(
        self,
        action: SendMessage,
    ) -> dict[str, Any]:
        """执行消息发送行动。"""
        provider = self._providers.get(action.adapter_id)

        if provider is None:
            raise LookupError(f"未找到 Adapter: {action.adapter_id}")

        return await provider.send_message(
            conversation_type=action.conversation_type,
            conversation_id=action.conversation_id,
            content=action.content,
        )

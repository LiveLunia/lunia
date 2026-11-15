from typing import Protocol

from lunia.core.cache import UserNameCache
from lunia.core.events import ChatEvent, ConversationType, Platform


def make_user_name_key(
    event: ChatEvent,
    user_id: str | None,
) -> tuple[Platform, str, ConversationType, str, str] | None:
    """从聊天事件中提取用户名称缓存键。"""

    if user_id is None:
        return None

    return (
        event["platform"],
        event["account_id"],
        event["conversation_type"],
        event["conversation_id"],
        user_id,
    )


class UserInfoProvider(Protocol):
    """提供用户信息的接口"""

    async def get_user_name(
        self,
        conversation_type: ConversationType,
        conversation_id: str,
        user_id: str,
    ) -> tuple[str | None, str | None] | None:
        """获取指定用户的名称信息"""


class UserNameResolver:
    """补全聊天事件中的显示名称"""

    def __init__(
        self,
        cache: UserNameCache,
        provider: UserInfoProvider,
    ) -> None:
        self._cache = cache
        self._provider = provider

    async def fetch_missing(self, event: ChatEvent) -> None:
        """使用 Provider 查询缺失的用户昵称并更新缓存."""
        user_id = event["actor_id"]
        if user_id is None:
            return

        key = make_user_name_key(event, user_id)
        if key is None:
            return

        names = self._cache.get(key)
        if (
            names is not None
            and names["nickname"] is not None
            and names["alias"] is not None
        ):
            return

        result = await self._provider.get_user_name(
            conversation_type=event["conversation_type"],
            conversation_id=event["conversation_id"],
            user_id=user_id,
        )
        if result is None:
            return

        current = self._cache.get(key)

        nickname, alias = result
        nickname = nickname or None
        alias = alias or None

        self._cache.update(
            key,
            nickname=(
                nickname if current is None or current["nickname"] is None else None
            ),
            alias=(alias if current is None or current["alias"] is None else None),
        )

    def _get_names(
        self,
        event: ChatEvent,
        user_id: str | None,
    ):
        """根据事件上下文查询指定用户的名称缓存。"""
        if user_id is None:
            return None

        key = make_user_name_key(event, user_id)
        if key is None:
            return None

        return self._cache.get(key)

    def resolve(self, event: ChatEvent) -> ChatEvent:
        """补全事件涉及用户的名称，返回事件副本。"""
        resolved = event.copy()

        # 1. 优先处理 Actor，学习当前事件提供的名称
        actor_id = event["actor_id"]

        if actor_id is not None:
            actor_key = make_user_name_key(event, actor_id)
            if actor_key is None:
                return resolved
            self._cache.update(
                actor_key,
                nickname=event["actor_name"],
                alias=event["actor_alias"],
            )

            actor_names = self._cache.get(actor_key)

            if actor_names is not None:
                resolved["actor_name"] = actor_names["nickname"]
                resolved["actor_alias"] = actor_names["alias"]

        # 2. 补全 Poke Target
        if event["kind"] == "chat.poke":
            poke_event = event.copy()
            payload = event["payload"].copy()

            target_names = self._get_names(
                event,
                payload["target_id"],
            )

            if target_names is not None:
                payload["target_name"] = target_names["nickname"]
                payload["target_alias"] = target_names["alias"]

            poke_event["actor_name"] = resolved["actor_name"]
            poke_event["actor_alias"] = resolved["actor_alias"]
            poke_event["payload"] = payload

            return poke_event

        # 3. 补全 Recall Sender
        if event["kind"] == "chat.recall":
            recall_event = event.copy()
            payload = event["payload"].copy()

            sender_names = self._get_names(
                event,
                payload["sender_id"],
            )

            if sender_names is not None:
                payload["sender_name"] = sender_names["nickname"]
                payload["sender_alias"] = sender_names["alias"]

            recall_event["actor_name"] = resolved["actor_name"]
            recall_event["actor_alias"] = resolved["actor_alias"]
            recall_event["payload"] = payload

            return recall_event

        return resolved

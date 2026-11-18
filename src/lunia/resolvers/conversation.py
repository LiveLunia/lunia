from lunia.core.cache import ConversationCache
from lunia.core.events.models import ChatEvent


class ConversationResolver:
    """补全聊天事件中的会话名称"""

    def __init__(self, cache: ConversationCache) -> None:
        self._cache = cache

    def resolve(self, event: ChatEvent) -> ChatEvent:
        """补全会话名称，返回事件副本。"""
        resolved = event.copy()
        key = (
            event["platform"],
            event["account_id"],
            event["conversation_type"],
            event["conversation_id"],
        )
        name = event["conversation_name"]

        if name is not None:
            self._cache.update(key, name)
        else:
            resolved["conversation_name"] = self._cache.get(key)

        return resolved

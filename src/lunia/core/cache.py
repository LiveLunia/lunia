from typing import TypedDict

from lunia.core.events import ConversationType, Platform

type _UserNameKey = tuple[
    Platform,
    str,  # account_id
    ConversationType,
    str,  # conversation_id
    str,  # user_id
]


class _UserNameEntry(TypedDict):
    nickname: str | None
    alias: str | None


class UserNameCache:
    """Lunia 的临时显示名称缓存"""

    def __init__(self) -> None:
        self._names: dict[_UserNameKey, _UserNameEntry] = {}

    def get(self, key: _UserNameKey) -> _UserNameEntry | None:
        """读取缓存中的名称资料"""
        entry = self._names.get(key)

        if entry is None:
            return None

        return entry.copy()

    def update(
        self,
        key: _UserNameKey,
        *,
        nickname: str | None = None,
        alias: str | None = None,
    ) -> None:
        """更新缓存"""
        if nickname is None and alias is None:
            return

        entry = self._names.setdefault(
            key,
            {"nickname": None, "alias": None},
        )

        if nickname is not None:
            entry["nickname"] = nickname or None

        if alias is not None:
            entry["alias"] = alias or None


type _ConversationKey = tuple[
    Platform,
    str,  # account_id
    ConversationType,
    str,  # conversation_id
]


class ConversationCache:
    """Lunia 的临时会话名称缓存"""

    def __init__(self) -> None:
        self._names: dict[_ConversationKey, str] = {}

    def get(self, key: _ConversationKey) -> str | None:
        """读取缓存中的会话名称"""
        return self._names.get(key)

    def update(
        self,
        key: _ConversationKey,
        name: str | None,
    ) -> None:
        """更新缓存"""
        if name is None or key[2] == "private":
            return

        self._names[key] = name

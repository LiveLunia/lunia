"""NapCat 消息接口与消息扩展；分类不表示 OneBot 11 标准归属。"""

from typing import Any, Literal

from lunia.adapters.napcat.client import NapCatClient


class MessageAPI:
    """消息接口与消息扩展，复用传入的 Client。"""

    def __init__(self, client: NapCatClient) -> None:
        self.client = client

    async def send_group_msg(
        self,
        group_id: str,
        message: str | list[dict[str, Any]],
        *,
        auto_escape: bool | str | None = None,
        source: str | None = None,
        news: list[dict[str, str]] | None = None,
        summary: str | None = None,
        prompt: str | None = None,
        send_timeout_ms: int | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """发送群聊消息。

        Args:
            group_id: 群号。
            message: 消息字符串或消息段数组。
            auto_escape: 是否将消息作为纯文本发送。
            source: 合并转发来源。
            news: 合并转发预览条目，每项包含字符串 text。
            summary: 合并转发摘要。
            prompt: 合并转发提示。
            send_timeout_ms: NapCat 服务端发送超时，单位毫秒；未指定时省略。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
            "message": message,
        }
        if auto_escape is not None:
            params["auto_escape"] = auto_escape
        if source is not None:
            params["source"] = source
        if news is not None:
            params["news"] = news
        if summary is not None:
            params["summary"] = summary
        if prompt is not None:
            params["prompt"] = prompt
        if send_timeout_ms is not None:
            params["timeout"] = send_timeout_ms
        return await self.client.call_api("send_group_msg", params, timeout=timeout)

    async def get_group_msg_history(
        self,
        group_id: str,
        *,
        message_seq: str | None = None,
        count: int = 20,
        reverse_order: bool = False,
        disable_get_url: bool = False,
        parse_mult_msg: bool = True,
        quick_reply: bool = False,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取群聊历史消息。

        Args:
            group_id: 群号。
            message_seq: 起始消息序号。
            count: 获取的数量。
            reverse_order: 是否反向排序。
            disable_get_url: 是否禁用获取 URL。
            parse_mult_msg: 是否解析合并消息。
            quick_reply: 是否快速回复。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
            "count": count,
            "reverse_order": reverse_order,
            "disable_get_url": disable_get_url,
            "parse_mult_msg": parse_mult_msg,
            "quick_reply": quick_reply,
            "reverseOrder": reverse_order,
        }
        if message_seq is not None:
            params["message_seq"] = message_seq
        return await self.client.call_api(
            "get_group_msg_history", params, timeout=timeout
        )

    async def get_forward_msg(
        self,
        *,
        message_id: str | None = None,
        id: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取合并转发消息内容。

        Args:
            message_id: 合并转发消息 ID，与 id 至少提供一项。
            id: 合并转发消息 ID。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        if message_id is None and id is None:
            raise ValueError("message_id 和 id 至少提供一项")
        params: dict[str, Any] = {}
        if message_id is not None:
            params["message_id"] = message_id
        if id is not None:
            params["id"] = id
        return await self.client.call_api("get_forward_msg", params, timeout=timeout)

    async def get_friend_msg_history(
        self,
        user_id: str,
        *,
        message_seq: str | None = None,
        count: int = 20,
        reverse_order: bool = False,
        disable_get_url: bool = False,
        parse_mult_msg: bool = True,
        quick_reply: bool = False,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取好友历史消息。

        Args:
            user_id: 用户 QQ 号。
            message_seq: 起始消息序号。
            count: 获取的数量。
            reverse_order: 是否反向排序。
            disable_get_url: 是否禁用获取 URL。
            parse_mult_msg: 是否解析合并消息。
            quick_reply: 是否快速回复。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "user_id": user_id,
            "count": count,
            "reverse_order": reverse_order,
            "disable_get_url": disable_get_url,
            "parse_mult_msg": parse_mult_msg,
            "quick_reply": quick_reply,
            "reverseOrder": reverse_order,
        }
        if message_seq is not None:
            params["message_seq"] = message_seq
        return await self.client.call_api(
            "get_friend_msg_history", params, timeout=timeout
        )

    async def forward_friend_single_msg(
        self,
        message_id: int | str,
        *,
        group_id: str | None = None,
        user_id: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """转发单条消息。

        Args:
            message_id: 消息ID。
            group_id: 目标群号。
            user_id: 目标用户QQ。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "message_id": message_id,
        }
        if group_id is not None:
            params["group_id"] = group_id
        if user_id is not None:
            params["user_id"] = user_id
        return await self.client.call_api(
            "forward_friend_single_msg", params, timeout=timeout
        )

    async def forward_group_single_msg(
        self,
        message_id: int | str,
        *,
        group_id: str | None = None,
        user_id: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """转发单条消息。

        Args:
            message_id: 消息ID。
            group_id: 目标群号。
            user_id: 目标用户QQ。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "message_id": message_id,
        }
        if group_id is not None:
            params["group_id"] = group_id
        if user_id is not None:
            params["user_id"] = user_id
        return await self.client.call_api(
            "forward_group_single_msg", params, timeout=timeout
        )

    async def mark_group_msg_as_read(
        self,
        group_id: str,
        *,
        user_id: str | int | None = None,
        message_id: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """标记群聊消息为已读。

        Args:
            group_id: 群号。
            user_id: 用户 QQ 号。
            message_id: 消息 ID。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
        }
        if user_id is not None:
            params["user_id"] = user_id
        if message_id is not None:
            params["message_id"] = message_id
        return await self.client.call_api(
            "mark_group_msg_as_read", params, timeout=timeout
        )

    async def mark_private_msg_as_read(
        self,
        user_id: str | int,
        *,
        group_id: str | None = None,
        message_id: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """标记私聊消息为已读。

        Args:
            user_id: 用户 QQ 号。
            group_id: 群号。
            message_id: 消息 ID。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "user_id": user_id,
        }
        if group_id is not None:
            params["group_id"] = group_id
        if message_id is not None:
            params["message_id"] = message_id
        return await self.client.call_api(
            "mark_private_msg_as_read", params, timeout=timeout
        )

    async def get_msg(
        self,
        message_id: int | str,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """根据消息 ID 获取消息详情。

        Args:
            message_id: 消息 ID。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "message_id": message_id,
        }
        return await self.client.call_api("get_msg", params, timeout=timeout)

    async def send_private_msg(
        self,
        user_id: str,
        message: str | list[dict[str, Any]],
        timeout: float | None = 10.0,
        *,
        group_id: str | None = None,
        auto_escape: bool | str | None = None,
        source: str | None = None,
        news: list[dict[str, str]] | None = None,
        summary: str | None = None,
        prompt: str | None = None,
        send_timeout_ms: int | None = None,
    ) -> dict[str, Any]:
        """发送私聊消息。

        Args:
            user_id: 用户 QQ 号。
            message: 消息字符串或消息段数组。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
            group_id: 群号。
            auto_escape: 是否将消息作为纯文本发送。
            source: 合并转发来源。
            news: 合并转发预览条目，每项包含字符串 text。
            summary: 合并转发摘要。
            prompt: 合并转发提示。
            send_timeout_ms: NapCat 服务端发送超时，单位毫秒；未指定时省略。
        """
        params: dict[str, Any] = {
            "user_id": user_id,
            "message": message,
        }
        if group_id is not None:
            params["group_id"] = group_id
        if auto_escape is not None:
            params["auto_escape"] = auto_escape
        if source is not None:
            params["source"] = source
        if news is not None:
            params["news"] = news
        if summary is not None:
            params["summary"] = summary
        if prompt is not None:
            params["prompt"] = prompt
        if send_timeout_ms is not None:
            params["timeout"] = send_timeout_ms
        return await self.client.call_api("send_private_msg", params, timeout=timeout)

    async def send_msg(
        self,
        message_type: Literal["private", "group"],
        message: str | list[dict[str, Any]],
        *,
        user_id: str | None = None,
        group_id: str | None = None,
        auto_escape: bool | str | None = None,
        source: str | None = None,
        news: list[dict[str, str]] | None = None,
        summary: str | None = None,
        prompt: str | None = None,
        send_timeout_ms: int | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """按指定类型发送私聊或群聊消息。

        Args:
            message_type: 消息类型，private 或 group。
            message: 消息字符串或消息段数组。
            user_id: 私聊目标 QQ 号，private 类型时必填。
            group_id: 群聊目标群号，group 类型时必填。
            auto_escape: 是否将消息作为纯文本发送。
            source: 合并转发来源。
            news: 合并转发预览条目，每项包含字符串 text。
            summary: 合并转发摘要。
            prompt: 合并转发提示。
            send_timeout_ms: NapCat 服务端发送超时，单位毫秒；未指定时省略。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        if message_type not in ("private", "group"):
            raise ValueError("message_type 必须为 private 或 group")
        if message_type == "private" and user_id is None:
            raise ValueError("私聊消息必须提供 user_id")
        if message_type == "group" and group_id is None:
            raise ValueError("群聊消息必须提供 group_id")
        params: dict[str, Any] = {
            "message_type": message_type,
            "message": message,
        }
        if user_id is not None:
            params["user_id"] = user_id
        if group_id is not None:
            params["group_id"] = group_id
        if auto_escape is not None:
            params["auto_escape"] = auto_escape
        if source is not None:
            params["source"] = source
        if news is not None:
            params["news"] = news
        if summary is not None:
            params["summary"] = summary
        if prompt is not None:
            params["prompt"] = prompt
        if send_timeout_ms is not None:
            params["timeout"] = send_timeout_ms
        return await self.client.call_api("send_msg", params, timeout=timeout)

    async def delete_msg(
        self,
        message_id: int | str,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """撤回已发送的消息。

        Args:
            message_id: 消息 ID。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "message_id": message_id,
        }
        return await self.client.call_api("delete_msg", params, timeout=timeout)

    async def mark_msg_as_read(
        self,
        *,
        user_id: str | int | None = None,
        group_id: str | None = None,
        message_id: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """标记指定渠道的消息为已读。

        Args:
            user_id: 用户 QQ 号。
            group_id: 群号。
            message_id: 消息 ID。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        if message_id is None and group_id is None and user_id is None:
            raise ValueError("至少提供一个消息或渠道定位字段")
        params: dict[str, Any] = {}
        if user_id is not None:
            params["user_id"] = user_id
        if group_id is not None:
            params["group_id"] = group_id
        if message_id is not None:
            params["message_id"] = message_id
        return await self.client.call_api("mark_msg_as_read", params, timeout=timeout)

    async def _mark_all_as_read(
        self,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """标记所有消息已读。"""
        params: dict[str, Any] = {}
        return await self.client.call_api("_mark_all_as_read", params, timeout=timeout)

    async def group_poke(
        self,
        group_id: str,
        user_id: str,
        *,
        target_id: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """在群聊中发送戳一戳。

        Args:
            group_id: 群号。
            user_id: 用户 QQ 号。
            target_id: 戳一戳目标 QQ 号。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
            "user_id": user_id,
        }
        if target_id is not None:
            params["target_id"] = target_id
        return await self.client.call_api("group_poke", params, timeout=timeout)

    async def friend_poke(
        self,
        user_id: str,
        *,
        target_id: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """向好友发送戳一戳。

        Args:
            user_id: 用户 QQ 号。
            target_id: 戳一戳目标 QQ 号。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "user_id": user_id,
        }
        if target_id is not None:
            params["target_id"] = target_id
        return await self.client.call_api("friend_poke", params, timeout=timeout)

    async def send_poke(
        self,
        user_id: str,
        *,
        group_id: str | None = None,
        target_id: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """向指定用户发送戳一戳。

        Args:
            user_id: 用户 QQ 号。
            group_id: 群号。
            target_id: 戳一戳目标 QQ 号。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "user_id": user_id,
        }
        if group_id is not None:
            params["group_id"] = group_id
        if target_id is not None:
            params["target_id"] = target_id
        return await self.client.call_api("send_poke", params, timeout=timeout)

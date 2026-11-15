from typing import Any

from lunia.core.events import (
    ChatEvent,
    ChatEventBase,
    MessageEvent,
    MessageSegment,
    PokeEvent,
    RecallEvent,
)
from lunia.core.logging import get_logger

logger = get_logger(__name__)


def optional_str(value: object) -> str | None:
    if value is None or value == "":
        return None
    return str(value)


def parse_segments(message: list[dict[str, Any]]) -> list[MessageSegment]:
    """将segments转换为MessageSegment"""
    segments: list[MessageSegment] = []

    for item in message:
        segment_type = item.get("type")
        data = item.get("data", {})

        if segment_type == "text":
            segments.append(
                {
                    "type": "text",
                    "text": data.get("text", ""),
                }
            )

        elif segment_type == "at":
            segments.append(
                {
                    "type": "at",
                    "target_id": str(data.get("qq", "")),
                }
            )

        elif segment_type == "reply":
            segments.append(
                {
                    "type": "reply",
                    "message_id": str(data.get("id", "")),
                }
            )

        elif segment_type == "image":
            segments.append(
                {
                    "type": "image",
                    "file": optional_str(data.get("file")),
                    "url": optional_str(data.get("url")),
                }
            )

        elif segment_type == "record":
            segments.append(
                {
                    "type": "record",
                    "file": optional_str(data.get("file")),
                    "url": optional_str(data.get("url")),
                    "path": optional_str(data.get("path")),
                }
            )

        elif segment_type == "video":
            segments.append(
                {
                    "type": "video",
                    "file": optional_str(data.get("file")),
                    "url": optional_str(data.get("url")),
                }
            )

        elif segment_type == "forward":
            segments.append(
                {
                    "type": "forward",
                    "forward_id": str(data.get("id", "")),
                }
            )

        elif segment_type == "json":
            content = data.get("data")

            if isinstance(content, (dict, str)):
                segments.append(
                    {
                        "type": "json",
                        "data": content,
                    }
                )
            else:
                segments.append(
                    {
                        "type": "unknown",
                        "original_type": "json",
                        "data": data,
                    }
                )

        else:
            segments.append(
                {
                    "type": "unknown",
                    "original_type": str(segment_type),
                    "data": data,
                }
            )

    return segments


def parse_base(
    data: dict,
    *,
    actor_id: str | None,
    actor_name: str | None = None,
    actor_alias: str | None = None,
) -> ChatEventBase:
    """将基础字段转换为ChatEventBase"""
    group_id = data.get("group_id")
    is_group = group_id is not None

    return {
        "platform": "qq",
        "account_id": str(data["self_id"]),
        "conversation_type": "group" if is_group else "private",
        "conversation_id": (str(group_id) if is_group else str(data["user_id"])),
        "conversation_name": data.get("group_name") if is_group else None,
        "actor_id": actor_id,
        "actor_name": actor_name,
        "actor_alias": actor_alias,
        "timestamp": data["time"],
    }


def parse_message(data: dict) -> MessageEvent:
    """将message转换为MessageEvent"""
    sender = data.get("sender") or {}
    actor_id = str(data["user_id"])

    group_id = data.get("group_id")
    is_group = group_id is not None

    return {
        **parse_base(
            data,
            actor_id=actor_id,
            actor_name=sender.get("nickname"),
            actor_alias=(sender.get("card") if is_group else sender.get("remark")),
        ),
        "kind": "chat.message",
        "payload": {
            "message_id": str(data["message_id"]),
            "segments": parse_segments(data["message"]),
        },
    }


def parse_poke(data: dict) -> PokeEvent:
    """将poke转换为PokeEvent"""
    texts = [
        item.get("txt", "")
        for item in (data.get("raw_info") or [])
        if isinstance(item, dict) and item.get("type") == "nor"
    ]

    return {
        **parse_base(
            data,
            actor_id=str(data["user_id"]),
        ),
        "kind": "chat.poke",
        "payload": {
            "target_id": str(data["target_id"]),
            "target_name": None,
            "target_alias": None,
            "action_text": texts[0] if texts else "戳了戳",
            "suffix_text": "".join(texts[1:]),
        },
    }


def parse_recall(data: dict) -> RecallEvent:
    """将recall转换为RecallEvent"""
    is_group = data["notice_type"] == "group_recall"
    sender_id = str(data["user_id"])
    actor_id = str(data["operator_id"]) if is_group else sender_id

    return {
        **parse_base(
            data,
            actor_id=actor_id,
        ),
        "kind": "chat.recall",
        "payload": {
            "message_id": str(data["message_id"]),
            "sender_id": sender_id,
            "sender_name": None,
            "sender_alias": None,
        },
    }


def parse_chat(data: dict) -> ChatEvent | None:
    """聊天事件格式化"""

    post_type = data.get("post_type")
    notice_type = data.get("notice_type")

    if post_type == "message":
        return parse_message(data)
    if post_type == "notice":
        if notice_type == "notify" and data.get("sub_type") == "poke":
            return parse_poke(data)
        if notice_type in ("group_recall", "friend_recall"):
            return parse_recall(data)

    return None

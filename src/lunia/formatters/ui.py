from lunia.core.events import ChatEvent, MessageSegment


def format_segments(segments: list[MessageSegment]) -> str:
    """转换消息段"""

    parts: list[str] = []
    prev_type = ""

    for segment in segments:
        if segment["type"] == "text":
            text = segment["text"]
            if prev_type == "at" and text.startswith(" "):
                text = text[1:]
            parts.append(text)
        elif segment["type"] == "at":
            target = segment["target_id"]
            name = "全体成员" if target == "all" else target
            parts.append(f"@{name} ")
        elif segment["type"] == "reply":
            parts.append(f"\n↳ [引用消息 {segment['message_id']}]\n")
        elif segment["type"] == "image":
            parts.append("[图片]")
        elif segment["type"] == "record":
            parts.append("[语音]")
        elif segment["type"] == "video":
            parts.append("[视频]")
        elif segment["type"] == "forward":
            parts.append("[合并转发]")
        elif segment["type"] == "json":
            parts.append("[JSON卡片]")
        else:
            parts.append(f"[{segment['original_type']}]")

        prev_type = segment["type"]

    return "".join(parts)


def format_display_name(
    user_id: str | None,
    nickname: str | None,
    alias: str | None,
) -> str:
    """处理显示昵称"""
    if alias:
        if nickname and nickname != alias:
            return f"({nickname}){alias}"
        return alias

    return nickname or f"({user_id})未知用户"


def format_conversation_name(
    conversation_id: str | None,
    conversation_name: str | None,
) -> str:
    """处理会话名称"""
    return conversation_name or f"({conversation_id})未知会话"


def format_chat_event(event: ChatEvent) -> str:
    """转换聊天字段为可读UI文本"""
    actor = (
        "你"
        if event["account_id"] == event["actor_id"]
        else format_display_name(
            event["actor_id"],
            event["actor_name"],
            event["actor_alias"],
        )
    )

    if event["conversation_type"] == "group":
        group_name = format_conversation_name(
            event["conversation_id"],
            event["conversation_name"],
        )
        location = f"[群聊 | {group_name}]"
    else:
        location = "[私聊]"

    if event["kind"] == "chat.message":
        content = format_segments(event["payload"]["segments"])
        return f"{location} <- {actor}: {content}"
    elif event["kind"] == "chat.poke":
        payload = event["payload"]
        target_id = payload["target_id"]
        target = (
            "自己"
            if target_id == event["actor_id"]
            else "你"
            if target_id == event["account_id"]
            else format_display_name(
                target_id,
                payload["target_name"],
                payload["target_alias"],
            )
        )
        return (
            f"{location} <- {actor}{payload['action_text']}"
            f"{target}{payload['suffix_text']}"
        )
    elif event["kind"] == "chat.recall":
        payload = event["payload"]
        sender = format_display_name(
            payload["sender_id"],
            payload["sender_name"],
            payload["sender_alias"],
        )
        if event["actor_id"] == payload["sender_id"]:
            return f"{location} <- {actor}撤回了一条消息"
        return f"{location} <- {actor}撤回了{sender}的消息"
    else:
        return ""

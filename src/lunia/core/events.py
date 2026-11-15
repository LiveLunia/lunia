from typing import Literal, TypedDict

Platform = Literal["qq", "wechat", "telegram", "discord", "web", "cli"]
ConversationType = Literal["private", "group", "channel"]


class TextSegment(TypedDict):
    type: Literal["text"]
    text: str


class AtSegment(TypedDict):
    type: Literal["at"]
    target_id: str


class ReplySegment(TypedDict):
    type: Literal["reply"]
    message_id: str


class ImageSegment(TypedDict):
    type: Literal["image"]
    file: str | None
    url: str | None


class RecordSegment(TypedDict):
    type: Literal["record"]
    file: str | None
    url: str | None
    path: str | None


class VideoSegment(TypedDict):
    type: Literal["video"]
    file: str | None
    url: str | None


class ForwardSegment(TypedDict):
    type: Literal["forward"]
    forward_id: str


class JsonSegment(TypedDict):
    type: Literal["json"]
    data: str | dict[str, object]


class UnknownSegment(TypedDict):
    type: Literal["unknown"]
    original_type: str
    data: dict[str, object]


type MessageSegment = (
    TextSegment
    | AtSegment
    | ReplySegment
    | ImageSegment
    | RecordSegment
    | VideoSegment
    | ForwardSegment
    | JsonSegment
    | UnknownSegment
)


class MessagePayload(TypedDict):
    """消息字段"""

    message_id: str
    segments: list[MessageSegment]


class PokePayload(TypedDict):
    """戳一戳字段"""

    target_id: str
    target_name: str | None
    target_alias: str | None
    action_text: str
    suffix_text: str


class RecallPayload(TypedDict):
    """撤回字段"""

    message_id: str
    sender_id: str | None
    sender_name: str | None
    sender_alias: str | None


class ChatEventBase(TypedDict):
    """基本聊天事件"""

    platform: Platform
    account_id: str
    conversation_type: ConversationType
    conversation_id: str
    conversation_name: str | None
    actor_id: str | None
    actor_name: str | None
    actor_alias: str | None
    timestamp: int


class MessageEvent(ChatEventBase):
    """消息事件"""

    kind: Literal["chat.message"]
    payload: MessagePayload


class PokeEvent(ChatEventBase):
    """戳一戳事件"""

    kind: Literal["chat.poke"]
    payload: PokePayload


class RecallEvent(ChatEventBase):
    """撤回事件"""

    kind: Literal["chat.recall"]
    payload: RecallPayload


type ChatEvent = MessageEvent | PokeEvent | RecallEvent

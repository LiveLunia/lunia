from dataclasses import dataclass

from lunia.core.events.models import ConversationType


@dataclass(frozen=True, slots=True)
class SendMessage:
    adapter_id: str
    conversation_type: ConversationType
    conversation_id: str
    content: str

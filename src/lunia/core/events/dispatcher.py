from collections.abc import Callable
from typing import Any

from ..logging import get_logger

logger = get_logger(__name__)

type EventReceiver = Callable[[Any], None]


class EventDispatcher:
    """Lunia 内部事件分发器."""

    def __init__(self) -> None:
        self._receivers: dict[str, list[EventReceiver]] = {}

    def subscribe(self, event_type: str, receiver: EventReceiver) -> None:
        """订阅指定事件."""
        receivers = self._receivers.setdefault(event_type, [])

        if receiver not in receivers:
            receivers.append(receiver)

    def unsubscribe(self, event_type: str, receiver: EventReceiver) -> None:
        """取消订阅指定事件."""
        receivers = self._receivers.get(event_type)

        if receivers is None:
            return

        if receiver in receivers:
            receivers.remove(receiver)

        if not receivers:
            del self._receivers[event_type]

    def dispatch(self, event_type: str, event: Any) -> None:
        """投递事件给所有订阅者."""

        receivers = tuple(self._receivers.get(event_type, []))

        for receiver in receivers:
            try:
                receiver(event)
            except Exception:
                logger.exception(
                    "事件投递失败: event_type=%s",
                    event_type,
                )

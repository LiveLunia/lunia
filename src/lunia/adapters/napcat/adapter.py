import json
from typing import Any

from lunia.adapters.napcat.parser import parse_chat
from lunia.core.events.bus import EventBus
from lunia.core.logging import get_logger

logger = get_logger(__name__)


class NapCatAdapter:
    """解析 NapCat 原始上报，并将事件投递到 Lunia 事件总线"""

    def __init__(self, bus: EventBus) -> None:
        self._bus = bus

    def on_event(self, data: dict[str, Any]) -> None:
        """同步解析上报并将聊天事件入队。"""
        try:
            event = parse_chat(data)
        except Exception:
            # 隔离单条外部上报的解析失败，发布异常由调用方处理。
            logger.exception(
                "NapCat 上报解析失败，已跳过: post_type=%s, notice_type=%s",
                data.get("post_type"),
                data.get("notice_type"),
            )
            return

        if event is None:
            return

        if event["kind"] == "chat.message":
            for segment in event["payload"]["segments"]:
                if segment["type"] == "unknown":
                    logger.debug("未知消息类型: %s", segment["original_type"])
        logger.debug(
            "Lunia 解析结果:\n%s",
            json.dumps(event, ensure_ascii=False, indent=2),
        )
        self._bus.publish(event["kind"], event)

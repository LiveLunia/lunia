import json
from typing import Any

from lunia.adapters.napcat.parser import parse_chat
from lunia.core.dispatcher import EventDispatcher
from lunia.core.logging import get_logger

logger = get_logger(__name__)


class NapCatAdapter:
    """解析 NapCat 原始上报，并将聊天事件投递到现有分发器。"""

    def __init__(self, dispatcher: EventDispatcher) -> None:
        self._dispatcher = dispatcher

    def on_event(self, data: dict[str, Any]) -> None:
        """同步解析与投递，不在接收循环中等待消费者或平台查询。"""
        try:
            event = parse_chat(data)
        except Exception:
            # 单条外部上报的解析失败不能中断连接；分发错误不在此捕获。
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
        self._dispatcher.dispatch(event["kind"], event)

import asyncio
import json
from typing import Any

from lunia.core.events.bus import EventBus
from lunia.core.events.models import EventEnvelope
from lunia.core.logging import get_logger

from .api import NapCatAPI
from .client import NapCatClient
from .parser import parse_chat

logger = get_logger(__name__)


class NapCatAdapter:
    """解析事件并上报至 Lunia 事件总线, 管理 Client 生命周期"""

    def __init__(
        self,
        adapter_id: str,
        bus: EventBus,
        url: str,
        token: str,
    ) -> None:
        self.adapter_id = adapter_id
        self._bus = bus
        self.client = NapCatClient(
            url,
            token,
            on_event=self.on_event,
        )
        self.api = NapCatAPI(
            client=self.client,
        )
        self._task: asyncio.Task[None] | None = None

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

        envelope = EventEnvelope(
            adapter_id=self.adapter_id,
            event=event,
        )

        accepted = self._bus.publish(event["kind"], envelope)
        if not accepted:
            logger.debug(
                "NapCat 事件未被 EventBus 接收: %s",
                event["kind"],
            )

    async def start(self) -> None:
        if self._task is not None:
            raise RuntimeError("NapCatAdapter 已启动")

        self._task = asyncio.create_task(
            self.client.run(),
            name=f"napcat-{self.adapter_id}",
        )

    async def run(self) -> None:
        if self._task is None:
            raise RuntimeError("NapCatAdapter 尚未启动")

        await self._task

    async def stop(self) -> None:
        if self._task is None:
            return

        task = self._task
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass
        finally:
            self._task = None

import asyncio
import json
from collections.abc import Awaitable, Callable
from typing import Any
from uuid import uuid4

import websockets

from lunia.adapters.napcat.parser import parse_chat
from lunia.core.events import ChatEvent
from lunia.core.logging import get_logger

logger = get_logger(__name__)
type ChatEventHandler = Callable[[ChatEvent], Awaitable[None]]


class NapCatClient:
    def __init__(
        self,
        url: str,
        token: str,
        on_event: ChatEventHandler | None = None,
    ):
        self.url = url
        self.token = token
        self.ws = None
        self.pending: dict[str, asyncio.Future[dict[str, Any]]] = {}
        self._on_event = on_event

    async def connect(self):
        """建立与 NapCat 的 ws 连接."""
        self.ws = await websockets.connect(
            self.url,
            additional_headers={"Authorization": f"Bearer {self.token}"},
        )
        logger.info("NapCat WebSocket 连接成功.")

    async def call_api(
        self,
        action: str,
        params: dict[str, Any],
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """发送 OneBot API 请求并等待对应响应.

        Args:
            action: OneBot API 动作名称.
            params: API 请求参数.
            timeout: 等待响应的超时时间，单位为秒.

        Returns:
            NapCat 返回的完整 API 响应.

        Raises:
            ConnectionError: ws 连接尚未建立.
            TimeoutError: 在指定时间内未收到响应.
        """
        if self.ws is None:
            raise ConnectionError("NapCat 尚未连接")

        echo = "Lunia-" + uuid4().hex
        future = asyncio.get_running_loop().create_future()
        self.pending[echo] = future
        request = {
            "action": action,
            "params": params,
            "echo": echo,
        }
        try:
            await self.ws.send(json.dumps(request))
            result = await asyncio.wait_for(future, timeout)
            return result

        except TimeoutError:
            logger.warning(
                "NapCat API 请求超时: action=%s, timeout=%0.1fs",
                action,
                timeout,
            )
            raise

        finally:
            self.pending.pop(str(echo), None)

    def _fail_pending(self) -> None:
        """连接断开时终止所有未完成的 API 请求."""
        pending = self.pending
        self.pending = {}

        for future in pending.values():
            if not future.done():
                future.set_exception(ConnectionError("NapCat 连接中断"))

    async def _handle_message(self, data: dict[str, Any]) -> None:
        """处理接收到的 OneBot 数据."""
        if data.get("echo") is not None:
            echo = data["echo"]
            future = self.pending.pop(str(echo), None)
            if future is not None and not future.done():
                future.set_result(data)
        else:
            # if data.get("post_type") != "meta_event":
            #     logger.debug(
            #         "NapCat 原始事件:\n%s",
            #         json.dumps(data, ensure_ascii=False, indent=2),
            #     )
            event = parse_chat(data)
            if event is not None:
                if event["kind"] == "chat.message":
                    for segment in event["payload"]["segments"]:
                        if segment["type"] == "unknown":
                            logger.debug("未知消息类型: %s", segment["original_type"])
                logger.debug(
                    "Lunia 解析结果:\n%s",
                    json.dumps(event, ensure_ascii=False, indent=2),
                )
                if self._on_event is not None:
                    await self._on_event(event)

    async def _receive_loop(self) -> None:
        """持续接收 ws 消息并进行内部事件分发."""
        if self.ws is not None:
            async for message in self.ws:
                try:
                    data = json.loads(message)
                except (json.JSONDecodeError, TypeError) as exc:
                    logger.warning("非法JSON数据, 已跳过: %s", exc)
                    continue

                if isinstance(data, dict):
                    await self._handle_message(data)

    async def run(self):
        """维持 NapCat 连接与中断重连."""
        while True:
            try:
                await self.connect()
                await self._receive_loop()

            except (
                OSError,
                ConnectionError,
                websockets.exceptions.ConnectionClosedError,
                websockets.exceptions.InvalidHandshake,
                TimeoutError,
            ) as exc:
                logger.warning("NapCat 连接异常, 即将重连: %s", exc)

            finally:
                self._fail_pending()
                if self.ws is not None:
                    ws = self.ws
                    self.ws = None
                    await ws.close()

            await asyncio.sleep(3)

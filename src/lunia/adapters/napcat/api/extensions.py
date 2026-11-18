"""NapCat 其他扩展接口"""

from typing import Any

from lunia.adapters.napcat.client import NapCatClient


class ExtensionsAPI:
    """其他扩展接口"""

    def __init__(self, client: NapCatClient) -> None:
        self.client = client

    async def ocr_image(
        self,
        image: str,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """识别图片中的文字。

        Args:
            image: 图片路径、URL 或 Base64。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "image": image,
        }
        return await self.client.call_api("ocr_image", params, timeout=timeout)

    async def handle_quick_operation(
        self,
        context: dict[str, Any],
        operation: dict[str, Any],
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """处理快速操作。

        Args:
            context: 原始事件上下文，需含 time、self_id、post_type、user_id。
            operation: 快速操作内容，可发送消息、撤回、踢人或禁言。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "context": context,
            "operation": operation,
        }
        return await self.client.call_api(
            ".handle_quick_operation", params, timeout=timeout
        )

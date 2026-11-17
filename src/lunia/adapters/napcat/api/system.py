"""NapCat 系统接口与系统扩展；分类不表示 OneBot 11 标准归属。"""

from typing import Any

from lunia.adapters.napcat.client import NapCatClient


class SystemAPI:
    """系统接口与系统扩展，复用传入的 Client。"""

    def __init__(self, client: NapCatClient) -> None:
        self.client = client

    async def get_login_info(
        self,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取当前登录账号信息。"""
        return await self.client.call_api("get_login_info", {}, timeout=timeout)

    async def get_version_info(
        self,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取 NapCat 版本信息。"""
        return await self.client.call_api("get_version_info", {}, timeout=timeout)

    async def can_send_record(
        self,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """检查当前是否可以发送语音。"""
        return await self.client.call_api("can_send_record", {}, timeout=timeout)

    async def can_send_image(
        self,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """检查当前是否可以发送图片。"""
        return await self.client.call_api("can_send_image", {}, timeout=timeout)

    async def get_status(
        self,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取 NapCat 运行状态。"""
        return await self.client.call_api("get_status", {}, timeout=timeout)

    async def set_online_status(
        self,
        status: int | str,
        ext_status: int | str,
        battery_status: int | str,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """设置在线状态。

        Args:
            status: 在线状态。
            ext_status: 扩展状态。
            battery_status: 电量状态。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "status": status,
            "ext_status": ext_status,
            "battery_status": battery_status,
        }
        return await self.client.call_api("set_online_status", params, timeout=timeout)

    async def set_input_status(
        self,
        user_id: str,
        event_type: int,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """设置对指定用户的输入状态。

        Args:
            user_id: 用户 QQ 号。
            event_type: 输入状态事件类型。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "user_id": user_id,
            "event_type": event_type,
        }
        return await self.client.call_api("set_input_status", params, timeout=timeout)

    async def nc_get_user_status(
        self,
        user_id: str,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取用户在线状态。

        Args:
            user_id: QQ号。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "user_id": user_id,
        }
        return await self.client.call_api("nc_get_user_status", params, timeout=timeout)

    async def check_url_safely(
        self,
        url: str,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """检查URL安全性。

        Args:
            url: 要检查的 URL。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "url": url,
        }
        return await self.client.call_api("check_url_safely", params, timeout=timeout)

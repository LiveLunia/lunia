"""NapCat 用户接口与用户扩展"""

from typing import Any

from lunia.adapters.napcat.client import NapCatClient


class UserAPI:
    """用户接口与用户扩展"""

    def __init__(self, client: NapCatClient) -> None:
        self.client = client

    async def set_self_longnick(
        self,
        long_nick: str,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """设置个性签名。

        Args:
            long_nick: 签名内容。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "longNick": long_nick,
        }
        return await self.client.call_api("set_self_longnick", params, timeout=timeout)

    async def set_qq_avatar(
        self,
        file: str,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """设置QQ头像。

        Args:
            file: 图片路径、URL或Base64。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "file": file,
        }
        return await self.client.call_api("set_qq_avatar", params, timeout=timeout)

    async def set_friend_remark(
        self,
        user_id: str,
        remark: str,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """设置好友备注。

        Args:
            user_id: 对方 QQ 号。
            remark: 备注内容。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "user_id": user_id,
            "remark": remark,
        }
        return await self.client.call_api("set_friend_remark", params, timeout=timeout)

    async def send_like(
        self,
        user_id: str,
        *,
        times: int | str = 1,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """给指定用户点赞。

        Args:
            user_id: 用户 QQ 号。
            times: 点赞次数。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "user_id": user_id,
            "times": times,
        }
        return await self.client.call_api("send_like", params, timeout=timeout)

    async def get_friend_list(
        self,
        *,
        no_cache: bool | str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取当前账号的好友列表。

        Args:
            no_cache: 是否绕过缓存。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {}
        if no_cache is not None:
            params["no_cache"] = no_cache
        return await self.client.call_api("get_friend_list", params, timeout=timeout)

    async def set_friend_add_request(
        self,
        flag: str,
        *,
        approve: str | bool | None = None,
        remark: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """处理加好友请求。

        Args:
            flag: 加好友请求的 flag (需从上报中获取)。
            approve: 是否同意请求。
            remark: 添加后的好友备注。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "flag": flag,
        }
        if approve is not None:
            params["approve"] = approve
        if remark is not None:
            params["remark"] = remark
        return await self.client.call_api(
            "set_friend_add_request", params, timeout=timeout
        )

    async def get_cookies(
        self,
        domain: str,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取 Cookies。

        Args:
            domain: 需要获取 cookies 的域名。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "domain": domain,
        }
        return await self.client.call_api("get_cookies", params, timeout=timeout)

    async def get_recent_contact(
        self,
        *,
        count: int | str = 10,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取最近会话列表。

        Args:
            count: 获取的数量。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "count": count,
        }
        return await self.client.call_api("get_recent_contact", params, timeout=timeout)

    async def set_qq_profile(
        self,
        nickname: str,
        *,
        personal_note: str | None = None,
        sex: int | str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """设置QQ资料。

        Args:
            nickname: 昵称。
            personal_note: 个性签名。
            sex: 性别 (0: 未知, 1: 男, 2: 女)。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "nickname": nickname,
        }
        if personal_note is not None:
            params["personal_note"] = personal_note
        if sex is not None:
            params["sex"] = sex
        return await self.client.call_api("set_qq_profile", params, timeout=timeout)

    async def delete_friend(
        self,
        *,
        friend_id: str | None = None,
        user_id: str | None = None,
        temp_block: bool | None = None,
        temp_both_del: bool | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """删除好友。

        Args:
            friend_id: 好友 QQ 号，与 user_id 至少提供一项。
            user_id: 用户 QQ 号。
            temp_block: 是否加入黑名单。
            temp_both_del: 是否双向删除。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        if friend_id is None and user_id is None:
            raise ValueError("friend_id 与 user_id 至少提供一项")
        params: dict[str, Any] = {}
        if friend_id is not None:
            params["friend_id"] = friend_id
        if user_id is not None:
            params["user_id"] = user_id
        if temp_block is not None:
            params["temp_block"] = temp_block
        if temp_both_del is not None:
            params["temp_both_del"] = temp_both_del
        return await self.client.call_api("delete_friend", params, timeout=timeout)

    async def get_stranger_info(
        self,
        user_id: str,
        *,
        no_cache: bool | str = False,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取指定非好友用户的信息。

        Args:
            user_id: 用户 QQ 号。
            no_cache: 是否绕过缓存。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "user_id": user_id,
            "no_cache": no_cache,
        }
        return await self.client.call_api("get_stranger_info", params, timeout=timeout)

    async def _get_model_show(
        self,
        *,
        model: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取机型显示。

        Args:
            model: 模型名称。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {}
        if model is not None:
            params["model"] = model
        return await self.client.call_api("_get_model_show", params, timeout=timeout)

    async def get_friends_with_category(
        self,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取带分组的好友列表。"""
        return await self.client.call_api(
            "get_friends_with_category", {}, timeout=timeout
        )

    async def get_profile_like(
        self,
        *,
        user_id: str | None = None,
        start: int | str = 0,
        count: int | str = 10,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取资料点赞。

        Args:
            user_id: QQ号。
            start: 起始位置。
            count: 获取数量。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "start": start,
            "count": count,
        }
        if user_id is not None:
            params["user_id"] = user_id
        return await self.client.call_api("get_profile_like", params, timeout=timeout)

    async def set_diy_online_status(
        self,
        face_id: int | str,
        *,
        face_type: int | str = "1",
        wording: str = " ",
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """设置自定义在线状态。

        Args:
            face_id: 图标ID。
            face_type: 图标类型。
            wording: 状态文字内容。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "face_id": face_id,
            "face_type": face_type,
            "wording": wording,
        }
        return await self.client.call_api(
            "set_diy_online_status", params, timeout=timeout
        )

    async def get_unidirectional_friend_list(
        self,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取单向好友列表。"""
        params: dict[str, Any] = {}
        return await self.client.call_api(
            "get_unidirectional_friend_list", params, timeout=timeout
        )

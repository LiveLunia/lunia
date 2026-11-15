from typing import Any, Literal

from .client import NapCatClient


class NapCatAPI:
    """NapCat API 封装"""

    def __init__(self, client: NapCatClient) -> None:
        self.client = client

    # 群组扩展

    async def del_group_album_media(
        self,
        group_id: str,
        album_id: str,
        lloc: str,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """删除群相册媒体。

        Args:
            group_id: 群号。
            album_id: 相册ID。
            lloc: 媒体ID (lloc)。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
            "album_id": album_id,
            "lloc": lloc,
        }
        return await self.client.call_api(
            "del_group_album_media", params, timeout=timeout
        )

    async def set_group_album_media_like(
        self,
        group_id: str,
        album_id: str,
        batch_id: str,
        *,
        lloc: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """点赞群相册媒体。

        Args:
            group_id: 群号。
            album_id: 相册ID。
            batch_id: 上传批次 ID。
            lloc: lloc，若对整个上传操作则不填。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
            "album_id": album_id,
            "batch_id": batch_id,
        }
        if lloc is not None:
            params["lloc"] = lloc
        return await self.client.call_api(
            "set_group_album_media_like", params, timeout=timeout
        )

    async def cancel_group_album_media_like(
        self,
        group_id: str,
        album_id: str,
        batch_id: str,
        *,
        lloc: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """取消点赞群相册媒体。

        Args:
            group_id: 群号。
            album_id: 相册ID。
            batch_id: 上传批次 ID。
            lloc: lloc，若对整个上传操作则不填。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
            "album_id": album_id,
            "batch_id": batch_id,
        }
        if lloc is not None:
            params["lloc"] = lloc
        return await self.client.call_api(
            "cancel_group_album_media_like", params, timeout=timeout
        )

    async def do_group_album_comment(
        self,
        group_id: str,
        album_id: str,
        content: str,
        *,
        lloc: str | None = None,
        batch_id: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """发表群相册评论。

        Args:
            group_id: 群号。
            album_id: 相册 ID。
            content: 评论内容。
            lloc: 图片 ID；不传或为空时评论整个上传批次，此时必须提供 batch_id。
            batch_id: 上传批次 ID。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        if not lloc and not batch_id:
            raise ValueError("lloc 与 batch_id 至少提供一项")
        params: dict[str, Any] = {
            "group_id": group_id,
            "album_id": album_id,
            "content": content,
        }
        if lloc is not None:
            params["lloc"] = lloc
        if batch_id is not None:
            params["batch_id"] = batch_id
        return await self.client.call_api(
            "do_group_album_comment", params, timeout=timeout
        )

    async def get_group_album_media_list(
        self,
        group_id: str,
        album_id: str,
        *,
        attach_info: str = "",
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取群相册媒体列表。

        Args:
            group_id: 群号。
            album_id: 相册ID。
            attach_info: 附加信息（用于分页）。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
            "album_id": album_id,
            "attach_info": attach_info,
        }
        return await self.client.call_api(
            "get_group_album_media_list", params, timeout=timeout
        )

    async def get_qun_album_list(
        self,
        group_id: str,
        *,
        attach_info: str = "",
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取群相册列表。

        Args:
            group_id: 群号。
            attach_info: 附加信息（用于分页，从上一次返回结果中获取）。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
            "attach_info": attach_info,
        }
        return await self.client.call_api("get_qun_album_list", params, timeout=timeout)

    async def upload_image_to_qun_album(
        self,
        group_id: str,
        album_id: str,
        album_name: str,
        file: str,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """上传图片到群相册。

        Args:
            group_id: 群号。
            album_id: 相册ID。
            album_name: 相册名称。
            file: 图片路径、URL或Base64。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
            "album_id": album_id,
            "album_name": album_name,
            "file": file,
        }
        return await self.client.call_api(
            "upload_image_to_qun_album", params, timeout=timeout
        )

    async def set_group_add_option(
        self,
        group_id: str,
        add_type: int,
        *,
        group_question: str | None = None,
        group_answer: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """设置群加群选项。

        Args:
            group_id: 群号。
            add_type: 加群方式。
            group_question: 加群问题。
            group_answer: 加群答案。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
            "add_type": add_type,
        }
        if group_question is not None:
            params["group_question"] = group_question
        if group_answer is not None:
            params["group_answer"] = group_answer
        return await self.client.call_api(
            "set_group_add_option", params, timeout=timeout
        )

    async def set_group_robot_add_option(
        self,
        group_id: str,
        *,
        robot_member_switch: int | None = None,
        robot_member_examine: int | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """设置群机器人加群选项。

        Args:
            group_id: 群号。
            robot_member_switch: 机器人成员开关。
            robot_member_examine: 机器人成员审核。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
        }
        if robot_member_switch is not None:
            params["robot_member_switch"] = robot_member_switch
        if robot_member_examine is not None:
            params["robot_member_examine"] = robot_member_examine
        return await self.client.call_api(
            "set_group_robot_add_option", params, timeout=timeout
        )

    async def set_group_search(
        self,
        group_id: str,
        *,
        no_code_finger_open: int | None = None,
        no_finger_open: int | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """设置群搜索选项。

        Args:
            group_id: 群号。
            no_code_finger_open: 文档未说明含义的群搜索数值选项。
            no_finger_open: 文档未说明含义的群搜索数值选项。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
        }
        if no_code_finger_open is not None:
            params["no_code_finger_open"] = no_code_finger_open
        if no_finger_open is not None:
            params["no_finger_open"] = no_finger_open
        return await self.client.call_api("set_group_search", params, timeout=timeout)

    async def set_group_remark(
        self,
        group_id: str,
        remark: str,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """设置群备注。

        Args:
            group_id: 群号。
            remark: 备注。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
            "remark": remark,
        }
        return await self.client.call_api("set_group_remark", params, timeout=timeout)

    async def get_group_info_ex(
        self,
        group_id: str,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取群详细扩展信息。

        Args:
            group_id: 群号。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
        }
        return await self.client.call_api("get_group_info_ex", params, timeout=timeout)

    async def set_group_sign(
        self,
        group_id: str,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """群打卡。

        Args:
            group_id: 群号。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
        }
        return await self.client.call_api("set_group_sign", params, timeout=timeout)

    async def send_group_sign(
        self,
        group_id: str,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """群打卡。

        Args:
            group_id: 群号。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
        }
        return await self.client.call_api("send_group_sign", params, timeout=timeout)

    async def get_group_signed_list(
        self,
        group_id: str,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取群组今日打卡列表。

        Args:
            group_id: 群号。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
        }
        return await self.client.call_api(
            "get_group_signed_list", params, timeout=timeout
        )

    async def get_group_share_link(
        self,
        group_id: str,
        *,
        need_short_url: bool | str = True,
        src_id: int | str = 73,
        additional_param: str = "",
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取群分享链接。

        Args:
            group_id: 群号。
            need_short_url: 是否返回短链 (qm.qq.com/q/xxx)，false 返回完整 universal-share 链接。
            src_id: 分享来源 ID。
            additional_param: 附加参数。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
            "need_short_url": need_short_url,
            "src_id": src_id,
            "additional_param": additional_param,
        }
        return await self.client.call_api(
            "get_group_share_link", params, timeout=timeout
        )

    async def upload_images_to_qun_album(
        self,
        group_id: str,
        album_id: str,
        album_name: str,
        files: list[str],
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """上传多张图片到群相册。

        Args:
            group_id: 群号。
            album_id: 相册ID。
            album_name: 相册名称。
            files: 图片路径、URL或Base64 数组，一次上传多张。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
            "album_id": album_id,
            "album_name": album_name,
            "files": files,
        }
        return await self.client.call_api(
            "upload_images_to_qun_album", params, timeout=timeout
        )

    async def upload_video_to_qun_album(
        self,
        group_id: str,
        album_id: str,
        album_name: str,
        file: str,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """上传视频到群相册。

        Args:
            group_id: 群号。
            album_id: 相册ID。
            album_name: 相册名称。
            file: 视频路径、URL或Base64。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
            "album_id": album_id,
            "album_name": album_name,
            "file": file,
        }
        return await self.client.call_api(
            "upload_video_to_qun_album", params, timeout=timeout
        )

    # 核心接口

    async def set_group_todo(
        self,
        group_id: str,
        *,
        message_id: str | None = None,
        message_seq: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """设置群待办。

        Args:
            group_id: 群号。
            message_id: 消息ID。
            message_seq: 消息Seq (可选)。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
        }
        if message_id is not None:
            params["message_id"] = message_id
        if message_seq is not None:
            params["message_seq"] = message_seq
        return await self.client.call_api("set_group_todo", params, timeout=timeout)

    async def complete_group_todo(
        self,
        group_id: str,
        *,
        message_id: str | None = None,
        message_seq: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """完成群待办。

        Args:
            group_id: 群号。
            message_id: 消息ID。
            message_seq: 消息Seq (可选)。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
        }
        if message_id is not None:
            params["message_id"] = message_id
        if message_seq is not None:
            params["message_seq"] = message_seq
        return await self.client.call_api(
            "complete_group_todo", params, timeout=timeout
        )

    async def cancel_group_todo(
        self,
        group_id: str,
        *,
        message_id: str | None = None,
        message_seq: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """取消群待办。

        Args:
            group_id: 群号。
            message_id: 消息ID。
            message_seq: 消息Seq (可选)。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
        }
        if message_id is not None:
            params["message_id"] = message_id
        if message_seq is not None:
            params["message_seq"] = message_seq
        return await self.client.call_api("cancel_group_todo", params, timeout=timeout)

    async def group_poke(
        self,
        group_id: str,
        user_id: str,
        *,
        target_id: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """在群聊中发送戳一戳。

        Args:
            group_id: 群号。
            user_id: 用户 QQ 号。
            target_id: 戳一戳目标 QQ 号。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
            "user_id": user_id,
        }
        if target_id is not None:
            params["target_id"] = target_id
        return await self.client.call_api("group_poke", params, timeout=timeout)

    async def friend_poke(
        self,
        user_id: str,
        *,
        target_id: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """向好友发送戳一戳。

        Args:
            user_id: 用户 QQ 号。
            target_id: 戳一戳目标 QQ 号。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "user_id": user_id,
        }
        if target_id is not None:
            params["target_id"] = target_id
        return await self.client.call_api("friend_poke", params, timeout=timeout)

    async def send_poke(
        self,
        user_id: str,
        *,
        group_id: str | None = None,
        target_id: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """向指定用户发送戳一戳。

        Args:
            user_id: 用户 QQ 号。
            group_id: 群号。
            target_id: 戳一戳目标 QQ 号。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "user_id": user_id,
        }
        if group_id is not None:
            params["group_id"] = group_id
        if target_id is not None:
            params["target_id"] = target_id
        return await self.client.call_api("send_poke", params, timeout=timeout)

    # 群组接口

    async def get_group_detail_info(
        self,
        group_id: str,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取群详细信息。

        Args:
            group_id: 群号。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
        }
        return await self.client.call_api(
            "get_group_detail_info", params, timeout=timeout
        )

    async def get_group_list(
        self,
        *,
        no_cache: bool | str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取当前账号的群聊列表。

        Args:
            no_cache: 是否绕过缓存。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {}
        if no_cache is not None:
            params["no_cache"] = no_cache
        return await self.client.call_api("get_group_list", params, timeout=timeout)

    async def get_group_info(
        self,
        group_id: str,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取群聊基本信息。

        Args:
            group_id: 群号。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
        }
        return await self.client.call_api("get_group_info", params, timeout=timeout)

    async def get_group_member_list(
        self,
        group_id: str,
        *,
        no_cache: bool | str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取群聊成员列表。

        Args:
            group_id: 群号。
            no_cache: 是否绕过缓存。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
        }
        if no_cache is not None:
            params["no_cache"] = no_cache
        return await self.client.call_api(
            "get_group_member_list", params, timeout=timeout
        )

    async def get_group_member_info(
        self,
        group_id: str,
        user_id: str,
        *,
        no_cache: bool | str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取群聊中指定成员的信息。

        Args:
            group_id: 群号。
            user_id: 用户 QQ 号。
            no_cache: 是否绕过缓存。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
            "user_id": user_id,
        }
        if no_cache is not None:
            params["no_cache"] = no_cache
        return await self.client.call_api(
            "get_group_member_info", params, timeout=timeout
        )

    async def send_group_msg(
        self,
        group_id: str,
        message: str | list[dict[str, Any]],
        *,
        auto_escape: bool | str | None = None,
        source: str | None = None,
        news: list[dict[str, str]] | None = None,
        summary: str | None = None,
        prompt: str | None = None,
        send_timeout_ms: int | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """发送群聊消息。

        Args:
            group_id: 群号。
            message: 消息字符串或消息段数组。
            auto_escape: 是否将消息作为纯文本发送。
            source: 合并转发来源。
            news: 合并转发预览条目，每项包含字符串 text。
            summary: 合并转发摘要。
            prompt: 合并转发提示。
            send_timeout_ms: NapCat 服务端发送超时，单位毫秒；未指定时省略。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
            "message": message,
        }
        if auto_escape is not None:
            params["auto_escape"] = auto_escape
        if source is not None:
            params["source"] = source
        if news is not None:
            params["news"] = news
        if summary is not None:
            params["summary"] = summary
        if prompt is not None:
            params["prompt"] = prompt
        if send_timeout_ms is not None:
            params["timeout"] = send_timeout_ms
        return await self.client.call_api("send_group_msg", params, timeout=timeout)

    async def set_group_add_request(
        self,
        flag: str,
        *,
        approve: bool | str | None = None,
        reason: str | None = None,
        count: int = 100,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """处理加群请求。

        Args:
            flag: 请求flag。
            approve: 是否同意。
            reason: 拒绝理由。
            count: 搜索通知数量。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "flag": flag,
            "count": count,
        }
        if approve is not None:
            params["approve"] = approve
        if reason is not None:
            params["reason"] = reason
        return await self.client.call_api(
            "set_group_add_request", params, timeout=timeout
        )

    async def set_group_leave(
        self,
        group_id: str,
        *,
        is_dismiss: bool | str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """退出群组。

        Args:
            group_id: 群号。
            is_dismiss: 是否解散。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
        }
        if is_dismiss is not None:
            params["is_dismiss"] = is_dismiss
        return await self.client.call_api("set_group_leave", params, timeout=timeout)

    async def set_group_whole_ban(
        self,
        group_id: str,
        *,
        enable: bool | str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """全员禁言。

        Args:
            group_id: 群号。
            enable: 是否开启全员禁言。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
        }
        if enable is not None:
            params["enable"] = enable
        return await self.client.call_api(
            "set_group_whole_ban", params, timeout=timeout
        )

    async def set_group_ban(
        self,
        group_id: str,
        user_id: str,
        *,
        duration: int | str = 0,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """群组禁言。

        Args:
            group_id: 群号。
            user_id: 用户 QQ 号。
            duration: 禁言时长，单位秒。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
            "user_id": user_id,
            "duration": duration,
        }
        return await self.client.call_api("set_group_ban", params, timeout=timeout)

    async def set_group_kick(
        self,
        group_id: str,
        user_id: str,
        *,
        reject_add_request: bool | str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """群组踢人。

        Args:
            group_id: 群号。
            user_id: 用户 QQ 号。
            reject_add_request: 是否拒绝加群请求。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
            "user_id": user_id,
        }
        if reject_add_request is not None:
            params["reject_add_request"] = reject_add_request
        return await self.client.call_api("set_group_kick", params, timeout=timeout)

    async def set_group_admin(
        self,
        group_id: str,
        user_id: str,
        *,
        enable: bool | str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """设置群管理员。

        Args:
            group_id: 群号。
            user_id: 用户 QQ 号。
            enable: 是否设置为管理员。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
            "user_id": user_id,
        }
        if enable is not None:
            params["enable"] = enable
        return await self.client.call_api("set_group_admin", params, timeout=timeout)

    async def set_group_name(
        self,
        group_id: str,
        group_name: str,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """设置群名称。

        Args:
            group_id: 群号。
            group_name: 群名称。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
            "group_name": group_name,
        }
        return await self.client.call_api("set_group_name", params, timeout=timeout)

    async def set_group_card(
        self,
        group_id: str,
        user_id: str,
        *,
        card: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """设置群名片。

        Args:
            group_id: 群号。
            user_id: 用户QQ。
            card: 群名片。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
            "user_id": user_id,
        }
        if card is not None:
            params["card"] = card
        return await self.client.call_api("set_group_card", params, timeout=timeout)

    async def get_essence_msg_list(
        self,
        group_id: str,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取群精华消息。

        Args:
            group_id: 群号。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
        }
        return await self.client.call_api(
            "get_essence_msg_list", params, timeout=timeout
        )

    async def get_group_ignored_notifies(
        self,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取群忽略通知。"""
        params: dict[str, Any] = {}
        return await self.client.call_api(
            "get_group_ignored_notifies", params, timeout=timeout
        )

    async def delete_essence_msg(
        self,
        *,
        message_id: int | str | None = None,
        msg_seq: str | None = None,
        msg_random: str | None = None,
        group_id: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """移出精华消息。

        Args:
            message_id: 消息ID。
            msg_seq: 消息序号。
            msg_random: 消息随机数。
            group_id: 群号。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {}
        if message_id is not None:
            params["message_id"] = message_id
        if msg_seq is not None:
            params["msg_seq"] = msg_seq
        if msg_random is not None:
            params["msg_random"] = msg_random
        if group_id is not None:
            params["group_id"] = group_id
        return await self.client.call_api("delete_essence_msg", params, timeout=timeout)

    async def _get_group_notice(
        self,
        group_id: str,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取群公告。

        Args:
            group_id: 群号。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
        }
        return await self.client.call_api("_get_group_notice", params, timeout=timeout)

    async def set_essence_msg(
        self,
        message_id: int | str,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """设置精华消息。

        Args:
            message_id: 消息ID。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "message_id": message_id,
        }
        return await self.client.call_api("set_essence_msg", params, timeout=timeout)

    async def _del_group_notice(
        self,
        group_id: str,
        notice_id: str,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """删除群公告。

        Args:
            group_id: 群号。
            notice_id: 公告ID。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
            "notice_id": notice_id,
        }
        return await self.client.call_api("_del_group_notice", params, timeout=timeout)

    async def get_group_shut_list(
        self,
        group_id: str,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取群禁言列表。

        Args:
            group_id: 群号。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
        }
        return await self.client.call_api(
            "get_group_shut_list", params, timeout=timeout
        )

    async def get_group_ignore_add_request(
        self,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取群被忽略的加群请求。"""
        params: dict[str, Any] = {}
        return await self.client.call_api(
            "get_group_ignore_add_request", params, timeout=timeout
        )

    async def set_group_member_invite_policy(
        self,
        group_id: str,
        policy: Literal[
            "disabled", "require_approval", "no_approval", "no_approval_under_100"
        ],
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """设置群成员邀请策略。

        Args:
            group_id: 群号。
            policy: 成员邀请策略：禁止、需要管理员审核、无需审核、群成员少于100人时无需审核。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
            "policy": policy,
        }
        return await self.client.call_api(
            "set_group_member_invite_policy", params, timeout=timeout
        )

    async def set_group_member_permissions(
        self,
        group_id: str,
        *,
        allow_member_upload_album: bool | None = None,
        allow_member_temporary_session: bool | None = None,
        allow_member_create_group: bool | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """设置群成员功能权限。

        Args:
            group_id: 群号。
            allow_member_upload_album: 允许成员上传群相册。
            allow_member_temporary_session: 允许成员发起临时会话。
            allow_member_create_group: 允许成员发起新的群聊。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
        }
        if allow_member_upload_album is not None:
            params["allow_member_upload_album"] = allow_member_upload_album
        if allow_member_temporary_session is not None:
            params["allow_member_temporary_session"] = allow_member_temporary_session
        if allow_member_create_group is not None:
            params["allow_member_create_group"] = allow_member_create_group
        return await self.client.call_api(
            "set_group_member_permissions", params, timeout=timeout
        )

    async def set_group_new_member_history_visibility(
        self,
        group_id: str,
        visible: bool,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """设置新成员历史消息可见性。

        Args:
            group_id: 群号。
            visible: 新成员默认可见最近聊天记录。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
            "visible": visible,
        }
        return await self.client.call_api(
            "set_group_new_member_history_visibility", params, timeout=timeout
        )

    # 扩展接口

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

    async def set_group_special_title(
        self,
        group_id: str,
        user_id: str,
        *,
        special_title: str = "",
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """设置专属头衔。

        Args:
            group_id: 群号。
            user_id: QQ号。
            special_title: 专属头衔。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
            "user_id": user_id,
            "special_title": special_title,
        }
        return await self.client.call_api(
            "set_group_special_title", params, timeout=timeout
        )

    # 系统接口

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

    # 用户接口

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

    # 系统扩展

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

    # 文件接口

    async def get_file(
        self,
        *,
        file: str | None = None,
        file_id: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取文件信息及下载路径。

        Args:
            file: 文件路径、URL 或 Base64，与 file_id 至少提供一项。
            file_id: 文件 ID。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        if file is None and file_id is None:
            raise ValueError("file 和 file_id 至少提供一项")
        params: dict[str, Any] = {}
        if file is not None:
            params["file"] = file
        if file_id is not None:
            params["file_id"] = file_id
        return await self.client.call_api("get_file", params, timeout=timeout)

    async def get_image(
        self,
        *,
        file: str | None = None,
        file_id: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取图片信息及路径。

        Args:
            file: 文件路径、URL 或 Base64，与 file_id 至少提供一项。
            file_id: 文件 ID。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        if file is None and file_id is None:
            raise ValueError("file 和 file_id 至少提供一项")
        params: dict[str, Any] = {}
        if file is not None:
            params["file"] = file
        if file_id is not None:
            params["file_id"] = file_id
        return await self.client.call_api("get_image", params, timeout=timeout)

    async def get_record(
        self,
        *,
        out_format: str,
        file: str | None = None,
        file_id: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取语音文件信息并指定转换格式。

        Args:
            out_format: 语音输出格式。
            file: 文件路径、URL 或 Base64，与 file_id 至少提供一项。
            file_id: 文件 ID。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        if file is None and file_id is None:
            raise ValueError("file 和 file_id 至少提供一项")
        params: dict[str, Any] = {
            "out_format": out_format,
        }
        if file is not None:
            params["file"] = file
        if file_id is not None:
            params["file_id"] = file_id
        return await self.client.call_api("get_record", params, timeout=timeout)

    async def get_group_file_url(
        self,
        group_id: str,
        file_id: str,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取群文件的下载链接。

        Args:
            group_id: 群号。
            file_id: 文件 ID。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
            "file_id": file_id,
        }
        return await self.client.call_api("get_group_file_url", params, timeout=timeout)

    async def get_private_file_url(
        self,
        file_id: str,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取私聊文件URL。

        Args:
            file_id: 文件ID。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "file_id": file_id,
        }
        return await self.client.call_api(
            "get_private_file_url", params, timeout=timeout
        )

    # Go-CQHTTP

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

    async def get_group_root_files(
        self,
        group_id: str,
        *,
        file_count: int | str = 50,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取群文件根目录下的文件及文件夹。

        Args:
            group_id: 群号。
            file_count: 获取的文件数量。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
            "file_count": file_count,
        }
        return await self.client.call_api(
            "get_group_root_files", params, timeout=timeout
        )

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

    async def get_group_honor_info(
        self,
        group_id: str,
        *,
        type: Literal[
            "all", "talkative", "performer", "legend", "strong_newbie", "emotion"
        ]
        | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取群荣誉信息。

        Args:
            group_id: 群号。
            type: 荣誉类型。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
        }
        if type is not None:
            params["type"] = type
        return await self.client.call_api(
            "get_group_honor_info", params, timeout=timeout
        )

    async def _send_group_notice(
        self,
        group_id: str,
        content: str,
        *,
        image: str | None = None,
        pinned: int | str = 0,
        type: int | str = 1,
        confirm_required: int | str = 1,
        is_show_edit_card: int | str = 0,
        tip_window_type: int | str = 0,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """发送群公告。

        Args:
            group_id: 群号。
            content: 公告内容。
            image: 公告图片路径或 URL。
            pinned: 是否置顶 (0/1)。
            type: 类型 (默认为 1)。
            confirm_required: 是否需要确认 (0/1)。
            is_show_edit_card: 是否显示修改群名片引导 (0/1)。
            tip_window_type: 弹窗类型 (默认为 0)。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
            "content": content,
            "pinned": pinned,
            "type": type,
            "confirm_required": confirm_required,
            "is_show_edit_card": is_show_edit_card,
            "tip_window_type": tip_window_type,
        }
        if image is not None:
            params["image"] = image
        return await self.client.call_api("_send_group_notice", params, timeout=timeout)

    async def get_group_at_all_remain(
        self,
        group_id: str,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取群艾特全体剩余次数。

        Args:
            group_id: 群号。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
        }
        return await self.client.call_api(
            "get_group_at_all_remain", params, timeout=timeout
        )

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

    async def download_file(
        self,
        *,
        url: str | None = None,
        base64: str | None = None,
        name: str | None = None,
        headers: str | list[str] | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """下载文件到 NapCat 本地临时目录。

        Args:
            url: 文件下载链接，与 base64 至少提供一项。
            base64: 文件的 Base64 数据。
            name: 文件名。
            headers: 下载请求头。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        if url is None and base64 is None:
            raise ValueError("url 和 base64 至少提供一项")
        params: dict[str, Any] = {}
        if url is not None:
            params["url"] = url
        if base64 is not None:
            params["base64"] = base64
        if name is not None:
            params["name"] = name
        if headers is not None:
            params["headers"] = headers
        return await self.client.call_api("download_file", params, timeout=timeout)

    async def upload_group_file(
        self,
        group_id: str,
        file: str,
        name: str,
        *,
        folder: str | None = None,
        folder_id: str | None = None,
        upload_file: bool = True,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """上传文件到群文件系统。

        Args:
            group_id: 群号。
            file: NapCat 主机可访问的文件路径或 URL。
            name: 文件名。
            folder: 父目录 ID。
            folder_id: 父目录 ID 的兼容字段。
            upload_file: 是否执行上传。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
            "file": file,
            "name": name,
            "upload_file": upload_file,
        }
        if folder is not None:
            params["folder"] = folder
        if folder_id is not None:
            params["folder_id"] = folder_id
        return await self.client.call_api("upload_group_file", params, timeout=timeout)

    async def get_group_msg_history(
        self,
        group_id: str,
        *,
        message_seq: str | None = None,
        count: int = 20,
        reverse_order: bool = False,
        disable_get_url: bool = False,
        parse_mult_msg: bool = True,
        quick_reply: bool = False,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取群聊历史消息。

        Args:
            group_id: 群号。
            message_seq: 起始消息序号。
            count: 获取的数量。
            reverse_order: 是否反向排序。
            disable_get_url: 是否禁用获取 URL。
            parse_mult_msg: 是否解析合并消息。
            quick_reply: 是否快速回复。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
            "count": count,
            "reverse_order": reverse_order,
            "disable_get_url": disable_get_url,
            "parse_mult_msg": parse_mult_msg,
            "quick_reply": quick_reply,
            "reverseOrder": reverse_order,
        }
        if message_seq is not None:
            params["message_seq"] = message_seq
        return await self.client.call_api(
            "get_group_msg_history", params, timeout=timeout
        )

    async def get_forward_msg(
        self,
        *,
        message_id: str | None = None,
        id: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取合并转发消息内容。

        Args:
            message_id: 合并转发消息 ID，与 id 至少提供一项。
            id: 合并转发消息 ID。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        if message_id is None and id is None:
            raise ValueError("message_id 和 id 至少提供一项")
        params: dict[str, Any] = {}
        if message_id is not None:
            params["message_id"] = message_id
        if id is not None:
            params["id"] = id
        return await self.client.call_api("get_forward_msg", params, timeout=timeout)

    async def get_friend_msg_history(
        self,
        user_id: str,
        *,
        message_seq: str | None = None,
        count: int = 20,
        reverse_order: bool = False,
        disable_get_url: bool = False,
        parse_mult_msg: bool = True,
        quick_reply: bool = False,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取好友历史消息。

        Args:
            user_id: 用户 QQ 号。
            message_seq: 起始消息序号。
            count: 获取的数量。
            reverse_order: 是否反向排序。
            disable_get_url: 是否禁用获取 URL。
            parse_mult_msg: 是否解析合并消息。
            quick_reply: 是否快速回复。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "user_id": user_id,
            "count": count,
            "reverse_order": reverse_order,
            "disable_get_url": disable_get_url,
            "parse_mult_msg": parse_mult_msg,
            "quick_reply": quick_reply,
            "reverseOrder": reverse_order,
        }
        if message_seq is not None:
            params["message_seq"] = message_seq
        return await self.client.call_api(
            "get_friend_msg_history", params, timeout=timeout
        )

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

    async def set_group_portrait(
        self,
        file: str,
        group_id: str,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """设置群头像。

        Args:
            file: 头像文件路径或 URL。
            group_id: 群号。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "file": file,
            "group_id": group_id,
        }
        return await self.client.call_api("set_group_portrait", params, timeout=timeout)

    async def upload_private_file(
        self,
        user_id: str,
        file: str,
        name: str,
        *,
        upload_file: bool = True,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """上传文件到指定私聊会话。

        Args:
            user_id: 用户 QQ 号。
            file: NapCat 主机可访问的文件路径或 URL。
            name: 文件名。
            upload_file: 是否执行上传。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "user_id": user_id,
            "file": file,
            "name": name,
            "upload_file": upload_file,
        }
        return await self.client.call_api(
            "upload_private_file", params, timeout=timeout
        )

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

    async def delete_group_file(
        self,
        group_id: str,
        file_id: str,
        *,
        bus_id: int | None = None,
        busid: int | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """删除群文件。

        Args:
            group_id: 群号。
            file_id: 文件ID。
            bus_id: 文件业务ID，默认使用文件列表中的 busid。
            busid: 文件业务ID，兼容 busid 字段。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
            "file_id": file_id,
        }
        if bus_id is not None:
            params["bus_id"] = bus_id
        if busid is not None:
            params["busid"] = busid
        return await self.client.call_api("delete_group_file", params, timeout=timeout)

    async def create_group_file_folder(
        self,
        group_id: str,
        *,
        folder_name: str | None = None,
        name: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """创建群文件目录。

        Args:
            group_id: 群号。
            folder_name: 文件夹名称。
            name: 文件夹名称。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        if folder_name is None and name is None:
            raise ValueError("folder_name 与 name 至少提供一项")
        params: dict[str, Any] = {
            "group_id": group_id,
        }
        if folder_name is not None:
            params["folder_name"] = folder_name
        if name is not None:
            params["name"] = name
        return await self.client.call_api(
            "create_group_file_folder", params, timeout=timeout
        )

    async def delete_group_folder(
        self,
        group_id: str,
        *,
        folder_id: str | None = None,
        folder: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """删除群文件目录。

        Args:
            group_id: 群号。
            folder_id: 文件夹ID。
            folder: 文件夹ID。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        if folder_id is None and folder is None:
            raise ValueError("folder_id 与 folder 至少提供一项")
        params: dict[str, Any] = {
            "group_id": group_id,
        }
        if folder_id is not None:
            params["folder_id"] = folder_id
        if folder is not None:
            params["folder"] = folder
        return await self.client.call_api(
            "delete_group_folder", params, timeout=timeout
        )

    async def get_group_file_system_info(
        self,
        group_id: str,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取群文件系统信息。

        Args:
            group_id: 群号。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
        }
        return await self.client.call_api(
            "get_group_file_system_info", params, timeout=timeout
        )

    async def get_group_files_by_folder(
        self,
        group_id: str,
        *,
        folder_id: str | None = None,
        folder: str | None = None,
        file_count: int | str = 50,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """获取群文件夹内的文件及子文件夹。

        Args:
            group_id: 群号。
            folder_id: 文件夹 ID，与 folder 至少提供一项。
            folder: 父目录 ID。
            file_count: 获取的文件数量。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        if folder_id is None and folder is None:
            raise ValueError("folder_id 和 folder 至少提供一项")
        params: dict[str, Any] = {
            "group_id": group_id,
            "file_count": file_count,
        }
        if folder_id is not None:
            params["folder_id"] = folder_id
        if folder is not None:
            params["folder"] = folder
        return await self.client.call_api(
            "get_group_files_by_folder", params, timeout=timeout
        )

    # 消息接口

    async def forward_friend_single_msg(
        self,
        message_id: int | str,
        *,
        group_id: str | None = None,
        user_id: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """转发单条消息。

        Args:
            message_id: 消息ID。
            group_id: 目标群号。
            user_id: 目标用户QQ。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "message_id": message_id,
        }
        if group_id is not None:
            params["group_id"] = group_id
        if user_id is not None:
            params["user_id"] = user_id
        return await self.client.call_api(
            "forward_friend_single_msg", params, timeout=timeout
        )

    async def forward_group_single_msg(
        self,
        message_id: int | str,
        *,
        group_id: str | None = None,
        user_id: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """转发单条消息。

        Args:
            message_id: 消息ID。
            group_id: 目标群号。
            user_id: 目标用户QQ。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "message_id": message_id,
        }
        if group_id is not None:
            params["group_id"] = group_id
        if user_id is not None:
            params["user_id"] = user_id
        return await self.client.call_api(
            "forward_group_single_msg", params, timeout=timeout
        )

    async def mark_group_msg_as_read(
        self,
        group_id: str,
        *,
        user_id: str | int | None = None,
        message_id: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """标记群聊消息为已读。

        Args:
            group_id: 群号。
            user_id: 用户 QQ 号。
            message_id: 消息 ID。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "group_id": group_id,
        }
        if user_id is not None:
            params["user_id"] = user_id
        if message_id is not None:
            params["message_id"] = message_id
        return await self.client.call_api(
            "mark_group_msg_as_read", params, timeout=timeout
        )

    async def mark_private_msg_as_read(
        self,
        user_id: str | int,
        *,
        group_id: str | None = None,
        message_id: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """标记私聊消息为已读。

        Args:
            user_id: 用户 QQ 号。
            group_id: 群号。
            message_id: 消息 ID。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "user_id": user_id,
        }
        if group_id is not None:
            params["group_id"] = group_id
        if message_id is not None:
            params["message_id"] = message_id
        return await self.client.call_api(
            "mark_private_msg_as_read", params, timeout=timeout
        )

    async def get_msg(
        self,
        message_id: int | str,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """根据消息 ID 获取消息详情。

        Args:
            message_id: 消息 ID。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "message_id": message_id,
        }
        return await self.client.call_api("get_msg", params, timeout=timeout)

    async def send_private_msg(
        self,
        user_id: str,
        message: str | list[dict[str, Any]],
        timeout: float | None = 10.0,
        *,
        group_id: str | None = None,
        auto_escape: bool | str | None = None,
        source: str | None = None,
        news: list[dict[str, str]] | None = None,
        summary: str | None = None,
        prompt: str | None = None,
        send_timeout_ms: int | None = None,
    ) -> dict[str, Any]:
        """发送私聊消息。

        Args:
            user_id: 用户 QQ 号。
            message: 消息字符串或消息段数组。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
            group_id: 群号。
            auto_escape: 是否将消息作为纯文本发送。
            source: 合并转发来源。
            news: 合并转发预览条目，每项包含字符串 text。
            summary: 合并转发摘要。
            prompt: 合并转发提示。
            send_timeout_ms: NapCat 服务端发送超时，单位毫秒；未指定时省略。
        """
        params: dict[str, Any] = {
            "user_id": user_id,
            "message": message,
        }
        if group_id is not None:
            params["group_id"] = group_id
        if auto_escape is not None:
            params["auto_escape"] = auto_escape
        if source is not None:
            params["source"] = source
        if news is not None:
            params["news"] = news
        if summary is not None:
            params["summary"] = summary
        if prompt is not None:
            params["prompt"] = prompt
        if send_timeout_ms is not None:
            params["timeout"] = send_timeout_ms
        return await self.client.call_api("send_private_msg", params, timeout=timeout)

    async def send_msg(
        self,
        message_type: Literal["private", "group"],
        message: str | list[dict[str, Any]],
        *,
        user_id: str | None = None,
        group_id: str | None = None,
        auto_escape: bool | str | None = None,
        source: str | None = None,
        news: list[dict[str, str]] | None = None,
        summary: str | None = None,
        prompt: str | None = None,
        send_timeout_ms: int | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """按指定类型发送私聊或群聊消息。

        Args:
            message_type: 消息类型，private 或 group。
            message: 消息字符串或消息段数组。
            user_id: 私聊目标 QQ 号，private 类型时必填。
            group_id: 群聊目标群号，group 类型时必填。
            auto_escape: 是否将消息作为纯文本发送。
            source: 合并转发来源。
            news: 合并转发预览条目，每项包含字符串 text。
            summary: 合并转发摘要。
            prompt: 合并转发提示。
            send_timeout_ms: NapCat 服务端发送超时，单位毫秒；未指定时省略。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        if message_type not in ("private", "group"):
            raise ValueError("message_type 必须为 private 或 group")
        if message_type == "private" and user_id is None:
            raise ValueError("私聊消息必须提供 user_id")
        if message_type == "group" and group_id is None:
            raise ValueError("群聊消息必须提供 group_id")
        params: dict[str, Any] = {
            "message_type": message_type,
            "message": message,
        }
        if user_id is not None:
            params["user_id"] = user_id
        if group_id is not None:
            params["group_id"] = group_id
        if auto_escape is not None:
            params["auto_escape"] = auto_escape
        if source is not None:
            params["source"] = source
        if news is not None:
            params["news"] = news
        if summary is not None:
            params["summary"] = summary
        if prompt is not None:
            params["prompt"] = prompt
        if send_timeout_ms is not None:
            params["timeout"] = send_timeout_ms
        return await self.client.call_api("send_msg", params, timeout=timeout)

    async def delete_msg(
        self,
        message_id: int | str,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """撤回已发送的消息。

        Args:
            message_id: 消息 ID。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        params: dict[str, Any] = {
            "message_id": message_id,
        }
        return await self.client.call_api("delete_msg", params, timeout=timeout)

    async def mark_msg_as_read(
        self,
        *,
        user_id: str | int | None = None,
        group_id: str | None = None,
        message_id: str | None = None,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """标记指定渠道的消息为已读。

        Args:
            user_id: 用户 QQ 号。
            group_id: 群号。
            message_id: 消息 ID。
            timeout: 客户端等待响应的超时秒数；None 表示不限时。
        """
        if message_id is None and group_id is None and user_id is None:
            raise ValueError("至少提供一个消息或渠道定位字段")
        params: dict[str, Any] = {}
        if user_id is not None:
            params["user_id"] = user_id
        if group_id is not None:
            params["group_id"] = group_id
        if message_id is not None:
            params["message_id"] = message_id
        return await self.client.call_api("mark_msg_as_read", params, timeout=timeout)

    async def _mark_all_as_read(
        self,
        *,
        timeout: float | None = 10.0,
    ) -> dict[str, Any]:
        """标记所有消息已读。"""
        params: dict[str, Any] = {}
        return await self.client.call_api("_mark_all_as_read", params, timeout=timeout)

    # 用户扩展

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

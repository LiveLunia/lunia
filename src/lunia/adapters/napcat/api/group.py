"""NapCat 群组接口与群组扩展；分类不表示 OneBot 11 标准归属。"""

from typing import Any, Literal

from lunia.adapters.napcat.client import NapCatClient


class GroupAPI:
    """群组接口与群组扩展，复用传入的 Client。"""

    def __init__(self, client: NapCatClient) -> None:
        self.client = client

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

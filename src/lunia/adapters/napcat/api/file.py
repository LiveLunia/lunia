"""NapCat 文件接口与文件扩展"""

from typing import Any

from lunia.adapters.napcat.client import NapCatClient


class FileAPI:
    """文件接口与文件扩展"""

    def __init__(self, client: NapCatClient) -> None:
        self.client = client

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

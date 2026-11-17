"""共享同一个 Client 的 NapCat 分类 API。"""

from lunia.adapters.napcat.client import NapCatClient

from .extensions import ExtensionsAPI
from .file import FileAPI
from .group import GroupAPI
from .message import MessageAPI
from .system import SystemAPI
from .user import UserAPI

__all__ = ["NapCatAPI"]


class NapCatAPI:
    """组合 NapCat 各功能领域的 API，不创建独立连接。"""

    def __init__(self, client: NapCatClient) -> None:
        self.client = client
        self.message = MessageAPI(client)
        self.group = GroupAPI(client)
        self.user = UserAPI(client)
        self.file = FileAPI(client)
        self.system = SystemAPI(client)
        self.extensions = ExtensionsAPI(client)

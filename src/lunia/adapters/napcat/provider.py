from lunia.adapters.napcat.api import NapCatAPI
from lunia.core.events import ConversationType
from lunia.core.logging import get_logger

logger = get_logger(__name__)


class NapCatUserProvider:
    """通过 NapCat API 提供用户名称信息。"""

    def __init__(self, api: NapCatAPI) -> None:
        self._api = api

    async def get_user_name(
        self,
        conversation_type: ConversationType,
        conversation_id: str,
        user_id: str,
    ) -> tuple[str | None, str | None] | None:
        """获取用户昵称与会话别名"""
        try:
            if conversation_type == "group":
                response = await self._api.group.get_group_member_info(
                    group_id=conversation_id,
                    user_id=user_id,
                )
                alias_field = "card"

            elif conversation_type == "private":
                response = await self._api.user.get_stranger_info(
                    user_id=user_id,
                )
                alias_field = "remark"

            else:
                return None

            if response.get("status") != "ok":
                return None
            if response.get("retcode") != 0:
                return None

            data = response.get("data")

            if not isinstance(data, dict):
                return None

            nickname = data.get("nickname")
            alias = data.get(alias_field)

            if not isinstance(nickname, str):
                nickname = None

            if not isinstance(alias, str):
                alias = None

            return nickname, alias

        except Exception:
            logger.exception("NapCat 用户资料查询失败")
            return None

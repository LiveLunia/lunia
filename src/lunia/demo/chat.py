import os

from lunia.core.actions.models import SendMessage
from lunia.core.actions.router import ActionRouter
from lunia.core.events.models import EventEnvelope
from lunia.core.logging import get_logger
from lunia.llm import LLMManager, LLMRequest, Message

logger = get_logger(__name__)

test_qq = str(os.environ["TEST_QQ"])


class ChatDemo:
    """临时 LLM 对话用例，用于验证完整的消息链路。"""

    def __init__(
        self,
        llm: LLMManager,
        actions: ActionRouter,
    ) -> None:
        self.llm = llm
        self.actions = actions

    async def handle(self, envelope: EventEnvelope) -> None:
        """处理聊天事件并调用 LLM 回复。"""
        event = envelope.event

        if event["kind"] != "chat.message":
            return

        if event["actor_id"] == event["account_id"]:
            return

        if envelope.adapter_id is None:
            logger.warning("聊天事件缺少 Adapter 来源")
            return

        text = "".join(
            segment["text"]
            for segment in event["payload"]["segments"]
            if segment["type"] == "text"
        ).strip()

        if not text:
            return

        if event["conversation_type"] == "group" and "lunia" not in text.lower():
            return

        if (
            event["conversation_type"] == "private"
            and event["conversation_id"] != test_qq
        ):
            return

        # 构建模型请求
        request = LLMRequest(
            model="chat",
            messages=[
                Message(
                    role="system",
                    content=(
                        "你是 Lunia，一位自然、亲切的虚拟角色。"
                        "请简洁地回应用户，不要使用助手式套话。"
                    ),
                ),
                Message(role="user", content=text),
            ],
            max_tokens=512,
        )

        try:
            response = await self.llm.complete(request)

            action = SendMessage(
                adapter_id=envelope.adapter_id,
                conversation_type=event["conversation_type"],
                conversation_id=event["conversation_id"],
                content=response.content,
            )

            result = await self.actions.execute(action)

            if result.get("status") != "ok" or result.get("retcode") != 0:
                logger.error("消息发送失败: %s", result)

        except Exception:
            logger.exception("LLM 对话处理失败")

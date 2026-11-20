import asyncio
from unittest.mock import AsyncMock

from lunia.llm import (
    LLMManager,
    LLMRequest,
    LLMResponse,
    Message,
    ModelConfig,
    ProviderConfig,
)


def test_llm_manager_routes_model() -> None:
    async def scenario() -> None:
        manager = LLMManager(
            providers={
                "deepseek": ProviderConfig(
                    base_url="https://api.deepseek.com",
                    api_key="test-key",
                ),
            },
            models={
                "chat": ModelConfig(
                    provider="deepseek",
                    model_id="deepseek-flash",
                ),
            },
        )

        fake = AsyncMock()
        fake.complete.return_value = LLMResponse(
            content="你好！",
            model="deepseek-flash",
        )

        # 替换网络客户端，不发送真实 HTTP 请求
        original = manager._clients["deepseek"]

        try:
            manager._clients["deepseek"] = fake

            request = LLMRequest(
                model="chat",
                messages=[
                    Message(role="user", content="你好"),
                ],
            )

            result = await manager.complete(request)

            assert result.content == "你好！"

            fake.complete.assert_awaited_once_with(
                model="deepseek-flash",
                messages=request.messages,
            )
        finally:
            await original.close()
            await manager.close()

    asyncio.run(scenario())

from lunia.llm.config import ModelConfig, ProviderConfig
from lunia.llm.protocols.openai import OpenAICompatibleClient
from lunia.llm.types import LLMRequest, LLMResponse


class LLMManager:
    """管理模型别名与 Provider 客户端。"""

    def __init__(
        self,
        providers: dict[str, ProviderConfig],
        models: dict[str, ModelConfig],
    ) -> None:
        self._models = models.copy()
        self._clients = {
            name: OpenAICompatibleClient(
                base_url=config.base_url,
                api_key=config.api_key,
            )
            for name, config in providers.items()
        }
        self._closed = False

    async def complete(
        self,
        request: LLMRequest,
    ) -> LLMResponse:
        if self._closed:
            raise RuntimeError("LLMManager 已关闭")

        config = self._models.get(request.model)
        if config is None:
            raise LookupError(f"未知模型别名: {request.model}")

        client = self._clients.get(config.provider)
        if client is None:
            raise LookupError(f"未知 LLM Provider: {config.provider}")

        return await client.complete(
            model=config.model_id,
            messages=request.messages,
        )

    async def close(self) -> None:
        if self._closed:
            return

        self._closed = True

        for client in self._clients.values():
            await client.close()

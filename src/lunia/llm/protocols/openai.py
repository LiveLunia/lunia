from openai import AsyncOpenAI
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)

from lunia.llm.types import (
    LLMResponse,
    Message,
    Usage,
)


def to_openai_messages(
    messages: list[Message],
) -> list[ChatCompletionMessageParam]:
    result: list[ChatCompletionMessageParam] = []

    for message in messages:
        match message.role:
            case "system":
                result.append(
                    ChatCompletionSystemMessageParam(
                        role="system",
                        content=message.content,
                    )
                )
            case "user":
                result.append(
                    ChatCompletionUserMessageParam(
                        role="user",
                        content=message.content,
                    )
                )
            case "assistant":
                result.append(
                    ChatCompletionAssistantMessageParam(
                        role="assistant",
                        content=message.content,
                    )
                )

    return result


class OpenAICompatibleClient:
    """OpenAI Chat Completions 兼容协议客户端。"""

    def __init__(
        self,
        base_url: str,
        api_key: str,
    ) -> None:
        self._client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=30.0,
            max_retries=1,
        )

    async def complete(
        self,
        model: str,
        messages: list[Message],
    ) -> LLMResponse:
        response = await self._client.chat.completions.create(
            model=model,
            messages=to_openai_messages(messages),
        )

        content = response.choices[0].message.content

        if content is None:
            raise ValueError("模型未返回文本内容")

        usage = None
        if response.usage is not None:
            usage = Usage(
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
            )

        return LLMResponse(
            content=content,
            model=response.model,
            usage=usage,
        )

    async def close(self) -> None:
        await self._client.close()

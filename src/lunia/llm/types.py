from dataclasses import dataclass
from typing import Literal

type Role = Literal["system", "user", "assistant"]


@dataclass(frozen=True, slots=True)
class Message:
    role: Role
    content: str


@dataclass(frozen=True, slots=True)
class Usage:
    input_tokens: int
    output_tokens: int
    total_tokens: int


@dataclass(frozen=True, slots=True)
class LLMRequest:
    model: str  # 内部模型名称
    messages: list[Message]


@dataclass(frozen=True, slots=True)
class LLMResponse:
    content: str
    model: str
    usage: Usage | None = None

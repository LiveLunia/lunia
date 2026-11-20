from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProviderConfig:
    base_url: str
    api_key: str


@dataclass(frozen=True, slots=True)
class ModelConfig:
    provider: str
    model_id: str

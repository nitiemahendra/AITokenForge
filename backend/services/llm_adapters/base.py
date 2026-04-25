from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMResponse:
    text: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float
    success: bool
    error: Optional[str] = None


class LLMAdapter(ABC):
    """Base interface for all local LLM adapters."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.1,
    ) -> LLMResponse:
        ...

    @abstractmethod
    async def is_available(self) -> bool:
        ...

    @abstractmethod
    def adapter_name(self) -> str:
        ...

    @abstractmethod
    def model_name(self) -> str:
        ...

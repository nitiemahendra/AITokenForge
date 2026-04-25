import asyncio
import time
from typing import Optional

from .base import LLMAdapter, LLMResponse


class MockAdapter(LLMAdapter):
    """
    Deterministic mock adapter for testing and CI environments
    where no local LLM is available.
    """

    def adapter_name(self) -> str:
        return "mock"

    def model_name(self) -> str:
        return "mock-model"

    async def is_available(self) -> bool:
        return True

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.1,
    ) -> LLMResponse:
        await asyncio.sleep(0.05)  # Simulate latency

        # Extract the original prompt from the optimization request
        lines = prompt.split("\n")
        cleaned_lines = []
        in_prompt_section = False
        for line in lines:
            if "ORIGINAL PROMPT:" in line or "PROMPT TO ANALYZE:" in line:
                in_prompt_section = True
                continue
            if in_prompt_section and line.strip().startswith("---"):
                break
            if in_prompt_section and line.strip():
                cleaned_lines.append(line.strip())

        # Mock compression: remove filler words
        result = " ".join(cleaned_lines) if cleaned_lines else prompt[:200]
        for filler in [
            "Please ", "Kindly ", "I would like you to ", "Can you ", "Could you ",
            "In order to ", "It is important that ", "You should ", "Make sure to ",
        ]:
            result = result.replace(filler, "")

        return LLMResponse(
            text=result.strip() or "Optimized prompt placeholder.",
            model="mock-model",
            prompt_tokens=len(prompt.split()),
            completion_tokens=len(result.split()),
            latency_ms=50.0,
            success=True,
        )

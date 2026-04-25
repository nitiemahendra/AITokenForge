import time

import httpx

from ...utils.logger import get_logger
from .base import LLMAdapter, LLMResponse

logger = get_logger(__name__)


class OllamaAdapter(LLMAdapter):
    """
    Adapter for Ollama local inference server.
    Targets Gemma 3 4B by default but works with any Ollama-served model.
    """

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "gemma3:4b", timeout: int = 120):
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout = timeout
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(timeout))

    def adapter_name(self) -> str:
        return "ollama"

    def model_name(self) -> str:
        return self._model

    async def is_available(self) -> bool:
        try:
            response = await self._client.get(f"{self._base_url}/api/tags")
            return response.status_code == 200
        except Exception as exc:
            logger.warning("ollama_unavailable", error=str(exc))
            return False

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 2048,
        temperature: float = 0.1,
    ) -> LLMResponse:
        payload: dict = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if system_prompt:
            payload["system"] = system_prompt

        start = time.perf_counter()
        try:
            response = await self._client.post(
                f"{self._base_url}/api/generate",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            latency_ms = (time.perf_counter() - start) * 1000

            return LLMResponse(
                text=data.get("response", "").strip(),
                model=self._model,
                prompt_tokens=data.get("prompt_eval_count", 0),
                completion_tokens=data.get("eval_count", 0),
                latency_ms=latency_ms,
                success=True,
            )
        except httpx.HTTPStatusError as exc:
            logger.error("ollama_http_error", status=exc.response.status_code, error=str(exc))
            return LLMResponse(
                text="",
                model=self._model,
                prompt_tokens=0,
                completion_tokens=0,
                latency_ms=(time.perf_counter() - start) * 1000,
                success=False,
                error=f"HTTP {exc.response.status_code}: {exc.response.text[:200]}",
            )
        except Exception as exc:
            logger.error("ollama_error", error=str(exc))
            return LLMResponse(
                text="",
                model=self._model,
                prompt_tokens=0,
                completion_tokens=0,
                latency_ms=(time.perf_counter() - start) * 1000,
                success=False,
                error=str(exc),
            )

    async def list_models(self) -> list[str]:
        try:
            response = await self._client.get(f"{self._base_url}/api/tags")
            response.raise_for_status()
            return [m["name"] for m in response.json().get("models", [])]
        except Exception:
            return []

    async def close(self) -> None:
        await self._client.aclose()

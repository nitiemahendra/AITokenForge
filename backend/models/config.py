from typing import Dict, Optional
from pydantic import BaseModel, Field


class ModelPricing(BaseModel):
    input_per_1k_tokens: float
    output_per_1k_tokens: float
    context_window: int = 128_000
    provider: str = "unknown"
    display_name: str = ""


# Pricing in USD per 1K tokens — updated April 2026
# Prices marked (est.) are approximate based on public announcements
DEFAULT_PRICING: Dict[str, ModelPricing] = {
    # ── OpenAI ────────────────────────────────────────────────────────────────
    "gpt-5": ModelPricing(
        input_per_1k_tokens=0.002,
        output_per_1k_tokens=0.0125,
        context_window=1_000_000,
        provider="openai",
        display_name="GPT-5",
    ),
    "gpt-4.1": ModelPricing(
        input_per_1k_tokens=0.002,
        output_per_1k_tokens=0.008,
        context_window=1_047_576,
        provider="openai",
        display_name="GPT-4.1",
    ),
    "gpt-4.1-mini": ModelPricing(
        input_per_1k_tokens=0.0004,
        output_per_1k_tokens=0.0016,
        context_window=1_047_576,
        provider="openai",
        display_name="GPT-4.1 Mini",
    ),
    "gpt-4.1-nano": ModelPricing(
        input_per_1k_tokens=0.0001,
        output_per_1k_tokens=0.0004,
        context_window=1_047_576,
        provider="openai",
        display_name="GPT-4.1 Nano",
    ),
    "o3": ModelPricing(
        input_per_1k_tokens=0.010,
        output_per_1k_tokens=0.040,
        context_window=200_000,
        provider="openai",
        display_name="OpenAI o3",
    ),
    "o4-mini": ModelPricing(
        input_per_1k_tokens=0.0011,
        output_per_1k_tokens=0.0044,
        context_window=200_000,
        provider="openai",
        display_name="OpenAI o4-mini",
    ),
    "gpt-4o": ModelPricing(
        input_per_1k_tokens=0.0025,
        output_per_1k_tokens=0.010,
        context_window=128_000,
        provider="openai",
        display_name="GPT-4o",
    ),
    "gpt-4o-mini": ModelPricing(
        input_per_1k_tokens=0.000150,
        output_per_1k_tokens=0.000600,
        context_window=128_000,
        provider="openai",
        display_name="GPT-4o Mini",
    ),
    # ── Anthropic ─────────────────────────────────────────────────────────────
    "claude-opus-4-7": ModelPricing(
        input_per_1k_tokens=0.010,
        output_per_1k_tokens=0.050,
        context_window=200_000,
        provider="anthropic",
        display_name="Claude Opus 4.7",
    ),
    "claude-opus-4-5": ModelPricing(
        input_per_1k_tokens=0.015,
        output_per_1k_tokens=0.075,
        context_window=200_000,
        provider="anthropic",
        display_name="Claude Opus 4",
    ),
    "claude-sonnet-4-5": ModelPricing(
        input_per_1k_tokens=0.003,
        output_per_1k_tokens=0.015,
        context_window=200_000,
        provider="anthropic",
        display_name="Claude Sonnet 4.5",
    ),
    "claude-sonnet-4-6": ModelPricing(
        input_per_1k_tokens=0.003,
        output_per_1k_tokens=0.015,
        context_window=200_000,
        provider="anthropic",
        display_name="Claude Sonnet 4.6",
    ),
    "claude-haiku-4-5": ModelPricing(
        input_per_1k_tokens=0.0008,
        output_per_1k_tokens=0.004,
        context_window=200_000,
        provider="anthropic",
        display_name="Claude Haiku 4.5",
    ),
    # ── Google DeepMind ───────────────────────────────────────────────────────
    "gemini-3-pro": ModelPricing(
        input_per_1k_tokens=0.002,
        output_per_1k_tokens=0.015,
        context_window=2_000_000,
        provider="google",
        display_name="Gemini 3 Pro (est.)",
    ),
    "gemini-2.5-pro": ModelPricing(
        input_per_1k_tokens=0.00125,
        output_per_1k_tokens=0.010,
        context_window=1_048_576,
        provider="google",
        display_name="Gemini 2.5 Pro",
    ),
    "gemini-2.5-flash": ModelPricing(
        input_per_1k_tokens=0.000075,
        output_per_1k_tokens=0.000300,
        context_window=1_048_576,
        provider="google",
        display_name="Gemini 2.5 Flash",
    ),
    "gemini-2.0-flash": ModelPricing(
        input_per_1k_tokens=0.0001,
        output_per_1k_tokens=0.0004,
        context_window=1_048_576,
        provider="google",
        display_name="Gemini 2.0 Flash",
    ),
    # ── xAI ───────────────────────────────────────────────────────────────────
    "grok-3": ModelPricing(
        input_per_1k_tokens=0.003,
        output_per_1k_tokens=0.015,
        context_window=131_072,
        provider="xai",
        display_name="Grok 3",
    ),
    "grok-3-mini": ModelPricing(
        input_per_1k_tokens=0.0003,
        output_per_1k_tokens=0.0005,
        context_window=131_072,
        provider="xai",
        display_name="Grok 3 Mini",
    ),
    # ── DeepSeek ──────────────────────────────────────────────────────────────
    "deepseek-v3": ModelPricing(
        input_per_1k_tokens=0.00027,
        output_per_1k_tokens=0.0011,
        context_window=128_000,
        provider="deepseek",
        display_name="DeepSeek V3",
    ),
    "deepseek-r1": ModelPricing(
        input_per_1k_tokens=0.00055,
        output_per_1k_tokens=0.00219,
        context_window=128_000,
        provider="deepseek",
        display_name="DeepSeek R1",
    ),
    # ── Meta ──────────────────────────────────────────────────────────────────
    "llama-4-maverick": ModelPricing(
        input_per_1k_tokens=0.00022,
        output_per_1k_tokens=0.00088,
        context_window=1_000_000,
        provider="meta",
        display_name="Llama 4 Maverick",
    ),
    "llama-4-scout": ModelPricing(
        input_per_1k_tokens=0.00015,
        output_per_1k_tokens=0.00060,
        context_window=10_000_000,
        provider="meta",
        display_name="Llama 4 Scout",
    ),
    # ── Alibaba ───────────────────────────────────────────────────────────────
    "qwen3-235b": ModelPricing(
        input_per_1k_tokens=0.0006,
        output_per_1k_tokens=0.0024,
        context_window=131_072,
        provider="alibaba",
        display_name="Qwen3 235B",
    ),
    "qwen3-30b": ModelPricing(
        input_per_1k_tokens=0.00015,
        output_per_1k_tokens=0.00060,
        context_window=131_072,
        provider="alibaba",
        display_name="Qwen3 30B",
    ),
    # ── Moonshot AI ───────────────────────────────────────────────────────────
    "kimi-k2": ModelPricing(
        input_per_1k_tokens=0.001,
        output_per_1k_tokens=0.003,
        context_window=131_072,
        provider="moonshot",
        display_name="Kimi K2",
    ),
    "custom": ModelPricing(
        input_per_1k_tokens=0.001,
        output_per_1k_tokens=0.002,
        context_window=4_096,
        provider="custom",
        display_name="Custom Model",
    ),
}


class AppConfig(BaseModel):
    app_name: str = "TokenForge"
    version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    cors_origins: list = Field(default_factory=lambda: ["http://localhost:5173", "http://localhost:3000"])

    # LLM Adapter
    llm_adapter: str = "ollama"  # ollama | gemma | mock
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma4:latest"
    ollama_timeout: int = 120
    gemma_model_path: Optional[str] = None

    # Embedding
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_device: str = "cpu"  # cpu | cuda | mps

    # Optimization defaults
    default_mode: str = "balanced"
    max_prompt_length: int = 100_000
    semantic_similarity_threshold: float = 0.85

    # Rate limiting
    rate_limit_requests: int = 60
    rate_limit_window: int = 60  # seconds

    # Pricing overrides (optional)
    custom_pricing: Optional[Dict[str, ModelPricing]] = None

    @property
    def effective_pricing(self) -> Dict[str, ModelPricing]:
        pricing = dict(DEFAULT_PRICING)
        if self.custom_pricing:
            pricing.update(self.custom_pricing)
        return pricing

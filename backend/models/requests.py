from enum import Enum

from pydantic import BaseModel, Field, field_validator


class OptimizationMode(str, Enum):
    SAFE = "safe"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"


class TargetModel(str, Enum):
    # OpenAI
    GPT_5 = "gpt-5"
    GPT_41 = "gpt-4.1"
    GPT_41_MINI = "gpt-4.1-mini"
    GPT_41_NANO = "gpt-4.1-nano"
    O3 = "o3"
    O4_MINI = "o4-mini"
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    # Anthropic
    CLAUDE_OPUS_47 = "claude-opus-4-7"
    CLAUDE_OPUS_4 = "claude-opus-4-5"
    CLAUDE_SONNET_45 = "claude-sonnet-4-5"
    CLAUDE_SONNET_46 = "claude-sonnet-4-6"
    CLAUDE_HAIKU_45 = "claude-haiku-4-5"
    # Google
    GEMINI_3_PRO = "gemini-3-pro"
    GEMINI_25_PRO = "gemini-2.5-pro"
    GEMINI_25_FLASH = "gemini-2.5-flash"
    GEMINI_20_FLASH = "gemini-2.0-flash"
    # xAI
    GROK_3 = "grok-3"
    GROK_3_MINI = "grok-3-mini"
    # DeepSeek
    DEEPSEEK_V3 = "deepseek-v3"
    DEEPSEEK_R1 = "deepseek-r1"
    # Meta
    LLAMA_4_MAVERICK = "llama-4-maverick"
    LLAMA_4_SCOUT = "llama-4-scout"
    # Alibaba
    QWEN3_235B = "qwen3-235b"
    QWEN3_30B = "qwen3-30b"
    # Moonshot
    KIMI_K2 = "kimi-k2"
    CUSTOM = "custom"


class OptimizeRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=100_000, description="The prompt to optimize")
    mode: OptimizationMode = Field(default=OptimizationMode.BALANCED, description="Optimization aggressiveness")
    target_model: TargetModel = Field(default=TargetModel.GPT_4O, description="Target LLM for cost estimation")
    preserve_formatting: bool = Field(default=True, description="Preserve markdown/code block formatting")
    preserve_constraints: bool = Field(default=True, description="Preserve explicit constraints and rules")
    max_compression_ratio: float | None = Field(default=None, ge=0.1, le=0.99, description="Cap compression ratio")
    context: str | None = Field(default=None, max_length=10_000, description="Additional context for optimization")

    @field_validator("prompt")
    @classmethod
    def strip_prompt(cls, v: str) -> str:
        return v.strip()


class AnalyzeRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=100_000, description="The prompt to analyze")
    target_model: TargetModel = Field(default=TargetModel.GPT_4O, description="Target LLM for token counting")
    include_breakdown: bool = Field(default=False, description="Include per-segment token breakdown")

    @field_validator("prompt")
    @classmethod
    def strip_prompt(cls, v: str) -> str:
        return v.strip()

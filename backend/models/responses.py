from typing import Any

from pydantic import BaseModel, Field


class TokenBreakdown(BaseModel):
    segment: str
    token_count: int
    type: str  # "instruction", "context", "example", "constraint"


class TokenAnalysis(BaseModel):
    token_count: int
    estimated_output_tokens: int
    total_estimated_tokens: int
    tokenizer_used: str
    breakdown: list[TokenBreakdown] | None = None


class CostEstimate(BaseModel):
    input_cost: float
    estimated_output_cost: float
    total_cost: float
    currency: str = "USD"
    model: str
    pricing_per_1k_input: float
    pricing_per_1k_output: float


class SemanticResult(BaseModel):
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    risk_level: str
    embedding_model: str
    confidence: float = Field(..., ge=0.0, le=1.0)


class OptimizeResponse(BaseModel):
    request_id: str
    original_prompt: str
    optimized_prompt: str
    original_tokens: int
    optimized_tokens: int
    token_reduction_percent: float
    semantic_similarity: float
    risk_level: str
    estimated_cost_before: float
    estimated_cost_after: float
    cost_savings_percent: float
    optimization_mode: str
    target_model: str
    processing_time_ms: float
    llm_adapter_used: str
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AnalyzeResponse(BaseModel):
    request_id: str
    prompt: str
    token_analysis: TokenAnalysis
    cost_estimate: CostEstimate
    processing_time_ms: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    status: str
    version: str
    llm_adapter: str
    llm_available: bool
    embedding_model: str
    embedding_available: bool
    uptime_seconds: float
    models_loaded: list[str]


class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str
    context_window: int
    pricing_input_per_1k: float
    pricing_output_per_1k: float
    supports_optimization: bool


class ModelsResponse(BaseModel):
    models: list[ModelInfo]
    llm_adapters: list[str]
    optimization_modes: list[str]

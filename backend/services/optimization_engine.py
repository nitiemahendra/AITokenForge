import re
import time
import uuid
from typing import Optional

from ..models.requests import OptimizeRequest, OptimizationMode, TargetModel
from ..models.responses import OptimizeResponse
from ..utils.logger import get_logger
from ..utils.sanitizer import sanitize_prompt, sanitize_for_log
from ..utils.validators import validate_compression_ratio
from .llm_adapters.base import LLMAdapter
from .token_analyzer import TokenAnalyzer
from .semantic_engine import SemanticEngine
from .cost_estimator import CostEstimator

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# System prompts per optimization mode
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT_SAFE = """You are an expert prompt engineer specializing in minimal, high-fidelity compression.
Your task is to compress the given prompt while:
- Preserving ALL semantic meaning, intent, and constraints
- Keeping every explicit rule, formatting requirement, and output specification
- Only removing obvious redundancy and filler phrases
- Maintaining the original tone and register
Return ONLY the compressed prompt. No explanations, no preamble, no markdown wrapping."""

_SYSTEM_PROMPT_BALANCED = """You are an expert prompt engineer specializing in token-efficient prompt compression.
Your task is to significantly compress the given prompt while:
- Preserving core semantic meaning and primary intent
- Keeping critical constraints and output requirements
- Removing redundancy, verbose phrasing, and unnecessary context
- Converting long explanations to concise directives
- Merging duplicate instructions
Return ONLY the compressed prompt. No explanations, no preamble, no markdown wrapping."""

_SYSTEM_PROMPT_AGGRESSIVE = """You are an expert prompt engineer specializing in maximum token reduction.
Your task is to aggressively compress the given prompt to its absolute minimum while:
- Preserving the primary task and non-negotiable output format
- Converting everything to ultra-compact directives
- Eliminating all context, examples, and explanatory text not strictly required
- Using abbreviations and shorthand where unambiguous
Return ONLY the compressed prompt. No explanations, no preamble, no markdown wrapping."""

_SYSTEM_PROMPTS = {
    OptimizationMode.SAFE: _SYSTEM_PROMPT_SAFE,
    OptimizationMode.BALANCED: _SYSTEM_PROMPT_BALANCED,
    OptimizationMode.AGGRESSIVE: _SYSTEM_PROMPT_AGGRESSIVE,
}

_TEMPERATURE_MAP = {
    OptimizationMode.SAFE: 0.05,
    OptimizationMode.BALANCED: 0.1,
    OptimizationMode.AGGRESSIVE: 0.15,
}


def _build_optimization_prompt(request: OptimizeRequest) -> str:
    mode_notes = {
        OptimizationMode.SAFE: "Apply MINIMAL compression. Preserve all formatting.",
        OptimizationMode.BALANCED: "Apply MODERATE compression. Keep key formatting.",
        OptimizationMode.AGGRESSIVE: "Apply MAXIMUM compression. Strip all non-essential text.",
    }
    formatting_note = "IMPORTANT: Preserve all code blocks, markdown, and formatting." if request.preserve_formatting else ""
    constraints_note = "IMPORTANT: Preserve all explicit rules, constraints, and requirements." if request.preserve_constraints else ""
    context_section = f"\nADDITIONAL CONTEXT:\n{request.context}\n" if request.context else ""

    return f"""OPTIMIZATION MODE: {request.mode.value.upper()}
{mode_notes[request.mode]}
{formatting_note}
{constraints_note}
TARGET MODEL: {request.target_model.value}
{context_section}
---
ORIGINAL PROMPT:
{request.prompt}
---
COMPRESSED PROMPT:"""


class OptimizationEngine:
    """
    Orchestrates the full prompt optimization pipeline:
    analyze → compress via LLM → score semantics → estimate costs → return results.
    """

    def __init__(
        self,
        llm_adapter: LLMAdapter,
        token_analyzer: TokenAnalyzer,
        semantic_engine: SemanticEngine,
        cost_estimator: CostEstimator,
    ):
        self._llm = llm_adapter
        self._token_analyzer = token_analyzer
        self._semantic = semantic_engine
        self._cost = cost_estimator

    async def optimize(self, request: OptimizeRequest) -> OptimizeResponse:
        request_id = str(uuid.uuid4())
        start_time = time.perf_counter()

        logger.info(
            "optimize_start",
            request_id=request_id,
            mode=request.mode.value,
            target_model=request.target_model.value,
            prompt_preview=sanitize_for_log(request.prompt),
        )

        # --- 1. Analyze original ---
        original_analysis = self._token_analyzer.analyze(request.prompt, request.target_model)
        original_cost = self._cost.estimate(
            original_analysis.token_count,
            original_analysis.estimated_output_tokens,
            request.target_model,
        )

        # --- 2. LLM compression ---
        llm_prompt = _build_optimization_prompt(request)
        system_prompt = _SYSTEM_PROMPTS[request.mode]
        temperature = _TEMPERATURE_MAP[request.mode]

        llm_response = await self._llm.generate(
            prompt=llm_prompt,
            system_prompt=system_prompt,
            max_tokens=max(512, original_analysis.token_count),
            temperature=temperature,
        )

        if not llm_response.success or not llm_response.text.strip():
            logger.error("llm_optimization_failed", request_id=request_id, error=llm_response.error)
            # Return original prompt with a warning
            optimized_prompt = request.prompt
            warnings = [f"LLM optimization failed: {llm_response.error}. Returning original prompt."]
        else:
            optimized_prompt = sanitize_prompt(llm_response.text.strip())
            warnings = []

        # Enforce max compression ratio if specified
        if request.max_compression_ratio is not None:
            original_len = len(request.prompt.split())
            optimized_len = len(optimized_prompt.split())
            min_len = int(original_len * (1 - request.max_compression_ratio))
            if optimized_len < min_len:
                # Revert to original; the LLM over-compressed
                optimized_prompt = request.prompt
                warnings.append(
                    f"Optimization exceeded max_compression_ratio={request.max_compression_ratio}. Original returned."
                )

        # --- 3. Analyze optimized ---
        optimized_analysis = self._token_analyzer.analyze(optimized_prompt, request.target_model)
        optimized_cost = self._cost.estimate(
            optimized_analysis.token_count,
            optimized_analysis.estimated_output_tokens,
            request.target_model,
        )

        # --- 4. Semantic similarity ---
        semantic_result = self._semantic.compute_similarity(request.prompt, optimized_prompt)

        # --- 5. Aggregate warnings ---
        ratio_warnings = validate_compression_ratio(
            original_analysis.token_count, optimized_analysis.token_count
        )
        warnings.extend(ratio_warnings)

        if semantic_result.risk_level == "high":
            warnings.append(
                f"Semantic similarity is low ({semantic_result.similarity_score:.2f}). "
                "Review the optimized prompt carefully before use."
            )

        token_reduction = (
            (1 - optimized_analysis.token_count / original_analysis.token_count) * 100
            if original_analysis.token_count > 0
            else 0.0
        )
        cost_savings = self._cost.savings_percent(original_cost.total_cost, optimized_cost.total_cost)
        processing_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            "optimize_complete",
            request_id=request_id,
            original_tokens=original_analysis.token_count,
            optimized_tokens=optimized_analysis.token_count,
            token_reduction_pct=round(token_reduction, 1),
            semantic_similarity=semantic_result.similarity_score,
            cost_savings_pct=cost_savings,
            latency_ms=round(processing_ms, 1),
        )

        return OptimizeResponse(
            request_id=request_id,
            original_prompt=request.prompt,
            optimized_prompt=optimized_prompt,
            original_tokens=original_analysis.token_count,
            optimized_tokens=optimized_analysis.token_count,
            token_reduction_percent=round(token_reduction, 2),
            semantic_similarity=semantic_result.similarity_score,
            risk_level=semantic_result.risk_level,
            estimated_cost_before=original_cost.total_cost,
            estimated_cost_after=optimized_cost.total_cost,
            cost_savings_percent=cost_savings,
            optimization_mode=request.mode.value,
            target_model=request.target_model.value,
            processing_time_ms=round(processing_ms, 1),
            llm_adapter_used=self._llm.adapter_name(),
            warnings=warnings,
            metadata={
                "original_cost_breakdown": original_cost.model_dump(),
                "optimized_cost_breakdown": optimized_cost.model_dump(),
                "semantic_confidence": semantic_result.confidence,
                "embedding_model": semantic_result.embedding_model,
                "llm_model": self._llm.model_name(),
                "llm_latency_ms": round(llm_response.latency_ms, 1),
            },
        )

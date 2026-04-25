from typing import Optional
import tiktoken

from ..models.requests import TargetModel
from ..models.responses import TokenAnalysis, TokenBreakdown
from ..utils.logger import get_logger

logger = get_logger(__name__)

# Map target models to their tiktoken encoding
# OpenAI GPT-4o family uses o200k_base; everything else approximates with cl100k_base
_ENCODING_MAP = {
    TargetModel.GPT_5: "o200k_base",
    TargetModel.GPT_41: "o200k_base",
    TargetModel.GPT_41_MINI: "o200k_base",
    TargetModel.GPT_41_NANO: "o200k_base",
    TargetModel.O3: "o200k_base",
    TargetModel.O4_MINI: "o200k_base",
    TargetModel.GPT_4O: "o200k_base",
    TargetModel.GPT_4O_MINI: "o200k_base",
}

# Estimated output-to-input token ratio by model family
_OUTPUT_RATIO_MAP = {
    "gpt": 0.6,
    "o3": 0.8,
    "o4": 0.8,
    "claude": 0.55,
    "gemini": 0.65,
    "grok": 0.6,
    "deepseek": 0.7,
    "llama": 0.6,
    "qwen": 0.6,
    "kimi": 0.65,
    "custom": 0.5,
}

_ENCODING_CACHE: dict[str, tiktoken.Encoding] = {}


def _get_encoding(encoding_name: str) -> tiktoken.Encoding:
    if encoding_name not in _ENCODING_CACHE:
        _ENCODING_CACHE[encoding_name] = tiktoken.get_encoding(encoding_name)
    return _ENCODING_CACHE[encoding_name]


class TokenAnalyzer:
    """
    Counts tokens for a given prompt using the appropriate tokenizer
    for the target model. Falls back gracefully if tiktoken is unavailable
    for a given model.
    """

    def count_tokens(self, text: str, target_model: TargetModel) -> int:
        encoding_name = _ENCODING_MAP.get(target_model, "cl100k_base")
        try:
            enc = _get_encoding(encoding_name)
            return len(enc.encode(text))
        except Exception as exc:
            logger.warning("tiktoken_fallback", model=target_model, error=str(exc))
            # Whitespace-split word count approximation (avg ~1.3 tokens/word)
            return int(len(text.split()) * 1.3)

    def _estimate_output_tokens(self, input_tokens: int, target_model: TargetModel) -> int:
        model_str = target_model.value.lower()
        for family, ratio in _OUTPUT_RATIO_MAP.items():
            if family in model_str:
                return int(input_tokens * ratio)
        return int(input_tokens * 0.6)

    def analyze(
        self,
        prompt: str,
        target_model: TargetModel,
        include_breakdown: bool = False,
    ) -> TokenAnalysis:
        encoding_name = _ENCODING_MAP.get(target_model, "cl100k_base")
        input_count = self.count_tokens(prompt, target_model)
        output_estimate = self._estimate_output_tokens(input_count, target_model)

        breakdown: Optional[list[TokenBreakdown]] = None
        if include_breakdown:
            breakdown = self._build_breakdown(prompt, target_model)

        return TokenAnalysis(
            token_count=input_count,
            estimated_output_tokens=output_estimate,
            total_estimated_tokens=input_count + output_estimate,
            tokenizer_used=encoding_name,
            breakdown=breakdown,
        )

    def _build_breakdown(self, prompt: str, target_model: TargetModel) -> list[TokenBreakdown]:
        """Segment the prompt heuristically and count tokens per segment."""
        segments = []
        lines = prompt.split("\n")
        current_segment: list[str] = []
        current_type = "content"

        for line in lines:
            line_lower = line.lower().strip()
            if any(kw in line_lower for kw in ["system:", "instruction:", "you are", "your role"]):
                if current_segment:
                    segments.append(("\n".join(current_segment), current_type))
                current_segment = [line]
                current_type = "instruction"
            elif any(kw in line_lower for kw in ["example:", "for example", "e.g."]):
                if current_segment:
                    segments.append(("\n".join(current_segment), current_type))
                current_segment = [line]
                current_type = "example"
            elif any(kw in line_lower for kw in ["constraint:", "rule:", "must", "never", "always"]):
                if current_segment:
                    segments.append(("\n".join(current_segment), current_type))
                current_segment = [line]
                current_type = "constraint"
            else:
                current_segment.append(line)

        if current_segment:
            segments.append(("\n".join(current_segment), current_type))

        return [
            TokenBreakdown(
                segment=seg[:100] + ("…" if len(seg) > 100 else ""),
                token_count=self.count_tokens(seg, target_model),
                type=seg_type,
            )
            for seg, seg_type in segments
            if seg.strip()
        ]

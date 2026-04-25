from ..models.config import DEFAULT_PRICING, ModelPricing
from ..models.requests import TargetModel
from ..models.responses import CostEstimate
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CostEstimator:
    """
    Estimates API cost for a given token count and target model.
    Pricing is configurable via constructor injection.
    """

    def __init__(self, pricing_overrides: dict[str, ModelPricing] | None = None):
        self._pricing = dict(DEFAULT_PRICING)
        if pricing_overrides:
            self._pricing.update(pricing_overrides)

    def estimate(
        self,
        input_tokens: int,
        estimated_output_tokens: int,
        target_model: TargetModel,
    ) -> CostEstimate:
        pricing = self._pricing.get(target_model.value)
        if pricing is None:
            logger.warning("unknown_model_pricing", model=target_model.value, fallback="custom")
            pricing = self._pricing["custom"]

        input_cost = (input_tokens / 1000) * pricing.input_per_1k_tokens
        output_cost = (estimated_output_tokens / 1000) * pricing.output_per_1k_tokens
        total = input_cost + output_cost

        return CostEstimate(
            input_cost=round(input_cost, 6),
            estimated_output_cost=round(output_cost, 6),
            total_cost=round(total, 6),
            model=target_model.value,
            pricing_per_1k_input=pricing.input_per_1k_tokens,
            pricing_per_1k_output=pricing.output_per_1k_tokens,
        )

    def savings_percent(self, original_cost: float, optimized_cost: float) -> float:
        if original_cost <= 0:
            return 0.0
        return round((1 - optimized_cost / original_cost) * 100, 2)

    def update_pricing(self, model: str, pricing: ModelPricing) -> None:
        self._pricing[model] = pricing
        logger.info("pricing_updated", model=model)

from fastapi import APIRouter, Depends

from ...models.responses import ModelsResponse, ModelInfo
from ...models.requests import OptimizationMode
from ..dependencies import get_app_state

router = APIRouter(tags=["models"])


@router.get(
    "/models",
    response_model=ModelsResponse,
    summary="List supported models and adapters",
    description="Returns all supported target models with pricing and available LLM adapters.",
)
async def list_models(app_state=Depends(get_app_state)) -> ModelsResponse:
    pricing = app_state["config"].effective_pricing

    model_list = [
        ModelInfo(
            id=model_id,
            name=p.display_name or model_id,
            provider=p.provider,
            context_window=p.context_window,
            pricing_input_per_1k=p.input_per_1k_tokens,
            pricing_output_per_1k=p.output_per_1k_tokens,
            supports_optimization=True,
        )
        for model_id, p in pricing.items()
    ]

    return ModelsResponse(
        models=model_list,
        llm_adapters=["ollama", "mock"],
        optimization_modes=[m.value for m in OptimizationMode],
    )


import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, status

from ...models.requests import OptimizeRequest
from ...models.responses import OptimizeResponse
from ...utils.sanitizer import sanitize_prompt
from ..dependencies import get_optimization_engine

router = APIRouter(prefix="/optimize", tags=["optimization"])
logger = structlog.get_logger(__name__)


@router.post(
    "",
    response_model=OptimizeResponse,
    summary="Optimize a prompt for token reduction",
    description=(
        "Analyzes the input prompt, uses a local LLM to compress it, "
        "scores semantic preservation, and returns cost savings estimates."
    ),
)
async def optimize_prompt(
    request: OptimizeRequest,
    http_request: Request,
    engine=Depends(get_optimization_engine),
) -> OptimizeResponse:
    structlog.contextvars.bind_contextvars(
        client_ip=http_request.client.host if http_request.client else "unknown",
    )

    request.prompt = sanitize_prompt(request.prompt)
    if not request.prompt:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Prompt is empty after sanitization.",
        )

    try:
        return await engine.optimize(request)
    except Exception as exc:
        logger.error("optimize_endpoint_error", error=str(exc), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Optimization failed. Check server logs for details.",
        ) from exc

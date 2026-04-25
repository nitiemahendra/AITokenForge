import uuid
import time
from fastapi import APIRouter, Depends, HTTPException, Request, status
import structlog

from ...models.requests import AnalyzeRequest
from ...models.responses import AnalyzeResponse
from ...utils.sanitizer import sanitize_prompt
from ..dependencies import get_token_analyzer, get_cost_estimator

router = APIRouter(prefix="/analyze", tags=["analysis"])
logger = structlog.get_logger(__name__)


@router.post(
    "",
    response_model=AnalyzeResponse,
    summary="Analyze token count and cost for a prompt",
    description="Returns token breakdown, estimated output tokens, and cost estimate without optimization.",
)
async def analyze_prompt(
    request: AnalyzeRequest,
    http_request: Request,
    token_analyzer=Depends(get_token_analyzer),
    cost_estimator=Depends(get_cost_estimator),
) -> AnalyzeResponse:
    start_time = time.perf_counter()
    request_id = str(uuid.uuid4())

    request.prompt = sanitize_prompt(request.prompt)
    if not request.prompt:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Prompt is empty after sanitization.",
        )

    try:
        analysis = token_analyzer.analyze(
            request.prompt,
            request.target_model,
            include_breakdown=request.include_breakdown,
        )
        cost = cost_estimator.estimate(
            analysis.token_count,
            analysis.estimated_output_tokens,
            request.target_model,
        )
        processing_ms = (time.perf_counter() - start_time) * 1000

        return AnalyzeResponse(
            request_id=request_id,
            prompt=request.prompt,
            token_analysis=analysis,
            cost_estimate=cost,
            processing_time_ms=round(processing_ms, 1),
            metadata={"target_model": request.target_model.value},
        )
    except Exception as exc:
        logger.error("analyze_endpoint_error", error=str(exc), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analysis failed. Check server logs for details.",
        ) from exc

import asyncio
import os
import sys
import time
from fastapi import APIRouter, Depends

from ...models.responses import HealthResponse
from ..dependencies import get_app_state

router = APIRouter(tags=["system"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns the operational status of all system components.",
)
async def health_check(app_state=Depends(get_app_state)) -> HealthResponse:
    llm_available = await app_state["llm_adapter"].is_available()
    uptime = time.time() - app_state["start_time"]

    return HealthResponse(
        status="healthy" if llm_available else "degraded",
        version=app_state["config"].version,
        llm_adapter=app_state["llm_adapter"].adapter_name(),
        llm_available=llm_available,
        embedding_model=app_state["semantic_engine"].embedding_model_name,
        embedding_available=app_state["semantic_engine"].is_available,
        uptime_seconds=round(uptime, 1),
        models_loaded=list(app_state["config"].effective_pricing.keys()),
    )


@router.post("/api/v1/admin/restart", summary="Restart server")
async def restart_server():
    async def _do_restart():
        await asyncio.sleep(0.6)
        os.execv(sys.executable, [sys.executable] + sys.argv)

    asyncio.create_task(_do_restart())
    return {"status": "restarting", "message": "Server restarting in ~1 second"}

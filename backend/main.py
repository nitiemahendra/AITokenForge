import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .utils.logger import setup_logging, get_logger
from .models.config import AppConfig
from .services.llm_adapters.ollama_adapter import OllamaAdapter
from .services.llm_adapters.mock_adapter import MockAdapter
from .services.token_analyzer import TokenAnalyzer
from .services.semantic_engine import SemanticEngine
from .services.cost_estimator import CostEstimator
from .services.optimization_engine import OptimizationEngine
from .api.middleware.logging import RequestLoggingMiddleware
from .api.middleware.rate_limit import RateLimitMiddleware
from .api.routes import optimize_router, analyze_router, health_router, models_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(settings.log_level, settings.json_logs)

    logger.info("tokenforge_starting", version=settings.version, adapter=settings.llm_adapter)

    # --- Build LLM adapter ---
    if settings.llm_adapter == "ollama":
        llm_adapter = OllamaAdapter(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            timeout=settings.ollama_timeout,
        )
    else:
        logger.warning("using_mock_adapter", reason="llm_adapter setting is not 'ollama'")
        llm_adapter = MockAdapter()

    # --- Build services ---
    token_analyzer = TokenAnalyzer()
    semantic_engine = SemanticEngine(
        model_name=settings.embedding_model,
        device=settings.embedding_device,
    )
    cost_estimator = CostEstimator()
    optimization_engine = OptimizationEngine(
        llm_adapter=llm_adapter,
        token_analyzer=token_analyzer,
        semantic_engine=semantic_engine,
        cost_estimator=cost_estimator,
    )

    config = AppConfig(
        llm_adapter=settings.llm_adapter,
        ollama_base_url=settings.ollama_base_url,
        ollama_model=settings.ollama_model,
        embedding_model=settings.embedding_model,
    )

    app.state.app_state = {
        "config": config,
        "llm_adapter": llm_adapter,
        "token_analyzer": token_analyzer,
        "semantic_engine": semantic_engine,
        "cost_estimator": cost_estimator,
        "optimization_engine": optimization_engine,
        "start_time": time.time(),
    }

    logger.info("tokenforge_ready", embedding_available=semantic_engine.is_available)
    yield

    # --- Shutdown ---
    if hasattr(llm_adapter, "close"):
        await llm_adapter.close()
    logger.info("tokenforge_shutdown")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="TokenForge API",
        description=(
            "AI Cost Optimization Infrastructure — reduce LLM token usage "
            "while preserving semantic intent."
        ),
        version=settings.version,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # --- Middleware (order matters: outer to inner) ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RateLimitMiddleware, max_requests=settings.rate_limit_requests, window_seconds=settings.rate_limit_window)
    app.add_middleware(RequestLoggingMiddleware)

    # --- Routes ---
    app.include_router(health_router)
    app.include_router(models_router)
    app.include_router(optimize_router, prefix="/api/v1")
    app.include_router(analyze_router, prefix="/api/v1")

    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error("unhandled_exception", error=str(exc), path=str(request.url), exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred."},
        )

    return app


app = create_app()

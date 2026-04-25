from .analyze import router as analyze_router
from .health import router as health_router
from .models import router as models_router
from .optimize import router as optimize_router

__all__ = ["optimize_router", "analyze_router", "health_router", "models_router"]

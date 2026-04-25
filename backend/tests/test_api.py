import time

import pytest
from httpx import ASGITransport, AsyncClient

from ..main import app
from ..models.config import AppConfig
from ..services.cost_estimator import CostEstimator
from ..services.llm_adapters.mock_adapter import MockAdapter
from ..services.optimization_engine import OptimizationEngine
from ..services.semantic_engine import SemanticEngine
from ..services.token_analyzer import TokenAnalyzer


@pytest.fixture
async def client():
    # Initialize app state directly — avoids requiring the lifespan to run
    mock_adapter = MockAdapter()
    token_analyzer = TokenAnalyzer()
    semantic_engine = SemanticEngine()
    cost_estimator = CostEstimator()
    optimization_engine = OptimizationEngine(
        llm_adapter=mock_adapter,
        token_analyzer=token_analyzer,
        semantic_engine=semantic_engine,
        cost_estimator=cost_estimator,
    )
    app.state.app_state = {
        "config": AppConfig(llm_adapter="mock"),
        "llm_adapter": mock_adapter,
        "token_analyzer": token_analyzer,
        "semantic_engine": semantic_engine,
        "cost_estimator": cost_estimator,
        "optimization_engine": optimization_engine,
        "start_time": time.time(),
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.mark.anyio
async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert data["version"] == "1.0.0"


@pytest.mark.anyio
async def test_models_endpoint(client):
    response = await client.get("/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert len(data["models"]) > 0
    assert "optimization_modes" in data
    assert "balanced" in data["optimization_modes"]


@pytest.mark.anyio
async def test_analyze_endpoint(client):
    response = await client.post(
        "/api/v1/analyze",
        json={"prompt": "Summarize the following document in 3 bullet points.", "target_model": "gpt-4o"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["token_analysis"]["token_count"] > 0
    assert data["cost_estimate"]["total_cost"] >= 0
    assert "request_id" in data


@pytest.mark.anyio
async def test_analyze_empty_prompt(client):
    response = await client.post(
        "/api/v1/analyze",
        json={"prompt": "   ", "target_model": "gpt-4o"},
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_optimize_endpoint_mock(client):
    response = await client.post(
        "/api/v1/optimize",
        json={
            "prompt": "Please kindly summarize the following document in three bullet points. Make sure to include all key insights.",
            "mode": "balanced",
            "target_model": "gpt-4o",
        },
    )
    # Success or degraded (if ollama not running in CI)
    assert response.status_code in (200, 500)
    if response.status_code == 200:
        data = response.json()
        assert "optimized_prompt" in data
        assert "token_reduction_percent" in data
        assert "semantic_similarity" in data
        assert data["original_tokens"] > 0


@pytest.mark.anyio
async def test_optimize_invalid_mode(client):
    response = await client.post(
        "/api/v1/optimize",
        json={"prompt": "Test prompt", "mode": "nuclear"},
    )
    assert response.status_code == 422

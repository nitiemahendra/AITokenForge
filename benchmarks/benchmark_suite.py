"""
TokenForge Benchmark Suite

Measures:
  - Token counting throughput (prompts/sec)
  - Semantic similarity latency
  - End-to-end optimization latency (requires running Ollama)
  - Cost estimation throughput

Run:  python -m benchmarks.benchmark_suite
"""

import asyncio
import time
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.token_analyzer import TokenAnalyzer
from backend.services.semantic_engine import SemanticEngine
from backend.services.cost_estimator import CostEstimator
from backend.models.requests import TargetModel, OptimizationMode, OptimizeRequest
from backend.services.llm_adapters.mock_adapter import MockAdapter
from backend.services.optimization_engine import OptimizationEngine

SAMPLE_PROMPTS = [
    "Summarize the document.",
    "You are a helpful assistant. Please kindly analyze the following customer feedback and identify the top three themes. Make sure to be thorough and comprehensive in your analysis.",
    "System: You are an expert data scientist with 10 years of experience in machine learning.\n\nTask: Given the dataset below, perform exploratory data analysis. Include: 1) Summary statistics, 2) Missing value analysis, 3) Correlation analysis, 4) Key insights.\n\nConstraints: Use Python code. Format output as JSON. Include confidence intervals.\n\nDataset: [provided below]",
    " ".join(["Please analyze the following text and provide detailed insights about its semantic content, key themes, and underlying patterns."] * 10),
]


def benchmark_token_counting(n: int = 1000) -> None:
    analyzer = TokenAnalyzer()
    prompt = SAMPLE_PROMPTS[2]
    start = time.perf_counter()
    for _ in range(n):
        analyzer.count_tokens(prompt, TargetModel.GPT_4O)
    elapsed = time.perf_counter() - start
    print(f"Token counting:    {n / elapsed:.0f} prompts/sec  ({elapsed * 1000 / n:.2f} ms/call)")


def benchmark_semantic_similarity(n: int = 100) -> None:
    engine = SemanticEngine()
    a = SAMPLE_PROMPTS[2]
    b = SAMPLE_PROMPTS[1]
    latencies = []
    for _ in range(n):
        start = time.perf_counter()
        engine.compute_similarity(a, b)
        latencies.append((time.perf_counter() - start) * 1000)
    print(
        f"Semantic similarity: p50={statistics.median(latencies):.1f}ms  "
        f"p95={sorted(latencies)[int(n * 0.95)]:.1f}ms  "
        f"({n} iterations)"
    )


def benchmark_cost_estimation(n: int = 10_000) -> None:
    estimator = CostEstimator()
    start = time.perf_counter()
    for _ in range(n):
        estimator.estimate(1200, 600, TargetModel.GPT_4O)
    elapsed = time.perf_counter() - start
    print(f"Cost estimation:   {n / elapsed:.0f} calls/sec  ({elapsed * 1000 / n:.3f} ms/call)")


async def benchmark_optimization_mock(n: int = 20) -> None:
    adapter = MockAdapter()
    analyzer = TokenAnalyzer()
    semantic = SemanticEngine()
    estimator = CostEstimator()
    engine = OptimizationEngine(adapter, analyzer, semantic, estimator)

    latencies = []
    for prompt in (SAMPLE_PROMPTS * (n // len(SAMPLE_PROMPTS) + 1))[:n]:
        req = OptimizeRequest(prompt=prompt, mode=OptimizationMode.BALANCED, target_model=TargetModel.GPT_4O)
        start = time.perf_counter()
        await engine.optimize(req)
        latencies.append((time.perf_counter() - start) * 1000)

    print(
        f"E2E optimization (mock): p50={statistics.median(latencies):.1f}ms  "
        f"p95={sorted(latencies)[int(n * 0.95)]:.1f}ms  "
        f"({n} iterations)"
    )


if __name__ == "__main__":
    print("\n=== TokenForge Benchmark Suite ===\n")
    benchmark_token_counting()
    benchmark_semantic_similarity()
    benchmark_cost_estimation()
    asyncio.run(benchmark_optimization_mock())
    print("\nDone.\n")

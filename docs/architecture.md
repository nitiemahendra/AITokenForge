# TokenForge Architecture

## Design Principles

1. **Local-first** — All processing happens on your machine. No data leaves your environment.
2. **Adapter pattern** — LLM backends are swappable. Replace Ollama with llama.cpp or vLLM with a single config change.
3. **Graceful degradation** — If sentence-transformers isn't installed, falls back to Jaccard similarity. If Ollama is down, returns clear errors.
4. **Typed everywhere** — Pydantic models on all API boundaries. TypeScript types synchronized with backend schemas.

## Request Lifecycle

```
Client
  │
  │  POST /api/v1/optimize
  ▼
RateLimitMiddleware          ← sliding window, per-IP
  │
RequestLoggingMiddleware     ← structured logs, request ID injection
  │
CORSMiddleware
  │
  ▼
optimize_prompt (route)
  │  sanitize_prompt()       ← strip control chars, null bytes
  │
  ▼
OptimizationEngine.optimize()
  ├── TokenAnalyzer.analyze()          → tiktoken count on original
  ├── CostEstimator.estimate()         → original cost
  │
  ├── _build_optimization_prompt()     → constructs LLM instruction
  ├── LLMAdapter.generate()            → Ollama / Gemma inference
  │
  ├── TokenAnalyzer.analyze()          → tiktoken count on optimized
  ├── CostEstimator.estimate()         → optimized cost
  │
  ├── SemanticEngine.compute_similarity()  → cosine (sentence-transformers)
  │                                         or Jaccard (fallback)
  │
  └── OptimizeResponse                 → assembled, typed, returned
```

## Module Map

```
backend/
├── main.py              Application factory + lifespan wiring
├── config.py            Pydantic-settings from .env
│
├── api/
│   ├── routes/          One file per endpoint group
│   │   ├── optimize.py  POST /api/v1/optimize
│   │   ├── analyze.py   POST /api/v1/analyze
│   │   ├── health.py    GET  /health
│   │   └── models.py    GET  /models
│   ├── middleware/
│   │   ├── logging.py   Structured request/response logging
│   │   └── rate_limit.py Sliding window rate limiter
│   └── dependencies.py  FastAPI dependency injection helpers
│
├── services/
│   ├── optimization_engine.py  Orchestration — the core pipeline
│   ├── token_analyzer.py       tiktoken wrapper + breakdown
│   ├── semantic_engine.py      sentence-transformers + Jaccard fallback
│   ├── cost_estimator.py       Pricing table lookup
│   └── llm_adapters/
│       ├── base.py             Abstract LLMAdapter interface
│       ├── ollama_adapter.py   Ollama HTTP client
│       └── mock_adapter.py     Deterministic test adapter
│
├── models/
│   ├── requests.py      OptimizeRequest, AnalyzeRequest + enums
│   ├── responses.py     All response schemas
│   └── config.py        AppConfig, ModelPricing, DEFAULT_PRICING
│
└── utils/
    ├── logger.py        structlog setup with console/JSON rendering
    ├── sanitizer.py     PII redaction, control char stripping
    └── validators.py    Shared validation helpers
```

## Extensibility Points

### Adding a New LLM Backend

Implement `LLMAdapter` ABC in `backend/services/llm_adapters/`:

```python
class MyAdapter(LLMAdapter):
    async def generate(self, prompt, system_prompt, max_tokens, temperature) -> LLMResponse: ...
    async def is_available(self) -> bool: ...
    def adapter_name(self) -> str: ...
    def model_name(self) -> str: ...
```

Wire it in `backend/main.py` lifespan under `if settings.llm_adapter == "my-adapter"`.

### Adding Optimization Strategies

`OptimizationEngine` delegates entirely to the LLM via mode-specific system prompts.  
To add a rule-based pre-pass (deduplication, regex compression):

1. Add a `PreProcessor` protocol in `services/`
2. Call it in `OptimizationEngine.optimize()` before the LLM call
3. Track tokens saved by pre-processing separately in metadata

### Adding Custom Pricing

```python
# In your deployment config
from backend.services.cost_estimator import CostEstimator
from backend.models.config import ModelPricing

estimator = CostEstimator(pricing_overrides={
    "my-model": ModelPricing(input_per_1k_tokens=0.002, output_per_1k_tokens=0.004, ...)
})
```

## Planned: Middleware Proxy Mode

Future versions will include a transparent API proxy that intercepts OpenAI/Anthropic calls,
optimizes the prompt in-flight, and forwards to the real endpoint — zero code changes in
your application.

```
Your app → TokenForge Proxy → OpenAI API
```

The proxy will expose the same API schema as OpenAI, making it a drop-in replacement.

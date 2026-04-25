# TokenForge API Documentation

Base URL (local): `http://localhost:8000`

Interactive docs: `http://localhost:8000/docs` (Swagger UI)

---

## Authentication

No authentication required for local deployment.  
For production, add an API key middleware to `backend/api/middleware/`.

---

## Endpoints

### POST `/api/v1/optimize`

**Description:** Optimize a prompt using a local LLM with semantic scoring and cost estimation.

**Request Body:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `prompt` | string | Yes | — | Prompt to optimize (max 100,000 chars) |
| `mode` | enum | No | `balanced` | `safe` \| `balanced` \| `aggressive` |
| `target_model` | enum | No | `gpt-4o` | Model for cost estimation |
| `preserve_formatting` | bool | No | `true` | Keep markdown/code blocks |
| `preserve_constraints` | bool | No | `true` | Keep rules and constraints |
| `max_compression_ratio` | float | No | `null` | Cap compression (0.1–0.99) |
| `context` | string | No | `null` | Additional context for the optimizer |

**Response:**

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "original_prompt": "Please kindly analyze the customer feedback...",
  "optimized_prompt": "Analyze customer feedback. Identify top 3 themes.",
  "original_tokens": 1240,
  "optimized_tokens": 410,
  "token_reduction_percent": 66.9,
  "semantic_similarity": 0.9512,
  "risk_level": "low",
  "estimated_cost_before": 0.003162,
  "estimated_cost_after": 0.001051,
  "cost_savings_percent": 66.77,
  "optimization_mode": "balanced",
  "target_model": "gpt-4o",
  "processing_time_ms": 1284.3,
  "llm_adapter_used": "ollama",
  "warnings": [],
  "metadata": {
    "original_cost_breakdown": { "input_cost": 0.0031, "estimated_output_cost": 0.00006, "total_cost": 0.003162 },
    "optimized_cost_breakdown": { "input_cost": 0.001025, "estimated_output_cost": 0.000026, "total_cost": 0.001051 },
    "semantic_confidence": 0.95,
    "embedding_model": "all-MiniLM-L6-v2",
    "llm_model": "gemma3:4b",
    "llm_latency_ms": 1180.2
  }
}
```

**Error Codes:**
- `422` — Validation error (empty prompt, invalid mode)
- `429` — Rate limit exceeded
- `500` — LLM or internal error

---

### POST `/api/v1/analyze`

**Description:** Token count and cost estimate only. No LLM call — very fast.

**Request Body:**

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `prompt` | string | Yes | — |
| `target_model` | enum | No | `gpt-4o` |
| `include_breakdown` | bool | No | `false` |

**Response:**

```json
{
  "request_id": "...",
  "prompt": "...",
  "token_analysis": {
    "token_count": 1240,
    "estimated_output_tokens": 744,
    "total_estimated_tokens": 1984,
    "tokenizer_used": "o200k_base",
    "breakdown": [
      { "segment": "System: You are a helpful…", "token_count": 180, "type": "instruction" },
      { "segment": "Analyze the following data…", "token_count": 640, "type": "content" }
    ]
  },
  "cost_estimate": {
    "input_cost": 0.0031,
    "estimated_output_cost": 0.00744,
    "total_cost": 0.010540,
    "currency": "USD",
    "model": "gpt-4o",
    "pricing_per_1k_input": 0.0025,
    "pricing_per_1k_output": 0.010
  },
  "processing_time_ms": 12.4
}
```

---

### GET `/health`

**Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "llm_adapter": "ollama",
  "llm_available": true,
  "embedding_model": "all-MiniLM-L6-v2",
  "embedding_available": true,
  "uptime_seconds": 3600.5,
  "models_loaded": ["gpt-4o", "gpt-4o-mini", "claude-3-opus", "..."]
}
```

Status values: `healthy` | `degraded` (LLM unavailable but fallback active)

---

### GET `/models`

Returns all supported pricing models and available adapter/mode lists.

---

## Rate Limiting

Default: 60 requests per 60 seconds per IP.  
Returns `429` with `Retry-After` header when exceeded.

Configure via:
```bash
RATE_LIMIT_REQUESTS=60
RATE_LIMIT_WINDOW=60
```

---

## Risk Levels

| Level | Semantic Similarity | Interpretation |
|-------|--------------------|-|
| `low` | ≥ 0.88 | Safe to use in production |
| `medium` | 0.75–0.88 | Review before use |
| `high` | < 0.75 | Significant semantic drift — verify manually |

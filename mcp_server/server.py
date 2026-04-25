"""
TokenForge MCP Server

Exposes TokenForge capabilities as Claude tools by proxying to the
FastAPI backend at http://localhost:8000.

  - optimize_prompt     : compress a prompt, get token savings + cost estimate
  - analyze_tokens      : count tokens and estimate cost without optimizing
  - compare_models      : compare cost of a prompt across multiple LLM models
  - get_pricing         : look up current pricing for any supported model

Run standalone:
    python -m mcp_server.server
"""

import asyncio
import sys
import os
import logging

# Silence library noise before any imports
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
os.environ.setdefault("HF_HUB_VERBOSITY", "error")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)

_real_stdout = sys.stdout
sys.stdout = sys.stderr

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

sys.stdout = _real_stdout

# ── Config ────────────────────────────────────────────────────────────────────
BACKEND_URL = os.getenv("TOKENFORGE_BACKEND_URL", "http://localhost:8000")
# Long timeout — gemma4 can be slow; MCP client timeout is ~5 min in latest Desktop
HTTP_TIMEOUT = httpx.Timeout(300.0)

# ── MCP Server ────────────────────────────────────────────────────────────────
server = Server("tokenforge")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="optimize_prompt",
            description=(
                "Compress an LLM prompt to reduce token usage while preserving its meaning. "
                "Returns the optimized prompt, token counts, semantic similarity score, "
                "and estimated API cost savings."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "The prompt text to optimize"},
                    "mode": {
                        "type": "string",
                        "enum": ["safe", "balanced", "aggressive"],
                        "default": "balanced",
                        "description": "safe=minimal compression, balanced=moderate, aggressive=maximum reduction",
                    },
                    "target_model": {
                        "type": "string",
                        "default": "gpt-4o",
                        "description": "Model for cost estimation: gpt-4o, gpt-4o-mini, claude-3-sonnet, etc.",
                    },
                },
                "required": ["prompt"],
            },
        ),
        Tool(
            name="analyze_tokens",
            description=(
                "Count tokens in a prompt and estimate API cost. "
                "Fast — no LLM call. Use to check cost before sending."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "The prompt text to analyze"},
                    "target_model": {
                        "type": "string",
                        "default": "gpt-4o",
                        "description": "Model for token counting and cost estimation",
                    },
                },
                "required": ["prompt"],
            },
        ),
        Tool(
            name="compare_models",
            description=(
                "Compare the cost of the same prompt across multiple LLM models. "
                "Returns a ranked table from cheapest to most expensive."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "The prompt to cost-compare"},
                    "models": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["gpt-5", "claude-sonnet-4-6", "claude-opus-4-7", "gemini-3-pro", "grok-3", "deepseek-v3", "llama-4-maverick", "qwen3-235b", "kimi-k2"],
                        "description": "List of model names to compare",
                    },
                },
                "required": ["prompt"],
            },
        ),
        Tool(
            name="get_pricing",
            description="Look up API pricing for any supported LLM model.",
            inputSchema={
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": "Model name, e.g. gpt-4o, claude-3-opus, gemini-1.5-flash",
                    },
                },
                "required": [],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "optimize_prompt":
        return await _tool_optimize(arguments)
    elif name == "analyze_tokens":
        return await _tool_analyze(arguments)
    elif name == "compare_models":
        return await _tool_compare(arguments)
    elif name == "get_pricing":
        return await _tool_pricing(arguments)
    return [TextContent(type="text", text=f"Unknown tool: {name}")]


# ── Tool implementations (thin REST proxies) ──────────────────────────────────

async def _post(path: str, body: dict) -> dict:
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        r = await client.post(f"{BACKEND_URL}{path}", json=body)
        r.raise_for_status()
        return r.json()


async def _get(path: str) -> dict:
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        r = await client.get(f"{BACKEND_URL}{path}")
        r.raise_for_status()
        return r.json()


async def _tool_optimize(args: dict) -> list[TextContent]:
    prompt = args.get("prompt", "").strip()
    if not prompt:
        return [TextContent(type="text", text="Error: prompt is required.")]
    try:
        data = await _post("/api/v1/optimize", {
            "prompt": prompt,
            "mode": args.get("mode", "balanced"),
            "target_model": args.get("target_model", "gpt-4o"),
            "preserve_formatting": True,
            "preserve_constraints": True,
        })
    except httpx.ConnectError:
        return [TextContent(type="text", text=f"Cannot reach TokenForge backend at {BACKEND_URL}. Start it with: scripts\\start-backend.bat")]
    except Exception as exc:
        return [TextContent(type="text", text=f"Optimization failed: {exc}")]

    savings = data["estimated_cost_before"] - data["estimated_cost_after"]
    output = f"""## TokenForge — Prompt Optimization

**Mode:** {data["optimization_mode"]}  |  **Model:** {data["target_model"]}

### Optimized Prompt
```
{data["optimized_prompt"]}
```

### Metrics
| Metric | Value |
|--------|-------|
| Original tokens | {data["original_tokens"]:,} |
| Optimized tokens | {data["optimized_tokens"]:,} |
| Token reduction | **{data["token_reduction_percent"]:.1f}%** |
| Semantic similarity | {data["semantic_similarity"]:.3f} ({data["risk_level"]} risk) |
| Cost before | ${data["estimated_cost_before"]:.6f} |
| Cost after | ${data["estimated_cost_after"]:.6f} |
| **Savings per call** | **${savings:.6f} ({data["cost_savings_percent"]:.1f}%)** |
| Processing time | {data["processing_time_ms"]:.0f}ms |
"""
    if data.get("warnings"):
        output += "\n### Warnings\n" + "".join(f"- {w}\n" for w in data["warnings"])
    if data.get("risk_level") == "high":
        output += "\n> High semantic drift — review carefully before use.\n"
    return [TextContent(type="text", text=output)]


async def _tool_analyze(args: dict) -> list[TextContent]:
    prompt = args.get("prompt", "").strip()
    if not prompt:
        return [TextContent(type="text", text="Error: prompt is required.")]
    try:
        data = await _post("/api/v1/analyze", {
            "prompt": prompt,
            "target_model": args.get("target_model", "gpt-4o"),
            "include_breakdown": False,
        })
    except httpx.ConnectError:
        return [TextContent(type="text", text=f"Cannot reach TokenForge backend at {BACKEND_URL}.")]
    except Exception as exc:
        return [TextContent(type="text", text=f"Analysis failed: {exc}")]

    ta = data["token_analysis"]
    ce = data["cost_estimate"]
    total = ce["total_cost"]

    output = f"""## TokenForge — Token Analysis

**Model:** {data["metadata"]["target_model"]}  |  **Tokenizer:** {ta["tokenizer_used"]}

| Metric | Tokens | Cost (USD) |
|--------|--------|------------|
| Input | {ta["token_count"]:,} | ${ce["input_cost"]:.6f} |
| Est. output | {ta["estimated_output_tokens"]:,} | ${ce["estimated_output_cost"]:.6f} |
| **Total** | **{ta["total_estimated_tokens"]:,}** | **${total:.6f}** |

**Pricing:** ${ce["pricing_per_1k_input"]}/1K input · ${ce["pricing_per_1k_output"]}/1K output

### At Scale
| Volume | Total cost | Saved if optimized 50% |
|--------|-----------|------------------------|
| 1,000 calls | ${total * 1_000:.3f} | ${total * 500:.3f} |
| 100,000 calls | ${total * 100_000:.2f} | ${total * 50_000:.2f} |
| 1,000,000 calls | ${total * 1_000_000:.2f} | ${total * 500_000:.2f} |
"""
    return [TextContent(type="text", text=output)]


async def _tool_compare(args: dict) -> list[TextContent]:
    prompt = args.get("prompt", "").strip()
    if not prompt:
        return [TextContent(type="text", text="Error: prompt is required.")]

    default_models = ["gpt-5", "claude-sonnet-4-6", "claude-opus-4-7", "gemini-3-pro", "grok-3", "deepseek-v3", "llama-4-maverick", "qwen3-235b", "kimi-k2"]
    model_names = args.get("models", default_models)

    try:
        models_data = await _get("/models")
    except Exception:
        models_data = {}

    rows = []
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        for model in model_names:
            try:
                r = await client.post(f"{BACKEND_URL}/api/v1/analyze", json={"prompt": prompt, "target_model": model})
                d = r.json()
                ce = d["cost_estimate"]
                rows.append({
                    "model": model,
                    "cost": ce["total_cost"],
                    "input_per_1k": ce["pricing_per_1k_input"],
                    "output_per_1k": ce["pricing_per_1k_output"],
                    "tokens": d["token_analysis"]["token_count"],
                })
            except Exception:
                pass

    if not rows:
        return [TextContent(type="text", text="Could not retrieve model data. Is the backend running?")]

    rows.sort(key=lambda r: r["cost"])
    cheapest = rows[0]["cost"]

    output = f"""## TokenForge — Model Cost Comparison

**Prompt:** {prompt[:80]}{"…" if len(prompt) > 80 else ""}

### Ranked by cost (cheapest first)
| Rank | Model | Cost/call | vs cheapest | Input/1K | Output/1K |
|------|-------|-----------|-------------|----------|-----------|
"""
    for i, r in enumerate(rows, 1):
        ratio = f"+{((r['cost'] / cheapest - 1) * 100):.0f}%" if i > 1 else "—"
        output += f"| {i} | {r['model']} | ${r['cost']:.6f} | {ratio} | ${r['input_per_1k']} | ${r['output_per_1k']} |\n"

    output += f"\n> Combine with `optimize_prompt` for maximum savings.\n"
    return [TextContent(type="text", text=output)]


async def _tool_pricing(args: dict) -> list[TextContent]:
    try:
        data = await _get("/models")
    except httpx.ConnectError:
        return [TextContent(type="text", text=f"Cannot reach TokenForge backend at {BACKEND_URL}.")]
    except Exception as exc:
        return [TextContent(type="text", text=f"Failed: {exc}")]

    model_filter = args.get("model", "").lower().strip()
    models = {m["id"]: m for m in data.get("models", [])}

    if model_filter:
        match = next((m for mid, m in models.items() if model_filter in mid.lower()), None)
        if not match:
            return [TextContent(type="text", text=f"Model '{model_filter}' not found. Supported: {', '.join(models.keys())}")]
        output = f"""## TokenForge — Pricing: {match.get('name', model_filter)}

| Field | Value |
|-------|-------|
| Provider | {match.get('provider', 'unknown')} |
| Input cost | ${match.get('pricing_input_per_1k', '?')} / 1K tokens |
| Output cost | ${match.get('pricing_output_per_1k', '?')} / 1K tokens |
| Context window | {match.get('context_window', 0):,} tokens |
"""
    else:
        output = "## TokenForge — All Model Pricing\n\n"
        output += "| Model | Provider | Input/1K | Output/1K | Context |\n"
        output += "|-------|----------|----------|-----------|--------|\n"
        for mid, m in sorted(models.items()):
            output += f"| {m.get('name', mid)} | {m.get('provider','?')} | ${m.get('pricing_input_per_1k','?')} | ${m.get('pricing_output_per_1k','?')} | {m.get('context_window',0):,} |\n"

    return [TextContent(type="text", text=output)]


# ── Entry point ───────────────────────────────────────────────────────────────

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())

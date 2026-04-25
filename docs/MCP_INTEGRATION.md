# MCP Integration Guide

TokenForge implements the [Model Context Protocol (MCP)](https://modelcontextprotocol.io) and works as a native MCP server inside Claude Desktop and any MCP-compatible client.

---

## Prerequisites

- TokenForge installed and running (`python launcher/launch.py`)
- Claude Desktop installed
- Backend healthy: `curl http://localhost:8000/health`

---

## Claude Desktop Setup

### 1. Locate your config file

| OS | Path |
|---|---|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

### 2. Add TokenForge as an MCP server

```json
{
  "mcpServers": {
    "tokenforge": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/absolute/path/to/tokenforge",
      "env": {
        "TOKENFORGE_BACKEND_URL": "http://localhost:8000"
      }
    }
  }
}
```

**Windows path example:**
```json
{
  "mcpServers": {
    "tokenforge": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "C:\\Users\\YourName\\tokenforge",
      "env": {
        "TOKENFORGE_BACKEND_URL": "http://localhost:8000"
      }
    }
  }
}
```

### 3. Restart Claude Desktop

The TokenForge tools will appear in the tool picker (hammer icon) in any conversation.

---

## Available MCP Tools

### `optimize_prompt`

Compress a prompt using semantic-preserving optimization.

**Parameters:**
| Parameter | Type | Required | Description |
|---|---|---|---|
| `prompt` | string | ✅ | The prompt text to optimize |
| `mode` | string | No | `safe`, `balanced`, or `aggressive` (default: `balanced`) |
| `target_model` | string | No | Model for cost estimation (default: `gpt-4o`) |

**Returns:**
```json
{
  "optimized_prompt": "...",
  "original_tokens": 1247,
  "optimized_tokens": 423,
  "token_reduction_percent": 66.1,
  "semantic_similarity": 0.94,
  "risk_level": "low",
  "cost_before": 0.01247,
  "cost_after": 0.00423
}
```

**Example in Claude Desktop:**
```
Optimize this system prompt for me using balanced mode targeting claude-opus-4-7:

[paste your verbose system prompt]
```

---

### `analyze_tokens`

Count tokens and estimate API cost without making any LLM call.

**Parameters:**
| Parameter | Type | Required | Description |
|---|---|---|---|
| `prompt` | string | ✅ | Text to analyze |
| `target_model` | string | No | Model for pricing (default: `gpt-4o`) |

**Returns:**
```json
{
  "token_count": 2400,
  "estimated_output_tokens": 600,
  "total_tokens": 3000,
  "cost_estimate": {
    "input_cost": 0.024,
    "output_cost": 0.012,
    "total_cost": 0.036
  }
}
```

---

### `compare_models`

Compare prompt costs across multiple models side by side.

**Parameters:**
| Parameter | Type | Required | Description |
|---|---|---|---|
| `prompt` | string | ✅ | Prompt to price |

**Returns:** Cost breakdown for all 28 supported models, sorted by price.

---

### `get_pricing`

Look up current pricing for a specific model.

**Parameters:**
| Parameter | Type | Required | Description |
|---|---|---|---|
| `model` | string | ✅ | Model ID (e.g., `gpt-4o`, `claude-opus-4-7`) |

---

## Common Workflows

### RAG Context Compression

Before sending retrieved documents to an expensive model:

```
I need to send this RAG context to claude-opus-4-7 — can you optimize it first 
using balanced mode so I reduce token costs?

[paste retrieved documents]
```

Expected: 40–60% token reduction, semantic score > 0.92

---

### System Prompt Optimization

Optimize a verbose system prompt once, cache and reuse:

```
Optimize this system prompt in safe mode. I need to preserve all the rules 
and constraints exactly:

[paste system prompt]
```

Expected: 20–35% reduction, semantic score > 0.97

---

### Pre-flight Cost Check

Before running a batch job:

```
How much will it cost to send this prompt to GPT-4o 10,000 times per day?
Can you analyze the tokens and give me a monthly estimate?

[paste prompt]
```

---

### Model Selection

Choosing the right model for a use case:

```
Compare the cost of this prompt across all supported models. I want to 
pick the cheapest option that still has good quality.

[paste prompt]
```

---

## MCP Server Configuration

Environment variables for the MCP server process:

| Variable | Default | Description |
|---|---|---|
| `TOKENFORGE_BACKEND_URL` | `http://localhost:8000` | TokenForge backend URL |

---

## Troubleshooting

**Tools not showing in Claude Desktop**
1. Check backend is running: `curl http://localhost:8000/health`
2. Verify the `cwd` path in config is absolute and correct
3. Check Python is in PATH: `python --version`
4. Restart Claude Desktop completely

**"Connection refused" error**
Start the backend first: `python launcher/launch.py`

**Tool calls timing out**
Ollama inference can be slow on first call. The MCP server has a 300s timeout. If you consistently timeout, switch to a lighter model (`gemma4:1b`).

**Finding Claude Desktop logs**
- macOS: `~/Library/Logs/Claude/`
- Windows: `%APPDATA%\Claude\logs\`

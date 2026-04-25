<div align="center">

<h1>⚡ TokenForge</h1>

<p><strong>AI Cost Optimization Infrastructure — Local-First · Privacy-Preserving · Open Source</strong></p>

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Tests](https://github.com/nitiemahendra/tokenforge/actions/workflows/ci.yml/badge.svg)](https://github.com/nitiemahendra/tokenforge/actions)
[![MCP Compatible](https://img.shields.io/badge/MCP-Claude%20Desktop-purple.svg)](docs/MCP_INTEGRATION.md)
[![Models](https://img.shields.io/badge/Models-28+-orange.svg)](#supported-models)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)](CONTRIBUTING.md)

<br/>

**Reduce LLM token costs by up to 70%.**
Run entirely on your machine. No cloud. No data sharing. No subscriptions.

<br/>

[Quick Start](#quick-start) · [Installation](#installation) · [Claude Desktop](#claude-desktop-integration) · [API Docs](docs/api.md) · [Contributing](CONTRIBUTING.md)

</div>

---

## Why TokenForge Exists

AI costs are rising because prompts and context are inefficient.

Every AI application carries a hidden tax: **bloated prompts**. System prompts, RAG context, conversation history, and instructions accumulate redundant tokens that carry no real semantic value — but you pay for every single one. At scale this compounds into thousands of dollars per month in pure waste.

**The industry has no good solution:**
- Cloud optimization services require sending your prompts to a third party *(unacceptable for private IP)*
- Regex-based compression destroys meaning
- Manual editing does not scale
- LLM wrappers add cost instead of reducing it

**TokenForge is different.** It runs a local embedding model (MiniLM-L6-v2) to measure semantic similarity before and after every optimization. Every result includes a **semantic similarity score** (0–1) and a **risk level**. You stay in full control.

> TokenForge reduces token waste while preserving semantic intent and privacy.

---

## TokenForge Is NOT a Prompt Shortener

> **TokenForge is AI Cost Optimization Infrastructure.**

| Naive Shortener | TokenForge Infrastructure |
|---|---|
| Cuts characters blindly | Semantic-aware compression, scored |
| No cost visibility | Live cost estimates for 28 models |
| No integration layer | MCP-native for Claude Desktop |
| Cloud-based | 100% local, zero data egress |
| No quality guarantee | Similarity verified on every run |

---

## Features

- **70% token reduction** with configurable modes (Safe / Balanced / Aggressive)
- **Local-first** — all processing on your machine via Ollama + gemma
- **Semantic scoring** — cosine similarity measured on every optimization
- **28 models** — live cost estimates for GPT-5, Claude Opus, Gemini, Grok, DeepSeek, Llama, Qwen
- **Claude Desktop MCP** — 4 native tools: optimize, analyze, compare, pricing
- **React dashboard** — real-time token counter, visual diff, cost analytics
- **REST API** — drop into any LLM pipeline as a pre-processing layer
- **Zero telemetry** — no analytics, no tracking, no phone home

---

## Architecture

```
Your Machine
├── React Dashboard  :3001
├── Claude Desktop (MCP client)
│
└── FastAPI Backend  :8000
    ├── Token Analyzer    (tiktoken)
    ├── Semantic Engine   (MiniLM-L6-v2)
    ├── Cost Estimator    (28 models)
    └── Optimization Engine
            └── Ollama  :11434
                    └── gemma4:1b / 4b / latest
```

---

## Quick Start

**Prerequisites:** Python 3.10+, Node.js 18+, [Ollama](https://ollama.com)

```bash
git clone https://github.com/nitiemahendra/tokenforge.git
cd tokenforge
python installer/install.py
python launcher/launch.py
```

- Dashboard → http://localhost:3001
- API → http://localhost:8000
- API Docs → http://localhost:8000/docs

---

## Installation

### Smart Installer (Recommended)

```bash
python installer/install.py
```

Auto-detects your RAM and recommends the right model:

| RAM | Model | Quality |
|---|---|---|
| < 8 GB | `gemma4:1b` | Fast, lightweight |
| 8–16 GB | `gemma4:4b` | Balanced |
| > 16 GB | `gemma4:latest` | Best quality |

### Manual

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..
ollama pull gemma4:4b
cp .env.example .env
python launcher/launch.py
```

### Docker

```bash
# Development
docker compose up

# Production (Ollama included)
docker compose -f docker/docker-compose.prod.yml up -d
```

### Shell Scripts

```bash
bash scripts/launch.sh           # macOS / Linux
scripts\launch.bat               # Windows
```

---

## Claude Desktop Integration

TokenForge ships as a native **MCP server**.

**1. Find your config:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**2. Add the server:**

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

**3. Restart Claude Desktop.** Available tools:

| Tool | Description |
|---|---|
| `optimize_prompt` | Compress prompt — returns optimized text + savings + cost |
| `analyze_tokens` | Count tokens and estimate cost |
| `compare_models` | Side-by-side cost comparison |
| `get_pricing` | Look up model pricing |

Full guide → [docs/MCP_INTEGRATION.md](docs/MCP_INTEGRATION.md)

---

## REST API

```bash
# Optimize
curl -X POST http://localhost:8000/api/v1/optimize \
  -H "Content-Type: application/json" \
  -d '{"prompt": "...", "mode": "balanced", "target_model": "gpt-4o"}'

# Analyze
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "...", "target_model": "claude-sonnet-4-6"}'

# Models list
curl http://localhost:8000/models

# Health check
curl http://localhost:8000/health
```

Full reference → [docs/api.md](docs/api.md)

---

## Supported Models

| Provider | Models |
|---|---|
| OpenAI | GPT-5, GPT-4.1, GPT-4.1-mini, GPT-4.1-nano, o3, o4-mini, GPT-4o, GPT-4o-mini |
| Anthropic | Claude Opus 4.7, Claude Opus 4.5, Claude Sonnet 4.6, Claude Sonnet 4.5, Claude Haiku 4.5 |
| Google | Gemini 3 Pro, Gemini 2.5 Pro, Gemini 2.5 Flash, Gemini 2.0 Flash |
| xAI | Grok 3, Grok 3 Mini |
| DeepSeek | DeepSeek V3, DeepSeek R1 |
| Meta | Llama 4 Maverick, Llama 4 Scout |
| Alibaba | Qwen3 235B, Qwen3 30B |
| Moonshot | Kimi K2 |
| Custom | Add any model + pricing via the dashboard |

---

## Optimization Modes

| Mode | Reduction | Min Score | Best For |
|---|---|---|---|
| Safe | 20–35% | 0.97 | Legal, compliance, system prompts |
| Balanced | 40–60% | 0.92 | General use, RAG context |
| Aggressive | 55–70% | 0.85 | Bulk processing, max savings |

---

## Environment Variables

```bash
cp .env.example .env
```

| Variable | Default | Description |
|---|---|---|
| `LLM_ADAPTER` | `ollama` | `ollama` or `mock` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server |
| `OLLAMA_MODEL` | `gemma4:4b` | Optimization model |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Semantic similarity |
| `LOG_LEVEL` | `INFO` | Verbosity |
| `CORS_ORIGINS` | `http://localhost:3001` | Frontend origin |

---

## Troubleshooting

**Ollama not found** — Download from https://ollama.com

**Port 8000 in use**
```bash
lsof -i :8000 | grep LISTEN        # macOS/Linux
netstat -ano | findstr :8000        # Windows
```

**MCP tools missing in Claude Desktop**
1. `curl http://localhost:8000/health` — verify backend is up
2. Use absolute path in the config
3. Restart Claude Desktop

**Out of memory** — Switch to `gemma4:1b` and set `OLLAMA_MODEL=gemma4:1b` in `.env`

Full guide → [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
<img width="1920" height="1017" alt="claude_tokenforge_connector" src="https://github.com/user-attachments/assets/2850620b-ff03-4259-ba47-ff476f409141" />
<img width="1920" height="1017" alt="claude_tokenforge_usage" src="https://github.com/user-attachments/assets/952344b1-4a2a-46ca-935a-1e209c11edb6" />
<img width="1920" height="1015" alt="claude_tokenforge_mcp_server" src="https://github.com/user-attachments/assets/07d8be99-4955-44df-98dc-62e828550eee" />
<img width="1918" height="975" alt="TokenForge Localhost dashboard" src="https://github.com/user-attachments/assets/3e1421a2-f391-4546-a1d2-526942e0208c" />




---

## Contributing

```bash
git clone https://github.com/nitiemahendra/tokenforge.git
cd tokenforge
git checkout -b feature/your-feature
python -m pytest backend/tests/     # must pass
git push origin feature/your-feature
# open a Pull Request
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

---

## Support TokenForge

TokenForge is free and open source. If it saves you money on AI costs, consider supporting continued development:

[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-GitHub-ea4aaa?style=flat-square&logo=github)](https://github.com/sponsors/nitiemahendra)


> Saving money with TokenForge? Support continued development ❤️

---

## Security

TokenForge runs entirely locally. Your prompts, keys, and data never leave your machine.
Found a vulnerability? See [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE) — free for personal and commercial use.

---

<div align="center">

Built by [Mahendra Kumar](https://www.linkedin.com/in/mahendrakumarnitie/) · [aitokenforge.netlify.app](https://aitokenforge.netlify.app)

*AI Cost Optimization Infrastructure — Local-first. Privacy-preserving. Free forever.*

</div>

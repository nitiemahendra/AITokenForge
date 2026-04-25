# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x (latest) | ✅ Active security fixes |
| < 1.0 | ❌ No longer supported |

---

## Reporting a Vulnerability

**Please do NOT open a public GitHub issue for security vulnerabilities.**

Report privately via one of:

1. **Email:** nitiemahendra@gmail.com — subject: `[SECURITY] TokenForge vulnerability`
2. **GitHub advisory:** [Open a private advisory](https://github.com/nitiemahendra/aitokenforge/security/advisories/new)

**Include:** description, reproduction steps, potential impact, suggested fix.

Response timeline: acknowledgement ≤ 48 h · assessment ≤ 7 days · fix timeline ≤ 14 days.

---

## Safe Handling Architecture

TokenForge uses a **local-first, zero-egress** security model. No user data ever leaves the machine.

### Layer 1 — Configuration (no secrets in source)

All runtime configuration is read exclusively from environment variables via `pydantic-settings`:

```
backend/config.py          ← Settings class, reads from .env / environment
.env.example               ← Safe placeholder template (committed)
.env                       ← Actual values (gitignored, never committed)
```

**Rules enforced:**
- Zero API keys, passwords, or tokens in source code
- Zero hardcoded credentials in Docker files or CI workflows
- `.env` blocked by `.gitignore` (pattern: `.env`, `.env.*`)
- CI workflows use `LLM_ADAPTER=mock` so no real credentials are ever needed

### Layer 2 — Prompt data (memory-only, never persisted)

| Stage | Where data lives | Persisted? |
|-------|-----------------|------------|
| HTTP request arrives | Python process memory | No |
| Token counting | In-process | No |
| Semantic embedding | In-process NumPy array | No |
| LLM inference (Ollama) | localhost:11434 — local process | No |
| HTTP response returned | Python process memory | No |

Prompts are **never** written to disk, logged, or transmitted off-device.

### Layer 3 — Logging policy (sanitized, structured)

The logger in `backend/utils/logger.py` emits only:

```
request_id | method | path | status_code | duration_ms
```

Fields that are **explicitly excluded** from all log events:
- `prompt` / `optimized_prompt` / any prompt fragment
- `Authorization` / `Cookie` / `X-API-Key` headers
- IP addresses beyond `127.0.0.1` (localhost only)
- Model weights or embedding vectors

### Layer 4 — Input sanitization

`backend/utils/sanitizer.py` and `backend/utils/validators.py` enforce:
- Maximum prompt length (`MAX_PROMPT_LENGTH`, default 100 000 chars)
- UTF-8 validation before processing
- Pydantic models on every request body — malformed input rejected at the boundary

### Layer 5 — Network isolation

All services bind to `127.0.0.1` (loopback only) by default:

| Service | Bind address | Port |
|---------|-------------|------|
| FastAPI backend | 0.0.0.0 (configurable) | 8000 |
| Vite dev server | localhost | 3001 |
| Ollama | localhost | 11434 |

> **Warning:** The API has no authentication in local mode by design (trusted localhost).
> If you expose port 8000 on a network, add authentication via a reverse proxy (nginx + basic auth, or Caddy + OAuth).

CORS is locked to localhost origins in `config.py`:
```python
cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000", "http://localhost:3001"]
```

### Layer 6 — Dependency integrity

Dependencies are **version-pinned** in `backend/requirements.txt` and `frontend/package.json`.

Audit commands:
```bash
# Python
pip install pip-audit
pip-audit -r backend/requirements.txt

# Node
cd frontend && npm audit
```

### Layer 7 — Git guardrails

`.gitignore` blocks the following classes of file at the repository level:

| Category | Blocked patterns |
|----------|-----------------|
| Env / secrets | `.env`, `.env.*`, `*.secret`, `*_secret*`, `secrets/`, `credentials/` |
| Keys / certs | `*.pem`, `*.key`, `*.cert`, `*.p12`, `*.pfx` |
| Logs | `*.log`, `logs/`, `backend_server.log` |
| ML weights | `*.bin`, `*.safetensors`, `*.gguf`, `*.pt`, `*.pth`, `*.pkl` |
| Prompt cache | `prompt_cache/`, `optimization_cache/`, `*.embeddings` |
| DB files | `*.db`, `*.sqlite`, `*.sqlite3` |
| Build artifacts | `dist/`, `build/`, `node_modules/`, `__pycache__/` |
| IDE / OS | `.vscode/settings.json`, `.idea/`, `.DS_Store`, `Thumbs.db` |

---

## What TokenForge Never Does

- ❌ Sends prompts to any external server
- ❌ Collects analytics, telemetry, or usage data
- ❌ Requires API keys or account registration
- ❌ Persists optimization history to disk
- ❌ Communicates with TokenForge or Anthropic servers

## What TokenForge Does

- ✅ All LLM inference via local Ollama (no cloud API)
- ✅ Embedding model runs fully on-device (MiniLM-L6-v2)
- ✅ All API calls stay within localhost
- ✅ Open-source — you can audit every line

---

## Open-Core Privacy Guarantee

Future premium features will maintain the same local-processing guarantee. No user prompt data will flow through hosted services without explicit, informed, per-user opt-in consent.

---

## Responsible Disclosure

Public disclosure only after: fix developed and tested + 30-day patch window + reporter notified and credited.

Thank you for helping keep TokenForge safe.

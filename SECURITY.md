# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| 1.x (latest) | ✅ Active security fixes |
| < 1.0 | ❌ No longer supported |

---

## Reporting a Vulnerability

**Please do NOT open a public GitHub issue for security vulnerabilities.**

Report privately:

1. **Email:** nitiemahendra@gmail.com with subject `[SECURITY] TokenForge vulnerability`
2. **GitHub:** Use [GitHub's private vulnerability reporting](https://github.com/nitiemahendra/tokenforge/security/advisories/new)

**Include in your report:**
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

**Response timeline:**
- Acknowledgement within **48 hours**
- Initial assessment within **7 days**
- Fix timeline communicated within **14 days**

You will be credited in the security advisory and CHANGELOG unless you prefer to remain anonymous.

---

## Security Architecture

TokenForge is designed with a **local-first, zero-egress** security model:

### What TokenForge Does NOT Do

- ❌ Does not send prompts to any external service
- ❌ Does not collect usage analytics or telemetry
- ❌ Does not require API keys or account registration
- ❌ Does not store optimization history persistently
- ❌ Does not communicate with TokenForge servers

### What TokenForge Does

- ✅ All processing happens on your machine
- ✅ LLM inference via local Ollama (no cloud API)
- ✅ Embedding model runs locally (MiniLM-L6-v2)
- ✅ All API calls stay within `localhost`
- ✅ No external network requests during optimization

---

## Sensitive Data Handling

### Prompts
- Prompts are processed in memory only
- Never written to disk
- Never logged (see Logging Policy below)
- Never transmitted off-device

### Logging Policy

TokenForge explicitly **never logs**:
- User prompts or any portion thereof
- API keys or credentials
- Optimization results
- Conversation history
- Request payloads containing user content

Logs contain only: request metadata (method, path, status code, duration, request ID).

See `backend/utils/logger.py` for the logging configuration.

### Environment Variables
- The `.env` file is in `.gitignore` — never committed
- `.env.example` contains only placeholder values
- No secrets are hardcoded in source

---

## Network Security

TokenForge binds only to `localhost` by default:
- Backend: `127.0.0.1:8000`
- Frontend dev server: `127.0.0.1:3001`
- Ollama: `127.0.0.1:11434`

**Do not expose these ports to a public network** without adding authentication. The API has no authentication layer in local mode by design — it assumes a trusted local environment.

If you deploy TokenForge as a shared service, add authentication via a reverse proxy (nginx/Caddy with basic auth or OAuth).

---

## Dependency Security

Dependencies are pinned in `backend/requirements.txt`. Run `pip audit` periodically:

```bash
pip install pip-audit
pip-audit -r backend/requirements.txt
```

For Node dependencies:

```bash
cd frontend && npm audit
```

---

## Open-Core Boundary

TokenForge's optimization engine processes user prompts locally. Future premium/enterprise features will maintain the same local-processing guarantee — no user data will flow through hosted services without explicit opt-in consent.

---

## Responsible Disclosure

We follow responsible disclosure practices. Public disclosure of a reported vulnerability will only happen after:
1. A fix has been developed and tested
2. Sufficient time has passed for users to update (typically 30 days)
3. The reporter has been notified and credited

Thank you for helping keep TokenForge safe for everyone.

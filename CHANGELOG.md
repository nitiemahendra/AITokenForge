# Changelog

All notable changes to TokenForge are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- VS Code extension
- Automated prompt versioning
- Batch optimization endpoint
- Team dashboard (open-core premium)

---

## [1.0.1] — 2026-04-25

### Fixed
- Resolved ruff lint errors across backend (import sorting, unused imports, deprecated type hints)
- Fixed mypy type errors in `logger.py`, `semantic_engine.py`, and `main.py`
- Removed broken git submodule reference for `website/` directory
- CI pipeline now fully green (Backend Tests, Frontend Build, Docker Build)

---

## [1.0.0] — 2026-04-25

### Added
- FastAPI backend with 5 REST endpoints (optimize, analyze, models, health, restart)
- React 18 dashboard with Vite, TailwindCSS, real-time token counter
- Semantic similarity engine using `all-MiniLM-L6-v2` (sentence-transformers)
- Token analyzer with tiktoken (OpenAI tokenizer)
- Cost estimator for 28 AI models with live pricing
- Three optimization modes: Safe (20–35%), Balanced (40–60%), Aggressive (55–70%)
- Ollama adapter for local LLM inference (gemma4)
- MCP server with 4 tools: `optimize_prompt`, `analyze_tokens`, `compare_models`, `get_pricing`
- Claude Desktop integration via MCP protocol
- Smart installer with RAM-based model recommendation
- Cross-platform launcher (Python, Windows .bat, Unix .sh)
- Docker support: development compose + production compose with Ollama service
- GitHub Actions CI: lint, type-check, test, docker build
- Structured JSON logging (structlog) — prompt-safe, no user data logged
- Rate limiting middleware (60 req/60s default)
- Error log panel in dashboard with collapsible view
- Restart and Refresh buttons in dashboard status bar
- Support for custom model pricing via dashboard UI
- 28 tests across 4 test modules — all passing
- Full documentation: API reference, architecture, installation, troubleshooting, MCP guide

### Security
- All processing local — no data leaves the machine
- `.env` excluded from repository
- Logging policy: prompts never logged
- Model weights excluded from repository

---

[Unreleased]: https://github.com/nitiemahendra/tokenforge/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/nitiemahendra/tokenforge/releases/tag/v1.0.0

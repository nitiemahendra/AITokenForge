# Contributing to TokenForge

Thank you for helping build AI cost optimization infrastructure that is open, local, and free for everyone.

## Quick Reference

| Task | Command |
|---|---|
| Run tests | `python -m pytest backend/tests/` |
| Lint | `ruff check .` |
| Format | `ruff format .` |
| Type check | `mypy backend/` |
| All checks | `make test && make lint && make type-check` |

---

## Ways to Contribute

- **Bug reports** — [open an issue](https://github.com/nitiemahendra/tokenforge/issues/new?template=bug_report.md)
- **Feature requests** — [open an issue](https://github.com/nitiemahendra/tokenforge/issues/new?template=feature_request.md)
- **Code contributions** — fork → branch → PR
- **Documentation** — fix typos, add examples, improve guides
- **New model pricing** — add current pricing for models in `backend/models/config.py`
- **New LLM adapters** — implement `BaseLLMAdapter` in `backend/services/llm_adapters/`

---

## Development Setup

```bash
git clone https://github.com/nitiemahendra/tokenforge.git
cd tokenforge

# Python environment
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
pip install -r backend/requirements-dev.txt

# Frontend
cd frontend && npm install && cd ..

# Start services
ollama pull gemma4:4b
cp .env.example .env
python launcher/launch.py
```

---

## Branch Strategy

```
main           Production-ready, protected
develop        Integration branch for features
feature/*      New features: feature/add-openai-adapter
fix/*          Bug fixes: fix/semantic-score-edge-case
docs/*         Documentation only: docs/update-mcp-guide
```

Always branch from `main` for fixes, `develop` for features.

---

## Pull Request Process

1. **Create a focused branch** — one PR per feature/fix
2. **Write tests** — all new code must have test coverage
3. **Pass all checks** — `make test && make lint && make type-check`
4. **Update docs** — update relevant `.md` files if behavior changes
5. **Fill out the PR template** — describe what, why, and how to test
6. **Keep it small** — PRs under 400 lines are reviewed faster

---

## Code Standards

### Python
- **Style:** `ruff format` (Black-compatible, 100 char line length)
- **Linting:** `ruff check` — no warnings allowed
- **Types:** Add type hints to all new functions
- **Tests:** pytest, `pytest-asyncio` for async routes
- **No secrets in code** — use env vars via `pydantic-settings`

### TypeScript / React
- **Style:** Prettier (run `npm run format` in `frontend/`)
- **Types:** Strict mode — no `any` except where unavoidable
- **Components:** Functional, hooks-based
- **No inline styles** — use Tailwind classes

### Commit Messages
Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add Anthropic direct adapter
fix: semantic score NaN on empty prompt
docs: add Docker production guide
test: add edge case for 0-token prompt
refactor: extract cost estimator to service
```

---

## Adding a New Model

1. Open `backend/models/config.py`
2. Add the model to `TargetModel` enum
3. Add pricing to `DEFAULT_PRICING` dict (per 1M tokens, input/output)
4. Update `frontend/src/types/index.ts` — add to `TargetModel` union
5. Add a test in `backend/tests/test_cost_estimator.py`

---

## Adding a New LLM Adapter

1. Create `backend/services/llm_adapters/your_adapter.py`
2. Implement `BaseLLMAdapter` interface (see `base.py`)
3. Register in `backend/main.py` lifespan factory
4. Add adapter name to `LLM_ADAPTER` env var docs
5. Add tests using `MockAdapter` pattern

---

## Security Rules

- **Never log prompt content** — prompts may contain private IP
- **Never commit `.env`** — use `.env.example` with placeholder values
- **Never commit model weights** — use `ollama pull` instructions
- **Rate limit** new endpoints (see `middleware/rate_limit.py`)
- **Sanitize** all user input via `backend/utils/sanitizer.py`

---

## Reporting Issues

### Bugs
Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md). Include:
- OS and Python version
- Steps to reproduce
- Expected vs actual behavior
- Relevant logs (sanitize any prompt content before sharing)

### Security Vulnerabilities
**Do not open a public issue.** See [SECURITY.md](SECURITY.md).

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). Be respectful, constructive, and inclusive.

---

Thank you for contributing to open AI infrastructure.

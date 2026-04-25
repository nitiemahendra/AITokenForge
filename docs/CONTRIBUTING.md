# Contributing to TokenForge

Thank you for your interest in contributing! TokenForge is open-source and welcomes contributions of all kinds.

---

## Ways to Contribute

- 🐛 **Bug reports** — open a GitHub issue with reproduction steps
- 💡 **Feature requests** — open a GitHub discussion
- 🔧 **Pull requests** — bug fixes, new model pricing, new features
- 📖 **Documentation** — improve guides, fix typos, add examples
- ⭐ **Star the repo** — helps others discover the project

---

## Development Setup

```bash
git clone https://github.com/tokenforge/tokenforge.git
cd tokenforge
python installer/install.py
python launcher/launch.py
```

This starts everything with hot-reload enabled.

---

## Project Structure

```
backend/
  api/routes/      # FastAPI endpoints — add new endpoints here
  services/        # Core engines — optimization, tokens, semantics
  models/          # Pydantic schemas and pricing config
  tests/           # pytest test suite
frontend/
  src/components/  # React UI components
  src/hooks/       # Custom React hooks
mcp_server/
  server.py        # MCP tools — proxies to the REST API
```

---

## Adding a New Model

1. Add pricing to `backend/models/config.py` in `DEFAULT_PRICING`:
```python
"my-model-id": ModelPricing(
    input_per_1k_tokens=0.001,
    output_per_1k_tokens=0.004,
    context_window=128_000,
    provider="myprovider",
    display_name="My Model Name",
),
```

2. Add to `TargetModel` enum in `backend/models/requests.py`:
```python
MY_MODEL = "my-model-id"
```

3. If the model uses a different tokenizer than `cl100k_base`, add it to `_ENCODING_MAP` in `backend/services/token_analyzer.py`.

---

## Running Tests

```bash
cd backend
../.venv/Scripts/python.exe -m pytest tests/ -v

# With coverage
../.venv/Scripts/python.exe -m pytest tests/ --cov=backend --cov-report=html
```

---

## Code Style

- Python: `ruff` for linting and formatting (`ruff check .` and `ruff format .`)
- TypeScript: Prettier via VS Code
- Line length: 100 characters
- No unused imports

The `.vscode/settings.json` configures format-on-save automatically.

---

## Pull Request Guidelines

1. Fork the repo and create a branch: `git checkout -b feat/my-feature`
2. Make your changes
3. Run tests: `pytest tests/`
4. Update docs if needed
5. Open a PR with a clear description of what and why

**PR title format:**
- `feat: add Mistral model pricing`
- `fix: correct Gemini 2.5 Flash output cost`
- `docs: improve MCP setup guide`
- `refactor: simplify token analyzer`

---

## Reporting Security Issues

Do NOT open public issues for security vulnerabilities. Email: security@tokenforge.dev

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

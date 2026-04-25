.PHONY: help install install-dev dev dev-backend dev-frontend test lint format type-check docker-up docker-down docker-build clean bench

PYTHON := python
PIP := pip
UVICORN := uvicorn
NPM := npm

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ─── Install ──────────────────────────────────────────────────────────────────

install: ## Install backend + frontend dependencies
	cd backend && $(PIP) install -r requirements.txt
	cd frontend && $(NPM) install

install-dev: ## Install dev dependencies
	cd backend && $(PIP) install -r requirements-dev.txt
	cd frontend && $(NPM) install

# ─── Development ─────────────────────────────────────────────────────────────

dev: ## Start both backend and frontend (requires two terminals or use tmux)
	@echo "Start backend:  make dev-backend"
	@echo "Start frontend: make dev-frontend"

dev-backend: ## Start FastAPI backend in dev mode
	@cp -n .env.example .env 2>/dev/null || true
	C:/Users/Meehu/AppData/Local/Programs/Python/Python312/python.exe -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Start Vite dev server
	cd frontend && $(NPM) run dev

# ─── Testing ─────────────────────────────────────────────────────────────────

test: ## Run backend test suite
	cd .. && $(PYTHON) -m pytest backend/tests -v --tb=short

test-cov: ## Run tests with coverage report
	cd .. && $(PYTHON) -m pytest backend/tests -v --cov=backend --cov-report=term-missing --cov-report=html

# ─── Code quality ────────────────────────────────────────────────────────────

lint: ## Run ruff linter
	ruff check backend/

format: ## Auto-format with ruff
	ruff format backend/

type-check: ## Run mypy type checker
	mypy backend/ --ignore-missing-imports

# ─── Docker ──────────────────────────────────────────────────────────────────

docker-build: ## Build Docker images
	docker-compose build

docker-up: ## Start all services with Docker Compose
	docker-compose up -d

docker-down: ## Stop all Docker services
	docker-compose down

docker-logs: ## Follow Docker logs
	docker-compose logs -f

docker-clean: ## Remove containers, volumes, and images
	docker-compose down -v --rmi local

# ─── Benchmarks ──────────────────────────────────────────────────────────────

bench: ## Run benchmark suite
	$(PYTHON) -m benchmarks.benchmark_suite

# ─── Utilities ───────────────────────────────────────────────────────────────

clean: ## Remove Python cache files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true

ollama-check: ## Check that Ollama is running and has the required model
	@curl -s http://localhost:11434/api/tags | python -m json.tool | grep -i "gemma" || echo "Warning: gemma4 not found. Run: ollama pull gemma4:latest"

# TokenForge Installation Guide

## Prerequisites

| Requirement | Version | Check |
|-------------|---------|-------|
| Python | 3.10+ | `python --version` |
| Node.js | 18+ | `node --version` |
| Git | any | `git --version` |
| Ollama | latest | `ollama --version` |
| RAM | 4 GB+ | — |

---

## Quick Install (All Platforms)

```bash
git clone https://github.com/tokenforge/tokenforge.git
cd tokenforge
python installer/install.py
python launcher/launch.py
```

The smart installer handles everything:
- Detects your OS and RAM
- Recommends the right AI model
- Creates Python virtual environment
- Installs all Python and npm dependencies
- Pulls the Ollama model
- Copies `.env` configuration

---

## Manual Installation

If the smart installer fails, follow these steps:

### 1. Install Ollama

**Windows:** Download from [ollama.com/download](https://ollama.com/download)

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Pull a model

```bash
# Recommended for 8+ GB RAM
ollama pull gemma4:latest

# Lighter option for 4–8 GB RAM
ollama pull gemma4:1b
```

### 3. Create Python virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

### 4. Install backend dependencies

```bash
pip install -r backend/requirements.txt
```

### 5. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

### 6. Configure environment

```bash
cp .env.example .env
# Edit .env to set OLLAMA_MODEL= to your pulled model name
```

### 7. Start services

**Backend:**
```bash
.venv/Scripts/python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

**Frontend (new terminal):**
```bash
cd frontend
npm run dev
```

Open **http://localhost:3001**

---

## Docker Installation

```bash
docker compose up
```

Services:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3001`

---

## Claude Desktop MCP Integration

1. Install [Claude Desktop](https://claude.ai/download)
2. Run `python installer/install.py` — config is written automatically
3. Restart Claude Desktop
4. Go to **Settings → Developer** — `tokenforge` should show **running**

### Manual MCP config (Windows Store Claude Desktop)

Edit: `%LocalAppData%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "tokenforge": {
      "command": "C:\\path\\to\\tokenforge\\.venv\\Scripts\\python.exe",
      "args": ["-m", "mcp_server.server"],
      "cwd": "C:\\path\\to\\tokenforge",
      "env": {
        "PYTHONPATH": "C:\\path\\to\\tokenforge",
        "OLLAMA_BASE_URL": "http://localhost:11434",
        "OLLAMA_MODEL": "gemma4:latest",
        "LLM_ADAPTER": "ollama"
      }
    }
  }
}
```

---

## Verifying Installation

```bash
# Backend health
curl http://localhost:8000/health

# Expected response
{"status":"healthy","llm_available":true,"embedding_available":true}

# List models
curl http://localhost:8000/models | python -m json.tool
```

---

## Updating

```bash
git pull
python installer/install.py  # re-runs dependency install
```

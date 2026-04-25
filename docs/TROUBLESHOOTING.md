# TokenForge Troubleshooting

## Backend won't start

**"Module not found" errors**
```bash
# Re-run installer to fix the virtual environment
python installer/install.py
```

**Port 8000 already in use**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Mac/Linux
lsof -ti:8000 | xargs kill
```

**Wrong Python interpreter**
Make sure you're using the `.venv` Python:
```bash
# Windows
.venv\Scripts\python.exe -m uvicorn backend.main:app --port 8000

# Mac/Linux
.venv/bin/python -m uvicorn backend.main:app --port 8000
```

---

## Frontend won't start

**"node_modules not found"**
```bash
cd frontend && npm install
```

**Port 3001 in use**
Edit `frontend/vite.config.ts` and change `port: 3001` to another port.

---

## Ollama issues

**"Ollama not found"**
- Install from [ollama.com/download](https://ollama.com/download)
- Make sure it's in your PATH

**Model not responding / slow**
```bash
# Check what models you have
ollama list

# Pull the right size for your RAM
ollama pull gemma4:1b      # 4–8 GB RAM
ollama pull gemma4:latest  # 16+ GB RAM

# Check Ollama is running
curl http://localhost:11434/api/tags
```

**optimize_prompt times out in Claude Desktop**
Gemma4 (12B) is large. On CPU-only machines it can take 2–5 minutes.
Use a smaller model:
```bash
ollama pull gemma4:1b
```
Then update `.env`: `OLLAMA_MODEL=gemma4:1b`

---

## MCP server issues (Claude Desktop)

**tokenforge shows "failed" in Settings → Developer**

1. Click "View Logs" — check the error message
2. Most common: `No module named 'mcp_server'`
   - Fix: Add `PYTHONPATH` to the MCP config (see Installation guide)
3. Check the config file location (Windows Store vs. Win32 install differ)

**Config location:**
- Win32 Claude Desktop: `%AppData%\Roaming\Claude\claude_desktop_config.json`
- Windows Store Claude Desktop: `%LocalAppData%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json`

**Test the MCP server manually:**
```bash
cd C:\path\to\tokenforge
.venv\Scripts\python.exe -m mcp_server.server
# Should hang (waiting for stdio input) — that's correct
# Ctrl+C to stop
```

---

## API returns 422 (Validation Error)

The model name you sent doesn't match the enum. Use:
```bash
curl http://localhost:8000/models | python -m json.tool
# Lists all valid model IDs
```

---

## "embedding_available: false" in health check

The sentence-transformers model isn't loaded. This happens on first run while the model downloads.
Wait 30 seconds and retry. Check backend logs:
```bash
cat backend_server.log | tail -20
```

---

## Getting more help

- Open an issue: [github.com/tokenforge/tokenforge/issues](https://github.com/tokenforge/tokenforge/issues)
- Check existing issues before opening a new one
- Include your OS, Python version, and the full error message

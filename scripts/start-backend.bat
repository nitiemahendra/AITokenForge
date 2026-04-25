@echo off
echo Starting TokenForge backend on http://localhost:8000 ...
cd /d %~dp0..
.venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

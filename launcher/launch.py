"""
TokenForge Launcher
===================
One-click launcher for the TokenForge development stack.

Usage:
    python launcher/launch.py

What it does:
  1. Prints a startup banner
  2. Runs health checks (Ollama running? ports 8000 / 3001 free?)
  3. Starts Ollama if not already running
  4. Starts the FastAPI backend via uvicorn inside .venv
  5. Starts the Vite frontend (npm run dev) inside frontend/
  6. Polls http://localhost:8000/health until the backend is ready (max 30 s)
  7. Opens http://localhost:3001 in the default browser
  8. Waits; handles Ctrl+C cleanly by terminating all child processes
"""

from __future__ import annotations

import os
import platform
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

# ---------------------------------------------------------------------------
# Project root is two levels up from this file: launcher/ -> project root
# ---------------------------------------------------------------------------
ROOT: Path = Path(__file__).resolve().parent.parent

BACKEND_PORT = 8000
FRONTEND_PORT = 3001
HEALTH_URL = f"http://localhost:{BACKEND_PORT}/health"
FRONTEND_URL = f"http://localhost:{FRONTEND_PORT}"
HEALTH_TIMEOUT_S = 30
HEALTH_POLL_INTERVAL_S = 1.0

# ---------------------------------------------------------------------------
# ANSI colour helpers
# ---------------------------------------------------------------------------
_IS_WIN = platform.system() == "Windows"
_ANSI   = sys.stdout.isatty() and (
    not _IS_WIN
    or os.environ.get("TERM_PROGRAM") in ("vscode", "alacritty", "mintty")
    or os.environ.get("WT_SESSION") is not None          # Windows Terminal
)

_R = "\033[0m"  if _ANSI else ""
_G = "\033[92m" if _ANSI else ""
_Y = "\033[93m" if _ANSI else ""
_RE = "\033[91m" if _ANSI else ""
_B = "\033[1m"  if _ANSI else ""
_C = "\033[96m" if _ANSI else ""


def ok(msg: str)     -> None: print(f"  {_G}✓{_R} {msg}")
def warn(msg: str)   -> None: print(f"  {_Y}⚠{_R} {msg}")
def err(msg: str)    -> None: print(f"  {_RE}✗{_R} {msg}")
def info(msg: str)   -> None: print(f"  {_C}→{_R} {msg}")
def bold(msg: str)   -> None: print(f"{_B}{msg}{_R}")


# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------

def print_banner() -> None:
    lines = [
        "╔══════════════════════════════════════╗",
        "║         TokenForge v1.0.0            ║",
        "║  AI Cost Optimization Infrastructure ║",
        "╚══════════════════════════════════════╝",
    ]
    print()
    for line in lines:
        print(f"  {_C}{_B}{line}{_R}")
    print()


# ---------------------------------------------------------------------------
# Health checks
# ---------------------------------------------------------------------------

def _is_port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) != 0


def _ollama_running() -> bool:
    """Return True if Ollama's HTTP API (port 11434) responds."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.0)
            return s.connect_ex(("127.0.0.1", 11434)) == 0
    except OSError:
        return False


def run_health_checks() -> tuple[bool, bool, bool]:
    """
    Returns (ollama_ok, backend_port_free, frontend_port_free).
    Prints status for each check.
    """
    bold("── Health Checks ─────────────────────────────────")

    ollama_ok = _ollama_running()
    if ollama_ok:
        ok("Ollama is already running (port 11434)")
    else:
        warn("Ollama is not running — will start it automatically")

    backend_free = _is_port_free(BACKEND_PORT)
    if backend_free:
        ok(f"Port {BACKEND_PORT} is free (backend)")
    else:
        err(f"Port {BACKEND_PORT} is already in use — backend cannot start")

    frontend_free = _is_port_free(FRONTEND_PORT)
    if frontend_free:
        ok(f"Port {FRONTEND_PORT} is free (frontend)")
    else:
        warn(f"Port {FRONTEND_PORT} is already in use — frontend may bind to a different port")

    print()
    return ollama_ok, backend_free, frontend_free


# ---------------------------------------------------------------------------
# Platform helpers
# ---------------------------------------------------------------------------

def _venv_python() -> Path:
    if _IS_WIN:
        return ROOT / ".venv" / "Scripts" / "python.exe"
    return ROOT / ".venv" / "bin" / "python"


def _start_ollama_cmd() -> list[str]:
    """Return the shell command that starts the Ollama server in the background."""
    system = platform.system()
    if system == "Windows":
        # 'ollama serve' is the cross-platform sub-command
        return ["ollama", "serve"]
    return ["ollama", "serve"]


# ---------------------------------------------------------------------------
# Process management
# ---------------------------------------------------------------------------

_PROCESSES: list[subprocess.Popen[bytes]] = []


def _register(proc: subprocess.Popen[bytes]) -> subprocess.Popen[bytes]:
    _PROCESSES.append(proc)
    return proc


def _kill_all() -> None:
    for proc in _PROCESSES:
        if proc.poll() is None:
            try:
                if _IS_WIN:
                    subprocess.call(
                        ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                else:
                    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            except Exception:
                try:
                    proc.terminate()
                except Exception:
                    pass


def _signal_handler(sig: int, frame: object) -> None:  # noqa: ARG001
    print(f"\n\n{_Y}  Ctrl+C received — shutting down all services …{_R}\n")
    _kill_all()
    sys.exit(0)


# ---------------------------------------------------------------------------
# Service starters
# ---------------------------------------------------------------------------

def start_ollama() -> subprocess.Popen[bytes] | None:
    bold("── Starting Ollama ───────────────────────────────")
    cmd = _start_ollama_cmd()
    info(f"Running: {' '.join(cmd)}")
    try:
        kwargs: dict = dict(
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if not _IS_WIN:
            kwargs["start_new_session"] = True
        proc = subprocess.Popen(cmd, **kwargs)
        _register(proc)

        # Wait briefly for Ollama to bind its port
        for _ in range(10):
            time.sleep(0.5)
            if _ollama_running():
                ok("Ollama started successfully")
                return proc
        warn("Ollama did not respond within 5 s — continuing anyway")
        return proc
    except FileNotFoundError:
        err("'ollama' executable not found. Run the installer first.")
        return None
    except Exception as exc:
        err(f"Failed to start Ollama: {exc}")
        return None


def start_backend() -> subprocess.Popen[bytes] | None:
    bold("── Starting Backend (FastAPI / uvicorn) ──────────")
    python_bin = _venv_python()
    if not python_bin.exists():
        err(f".venv Python not found at {python_bin}")
        err("Run 'python installer/install.py' first.")
        return None

    cmd = [
        str(python_bin), "-m", "uvicorn",
        "backend.main:app",
        "--host", "0.0.0.0",
        "--port", str(BACKEND_PORT),
        "--reload",
    ]
    info(f"Running: {' '.join(cmd)}")
    info(f"CWD: {ROOT}")

    try:
        kwargs: dict = dict(cwd=str(ROOT))
        if not _IS_WIN:
            kwargs["start_new_session"] = True
        proc = subprocess.Popen(cmd, **kwargs)
        _register(proc)
        ok(f"Backend process started (PID {proc.pid})")
        return proc
    except Exception as exc:
        err(f"Failed to start backend: {exc}")
        return None


def start_frontend() -> subprocess.Popen[bytes] | None:
    bold("── Starting Frontend (Vite / npm run dev) ────────")
    frontend_dir = ROOT / "frontend"
    if not frontend_dir.exists():
        err(f"frontend/ directory not found at {frontend_dir}")
        return None

    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        warn("node_modules not found — run 'python installer/install.py' first")

    cmd = ["npm", "run", "dev"]
    info(f"Running: {' '.join(cmd)}")
    info(f"CWD: {frontend_dir}")

    try:
        kwargs: dict = dict(cwd=str(frontend_dir))
        if not _IS_WIN:
            kwargs["start_new_session"] = True
        proc = subprocess.Popen(cmd, **kwargs)
        _register(proc)
        ok(f"Frontend process started (PID {proc.pid})")
        return proc
    except FileNotFoundError:
        err("'npm' not found. Install Node.js at https://nodejs.org/")
        return None
    except Exception as exc:
        err(f"Failed to start frontend: {exc}")
        return None


# ---------------------------------------------------------------------------
# Backend readiness probe
# ---------------------------------------------------------------------------

def wait_for_backend(timeout: float = HEALTH_TIMEOUT_S) -> bool:
    bold("── Waiting for Backend ───────────────────────────")
    info(f"Polling {HEALTH_URL} (timeout {timeout:.0f} s) …")
    deadline = time.monotonic() + timeout
    attempt = 0
    while time.monotonic() < deadline:
        attempt += 1
        try:
            with urllib.request.urlopen(HEALTH_URL, timeout=2) as resp:
                if resp.status == 200:
                    ok(f"Backend is healthy (attempt {attempt})")
                    return True
        except (urllib.error.URLError, OSError):
            pass
        time.sleep(HEALTH_POLL_INTERVAL_S)
        print(f"    … still waiting ({attempt})", end="\r", flush=True)

    print()  # clear the \r line
    err(f"Backend did not become healthy within {timeout:.0f} s")
    return False


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main() -> int:
    # Register Ctrl+C handler early
    signal.signal(signal.SIGINT, _signal_handler)
    if not _IS_WIN:
        signal.signal(signal.SIGTERM, _signal_handler)

    print_banner()

    # ── Health checks ────────────────────────────────────────────────────────
    ollama_ok, backend_free, _frontend_free = run_health_checks()

    if not backend_free:
        err(f"Port {BACKEND_PORT} is occupied. Stop the existing process and retry.")
        return 1

    # ── Start Ollama if needed ───────────────────────────────────────────────
    if not ollama_ok:
        print()
        if start_ollama() is None:
            warn("Continuing without confirmed Ollama status …")
    print()

    # ── Start backend ────────────────────────────────────────────────────────
    backend_proc = start_backend()
    print()
    if backend_proc is None:
        err("Backend failed to start — aborting.")
        _kill_all()
        return 1

    # ── Start frontend ───────────────────────────────────────────────────────
    frontend_proc = start_frontend()
    print()

    # ── Wait for backend readiness ───────────────────────────────────────────
    backend_ready = wait_for_backend()
    print()

    # ── Open browser ─────────────────────────────────────────────────────────
    if backend_ready and frontend_proc is not None:
        info(f"Opening browser → {FRONTEND_URL}")
        try:
            # Small delay to let Vite finish binding
            time.sleep(2)
            webbrowser.open(FRONTEND_URL)
        except Exception:
            warn(f"Could not open browser automatically. Navigate to {FRONTEND_URL}")
    elif not backend_ready:
        warn("Backend health check failed — check terminal output for errors.")

    # ── Running summary ──────────────────────────────────────────────────────
    bold("── Services Running ──────────────────────────────")
    ok(f"Backend  → http://localhost:{BACKEND_PORT}")
    ok(f"Frontend → {FRONTEND_URL}")
    ok(f"API docs → http://localhost:{BACKEND_PORT}/docs")
    print()
    bold(f"  Press {_Y}Ctrl+C{_B} to stop all services and exit.")
    print()

    # ── Keep alive — poll child processes ────────────────────────────────────
    try:
        while True:
            time.sleep(2)
            # If backend died, report and exit
            if backend_proc.poll() is not None:
                print()
                err(f"Backend process exited unexpectedly (code {backend_proc.returncode}).")
                err("Check the terminal output above for error details.")
                _kill_all()
                return 1
            # Frontend dying is less critical (Vite may restart on its own)
            if frontend_proc is not None and frontend_proc.poll() is not None:
                warn(f"Frontend process exited (code {frontend_proc.returncode}).")
                frontend_proc = None  # stop re-checking
    except KeyboardInterrupt:
        # Handled by signal handler, but catch here as a safety net
        _signal_handler(signal.SIGINT, None)

    return 0


if __name__ == "__main__":
    sys.exit(main())

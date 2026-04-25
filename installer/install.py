"""
TokenForge Installer
====================
Cross-platform smart installer for the TokenForge project.

Usage:
    python installer/install.py

What it does:
  1. Validates Python >= 3.10
  2. Detects available RAM and recommends the right Ollama model
  3. Checks Ollama is installed (prints install URL if not)
  4. Pulls the recommended Ollama model if not already present
  5. Creates a .venv virtual environment
  6. Installs backend Python dependencies into .venv
  7. Installs frontend npm dependencies
  8. Copies .env.example -> .env if .env is absent
  9. Prints a success summary
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Project root is two levels up from this file: installer/ -> project root
# ---------------------------------------------------------------------------
ROOT: Path = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# ANSI colour helpers (disabled automatically on Windows when not supported)
# ---------------------------------------------------------------------------
_ANSI_SUPPORTED = sys.stdout.isatty() and platform.system() != "Windows" or (
    platform.system() == "Windows"
    and os.environ.get("TERM_PROGRAM") in ("vscode", "alacritty", "mintty")
)

_RESET  = "\033[0m"  if _ANSI_SUPPORTED else ""
_GREEN  = "\033[92m" if _ANSI_SUPPORTED else ""
_RED    = "\033[91m" if _ANSI_SUPPORTED else ""
_YELLOW = "\033[93m" if _ANSI_SUPPORTED else ""
_BOLD   = "\033[1m"  if _ANSI_SUPPORTED else ""


def ok(msg: str) -> None:
    print(f"  {_GREEN}✓{_RESET} {msg}")


def fail(msg: str) -> None:
    print(f"  {_RED}✗{_RESET} {msg}")


def action(msg: str) -> None:
    print(f"  {_YELLOW}→{_RESET} {msg}")


def section(title: str) -> None:
    print(f"\n{_BOLD}{'─' * 50}{_RESET}")
    print(f"{_BOLD}  {title}{_RESET}")
    print(f"{_BOLD}{'─' * 50}{_RESET}")


# ---------------------------------------------------------------------------
# RAM detection (psutil preferred, fallback to platform-specific commands)
# ---------------------------------------------------------------------------

def _get_ram_gb() -> float | None:
    """Return total RAM in GB, or None if undetectable."""
    # Try psutil first (fast path)
    try:
        import psutil  # type: ignore[import]
        return psutil.virtual_memory().total / (1024 ** 3)
    except ImportError:
        pass

    system = platform.system()
    try:
        if system == "Windows":
            out = subprocess.check_output(
                ["wmic", "ComputerSystem", "get", "TotalPhysicalMemory"],
                text=True,
                stderr=subprocess.DEVNULL,
            )
            for line in out.splitlines():
                line = line.strip()
                if line.isdigit():
                    return int(line) / (1024 ** 3)
        elif system == "Darwin":
            out = subprocess.check_output(
                ["sysctl", "-n", "hw.memsize"],
                text=True,
                stderr=subprocess.DEVNULL,
            )
            return int(out.strip()) / (1024 ** 3)
        elif system == "Linux":
            mem_info = Path("/proc/meminfo").read_text()
            for line in mem_info.splitlines():
                if line.startswith("MemTotal:"):
                    kb = int(line.split()[1])
                    return kb / (1024 ** 2)
    except Exception:
        pass
    return None


def recommend_model(ram_gb: float | None) -> str:
    if ram_gb is None:
        action("Could not detect RAM — defaulting to gemma4:1b (safe choice).")
        return "gemma4:1b"
    if ram_gb < 8:
        return "gemma4:1b"
    if ram_gb <= 16:
        return "gemma4:4b"
    return "gemma4:latest"


# ---------------------------------------------------------------------------
# Step helpers
# ---------------------------------------------------------------------------

def check_python_version() -> bool:
    section("Step 1 — Python version")
    major, minor = sys.version_info[:2]
    if (major, minor) < (3, 10):
        fail(f"Python {major}.{minor} detected. TokenForge requires Python >= 3.10.")
        fail("Download the latest Python at https://www.python.org/downloads/")
        return False
    ok(f"Python {major}.{minor} — OK")
    return True


def detect_ram_and_model() -> str:
    section("Step 2 — RAM detection & model recommendation")
    ram = _get_ram_gb()
    if ram is not None:
        ok(f"Detected RAM: {ram:.1f} GB")
    model = recommend_model(ram)
    if ram is not None:
        label = (
            "< 8 GB  → gemma4:1b (lightweight)"
            if ram < 8 else
            "8–16 GB → gemma4:4b (balanced)"
            if ram <= 16 else
            "> 16 GB → gemma4:latest (full quality)"
        )
        action(f"Tier: {label}")
    ok(f"Recommended model: {_BOLD}{model}{_RESET}")
    return model


def check_ollama(model: str) -> bool:
    section("Step 3 — Ollama")
    ollama_bin = shutil.which("ollama")
    if ollama_bin is None:
        fail("Ollama is not installed or not on PATH.")
        print()
        print("  Install Ollama for your platform:")
        print("    Windows / Mac / Linux → https://ollama.com/download")
        print("    Linux (one-liner):      curl -fsSL https://ollama.com/install.sh | sh")
        print()
        fail("Please install Ollama, then re-run this installer.")
        return False
    ok(f"Ollama found: {ollama_bin}")

    # Check if model is already pulled
    action(f"Checking whether model '{model}' is already pulled …")
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if model in result.stdout:
            ok(f"Model '{model}' is already available locally.")
            return True
    except Exception:
        pass  # Fall through to pull attempt

    action(f"Pulling model '{model}' via Ollama (this may take several minutes) …")
    try:
        subprocess.run(
            ["ollama", "pull", model],
            check=True,
        )
        ok(f"Model '{model}' pulled successfully.")
        return True
    except subprocess.CalledProcessError as exc:
        fail(f"'ollama pull {model}' failed with exit code {exc.returncode}.")
        fail("Make sure Ollama is running (`ollama serve`) and try again.")
        return False
    except FileNotFoundError:
        fail("'ollama' command not found after PATH check — this should not happen.")
        return False


def create_venv() -> bool:
    section("Step 4 — Virtual environment")
    venv_dir = ROOT / ".venv"
    if venv_dir.exists():
        ok(".venv already exists — skipping creation.")
        return True
    action("Creating .venv …")
    try:
        subprocess.run(
            [sys.executable, "-m", "venv", str(venv_dir)],
            check=True,
        )
        ok(".venv created successfully.")
        return True
    except subprocess.CalledProcessError as exc:
        fail(f"Failed to create .venv (exit code {exc.returncode}).")
        return False


def _venv_python() -> Path:
    """Return the path to the Python executable inside .venv."""
    if platform.system() == "Windows":
        return ROOT / ".venv" / "Scripts" / "python.exe"
    return ROOT / ".venv" / "bin" / "python"


def install_backend_deps() -> bool:
    section("Step 5 — Backend Python dependencies")
    req_file = ROOT / "backend" / "requirements.txt"
    if not req_file.exists():
        fail(f"requirements.txt not found at {req_file}")
        return False

    python_bin = _venv_python()
    if not python_bin.exists():
        fail(f".venv Python not found at {python_bin} — did Step 4 succeed?")
        return False

    action(f"Installing from {req_file.relative_to(ROOT)} …")
    try:
        subprocess.run(
            [
                str(python_bin), "-m", "pip", "install",
                "--upgrade", "pip",
                "--quiet",
            ],
            check=True,
            cwd=str(ROOT),
        )
        subprocess.run(
            [
                str(python_bin), "-m", "pip", "install",
                "-r", str(req_file),
                "--quiet",
            ],
            check=True,
            cwd=str(ROOT),
        )
        ok("Backend dependencies installed.")
        return True
    except subprocess.CalledProcessError as exc:
        fail(f"pip install failed (exit code {exc.returncode}).")
        return False


def install_frontend_deps() -> bool:
    section("Step 6 — Frontend npm dependencies")
    frontend_dir = ROOT / "frontend"
    if not frontend_dir.exists():
        fail(f"frontend/ directory not found at {frontend_dir}")
        return False

    npm_bin = shutil.which("npm")
    if npm_bin is None:
        fail("npm is not installed or not on PATH.")
        fail("Install Node.js (includes npm) at https://nodejs.org/")
        return False
    ok(f"npm found: {npm_bin}")

    node_modules = frontend_dir / "node_modules"
    if node_modules.exists():
        ok("node_modules already present — skipping npm install.")
        return True

    action("Running 'npm install' inside frontend/ …")
    try:
        subprocess.run(
            ["npm", "install"],
            check=True,
            cwd=str(frontend_dir),
        )
        ok("Frontend dependencies installed.")
        return True
    except subprocess.CalledProcessError as exc:
        fail(f"npm install failed (exit code {exc.returncode}).")
        return False


def copy_env_file() -> bool:
    section("Step 7 — Environment configuration (.env)")
    env_file    = ROOT / ".env"
    env_example = ROOT / ".env.example"

    if env_file.exists():
        ok(".env already exists — leaving it untouched.")
        return True

    if not env_example.exists():
        action(".env.example not found — skipping .env creation.")
        action("You may need to create .env manually before running the app.")
        return True  # Non-fatal

    shutil.copy(env_example, env_file)
    ok(f"Copied .env.example → .env")
    action("Review .env and fill in any required values before starting.")
    return True


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main() -> int:
    print(f"\n{_BOLD}{'=' * 50}{_RESET}")
    print(f"{_BOLD}   TokenForge Installer{_RESET}")
    print(f"{_BOLD}{'=' * 50}{_RESET}")
    print(f"  Project root: {ROOT}")

    failures: list[str] = []

    # Step 1 — Python version
    if not check_python_version():
        failures.append("Python version check")

    # Step 2 — RAM & model
    model = detect_ram_and_model()

    # Step 3 — Ollama
    if not check_ollama(model):
        failures.append("Ollama setup")

    # Step 4 — .venv
    if not create_venv():
        failures.append("Virtual environment creation")

    # Step 5 — Backend deps (only if venv is usable)
    if not install_backend_deps():
        failures.append("Backend dependency installation")

    # Step 6 — Frontend deps
    if not install_frontend_deps():
        failures.append("Frontend dependency installation")

    # Step 7 — .env
    copy_env_file()

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    section("Installation Summary")
    if not failures:
        ok("All steps completed successfully!")
        print()
        print(f"  {_BOLD}Next step:{_RESET}")
        print(f"    {_GREEN}python launcher/launch.py{_RESET}")
        print()
        return 0
    else:
        fail(f"{len(failures)} step(s) encountered errors:")
        for item in failures:
            fail(f"  • {item}")
        print()
        action("Fix the errors above and re-run this installer.")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())

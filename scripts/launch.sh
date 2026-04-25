#!/usr/bin/env bash
# ==============================================================
# TokenForge — Unix one-click launcher (macOS / Linux)
# Usage:  bash scripts/launch.sh
#         or make the file executable first:
#           chmod +x scripts/launch.sh && ./scripts/launch.sh
# ==============================================================

set -euo pipefail

# Resolve the project root (parent of the scripts/ directory).
# Works regardless of where the script is called from.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Change to the project root so all relative paths inside launch.py resolve.
cd "${ROOT}"

# ── Verify Python 3 is available ────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo ""
    echo "  [ERROR] 'python3' not found on PATH."
    echo "  Install Python 3.10+ from https://www.python.org/downloads/"
    echo "  or via your system package manager:"
    echo "    macOS:  brew install python@3.12"
    echo "    Ubuntu: sudo apt install python3.12"
    echo ""
    exit 1
fi

# ── Ensure the script is executable (self-healing) ──────────────────────────
SELF="${BASH_SOURCE[0]}"
if [[ ! -x "${SELF}" ]]; then
    chmod +x "${SELF}"
fi

# ── Run the launcher ─────────────────────────────────────────────────────────
python3 launcher/launch.py
EXIT_CODE=$?

if [[ ${EXIT_CODE} -ne 0 ]]; then
    echo ""
    echo "  [ERROR] TokenForge exited with code ${EXIT_CODE}."
    echo "  Review the output above for details."
    echo ""
    exit ${EXIT_CODE}
fi

exit 0

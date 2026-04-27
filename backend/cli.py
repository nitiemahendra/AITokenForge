"""
CLI entry point: `tokenforge` / `tokenforge-server`

Starts the TokenForge FastAPI backend with uvicorn.
"""

from __future__ import annotations

import argparse
import sys


def serve() -> None:
    try:
        import uvicorn
    except ImportError:
        sys.stderr.write("uvicorn is not installed. Run: pip install aitokenforge\n")
        sys.exit(1)

    parser = argparse.ArgumentParser(
        prog="tokenforge",
        description="TokenForge — AI Cost Optimization Infrastructure",
    )
    parser.add_argument("--host", default="0.0.0.0", help="Bind host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Bind port (default: 8000)")
    parser.add_argument("--reload", action="store_true", default=False, help="Enable auto-reload")
    parser.add_argument("--log-level", default="info", help="Log level (default: info)")
    args = parser.parse_args()

    sys.stderr.write(f"\n  TokenForge v1.0.1  —  http://localhost:{args.port}/docs\n\n")
    uvicorn.run(
        "backend.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level,
    )


if __name__ == "__main__":
    serve()

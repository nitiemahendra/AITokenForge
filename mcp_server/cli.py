"""
CLI entry point: `tokenforge-mcp`

Starts the TokenForge MCP server (stdio transport for Claude Desktop).
"""

from __future__ import annotations

import asyncio
import sys


def run() -> None:
    try:
        from mcp_server.server import main
    except ImportError as exc:
        print(f"Failed to import MCP server: {exc}", file=sys.stderr)
        print("Run: pip install aitokenforge", file=sys.stderr)
        sys.exit(1)

    asyncio.run(main())


if __name__ == "__main__":
    run()

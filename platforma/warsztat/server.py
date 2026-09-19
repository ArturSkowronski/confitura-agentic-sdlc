"""Serwer MCP „warsztat”: jedyne, co agent wykonawca widzi ze świata. Streamable HTTP na :3000/mcp.

Uruchomienie w klastrze: CRD MCPServer (kmcp) z obrazem fabryka-warsztat; kagent odkrywa narzędzia sam.
Lokalnie: WORK_DIR=. python3 server.py
"""

from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP

from workspace import Workspace

ws = Workspace.from_env()
mcp = FastMCP("warsztat", host="0.0.0.0", port=int(os.environ.get("PORT", "3000")), stateless_http=True)


@mcp.tool()
def list_files(path: str = ".") -> str:
    """List files and directories in the repository (path relative to the repo root)."""
    return ws.list_files(path)


@mcp.tool()
def read_file(path: str) -> str:
    """Contents of a file from the repository."""
    return ws.read_file(path)


@mcp.tool()
def write_file(path: str, content: str) -> str:
    """Write the whole file (overwrites). Protected paths are rejected."""
    return ws.write_file(path, content)


@mcp.tool()
def run_build(module: str = "") -> str:
    """Run `mvn -B -q verify` in system/ (optionally only one module, e.g. pricing-lib). Returns the exit code and the tail of the log."""
    return ws.run_build(module)


@mcp.tool()
def git_diff() -> str:
    """Changed files and the diff against the last commit."""
    return ws.git_diff()


if __name__ == "__main__":
    print(f"warsztat: {ws.root}, chronione={ws.protected}, ukryte={ws.hidden}")
    mcp.run(transport="streamable-http")

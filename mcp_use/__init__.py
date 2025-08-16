# ruff: noqa: I001
"""
mcp_use - An MCP library for LLMs.

This library provides a unified interface for connecting different LLMs
to MCP tools through existing LangChain adapters.
"""

from importlib.metadata import PackageNotFoundError, version

from . import observability
try:  # pragma: no cover - optional heavy deps
    from .agents.mcpagent import MCPAgent
except Exception:  # pragma: no cover
    MCPAgent = None  # type: ignore[assignment]

try:  # pragma: no cover
    from .client import MCPClient
    from .connectors import BaseConnector, HttpConnector, StdioConnector, WebSocketConnector
    from .session import MCPSession
except Exception:  # pragma: no cover
    MCPClient = BaseConnector = HttpConnector = StdioConnector = WebSocketConnector = MCPSession = None  # type: ignore[assignment]

try:  # pragma: no cover
    from .config import load_config_file
except Exception:  # pragma: no cover
    load_config_file = None  # type: ignore[assignment]

from .logging import MCP_USE_DEBUG, Logger, logger

try:  # pragma: no cover
    __version__ = version("mcp-use")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0"

__all__ = [
    "MCPAgent",
    "MCPClient",
    "MCPSession",
    "BaseConnector",
    "StdioConnector",
    "WebSocketConnector",
    "HttpConnector",
    "load_config_file",
    "logger",
    "MCP_USE_DEBUG",
    "Logger",
    "set_debug",
    "observability",
]


# Helper function to set debug mode
def set_debug(debug=2):
    """Set the debug mode for mcp_use.

    Args:
        debug: Whether to enable debug mode (default: True)
    """
    Logger.set_debug(debug)

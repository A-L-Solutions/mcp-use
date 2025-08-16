"""Simple CLI entrypoint for the orchestrator demo."""
from __future__ import annotations

import argparse
import asyncio

from mcp_use.client import MCPClient

from .config import load_graph_config
from .events import ConsoleEventBus
from .orchestrator import MCPOrchestrator


async def main(prompt: str) -> None:
    client = MCPClient.from_config_file("examples/lovable_mini/servers.json")
    cfg = load_graph_config("examples/lovable_mini/graph.json")
    orch = MCPOrchestrator(client, cfg, event_bus=ConsoleEventBus())
    async for chunk in orch.astream(prompt):
        print(chunk, end="", flush=True)


if __name__ == "__main__":  # pragma: no cover - CLI utility
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", nargs="?", default="Hello")
    args = parser.parse_args()
    asyncio.run(main(args.prompt))

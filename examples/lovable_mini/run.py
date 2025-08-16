import asyncio, json, sys
from mcp_use.client import MCPClient
from mcp_use.orchestrator.orchestrator import MCPOrchestrator
from mcp_use.orchestrator.config import load_graph_config

async def main():
    prompt = sys.argv[1] if len(sys.argv) > 1 else \
        "Generate a simple landing page for 'Mars Technosoft' (hero, features, contact)."

    client = MCPClient.from_config_file("examples/lovable_mini/servers.json")
    cfg = load_graph_config("examples/lovable_mini/graph.json")
    orch = MCPOrchestrator(client, cfg)

    async for chunk in orch.astream(prompt):
        print(chunk, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main())

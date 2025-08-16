import pytest

from mcp_use.client import MCPClient
from mcp_use.orchestrator import MCPOrchestrator
from mcp_use.orchestrator.config import AgentConfig, GraphConfig


class DummyAgent:
    def __init__(self, *args, **kwargs):
        self.tools_used_names = []

    async def run(self, prompt: str) -> str:
        self.tools_used_names.append("dummy")
        return f"{prompt}-done"


def make_client() -> MCPClient:
    return MCPClient(config={"servers": [], "llm": {}})


@pytest.mark.asyncio
async def test_minimal_flow(monkeypatch):
    monkeypatch.setattr("mcp_use.orchestrator.builder.MCPAgent", DummyAgent)

    cfg = GraphConfig(
        start="router",
        limits={"global_steps": 5},
        human_approval_after=[],
        agents={
            "router": AgentConfig(type="rule", max_steps=1),
            "A": AgentConfig(allow_tools=["dummy"], max_steps=1),
            "B": AgentConfig(allow_tools=["dummy"], max_steps=1),
        },
        edges=[("router", "A"), ("A", "B"), ("B", "END")],
    )
    orch = MCPOrchestrator(make_client(), cfg)
    state = await orch.run("hi")
    assert state["artifacts"]["A_output"] == "hi-done"
    assert state["artifacts"]["B_output"] == "hi-done"
    assert state["last_hop"] == "B"

    cfg_bad = GraphConfig(
        start="router",
        limits={"global_steps": 5},
        human_approval_after=[],
        agents={
            "router": AgentConfig(type="rule", max_steps=1),
            "A": AgentConfig(allow_tools=[], max_steps=1),
        },
        edges=[("router", "A"), ("A", "END")],
    )
    orch_bad = MCPOrchestrator(make_client(), cfg_bad)
    with pytest.raises(RuntimeError):
        await orch_bad.run("hi")

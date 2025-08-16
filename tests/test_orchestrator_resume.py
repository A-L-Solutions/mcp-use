import pytest

from mcp_use.client import MCPClient
from mcp_use.orchestrator import MCPOrchestrator
from mcp_use.orchestrator.checkpointer import JsonCheckpointer
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
async def test_resume(monkeypatch, tmp_path):
    monkeypatch.setattr("mcp_use.orchestrator.builder.MCPAgent", DummyAgent)
    checkpointer = JsonCheckpointer(base_path=tmp_path.as_posix())

    cfg = GraphConfig(
        start="router",
        limits={"global_steps": 5},
        human_approval_after=["coder"],
        agents={
            "router": AgentConfig(type="rule", max_steps=1),
            "coder": AgentConfig(allow_tools=["dummy"], max_steps=1),
            "verifier": AgentConfig(allow_tools=["dummy"], max_steps=1),
        },
        edges=[("router", "coder"), ("coder", "verifier"), ("verifier", "END")],
    )
    orch = MCPOrchestrator(make_client(), cfg, checkpointer=checkpointer)
    state = await orch.run("hi")
    run_id = orch._run_id  # type: ignore[attr-defined]
    assert state["last_hop"] == "coder"
    assert "verifier_output" not in state["artifacts"]

    resumed = await orch.resume(run_id)
    assert resumed["artifacts"]["verifier_output"] == "hi-done"

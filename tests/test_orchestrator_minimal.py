import asyncio
import pytest

# ruff: noqa: I001

from mcp_use.orchestrator import (
    AgentConfig,
    GraphConfig,
    MCPOrchestrator,
    builder,
)


class StubAgent:
    def __init__(self, output: str, tools: list[str] | None = None):
        self.output = output
        self.tools_used_names = tools or []

    async def run(self, prompt: str) -> str:
        return self.output


def test_run_and_policy(monkeypatch):
    cfg = GraphConfig(
        start="router",
        limits={"global_steps": 5},
        human_approval_after=[],
        agents={
            "router": AgentConfig(type="rule", max_steps=1),
            "A": AgentConfig(allow_tools=[], max_steps=2),
            "B": AgentConfig(allow_tools=["ok"], max_steps=2),
        },
        edges=[("router", "A"), ("A", "B"), ("B", "END")],
    )

    agents = {"A": StubAgent("a"), "B": StubAgent("b", tools=["ok"])}

    monkeypatch.setattr(builder, "build_agents", lambda client, cfg: agents)

    orch = MCPOrchestrator(client=None, graph_cfg=cfg)  # type: ignore[arg-type]
    state = asyncio.run(orch.run("hi"))
    assert state["artifacts"]["A_output"] == "a"
    assert state["artifacts"]["B_output"] == "b"
    assert state["last_hop"] == "B"

    agents_bad = {"A": StubAgent("a"), "B": StubAgent("b", tools=["bad"])}
    monkeypatch.setattr(builder, "build_agents", lambda client, cfg: agents_bad)
    orch = MCPOrchestrator(client=None, graph_cfg=cfg)  # type: ignore[arg-type]
    with pytest.raises(Exception):
        asyncio.run(orch.run("hi"))

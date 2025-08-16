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
    def __init__(self, output: str):
        self.output = output
        self.tools_used_names: list[str] = []

    async def run(self, prompt: str) -> str:
        return self.output


def test_resume(monkeypatch, tmp_path):
    cfg = GraphConfig(
        start="router",
        limits={"global_steps": 5},
        human_approval_after=["coder"],
        agents={
            "router": AgentConfig(type="rule", max_steps=1),
            "coder": AgentConfig(allow_tools=[], max_steps=2),
            "verifier": AgentConfig(allow_tools=[], max_steps=2),
        },
        edges=[("router", "coder"), ("coder", "verifier"), ("verifier", "END")],
    )

    agents = {"coder": StubAgent("code"), "verifier": StubAgent("verified")}
    monkeypatch.setattr(builder, "build_agents", lambda client, cfg: agents)

    orch = MCPOrchestrator(client=None, graph_cfg=cfg)  # type: ignore[arg-type]
    state = asyncio.run(orch.run("hi"))
    assert state["last_hop"] == "coder"
    run_id = orch._last_run_id
    assert run_id is not None

    state2 = asyncio.run(orch.resume(run_id))
    assert state2["final_answer"] == "verified"

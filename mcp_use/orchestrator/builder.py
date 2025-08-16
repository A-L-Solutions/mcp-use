"""Helpers to construct agents and graphs."""
# ruff: noqa: I001
from __future__ import annotations

from collections.abc import Callable
from typing import Any, TYPE_CHECKING

try:  # pragma: no cover
    from langgraph.types import Command
except Exception:  # pragma: no cover
    class Command:  # type: ignore
        def __init__(self, goto: str | None = None, update: dict | None = None):
            self.goto = goto
            self.update = update or {}

from .agent_node import AgentNode
from .config import GraphConfig
from .events import EventBus
from .policy import Budgets, ToolPolicy
from .router import RuleRouterNode

if TYPE_CHECKING:  # pragma: no cover
    from mcp_use.agents.mcpagent import MCPAgent  # noqa: F401
    from mcp_use.client import MCPClient  # noqa: F401


START = "START"
END = "END"


class SimpleGraphApp:
    """Very small graph executor used when LangGraph isn't available."""

    def __init__(self, nodes: dict[str, Callable], edges: dict[str, list[str]], start: str) -> None:
        self.nodes = nodes
        self.edges = edges
        self.start = start

    async def astep(self, state, node_name: str) -> str:
        node_fn = self.nodes[node_name]
        cmd: Command | None = await node_fn(state)
        if cmd and getattr(cmd, "update", None):
            state.update(cmd.update)
        next_node = getattr(cmd, "goto", None)
        if next_node is None:
            next_node = self.edges.get(node_name, [END])[0]
        return next_node


def build_agents(client: Any, cfg: GraphConfig) -> dict[str, Any]:  # pragma: no cover - heavy
    """Instantiate ``MCPAgent`` instances for config."""
    agents: dict[str, Any] = {}
    for _name, acfg in cfg.agents.items():
        if acfg.type == "rule":
            continue
        # Placeholder: caller expected to supply properly initialised MCPAgent via monkeypatching in tests
        raise RuntimeError("build_agents requires external LLM setup; monkeypatch in tests")
    return agents


def compile_graph(client: Any, cfg: GraphConfig, event_bus: EventBus | None = None) -> SimpleGraphApp:
    agents = build_agents(client, cfg)
    nodes: dict[str, Callable] = {}
    edges: dict[str, list[str]] = {}

    for src, dst in cfg.edges:
        edges.setdefault(src, []).append(dst)

    # router node
    nodes["router"] = RuleRouterNode(edges)

    for name, acfg in cfg.agents.items():
        if acfg.type == "rule":
            continue
        policy = ToolPolicy(acfg.allow_tools or []) if acfg.allow_tools is not None else None
        budgets = Budgets(max_steps=acfg.max_steps)
        nodes[name] = AgentNode(name, agents.get(name), policy=policy, budgets=budgets, event_bus=event_bus)

    return SimpleGraphApp(nodes, edges, cfg.start)

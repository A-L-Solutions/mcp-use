"""Utilities to build agents and compile graphs."""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from typing import Any

try:  # pragma: no cover - optional
    from langgraph.constants import END, START
    from langgraph.graph import StateGraph
    from langgraph.types import Command
except Exception:  # pragma: no cover - fallback
    from dataclasses import dataclass

    START = "START"
    END = "END"

    @dataclass
    class Command:  # type: ignore
        goto: str | None = None
        update: dict | None = None

    class StateGraph:
        def __init__(self, _state):
            self.nodes: dict[str, Callable[[Any], Any]] = {}
            self.edges: defaultdict[str, list[str]] = defaultdict(list)

        def add_node(self, name: str, fn: Callable[[Any], Any]) -> None:
            self.nodes[name] = fn

        def add_edge(self, src: str, dst: str) -> None:
            self.edges[src].append(dst)

        def compile(self) -> CompiledGraph:
            return CompiledGraph(self.nodes, self.edges)

    class CompiledGraph:
        def __init__(self, nodes, edges):
            self.nodes = nodes
            self.edges = edges

        async def astep(self, state, node: str):
            fn = self.nodes[node]
            result = await fn(state)
            if isinstance(result, Command):
                if result.update:
                    state.update(result.update)
                goto = result.goto
            else:
                goto = None
            if goto is None:
                goto = self.edges.get(node, [END])[0]
            return state, goto

    StateGraphCompiled = CompiledGraph

from mcp_use.agents import MCPAgent

from .agent_node import AgentNode
from .config import GraphConfig
from .policy import Budgets, ToolPolicy
from .router import RuleRouterNode
from .state import RunState


def _load_llm(client, model_override: str | None = None):
    cfg = getattr(client, "config", {}).get("llm", {})
    model = model_override or cfg.get("model")
    provider = cfg.get("provider")
    if provider == "openai" and model:
        try:  # pragma: no cover - optional
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(model=model)
        except Exception:  # pragma: no cover - fallback
            return None
    return None


def build_agents(client, cfg: GraphConfig) -> dict[str, MCPAgent]:
    agents: dict[str, MCPAgent] = {}
    for name, acfg in cfg.agents.items():
        if acfg.type == "rule":
            continue
        llm = _load_llm(client, acfg.model)
        agent = MCPAgent(
            llm=llm,  # type: ignore[arg-type]
            client=client,
            max_steps=acfg.max_steps,
            use_server_manager=True,
        )
        agents[name] = agent
    return agents


def compile_graph(client, cfg: GraphConfig):
    agents = build_agents(client, cfg)
    graph = StateGraph(RunState)

    # Router
    router_cfg = cfg.agents.get(cfg.start)
    if router_cfg and router_cfg.type == "rule":
        router = RuleRouterNode(cfg.edge_map)
        graph.add_node(cfg.start, router)
    else:
        raise ValueError("start node must be a router")

    # Agent nodes
    for name, agent in agents.items():
        policy = ToolPolicy(acfg.allow_tools if (acfg := cfg.agents[name]).allow_tools else [])
        budgets = Budgets(max_steps=acfg.max_steps)
        graph.add_node(name, AgentNode(name, agent, policy, budgets))

    # Edges
    graph.add_edge(START, cfg.start)
    for src, dst in cfg.edges:
        graph.add_edge(src, dst)
    graph.add_edge(END, END)

    app = graph.compile()
    return app

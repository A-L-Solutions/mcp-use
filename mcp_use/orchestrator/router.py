"""Routing nodes."""
from __future__ import annotations

try:  # pragma: no cover - optional
    from langgraph.types import Command
except Exception:  # pragma: no cover - fallback
    from dataclasses import dataclass

    @dataclass
    class Command:  # type: ignore
        goto: str | None = None
        update: dict | None = None

from .state import RunState


class RuleRouterNode:
    """Deterministic router following edges and ``last_hop``."""

    def __init__(self, edges: dict[str, list[str]]) -> None:
        self.edges = edges

    async def __call__(self, state: RunState) -> Command:
        last = state.get("last_hop") or "router"
        next_nodes = self.edges.get(last, [])
        goto = next_nodes[0] if next_nodes else "END"
        return Command(goto=goto)


class SupervisorRouterNode:
    """Router that asks an MCPAgent which node to run next."""

    def __init__(self, agent) -> None:
        self.agent = agent

    async def __call__(self, state: RunState) -> Command:  # pragma: no cover - simple
        prompt = state.get("next_prompt") or ""
        resp = await self.agent.run(prompt)
        try:
            import json

            data = json.loads(resp)
            goto = data.get("next")
        except Exception:
            goto = None
        return Command(goto=goto)

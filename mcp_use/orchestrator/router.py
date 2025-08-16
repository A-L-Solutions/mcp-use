"""Simple routing nodes."""
from __future__ import annotations

try:  # pragma: no cover
    from langgraph.types import Command
except Exception:  # pragma: no cover
    class Command:  # type: ignore
        def __init__(self, goto: str | None = None, update: dict | None = None):
            self.goto = goto
            self.update = update or {}

from .state import RunState


class RuleRouterNode:
    """Deterministic router based on static edges."""

    def __init__(self, edges: dict[str, list[str]]) -> None:
        self.edges = edges

    async def __call__(self, state: RunState) -> Command:  # pragma: no cover - simple
        last = state.get("last_hop") or "router"
        nexts = self.edges.get(last, [])
        goto = nexts[0] if nexts else "END"
        return Command(goto=goto)

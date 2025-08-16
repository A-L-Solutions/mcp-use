"""LangGraph node wrapping an ``MCPAgent``."""
from __future__ import annotations

from typing import Any

try:  # pragma: no cover - best effort
    from langgraph.types import Command
except Exception:  # pragma: no cover - fallback for environments without langgraph
    class Command:  # type: ignore
        def __init__(self, goto: str | None = None, update: dict[str, Any] | None = None):
            self.goto = goto
            self.update = update or {}

from typing import TYPE_CHECKING

from .events import EventBus
from .policy import Budgets, ToolPolicy, enforce_before_agent_step
from .state import RunState, get_ns, set_ns_value

if TYPE_CHECKING:  # pragma: no cover
    from mcp_use.agents.mcpagent import MCPAgent  # noqa: F401


class AgentNode:
    """Wrapper that turns an ``MCPAgent`` into a callable node."""

    def __init__(
        self,
        name: str,
        agent: Any,
        policy: ToolPolicy | None = None,
        budgets: Budgets | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self.name = name
        self.agent = agent
        self.policy = policy
        self.budgets = budgets
        self.event_bus = event_bus or EventBus()

    async def __call__(self, state: RunState) -> Command:
        self.event_bus.on_step_start(self.name, state)
        try:
            ns = get_ns(state, self.name)
            ns["tools"] = getattr(self.agent, "tools_used_names", [])
            enforce_before_agent_step(state, self.name, self.policy, self.budgets)

            result = await self.agent.run(state.get("next_prompt", ""))
            state["artifacts"][f"{self.name}_output"] = result
            set_ns_value(state, self.name, "last", result)
            state["messages"].append({"role": self.name, "content": result})
            return Command(update={"next_prompt": result})
        finally:
            self.event_bus.on_step_end(self.name, state)

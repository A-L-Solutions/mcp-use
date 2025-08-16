"""LangGraph node wrapper around :class:`MCPAgent`."""
from __future__ import annotations

from typing import Any

try:  # pragma: no cover - optional
    from langgraph.types import Command
except Exception:  # pragma: no cover - fallback
    from dataclasses import dataclass

    @dataclass
    class Command:  # type: ignore
        goto: str | None = None
        update: dict | None = None

from .policy import Budgets, ToolPolicy, enforce_before_agent_step
from .state import RunState, get_ns


class AgentNode:
    """Wrap an :class:`MCPAgent` for graph execution."""

    def __init__(self, name: str, agent: Any, policy: ToolPolicy | None = None, budgets: Budgets | None = None):
        self.name = name
        self.agent = agent
        self.policy = policy
        self.budgets = budgets

    async def __call__(self, state: RunState) -> Command:
        prompt = state.get("next_prompt") or ""
        enforce_before_agent_step(state, self.name, self.policy, self.budgets)

        result = await self.agent.run(prompt)  # type: ignore[no-untyped-call]

        agent_ns = get_ns(state, self.name)
        agent_ns["last"] = result
        agent_ns["steps"] = agent_ns.get("steps", 0) + 1
        state["artifacts"][f"{self.name}_output"] = result
        state["messages"].append(result)
        state["budget"]["steps"] += 1

        # enforce tool policy after step
        if self.policy and self.policy.allowed_tools:
            for tool in getattr(self.agent, "tools_used_names", []):
                if tool not in self.policy.allowed_tools:
                    raise RuntimeError(f"tool {tool} not allowed for {self.name}")

        return Command(update={"next_prompt": result})

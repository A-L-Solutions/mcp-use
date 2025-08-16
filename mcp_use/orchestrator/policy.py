"""Policy and budget utilities."""
from __future__ import annotations

from dataclasses import dataclass

from .state import RunState, get_ns


@dataclass
class ToolPolicy:
    """Simple policy describing allowed tools for an agent."""

    allowed_tools: list[str]
    disallowed_tools: list[str] | None = None


@dataclass
class Budgets:
    max_steps: int | None = None
    max_tokens: int | None = None
    max_seconds: int | None = None


def enforce_before_agent_step(
    state: RunState, agent_name: str, policy: ToolPolicy | None, budgets: Budgets | None
) -> None:
    """Verify budget limits before executing an agent step."""
    steps = state["budget"]["steps"]
    max_steps = state["budget"].get("max_steps")
    if max_steps is not None and steps >= max_steps:
        raise RuntimeError("global step budget exceeded")

    if budgets and budgets.max_steps is not None:
        agent_ns = get_ns(state, agent_name)
        taken = agent_ns.get("steps", 0)
        if taken >= budgets.max_steps:
            raise RuntimeError(f"{agent_name} exceeded step budget")

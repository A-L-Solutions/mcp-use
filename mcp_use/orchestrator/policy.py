"""Budget and tool policy enforcement."""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .state import RunState


@dataclass
class ToolPolicy:
    """Simple allow/deny policy for tools."""

    allowed_tools: list[str]
    disallowed_tools: list[str] | None = None


@dataclass
class Budgets:
    """Per-agent and global budgets."""

    max_steps: int | None = None
    max_tokens: int | None = None
    max_seconds: int | None = None


class PolicyViolation(Exception):
    """Raised when a policy check fails."""


def _tool_check(tools: Iterable[str], policy: ToolPolicy | None) -> None:
    if not policy:
        return
    for tool in tools:
        if tool not in policy.allowed_tools:
            raise PolicyViolation(f"Tool '{tool}' not allowed")
        if policy.disallowed_tools and tool in policy.disallowed_tools:
            raise PolicyViolation(f"Tool '{tool}' disallowed")


def enforce_before_agent_step(
    state: RunState, agent_name: str, policy: ToolPolicy | None, budgets: Budgets | None
) -> None:
    """Check budgets and tool policy before an agent step."""
    if budgets and budgets.max_steps is not None:
        steps = state.setdefault("budget", {}).setdefault("steps", 0)
        if steps >= budgets.max_steps:
            raise PolicyViolation(f"Max steps exceeded for {agent_name}")
        state["budget"]["steps"] = steps + 1

    tools = getattr(state.get("ns", {}).get(agent_name, {}), "get", lambda x, default=None: default)(
        "tools", []
    )
    if isinstance(tools, list):
        _tool_check(tools, policy)

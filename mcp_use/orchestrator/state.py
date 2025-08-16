"""State management utilities for the orchestrator."""
from __future__ import annotations

from typing import Any, TypedDict


class RunState(TypedDict, total=False):
    """State shared between orchestrator nodes."""

    messages: list[dict[str, Any]]
    artifacts: dict[str, Any]
    ns: dict[str, dict[str, Any]]
    next_prompt: str | None
    final_answer: str | None
    budget: dict[str, Any]
    approvals: list[str]
    last_hop: str | None


def init_state(prompt: str, global_steps: int) -> RunState:
    """Initialise a ``RunState`` for a new run."""
    return RunState(
        messages=[{"role": "user", "content": prompt}],
        artifacts={},
        ns={},
        next_prompt=prompt,
        final_answer=None,
        budget={"steps": 0, "max_steps": global_steps},
        approvals=[],
        last_hop=None,
    )


def get_ns(state: RunState, name: str) -> dict[str, Any]:
    """Get the namespace dictionary for an agent."""
    return state.setdefault("ns", {}).setdefault(name, {})


def set_ns_value(state: RunState, name: str, key: str, value: Any) -> None:
    """Set a value in an agent's namespace."""
    get_ns(state, name)[key] = value


def trim_messages(state: RunState, limit: int = 50) -> None:
    """Trim the message history to ``limit`` items."""
    msgs = state.get("messages", [])
    if len(msgs) > limit:
        state["messages"] = msgs[-limit:]

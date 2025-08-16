"""State helpers for the orchestrator."""
from __future__ import annotations

import uuid
from collections.abc import MutableMapping
from typing import Any, TypedDict


class RunState(TypedDict, total=False):
    """State tracked across orchestrator runs."""

    messages: list[str]
    artifacts: dict[str, str]
    ns: dict[str, dict[str, Any]]
    next_prompt: str | None
    final_answer: str | None
    budget: dict[str, int]
    approvals: dict[str, bool]
    last_hop: str | None
    run_id: str


def init_state(prompt: str, global_steps: int) -> RunState:
    """Create an initial :class:`RunState` for a new run."""
    return {
        "messages": [prompt],
        "artifacts": {},
        "ns": {},
        "next_prompt": prompt,
        "final_answer": None,
        "budget": {"steps": 0, "max_steps": global_steps},
        "approvals": {},
        "last_hop": None,
        "run_id": uuid.uuid4().hex,
    }


def get_ns(state: MutableMapping[str, Any], name: str) -> MutableMapping[str, Any]:
    """Return the namespace for an agent, creating it if needed."""
    ns = state.setdefault("ns", {})  # type: ignore[assignment]
    return ns.setdefault(name, {})


def trim_messages(state: RunState, max_messages: int) -> None:
    """Trim message history to the last ``max_messages`` items."""
    msgs = state.get("messages")
    if msgs is not None and len(msgs) > max_messages:
        state["messages"] = msgs[-max_messages:]

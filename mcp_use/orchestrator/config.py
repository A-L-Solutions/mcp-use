"""Graph configuration models using dataclasses."""
from __future__ import annotations

import json
from dataclasses import dataclass, field


@dataclass
class AgentConfig:
    """Configuration for a single agent."""

    type: str = "agent"
    allow_tools: list[str] | None = field(default_factory=list)
    max_steps: int = 5
    model: str | None = None


@dataclass
class GraphConfig:
    start: str
    limits: dict[str, int] = field(default_factory=dict)
    human_approval_after: list[str] = field(default_factory=list)
    agents: dict[str, AgentConfig] = field(default_factory=dict)
    edges: list[tuple[str, str]] = field(default_factory=list)


def load_graph_config(path: str) -> GraphConfig:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    agents = {k: AgentConfig(**v) for k, v in data["agents"].items()}
    data["agents"] = agents
    return GraphConfig(**data)

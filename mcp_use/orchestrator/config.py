"""Configuration models for the orchestrator."""
from __future__ import annotations

import json
from dataclasses import dataclass, field


@dataclass
class AgentConfig:
    type: str = "agent"
    allow_tools: list[str] | None = None
    max_steps: int = 0
    model: str | None = None


@dataclass
class GraphConfig:
    start: str
    limits: dict[str, int] = field(default_factory=dict)
    human_approval_after: list[str] = field(default_factory=list)
    agents: dict[str, AgentConfig] = field(default_factory=dict)
    edges: list[tuple[str, str]] = field(default_factory=list)

    @property
    def edge_map(self) -> dict[str, list[str]]:
        m: dict[str, list[str]] = {}
        for src, dst in self.edges:
            m.setdefault(src, []).append(dst)
        return m


def load_graph_config(path: str) -> GraphConfig:
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    agents = {k: AgentConfig(**v) for k, v in data.get("agents", {}).items()}
    edges = [tuple(e) for e in data.get("edges", [])]
    return GraphConfig(
        start=data.get("start", ""),
        limits=data.get("limits", {}),
        human_approval_after=data.get("human_approval_after", []),
        agents=agents,
        edges=edges,
    )

"""Multi-agent orchestrator built on a simple LangGraph-like engine."""
# ruff: noqa: I001
from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from typing import Any, TYPE_CHECKING

from .builder import END, compile_graph
from .checkpointer import JsonCheckpointer
from .config import GraphConfig
from .events import ConsoleEventBus, EventBus
from .state import RunState, init_state

if TYPE_CHECKING:  # pragma: no cover
    from mcp_use.client import MCPClient  # noqa: F401


class MCPOrchestrator:
    """Coordinate multiple ``MCPAgent`` instances via a simple graph."""

    def __init__(
        self,
        client: Any,
        graph_cfg: dict | GraphConfig,
        checkpointer: JsonCheckpointer | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self.client = client
        self.cfg = graph_cfg if isinstance(graph_cfg, GraphConfig) else GraphConfig(**graph_cfg)
        self.checkpointer = checkpointer or JsonCheckpointer()
        self.event_bus = event_bus or ConsoleEventBus()
        self.app = compile_graph(client, self.cfg, event_bus=self.event_bus)
        self._last_run_id: str | None = None

    async def _run_loop(self, state: RunState, node: str, run_id: str) -> RunState:
        current = node
        while current != END:
            next_node = await self.app.astep(state, current)
            state["last_hop"] = current
            meta = {"next_node": next_node}
            self.checkpointer.save(run_id, state, meta)
            if current in self.cfg.human_approval_after:
                return state  # pause for approval
            current = next_node
        state["final_answer"] = state.get("next_prompt")
        self.checkpointer.save(run_id, state, {"next_node": END})
        return state

    async def run(self, prompt: str) -> RunState:
        run_id = str(uuid.uuid4())
        self._last_run_id = run_id
        state = init_state(prompt, self.cfg.limits.get("global_steps", 0))
        return await self._run_loop(state, self.app.start, run_id)

    async def astream(self, prompt: str) -> AsyncIterator[str | dict]:
        state = await self.run(prompt)
        for msg in state["messages"][1:]:  # skip initial user prompt
            yield msg["content"]

    async def resume(self, run_id: str) -> RunState:
        state, meta = self.checkpointer.load(run_id)
        next_node = meta.get("next_node", self.app.start)
        return await self._run_loop(state, next_node, run_id)

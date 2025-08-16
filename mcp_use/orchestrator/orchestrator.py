"""High level orchestration entrypoint."""
from __future__ import annotations

from collections.abc import AsyncIterator

try:  # pragma: no cover - optional
    from langgraph.constants import END
except Exception:  # pragma: no cover - fallback
    END = "END"

from .builder import compile_graph
from .checkpointer import JsonCheckpointer
from .config import GraphConfig
from .events import EventBus
from .state import RunState, init_state


class MCPOrchestrator:
    """Coordinate multiple :class:`MCPAgent` instances via a graph."""

    def __init__(
        self,
        client,
        graph_cfg: dict | GraphConfig,
        *,
        checkpointer: JsonCheckpointer | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self.client = client
        self.cfg = graph_cfg if isinstance(graph_cfg, GraphConfig) else GraphConfig(**graph_cfg)
        self.checkpointer = checkpointer
        self.event_bus = event_bus or EventBus()
        self.app = compile_graph(client, self.cfg)
        self._run_id: str | None = None

    async def run(self, prompt: str) -> RunState:
        state = init_state(prompt, self.cfg.limits.get("global_steps", 50))
        self._run_id = state["run_id"]
        node = self.cfg.start
        while node != END:
            self.event_bus.on_step_start(node, state)
            state, next_node = await self.app.astep(state, node)
            state["last_hop"] = node
            self.event_bus.on_step_end(node, state)
            if node in self.cfg.human_approval_after and next_node != END:
                if self.checkpointer:
                    self.checkpointer.save(self._run_id, state, {"next_node": next_node})
                break
            node = next_node
        if node == END and self.checkpointer:
            self.checkpointer.save(self._run_id, state, {"next_node": END})
        return state

    async def astream(self, prompt: str) -> AsyncIterator[str | dict]:
        state = init_state(prompt, self.cfg.limits.get("global_steps", 50))
        self._run_id = state["run_id"]
        node = self.cfg.start
        while node != END:
            self.event_bus.on_step_start(node, state)
            state, next_node = await self.app.astep(state, node)
            state["last_hop"] = node
            yield state.get("ns", {}).get(node, {}).get("last", "")
            self.event_bus.on_step_end(node, state)
            if node in self.cfg.human_approval_after and next_node != END:
                if self.checkpointer:
                    self.checkpointer.save(self._run_id, state, {"next_node": next_node})
                break
            node = next_node
        if node == END and self.checkpointer:
            self.checkpointer.save(self._run_id, state, {"next_node": END})

    async def resume(self, run_id: str) -> RunState:
        if not self.checkpointer:
            raise RuntimeError("no checkpointer configured")
        state, meta = self.checkpointer.load(run_id)
        node = meta.get("next_node", self.cfg.start)
        while node != END:
            self.event_bus.on_step_start(node, state)
            state, next_node = await self.app.astep(state, node)
            state["last_hop"] = node
            self.event_bus.on_step_end(node, state)
            node = next_node
        self.checkpointer.save(run_id, state, {"next_node": END})
        return state

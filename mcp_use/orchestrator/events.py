"""Event bus used by the orchestrator."""
from __future__ import annotations

from typing import Any

from .state import RunState


class EventBus:
    """Base class for event handling."""

    def on_step_start(self, name: str, state: RunState) -> None:  # pragma: no cover - simple default
        pass

    def on_step_end(self, name: str, state: RunState) -> None:  # pragma: no cover - simple default
        pass

    def on_tool_call(self, agent: str, tool_name: str, args: Any) -> None:  # pragma: no cover
        pass

    def on_handoff(self, src: str, dst: str) -> None:  # pragma: no cover
        pass

    def on_error(self, name: str, exc: Exception) -> None:  # pragma: no cover
        pass


class ConsoleEventBus(EventBus):
    """Very small console logger for events."""

    def _log(self, msg: str) -> None:
        print(msg, flush=True)

    def on_step_start(self, name: str, state: RunState) -> None:  # pragma: no cover - trivial
        self._log(f"--- switching to {name} ---")

    def on_error(self, name: str, exc: Exception) -> None:  # pragma: no cover - trivial
        self._log(f"error in {name}: {exc}")

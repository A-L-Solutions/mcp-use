"""Lightweight event bus for orchestration."""
from __future__ import annotations

from .state import RunState


class EventBus:
    """Base event bus with no-op handlers."""

    def on_step_start(self, name: str, state: RunState) -> None:  # pragma: no cover - default
        pass

    def on_step_end(self, name: str, state: RunState) -> None:  # pragma: no cover - default
        pass

    def on_tool_call(self, agent: str, tool_name: str, args: dict | None = None) -> None:  # pragma: no cover - default
        pass

    def on_handoff(self, src: str, dst: str) -> None:  # pragma: no cover - default
        pass

    def on_error(self, name: str, exc: Exception) -> None:  # pragma: no cover - default
        pass


class ConsoleEventBus(EventBus):
    """Simple console logger implementation."""

    def on_step_start(self, name: str, state: RunState) -> None:  # pragma: no cover - logging
        print(f"--- switching to {name} ---")

    def on_handoff(self, src: str, dst: str) -> None:  # pragma: no cover - logging
        print(f"handoff: {src} -> {dst}")

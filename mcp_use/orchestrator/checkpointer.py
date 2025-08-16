"""Checkpoint persistence for orchestrator runs."""
from __future__ import annotations

import json
import os

from .state import RunState


class JsonCheckpointer:
    """Store run state to JSON files."""

    def __init__(self, base_path: str = ".mcp_use_runs") -> None:
        self.base_path = base_path

    def _path(self, run_id: str) -> str:
        return os.path.join(self.base_path, f"{run_id}.json")

    def save(self, run_id: str, state: RunState, meta: dict) -> None:
        os.makedirs(self.base_path, exist_ok=True)
        with open(self._path(run_id), "w", encoding="utf-8") as fh:
            json.dump({"state": state, "meta": meta}, fh)

    def load(self, run_id: str) -> tuple[RunState, dict]:
        with open(self._path(run_id), encoding="utf-8") as fh:
            data = json.load(fh)
        return data["state"], data.get("meta", {})

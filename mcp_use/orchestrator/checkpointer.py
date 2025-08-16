"""JSON checkpointer for run state."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .state import RunState


class JsonCheckpointer:
    """Persist ``RunState`` as JSON files."""

    def __init__(self, root: str = ".mcp_use_runs") -> None:
        self.root = Path(root)
        self.root.mkdir(exist_ok=True)

    def _path(self, run_id: str) -> Path:
        return self.root / f"{run_id}.json"

    def save(self, run_id: str, state: RunState, meta: dict[str, Any]) -> None:
        data = {"state": state, "meta": meta}
        with self._path(run_id).open("w", encoding="utf-8") as f:
            json.dump(data, f)

    def load(self, run_id: str) -> tuple[RunState, dict[str, Any]]:
        path = self._path(run_id)
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data["state"], data.get("meta", {})

"""Process-wide context for MCP tools (repo root, loaded config)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

_ctx: AppContext | None = None


@dataclass(frozen=True)
class AppContext:
    repo_root: Path
    config: dict[str, Any]

    def path(self, *parts: str) -> Path:
        return self.repo_root.joinpath(*parts)


def init_ctx(repo_root: Path, config: dict[str, Any]) -> None:
    global _ctx
    _ctx = AppContext(repo_root=repo_root.resolve(), config=config)


def get_ctx() -> AppContext:
    if _ctx is None:
        raise RuntimeError("prestonotes_mcp context not initialized")
    return _ctx

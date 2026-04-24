"""Input validation, rate limiting, and audit logging for MCP tools."""

from __future__ import annotations

import json
import re
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from prestonotes_mcp.runtime import get_ctx

_rate_bucket: int = 0
_rate_count: int = 0


def _security_cfg() -> dict[str, Any]:
    ctx = get_ctx()
    sec = ctx.config.get("security", {})
    return sec if isinstance(sec, dict) else {}


def validate_customer_name(name: str) -> str:
    """Return stripped name or raise ValueError."""
    n = (name or "").strip()
    if not n:
        raise ValueError("customer_name is required")
    pat = _security_cfg().get("customer_name_pattern") or r"^[A-Za-z0-9_][A-Za-z0-9 _\-]{0,63}$"
    if not re.match(pat, n):
        raise ValueError(f"Invalid customer_name (pattern): {name!r}")
    if ".." in n or "/" in n or "\\" in n:
        raise ValueError("customer_name must not contain path segments")
    return n


def customer_dir(customer_name: str) -> Path:
    """Resolved path under MyNotes/Customers/{customer} — must stay within repo."""
    ctx = get_ctx()
    name = validate_customer_name(customer_name)
    base = ctx.path("MyNotes", "Customers", name).resolve()
    root = ctx.path("MyNotes", "Customers").resolve()
    try:
        base.relative_to(root)
    except ValueError as exc:
        raise ValueError("Invalid customer path") from exc
    return base


def check_rate_limit() -> None:
    global _rate_bucket, _rate_count
    lim = int(_security_cfg().get("rate_limit_per_minute", 30))
    now = int(time.time() // 60)
    if now != _rate_bucket:
        _rate_bucket = now
        _rate_count = 0
    _rate_count += 1
    if _rate_count > lim:
        raise RuntimeError(f"Rate limit exceeded ({lim} tool calls per minute). Wait and retry.")


def check_mutation_json_size(payload: str) -> None:
    max_b = int(_security_cfg().get("max_mutation_json_bytes", 524288))
    if len(payload.encode("utf-8")) > max_b:
        raise ValueError(f"mutations_json exceeds max size ({max_b} bytes)")


def check_call_record_json_size(payload: str) -> None:
    max_b = int(_security_cfg().get("max_call_record_json_bytes", 2_097_152))
    if len(payload.encode("utf-8")) > max_b:
        raise ValueError(f"record_json exceeds max size ({max_b} bytes)")


def _audit_path() -> Path:
    ctx = get_ctx()
    paths = ctx.config.get("paths", {})
    rel = "logs/mcp-audit.log"
    if isinstance(paths, dict) and paths.get("audit_log_rel"):
        rel = str(paths["audit_log_rel"])
    return ctx.path(*rel.split("/"))


def _write_audit(payload: dict[str, Any]) -> None:
    if not _security_cfg().get("audit_tool_calls", True):
        return
    p = _audit_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")


@contextmanager
def tool_scope(tool_name: str, **kwargs: Any) -> Iterator[None]:
    """Rate limit + audit around a tool body."""
    check_rate_limit()
    summary = json.dumps(kwargs, default=str)[:1900]
    t0 = time.perf_counter()
    try:
        yield
    except Exception as exc:
        _write_audit(
            {
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "tool": tool_name,
                "ok": False,
                "args": summary,
                "error": str(exc)[:2000],
                "ms": int((time.perf_counter() - t0) * 1000),
            }
        )
        raise
    else:
        _write_audit(
            {
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "tool": tool_name,
                "ok": True,
                "args": summary,
                "ms": int((time.perf_counter() - t0) * 1000),
            }
        )

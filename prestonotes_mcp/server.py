"""FastMCP entrypoint — prestoNotes MCP tools and resources (v2)."""

from __future__ import annotations

import json
import os
import re
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

from prestonotes_mcp.call_records import (
    call_records_path,
    read_call_record_files,
    rebuild_transcript_index,
    transcript_index_path,
    validate_call_id,
    validate_call_record_object,
    validate_call_type_filter,
)
from prestonotes_mcp.config import (
    auth_login_command_for_user,
    gcloud_account_for_auth,
    gdrive_base_from_config,
    google_auth_terminal_fix_fields,
    load_config,
    mynotes_root_folder_id,
    repo_root_from_env_or_file,
)
from prestonotes_mcp.exec_helper import repo_root, run_shell_script, run_uv_script
from prestonotes_mcp.journey import append_challenge_transition, write_journey_timeline_markdown
from prestonotes_mcp.ledger_v2 import append_ledger_v2_row, validate_ledger_v2_row
from prestonotes_mcp.runtime import AppContext, init_ctx
from prestonotes_mcp.security import (
    check_call_record_json_size,
    check_journey_timeline_size,
    check_mutation_json_size,
    customer_dir,
    tool_scope,
    validate_customer_name,
)

mcp = FastMCP(
    "prestonotes",
    instructions=(
        "prestoNotes MCP v2: customer notes, Google Docs, ledger, sync, call records, journey. "
        "For writes (write_doc, write_call_record, write_journey_timeline, update_challenge_state, "
        "append_ledger_v2, bootstrap_customer with dry_run=false), sync_notes, sync_transcripts: "
        "show the user the plan first and obtain approval in chat before calling. "
        "Mutation path: approved mutation JSON → write_doc (prestonotes_gdoc/update-gdoc-customer-notes.py). "
        "Call records: JSON per docs/project_spec §7.1 under MyNotes/Customers/<name>/call-records/. "
        "run_pipeline is not available in v2. "
        "Before discover_doc or read_doc, call check_google_auth if unsure whether gcloud is logged in. "
        "If any Google tool returns run_in_terminal_to_fix, show that exact command to the user first "
        "(from their .cursor/mcp.json env: GCLOUD_AUTH_LOGIN_COMMAND or GCLOUD_ACCOUNT) so they can "
        "authenticate in Terminal, then retry. "
        "Use one customer per chat session."
    ),
)


def _defaults() -> dict[str, Any]:
    from prestonotes_mcp.runtime import get_ctx

    d = get_ctx().config.get("defaults", {})
    return d if isinstance(d, dict) else {}


def _doc_schema_path(ctx: AppContext) -> str:
    paths = ctx.config.get("paths", {})
    return str(
        paths.get("doc_schema", "prestonotes_gdoc/config/doc-schema.yaml"),
    )


def _rel_path(p: str) -> Path:
    root = repo_root().resolve()
    path = (root / p).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError("path must stay inside the repository") from exc
    return path


# ---------------------------------------------------------------------------
# Read tools
# ---------------------------------------------------------------------------


@mcp.tool
def check_google_auth() -> str:
    """Verify gcloud can get an access token for Google Docs/Drive API. On failure, the response includes run_in_terminal_to_fix — the full command to paste in Terminal (from Cursor .cursor/mcp.json env + prestonotes-mcp.yaml). MCP cannot open a browser; you must run that command locally."""
    with tool_scope("check_google_auth"):
        from prestonotes_mcp.runtime import get_ctx

        ctx = get_ctx()
        cfg = ctx.config
        fix_cmd = auth_login_command_for_user(cfg)
        acct = gcloud_account_for_auth(cfg)
        cmd = ["gcloud", "auth", "print-access-token"]
        if acct:
            cmd.extend(["--account", acct])
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        token = (proc.stdout or "").strip()
        if proc.returncode == 0 and token:
            return json.dumps(
                {
                    "ok": True,
                    "message": "Google access token obtained successfully.",
                    "gcloud_account_used": acct
                    or "(gcloud default account — set GCLOUD_ACCOUNT in .cursor/mcp.json env to pin an account)",
                    "run_in_terminal_if_token_expires": fix_cmd,
                }
            )
        err = (proc.stderr or proc.stdout or "").strip()
        return json.dumps(
            {
                "ok": False,
                "message": "Could not get a Google access token. Copy run_in_terminal_to_fix into your Terminal, complete login, then retry your API tool.",
                "error_detail": err[-6000:],
                "run_in_terminal_to_fix": fix_cmd,
                "gcloud_account_configured": acct or None,
            }
        )


@mcp.tool
def list_customers() -> str:
    """List customer folder names under MyNotes/Customers (local mirror)."""
    with tool_scope("list_customers"):
        root = repo_root()
        d = root / "MyNotes" / "Customers"
        if not d.is_dir():
            return json.dumps(
                {"customers": [], "note": "MyNotes/Customers not found — run sync first."}
            )
        names = sorted(p.name for p in d.iterdir() if p.is_dir() and not p.name.startswith("."))
        return json.dumps({"customers": names, "count": len(names)})


@mcp.tool
def get_customer_status(customer_name: str) -> str:
    """Return quick filesystem status for a customer: transcripts, ledger, audit log presence."""
    with tool_scope("get_customer_status", customer_name=customer_name):
        validate_customer_name(customer_name)
        cdir = customer_dir(customer_name)
        if not cdir.is_dir():
            return json.dumps({"error": f"Customer folder not found: {cdir}", "exists": False})
        tdir = cdir / "Transcripts"
        transcripts: list[dict[str, Any]] = []
        if tdir.is_dir():
            for p in sorted(
                tdir.glob("_MASTER_TRANSCRIPT_*.txt"), key=lambda x: x.stat().st_mtime, reverse=True
            ):
                transcripts.append(
                    {
                        "file": p.name,
                        "mtime_utc": datetime.fromtimestamp(
                            p.stat().st_mtime, tz=timezone.utc
                        ).isoformat(),
                        "bytes": p.stat().st_size,
                    }
                )
        ledger_glob = (
            list((cdir / "AI_Insights").glob("*-History-Ledger.md"))
            if (cdir / "AI_Insights").is_dir()
            else []
        )
        audit = cdir / "pnotes_agent_log.md"
        return json.dumps(
            {
                "exists": True,
                "path": str(cdir),
                "transcript_files": transcripts[:10],
                "transcript_count": len(transcripts),
                "ledger_files": [p.name for p in ledger_glob],
                "audit_log_exists": audit.is_file(),
            }
        )


@mcp.tool
def discover_doc(customer_name: str) -> str:
    """Find the Google Doc ID for a customer's Notes document. Requires MYNOTES_ROOT_FOLDER_ID (env or config)."""
    with tool_scope("discover_doc", customer_name=customer_name):
        from prestonotes_mcp.runtime import get_ctx

        validate_customer_name(customer_name)
        ctx = get_ctx()
        rid = mynotes_root_folder_id(ctx.config)
        if not rid:
            return json.dumps(
                {
                    "error": "Set MYNOTES_ROOT_FOLDER_ID in .cursor/mcp.json env (Google Drive folder ID for MyNotes root).",
                }
            )
        proc = run_uv_script(
            "prestonotes_gdoc/update-gdoc-customer-notes.py",
            "discover",
            "--customer",
            customer_name,
            "--root-folder-id",
            rid,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        if proc.returncode != 0:
            err = {
                "error": "discover failed",
                "exit_code": proc.returncode,
                "output": out[-8000:],
                **google_auth_terminal_fix_fields(ctx.config),
            }
            return json.dumps(err)
        return json.dumps({"output": out.strip(), "exit_code": proc.returncode})


@mcp.tool
def read_doc(doc_id: str, include_internal: bool = True) -> str:
    """Read a customer Notes Google Doc and return the JSON section map."""
    with tool_scope("read_doc", doc_id=doc_id, include_internal=include_internal):
        from prestonotes_mcp.runtime import get_ctx

        doc_id = (doc_id or "").strip()
        if not doc_id or not re.match(r"^[A-Za-z0-9_-]{10,}$", doc_id):
            raise ValueError("doc_id looks invalid")
        ctx = get_ctx()
        cfg = _doc_schema_path(ctx)
        args = ["read", "--doc-id", doc_id, "--config", cfg]
        if include_internal:
            args.append("--include-internal")
        proc = run_uv_script("prestonotes_gdoc/update-gdoc-customer-notes.py", *args)
        out = proc.stdout or ""
        err = proc.stderr or ""
        if proc.returncode != 0:
            return json.dumps(
                {
                    "error": "read failed",
                    "exit_code": proc.returncode,
                    "stderr": err[-8000:],
                    **google_auth_terminal_fix_fields(ctx.config),
                }
            )
        return (
            out.strip()
            if out.strip()
            else json.dumps({"error": "empty stdout", "stderr": err[-2000:]})
        )


@mcp.tool
def read_transcripts(customer_name: str, limit: int | None = None) -> str:
    """Read latest N per-call transcript .txt files (newest first). Deprioritizes _MASTER_*.txt when other .txt files exist. See prestonotes-mcp.yaml.example for defaults."""
    with tool_scope("read_transcripts", customer_name=customer_name, limit=limit):
        validate_customer_name(customer_name)
        d = _defaults()
        raw_limit = int(d.get("transcript_limit", 3)) if limit is None else int(limit)
        lim = max(1, min(raw_limit, 20))
        max_bytes = int(d.get("transcript_max_bytes", 51200))
        exclude_master = bool(d.get("transcript_exclude_master_when_per_call", True))
        tdir = customer_dir(customer_name) / "Transcripts"
        if not tdir.is_dir():
            return json.dumps({"error": "Transcripts folder not found", "path": str(tdir)})
        all_txt = [p for p in tdir.glob("*.txt") if p.is_file()]
        per_call = [p for p in all_txt if not p.name.startswith("_MASTER_")]
        candidates = per_call if (exclude_master and per_call) else all_txt
        files = sorted(candidates, key=lambda x: x.stat().st_mtime, reverse=True)[:lim]
        out: list[dict[str, Any]] = []
        for p in files:
            raw = p.read_text(encoding="utf-8", errors="replace")
            raw_b = raw.encode("utf-8")
            truncated = len(raw_b) > max_bytes
            text = raw_b[:max_bytes].decode("utf-8", errors="replace") if truncated else raw
            out.append(
                {
                    "file": p.name,
                    "bytes_total": len(raw_b),
                    "truncated": truncated,
                    "text": text,
                }
            )
        return json.dumps({"transcripts": out}, ensure_ascii=False)


@mcp.tool
def read_audit_log(customer_name: str) -> str:
    """Read pnotes_agent_log.md for a customer (AI audit / rejection watermarks)."""
    with tool_scope("read_audit_log", customer_name=customer_name):
        validate_customer_name(customer_name)
        p = customer_dir(customer_name) / "pnotes_agent_log.md"
        if not p.is_file():
            return json.dumps({"error": "file not found", "path": str(p)})
        text = p.read_text(encoding="utf-8", errors="replace")
        return json.dumps({"path": str(p), "content": text}, ensure_ascii=False)


@mcp.tool
def read_ledger(customer_name: str, max_rows: int = 10) -> str:
    """Read the History Ledger markdown for a customer (full file; prefer small files)."""
    _ = max_rows  # reserved for future row-limited reads
    with tool_scope("read_ledger", customer_name=customer_name, max_rows=max_rows):
        validate_customer_name(customer_name)
        ai = customer_dir(customer_name) / "AI_Insights"
        if not ai.is_dir():
            return json.dumps({"error": "AI_Insights not found", "path": str(ai)})
        ledgers = sorted(ai.glob("*-History-Ledger.md"))
        if not ledgers:
            return json.dumps({"error": "no ledger file", "path": str(ai)})
        p = ledgers[0]
        text = p.read_text(encoding="utf-8", errors="replace")
        max_chars = 200_000
        if len(text) > max_chars:
            text = text[:100000] + "\n\n...[truncated]...\n\n" + text[-50000:]
        return json.dumps({"path": str(p), "content": text}, ensure_ascii=False)


@mcp.tool
def check_product_intelligence() -> str:
    """Check Product-Intelligence.md freshness (internal reference)."""
    with tool_scope("check_product_intelligence"):
        from prestonotes_mcp.runtime import get_ctx

        ctx = get_ctx()
        paths = ctx.config.get("paths", {})
        rel = str(
            paths.get("product_intel", "MyNotes/Internal/AI_Insights/Product-Intelligence.md")
        )
        p = ctx.path(*rel.split("/"))
        d = _defaults()
        max_age = int(d.get("product_intel_max_age_days", 7))
        if not p.is_file():
            return json.dumps(
                {"fresh": False, "error": "file not found", "path": str(p), "max_age_days": max_age}
            )
        text = p.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"last_updated:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", text, re.I)
        if not m:
            return json.dumps({"fresh": False, "note": "no last_updated in file", "path": str(p)})
        dt = datetime.strptime(m.group(1), "%Y-%m-%d").date()
        age = (datetime.now().date() - dt).days
        return json.dumps(
            {"fresh": age <= max_age, "age_days": age, "last_updated": m.group(1), "path": str(p)}
        )


# ---------------------------------------------------------------------------
# Write / sync tools (user must approve in chat before mutating external state)
# ---------------------------------------------------------------------------


@mcp.tool
def sync_notes(customer_name: str | None = None) -> str:
    """Pull MyNotes from Google Drive to the local repo. Optional customer name scopes to one folder."""
    with tool_scope("sync_notes", customer_name=customer_name or ""):
        args: list[str] = []
        if customer_name:
            validate_customer_name(customer_name)
            args.append(customer_name)
        try:
            proc = run_shell_script("scripts/rsync-gdrive-notes.sh", *args)
        except FileNotFoundError as exc:
            return json.dumps(
                {
                    "error": str(exc),
                    "hint": "Script missing in this repo — port TASK-006 (scripts/rsync-gdrive-notes.sh).",
                }
            )
        out = (proc.stdout or "") + (proc.stderr or "")
        return json.dumps({"exit_code": proc.returncode, "output": out[-12000:]})


@mcp.tool
def sync_transcripts() -> str:
    """Run Granola → Drive transcript sync (granola-sync.py)."""
    with tool_scope("sync_transcripts"):
        script_path = repo_root() / "scripts" / "granola-sync.py"
        if not script_path.is_file():
            return json.dumps(
                {
                    "error": f"Script not found: {script_path}",
                    "hint": "Expected scripts/granola-sync.py in the repo (TASK-005).",
                }
            )
        proc = run_uv_script("scripts/granola-sync.py")
        out = (proc.stdout or "") + (proc.stderr or "")
        return json.dumps({"exit_code": proc.returncode, "output": out[-12000:]})


@mcp.tool
def write_doc(
    doc_id: str,
    mutations_json: str,
    dry_run: bool = False,
) -> str:
    """Apply an approved mutation JSON plan to a Google Doc. Modifies external state — get user approval in chat first. Use dry_run=true to preview."""
    with tool_scope("write_doc", doc_id=doc_id, dry_run=dry_run):
        check_mutation_json_size(mutations_json)
        doc_id = (doc_id or "").strip()
        if not doc_id:
            raise ValueError("doc_id required")
        from prestonotes_mcp.runtime import get_ctx

        ctx = get_ctx()
        paths = ctx.config.get("paths", {})
        cfg = str(paths.get("doc_schema", "prestonotes_gdoc/config/doc-schema.yaml"))
        root = repo_root()
        tmp = root / "tmp"
        tmp.mkdir(parents=True, exist_ok=True)
        mut_path = tmp / f"mcp-mutations-{uuid.uuid4().hex}.json"
        mut_path.write_text(mutations_json, encoding="utf-8")
        args = ["write", "--doc-id", doc_id, "--config", cfg, "--mutations", str(mut_path)]
        if dry_run:
            args.append("--dry-run")
        proc = run_uv_script("prestonotes_gdoc/update-gdoc-customer-notes.py", *args)
        out = (proc.stdout or "") + (proc.stderr or "")
        try:
            mut_path.unlink(missing_ok=True)
        except OSError:
            pass
        if proc.returncode != 0:
            return json.dumps(
                {
                    "error": "write failed",
                    "exit_code": proc.returncode,
                    "output": out[-12000:],
                    **google_auth_terminal_fix_fields(ctx.config),
                }
            )
        return json.dumps({"exit_code": proc.returncode, "output": out[-12000:]})


@mcp.tool
def append_ledger(customer_name: str, doc_id: str, applied_json_path: str) -> str:
    """Append a History Ledger row after a successful write (ledger-append)."""
    with tool_scope("append_ledger", customer_name=customer_name):
        validate_customer_name(customer_name)
        from prestonotes_mcp.runtime import get_ctx

        ctx = get_ctx()
        paths = ctx.config.get("paths", {})
        cfg = str(paths.get("doc_schema", "prestonotes_gdoc/config/doc-schema.yaml"))
        aj = _rel_path(applied_json_path)
        proc = run_uv_script(
            "prestonotes_gdoc/update-gdoc-customer-notes.py",
            "ledger-append",
            "--customer",
            customer_name,
            "--doc-id",
            doc_id,
            "--config",
            cfg,
            "--applied-json",
            str(aj.relative_to(repo_root())),
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        if proc.returncode != 0:
            return json.dumps(
                {
                    "exit_code": proc.returncode,
                    "output": out[-8000:],
                    **google_auth_terminal_fix_fields(ctx.config),
                }
            )
        return json.dumps({"exit_code": proc.returncode, "output": out[-8000:]})


@mcp.tool
def append_ledger_v2(customer_name: str, row_json: str) -> str:
    """Append one v2 History Ledger row (24 columns: legacy + call_type, challenges, value_realized, key_stakeholders). Mutates customer data — get user approval in chat first. Requires a migrated ledger; if still 19 columns, error directs to python -m prestonotes_mcp.tools.migrate_ledger."""
    with tool_scope("append_ledger_v2", customer_name=customer_name):
        validate_customer_name(customer_name)
        if len(row_json) > 400_000:
            raise ValueError("row_json too large")
        data = json.loads(row_json)
        if not isinstance(data, dict):
            raise ValueError("row_json must be a JSON object")
        validate_ledger_v2_row(data)
        path = append_ledger_v2_row(customer_name, data)
        return json.dumps({"ok": True, "path": str(path)})


@mcp.tool
def log_run(customer_name: str, markdown_block: str) -> str:
    """Append a run note to pnotes_agent_log.md (operational memory)."""
    with tool_scope("log_run", customer_name=customer_name):
        validate_customer_name(customer_name)
        if len(markdown_block) > 100_000:
            raise ValueError("markdown_block too large")
        p = customer_dir(customer_name) / "pnotes_agent_log.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        header = "# pnotes_agent_log\n\n"
        block = (
            f"\n## mcp {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%SZ')}\n\n"
            f"{markdown_block}\n\n---\n\n"
        )
        existing = p.read_text(encoding="utf-8") if p.is_file() else ""
        if not existing.strip():
            p.write_text(header + block, encoding="utf-8")
        elif existing.startswith("# pnotes_agent_log"):
            rest = existing[len("# pnotes_agent_log") :].lstrip("\n")
            p.write_text(header + block + rest, encoding="utf-8")
        else:
            p.write_text(header + block + existing, encoding="utf-8")
        return json.dumps({"ok": True, "path": str(p)})


@mcp.tool
def bootstrap_customer(customer_name: str, dry_run: bool = True) -> str:
    """Create customer folders and Notes Google Doc on Drive. Defaults to dry_run=true (safe). Set dry_run=false only after explicit user approval."""
    with tool_scope("bootstrap_customer", customer_name=customer_name, dry_run=dry_run):
        validate_customer_name(customer_name)
        from prestonotes_mcp.runtime import get_ctx

        ctx = get_ctx()
        args = [customer_name]
        if dry_run:
            args.append("--dry-run")
        proc = run_uv_script("prestonotes_gdoc/000-bootstrap-gdoc-customer-notes.py", *args)
        out = (proc.stdout or "") + (proc.stderr or "")
        if proc.returncode != 0:
            return json.dumps(
                {
                    "exit_code": proc.returncode,
                    "output": out[-12000:],
                    **google_auth_terminal_fix_fields(ctx.config),
                }
            )
        return json.dumps({"exit_code": proc.returncode, "output": out[-12000:]})


# ---------------------------------------------------------------------------
# Call record tools (§7.1–7.2 — local MyNotes JSON)
# ---------------------------------------------------------------------------


@mcp.tool
def write_call_record(customer_name: str, call_id: str, record_json: str) -> str:
    """Write a validated per-call record JSON to MyNotes/Customers/<name>/call-records/<call_id>.json. Requires user approval before mutating customer data."""
    with tool_scope("write_call_record", customer_name=customer_name, call_id=call_id):
        validate_customer_name(customer_name)
        check_call_record_json_size(record_json)
        cid = validate_call_id(call_id)
        data = json.loads(record_json)
        if not isinstance(data, dict):
            raise ValueError("record_json must be a JSON object")
        if str(data.get("call_id", "")).strip() != cid:
            raise ValueError("record_json.call_id must match call_id argument")
        validate_call_record_object(data)
        path = call_records_path(customer_name, cid)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return json.dumps({"ok": True, "path": str(path)})


@mcp.tool
def read_call_records(
    customer_name: str,
    since_date: str | None = None,
    call_type: str | None = None,
) -> str:
    """List call records for a customer, optionally filtered by since_date (YYYY-MM-DD) and/or call_type."""
    with tool_scope(
        "read_call_records",
        customer_name=customer_name,
        since_date=since_date or "",
        call_type=call_type or "",
    ):
        validate_customer_name(customer_name)
        sd = since_date.strip() if since_date else None
        if sd and not re.match(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", sd):
            raise ValueError("since_date must be YYYY-MM-DD")
        ct = validate_call_type_filter(call_type)
        records = read_call_record_files(customer_name, sd, ct)
        return json.dumps({"records": records, "count": len(records)}, ensure_ascii=False)


@mcp.tool
def update_transcript_index(customer_name: str) -> str:
    """Rebuild transcript-index.json by scanning call-records/*.json (project_spec §7.2)."""
    with tool_scope("update_transcript_index", customer_name=customer_name):
        validate_customer_name(customer_name)
        idx = rebuild_transcript_index(customer_name)
        p = transcript_index_path(customer_name)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(idx, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return json.dumps(idx, ensure_ascii=False)


@mcp.tool
def read_transcript_index(customer_name: str) -> str:
    """Read MyNotes/Customers/<name>/transcript-index.json."""
    with tool_scope("read_transcript_index", customer_name=customer_name):
        validate_customer_name(customer_name)
        p = transcript_index_path(customer_name)
        if not p.is_file():
            return json.dumps({"error": "file not found", "path": str(p)})
        return p.read_text(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Journey + challenge lifecycle (§4 AI_Insights, §7.4)
# ---------------------------------------------------------------------------


@mcp.tool
def write_journey_timeline(customer_name: str, content: str) -> str:
    """Write markdown to AI_Insights/<Customer>-Journey-Timeline.md (UTF-8). Mutates customer data — get user approval in chat before calling."""
    with tool_scope("write_journey_timeline", customer_name=customer_name):
        validate_customer_name(customer_name)
        check_journey_timeline_size(content)
        path = write_journey_timeline_markdown(customer_name, content)
        return json.dumps({"ok": True, "path": str(path)})


@mcp.tool
def update_challenge_state(
    customer_name: str, challenge_id: str, new_state: str, evidence: str
) -> str:
    """Append a challenge lifecycle transition to AI_Insights/challenge-lifecycle.json (states §7.4). Mutates customer data — get user approval in chat before calling."""
    with tool_scope(
        "update_challenge_state",
        customer_name=customer_name,
        challenge_id=challenge_id,
        new_state=new_state,
    ):
        validate_customer_name(customer_name)
        result = append_challenge_transition(customer_name, challenge_id, new_state, evidence)
        return json.dumps({"ok": True, **result})


# ---------------------------------------------------------------------------
# Resources (read-only reference material)
# ---------------------------------------------------------------------------


@mcp.resource("prestonotes://config/doc-schema")
def resource_doc_schema() -> str:
    """Google Doc schema YAML."""
    p = repo_root() / "prestonotes_gdoc" / "config" / "doc-schema.yaml"
    return p.read_text(encoding="utf-8", errors="replace") if p.is_file() else ""


@mcp.resource("prestonotes://config/section-sequence")
def resource_section_sequence() -> str:
    """Section builder sequence YAML."""
    p = repo_root() / "prestonotes_gdoc" / "config" / "section-sequence.yaml"
    return p.read_text(encoding="utf-8", errors="replace") if p.is_file() else ""


@mcp.resource("prestonotes://config/task-budgets")
def resource_task_budgets() -> str:
    """Task token budget YAML."""
    p = repo_root() / "prestonotes_gdoc" / "config" / "task-budgets.yaml"
    return p.read_text(encoding="utf-8", errors="replace") if p.is_file() else ""


@mcp.resource("prestonotes://prompts/persona")
def resource_persona() -> str:
    """SE persona prompt for customer notes."""
    p = (
        repo_root()
        / "prestonotes_gdoc"
        / "config"
        / "prompts"
        / "015-customer-notes-se-persona-prompt.md"
    )
    return p.read_text(encoding="utf-8", errors="replace") if p.is_file() else ""


@mcp.resource("prestonotes://prompts/lens")
def resource_lens() -> str:
    """Wiz solution lens prompt."""
    p = repo_root() / "prestonotes_gdoc" / "config" / "prompts" / "010-wiz-solution-lens.md"
    return p.read_text(encoding="utf-8", errors="replace") if p.is_file() else ""


def main() -> None:
    root = repo_root_from_env_or_file()
    os.environ.setdefault("PRESTONOTES_REPO_ROOT", str(root))
    cfg = load_config(root)
    gb = gdrive_base_from_config(cfg)
    if gb:
        os.environ.setdefault("GDRIVE_BASE_PATH", gb)
    init_ctx(root, cfg)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

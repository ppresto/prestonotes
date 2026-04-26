#!/usr/bin/env python3
"""E2E-only: replace the customer Notes Google Doc with a fresh copy of the template document.

This uses the Drive API ``files.copy`` to clone ``_TEMPLATE/_notes-template`` into the
customer folder, trashes the previous ``{Customer} Notes`` file, and renames the copy.
The new file is a full structural clone of the template (tabs, tables, styles).

**Document id:** The Google file id of the Notes document **changes** when the old file is
trashed and the copy is renamed. ``discover_doc`` / the next ``rsync`` from Drive updates
the local ``.gdoc`` stub. Stable-URL bookmarks to the *old* id will need updating; this
is the tradeoff for a reliable full-template reset without a multi-hundred-line Docs
batchUpdate replayer (see TASK-052).

Auth: gcloud user token (same as ``drive-trash-customer.py`` and ``000-bootstrap``).

Usage:
  uv run python prestonotes_gdoc/e2e_rebaseline_customer_gdoc.py _TEST_CUSTOMER
  uv run python prestonotes_gdoc/e2e_rebaseline_customer_gdoc.py _TEST_CUSTOMER --dry-run
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import uuid
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

# Reuse resolution logic from drive-trash-customer (duplicated to keep scripts standalone).
DRIVE_API_BASE = "https://www.googleapis.com/drive/v3"
FOLDER_MIME = "application/vnd.google-apps.folder"
DOC_MIME = "application/vnd.google-apps.document"
AUTH_LOGIN_CMD = [
    "gcloud",
    "auth",
    "login",
    "--account=patrick.presto@wiz.io",
    "--enable-gdrive-access",
    "--force",
]
DEFAULT_TEMPLATE_STUB = (
    "/Users/patrick.presto/Google Drive/My Drive/MyNotes/Customers/_TEMPLATE/_notes-template.gdoc"
)


def run_cmd(command: list[str]) -> str:
    proc = subprocess.run(command, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or f"Command failed: {command}")
    return proc.stdout.strip()


def get_access_token() -> str:
    try:
        return run_cmd(["gcloud", "auth", "print-access-token"])
    except RuntimeError as exc:
        auth_cmd = " ".join(AUTH_LOGIN_CMD)
        raise RuntimeError(
            "Unable to obtain a Google access token. "
            f"Run `{auth_cmd}` and retry.\nDetails: {exc}"
        ) from exc


def drive_request(
    token: str,
    method: str,
    path: str,
    query: dict[str, str] | None = None,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    url = f"{DRIVE_API_BASE}{path}"
    if query:
        url = f"{url}?{urllib.parse.urlencode(query)}"
    data = None
    headers = {"Authorization": f"Bearer {token}"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        raise RuntimeError(f"Drive API {method} {path} failed: HTTP {exc.code} {body}") from exc


def escape_q(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


def get_file_metadata(token: str, file_id: str, fields: str) -> dict[str, Any]:
    return drive_request(token, "GET", f"/files/{file_id}", query={"fields": fields})


def resolve_customers_folder_id(token: str, template_stub: Path) -> str:
    if not template_stub.exists():
        raise RuntimeError(f"Template .gdoc stub not found: {template_stub}")
    try:
        payload = json.loads(template_stub.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Failed to parse template .gdoc stub: {template_stub}") from exc
    template_doc_id = payload.get("doc_id")
    if not template_doc_id:
        raise RuntimeError(f"Template .gdoc stub does not contain doc_id: {template_stub}")
    template_meta = get_file_metadata(token, str(template_doc_id), "id,name,parents")
    parent_ids = template_meta.get("parents", [])
    if not parent_ids:
        raise RuntimeError("Template doc has no parent; cannot resolve Customers folder.")
    template_parent_id = parent_ids[0]
    template_parent_meta = get_file_metadata(token, template_parent_id, "id,name,parents")
    if template_parent_meta.get("name") == "_TEMPLATE":
        customers_parents = template_parent_meta.get("parents", [])
        if not customers_parents:
            raise RuntimeError("_TEMPLATE has no parent; cannot resolve Customers folder.")
        return customers_parents[0]
    return template_parent_id


def find_folders_under(
    token: str, parent_id: str, name: str, *, trashed: bool = False
) -> list[dict[str, Any]]:
    tr = "trashed=true" if trashed else "trashed=false"
    q = f"name='{escape_q(name)}' and mimeType='{FOLDER_MIME}' and {tr} and '{parent_id}' in parents"
    resp = drive_request(
        token,
        "GET",
        "/files",
        query={"q": q, "fields": "files(id,name,trashed,createdTime)", "pageSize": "50"},
    )
    return resp.get("files", [])


def find_doc_in_customer(token: str, customer_folder_id: str, doc_title: str) -> dict[str, Any] | None:
    q = (
        f"name='{escape_q(doc_title)}' and mimeType='{DOC_MIME}' and trashed=false "
        f"and '{customer_folder_id}' in parents"
    )
    resp = drive_request(
        token,
        "GET",
        "/files",
        query={"q": q, "fields": "files(id,name,mimeType,webViewLink)", "pageSize": "5"},
    )
    files = resp.get("files", [])
    return files[0] if files else None


def copy_file(
    token: str, source_id: str, new_name: str, parents: list[str]
) -> dict[str, Any]:
    return drive_request(
        token,
        "POST",
        f"/files/{source_id}/copy",
        query={"fields": "id,name,parents,webViewLink"},
        payload={"name": new_name, "parents": parents},
    )


def trash_file(token: str, file_id: str) -> dict[str, Any]:
    return drive_request(
        token,
        "PATCH",
        f"/files/{file_id}",
        query={"fields": "id,name,trashed"},
        payload={"trashed": True},
    )


def rename_file(token: str, file_id: str, new_name: str) -> dict[str, Any]:
    return drive_request(
        token,
        "PATCH",
        f"/files/{file_id}",
        query={"fields": "id,name"},
        payload={"name": new_name},
    )


def wait_trashed(token: str, file_id: str, timeout: float = 30.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        m = get_file_metadata(token, file_id, "id,trashed")
        if m.get("trashed"):
            return
        time.sleep(1.0)
    raise RuntimeError(f"Timed out waiting for file {file_id} to show trashed=true")


def run_rebaseline(
    *,
    customer: str,
    template_stub: Path,
    dry_run: bool,
    emit_json: bool,
) -> dict[str, Any]:
    if not customer.strip() or "/" in customer or "\\" in customer:
        raise ValueError("invalid customer name")
    doc_title = f"{customer} Notes"
    temp_title = f"{doc_title} __e2e_rebase_{uuid.uuid4().hex[:8]}__"

    token = get_access_token()
    customers_folder_id = resolve_customers_folder_id(token, template_stub)
    cfolders = find_folders_under(token, customers_folder_id, customer, trashed=False)
    if not cfolders:
        raise RuntimeError(
            f"No folder named {customer!r} under Customers in Drive. "
            "Run bootstrap (or nuclear reset + bootstrap) first."
        )
    customer_folder_id = cfolders[0]["id"]
    tstub = json.loads(Path(template_stub).read_text(encoding="utf-8"))
    template_doc_id = str(tstub.get("doc_id", "")).strip()
    if not template_doc_id:
        raise RuntimeError(f"Missing doc_id in template stub: {template_stub}")

    old = find_doc_in_customer(token, customer_folder_id, doc_title)
    out: dict[str, Any] = {
        "customer": customer,
        "doc_title": doc_title,
        "template_doc_id": template_doc_id,
        "temp_title": temp_title,
        "previous_notes_doc_id": (old or {}).get("id"),
    }

    if dry_run:
        out["dry_run"] = True
        out["would_trash_id"] = out["previous_notes_doc_id"]
        if not emit_json:
            print(
                f"[DRY-RUN] Would copy template {template_doc_id} to {temp_title!r}, "
                f"trash old {doc_title!r} ({out['previous_notes_doc_id']}), "
                f"then rename copy to {doc_title!r}."
            )
        return out

    if not old:
        # Greenfield: copy template with final name only.
        created = copy_file(token, template_doc_id, doc_title, [customer_folder_id])
        out["notes_doc_id"] = created.get("id")
        out["webViewLink"] = created.get("webViewLink", "")
        out["mode"] = "copy_only"
        return out

    new = copy_file(token, template_doc_id, temp_title, [customer_folder_id])
    new_id = new.get("id")
    if not new_id:
        raise RuntimeError("files.copy did not return id")

    trash_file(token, str(old["id"]))
    try:
        wait_trashed(token, str(old["id"]), timeout=45.0)
    except RuntimeError:
        # Best-effort; continue to rename
        pass

    renamed = rename_file(token, str(new_id), doc_title)
    out["notes_doc_id"] = renamed.get("id", new_id)
    out["previous_notes_doc_id"] = old.get("id")
    out["webViewLink"] = new.get("webViewLink", "")
    out["mode"] = "copy_trash_rename"
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("customer", help="Customer folder name, e.g. _TEST_CUSTOMER")
    p.add_argument(
        "--notes-template-stub",
        type=Path,
        default=Path(DEFAULT_TEMPLATE_STUB),
        help="Path to _notes-template.gdoc (JSON with doc_id).",
    )
    p.add_argument("--dry-run", action="store_true", help="Resolve and print, do not copy.")
    p.add_argument(
        "--json", action="store_true", help="Print machine-readable JSON to stdout (also on error)."
    )
    args = p.parse_args()
    try:
        res = run_rebaseline(
            customer=args.customer.strip(),
            template_stub=args.notes_template_stub.expanduser().resolve(),
            dry_run=bool(args.dry_run),
            emit_json=bool(args.json),
        )
        if args.json:
            print(json.dumps(res, indent=2))
        elif not args.dry_run and not args.json:
            print(
                f"[OK] E2E GDoc rebaseline: {res.get('doc_title')} "
                f"now {res.get('notes_doc_id')} (previous {res.get('previous_notes_doc_id')})"
            )
        return 0
    except (RuntimeError, ValueError) as exc:
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stdout)
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

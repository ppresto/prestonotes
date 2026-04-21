#!/usr/bin/env python3
"""Trash a Google Drive customer folder via the Drive REST API.

Used by the `_TEST_CUSTOMER` E2E reset flow (TASK-044). Idempotent: no-op when
the folder is already absent or already trashed. Auth mirrors
`000-bootstrap-gdoc-customer-notes.py` (gcloud user credentials).

Why this exists instead of `rm` on the mounted Drive:
- `rm` on a Google Drive for Desktop mount has racy semantics and Drive sometimes
  recreates the folder from the server side before the local delete has propagated.
- The API `PATCH /files/{id} {"trashed": true}` moves the folder to Drive trash
  synchronously with a clean success/fail contract.

Usage:
  uv run python prestonotes_gdoc/drive-trash-customer.py _TEST_CUSTOMER
  uv run python prestonotes_gdoc/drive-trash-customer.py _TEST_CUSTOMER --dry-run
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


DRIVE_API_BASE = "https://www.googleapis.com/drive/v3"
FOLDER_MIME = "application/vnd.google-apps.folder"
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
TRASH_POLL_TIMEOUT_SEC = 60.0
TRASH_POLL_INTERVAL_SEC = 2.0


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
    """Resolve the parent Customers folder the same way bootstrap-gdoc does.

    Reads the template `.gdoc` stub JSON, hops to the doc's parent (_TEMPLATE),
    then to its parent (Customers). This avoids ambiguity when multiple MyNotes
    folders exist across drives.
    """
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


def find_folders_under(token: str, parent_id: str, name: str, include_trashed: bool = False) -> list[dict[str, Any]]:
    trashed_clause = "" if include_trashed else " and trashed=false"
    query = (
        f"name='{escape_q(name)}' and mimeType='{FOLDER_MIME}'"
        f"{trashed_clause} and '{parent_id}' in parents"
    )
    resp = drive_request(
        token,
        "GET",
        "/files",
        query={"q": query, "fields": "files(id,name,trashed,createdTime)", "pageSize": "50"},
    )
    files = resp.get("files", [])
    files.sort(key=lambda f: f.get("createdTime", ""))
    return files


def trash_folder(token: str, folder_id: str) -> dict[str, Any]:
    return drive_request(
        token,
        "PATCH",
        f"/files/{folder_id}",
        query={"fields": "id,name,trashed"},
        payload={"trashed": True},
    )


def wait_until_trashed(token: str, folder_id: str) -> None:
    deadline = time.monotonic() + TRASH_POLL_TIMEOUT_SEC
    while time.monotonic() < deadline:
        meta = get_file_metadata(token, folder_id, "id,trashed")
        if meta.get("trashed"):
            return
        time.sleep(TRASH_POLL_INTERVAL_SEC)
    raise RuntimeError(f"Timed out waiting for folder {folder_id} to be reported as trashed.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Trash a Google Drive customer folder by name.")
    parser.add_argument("customer_name", help="Customer folder name under Customers/ (e.g. _TEST_CUSTOMER)")
    parser.add_argument(
        "--notes-template-stub",
        default=DEFAULT_TEMPLATE_STUB,
        help="Path to _TEMPLATE .gdoc stub used to resolve the Customers folder id (same as bootstrap).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Resolve the folder id but do not call PATCH; print what would be trashed.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a machine-readable JSON summary to stdout.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    customer = args.customer_name.strip()
    if not customer or "/" in customer or "\\" in customer:
        print(f"Invalid customer name: {args.customer_name!r}", file=sys.stderr)
        return 2

    token = get_access_token()
    customers_folder_id = resolve_customers_folder_id(token, Path(args.notes_template_stub).expanduser())
    matches = find_folders_under(token, customers_folder_id, customer, include_trashed=False)

    if not matches:
        summary = {
            "action": "noop",
            "reason": "not_found",
            "customer": customer,
            "customers_folder_id": customers_folder_id,
        }
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print(f"[OK] {customer} is already absent under Customers folder (nothing to trash).")
        return 0

    results: list[dict[str, Any]] = []
    for folder in matches:
        fid = str(folder["id"])
        if args.dry_run:
            results.append({"folder_id": fid, "name": folder.get("name"), "action": "would_trash"})
            continue
        trash_folder(token, fid)
        wait_until_trashed(token, fid)
        results.append({"folder_id": fid, "name": folder.get("name"), "action": "trashed"})

    summary = {
        "action": "trashed" if not args.dry_run else "dry_run",
        "customer": customer,
        "customers_folder_id": customers_folder_id,
        "results": results,
    }
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        for r in results:
            print(f"- {r['action']}: {r['name']} ({r['folder_id']})")
        if args.dry_run:
            print("[DRY-RUN] No Drive changes were made.")
        else:
            print(f"[OK] Trashed {len(results)} folder(s) named {customer!r} under Customers folder.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        cmd = " ".join(AUTH_LOGIN_CMD)
        print(
            "\nAuth quick-fix:\n"
            f"  {cmd}\n"
            "Then rerun this script.",
            file=sys.stderr,
        )
        raise SystemExit(1)

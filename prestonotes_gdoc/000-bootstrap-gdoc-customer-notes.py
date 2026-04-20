#!/usr/bin/env python3
"""
Bootstrap a customer folder in Google Drive and create a real copy of a notes template Google Doc.

This script intentionally uses the Google Drive REST API directly so it can run without
extra Python dependencies. Authentication is delegated to gcloud user credentials.
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
from dataclasses import dataclass
from pathlib import Path
from typing import Any


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

# Create/copy returns an id immediately, but GET and parent queries can lag (eventual consistency).
API_READY_TIMEOUT_SEC = 180.0
API_READY_POLL_INTERVAL_SEC = 2.0


@dataclass
class Config:
    customer_name: str
    notes_template_stub: Path
    create_ai_insights: bool
    create_transcripts: bool
    local_drive_customers_path: Path | None
    mount_wait_seconds: float
    mount_poll_interval: float
    auth_check_only: bool
    dry_run: bool


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
            f"Run `{auth_cmd}` and retry.\n"
            f"Details: {exc}"
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


def wait_for_file_id_ready(
    token: str,
    file_id: str,
    timeout_sec: float = API_READY_TIMEOUT_SEC,
    interval_sec: float = API_READY_POLL_INTERVAL_SEC,
    *,
    expect_mime: str | None = None,
) -> dict[str, Any]:
    """Poll GET /files/{id} until the resource is readable and not trashed."""
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        try:
            meta = get_file_metadata(token, file_id, "id,name,mimeType,trashed")
        except RuntimeError:
            time.sleep(interval_sec)
            continue
        if meta.get("trashed"):
            raise RuntimeError(f"Drive file {file_id} is trashed while waiting for availability.")
        if expect_mime and meta.get("mimeType") != expect_mime:
            time.sleep(interval_sec)
            continue
        return meta
    raise RuntimeError(
        f"Timed out after {timeout_sec:.0f}s waiting for Drive file {file_id} to become readable."
    )


def wait_until_doc_listed_under_parent(
    token: str,
    parent_folder_id: str,
    doc_name: str,
    expected_doc_id: str,
    timeout_sec: float = API_READY_TIMEOUT_SEC,
    interval_sec: float = API_READY_POLL_INTERVAL_SEC,
) -> dict[str, Any]:
    """Poll until children query sees the doc under the parent (stricter than GET-by-id alone)."""
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        hit = find_doc_by_name(token, parent_folder_id, doc_name)
        if hit and str(hit.get("id")) == expected_doc_id:
            return hit
        time.sleep(interval_sec)
    raise RuntimeError(
        f"Timed out after {timeout_sec:.0f}s waiting for '{doc_name}' ({expected_doc_id}) "
        f"to appear under folder {parent_folder_id} in Drive listings."
    )


def wait_until_folder_listed_under_parent(
    token: str,
    parent_folder_id: str,
    folder_name: str,
    expected_folder_id: str,
    timeout_sec: float = API_READY_TIMEOUT_SEC,
    interval_sec: float = API_READY_POLL_INTERVAL_SEC,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        hits = find_folders(token, parent_folder_id, folder_name)
        if hits and str(hits[0].get("id")) == expected_folder_id:
            return hits[0]
        time.sleep(interval_sec)
    raise RuntimeError(
        f"Timed out after {timeout_sec:.0f}s waiting for folder '{folder_name}' ({expected_folder_id}) "
        f"to appear under {parent_folder_id} in Drive listings."
    )


def wait_for_directory(path: Path, timeout_sec: float, interval_sec: float) -> bool:
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        if path.is_dir():
            return True
        time.sleep(interval_sec)
    return False


def find_folders(token: str, parent_id: str, name: str) -> list[dict[str, Any]]:
    query = (
        f"name='{escape_q(name)}' and mimeType='{FOLDER_MIME}' and trashed=false "
        f"and '{parent_id}' in parents"
    )
    resp = drive_request(
        token,
        "GET",
        "/files",
        query={"q": query, "fields": "files(id,name,mimeType,createdTime)", "pageSize": "50"},
    )
    files = resp.get("files", [])
    files.sort(key=lambda f: f.get("createdTime", ""))
    return files


def create_folder(token: str, parent_id: str, name: str) -> dict[str, Any]:
    return drive_request(
        token,
        "POST",
        "/files",
        query={"fields": "id,name,mimeType"},
        payload={"name": name, "mimeType": FOLDER_MIME, "parents": [parent_id]},
    )


def ensure_folder(token: str, parent_id: str, name: str, dry_run: bool) -> dict[str, Any]:
    # Drive listing can be eventually consistent. Retry before creating to avoid duplicate folders.
    for _ in range(5):
        existing = find_folders(token, parent_id, name)
        if existing:
            return existing[0]
        time.sleep(1.0)

    if dry_run:
        return {"id": f"dryrun-{name}", "name": name, "mimeType": FOLDER_MIME}

    created = create_folder(token, parent_id, name)
    fid = str(created["id"])
    wait_for_file_id_ready(token, fid, expect_mime=FOLDER_MIME)
    wait_until_folder_listed_under_parent(token, parent_id, name, fid)
    matches = find_folders(token, parent_id, name)
    if matches:
        return matches[0]
    return created


def find_doc_by_name(token: str, parent_id: str, name: str) -> dict[str, Any] | None:
    query = (
        f"name='{escape_q(name)}' and mimeType='{DOC_MIME}' and trashed=false "
        f"and '{parent_id}' in parents"
    )
    resp = drive_request(
        token,
        "GET",
        "/files",
        query={"q": query, "fields": "files(id,name,mimeType,webViewLink)", "pageSize": "10"},
    )
    files = resp.get("files", [])
    return files[0] if files else None


def copy_doc(token: str, source_doc_id: str, parent_id: str, new_name: str) -> dict[str, Any]:
    return drive_request(
        token,
        "POST",
        f"/files/{source_doc_id}/copy",
        query={"fields": "id,name,mimeType,webViewLink"},
        payload={"name": new_name, "parents": [parent_id]},
    )


def parse_template_stub(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Template .gdoc stub not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Failed to parse template .gdoc stub: {path}") from exc

    doc_id = payload.get("doc_id")
    if not doc_id:
        raise RuntimeError(f"Template .gdoc stub does not contain doc_id: {path}")
    return payload


def get_file_metadata(token: str, file_id: str, fields: str) -> dict[str, Any]:
    return drive_request(token, "GET", f"/files/{file_id}", query={"fields": fields})


def ensure_notes_doc(
    token: str,
    customer_folder_id: str,
    template_doc_id: str,
    customer_name: str,
    dry_run: bool,
) -> tuple[dict[str, Any], bool]:
    doc_name = f"{customer_name} Notes"
    existing = find_doc_by_name(token, customer_folder_id, doc_name)
    if existing:
        return existing, False
    if dry_run:
        return {"id": "dryrun-doc", "name": doc_name, "mimeType": DOC_MIME, "webViewLink": ""}, True
    created = copy_doc(token, template_doc_id, customer_folder_id, doc_name)
    doc_id = str(created["id"])
    wait_for_file_id_ready(token, doc_id, expect_mime=DOC_MIME)
    listed = wait_until_doc_listed_under_parent(token, customer_folder_id, doc_name, doc_id)
    return listed, True


def ensure_local_drive_scaffold(
    base_customers_path: Path,
    customer_name: str,
    notes_doc_id: str,
    template_stub: dict[str, Any],
    dry_run: bool,
) -> list[str]:
    created: list[str] = []
    customer_dir = base_customers_path / customer_name
    notes_stub_path = customer_dir / f"{customer_name} Notes.gdoc"

    if dry_run:
        return created

    # Never mkdir() the customer root on the Google Drive mount: if the API folder is not visible
    # yet, creating the path locally creates a *second* Drive folder and Drive renames one to
    # "Name 2". Wait for sync or use customer-scoped rsync instead.
    if not customer_dir.exists():
        return ["skipped (customer folder not visible in mounted Drive)"]

    # Do not mkdir AI_Insights / Transcripts here: those come from the API + Drive sync. Creating
    # them on the mount before the API children are visible can duplicate folders in Drive.

    stub_payload = {
        "": template_stub.get("", "WARNING! DO NOT EDIT THIS FILE! ANY CHANGES MADE WILL BE LOST!"),
        "doc_id": notes_doc_id,
        "resource_key": template_stub.get("resource_key", ""),
        "email": template_stub.get("email", ""),
    }
    notes_stub_path.write_text(json.dumps(stub_payload), encoding="utf-8")
    created.append(str(notes_stub_path))
    return created


def validate_customer_name(name: str) -> str:
    stripped = name.strip()
    if not stripped:
        raise argparse.ArgumentTypeError("customer name cannot be empty")
    invalid = {"/", "\\"}
    if any(ch in stripped for ch in invalid):
        raise argparse.ArgumentTypeError("customer name cannot contain path separators")
    return stripped


def parse_args() -> Config:
    parser = argparse.ArgumentParser(
        description="Bootstrap a Google Drive customer folder and copy notes template as a real Google Doc."
    )
    parser.add_argument("customer_name", type=validate_customer_name)
    parser.add_argument(
        "--notes-template-stub",
        default="/Users/patrick.presto/Google Drive/My Drive/MyNotes/Customers/_TEMPLATE/_notes-template.gdoc",
        help="Path to .gdoc template stub containing a doc_id.",
    )
    parser.add_argument(
        "--skip-ai-insights",
        action="store_true",
        help="Do not create AI_Insights folder.",
    )
    parser.add_argument(
        "--skip-transcripts",
        action="store_true",
        help="Do not create Transcripts folder.",
    )
    parser.add_argument(
        "--local-drive-customers-path",
        default="/Users/patrick.presto/Google Drive/My Drive/MyNotes/Customers",
        help="Mounted Google Drive Customers path used only for optional .gdoc pointer materialization.",
    )
    parser.add_argument(
        "--materialize-local-drive-pointer",
        action="store_true",
        help="Write [CustomerName] Notes.gdoc into mounted Drive when folder is already visible.",
    )
    parser.add_argument(
        "--mount-wait-seconds",
        type=float,
        default=120.0,
        help="With --materialize-local-drive-pointer: max seconds to wait for the customer folder "
        "to appear on the mounted Drive path (default 120). Set 0 to skip waiting.",
    )
    parser.add_argument(
        "--mount-poll-interval",
        type=float,
        default=3.0,
        help="Seconds between mount path checks when waiting.",
    )
    parser.add_argument(
        "--auth-check-only",
        action="store_true",
        help="Only validate auth and template access; do not create folders/docs.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Resolve actions without writing to Drive.")
    args = parser.parse_args()

    return Config(
        customer_name=args.customer_name,
        notes_template_stub=Path(args.notes_template_stub).expanduser(),
        create_ai_insights=not args.skip_ai_insights,
        create_transcripts=not args.skip_transcripts,
        local_drive_customers_path=Path(args.local_drive_customers_path).expanduser()
        if args.materialize_local_drive_pointer
        else None,
        mount_wait_seconds=args.mount_wait_seconds if args.materialize_local_drive_pointer else 0.0,
        mount_poll_interval=max(0.5, args.mount_poll_interval),
        auth_check_only=args.auth_check_only,
        dry_run=args.dry_run,
    )


def main() -> int:
    cfg = parse_args()
    template_stub = parse_template_stub(cfg.notes_template_stub)
    template_doc_id = str(template_stub["doc_id"])

    token = get_access_token()
    get_file_metadata(token, template_doc_id, "id,name,parents")

    if cfg.auth_check_only:
        print("[OK] Google auth + Drive scope + template access verified.")
        return 0

    # Resolve target Customers folder from the template location.
    # If template lives under Customers/_TEMPLATE, target the parent Customers folder.
    # This avoids ambiguity when multiple "MyNotes" folders exist across My Drive/shared drives.
    template_meta = get_file_metadata(token, template_doc_id, "id,name,parents")
    parent_ids = template_meta.get("parents", [])
    if not parent_ids:
        raise RuntimeError(
            "Template doc has no parent folder; cannot resolve target Customers directory."
        )
    template_parent_id = parent_ids[0]
    template_parent_meta = get_file_metadata(token, template_parent_id, "id,name,parents")
    if template_parent_meta.get("name") == "_TEMPLATE":
        customers_parent_ids = template_parent_meta.get("parents", [])
        if not customers_parent_ids:
            raise RuntimeError(
                "Template is under _TEMPLATE, but _TEMPLATE has no parent folder."
            )
        customers_folder_id = customers_parent_ids[0]
    else:
        customers_folder_id = template_parent_id
    customer = ensure_folder(token, customers_folder_id, cfg.customer_name, cfg.dry_run)

    created_subfolders: list[str] = []
    if cfg.create_ai_insights:
        ai = find_folders(token, customer["id"], "AI_Insights")
        if not ai:
            ensure_folder(token, customer["id"], "AI_Insights", cfg.dry_run)
            created_subfolders.append("AI_Insights")
    if cfg.create_transcripts:
        tx = find_folders(token, customer["id"], "Transcripts")
        if not tx:
            ensure_folder(token, customer["id"], "Transcripts", cfg.dry_run)
            created_subfolders.append("Transcripts")

    notes_doc, created_doc = ensure_notes_doc(
        token=token,
        customer_folder_id=customer["id"],
        template_doc_id=template_doc_id,
        customer_name=cfg.customer_name,
        dry_run=cfg.dry_run,
    )
    local_created: list[str] = []
    if cfg.local_drive_customers_path is not None:
        customer_mount = cfg.local_drive_customers_path / cfg.customer_name
        if not customer_mount.is_dir():
            if cfg.mount_wait_seconds > 0:
                print(
                    f"- Waiting up to {cfg.mount_wait_seconds:.0f}s for mounted path: {customer_mount}"
                )
                appeared = wait_for_directory(
                    customer_mount,
                    cfg.mount_wait_seconds,
                    cfg.mount_poll_interval,
                )
                if not appeared:
                    print(
                        "- Mounted customer folder still missing; skipped local .gdoc materialization.\n"
                        f'  Pull after Google Drive sync: ./scripts/rsync-gdrive-notes.sh "{cfg.customer_name}"'
                    )
            else:
                print(
                    "- Mounted customer folder missing; skipped materialization. "
                    "Increase --mount-wait-seconds or run customer-scoped rsync after Drive sync."
                )
        if customer_mount.is_dir():
            local_created = ensure_local_drive_scaffold(
                base_customers_path=cfg.local_drive_customers_path,
                customer_name=cfg.customer_name,
                notes_doc_id=str(notes_doc["id"]),
                template_stub=template_stub,
                dry_run=cfg.dry_run,
            )

    mode = "DRY-RUN" if cfg.dry_run else "APPLIED"
    print(f"[{mode}] Customer bootstrap complete: {cfg.customer_name}")
    print(f"- Customer folder id: {customer['id']}")
    print(f"- Template doc id: {template_doc_id}")
    print(f"- Notes doc: {notes_doc.get('name')} ({notes_doc.get('id')})")
    if notes_doc.get("webViewLink"):
        print(f"- Notes link: {notes_doc['webViewLink']}")
    print(f"- Notes action: {'created' if created_doc else 'reused existing'}")
    print(
        "- Subfolders created: "
        + (", ".join(created_subfolders) if created_subfolders else "none (already existed)")
    )
    if cfg.local_drive_customers_path is not None:
        print(
            "- Local mounted Drive materialization: "
            + (", ".join(local_created) if local_created else "none")
        )

    print("\nRun this to pull into local workspace (full tree or one customer):")
    print(f'  ./scripts/rsync-gdrive-notes.sh "{cfg.customer_name}"')
    print("  ./scripts/rsync-gdrive-notes.sh   # optional: full MyNotes mirror")
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

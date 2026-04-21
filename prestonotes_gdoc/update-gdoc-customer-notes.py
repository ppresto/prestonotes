#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0"]
# ///
"""
Read and update customer notes Google Docs via the Docs and Drive REST APIs.

Subcommands:
  discover  Find the Google Doc ID for a customer's notes document.
  read      Fetch and parse a Google Doc into a structured JSON section map.
  write     Apply a mutation plan JSON to a Google Doc via batchUpdate.

Authentication is delegated to gcloud user credentials (same pattern as
gdoc-bootstrap-customer-notes.py). Zero external dependencies beyond stdlib.
"""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DRIVE_API_BASE = "https://www.googleapis.com/drive/v3"
DOCS_API_BASE = "https://docs.googleapis.com/v1"
FOLDER_MIME = "application/vnd.google-apps.folder"
DOC_MIME = "application/vnd.google-apps.document"
TODAY = date.today().isoformat()
CONTACT_REL_TAG_RE = re.compile(r"\s*\[\[reports_to:(.*?)\]\]\s*$", re.IGNORECASE)
CONTACT_HIERARCHY_ENABLED = False
LOCAL_CUSTOMERS_BASE = Path("MyNotes/Customers")
_GDRIVE_BASE = os.environ.get("GDRIVE_BASE_PATH", "").strip()
GDRIVE_CUSTOMERS_BASE = (
    (Path(_GDRIVE_BASE) / "Customers") if _GDRIVE_BASE else LOCAL_CUSTOMERS_BASE
)
DAILY_ACTIVITY_SKIP_PATTERNS = re.compile(r"daily\s+activity", re.IGNORECASE)
DEFAULT_RUNLOG_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%SZ"
DEFAULT_RUNLOG_MAX_BYTES = int(0.05 * 1024 * 1024)  # 50KB, aligned with transcript rollover.
ALLOWED_DEAL_STAGE_VALUES = {
    "not-active", "pov", "tech win", "procurement", "win",
}
ALLOWED_DEAL_ACTIVITY_VALUES = {"active", "inactive"}
COMMERCIAL_SKUS = {"cloud", "sensor", "defend", "code"}
LIST_CONTROLLED_FIELDS: set[str] = set()
NUMERIC_CONTROLLED_FIELDS = {
    "critical_issues_open", "mttr_days", "monthly_reporting_hours",
}
ALLOWED_CHALLENGE_STATUSES = {"Open", "In Progress", "Resolved", "Closed", "Needs Validation"}
EXEC_SUMMARY_FIELDS = {"top_goal", "risk", "upsell_path"}
# Full list replacement (synthesis / Step 9 post-seed cleanup). Not for routine daily UCN.
REPLACE_FIELD_ENTRIES_TARGETS: dict[str, frozenset[str]] = {
    "exec_account_summary": frozenset(EXEC_SUMMARY_FIELDS),
    "contacts": frozenset({"free_text"}),
    "use_cases": frozenset({"free_text"}),
    "workflows": frozenset({"free_text"}),
    "cloud_environment": frozenset({"csp_regions", "idp_sso", "sizing"}),
}


def _replace_field_entries_allowed(sec_key: str, field_key: str) -> bool:
    allowed = REPLACE_FIELD_ENTRIES_TARGETS.get(sec_key)
    return allowed is not None and field_key in allowed
MAX_EXEC_SUMMARY_ENTRIES_BY_FIELD = {
    # Keep goals/risks uncapped by count; dedupe/evidence gates control quality.
    "upsell_path": 5,
}
STRICT_METADATA_FIELDS = {"exec_buyer", "champion", "technical_owner"}
UPSELL_SKU_TOKENS = ("wiz cloud", "wiz sensor", "wiz defend", "wiz code", "asm")
DEAL_RISK_TOKENS = (
    "budget", "executive", "exec", "alignment", "champion", "sponsor", "detractor",
    "timeline", "delay", "slip", "renewal", "expansion", "procurement", "commercial",
    "business case", "buy-in", "approval", "compete", "competitive", "displacement",
)
TECHNICAL_RISK_TOKENS = (
    "fedramp", "cve", "vulnerability", "scanner", "coverage", "sensor", "k8s", "kms",
    "exposure", "triage", "pipeline", "repo", "connector", "configuration", "reporting",
)
ACCOUNT_METADATA_HEADER = "Account Metadata"
USE_CASES_HEADER = "Use Cases / Requirements"
WORKFLOWS_HEADER = "Workflows / Processes"
ACCOUNT_SUMMARY_TAB_TITLE = "Account Summary"
ACCOUNT_METADATA_TAB_TITLE = "Account Metadata"
# Customer notes template: Daily Activity Logs is its own document tab (same title as the H1).
DAILY_ACTIVITY_LOGS_TAB_TITLE = "Daily Activity Logs"
TOP_GOAL_LABEL = "Goals"
ACCOMPLISHMENTS_HEADER = "Accomplishments"
CHALLENGE_TRACKER_FONT_PT = 10
ACCOUNT_METADATA_GUIDANCE_FONT_PT = 9
ENABLE_SYNTHESIZED_GOALS = False
# Cloud `tools_list` detail: legacy apply path truncated at 60 chars (removed). Sanitize still strips
# low-signal phrases; length cap below avoids runaway inserts (LLM controls verbosity).
MAX_TOOL_DETAIL_CHARS = 2000
# Daily Activity Logs: AI meeting recap prepended under H1 (body only; heading is separate).
MAX_DAILY_ACTIVITY_AI_BODY_CHARS = 200_000
# Post-apply contact line heuristics can drop valid rows; planner/LLM + contacts_section dedupe are primary.
AUTO_CLEANUP_CONTACTS_AFTER_APPLY = False
ALLOWED_ACTIONS_BY_STRATEGY = {
    "append_with_history": {"append_with_history", "flag_for_review"},
    "update_in_place": {"update_in_place", "set_if_empty"},
    "set_if_empty": {"set_if_empty"},
    "tools_list": {"add_tool", "update_tool_detail", "remove_tool_suggestion"},
    "free_text": {"append_with_history"},
}
TABLE_ALLOWED_ACTIONS = {"add_table_row", "update_table_row"}
MUTATING_ACTIONS = {
    "append_with_history",
    "set_if_empty",
    "update_in_place",
    "flag_for_review",
    "move_to_accomplishments",
    "replace_field_entries",
    "add_tool",
    "update_tool_detail",
    "remove_tool_suggestion",
    "add_table_row",
    "update_table_row",
    "prepend_daily_activity_ai_summary",
}
# Alternate H1/H2 titles seen in customer docs (canonical `header:` stays in doc-schema).
SECTION_HEADER_ALIASES: dict[str, list[str]] = {
    "use_cases": ["Use Cases"],
    "workflows": ["Workflows"],
}
KEY_FIELD_COVERAGE_REQUIREMENTS = {
    ("exec_account_summary", "top_goal"),
    ("exec_account_summary", "risk"),
    ("use_cases", "free_text"),
    ("workflows", "free_text"),
}
WORKFLOW_SIGNAL_TOKENS = {
    # Sequence/process markers
    "workflow", "process", "runbook", "playbook", "sequence", "step", "stage", "phase",
    "trigger", "intake", "triage", "investigate", "correlate", "enrich", "prioritize",
    "assign", "route", "handoff", "escalate", "approve", "review", "validate",
    "remediate", "closeout", "closure", "feedback loop",
    # Evidence/reporting artifacts
    "report", "reporting", "audit", "evidence", "artifact", "dashboard",
    "spreadsheet", "csv", "export", "lookup", "pivot", "sbom", "poam",
    "first-seen", "month-over-month", "30/60/90",
    # Ownership/resource/latency
    "owner", "owner-ready", "owner mapping", "resource", "capacity",
    "manual", "hours", "days", "weeks", "mttr", "sla", "aging", "backlog", "queue",
    "wait time", "cycle time", "time-to-remediation",
    # Systems commonly appearing in workflows
    "jira", "servicenow", "snow", "ticket", "ticketing", "alert",
    "anchore", "panther", "qualys", "crowdstrike", "carbonblack", "stacklet",
    "github", "gitlab", "jenkins", "harbor", "ci", "cd", "pipeline",
}
WORKFLOW_STRONG_PHRASES = {
    "csv export",
    "pivot table",
    "owner mapping",
    "owner-ready",
    "remediation packet",
    "prodsec handoff",
    "month-over-month",
    "first-seen cve",
    "ticketed follow-through",
    "threat signal intake",
}
REQUIREMENT_SIGNAL_TOKENS = {
    "must", "must-have", "required", "requirement", "requirements",
    "needs to", "need to", "should", "acceptance criteria", "success criteria",
    "non-negotiable", "goal state", "target state",
}

AUTH_LOGIN_CMD = [
    "gcloud", "auth", "login",
    "--account=patrick.presto@wiz.io",
    "--enable-gdrive-access", "--force",
]


# ---------------------------------------------------------------------------
# Auth (mirrors gdoc-bootstrap-customer-notes.py)
# ---------------------------------------------------------------------------

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
            f"Unable to obtain a Google access token. Run `{auth_cmd}` and retry.\n"
            f"Details: {exc}"
        ) from exc


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _api_request(
    token: str,
    method: str,
    url: str,
    query: dict[str, str] | None = None,
    payload: dict[str, Any] | None = None,
    retries: int = 3,
) -> dict[str, Any]:
    if query:
        url = f"{url}?{urllib.parse.urlencode(query)}"
    data = None
    headers = {"Authorization": f"Bearer {token}"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, method=method, headers=headers)

    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and attempt < retries - 1:
                wait = 2 ** attempt
                print(f"Rate limited. Retrying in {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            body = exc.read().decode("utf-8")
            raise RuntimeError(
                f"API {method} {url.split('?')[0]} failed: HTTP {exc.code} {body}"
            ) from exc
    raise RuntimeError("Max retries exceeded")


def drive_request(token: str, method: str, path: str, **kwargs) -> dict[str, Any]:
    return _api_request(token, method, f"{DRIVE_API_BASE}{path}", **kwargs)


def docs_request(token: str, method: str, path: str, **kwargs) -> dict[str, Any]:
    return _api_request(token, method, f"{DOCS_API_BASE}{path}", **kwargs)


def get_drive_file_metadata(token: str, file_id: str, fields: str) -> dict[str, Any]:
    return drive_request(token, "GET", f"/files/{file_id}", query={"fields": fields})


def find_doc_by_name_in_parent(token: str, parent_id: str, name: str) -> Optional[dict[str, Any]]:
    q = (
        f"name='{escape_q(name)}' and mimeType='{DOC_MIME}' and trashed=false "
        f"and '{parent_id}' in parents"
    )
    resp = drive_request(
        token,
        "GET",
        "/files",
        query={"q": q, "fields": "files(id,name,mimeType)", "pageSize": "10"},
    )
    files = resp.get("files", [])
    return files[0] if files else None


def create_doc_in_parent(token: str, parent_id: str, name: str) -> dict[str, Any]:
    return drive_request(
        token,
        "POST",
        "/files",
        query={"fields": "id,name,mimeType,webViewLink"},
        payload={"name": name, "mimeType": DOC_MIME, "parents": [parent_id]},
    )


def rename_drive_file(token: str, file_id: str, new_name: str) -> dict[str, Any]:
    return drive_request(
        token,
        "PATCH",
        f"/files/{file_id}",
        query={"fields": "id,name,mimeType"},
        payload={"name": new_name},
    )


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Entry:
    value: str
    timestamp: Optional[str] = None
    status: str = "active"
    review_reason: Optional[str] = None
    review_date: Optional[str] = None
    # Workflows / Processes: substring of value to bold in GDoc (must match value prefix before " — ").
    workflow_title: Optional[str] = None


@dataclass
class ToolEntry:
    display: str
    detail: Optional[str] = None
    flagged: bool = False
    flag_reason: Optional[str] = None
    flag_date: Optional[str] = None


@dataclass
class SectionField:
    key: str
    label: Optional[str]
    update_strategy: str
    entries: list[Entry] = field(default_factory=list)
    tools: dict[str, ToolEntry] = field(default_factory=dict)
    # Set by replace_field_entries: doc must delete all old paragraphs and re-insert (e.g. apply bullet glyphs).
    force_doc_rewrite: bool = False
    # Daily Activity Logs: (heading_line, body_markdown) pairs from prepend_daily_activity_ai_summary only.
    dal_prepends: list[tuple[str, str]] = field(default_factory=list)


@dataclass
class TableRow:
    challenge: str
    date: str
    category: str
    status: str
    notes_references: str


@dataclass
class DocumentSection:
    key: str
    header: str
    level: int
    section_type: str = "fields"
    fields: dict[str, SectionField] = field(default_factory=dict)
    rows: list[TableRow] = field(default_factory=list)
    header_start_index: Optional[int] = None
    header_end_index: Optional[int] = None
    content_end_index: Optional[int] = None
    tab_id: Optional[str] = None


SectionMap = dict[str, DocumentSection]


@dataclass
class Mutation:
    section_key: str
    action: str
    reasoning: str
    source: str = "transcript"
    field_key: Optional[str] = None
    new_value: Optional[str] = None
    target_value: Optional[str] = None
    tool_key: Optional[str] = None
    display_name: Optional[str] = None
    detail: Optional[str] = None
    row: Optional[dict[str, str]] = None


# ---------------------------------------------------------------------------
# Config loader
# ---------------------------------------------------------------------------

def load_config(path: str) -> dict:
    """Load customer notes schema YAML/JSON config."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    raw_text = p.read_text(encoding="utf-8")
    try:
        import yaml  # noqa: F811
        config = yaml.safe_load(raw_text)
    except ImportError:
        if p.suffix in (".yaml", ".yml"):
            config = _parse_yaml_minimal(raw_text)
        else:
            config = json.loads(raw_text)
    return config




def _parse_yaml_minimal(text: str) -> dict:
    """Fallback YAML parser when PyYAML is unavailable at initial import."""
    try:
        import yaml
        return yaml.safe_load(text)
    except ImportError:
        raise RuntimeError(
            "PyYAML is not installed. Run with: uv run custom-notes-agent/update-gdoc-customer-notes.py ..."
        )


def build_config_lookups(config: dict) -> tuple[dict, dict, dict]:
    """Returns (header_to_section_key, section_configs, field_strategies)."""
    sections = config.get("sections", [])
    header_to_key: dict[str, str] = {}
    section_configs: dict[str, dict] = {}
    field_strategies: dict[tuple, str] = {}

    for sec in sections:
        sec_key = sec["key"]
        header_to_key[sec["header"]] = sec_key
        for alias in SECTION_HEADER_ALIASES.get(sec_key, []):
            header_to_key[alias] = sec_key
        section_configs[sec_key] = sec
        for f in sec.get("fields", []):
            field_strategies[(sec_key, f["key"])] = f.get("update_strategy", "free_text")

    return header_to_key, section_configs, field_strategies


# ---------------------------------------------------------------------------
# Formatters (entry / tool serialization)
# ---------------------------------------------------------------------------

def format_entry_for_doc(entry: Entry) -> str:
    val = _strip_contact_rel_tag(entry.value or "")
    if entry.status == "flagged_for_review":
        reason = entry.review_reason or ""
        return f"[REVIEW: {reason}] {val}"
    elif entry.status == "superseded":
        # Superseded lines are omitted from the customer-facing Doc during write
        # (deleted, not rewritten with a visible tag). History lives in ledger/log.
        return ""
    else:
        return val


def _strip_nested_superseded(val: str) -> str:
    """Remove any residual [SUPERSEDED] tags embedded inside a value string."""
    while val.startswith("[SUPERSEDED]"):
        val = val[len("[SUPERSEDED]"):].strip()
    return val


def parse_entry_text(text: str) -> Entry:
    text = text.strip()
    text = text.lstrip("\t")
    # Accept existing bullet styles and normalize during parse.
    text = re.sub(r"^\s*[-*]\s+", "", text)
    text = re.sub(r"^\s{2,}[-*]\s+", "", text)
    if m := re.match(r"^\[REVIEW:\s*(.*?)\s*—\s*(\d{4}-\d{2}-\d{2})\]\s*(.*)$", text, re.DOTALL):
        return Entry(value=m.group(3).strip(), timestamp=m.group(2),
                     status="flagged_for_review", review_reason=m.group(1).strip(),
                     review_date=m.group(2))
    if m := re.match(r"^\[REVIEW:\s*(.*?)\]\s*(.*)$", text, re.DOTALL):
        return Entry(
            value=m.group(2).strip(),
            timestamp=None,
            status="flagged_for_review",
            review_reason=m.group(1).strip(),
            review_date=None,
        )
    if m := re.match(r"^\[SUPERSEDED:\s*(\d{4}-\d{2}-\d{2})\]\s*(.*)$", text):
        return Entry(value=_strip_nested_superseded(m.group(2).strip()), timestamp=m.group(1), status="superseded")
    if m := re.match(r"^\[SUPERSEDED\]\s*(.*)$", text):
        return Entry(value=_strip_nested_superseded(m.group(1).strip()), timestamp=None, status="superseded")
    # [YYYY-MM-DD] [SUPERSEDED] value — date-first superseded line (common stacking artifact)
    if m := re.match(r"^\[(\d{4}-\d{2}-\d{2})\]\s+\[SUPERSEDED\](.*)$", text):
        return Entry(value=_strip_nested_superseded(m.group(2).strip()), timestamp=m.group(1), status="superseded")
    # Backward compatible old format: [YYYY-MM-DD] value
    if m := re.match(r"^\[(\d{4}-\d{2}-\d{2})\]\s*(.*)$", text):
        return Entry(value=_strip_nested_superseded(m.group(2).strip()), timestamp=m.group(1), status="active")
    # New format: value [YYYY-MM-DD]
    if m := re.match(r"^(.*)\s\[(\d{4}-\d{2}-\d{2})\]\s*$", text):
        return Entry(value=_strip_nested_superseded(m.group(1).strip()), timestamp=m.group(2), status="active")
    return Entry(value=_strip_nested_superseded(text), timestamp=None, status="active")


def _strip_contact_rel_tag(value: str) -> str:
    return CONTACT_REL_TAG_RE.sub("", value).strip()


def _extract_contact_parent(value: str) -> Optional[str]:
    m = CONTACT_REL_TAG_RE.search(value or "")
    if not m:
        return None
    parent = m.group(1).strip()
    return parent if parent else None


def _extract_contact_name(value: str) -> str:
    clean = _strip_contact_rel_tag(value)
    if " - " in clean:
        return clean.split(" - ", 1)[0].strip()
    return clean.strip()


def format_tool_line(tool: ToolEntry) -> str:
    base = tool.display
    if tool.detail:
        base = f"{base} ({tool.detail})"
    if tool.flagged:
        reason = tool.flag_reason or ""
        fd = tool.flag_date or ""
        base = f"[REVIEW: {reason} — {fd}] {base}"
    return base


def parse_tool_line(text: str) -> tuple[str, str, Optional[str]]:
    text = text.strip()
    text = re.sub(r"^\s*[-*]\s+", "", text)
    review_prefix = re.match(r"^\[REVIEW:.*?\]\s*", text)
    if review_prefix:
        text = text[review_prefix.end():]
    m = re.match(r"^([^(]+?)(?:\s*\(([^)]+)\))?\s*$", text.strip())
    if m:
        display = m.group(1).strip()
        detail = m.group(2).strip() if m.group(2) else None
        normalized = re.sub(r"[^a-z0-9]", "_", display.lower()).strip("_")
        return normalized, display, detail
    normalized = re.sub(r"[^a-z0-9]", "_", text.strip().lower()).strip("_")
    return normalized, text.strip(), None


# ---------------------------------------------------------------------------
# Phase 1: Document discovery
# ---------------------------------------------------------------------------

def escape_q(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


def discover_customer_doc(token: str, root_folder_id: str, customer_name: str) -> str:
    """Traverse MyNotes/ -> Customers/ -> [customer_name]/ -> [customer_name] Notes."""

    def _find(parent_id: str, name: str, mime: str, desc: str) -> dict:
        q = (f"name='{escape_q(name)}' and mimeType='{mime}' "
             f"and '{parent_id}' in parents and trashed=false")
        resp = drive_request(token, "GET", "/files",
                             query={"q": q, "fields": "files(id,name,mimeType)", "pageSize": "10"})
        files = resp.get("files", [])
        if not files:
            raise RuntimeError(f"Could not find {desc}. Query returned no results.")
        return files[0]

    customers = _find(root_folder_id, "Customers", FOLDER_MIME,
                      f"'Customers' folder under root {root_folder_id}")
    customer = _find(customers["id"], customer_name, FOLDER_MIME,
                     f"'Customers/{customer_name}'")
    doc = _find(customer["id"], f"{customer_name} Notes", DOC_MIME,
                f"'{customer_name} Notes' in 'Customers/{customer_name}/'")
    return doc["id"]


# ---------------------------------------------------------------------------
# Phase 2: Document read & parse
# ---------------------------------------------------------------------------

def _extract_tab_payloads(doc: dict) -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    for tab in doc.get("tabs", []) or []:
        props = tab.get("tabProperties", {}) or {}
        dtab = tab.get("documentTab", {}) or {}
        payloads.append(
            {
                "tab_id": props.get("tabId"),
                "title": props.get("title", ""),
                "content": dtab.get("body", {}).get("content", []) or [],
            }
        )
    return payloads


def _content_for_tab_title(doc: dict, preferred_title: str) -> tuple[list, Optional[str]]:
    payloads = _extract_tab_payloads(doc)
    if payloads:
        for p in payloads:
            if p["title"] == preferred_title:
                return p["content"], p["tab_id"]
        # Fallback to first tab if preferred tab doesn't exist.
        return payloads[0]["content"], payloads[0]["tab_id"]
    return doc.get("body", {}).get("content", []), None


def _content_for_tab_title_strict(doc: dict, preferred_title: str) -> tuple[Optional[list], Optional[str]]:
    """Return tab body only when a tab with this exact title exists (no fallback)."""
    for p in _extract_tab_payloads(doc):
        if p["title"] == preferred_title:
            return p["content"], p["tab_id"]
    return None, None


def _content_for_tab_id(doc: dict, tab_id: Optional[str]) -> list:
    if not tab_id:
        return doc.get("body", {}).get("content", [])
    for p in _extract_tab_payloads(doc):
        if p["tab_id"] == tab_id:
            return p["content"]
    return doc.get("body", {}).get("content", [])


def fetch_document(token: str, document_id: str) -> tuple[dict, list]:
    doc = docs_request(
        token,
        "GET",
        f"/documents/{document_id}",
        query={"includeTabsContent": "true"},
    )
    # Default processing tab remains Account Summary.
    content, _ = _content_for_tab_title(doc, ACCOUNT_SUMMARY_TAB_TITLE)
    return doc, content


def extract_paragraph_text(paragraph: dict) -> str:
    parts = []
    for elem in paragraph.get("elements", []):
        content = elem.get("textRun", {}).get("content", "")
        parts.append(content)
    return "".join(parts).rstrip("\n")


def get_named_style(paragraph: dict) -> str:
    return paragraph.get("paragraphStyle", {}).get("namedStyleType", "NORMAL_TEXT")


# Paragraph styles Google Docs uses for outline headings (H1–H6).
_HEADING_NAMED_STYLES = (
    "HEADING_1",
    "HEADING_2",
    "HEADING_3",
    "HEADING_4",
    "HEADING_5",
    "HEADING_6",
)


def _field_label_line_matches(text: str, label: Optional[str]) -> bool:
    """
    True if this line is the labeled field's title line (e.g. Goals / Risk / Upsell Path).
    Use exact match, or label followed by ':' or space — not bare prefix match, so schema
    label 'Risk' does not match heading 'Risks' (which would leave inline text 's').
    """
    if not label:
        return False
    if text == label:
        return True
    if text.startswith(label + ":") or text.startswith(label + " "):
        return True
    return False


def parse_table_element(table_element: dict, column_keys: list[str]) -> list[TableRow]:
    rows = []
    table = table_element.get("table", {})
    for row_index, row in enumerate(table.get("tableRows", [])):
        if row_index == 0:
            continue
        cells = row.get("tableCells", [])
        if not cells:
            continue
        cell_texts = []
        for cell in cells:
            cell_text = ""
            for element in cell.get("content", []):
                if "paragraph" in element:
                    cell_text += extract_paragraph_text(element["paragraph"])
            cell_texts.append(cell_text.strip())
        while len(cell_texts) < len(column_keys):
            cell_texts.append("")
        cell_texts = cell_texts[: len(column_keys)]
        row_dict = dict(zip(column_keys, cell_texts))
        if all(not v for v in row_dict.values()):
            continue
        rows.append(TableRow(**row_dict))
    return rows


def _add_content_to_field(sf: SectionField, text: str) -> None:
    if sf.update_strategy == "tools_list":
        tool_key, display, detail = parse_tool_line(text)
        if tool_key and tool_key not in sf.tools:
            flagged = False
            flag_reason = flag_date = None
            rm = re.match(r"^\[REVIEW:\s*(.*?)\s*—\s*(\d{4}-\d{2}-\d{2})\]\s*(.*)$", text)
            if rm:
                flag_reason, flag_date = rm.group(1), rm.group(2)
                _, display, detail = parse_tool_line(rm.group(3))
                flagged = True
            sf.tools[tool_key] = ToolEntry(
                display=display, detail=detail,
                flagged=flagged, flag_reason=flag_reason, flag_date=flag_date,
            )
    else:
        sf.entries.append(parse_entry_text(text))


def parse_document(content: list, config: dict) -> SectionMap:
    header_to_key, section_configs, _ = build_config_lookups(config)
    sections = config.get("sections", [])
    section_map: SectionMap = {}

    for sec_cfg in sections:
        sec_key = sec_cfg["key"]
        sec_type = sec_cfg.get("type", "fields")
        sec = DocumentSection(key=sec_key, header=sec_cfg["header"],
                              level=sec_cfg["level"], section_type=sec_type)
        if sec_type == "table":
            sec.rows = []
        else:
            for f_cfg in sec_cfg.get("fields", []):
                sec.fields[f_cfg["key"]] = SectionField(
                    key=f_cfg["key"], label=f_cfg.get("label"),
                    update_strategy=f_cfg["update_strategy"],
                )
        section_map[sec_key] = sec

    current_section_key: Optional[str] = None
    current_field_key: Optional[str] = None
    last_index: dict[str, int] = {}

    for element in content:
        el_start = element.get("startIndex", 0)
        el_end = element.get("endIndex", 0)

        if "paragraph" in element:
            para = element["paragraph"]
            style = get_named_style(para)
            text = extract_paragraph_text(para).strip()

            if not text:
                if current_section_key:
                    last_index[current_section_key] = el_end
                continue

            if style in ("HEADING_1", "HEADING_2"):
                matched = header_to_key.get(text)
                if matched:
                    current_section_key = matched
                    current_field_key = None
                    section_map[matched].header_start_index = el_start
                    section_map[matched].header_end_index = el_end
                    last_index[matched] = el_end
                    continue
                # Unknown heading: do not append title text to the previous section's field
                # (e.g. H1 "Use Cases" while current_field_key was cloud_environment.sizing).
                current_field_key = None
                if style == "HEADING_1":
                    current_section_key = None
                continue

            if current_section_key:
                sec = section_map[current_section_key]
                last_index[current_section_key] = el_end

                if sec.section_type == "table":
                    continue
                if _is_guidance_line(text):
                    continue
                if current_section_key == "account_motion_metadata" and _is_ignored_metadata_label(text):
                    current_field_key = None
                    continue

                sec_cfg = section_configs.get(current_section_key, {})
                matched_field = None
                for f_cfg in sec_cfg.get("fields", []):
                    label = f_cfg.get("label")
                    if label and _field_label_line_matches(text, label):
                        matched_field = f_cfg["key"]
                        break

                if matched_field:
                    current_field_key = matched_field
                    inline_value = text
                    for f_cfg in sec_cfg.get("fields", []):
                        if f_cfg.get("key") == matched_field and f_cfg.get("label"):
                            inline_value = text[len(f_cfg["label"]):].strip().lstrip(":").strip()
                            break
                    if inline_value and inline_value != text:
                        _add_content_to_field(sec.fields[current_field_key], inline_value)
                    continue

                if current_field_key and current_field_key in sec.fields:
                    _add_content_to_field(sec.fields[current_field_key], text)
                elif sec.section_type in ("fields", "tools_section"):
                    if "free_text" in sec.fields:
                        _add_content_to_field(sec.fields["free_text"], text)

        elif "table" in element and current_section_key:
            sec = section_map[current_section_key]
            last_index[current_section_key] = el_end
            if sec.section_type == "table":
                sec_cfg = section_configs.get(current_section_key, {})
                col_keys = [c["key"] for c in sec_cfg.get("columns", [])]
                sec.rows = parse_table_element(element, col_keys)
                sec.content_end_index = el_end

    for sec_key, sec in section_map.items():
        if sec_key in last_index:
            sec.content_end_index = last_index[sec_key]

    return section_map


def _merge_tab_section_maps(
    summary_map: SectionMap,
    summary_tab_id: Optional[str],
    metadata_map: Optional[SectionMap],
    metadata_tab_id: Optional[str],
) -> SectionMap:
    # Default every section to Account Summary tab.
    for sec in summary_map.values():
        sec.tab_id = summary_tab_id

    if not metadata_map:
        return summary_map

    # Metadata-specific sections should come from Account Metadata tab when available.
    for key in ("account_motion_metadata", "deal_stage_tracker"):
        if key in metadata_map:
            summary_map[key] = metadata_map[key]
            summary_map[key].tab_id = metadata_tab_id
    return summary_map


def _merge_daily_activity_logs_from_dedicated_tab(
    section_map: SectionMap,
    dal_tab_content: list,
    dal_tab_id: str,
    config: dict,
) -> None:
    """Replace daily_activity_logs with parse of the dedicated Daily Activity Logs tab."""
    dal_map = parse_document(dal_tab_content, config)
    dal_sec = dal_map["daily_activity_logs"]
    dal_sec.tab_id = dal_tab_id
    section_map["daily_activity_logs"] = dal_sec


def _doc_tab_titles(doc: dict) -> list[str]:
    return [p["title"] for p in _extract_tab_payloads(doc)]


def section_map_to_dict(sm: SectionMap) -> dict:
    """Serialize SectionMap for JSON output (strips internal indices)."""
    result = {}
    for k, sec in sm.items():
        sec_d: dict[str, Any] = {
            "header": sec.header, "level": sec.level, "type": sec.section_type,
        }
        if sec.section_type == "table":
            if k == "deal_stage_tracker":
                sec_d["rows"] = [
                    {
                        "sku": r.challenge,
                        "stage": r.date,
                        "verification_activity": r.category,
                        "activity": r.status,
                        "reason": r.notes_references,
                    }
                    for r in sec.rows
                ]
            else:
                sec_d["rows"] = [asdict(r) for r in sec.rows]
        else:
            fields_d = {}
            for fk, fld in sec.fields.items():
                if fld.update_strategy == "tools_list":
                    fields_d[fk] = {
                        "label": fld.label, "strategy": fld.update_strategy,
                        "tools": {tk: asdict(tv) for tk, tv in fld.tools.items()},
                    }
                else:
                    fields_d[fk] = {
                        "label": fld.label, "strategy": fld.update_strategy,
                        "entries": [asdict(e) for e in fld.entries],
                    }
            sec_d["fields"] = fields_d
        result[k] = sec_d
    return result


def section_map_to_internal_dict(sm: SectionMap) -> dict:
    """Full serialization including document indices (for write-back)."""
    result = {}
    for k, sec in sm.items():
        result[k] = asdict(sec)
    return result


# ---------------------------------------------------------------------------
# Phase 4: Mutation application (in-memory)
# ---------------------------------------------------------------------------

def _active_entries(fld: SectionField) -> list[Entry]:
    return [e for e in fld.entries if e.status == "active"]


def _value_exists(fld: SectionField, val: str) -> bool:
    return any(e.value == val for e in _active_entries(fld))


def _normalize_similarity_text(value: str) -> str:
    txt = " ".join((value or "").lower().split())
    txt = re.sub(r"[^a-z0-9\\s]", " ", txt)
    # Light normalization for common plural/suffix variants.
    txt = re.sub(r"\\bprioritization\\b", "prioritize", txt)
    txt = re.sub(r"\\bpriorities\\b", "priority", txt)
    txt = re.sub(r"\\bvisibility\\b", "visible", txt)
    txt = re.sub(r"\\breporting\\b", "report", txt)
    return " ".join(txt.split())


def _token_set(value: str) -> set[str]:
    norm = _normalize_similarity_text(value)
    return {t for t in norm.split() if t and len(t) > 2}


def _jaccard_similarity(a: str, b: str) -> float:
    ta = _token_set(a)
    tb = _token_set(b)
    if not ta or not tb:
        return 0.0
    inter = len(ta & tb)
    union = len(ta | tb)
    return (inter / union) if union else 0.0


def _extract_goal_theme(text: str) -> Optional[str]:
    return _extract_challenge_theme(text)


def _merge_top_goal_by_theme(existing: str, new: str, theme: str) -> str:
    e = (existing or "").strip()
    n = (new or "").strip()
    if not e:
        return n
    if not n:
        return e
    if _normalize_similarity_text(e) == _normalize_similarity_text(n):
        return e
    el = e.lower()
    nl = n.lower()
    if theme == "prioritization":
        has_owner = ("owner" in el or "owner" in nl)
        has_routing = ("routing" in el or "routing" in nl or "route" in el or "route" in nl)
        has_container = ("container" in el or "container" in nl)
        has_cloud = ("cloud" in el or "cloud" in nl)
        tail = "so teams fix highest-impact risks first"
        scope = ""
        if has_container and has_cloud:
            scope = " across container and cloud workloads"
        elif has_container:
            scope = " across container workloads"
        elif has_cloud:
            scope = " across cloud workloads"
        lead = "Improve Sec/Eng prioritization"
        if has_owner and has_routing:
            lead += " by routing owner-ready findings"
        elif has_owner:
            lead += " with owner-ready context"
        return f"{lead}{scope} {tail}."
    if theme == "visibility":
        return "Increase CSPM, workload, and identity visibility so teams remediate with higher confidence and faster execution."
    if theme == "external_exposure":
        return "Reduce external exposure investigation drag with clearer ownership and end-to-end context for faster response."
    return n if len(n) >= len(e) else e


def _extract_mutation_evidence_date(m: dict) -> Optional[date]:
    # Preferred explicit field.
    explicit = str(m.get("evidence_date", "")).strip()
    if explicit:
        try:
            return datetime.strptime(explicit, "%Y-%m-%d").date()
        except ValueError:
            pass
    # Table row date is strongest structured source.
    row = m.get("row") or {}
    row_date = str(row.get("date", "")).strip()
    if row_date:
        try:
            return datetime.strptime(row_date, "%Y-%m-%d").date()
        except ValueError:
            pass
    # Fallback: scan common mutation text fields.
    blobs = [
        str(m.get("reasoning", "")),
        str(m.get("new_value", "")),
        str(m.get("target_value", "")),
        str(m.get("detail", "")),
    ]
    joined = " ".join(blobs)
    if match := re.search(r"(20\\d{2}-\\d{2}-\\d{2})", joined):
        try:
            return datetime.strptime(match.group(1), "%Y-%m-%d").date()
        except ValueError:
            return None
    return None


def _is_deal_risk_line(text: str) -> bool:
    t = (text or "").lower()
    if any(tok in t for tok in DEAL_RISK_TOKENS):
        return True
    # If purely technical language is present with no commercial language, fail gate.
    if any(tok in t for tok in TECHNICAL_RISK_TOKENS):
        return False
    return False


def _has_upsell_sku_token(text: str) -> bool:
    t = (text or "").lower()
    return any(tok in t for tok in UPSELL_SKU_TOKENS)


def _extract_challenge_theme(text: str) -> Optional[str]:
    t = _normalize_similarity_text(text)
    if any(k in t for k in ("prioritize", "priority", "owner", "ownership", "triage", "routing", "backlog")):
        return "prioritization"
    if any(k in t for k in ("visible", "cspm", "identity", "coverage", "sensor", "context")):
        return "visibility"
    if any(k in t for k in ("external exposure", "exposed", "internet", "egress", "ingress", "public")):
        return "external_exposure"
    return None


def _synthesized_goal_for_theme(theme: str) -> str:
    if theme == "prioritization":
        return "Improve Sec/Eng prioritization with owner-aware context so teams fix the highest-impact risks first."
    if theme == "visibility":
        return "Increase CSPM, workload, and identity visibility to improve risk confidence and remediation speed."
    return "Reduce external exposure investigation drag with stronger context and ownership mapping."


def _goal_has_associated_challenge(goal_text: str, challenge_context_texts: list[str]) -> bool:
    if not goal_text.strip() or not challenge_context_texts:
        return False
    goal_theme = _extract_goal_theme(goal_text)
    goal_norm = _normalize_similarity_text(goal_text)
    for ch in challenge_context_texts:
        if not ch.strip():
            continue
        if goal_theme and _extract_challenge_theme(ch) == goal_theme:
            return True
        # Fallback for goal/challenge lines that do not hit explicit theme keywords.
        if goal_norm and _jaccard_similarity(goal_text, ch) >= 0.18:
            return True
    return False


def _exec_summary_active_count(section_map: SectionMap, field_key: str) -> int:
    sec = section_map.get("exec_account_summary")
    if not sec or field_key not in sec.fields:
        return 0
    return len(_active_entries(sec.fields[field_key]))


def _validate_action_against_schema(
    mutation: dict,
    section_map: SectionMap,
    field_strategies: dict[tuple[str, str], str],
) -> Optional[str]:
    sec_key = str(mutation.get("section_key") or "").strip()
    action = str(mutation.get("action") or "").strip()
    field_key = mutation.get("field_key")
    if not sec_key or not action:
        return "Mutation missing section_key/action"
    sec = section_map.get(sec_key)
    if not sec:
        return f"Unknown section_key: {sec_key}"
    if sec.section_type == "table":
        if action not in TABLE_ALLOWED_ACTIONS:
            return f"Invalid action '{action}' for table section '{sec_key}'"
        return None
    if not field_key:
        return f"Mutation missing field_key for section '{sec_key}'"
    if action == "prepend_daily_activity_ai_summary":
        if sec_key != "daily_activity_logs" or field_key != "free_text":
            return (
                "prepend_daily_activity_ai_summary is only allowed for "
                f"daily_activity_logs.free_text (got {sec_key}.{field_key})"
            )
        return None
    strategy = field_strategies.get((sec_key, field_key))
    if not strategy:
        return f"Unknown field_key '{field_key}' for section '{sec_key}'"
    if sec_key == "exec_account_summary" and field_key == "top_goal" and action == "move_to_accomplishments":
        return None
    if action == "replace_field_entries":
        if not _replace_field_entries_allowed(sec_key, str(field_key or "").strip()):
            allowed_txt = ", ".join(
                f"{sk}.{'/'.join(sorted(fks))}"
                for sk, fks in sorted(REPLACE_FIELD_ENTRIES_TARGETS.items())
            )
            return f"Invalid replace_field_entries target (allowed: {allowed_txt})"
        raw = mutation.get("new_values")
        if not isinstance(raw, list):
            return "replace_field_entries requires new_values as a list of strings"
        return None
    allowed = ALLOWED_ACTIONS_BY_STRATEGY.get(strategy, set())
    if action not in allowed:
        return f"Invalid action '{action}' for strategy '{strategy}' ({sec_key}.{field_key})"
    return None


def _validate_no_evidence_marker(mutation: dict, section_map: SectionMap) -> Optional[str]:
    sec_key = str(mutation.get("section_key") or "").strip()
    field_key = str(mutation.get("field_key") or "").strip()
    if not sec_key or not field_key:
        return "no_evidence marker requires section_key and field_key"
    sec = section_map.get(sec_key)
    if not sec:
        return f"no_evidence marker has unknown section_key: {sec_key}"
    if field_key not in sec.fields:
        return f"no_evidence marker has unknown field_key '{field_key}' for section '{sec_key}'"
    return None


def _key_field_coverage_set(mutations: list[dict]) -> set[tuple[str, str]]:
    covered: set[tuple[str, str]] = set()
    for m in mutations:
        sec_key = str(m.get("section_key") or "").strip()
        field_key = str(m.get("field_key") or "").strip()
        action = str(m.get("action") or "").strip()
        key = (sec_key, field_key)
        if key not in KEY_FIELD_COVERAGE_REQUIREMENTS:
            continue
        if action in MUTATING_ACTIONS or action == "no_evidence":
            covered.add(key)
    return covered


def _contains_any_token(text: str, tokens: set[str]) -> bool:
    norm = (text or "").strip().lower()
    if not norm:
        return False
    for token in tokens:
        if token in norm:
            return True
    return False


def _count_token_hits(text: str, tokens: set[str]) -> int:
    norm = (text or "").strip().lower()
    if not norm:
        return 0
    hits = 0
    for token in tokens:
        if token in norm:
            hits += 1
    return hits


def _workflow_signal_score(text: str) -> int:
    norm = (text or "").strip().lower()
    if not norm:
        return 0
    score = 0
    if "->" in norm:
        score += 2
    if _contains_any_token(norm, {"workflow", "process", "runbook", "playbook"}):
        score += 2
    score += min(4, _count_token_hits(norm, WORKFLOW_SIGNAL_TOKENS))
    score += min(4, _count_token_hits(norm, WORKFLOW_STRONG_PHRASES) * 2)
    if _contains_any_token(norm, {"then ", "followed by", "next ", "finally ", "after that"}):
        score += 2
    return score


def _requirement_signal_score(text: str) -> int:
    norm = (text or "").strip().lower()
    if not norm:
        return 0
    score = min(4, _count_token_hits(norm, REQUIREMENT_SIGNAL_TOKENS))
    if _contains_any_token(norm, {"must", "required", "requirement", "acceptance criteria"}):
        score += 2
    return score


def _looks_like_workflow_narrative(text: str) -> bool:
    return _workflow_signal_score(text) >= 2


def _looks_like_requirement_statement(text: str) -> bool:
    return _requirement_signal_score(text) >= 2


def _should_route_to_workflows(text: str) -> bool:
    workflow_score = _workflow_signal_score(text)
    requirement_score = _requirement_signal_score(text)
    # Route to workflows when process evidence is stronger than requirement framing.
    return workflow_score >= 3 and workflow_score >= requirement_score + 1


def _should_route_to_use_cases(text: str) -> bool:
    workflow_score = _workflow_signal_score(text)
    requirement_score = _requirement_signal_score(text)
    # Route to use-cases only when requirement framing dominates and process cues are weak.
    return requirement_score >= 3 and workflow_score <= 1


def _route_use_case_workflow_mutation(mutation: dict) -> None:
    section_key = str(mutation.get("section_key") or "").strip()
    field_key = str(mutation.get("field_key") or "").strip()
    action = str(mutation.get("action") or "").strip()
    if field_key != "free_text":
        return
    if action not in {"append_with_history", "set_if_empty", "update_in_place"}:
        return
    text = str(mutation.get("new_value") or "").strip()
    if not text:
        return

    # Guardrail: keep section intent strict. Workflow narratives belong in Workflows / Processes.
    if section_key == "use_cases" and _should_route_to_workflows(text):
        mutation["section_key"] = "workflows"
        prior_reason = str(mutation.get("reasoning") or "").strip()
        suffix = (
            "Auto-routed to workflows.free_text because process-signal score "
            "exceeds requirement-signal score."
        )
        mutation["reasoning"] = f"{prior_reason} {suffix}".strip()
        return

    # Symmetric guardrail: requirement-only content should live in Use Cases / Requirements.
    if section_key == "workflows" and _should_route_to_use_cases(text):
        mutation["section_key"] = "use_cases"
        prior_reason = str(mutation.get("reasoning") or "").strip()
        suffix = (
            "Auto-routed to use_cases.free_text because requirement-signal score "
            "exceeds process-signal score."
        )
        mutation["reasoning"] = f"{prior_reason} {suffix}".strip()


def _prepare_mutations_for_write(
    section_map: SectionMap,
    mutations: list[dict],
    field_strategies: dict[tuple[str, str], str],
    max_evidence_date: Optional[date] = None,
) -> tuple[list[dict], list[dict], list[dict]]:
    """
    Returns (prepared_mutations, pre_skipped, auto_generated_mutations).
    Applies quality gate checks before in-memory mutation dispatch.
    """
    prepared: list[dict] = []
    pre_skipped: list[dict] = []
    auto_generated: list[dict] = []
    pending_norm_by_field: dict[str, set[str]] = {k: set() for k in EXEC_SUMMARY_FIELDS}
    active_norm_by_field: dict[str, set[str]] = {}
    active_values_by_field: dict[str, list[str]] = {}
    pending_values_by_field: dict[str, list[str]] = {k: [] for k in EXEC_SUMMARY_FIELDS}
    active_count_by_field: dict[str, int] = {}
    for k in EXEC_SUMMARY_FIELDS:
        sec = section_map.get("exec_account_summary")
        vals = []
        raw_vals: list[str] = []
        if sec and k in sec.fields:
            raw_vals = [e.value for e in _active_entries(sec.fields[k])]
            vals = [_normalize_similarity_text(v) for v in raw_vals]
        active_values_by_field[k] = raw_vals
        active_norm_by_field[k] = set(v for v in vals if v)
        active_count_by_field[k] = _exec_summary_active_count(section_map, k)

    challenge_context_texts: list[str] = []
    tracker = section_map.get("challenge_tracker")
    if tracker:
        for row in tracker.rows:
            if row.status in {"Open", "In Progress", "Needs Validation"}:
                challenge_context_texts.append(f"{row.challenge} {row.notes_references}".strip())
    for m in mutations:
        if m.get("section_key") != "challenge_tracker":
            continue
        if m.get("action") == "add_table_row":
            row = m.get("row") or {}
            status = str(row.get("status", "Open")).strip() or "Open"
            if status in {"Open", "In Progress", "Needs Validation"}:
                challenge_context_texts.append(
                    f"{row.get('challenge', '')} {row.get('notes_references', '')}".strip()
                )
        elif m.get("action") == "update_table_row":
            row = m.get("row") or {}
            status = str(row.get("status", "")).strip()
            if status in {"Open", "In Progress", "Needs Validation"}:
                challenge_context_texts.append(
                    f"{m.get('target_value', '')} {row.get('notes_references', '')}".strip()
                )

    for m in mutations:
        sec_key = m.get("section_key")
        field_key = m.get("field_key")
        action = m.get("action")

        sec_obj = section_map.get(sec_key) if sec_key else None
        if (
            sec_obj
            and DAILY_ACTIVITY_SKIP_PATTERNS.search(sec_obj.header)
            and action != "prepend_daily_activity_ai_summary"
        ):
            pre_skipped.append({"mutation": m, "reason": f"blocked_by_policy: Daily Activity Logs are read-only ({sec_obj.header})"})
            continue

        if action == "no_evidence":
            marker_error = _validate_no_evidence_marker(m, section_map)
            if marker_error:
                pre_skipped.append({"mutation": m, "reason": marker_error})
                continue
            reason = (m.get("reasoning") or "Planner declared no reliable evidence for this field in current run.").strip()
            pre_skipped.append({
                "mutation": m,
                "reason": f"missing_evidence declared for {sec_key}.{field_key}: {reason}",
            })
            continue

        schema_error = _validate_action_against_schema(m, section_map, field_strategies)
        if schema_error:
            pre_skipped.append({"mutation": m, "reason": schema_error})
            continue

        if action in MUTATING_ACTIONS:
            e_date = _extract_mutation_evidence_date(m)
            if e_date is None:
                pre_skipped.append({"mutation": m, "reason": "missing_evidence: mutation requires evidence_date"})
                continue

        if max_evidence_date is not None:
            e_date = _extract_mutation_evidence_date(m)
            if e_date and e_date > max_evidence_date:
                pre_skipped.append({"mutation": m, "reason": f"Evidence date {e_date.isoformat()} is after max_evidence_date {max_evidence_date.isoformat()}"})
                continue

        if sec_key == "exec_account_summary" and field_key in EXEC_SUMMARY_FIELDS:
            val = str(m.get("new_value", "")).strip()
            if action in {"append_with_history", "set_if_empty", "update_in_place"}:
                norm = _normalize_similarity_text(val)
                if not norm:
                    pre_skipped.append({"mutation": m, "reason": "Exec summary value is empty after normalization"})
                    continue
                if norm in active_norm_by_field[field_key] or norm in pending_norm_by_field[field_key]:
                    pre_skipped.append({"mutation": m, "reason": "Semantically duplicate exec summary value"})
                    continue

                pending_norm_by_field[field_key].add(norm)
                pending_values_by_field[field_key].append(val)

        # Strict metadata mode: these fields only update when mutation
        # includes an explicit same-day evidence marker.
        if sec_key == "account_motion_metadata" and field_key in STRICT_METADATA_FIELDS:
            if action in {"append_with_history", "set_if_empty", "update_in_place"}:
                if not bool(m.get("explicit_statement", False)):
                    pre_skipped.append({
                        "mutation": m,
                        "reason": f"Strict metadata field '{field_key}' requires explicit_statement=true",
                    })
                    continue
                e_date = _extract_mutation_evidence_date(m)
                if not e_date:
                    pre_skipped.append({
                        "mutation": m,
                        "reason": f"Strict metadata field '{field_key}' requires same-day evidence_date",
                    })
                    continue

        # Challenge status normalization and validation.
        if sec_key == "challenge_tracker":
            if action == "add_table_row":
                row = m.get("row") or {}
                status = str(row.get("status", "Open")).strip() or "Open"
                if status not in ALLOWED_CHALLENGE_STATUSES:
                    pre_skipped.append({"mutation": m, "reason": f"Invalid challenge status '{status}'"})
                    continue
                row["status"] = status
                m["row"] = row
            elif action == "update_table_row":
                row = m.get("row") or {}
                if "status" in row:
                    status = str(row.get("status", "")).strip()
                    if status and status not in ALLOWED_CHALLENGE_STATUSES:
                        pre_skipped.append({"mutation": m, "reason": f"Invalid challenge status '{status}'"})
                        continue

        prepared.append(m)

    # Optional synthesis from repeated challenge themes.
    if not ENABLE_SYNTHESIZED_GOALS:
        return prepared, pre_skipped, auto_generated

    # Synthesize missing strategic goals from repeated challenge themes.
    challenge_texts: list[str] = []
    tracker = section_map.get("challenge_tracker")
    if tracker:
        for r in tracker.rows:
            if r.status in {"Open", "In Progress", "Needs Validation"}:
                challenge_texts.append(f"{r.challenge} {r.notes_references}")
    for m in prepared:
        if m.get("section_key") == "challenge_tracker" and m.get("action") == "add_table_row":
            row = m.get("row") or {}
            status = str(row.get("status", "Open")).strip() or "Open"
            if status in {"Open", "In Progress", "Needs Validation"}:
                challenge_texts.append(f"{row.get('challenge', '')} {row.get('notes_references', '')}")
        if m.get("section_key") == "challenge_tracker" and m.get("action") == "update_table_row":
            row = m.get("row") or {}
            status = str(row.get("status", "")).strip()
            if status in {"Open", "In Progress", "Needs Validation"}:
                challenge_texts.append(f"{m.get('target_value', '')} {row.get('notes_references', '')}")

    theme_counts = {"prioritization": 0, "visibility": 0, "external_exposure": 0}
    for txt in challenge_texts:
        theme = _extract_challenge_theme(txt)
        if theme:
            theme_counts[theme] += 1

    existing_goal_norms = set(active_norm_by_field.get("top_goal", set())) | set(pending_norm_by_field.get("top_goal", set()))
    max_goal_capacity = MAX_EXEC_SUMMARY_ENTRIES_BY_FIELD.get("top_goal")
    goal_capacity = None if max_goal_capacity is None else max_goal_capacity - (
        active_count_by_field.get("top_goal", 0) + len(pending_norm_by_field.get("top_goal", set()))
    )
    if goal_capacity is None or goal_capacity > 0:
        for theme in ("prioritization", "visibility", "external_exposure"):
            if theme_counts[theme] < 2 or (goal_capacity is not None and goal_capacity <= 0):
                continue
            candidate = _synthesized_goal_for_theme(theme)
            norm = _normalize_similarity_text(candidate)
            if norm in existing_goal_norms:
                continue
            auto_m = {
                "section_key": "exec_account_summary",
                "field_key": "top_goal",
                "action": "append_with_history",
                "new_value": candidate,
                "reasoning": f"Synthesized from repeated open/in-progress challenges around {theme.replace('_', ' ')}",
                "source": "transcript",
            }
            auto_generated.append(auto_m)
            existing_goal_norms.add(norm)
            if goal_capacity is not None:
                goal_capacity -= 1

    return prepared + auto_generated, pre_skipped, auto_generated


def apply_mutations(section_map: SectionMap, mutations: list[dict]) -> tuple[list[dict], list[dict]]:
    """Apply a list of mutation dicts to the section map. Returns (applied, skipped)."""
    applied, skipped = [], []

    for m in mutations:
        sec_key = m.get("section_key", "")
        action = m.get("action", "")
        field_key = m.get("field_key")
        reasoning = m.get("reasoning", "")

        if sec_key not in section_map:
            skipped.append({"mutation": m, "reason": f"Unknown section_key: {sec_key}"})
            continue

        sec = section_map[sec_key]

        try:
            ok, msg = _dispatch_mutation(sec, section_map, m)
        except Exception as e:
            skipped.append({"mutation": m, "reason": f"Error: {e}"})
            continue

        evidence_date = _extract_mutation_evidence_date(m)
        entry = {
            "section_key": sec_key,
            "field_key": field_key,
            "action": action,
            "reasoning": reasoning,
            "message": msg,
            "subject": _mutation_subject(m),
            "full_change": _mutation_full_change(m),
            "evidence_date": evidence_date.isoformat() if evidence_date else "",
        }
        (applied if ok else skipped).append(
            entry if ok else {"mutation": m, "reason": msg}
        )

    return applied, skipped


def _utf16_code_unit_length(s: str) -> int:
    """Google Docs API indices count UTF-16 code units (supplementary chars = 2)."""
    n = 0
    for ch in s:
        n += 2 if ord(ch) > 0xFFFF else 1
    return n


def _workflow_entry_title_for_bold(
    sec_key: str,
    field_key: Optional[str],
    val: str,
    mutation: dict,
) -> Optional[str]:
    """Return title substring to bold when it matches the composed workflow line prefix."""
    if sec_key != "workflows" or field_key != "free_text":
        return None
    tl = str(mutation.get("title_line") or "").strip()
    if not tl or len(val) < len(tl) or val[: len(tl)] != tl:
        return None
    if len(val) == len(tl) or val[len(tl) :].startswith(" — "):
        return tl
    return None


def _dispatch_mutation(sec: DocumentSection, sm: SectionMap, m: dict) -> tuple[bool, str]:
    action = m["action"]
    field_key = m.get("field_key")

    if action == "set_if_empty":
        fld = sec.fields[field_key]
        if _active_entries(fld):
            return False, "Field already has active entries"
        val = (m.get("new_value") or "").strip()
        if not val:
            return False, "new_value is empty"
        validation_error = _validate_controlled_metadata(sec.key, field_key, val)
        if validation_error:
            return False, validation_error
        wf_title = _workflow_entry_title_for_bold(sec.key, field_key, val, m)
        fld.entries.append(
            Entry(value=val, timestamp=TODAY, status="active", workflow_title=wf_title)
        )
        return True, "Set empty field"

    elif action == "append_with_history":
        fld = sec.fields[field_key]
        val = (m.get("new_value") or "").strip()
        if not val:
            return False, "new_value is empty"
        validation_error = _validate_controlled_metadata(sec.key, field_key, val)
        if validation_error:
            return False, validation_error
        # Optional explicit relationship metadata for contacts hierarchy rendering.
        if CONTACT_HIERARCHY_ENABLED and sec.key == "contacts" and field_key == "free_text":
            reports_to = (m.get("reports_to") or "").strip()
            if reports_to:
                val = f"{val} [[reports_to:{reports_to}]]"
        if _value_exists(fld, val):
            return False, f"Value already exists: '{val[:60]}'"
        wf_title = _workflow_entry_title_for_bold(sec.key, field_key, val, m)
        fld.entries.append(
            Entry(value=val, timestamp=TODAY, status="active", workflow_title=wf_title)
        )
        return True, "Appended new entry"

    elif action == "prepend_daily_activity_ai_summary":
        if sec.key != "daily_activity_logs" or field_key != "free_text":
            return False, "prepend_daily_activity_ai_summary only applies to daily_activity_logs.free_text"
        heading = (m.get("heading_line") or "").strip()
        body = _strip_dal_body_transient_footer((m.get("body_markdown") or "").strip())
        if not heading or not body:
            return False, "heading_line and body_markdown are required"
        if len(body) > MAX_DAILY_ACTIVITY_AI_BODY_CHARS:
            return False, f"body_markdown exceeds {MAX_DAILY_ACTIVITY_AI_BODY_CHARS} characters"
        fld = sec.fields[field_key]
        hn = _normalize_daily_activity_heading_key(heading)
        for e in fld.entries:
            ev = (format_entry_for_doc(e) or "").strip()
            if not ev:
                continue
            first_line = ev.split("\n", 1)[0].strip()
            if _normalize_daily_activity_heading_key(first_line) == hn:
                return False, "Same AI heading already exists in Daily Activity Logs"
        fld.dal_prepends.append((heading, body))
        return True, "Queued AI meeting summary prepend for Daily Activity Logs"

    elif action == "update_in_place":
        fld = sec.fields[field_key]
        val = (m.get("new_value") or "").strip()
        if not val:
            return False, "new_value is empty"
        validation_error = _validate_controlled_metadata(sec.key, field_key, val)
        if validation_error:
            return False, validation_error
        active = _active_entries(fld)
        prior = active[-1].value if active else ""
        if active and active[-1].value == val:
            return False, f"Already current: '{val[:60]}'"
        for e in fld.entries:
            if e.status == "active":
                e.status = "superseded"
        wf_title = _workflow_entry_title_for_bold(sec.key, field_key, val, m)
        fld.entries.append(
            Entry(value=val, timestamp=TODAY, status="active", workflow_title=wf_title)
        )
        if prior:
            return True, f"Updated in place: '{_truncate_words(prior, 6, 48)}' -> '{_truncate_words(val, 6, 48)}'"
        return True, "Updated in place"

    elif action == "flag_for_review":
        fld = sec.fields[field_key]
        target = (m.get("target_value") or "").strip()
        if not target:
            return False, "target_value required"
        for e in fld.entries:
            if e.value == target:
                if e.status == "flagged_for_review":
                    return False, "Already flagged"
                e.status = "flagged_for_review"
                e.review_reason = m.get("reasoning", "")
                e.review_date = TODAY
                return True, f"Flagged: '{target[:60]}'"
        return False, f"Target not found: '{target[:60]}'"

    elif action == "replace_field_entries":
        if not _replace_field_entries_allowed(sec.key, field_key or ""):
            return False, "replace_field_entries target not allowed for this section/field"
        raw = m.get("new_values")
        if not isinstance(raw, list):
            return False, "new_values must be a list of strings"
        fld = sec.fields[field_key]
        fld.entries.clear()
        fld.force_doc_rewrite = True
        ts = str(m.get("entry_timestamp") or TODAY).strip() or TODAY
        added = 0
        for val in raw:
            s = str(val or "").strip()
            if not s:
                continue
            ve = _validate_controlled_metadata(sec.key, field_key, s)
            if ve:
                return False, ve
            wf_title = _workflow_entry_title_for_bold(sec.key, field_key, s, m) if sec.key == "workflows" else None
            fld.entries.append(
                Entry(value=s, timestamp=ts, status="active", workflow_title=wf_title)
            )
            added += 1
        return True, f"Replaced {sec.key}.{field_key} with {added} entr{'y' if added == 1 else 'ies'}"

    elif action == "move_to_accomplishments":
        if sec.key != "exec_account_summary" or field_key != "top_goal":
            return False, "move_to_accomplishments only supported for exec_account_summary.top_goal"
        fld = sec.fields[field_key]
        target = (m.get("target_value") or "").strip()
        if not target:
            return False, "target_value required"
        match_idx = None
        for i, e in enumerate(fld.entries):
            if e.status == "active" and (e.value or "").strip() == target:
                match_idx = i
                break
        if match_idx is None:
            return False, f"Active goal not found: '{target[:60]}'"
        removed = fld.entries.pop(match_idx)
        acc = sm.get("accomplishments")
        if not acc or "free_text" not in acc.fields:
            return False, "accomplishments.free_text section missing"
        acc_fld = acc.fields["free_text"]
        if _value_exists(acc_fld, removed.value):
            return True, f"Moved goal already present in accomplishments: '{removed.value[:60]}'"
        acc_fld.entries.append(Entry(value=removed.value, timestamp=TODAY, status="active"))
        return True, f"Moved goal to accomplishments: '{removed.value[:60]}'"

    elif action == "add_tool":
        fld = sec.fields[field_key]
        tk = (m.get("tool_key") or "").lower().replace(" ", "_").replace(".", "")
        dn = (m.get("display_name") or "").strip()
        if not tk or not dn:
            return False, "tool_key and display_name required"
        if tk in fld.tools:
            return False, f"Tool '{tk}' already exists"
        detail = _sanitize_tool_detail(m.get("detail"))
        fld.tools[tk] = ToolEntry(display=dn, detail=detail)
        return True, f"Added tool '{dn}'"

    elif action == "update_tool_detail":
        fld = sec.fields[field_key]
        tk = (m.get("tool_key") or "").lower().replace(" ", "_").replace(".", "")
        if tk not in fld.tools:
            return False, f"Tool '{tk}' not found"
        detail = _sanitize_tool_detail(m.get("detail"))
        if detail is None:
            detail = ""
        old_detail = fld.tools[tk].detail or ""
        if fld.tools[tk].detail == detail:
            return False, "Detail unchanged"
        fld.tools[tk].detail = detail or None
        if old_detail:
            return True, f"Updated detail for '{tk}': '{old_detail}' -> '{detail or '[blank]'}'"
        return True, f"Updated detail for '{tk}'"

    elif action == "remove_tool_suggestion":
        fld = sec.fields[field_key]
        tk = (m.get("tool_key") or "").lower().replace(" ", "_").replace(".", "")
        if tk not in fld.tools:
            return False, f"Tool '{tk}' not found"
        tool = fld.tools.pop(tk)
        if _is_malformed_tool_fragment(tool):
            return True, f"Removed malformed tool fragment '{tool.display}'"
        # Move removed tools to Cloud Environment Archive subsection.
        cloud = sm.get("cloud_environment")
        if not cloud:
            return True, f"Removed tool '{tk}' (cloud_environment missing; archive skipped)"
        archive_field = cloud.fields.get("archive")
        if archive_field is None:
            archive_field = SectionField(
                key="archive",
                label="Archive:",
                update_strategy="free_text",
            )
            cloud.fields["archive"] = archive_field
        detail = f" ({tool.detail})" if tool.detail else ""
        reason = (m.get("reasoning") or "No longer used").strip()
        archive_val = f"{tool.display}{detail} - archived: {reason}"
        archive_field.entries.append(Entry(value=archive_val, timestamp=TODAY, status="active"))
        return True, f"Archived removed tool '{tk}'"

    elif action == "add_table_row":
        row_data = m.get("row", {})
        challenge = row_data.get("challenge", "").strip()
        if not challenge:
            return False, "row.challenge required"
        status = str(row_data.get("status", "Open")).strip() or "Open"
        if sec.key == "challenge_tracker" and status not in ALLOWED_CHALLENGE_STATUSES:
            return False, f"Invalid row.status '{status}'"
        if sec.key == "deal_stage_tracker":
            stage = str(row_data.get("date", "")).strip().lower()
            activity = status.strip().lower()
            if stage and stage not in ALLOWED_DEAL_STAGE_VALUES:
                return False, f"Invalid deal stage '{stage}'"
            if activity and activity not in ALLOWED_DEAL_ACTIVITY_VALUES:
                return False, f"Invalid deal activity '{activity}'"
            row_data["date"] = stage
            row_data["status"] = activity
            status = activity
        # Keep challenge cell concise; move overflow detail into notes.
        notes = row_data.get("notes_references", "")
        if len(challenge) > 90:
            overflow = challenge[90:].strip()
            challenge = challenge[:90].rstrip() + "..."
            if overflow:
                notes = (f"{overflow} {notes}").strip()
        existing = [r.challenge.lower() for r in sec.rows]
        if challenge.lower() in existing:
            return False, f"Row exists: '{challenge[:60]}'"
        sec.rows.append(TableRow(
            challenge=challenge,
            date=row_data.get("date", TODAY),
            category=row_data.get("category", "Other"),
            status=status,
            notes_references=notes,
        ))
        return True, f"Added row: '{challenge[:60]}'"

    elif action == "update_table_row":
        target = (m.get("target_value") or "").strip().lower()
        row_data = m.get("row", {})
        if not target or not row_data:
            return False, "target_value and row required"
        for idx, row in enumerate(sec.rows):
            if row.challenge.lower() == target:
                new_status = (row_data.get("status") or "").strip().lower()
                if sec.key == "challenge_tracker" and new_status == "closed":
                    closure_note = (row_data.get("notes_references") or "").strip()
                    removed = sec.rows.pop(idx)
                    msg = f"Closed challenge removed from tracker: '{removed.challenge[:60]}'"
                    if closure_note:
                        msg += f"; close_note={_truncate_words(closure_note, max_words=10, max_chars=70)}"
                    return True, msg
                if "date" in row_data:
                    new_stage = str(row_data["date"]).strip().lower()
                    if sec.key == "deal_stage_tracker" and new_stage and new_stage not in ALLOWED_DEAL_STAGE_VALUES:
                        return False, f"Invalid deal stage '{new_stage}'"
                    row.date = new_stage
                if "status" in row_data:
                    if sec.key == "challenge_tracker" and row_data["status"] not in ALLOWED_CHALLENGE_STATUSES:
                        return False, f"Invalid row.status '{row_data['status']}'"
                    new_status = str(row_data["status"]).strip()
                    if sec.key == "deal_stage_tracker":
                        new_status = new_status.lower()
                        if new_status and new_status not in ALLOWED_DEAL_ACTIVITY_VALUES:
                            return False, f"Invalid deal activity '{new_status}'"
                    row.status = new_status
                if "category" in row_data:
                    row.category = row_data["category"]
                if "notes_references" in row_data:
                    new_note = row_data["notes_references"]
                    if sec.key == "challenge_tracker" and new_note and new_note not in row.notes_references:
                        row.notes_references = f"{row.notes_references}; [{TODAY}] {new_note}".strip("; ")
                    elif sec.key != "challenge_tracker":
                        row.notes_references = str(new_note or "").strip()
                return True, f"Updated row: '{row.challenge[:60]}'"
        return False, f"Row not found: '{target[:60]}'"

    return False, f"Unknown action: {action}"


def _is_malformed_tool_fragment(tool: ToolEntry) -> bool:
    disp = (tool.display or "").strip()
    # Defensive cleanup for known splice artifacts (for example: "ed)").
    if not disp:
        return True
    if re.match(r"^[a-z]{1,4}\)$", disp.lower()):
        return True
    return False


def _sanitize_tool_detail(detail: Optional[str]) -> Optional[str]:
    d = (detail or "").strip()
    if not d:
        return None
    generic_patterns = [
        r"^referenced in .*notes?$",
        r"^referenced in workflow notes?$",
        r"^referenced in pre-?sales notes?$",
        r"^mentioned in .*notes?$",
        r"^from source material$",
        r"^from notes$",
    ]
    for pat in generic_patterns:
        if re.match(pat, d, flags=re.IGNORECASE):
            return None
    if len(d) > MAX_TOOL_DETAIL_CHARS:
        d = d[: MAX_TOOL_DETAIL_CHARS - 3].rstrip() + "..."
    return d


def _validate_controlled_metadata(section_key: str, field_key: Optional[str], value: str) -> Optional[str]:
    if section_key != "account_motion_metadata" or not field_key:
        return None
    v = (value or "").strip()
    if not v:
        return "Controlled metadata value cannot be empty"
    vl = v.lower()

    if field_key == "sensor_coverage_pct":
        raw = v[:-1].strip() if v.endswith("%") else v
        try:
            pct = float(raw)
        except ValueError:
            return "Sensor Coverage % must be numeric (0-100), optional trailing %"
        if pct < 0 or pct > 100:
            return "Sensor Coverage % must be between 0 and 100"
        return None

    if field_key in NUMERIC_CONTROLLED_FIELDS:
        try:
            num = float(v)
        except ValueError:
            return f"{field_key} must be numeric"
        if num < 0:
            return f"{field_key} must be >= 0"
        if field_key == "critical_issues_open" and int(num) != num:
            return "critical_issues_open must be an integer"
        return None

    if field_key in LIST_CONTROLLED_FIELDS:
        if vl in {"none", "n/a", "unknown"}:
            return None
        parts = [p.strip() for p in v.split(",") if p.strip()]
        if not parts:
            return f"{field_key} must be a comma-separated list or one of: none, n/a, unknown"
        return None

    if field_key in {"exec_buyer", "champion", "technical_owner"}:
        return None

    return None


def _truncate_words(text: str, max_words: int = 12, max_chars: int = 88) -> str:
    clean = " ".join((text or "").strip().split())
    if not clean:
        return ""
    words = clean.split(" ")
    out = " ".join(words[:max_words])
    if len(words) > max_words or len(out) > max_chars:
        out = out[:max_chars].rstrip()
        if not out.endswith("..."):
            out += "..."
    return out


def _mutation_subject(m: dict) -> str:
    action = (m.get("action") or "").strip()
    if action == "replace_field_entries":
        fk = str(m.get("field_key") or "").strip()
        n = len(m.get("new_values") or []) if isinstance(m.get("new_values"), list) else 0
        return f"{fk} ({n} lines)".strip()
    if action in {"append_with_history", "set_if_empty", "update_in_place"}:
        return _truncate_words(str(m.get("new_value", "")))
    if action in {"flag_for_review", "update_table_row"}:
        tgt = _truncate_words(str(m.get("target_value", "")))
        row = m.get("row") or {}
        status = str(row.get("status", "")).strip()
        note = f"status={status}" if status else ""
        return f"{tgt} {note}".strip()
    if action == "add_table_row":
        row = m.get("row") or {}
        ch = _truncate_words(str(row.get("challenge", "")))
        status = str(row.get("status", "")).strip()
        return f"{ch} status={status}".strip()
    if action in {"add_tool", "remove_tool_suggestion"}:
        dn = str(m.get("display_name") or m.get("tool_key") or "").strip()
        detail = _truncate_words(str(m.get("detail", "")), max_words=8, max_chars=48)
        return f"{dn}: {detail}".strip(": ").strip()
    if action == "update_tool_detail":
        tk = str(m.get("tool_key", "")).strip()
        detail = _truncate_words(str(m.get("detail", "")), max_words=10, max_chars=64)
        return f"{tk}: {detail}".strip(": ").strip()
    return ""


def _mutation_full_change(m: dict) -> str:
    action = (m.get("action") or "").strip()
    if action == "replace_field_entries":
        raw = m.get("new_values")
        if isinstance(raw, list):
            return json.dumps(raw, ensure_ascii=True)[:8000]
        return ""
    if action in {"append_with_history", "set_if_empty", "update_in_place"}:
        return str(m.get("new_value", "")).strip()
    if action == "flag_for_review":
        target = str(m.get("target_value", "")).strip()
        reason = str(m.get("reasoning", "")).strip()
        return f"target={target}; reason={reason}".strip("; ")
    if action == "add_table_row":
        row = m.get("row") or {}
        return json.dumps(row, ensure_ascii=True)
    if action == "update_table_row":
        target = str(m.get("target_value", "")).strip()
        row = m.get("row") or {}
        return f"target={target}; row={json.dumps(row, ensure_ascii=True)}".strip("; ")
    if action in {"add_tool", "update_tool_detail"}:
        tool = str(m.get("display_name") or m.get("tool_key") or "").strip()
        detail = str(m.get("detail", "")).strip()
        return f"tool={tool}; detail={detail}".strip("; ")
    if action == "remove_tool_suggestion":
        tool = str(m.get("tool_key", "")).strip()
        reason = str(m.get("reasoning", "")).strip()
        return f"tool={tool}; reason={reason}".strip("; ")
    return json.dumps(m, ensure_ascii=True)


# ---------------------------------------------------------------------------
# Phase 5: Write-back to Google Docs
# ---------------------------------------------------------------------------

def _make_location(index: int, tab_id: Optional[str] = None) -> dict[str, Any]:
    loc: dict[str, Any] = {"index": index}
    if tab_id:
        loc["tabId"] = tab_id
    return loc


def _make_range(start_index: int, end_index: int, tab_id: Optional[str] = None) -> dict[str, Any]:
    rng: dict[str, Any] = {"startIndex": start_index, "endIndex": end_index}
    if tab_id:
        rng["tabId"] = tab_id
    return rng


def _make_insert_text(index: int, text: str, tab_id: Optional[str] = None) -> dict:
    return {"insertText": {"location": _make_location(index, tab_id=tab_id), "text": text}}


def _make_insert_with_style_requests(
    index: int,
    text: str,
    *,
    as_bullet: bool,
    indent_level: int = 0,
    tab_id: Optional[str] = None,
    bold_prefix_utf16_len: Optional[int] = None,
) -> list[dict]:
    """
    Insert one paragraph line and force NORMAL_TEXT style.
    Optionally convert it to a real Google Docs bullet paragraph.
    Optional bold span at the start of the inserted text (UTF-16 length, Docs API indexing).
    """
    text_to_insert = text
    requests: list[dict] = [_make_insert_text(index, text_to_insert, tab_id=tab_id)]
    end_index = index + len(text_to_insert)
    # Force normal paragraph style so inserted text never becomes H1/H2 accidentally.
    requests.append({
        "updateParagraphStyle": {
            "range": _make_range(index, end_index, tab_id=tab_id),
            "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
            "fields": "namedStyleType",
        }
    })
    if as_bullet:
        requests.append({
            "createParagraphBullets": {
                "range": _make_range(index, end_index, tab_id=tab_id),
                "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE",
            }
        })
        if indent_level > 0:
            # Google Docs bullets tend to default around 36pt; add depth from there.
            indent_pt = 36 + (18 * indent_level)
            requests.append({
                "updateParagraphStyle": {
                    "range": _make_range(index, end_index, tab_id=tab_id),
                    "paragraphStyle": {
                        "indentStart": {"magnitude": indent_pt, "unit": "PT"},
                    },
                    "fields": "indentStart",
                }
            })
    if bold_prefix_utf16_len and bold_prefix_utf16_len > 0:
        requests.append({
            "updateTextStyle": {
                "range": _make_range(index, index + bold_prefix_utf16_len, tab_id=tab_id),
                "textStyle": {"bold": True},
                "fields": "bold",
            }
        })
    return requests


def _normalize_daily_activity_heading_key(heading_line: str) -> str:
    """Strip markdown # markers for duplicate detection."""
    return re.sub(r"^#{1,6}\s*", "", (heading_line or "").strip())


def _strip_markdown_heading_display(heading_line: str) -> str:
    """Heading text as shown in the Doc (no literal ###); paragraph style is still HEADING_3."""
    return _normalize_daily_activity_heading_key(heading_line or "")


_DAL_ANCHORS_LINE_RE = re.compile(r"^\s*anchors\s*[-–]", re.IGNORECASE)


def _parse_dal_heading_date(heading_line: str) -> Optional[date]:
    """Parse leading YYYY-MM-DD or 'Mon D, YYYY' / 'Mon DD, YYYY' from a DAL title line."""
    s = _strip_markdown_heading_display(heading_line or "")
    if m := re.match(r"^(\d{4})-(\d{2})-(\d{2})\b", s):
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None
    if m := re.match(
        r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),?\s+(\d{4})\b",
        s,
        re.IGNORECASE,
    ):
        mon = {
            "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
            "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
        }.get(m.group(1).lower()[:3])
        if not mon:
            return None
        try:
            return date(int(m.group(3)), mon, int(m.group(2)))
        except ValueError:
            return None
    return None


def _dal_plain_and_bold_spans(line: str) -> tuple[str, list[tuple[int, int]]]:
    """Strip **bold** markers; return plain text and (start, end) spans in plain (Python indices)."""
    plain_parts: list[str] = []
    spans: list[tuple[int, int]] = []
    pos = 0
    pat = re.compile(r"\*\*(.+?)\*\*", re.DOTALL)
    while True:
        m = pat.search(line, pos)
        if not m:
            plain_parts.append(line[pos:])
            break
        plain_parts.append(line[pos : m.start()])
        base = sum(len(x) for x in plain_parts)
        inner = m.group(1)
        plain_parts.append(inner)
        spans.append((base, base + len(inner)))
        pos = m.end()
    return "".join(plain_parts), spans


def _dal_bullet_indent_and_rest(line: str) -> Optional[tuple[int, str]]:
    """If line is a markdown bullet, return (indent_level, content_after_dash). Else None."""
    m = re.match(r"^(\s*)-\s+(.*)$", line.rstrip("\r"))
    if not m:
        return None
    ws = m.group(1).replace("\t", "    ")
    indent_level = min(4, len(ws) // 2)
    return indent_level, m.group(2)


# Top-level meeting recap lines like `- **Context:** …` are section labels: bold, own line, no list bullet.
_DAL_SECTION_LABEL_MAX_LEN = 72


def _dal_try_top_level_section_label(
    indent_level: int,
    rest_after_dash: str,
) -> Optional[tuple[str, Optional[str]]]:
    """
    If this top-level bullet line is a section label (`- **Label:**` or `- **Label**` only),
    return (display_label, optional_body_text). Otherwise None.

    Lines like `- **Databricks** more text` (no colon inside the bold) stay normal bullets.
    """
    if indent_level != 0:
        return None
    m = re.match(r"^\*\*(.+?)\*\*\s*(.*)$", (rest_after_dash or "").strip())
    if not m:
        return None
    inner = m.group(1).strip()
    tail = (m.group(2) or "").strip()
    display = inner.rstrip(":").strip() or inner
    if len(display) > _DAL_SECTION_LABEL_MAX_LEN:
        return None
    inner_ends_colon = inner.rstrip().endswith(":")
    if inner_ends_colon and tail:
        return (display, tail)
    if not tail:
        return (display, None)
    return None


def _make_dal_standalone_bold_line_requests(
    index: int,
    text: str,
    *,
    tab_id: Optional[str],
) -> list[dict]:
    """One NORMAL paragraph whose entire line is bold (section label)."""
    return _make_dal_rich_paragraph_requests(
        index,
        text,
        [(0, len(text))],
        as_bullet=False,
        indent_level=0,
        tab_id=tab_id,
    )


def _utf16_offsets_in_string(s: str, py_start: int, py_end: int) -> tuple[int, int]:
    """Convert Python slice [py_start:py_end) on s to UTF-16 offsets from start of s."""
    prefix = s[:py_start]
    mid = s[py_start:py_end]
    return _utf16_code_unit_length(prefix), _utf16_code_unit_length(prefix) + _utf16_code_unit_length(mid)


def _make_dal_rich_paragraph_requests(
    index: int,
    plain_line: str,
    bold_spans_py: list[tuple[int, int]],
    *,
    as_bullet: bool,
    indent_level: int,
    tab_id: Optional[str],
) -> list[dict]:
    """Insert one paragraph (plain_line + newline) with optional bullets and **bold** spans."""
    text_to_insert = plain_line + "\n"
    reqs: list[dict] = [_make_insert_text(index, text_to_insert, tab_id=tab_id)]
    end_index = index + len(text_to_insert)
    reqs.append({
        "updateParagraphStyle": {
            "range": _make_range(index, end_index, tab_id=tab_id),
            "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
            "fields": "namedStyleType",
        },
    })
    if as_bullet:
        reqs.append({
            "createParagraphBullets": {
                "range": _make_range(index, end_index, tab_id=tab_id),
                "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE",
            },
        })
        if indent_level > 0:
            indent_pt = 36 + (18 * indent_level)
            reqs.append({
                "updateParagraphStyle": {
                    "range": _make_range(index, end_index, tab_id=tab_id),
                    "paragraphStyle": {
                        "indentStart": {"magnitude": indent_pt, "unit": "PT"},
                    },
                    "fields": "indentStart",
                },
            })
    for bs, be in bold_spans_py:
        if bs >= be or bs < 0 or be > len(plain_line):
            continue
        u0, u1 = _utf16_offsets_in_string(plain_line, bs, be)
        reqs.append({
            "updateTextStyle": {
                "range": _make_range(index + u0, index + u1, tab_id=tab_id),
                "textStyle": {"bold": True},
                "fields": "bold",
            },
        })
    return reqs


def _dal_block_end_index(
    raw_content: list,
    block_heading_start: int,
    section_header: str,
) -> int:
    """Index immediately after the last character of a DAL block that begins at block_heading_start (H3)."""
    start_i: Optional[int] = None
    for i, element in enumerate(raw_content):
        if "paragraph" not in element:
            continue
        st = element.get("startIndex", 0)
        en = element.get("endIndex", 0)
        if st <= block_heading_start < en:
            start_i = i
            break
    if start_i is None:
        return block_heading_start
    last_end = raw_content[start_i].get("endIndex", block_heading_start)
    for element in raw_content[start_i + 1 :]:
        if "paragraph" not in element:
            last_end = element.get("endIndex", last_end)
            continue
        st = element.get("startIndex", 0)
        en = element.get("endIndex", 0)
        para = element["paragraph"]
        style = get_named_style(para)
        text = extract_paragraph_text(para).strip()
        if style == "HEADING_3" and st > block_heading_start:
            return last_end
        if style in ("HEADING_1", "HEADING_2") and text and text != section_header:
            return last_end
        last_end = en
    return last_end


def _iter_dal_h3_blocks(
    raw_content: list,
    section_header: str,
    region_base: int,
) -> list[tuple[int, Optional[date]]]:
    """(paragraph_start_index, parsed_date_or_none) for each HEADING_3 in the section after region_base."""
    in_section = False
    out: list[tuple[int, Optional[date]]] = []
    for element in raw_content:
        if "paragraph" not in element:
            continue
        st = element.get("startIndex", 0)
        para = element["paragraph"]
        style = get_named_style(para)
        text = extract_paragraph_text(para).strip()
        if style in ("HEADING_1", "HEADING_2"):
            if text == section_header:
                in_section = True
                continue
            if in_section and style == "HEADING_1" and text != section_header:
                break
        if not in_section:
            continue
        if style != "HEADING_3" or not text:
            continue
        if st < region_base:
            continue
        out.append((st, _parse_dal_heading_date(text)))
    return out


def _find_daily_activity_ai_insert_index(
    raw_content: list,
    section: DocumentSection,
    heading_line: str,
) -> Optional[int]:
    """
    Insert point for a new AI summary block:
    - Default: after the 'Anchors - …' reminder line when present, else after the Daily Activity Logs H1.
    - Among dated HEADING_3 blocks, order newest-first: strictly newer than all existing → top;
      else insert before the first block whose date is strictly older than the new meeting date;
      else append after the last dated block's body.
    """
    h1_end = section.header_end_index
    if h1_end is None:
        return None
    section_header = section.header
    in_section = False
    anchors_end: Optional[int] = None
    for element in raw_content:
        if "paragraph" not in element:
            continue
        para = element["paragraph"]
        style = get_named_style(para)
        text = extract_paragraph_text(para).strip()
        if style in ("HEADING_1", "HEADING_2"):
            if text == section_header:
                in_section = True
                continue
            if in_section and style == "HEADING_1" and text != section_header:
                break
        if not in_section:
            continue
        if anchors_end is None and _DAL_ANCHORS_LINE_RE.match(text):
            anchors_end = element.get("endIndex", h1_end)
    region_base = anchors_end if anchors_end is not None else h1_end
    new_date = _parse_dal_heading_date(heading_line)
    blocks = _iter_dal_h3_blocks(raw_content, section_header, region_base)
    dated = [(st, d) for st, d in blocks if d is not None]
    if new_date is None or not dated:
        return region_base
    max_d = max(d for _, d in dated)
    if new_date > max_d:
        return region_base
    for st, bd in dated:
        if bd < new_date:
            return st
    last_start, _ = dated[-1]
    return _dal_block_end_index(raw_content, last_start, section_header)


def _strip_dal_body_transient_footer(body: str) -> str:
    """
    Remove trailing transcript/source disclaimer lines from body_markdown.
    Provenance belongs in mutation metadata (reasoning, source, evidence_date), not customer-facing Daily Activity.
    """
    lines = (body or "").split("\n")
    while lines and not lines[-1].strip():
        lines.pop()
    if lines and re.match(r"(?i)^\s*_?Source:\s*", lines[-1]):
        lines.pop()
        while lines and not lines[-1].strip():
            lines.pop()
    return "\n".join(lines).strip()


def _make_daily_activity_body_requests(
    start_index: int,
    body: str,
    *,
    tab_id: Optional[str],
) -> tuple[list[dict], int]:
    """
    Build requests to insert body lines. Section labels (`- **Context:** …`, `- **What changed**`)
    become bold NORMAL paragraphs on their own line (no list bullet); optional prose on the next
    line without a bullet. Indented `-` lines stay native bullets; other bullets keep list styling.
    """
    reqs: list[dict] = []
    cur = start_index
    total = 0
    for raw_line in (body or "").split("\n"):
        line = raw_line.rstrip("\r")
        if not line.strip():
            reqs.append(_make_insert_text(cur, "\n", tab_id=tab_id))
            chunk = 1
            reqs.append({
                "updateParagraphStyle": {
                    "range": _make_range(cur, cur + chunk, tab_id=tab_id),
                    "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                    "fields": "namedStyleType",
                },
            })
            cur += chunk
            total += chunk
            continue
        sub = _dal_bullet_indent_and_rest(line)
        if sub is not None:
            indent_level, rest = sub
            label_parts = _dal_try_top_level_section_label(indent_level, rest)
            if label_parts is not None:
                label_text, body_after = label_parts
                para_reqs = _make_dal_standalone_bold_line_requests(cur, label_text, tab_id=tab_id)
                reqs.extend(para_reqs)
                chunk = len(label_text) + 1
                cur += chunk
                total += chunk
                if body_after:
                    plain, spans = _dal_plain_and_bold_spans(body_after)
                    br = _make_dal_rich_paragraph_requests(
                        cur,
                        plain,
                        spans,
                        as_bullet=False,
                        indent_level=0,
                        tab_id=tab_id,
                    )
                    reqs.extend(br)
                    cur += len(plain) + 1
                    total += len(plain) + 1
                continue
            plain, spans = _dal_plain_and_bold_spans(rest)
        else:
            hstrip = re.sub(r"^#{1,6}\s*", "", line.strip())
            plain, spans = _dal_plain_and_bold_spans(hstrip)
        para_reqs = _make_dal_rich_paragraph_requests(
            cur,
            plain,
            spans,
            as_bullet=sub is not None,
            indent_level=sub[0] if sub is not None else 0,
            tab_id=tab_id,
        )
        reqs.extend(para_reqs)
        chunk = len(plain) + 1
        cur += chunk
        total += chunk
    # Trailing blank lines after block (same spacing as prior single-block insert)
    tail = "\n\n"
    reqs.append(_make_insert_text(cur, tail, tab_id=tab_id))
    tail_start = cur
    cur += len(tail)
    total += len(tail)
    reqs.append({
        "updateParagraphStyle": {
            "range": _make_range(tail_start, cur, tab_id=tab_id),
            "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
            "fields": "namedStyleType",
        },
    })
    return reqs, total


def _make_daily_activity_ai_prepend_requests(
    insert_at: int,
    heading_line: str,
    body: str,
    *,
    tab_id: Optional[str],
) -> list[dict]:
    """
    Insert one block: HEADING_3 title (without literal ###), blank line, then body with section labels
    (bold, no list bullet) and native bullets for nested/detail lines.
    """
    display_heading = _strip_markdown_heading_display(heading_line or "")
    body_clean = _strip_dal_body_transient_footer((body or "").strip())
    if not display_heading or not body_clean:
        return []
    prefix = display_heading + "\n\n"
    reqs: list[dict] = []
    reqs.append(_make_insert_text(insert_at, prefix, tab_id=tab_id))
    rel_break = prefix.find("\n")
    first_end = insert_at + (rel_break + 1 if rel_break != -1 else len(prefix))
    end_prefix = insert_at + len(prefix)
    reqs.append({
        "updateParagraphStyle": {
            "range": _make_range(insert_at, first_end, tab_id=tab_id),
            "paragraphStyle": {"namedStyleType": "HEADING_3"},
            "fields": "namedStyleType",
        },
    })
    if first_end < end_prefix:
        reqs.append({
            "updateParagraphStyle": {
                "range": _make_range(first_end, end_prefix, tab_id=tab_id),
                "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                "fields": "namedStyleType",
            },
        })
    body_reqs, _ = _make_daily_activity_body_requests(end_prefix, body_clean, tab_id=tab_id)
    reqs.extend(body_reqs)
    return reqs


def _make_replace_text(old: str, new: str) -> dict:
    return {"replaceAllText": {
        "containsText": {"text": old, "matchCase": True},
        "replaceText": new,
    }}


def build_write_requests(
    original: SectionMap,
    updated: SectionMap,
    raw_content: list,
    raw_content_by_tab: dict[str, list],
    table_elements: dict,
) -> tuple[list[dict], list[dict], list[dict], list[dict], list[dict], list[dict], list[dict]]:
    """Returns (regular_requests, pending_table_rows, pending_table_updates, pending_table_deletes, pending_tool_deletes, pending_tool_updates, pending_entry_deletes)."""
    replace_reqs: list[dict] = []
    insert_ops: list[dict] = []
    pending_rows: list[dict] = []
    pending_updates: list[dict] = []
    pending_deletes: list[dict] = []
    pending_tool_deletes: list[dict] = []
    pending_tool_updates: list[dict] = []
    pending_entry_deletes: list[dict] = []
    insert_seq = 0

    for sec_key, upd_sec in updated.items():
        orig_sec = original.get(sec_key)
        sec_content = raw_content_by_tab.get(upd_sec.tab_id or "", raw_content)

        if upd_sec.section_type == "table":
            _diff_table(orig_sec, upd_sec, replace_reqs, pending_rows, pending_updates, pending_deletes,
                        table_elements.get(sec_key))
            continue

        for fk, upd_fld in upd_sec.fields.items():
            orig_fld = orig_sec.fields.get(fk) if orig_sec else None

            if upd_fld.update_strategy == "tools_list":
                new_tools = {k: v for k, v in upd_fld.tools.items()
                             if not orig_fld or k not in orig_fld.tools}
                removed_tools = {}
                if orig_fld:
                    removed_tools = {k: v for k, v in orig_fld.tools.items() if k not in upd_fld.tools}
                for tk, tv in new_tools.items():
                    line = _format_tool_line_for_section(sec_key, fk, tv)
                    idx = _find_field_insert_index(sec_content, upd_sec, upd_fld)
                    if idx is not None:
                        idx = _normalize_insert_index(idx, sec_content)
                        insert_ops.append({
                            "index": idx,
                            "seq": insert_seq,
                            "requests": _make_insert_with_style_requests(
                                idx,
                                line + "\n",
                                as_bullet=_should_bulletize(sec_key, fk),
                                tab_id=upd_sec.tab_id,
                            ),
                        })
                        insert_seq += 1

                if orig_fld:
                    for _, old_tool in removed_tools.items():
                        pending_tool_deletes.append({
                            "section_header": upd_sec.header,
                            "field_label": upd_fld.label,
                            "tool_line": format_tool_line(old_tool),
                            "tab_id": upd_sec.tab_id,
                        })
                    for tk, upd_tool in upd_fld.tools.items():
                        if tk in orig_fld.tools:
                            orig_tool = orig_fld.tools[tk]
                            old_line = format_tool_line(orig_tool)
                            new_line = format_tool_line(upd_tool)
                            if old_line != new_line:
                                # Tool lines can share prefixes (e.g., "GitHub" and "GitHub Actions").
                                # Avoid global replaceAllText to prevent accidental line corruption.
                                pending_tool_updates.append({
                                    "section_header": upd_sec.header,
                                    "field_label": upd_fld.label,
                                    "old_line": old_line,
                                    "new_line": new_line,
                                    "tab_id": upd_sec.tab_id,
                                })
            else:
                orig_count = len(orig_fld.entries) if orig_fld else 0
                # replace_field_entries: always rewrite the Doc (delete old paragraphs, insert new) so
                # paragraph bullets / styles apply even when text is unchanged from last read.
                if getattr(upd_fld, "force_doc_rewrite", False):
                    new_entries = list(upd_fld.entries)
                # Append path: only entries after the original prefix (same length or longer list).
                # replace_field_entries often produces a *shorter* list; upd_fld.entries[orig_count:] is then
                # empty and nothing gets inserted while stale lines may still be deleted — bad.
                elif not orig_fld:
                    new_entries = list(upd_fld.entries)
                elif len(upd_fld.entries) > orig_count:
                    new_entries = list(upd_fld.entries[orig_count:])
                else:
                    orig_line_set = {
                        _format_entry_line_for_section(sec_key, fk, oe).strip()
                        for oe in orig_fld.entries
                    }
                    new_entries = [
                        e for e in upd_fld.entries
                        if _format_entry_line_for_section(sec_key, fk, e).strip()
                        and _format_entry_line_for_section(sec_key, fk, e).strip() not in orig_line_set
                    ]
                contact_rel_map = _build_contact_relation_map(upd_fld.entries) if (sec_key == "contacts" and fk == "free_text") else {}
                inserted_runlog_label = False
                inserted_field_label = False
                if sec_key == "daily_activity_logs" and fk == "free_text" and upd_fld.dal_prepends:
                    # Sort oldest->newest for stable ordering. insert_ops below sorts by (index, seq)
                    # reverse=True: higher seq runs first. At the *same* insert index, each Google Docs
                    # insertText prepends *above* prior inserts, so API order must be oldest→newest
                    # for visual order newest→first (matches docs/ai/references/daily-activity-ai-prepend.md).
                    ordered_dal_prepends = sorted(
                        list(upd_fld.dal_prepends),
                        key=lambda pair: (
                            _parse_dal_heading_date((pair[0] or "").strip()) or date.min,
                            (pair[0] or "").strip(),
                        ),
                    )
                    n_dal = len(ordered_dal_prepends)
                    dal_added = 0
                    for off, (hd, bd) in enumerate(ordered_dal_prepends):
                        dal_idx = _find_daily_activity_ai_insert_index(sec_content, upd_sec, hd.strip())
                        if dal_idx is None:
                            continue
                        dal_idx = _normalize_insert_index(dal_idx, sec_content)
                        insert_ops.append({
                            "index": dal_idx,
                            "seq": insert_seq + (n_dal - 1 - off),
                            "requests": _make_daily_activity_ai_prepend_requests(
                                dal_idx, hd.strip(), bd.strip(), tab_id=upd_sec.tab_id
                            ),
                        })
                        dal_added += 1
                    insert_seq += dal_added
                for entry in new_entries:
                    line = _format_entry_line_for_section(sec_key, fk, entry)
                    if not line:
                        continue
                    idx = _find_field_insert_index(sec_content, upd_sec, upd_fld)
                    if idx is not None:
                        idx = _normalize_insert_index(idx, sec_content)
                        if upd_fld.label and not inserted_field_label and not _field_label_exists(sec_content, upd_sec.header, upd_fld.label):
                            insert_ops.append({
                                "index": idx,
                                "seq": insert_seq,
                                "requests": _make_insert_with_style_requests(
                                    idx,
                                    upd_fld.label + "\n",
                                    as_bullet=False,
                                    tab_id=upd_sec.tab_id,
                                ),
                            })
                            insert_seq += 1
                            inserted_field_label = True
                        if (
                            sec_key == "appendix"
                            and fk == "agent_run_log"
                            and upd_fld.label
                            and not inserted_runlog_label
                            and not _field_label_exists(sec_content, upd_sec.header, upd_fld.label)
                        ):
                            # Create explicit label once when older docs are missing it.
                            insert_ops.append({
                                "index": idx,
                                "seq": insert_seq,
                                "requests": _make_insert_with_style_requests(
                                    idx,
                                    upd_fld.label + "\n",
                                    as_bullet=False,
                                    tab_id=upd_sec.tab_id,
                                ),
                            })
                            insert_seq += 1
                            inserted_runlog_label = True
                        indent_level = _contact_indent_level(entry, contact_rel_map) if (sec_key == "contacts" and fk == "free_text") else 0
                        bold_prefix = None
                        if (
                            sec_key == "workflows"
                            and fk == "free_text"
                            and getattr(entry, "workflow_title", None)
                        ):
                            wt = (entry.workflow_title or "").strip()
                            if wt and line.startswith(wt) and (
                                len(line) == len(wt) or line[len(wt) :].startswith(" — ")
                            ):
                                bold_prefix = _utf16_code_unit_length(wt)
                        insert_ops.append({
                            "index": idx,
                            "seq": insert_seq,
                            "requests": _make_insert_with_style_requests(
                                idx,
                                line + "\n",
                                as_bullet=_should_bulletize(sec_key, fk),
                                indent_level=indent_level,
                                tab_id=upd_sec.tab_id,
                                bold_prefix_utf16_len=bold_prefix,
                            ),
                        })
                        insert_seq += 1

                if orig_fld:
                    if sec_key != "exec_account_summary":
                        for i, upd_e in enumerate(upd_fld.entries):
                            if i < len(orig_fld.entries):
                                orig_e = orig_fld.entries[i]
                                if orig_e.status != upd_e.status:
                                    old_t = _format_entry_line_for_section(sec_key, fk, orig_e)
                                    new_t = _format_entry_line_for_section(sec_key, fk, upd_e)
                                    if old_t and not new_t:
                                        pending_entry_deletes.append({
                                            "section_header": upd_sec.header,
                                            "entry_line": old_t.strip(),
                                            "tab_id": upd_sec.tab_id,
                                        })
                                    elif old_t != new_t and old_t and new_t:
                                        replace_reqs.append(_make_replace_text(old_t, new_t))
                    if getattr(upd_fld, "force_doc_rewrite", False):
                        for orig_e in orig_fld.entries:
                            orig_val = (orig_e.value or "").strip()
                            if orig_val:
                                pending_entry_deletes.append({
                                    "section_header": upd_sec.header,
                                    "entry_line": orig_val,
                                    "tab_id": upd_sec.tab_id,
                                })
                    else:
                        upd_values = {
                            (e.value or "").strip()
                            for e in upd_fld.entries
                            if (e.value or "").strip()
                        }
                        for orig_e in orig_fld.entries:
                            orig_val = (orig_e.value or "").strip()
                            if orig_val and orig_val not in upd_values:
                                pending_entry_deletes.append({
                                    "section_header": upd_sec.header,
                                    "entry_line": orig_val,
                                    "tab_id": upd_sec.tab_id,
                                })

    # For equal indices, apply later logical lines first so final visual order is preserved.
    insert_ops.sort(key=lambda op: (op["index"], op["seq"]), reverse=True)
    insert_reqs: list[dict] = []
    for op in insert_ops:
        insert_reqs.extend(op["requests"])
    # Critical ordering: run index-based inserts before replaceAllText requests.
    # replaceAllText can change text lengths and invalidate precomputed indices.
    return insert_reqs + replace_reqs, pending_rows, pending_updates, pending_deletes, pending_tool_deletes, pending_tool_updates, pending_entry_deletes


def _normalize_insert_index(index: int, raw_content: list) -> int:
    """Docs API requires insert index to be strictly less than segment end index."""
    doc_end = 1
    for el in raw_content:
        end_idx = el.get("endIndex")
        if isinstance(end_idx, int) and end_idx > doc_end:
            doc_end = end_idx
    if index >= doc_end:
        return max(1, doc_end - 1)
    return index


def _format_entry_line_for_section(section_key: str, field_key: str, entry: Entry) -> str:
    return format_entry_for_doc(entry)


def _is_guidance_line(text: str) -> bool:
    t = (text or "").strip().lower()
    return t.startswith("guide:") or t.startswith("about:") or t.startswith("note:")


def _is_ignored_metadata_label(text: str) -> bool:
    return (text or "").strip() in {
        "Wiz Purchased Capabilities:",
        "Customer Stage:",
        "Commercial State:",
        "Renewal Timing:",
        "Blocker Summary:",
        "Tools In Replacement:",
        "Tools Decommissioned:",
        "Metadata Gaps:",
        "Deal Stage Timeline:",
    }


def _account_metadata_guidance_pairs() -> list[tuple[str, str]]:
    return [
        ("Exec Buyer:", ""),
        ("Champion:", ""),
        ("Technical Owner:", ""),
        ("Sensor Coverage %:", ""),
        ("Critical Issues Open:", ""),
        ("MTTR Days:", ""),
        ("Monthly Reporting Hours:", ""),
    ]


def _account_metadata_scaffold_text() -> str:
    lines = [ACCOUNT_METADATA_HEADER, ""]
    for label, about in _account_metadata_guidance_pairs():
        lines.append(label)
        if about:
            lines.append(about)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _normalize_challenge_key(text: str) -> str:
    base = " ".join((text or "").strip().lower().split())
    if not base:
        return ""
    base = re.sub(r"^\[.*?\]\s*", "", base)
    base = re.sub(r"[^a-z0-9\s]", " ", base)
    return " ".join(base.split())


def _reconcile_challenges_with_tracker(section_map: SectionMap) -> list[dict]:
    changes: list[dict] = []
    challenges_sec = section_map.get("challenges")
    tracker_sec = section_map.get("challenge_tracker")
    if not challenges_sec or not tracker_sec:
        return changes
    fld = challenges_sec.fields.get("free_text")
    if not fld:
        return changes

    existing_keys = {
        _normalize_challenge_key(r.challenge): r
        for r in tracker_sec.rows
        if _normalize_challenge_key(r.challenge)
    }
    retained_entries: list[Entry] = []
    for entry in fld.entries:
        val = (entry.value or "").strip()
        if entry.status != "active" or not val:
            retained_entries.append(entry)
            continue
        key = _normalize_challenge_key(val)
        if not key:
            retained_entries.append(entry)
            continue

        if key in existing_keys:
            changes.append({
                "section_key": "challenges",
                "field_key": "free_text",
                "action": "dedupe_with_table",
                "reasoning": "Removed duplicate bullet already tracked in Challenge Tracker",
                "message": f"Removed challenge bullet already in tracker: '{_truncate_words(val, max_words=10, max_chars=70)}'",
                "subject": _truncate_words(val, max_words=10, max_chars=70),
                "full_change": val,
            })
            continue

        short_challenge = _truncate_words(val, max_words=9, max_chars=72)
        row = TableRow(
            challenge=short_challenge,
            date=TODAY,
            category="Other",
            status="Open",
            notes_references=val,
        )
        tracker_sec.rows.append(row)
        existing_keys[key] = row
        changes.append({
            "section_key": "challenge_tracker",
            "field_key": "table",
            "action": "promote_bullet_to_table",
            "reasoning": "Challenge existed as bullet only; promoted to table for canonical tracking",
            "message": f"Added challenge row from bullet: '{_truncate_words(short_challenge, max_words=10, max_chars=70)}'",
            "subject": _truncate_words(short_challenge, max_words=10, max_chars=70),
            "full_change": f"{short_challenge} | {TODAY} | Other | Open | {val}",
        })
        changes.append({
            "section_key": "challenges",
            "field_key": "free_text",
            "action": "remove_bullet_after_promotion",
            "reasoning": "Removed bullet after promoting challenge to table",
            "message": f"Removed challenge bullet after table promotion: '{_truncate_words(val, max_words=10, max_chars=70)}'",
            "subject": _truncate_words(val, max_words=10, max_chars=70),
            "full_change": val,
        })
        # Do not retain bullet once promoted.
    fld.entries = retained_entries
    return changes


def _merge_duplicate_top_goal_themes(section_map: SectionMap) -> list[dict]:
    changes: list[dict] = []
    sec = section_map.get("exec_account_summary")
    if not sec or "top_goal" not in sec.fields:
        return changes
    fld = sec.fields["top_goal"]
    active_entries = [e for e in fld.entries if e.status == "active" and (e.value or "").strip()]
    if len(active_entries) < 2:
        return changes

    groups: dict[str, list[Entry]] = {}
    for e in active_entries:
        theme = _extract_goal_theme(e.value or "")
        if not theme:
            continue
        groups.setdefault(theme, []).append(e)

    for theme, entries in groups.items():
        if len(entries) < 2:
            continue
        merged = entries[0].value or ""
        for e in entries[1:]:
            merged = _merge_top_goal_by_theme(merged, e.value or "", theme)
        # Keep one canonical active entry and remove other same-theme duplicates.
        keep_idx = 0
        existing_norm = _normalize_similarity_text(merged)
        for i, e in enumerate(entries):
            if _normalize_similarity_text(e.value or "") == existing_norm:
                keep_idx = i
                break
        keep_entry = entries[keep_idx]
        keep_entry.value = merged
        keep_ids = {id(keep_entry)}
        fld.entries = [e for e in fld.entries if (id(e) in keep_ids) or (e not in entries)]
        changes.append({
            "section_key": "exec_account_summary",
            "field_key": "top_goal",
            "action": "auto_merge_top_goal_theme",
            "reasoning": f"Merged duplicate top_goal entries for theme '{theme}' into one canonical goal",
            "message": f"Merged {len(entries)} top_goal entries for theme '{theme}'",
            "subject": theme,
            "full_change": merged,
        })
    return changes


def _remove_exec_summary_superseded(section_map: SectionMap) -> list[dict]:
    changes: list[dict] = []
    sec = section_map.get("exec_account_summary")
    if not sec:
        return changes
    for fk in ("top_goal", "risk", "upsell_path"):
        fld = sec.fields.get(fk)
        if not fld:
            continue
        before = len(fld.entries)
        removed_vals = [e.value for e in fld.entries if e.status == "superseded"]
        if not removed_vals:
            continue
        fld.entries = [e for e in fld.entries if e.status != "superseded"]
        changes.append({
            "section_key": "exec_account_summary",
            "field_key": fk,
            "action": "auto_cleanup_exec_summary",
            "reasoning": "Removed superseded exec-summary lines to keep customer-facing summary concise",
            "message": f"Removed {before - len(fld.entries)} superseded exec-summary line(s)",
            "subject": fk,
            "full_change": "; ".join(removed_vals[:3]),
        })
    return changes


def _auto_populate_account_metadata(section_map: SectionMap) -> list[dict]:
    applied: list[dict] = []
    account = section_map.get("account_motion_metadata")
    stage_tracker = section_map.get("deal_stage_tracker")
    if not account:
        return applied

    # Seed deal-stage tracker defaults when empty.
    if stage_tracker and stage_tracker.section_type == "table" and not stage_tracker.rows:
        defaults = [
            TableRow(
                challenge="cloud",
                date="not-active",
                category="",
                status="inactive",
                notes_references="bootstrap default",
            ),
            TableRow(
                challenge="sensor",
                date="not-active",
                category="unverified",
                status="inactive",
                notes_references="no active opportunity",
            ),
            TableRow(
                challenge="defend",
                date="not-active",
                category="unverified",
                status="inactive",
                notes_references="no active opportunity",
            ),
            TableRow(
                challenge="code",
                date="not-active",
                category="unverified",
                status="inactive",
                notes_references="no active opportunity",
            ),
        ]
        stage_tracker.rows.extend(defaults)
        applied.append({
            "section_key": "deal_stage_tracker",
            "field_key": "table",
            "action": "auto_seed_stage_tracker",
            "reasoning": "Initialized default per-SKU deal-stage rows using allowed stage/activity values",
            "message": "Seeded default Deal Stage Tracker rows",
            "subject": "allowed deal-stage baseline",
            "full_change": json.dumps([asdict(r) for r in defaults], ensure_ascii=True),
        })
    elif stage_tracker and stage_tracker.section_type != "table":
        fld = stage_tracker.fields.get("free_text")
        if fld and not _active_entries(fld):
            defaults = [
                "cloud | not-active |  |  |  | inactive | bootstrap default",
                "sensor | not-active |  |  |  | inactive | no active opportunity",
                "defend | not-active |  |  |  | inactive | no active opportunity",
                "code | not-active |  |  |  | inactive | no active opportunity",
            ]
            for line in defaults:
                fld.entries.append(Entry(value=line, timestamp=TODAY, status="active"))
            applied.append({
                "section_key": "deal_stage_tracker",
                "field_key": "free_text",
                "action": "auto_seed_stage_tracker",
                "reasoning": "Initialized default per-SKU deal-stage rows (cloud pre-sale baseline)",
                "message": "Seeded default Deal Stage Tracker rows",
                "subject": "cloud pre-sale baseline",
                "full_change": " ; ".join(defaults),
            })

    return applied


def _cleanup_generic_tool_details(section_map: SectionMap) -> list[dict]:
    applied: list[dict] = []
    cloud = section_map.get("cloud_environment")
    if not cloud:
        return applied
    for field_key, fld in cloud.fields.items():
        if fld.update_strategy != "tools_list":
            continue
        for tk, tool in fld.tools.items():
            old = tool.detail or ""
            new = _sanitize_tool_detail(old)
            if (new or "") == old:
                continue
            tool.detail = new
            applied.append({
                "section_key": "cloud_environment",
                "field_key": field_key,
                "action": "auto_cleanup_tool_detail",
                "reasoning": "Removed low-signal generic tool detail text",
                "message": f"Cleared generic detail for tool '{tk}'",
                "subject": tk,
                "full_change": old,
            })
    return applied


NON_CONTACT_PREFIXES = {
    "inventory", "platform", "reporting", "compliance", "use case", "visibility",
    "governance", "workflow", "priority", "challenge", "risk", "goal",
}
NON_CONTACT_TOKENS = {
    "stacklet", "prodsec", "infra", "dealreview", "architecture", "overview",
    "csw", "aispm", "workflow", "meeting", "call",
}


def _normalize_contact_value(value: str) -> str:
    text = (value or "").strip()
    if not text:
        return ""
    if " - " in text:
        left, right = text.split(" - ", 1)
        rr = right.strip().lower()
        if rr in {"stakeholder", "contact", "participant", "attendee"}:
            return left.strip()
    return text


def _is_probable_contact_entry(value: str) -> bool:
    text = _normalize_contact_value(value)
    if not text:
        return False
    left = text.split(" - ", 1)[0].strip()
    if not left:
        return False
    if left.lower() in NON_CONTACT_PREFIXES:
        return False
    if any(left.lower().startswith(pfx + " ") for pfx in NON_CONTACT_PREFIXES):
        return False
    # Accept person names with 2-5 tokens and optional lowercase particles.
    if any(tok in left.lower().split() for tok in NON_CONTACT_TOKENS):
        return False
    tokens = [t for t in left.split() if t]
    if len(tokens) < 2 or len(tokens) > 5:
        return False
    particles = {"de", "da", "del", "van", "von", "bin", "al", "la", "le"}
    for t in tokens:
        if t.lower() in particles:
            continue
        if not re.match(r"^[A-Za-z][A-Za-z\\.'-]*$", t):
            return False
    capitals = sum(1 for t in tokens if t[:1].isupper())
    return capitals >= 1


def _auto_cleanup_contacts(section_map: SectionMap) -> list[dict]:
    """Optional post-apply heuristic filter; disabled by default (LLM-led contact quality)."""
    if not AUTO_CLEANUP_CONTACTS_AFTER_APPLY:
        return []
    applied: list[dict] = []
    contacts = section_map.get("contacts")
    if not contacts or "free_text" not in contacts.fields:
        return applied
    fld = contacts.fields["free_text"]
    kept: list[Entry] = []
    removed: list[str] = []
    seen_norm: set[str] = set()
    for e in fld.entries:
        if e.status != "active":
            kept.append(e)
            continue
        val = (e.value or "").strip()
        normalized_val = _normalize_contact_value(val)
        if normalized_val != val and normalized_val:
            e.value = normalized_val
            val = normalized_val
            applied.append({
                "section_key": "contacts",
                "field_key": "free_text",
                "action": "auto_normalize_contact",
                "reasoning": "Removed low-signal generic contact suffix",
                "message": f"Normalized contact line to '{_truncate_words(val, 8, 80)}'",
                "subject": _truncate_words(val, 8, 80),
                "full_change": val,
            })
        if not _is_probable_contact_entry(val):
            removed.append(val)
            continue
        norm = _normalize_similarity_text(val)
        if norm in seen_norm:
            removed.append(val)
            continue
        seen_norm.add(norm)
        kept.append(e)
    if removed:
        fld.entries = kept
        for val in removed:
            applied.append({
                "section_key": "contacts",
                "field_key": "free_text",
                "action": "auto_cleanup_contacts",
                "reasoning": "Removed non-contact or duplicate contact line",
                "message": f"Removed invalid contact line: '{_truncate_words(val, 8, 80)}'",
                "subject": _truncate_words(val, 8, 80),
                "full_change": val,
            })
    return applied


TOOL_DETAIL_DEFAULTS = {
    "jenkins": "pipeline orchestration for build and deployment workflows",
    "github": "source repository platform for application and infrastructure code",
    "github_actions": "CI/CD and PR security check workflow automation",
    "flux": "GitOps deployment management for Kubernetes workloads",
    "helm": "Kubernetes packaging and chart-based deployment management",
    "harbor": "container image registry and artifact repository",
    "terraform": "infrastructure-as-code provisioning and policy workflows",
    "cloudformation": "AWS infrastructure-as-code template deployment",
    "stacklet": "policy/tagging/remediation governance across cloud resources",
    "anchore": "container image vulnerability scanning and SBOM context",
    "tines": "security workflow orchestration and automation",
    "fossa": "software composition and SBOM analysis visibility",
    "semgrep": "SAST/SCA policy checks in code workflows",
    "sonarqube": "legacy code quality and static analysis workflows",
    "chainguard": "hardened base image and software supply chain controls",
    "qualys": "VM and exposure scanning signal source",
    "carbonblack": "endpoint detection and response agent coverage",
    "veza": "CIEM visibility and identity entitlement context",
    "panther": "SIEM and detection analytics workflows",
    "defect_dojo": "vulnerability ticketing bridge in restricted environments",
}


def _canonical_tool_display(tool_key: str, display: str) -> str:
    tk = (tool_key or "").strip().lower()
    d = (display or "").strip()
    dl = d.lower()
    if (("github" in tk and "actions" in tk) or ("github" in dl and "actions" in dl)):
        return "GitHub Actions"
    if tk.startswith("semgrep") or "semgrep" in dl:
        return "Semgrep"
    if tk == "defect_dojo":
        return "Defect Dojo"
    return d


def _auto_cleanup_tool_display_and_dedupe(section_map: SectionMap) -> list[dict]:
    applied: list[dict] = []
    cloud = section_map.get("cloud_environment")
    if not cloud:
        return applied
    for field_key, fld in cloud.fields.items():
        if fld.update_strategy != "tools_list":
            continue
        by_key = list(fld.tools.items())
        rebuilt: dict[str, ToolEntry] = {}
        seen_names: dict[str, str] = {}
        for tk, tool in by_key:
            canonical = _canonical_tool_display(tk, tool.display)
            if canonical and canonical != tool.display:
                old = tool.display
                tool.display = canonical
                applied.append({
                    "section_key": "cloud_environment",
                    "field_key": field_key,
                    "action": "auto_cleanup_tool_display",
                    "reasoning": "Normalized malformed tool display text",
                    "message": f"Normalized tool display '{_truncate_words(old, 8, 80)}' -> '{canonical}'",
                    "subject": canonical,
                    "full_change": f"{old} -> {canonical}",
                })
            nk = _normalize_similarity_text(tool.display)
            if nk in seen_names:
                winner_key = seen_names[nk]
                winner = rebuilt[winner_key]
                # Prefer the version with a detail payload.
                if (not winner.detail) and tool.detail:
                    rebuilt[winner_key] = tool
                applied.append({
                    "section_key": "cloud_environment",
                    "field_key": field_key,
                    "action": "auto_dedupe_tool",
                    "reasoning": "Removed duplicate tool entry after normalization",
                    "message": f"Removed duplicate tool entry '{tool.display}'",
                    "subject": tool.display,
                    "full_change": tool.display,
                })
                continue
            rebuilt[tk] = tool
            seen_names[nk] = tk
        fld.tools = rebuilt
    return applied


def _auto_enrich_cloud_tool_details(section_map: SectionMap) -> list[dict]:
    applied: list[dict] = []
    cloud = section_map.get("cloud_environment")
    if not cloud:
        return applied
    for field_key, fld in cloud.fields.items():
        if fld.update_strategy != "tools_list":
            continue
        for tk, tool in fld.tools.items():
            key = (tk or "").strip().lower()
            if not key:
                continue
            current = (tool.detail or "").strip()
            if current:
                continue
            detail = TOOL_DETAIL_DEFAULTS.get(key)
            if not detail:
                continue
            tool.detail = detail
            applied.append({
                "section_key": "cloud_environment",
                "field_key": field_key,
                "action": "auto_enrich_tool_detail",
                "reasoning": "Enriched tool with one-line usage description",
                "message": f"Enriched tool '{tk}' detail",
                "subject": tk,
                "full_change": detail,
            })
    return applied


def _format_tool_line_for_section(section_key: str, field_key: str, tool: ToolEntry) -> str:
    return format_tool_line(tool)


def _should_bulletize(section_key: str, field_key: str) -> bool:
    if section_key == "exec_account_summary":
        return True
    if section_key == "cloud_environment" and field_key in {
        "csp_regions",
        "sizing",
        "platforms",
        "idp_sso",
        "devops_vcs",
        "security_tools",
        "aspm_tools",
        "ticketing",
        "languages",
        "archive",
    }:
        return True
    if field_key == "free_text" and section_key in {
        "challenges", "contacts", "use_cases", "workflows", "accomplishments", "discovery",
    }:
        return True
    return False


def _build_contact_relation_map(entries: list[Entry]) -> dict[str, str]:
    rel: dict[str, str] = {}
    for e in entries:
        child = _extract_contact_name(e.value)
        parent = _extract_contact_parent(e.value)
        if child and parent:
            rel[child] = parent
    return rel


def _contact_indent_level(entry: Entry, rel_map: dict[str, str]) -> int:
    if not CONTACT_HIERARCHY_ENABLED:
        return 0
    child = _extract_contact_name(entry.value)
    seen = set()
    level = 0
    while child in rel_map and child not in seen and level < 4:
        seen.add(child)
        parent = rel_map[child]
        if not parent:
            break
        level += 1
        child = parent
    return level


def _find_field_insert_index(
    raw_content: list,
    section: DocumentSection,
    field: SectionField,
) -> Optional[int]:
    """
    Find a stable insertion point for a specific field block.
    For labeled fields, insert at the end of that field's current block.
    For free-text fields, fallback to section.content_end_index.
    """
    if not field.label:
        return _find_section_insert_index(raw_content, section.header) or section.content_end_index

    other_labels = {f.label for f in section.fields.values() if f.label and f.label != field.label}
    in_section = False
    in_field = False
    field_last_end: Optional[int] = None

    for element in raw_content:
        if "paragraph" not in element:
            if in_field:
                field_last_end = element.get("endIndex", field_last_end or 0)
            continue

        para = element["paragraph"]
        style = para.get("paragraphStyle", {}).get("namedStyleType", "")
        text = extract_paragraph_text(para).strip()
        end_index = element.get("endIndex", 0)

        if style in _HEADING_NAMED_STYLES:
            if text == section.header:
                in_section = True
                in_field = False
                continue
            # Once a labeled field is active, treat any different heading as
            # the boundary of that field block to avoid cross-subsection bleed.
            if in_section and in_field and text != field.label:
                break
            if in_section and style in ("HEADING_1", "HEADING_2") and _is_next_section_heading(
                style, section.level
            ):
                # next section starts; field block ended
                break

        if not in_section:
            continue

        if _field_label_line_matches(text, field.label):
            in_field = True
            field_last_end = end_index
            continue

        if in_field and (
            text in other_labels or any(_field_label_line_matches(text, lbl) for lbl in other_labels)
        ):
            # reached next field label within the same section
            break

        if in_field:
            field_last_end = end_index

    if field_last_end is not None:
        return field_last_end
    return _find_section_insert_index(raw_content, section.header) or section.content_end_index


def _find_section_insert_index(raw_content: list, section_header: str) -> Optional[int]:
    """Find section end index by scanning from its heading to next heading."""
    section_level = _section_level_from_header(raw_content, section_header)
    in_section = False
    section_end: Optional[int] = None
    for element in raw_content:
        if "paragraph" in element:
            para = element["paragraph"]
            style = para.get("paragraphStyle", {}).get("namedStyleType", "")
            text = extract_paragraph_text(para).strip()
            if style in ("HEADING_1", "HEADING_2"):
                if text == section_header:
                    in_section = True
                    section_end = element.get("endIndex", section_end or 0)
                    continue
                if in_section and _is_next_section_heading(style, section_level):
                    break
        if in_section:
            section_end = element.get("endIndex", section_end or 0)
    return section_end


def _section_level_from_header(raw_content: list, section_header: str) -> int:
    for element in raw_content:
        para = element.get("paragraph")
        if not para:
            continue
        style = para.get("paragraphStyle", {}).get("namedStyleType", "")
        text = extract_paragraph_text(para).strip()
        if text != section_header:
            continue
        if style == "HEADING_2":
            return 2
        return 1
    return 1


def _is_next_section_heading(style: str, section_level: int) -> bool:
    # For H1 sections, only the next H1 starts a new section.
    if section_level <= 1:
        return style == "HEADING_1"
    # For H2 sections, either H1 or H2 can start a new sibling/parent section.
    return style in ("HEADING_1", "HEADING_2")


def _section_heading_exists(raw_content: list, section_header: str) -> bool:
    for element in raw_content:
        para = element.get("paragraph")
        if not para:
            continue
        style = para.get("paragraphStyle", {}).get("namedStyleType", "")
        if style not in ("HEADING_1", "HEADING_2"):
            continue
        text = extract_paragraph_text(para).strip()
        if text == section_header:
            return True
    return False


def _ensure_section_heading_rename(
    token: str,
    document_id: str,
    raw_content: list,
    old_header: str,
    new_header: str,
    dry_run: bool,
) -> list:
    if old_header == new_header:
        return raw_content
    has_new = _section_heading_exists(raw_content, new_header)
    has_old = _section_heading_exists(raw_content, old_header)
    if has_new or not has_old:
        return raw_content
    if dry_run:
        print(f"[DRY RUN] Would rename section heading '{old_header}' -> '{new_header}'.")
        return raw_content
    docs_request(
        token,
        "POST",
        f"/documents/{document_id}:batchUpdate",
        payload={"requests": [{
            "replaceAllText": {
                "containsText": {"text": old_header, "matchCase": True},
                "replaceText": new_header,
            }
        }]},
    )
    _, refreshed = fetch_document(token, document_id)
    return refreshed


def _ensure_simple_section_exists(
    token: str,
    document_id: str,
    raw_content: list,
    section_header: str,
    dry_run: bool,
    tab_id: Optional[str] = None,
) -> list:
    if _section_heading_exists(raw_content, section_header):
        return raw_content
    if dry_run:
        print(f"[DRY RUN] Would append missing section heading '{section_header}'.")
        return raw_content
    doc_end = 1
    for el in raw_content:
        end_idx = el.get("endIndex")
        if isinstance(end_idx, int) and end_idx > doc_end:
            doc_end = end_idx
    insert_at = max(1, doc_end - 1)
    scaffold = f"\n{section_header}\n\n"
    docs_request(
        token,
        "POST",
        f"/documents/{document_id}:batchUpdate",
        payload={"requests": [
            {"insertText": {"location": _make_location(insert_at, tab_id=tab_id), "text": scaffold}},
            {"updateParagraphStyle": {
                "range": _make_range(insert_at + 1, insert_at + 1 + len(section_header), tab_id=tab_id),
                "paragraphStyle": {"namedStyleType": "HEADING_1"},
                "fields": "namedStyleType",
            }},
        ]},
    )
    refreshed_doc, _ = fetch_document(token, document_id)
    return _content_for_tab_id(refreshed_doc, tab_id)


def _ensure_account_metadata_guidance_layout(
    token: str,
    document_id: str,
    raw_content: list,
    dry_run: bool,
    tab_id: Optional[str] = None,
) -> list:
    if not _section_heading_exists(raw_content, ACCOUNT_METADATA_HEADER):
        return raw_content
    requests: list[dict] = []
    for label, about in _account_metadata_guidance_pairs():
        if not about:
            continue
        old_seq = f"{about}\n{label}"
        new_seq = f"{label}\n{about}"
        requests.append({
            "replaceAllText": {
                "containsText": {"text": old_seq, "matchCase": True},
                "replaceText": new_seq,
            }
        })
    if not requests:
        return raw_content
    if dry_run:
        print("[DRY RUN] Would normalize Account Metadata guidance ordering (label then About line).")
        return raw_content
    docs_request(
        token,
        "POST",
        f"/documents/{document_id}:batchUpdate",
        payload={"requests": requests},
    )
    refreshed_doc, _ = fetch_document(token, document_id)
    return _content_for_tab_id(refreshed_doc, tab_id)


def _style_account_metadata_guidance_text(
    token: str,
    document_id: str,
    raw_content: list,
    dry_run: bool,
    tab_id: Optional[str] = None,
) -> int:
    in_section = False
    section_level = _section_level_from_header(raw_content, ACCOUNT_METADATA_HEADER)
    reqs: list[dict] = []
    for element in raw_content:
        para = element.get("paragraph")
        if not para:
            continue
        style = para.get("paragraphStyle", {}).get("namedStyleType", "")
        text = extract_paragraph_text(para).strip()
        if style in ("HEADING_1", "HEADING_2"):
            if text == ACCOUNT_METADATA_HEADER:
                in_section = True
                continue
            if in_section and _is_next_section_heading(style, section_level):
                break
        if not in_section or not _is_guidance_line(text):
            continue
        s = element.get("startIndex")
        e = element.get("endIndex")
        if s is None or e is None or e <= s:
            continue
        reqs.append({
            "updateTextStyle": {
                "range": _make_range(s, e - 1, tab_id=tab_id),
                "textStyle": {"fontSize": {"magnitude": ACCOUNT_METADATA_GUIDANCE_FONT_PT, "unit": "PT"}},
                "fields": "fontSize",
            }
        })
    if not reqs:
        return 0
    if dry_run:
        print(f"[DRY RUN] Would compact {len(reqs)} Account Metadata guidance line(s) to {ACCOUNT_METADATA_GUIDANCE_FONT_PT}pt.")
        return len(reqs)
    docs_request(token, "POST", f"/documents/{document_id}:batchUpdate", payload={"requests": reqs})
    return len(reqs)


def _compact_challenge_tracker_text(
    token: str,
    document_id: str,
    dry_run: bool,
) -> int:
    doc = docs_request(token, "GET", f"/documents/{document_id}")
    content = doc.get("body", {}).get("content", [])
    table_start = _resolve_table_start_index(content, "Challenge Tracker", None)
    if table_start is None:
        return 0
    table_rows = _get_table_rows(content, table_start)
    reqs: list[dict] = []
    for row_idx, row in enumerate(table_rows):
        # Keep header row at normal/default size; compact data rows only.
        if row_idx == 0:
            continue
        for cell in row.get("tableCells", []):
            for s, e in _cell_text_ranges(cell):
                if e <= s:
                    continue
                reqs.append({
                    "updateTextStyle": {
                        "range": {"startIndex": s, "endIndex": e},
                        "textStyle": {"fontSize": {"magnitude": CHALLENGE_TRACKER_FONT_PT, "unit": "PT"}},
                        "fields": "fontSize",
                    }
                })
    if not reqs:
        return 0
    if dry_run:
        print(f"[DRY RUN] Would compact Challenge Tracker text to {CHALLENGE_TRACKER_FONT_PT}pt ({len(reqs)} range updates).")
        return len(reqs)
    docs_request(token, "POST", f"/documents/{document_id}:batchUpdate", payload={"requests": reqs})
    return len(reqs)


def _ensure_account_metadata_section(
    token: str,
    document_id: str,
    raw_content: list,
    dry_run: bool,
    tab_id: Optional[str] = None,
) -> list:
    has_new = _section_heading_exists(raw_content, ACCOUNT_METADATA_HEADER)
    if has_new:
        return raw_content

    if dry_run:
        print(f"[DRY RUN] Would append missing '{ACCOUNT_METADATA_HEADER}' section scaffold at document end.")
        return raw_content

    doc_end = 1
    for el in raw_content:
        end_idx = el.get("endIndex")
        if isinstance(end_idx, int) and end_idx > doc_end:
            doc_end = end_idx
    insert_at = max(1, doc_end - 1)
    scaffold = "\n" + _account_metadata_scaffold_text()
    docs_request(
        token,
        "POST",
        f"/documents/{document_id}:batchUpdate",
        payload={"requests": [
            {"insertText": {"location": _make_location(insert_at, tab_id=tab_id), "text": scaffold}},
            {"updateParagraphStyle": {
                "range": _make_range(insert_at + 1, insert_at + 1 + len(ACCOUNT_METADATA_HEADER), tab_id=tab_id),
                "paragraphStyle": {"namedStyleType": "HEADING_1"},
                "fields": "namedStyleType",
            }},
        ]},
    )
    refreshed_doc, _ = fetch_document(token, document_id)
    return _content_for_tab_id(refreshed_doc, tab_id)


def _field_label_exists(raw_content: list, section_header: str, field_label: str) -> bool:
    in_section = False
    for element in raw_content:
        if "paragraph" not in element:
            continue
        para = element["paragraph"]
        style = para.get("paragraphStyle", {}).get("namedStyleType", "")
        text = extract_paragraph_text(para).strip()
        if style in ("HEADING_1", "HEADING_2"):
            if text == section_header:
                in_section = True
                continue
            if in_section:
                return False
        if in_section and text == field_label:
            return True
    return False


def _diff_table(
    orig_sec: Optional[DocumentSection], upd_sec: DocumentSection,
    replace_reqs: list, pending_rows: list, pending_updates: list, pending_deletes: list, table_element: Optional[dict],
) -> None:
    orig_challenges = {r.challenge.lower(): r for r in (orig_sec.rows if orig_sec else [])}
    updated_keys = {r.challenge.lower() for r in upd_sec.rows}

    for row in upd_sec.rows:
        key = row.challenge.lower()
        if key in orig_challenges:
            orig = orig_challenges[key]
            if (orig.date != row.date or
                orig.status != row.status or
                orig.category != row.category or
                orig.notes_references != row.notes_references):
                pending_updates.append({
                    "section_header": upd_sec.header,
                    "table_start_index": table_element.get("startIndex") if table_element else None,
                    "tab_id": upd_sec.tab_id,
                    "challenge": row.challenge,
                    "date": row.date,
                    "category": row.category,
                    "status": row.status,
                    "notes_references": row.notes_references,
                })
        else:
            pending_rows.append({
                "section_key": upd_sec.key,
                "section_header": upd_sec.header,
                "table_start_index": table_element.get("startIndex") if table_element else None,
                "tab_id": upd_sec.tab_id,
                "new_row": asdict(row),
            })
    for orig_key, orig_row in orig_challenges.items():
        if orig_key not in updated_keys:
            pending_deletes.append({
                "section_header": upd_sec.header,
                "table_start_index": table_element.get("startIndex") if table_element else None,
                "tab_id": upd_sec.tab_id,
                "challenge": orig_row.challenge,
            })


def find_table_elements(raw_content_by_tab: dict[str, list], section_map: SectionMap, config: dict) -> dict:
    _header_to_key, _, _ = build_config_lookups(config)
    table_map: dict[str, dict] = {}
    for sec_key, sec in section_map.items():
        if sec.section_type != "table":
            continue
        content = raw_content_by_tab.get(sec.tab_id or "", [])
        current_key: Optional[str] = None
        for element in content:
            if "paragraph" in element:
                para = element["paragraph"]
                style = para.get("paragraphStyle", {}).get("namedStyleType", "")
                if style in ("HEADING_1", "HEADING_2"):
                    text = "".join(
                        e.get("textRun", {}).get("content", "") for e in para.get("elements", [])
                    ).strip()
                    current_key = sec_key if text == sec.header else None
            elif "table" in element and current_key == sec_key:
                table_map[sec_key] = element
                break
    return table_map


def write_to_doc(
    token: str, document_id: str,
    original: SectionMap, updated: SectionMap,
    raw_content: list, raw_content_by_tab: dict[str, list], table_elements: dict,
    dry_run: bool = False,
) -> int:
    regular_reqs, pending_rows, pending_updates, pending_deletes, pending_tool_deletes, pending_tool_updates, pending_entry_deletes = build_write_requests(
        original, updated, raw_content, raw_content_by_tab, table_elements)

    if not regular_reqs and not pending_rows and not pending_updates and not pending_deletes and not pending_tool_deletes and not pending_tool_updates and not pending_entry_deletes:
        print("No changes to write.")
        return 0

    if dry_run:
        print(f"[DRY RUN] {len(regular_reqs)} text requests, {len(pending_rows)} table row inserts, {len(pending_updates)} table row updates, {len(pending_deletes)} table row deletes, {len(pending_tool_deletes)} tool line deletes, {len(pending_tool_updates)} tool line updates, {len(pending_entry_deletes)} entry line deletes.")
        for r in regular_reqs:
            rtype = list(r.keys())[0]
            print(f"  {rtype}: {json.dumps(r)[:120]}")
        for p in pending_rows:
            print(f"  pendingTableRow: {json.dumps(p)[:120]}")
        for u in pending_updates:
            print(f"  pendingTableUpdate: {json.dumps(u)[:120]}")
        for d in pending_deletes:
            print(f"  pendingTableDelete: {json.dumps(d)[:120]}")
        for td in pending_tool_deletes:
            print(f"  pendingToolDelete: {json.dumps(td)[:120]}")
        for tu in pending_tool_updates:
            print(f"  pendingToolUpdate: {json.dumps(tu)[:120]}")
        for ed in pending_entry_deletes:
            print(f"  pendingEntryDelete: {json.dumps(ed)[:120]}")
        return 0

    total = 0

    if regular_reqs:
        docs_request(token, "POST", f"/documents/{document_id}:batchUpdate",
                     payload={"requests": regular_reqs})
        total += len(regular_reqs)

    for pending in pending_rows:
        _insert_table_row(token, document_id, pending)
        total += 1

    for pending in pending_updates:
        _update_table_row(token, document_id, pending)
        total += 1
    for pending in pending_deletes:
        _delete_table_row(token, document_id, pending)
        total += 1
    for pending in pending_tool_deletes:
        _delete_tool_line(token, document_id, pending)
        total += 1
    for pending in pending_tool_updates:
        _replace_tool_line(token, document_id, pending)
        total += 1
    for pending in pending_entry_deletes:
        _delete_entry_line(token, document_id, pending)
        total += 1

    return total


def _derive_customer_name_from_title(title: str) -> str:
    t = (title or "").strip()
    if t.endswith(" Notes"):
        return t[:-6].strip()
    return t or "Customer"


def _append_agent_run_log_markdown(
    notes_doc_id: str,
    notes_title: str,
    run_titles: list[str],
    applied: list[dict],
    skipped: list[dict],
    completeness_report: Optional[dict[str, str]],
    dry_run: bool,
    timestamp_format: str = DEFAULT_RUNLOG_TIMESTAMP_FORMAT,
    max_bytes: int = DEFAULT_RUNLOG_MAX_BYTES,
) -> None:
    if not run_titles:
        return

    customer = _derive_customer_name_from_title(notes_title)
    local_log_path = LOCAL_CUSTOMERS_BASE / customer / "pnotes_agent_log.md"
    gdrive_log_path = GDRIVE_CUSTOMERS_BASE / customer / "pnotes_agent_log.md"

    if dry_run:
        print(f"[DRY RUN] Would append {len(run_titles)} markdown run-log entries to {local_log_path} and {gdrive_log_path}.")
        return

    for run_title in reversed(run_titles):
        logged_at = datetime.now(timezone.utc).strftime(timestamp_format)
        block = _render_markdown_run_block(
            run_title=run_title,
            notes_doc_id=notes_doc_id,
            notes_title=notes_title,
            logged_at=logged_at,
            applied=applied,
            skipped=skipped,
            completeness_report=completeness_report,
        )
        _prepend_markdown_block(local_log_path, block)
        _enforce_runlog_rollover(local_log_path, max_bytes)
        if gdrive_log_path.parent.exists():
            _prepend_markdown_block(gdrive_log_path, block)
            _enforce_runlog_rollover(gdrive_log_path, max_bytes)
        else:
            print(
                f"WARNING: Skipping GDrive run-log write; customer folder not visible at {gdrive_log_path.parent}",
                file=sys.stderr,
            )


def _prepend_markdown_block(path: Path, block: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    header = "# pnotes_agent_log\n\n"
    if not existing.strip():
        path.write_text(header + block, encoding="utf-8")
        return
    if existing.startswith("# pnotes_agent_log"):
        rest = existing[len("# pnotes_agent_log"):].lstrip("\n")
        merged = header + block + ("\n" if not block.endswith("\n") else "") + rest
        path.write_text(merged, encoding="utf-8")
        return
    path.write_text(header + block + "\n" + existing, encoding="utf-8")


def _split_run_blocks(existing: str) -> tuple[str, list[str]]:
    header = "# pnotes_agent_log\n\n"
    text = existing
    if text.startswith(header):
        text = text[len(header):]
    text = text.lstrip("\n")
    starts = [m.start() for m in re.finditer(r"^## .*$", text, flags=re.MULTILINE)]
    if not starts:
        return header, []
    blocks: list[str] = []
    for idx, start in enumerate(starts):
        end = starts[idx + 1] if idx + 1 < len(starts) else len(text)
        block = text[start:end].strip("\n")
        if block:
            blocks.append(block + "\n\n")
    return header, blocks


def _compact_runlog_content(existing: str) -> str:
    # Remove bulky JSON snapshots to keep run log readable and compact.
    return re.sub(
        r"\n### Raw JSON Snapshot\n\n```json\n.*?\n```\n",
        "\n",
        existing,
        flags=re.DOTALL,
    )


def _prepend_blocks(path: Path, blocks: list[str]) -> None:
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    existing = _compact_runlog_content(existing)
    header, curr_blocks = _split_run_blocks(existing)
    merged_blocks = blocks + curr_blocks
    path.write_text(header + "".join(merged_blocks), encoding="utf-8")


def _enforce_runlog_rollover(path: Path, max_bytes: int) -> None:
    if max_bytes <= 0 or not path.exists():
        return
    existing = path.read_text(encoding="utf-8")
    compacted = _compact_runlog_content(existing)
    header, blocks = _split_run_blocks(compacted)
    if not blocks:
        path.write_text(compacted if compacted.startswith("# pnotes_agent_log") else (header + compacted), encoding="utf-8")
        return

    # Keep newest runs in the primary log, move oldest to archive.
    moved: list[str] = []
    while len((header + "".join(blocks)).encode("utf-8")) > max_bytes and len(blocks) > 1:
        moved.append(blocks.pop())  # oldest block

    path.write_text(header + "".join(blocks), encoding="utf-8")
    if moved:
        moved.reverse()  # newest of moved should appear first in archive
        archive_path = path.with_name("pnotes_agent_log.archive.md")
        _prepend_blocks(archive_path, moved)


def _change_kind(applied_item: dict) -> str:
    action = (applied_item.get("action") or "").strip()
    message = (applied_item.get("message") or "").lower()
    if action in {"append_with_history", "set_if_empty", "add_tool", "add_table_row"}:
        return "add"
    if action == "update_table_row" and "closed challenge removed" in message:
        return "delete"
    if action in {
        "remove_tool_suggestion",
        "auto_cleanup_contacts",
        "remove_bullet_after_promotion",
        "dedupe_with_table",
        "auto_dedupe_tool",
    }:
        return "delete"
    return "modify"


def _action_prefix(applied_item: dict) -> str:
    kind = _change_kind(applied_item)
    if kind == "add":
        return "+"
    if kind == "delete":
        return "-"
    return "~"


def _skip_reason_bucket(reason: str) -> str:
    r = (reason or "").lower()
    if "missing_evidence" in r or "evidence date" in r:
        return "missing_evidence"
    if "invalid action" in r or "strategy" in r:
        return "invalid_action_for_strategy"
    if "strict metadata field" in r or "requires explicit_statement" in r:
        return "blocked_by_policy"
    if "already current" in r or "already exists" in r or "semantically duplicate" in r:
        return "duplicate_or_noop"
    if "unknown section_key" in r or "unknown field_key" in r:
        return "schema_mismatch"
    return "other"


def _field_has_content(sec: DocumentSection, field_key: str) -> bool:
    fld = sec.fields.get(field_key)
    if not fld:
        return False
    if fld.update_strategy == "tools_list":
        return bool(fld.tools)
    return bool(_active_entries(fld))


def _compute_template_completeness_report(
    section_map: SectionMap,
    section_configs: dict[str, dict],
    applied: list[dict],
    skipped: list[dict],
) -> dict[str, str]:
    report: dict[str, str] = {}
    applied_targets = {
        f"{a.get('section_key')}.{a.get('field_key') or 'table'}"
        for a in applied
    }
    skipped_targets: dict[str, str] = {}
    for s in skipped:
        m = s.get("mutation") or {}
        sec_key = str(m.get("section_key") or "").strip()
        if not sec_key:
            continue
        target = f"{sec_key}.{m.get('field_key') or 'table'}"
        skipped_targets[target] = _skip_reason_bucket(str(s.get("reason") or ""))

    for sec_key, sec_cfg in section_configs.items():
        sec = section_map.get(sec_key)
        if not sec:
            continue
        if sec.section_type == "table":
            target = f"{sec_key}.table"
            if target in applied_targets:
                report[target] = "updated"
            elif target in skipped_targets:
                report[target] = f"blocked_by_policy:{skipped_targets[target]}"
            elif sec.rows:
                report[target] = "unchanged"
            else:
                report[target] = "missing_evidence"
            continue
        for f in sec_cfg.get("fields", []):
            fk = f["key"]
            target = f"{sec_key}.{fk}"
            if target in applied_targets:
                report[target] = "updated"
            elif target in skipped_targets:
                report[target] = f"blocked_by_policy:{skipped_targets[target]}"
            elif _field_has_content(sec, fk):
                report[target] = "unchanged"
            else:
                report[target] = "missing_evidence"
    return report


def _print_pre_skipped_section_summary(pre_skipped: list[dict]) -> None:
    if not pre_skipped:
        return
    buckets: dict[str, int] = {}
    for item in pre_skipped:
        m = item.get("mutation") or {}
        sec_key = str(m.get("section_key") or "unknown").strip() or "unknown"
        reason = str(item.get("reason") or "").lower()
        if "missing_evidence" in reason:
            reason_bucket = "missing_evidence"
        elif "duplicate" in reason:
            reason_bucket = "duplicate_or_noop"
        elif "blocked" in reason:
            reason_bucket = "blocked_by_policy"
        elif "invalid" in reason or "unknown" in reason:
            reason_bucket = "schema_or_action_error"
        else:
            reason_bucket = "other"
        key = f"{sec_key}:{reason_bucket}"
        buckets[key] = buckets.get(key, 0) + 1
    print("Pre-skip summary by section:")
    for key in sorted(buckets.keys()):
        print(f"  - {key} = {buckets[key]}")


def _render_markdown_run_block(
    run_title: str,
    notes_doc_id: str,
    notes_title: str,
    logged_at: str,
    applied: list[dict],
    skipped: list[dict],
    completeness_report: Optional[dict[str, str]] = None,
) -> str:
    action_counts: dict[str, int] = {}
    for a in applied:
        action = a.get("action", "unknown")
        action_counts[action] = action_counts.get(action, 0) + 1

    lines: list[str] = [
        f"## {run_title}",
        "",
        f"- Logged At (UTC): `{logged_at}`",
        f"- Notes Doc: `{notes_title}` (`{notes_doc_id}`)",
        f"- Applied mutations: `{len(applied)}`",
        f"- Skipped mutations: `{len(skipped)}`",
        "",
        "### Action Summary",
        "",
        "| Action | Count |",
        "|---|---:|",
    ]
    for action, count in sorted(action_counts.items()):
        lines.append(f"| `{action}` | {count} |")
    if not action_counts:
        lines.append("| `none` | 0 |")

    lines.extend(["", "### Changes", ""])

    for a in applied:
        prefix = _action_prefix(a)
        target = f"{a.get('section_key', '')}.{a.get('field_key') or 'table'}"
        msg = a.get("message", "")
        kind = _change_kind(a)
        lines.append(f"{prefix} `{target}` [{kind}] — {msg}")
        full_change = (a.get("full_change") or "").strip()
        if full_change:
            lines.append(f"    {prefix} change: {full_change}")
        e_date = (a.get("evidence_date") or "").strip()
        if e_date:
            lines.append(f"    {prefix} evidence_date: {e_date}")
        reason = (a.get("reasoning") or "").strip()
        if reason:
            lines.append(f"    {prefix} reason: {reason}")

    if skipped:
        lines.extend(["", "### Skipped", ""])
        for s in skipped:
            reason = s.get("reason", "")
            bucket = _skip_reason_bucket(reason)
            lines.append(f"~ skipped[{bucket}]: {reason}")
    if completeness_report:
        lines.extend(["", "### Template Completeness", ""])
        status_counts: dict[str, int] = {}
        for status in completeness_report.values():
            base = status.split(":", 1)[0]
            status_counts[base] = status_counts.get(base, 0) + 1
        for key in ("updated", "unchanged", "missing_evidence", "blocked_by_policy"):
            lines.append(f"- {key}: `{status_counts.get(key, 0)}`")
    ew = _derive_evidence_window(applied)
    lines.extend(["", f"- Evidence window: `{ew}`"])
    if applied:
        lines.append(f"- Ledger row appended: `{TODAY}` (UCN owns ledger writes)")
    lines.extend(["", "---", ""])
    return "\n".join(lines)


def _derive_evidence_window(applied: list[dict]) -> str:
    dates: list[str] = []
    for a in applied:
        ed = str(a.get("evidence_date") or "").strip()
        if re.match(r"^\d{4}-\d{2}-\d{2}$", ed):
            dates.append(ed)
            continue
        fc = str(a.get("full_change") or "").strip()
        if not fc:
            continue
        # Table-row full_change is stored as JSON string in many mutations.
        try:
            row = json.loads(fc)
            if isinstance(row, dict):
                d = str(row.get("date", "")).strip()
                if re.match(r"^\d{4}-\d{2}-\d{2}$", d):
                    dates.append(d)
        except Exception:
            pass
    if not dates:
        return "unknown"
    return f"{min(dates)} -> {max(dates)}"


def _insert_table_row(token: str, document_id: str, pending: dict) -> None:
    # Re-fetch and resolve table start index at execution time because prior
    # insertions can shift indices after the initial parse.
    tab_id = pending.get("tab_id")
    doc = docs_request(token, "GET", f"/documents/{document_id}", query={"includeTabsContent": "true"})
    content = _content_for_tab_id(doc, tab_id)
    section_header = pending.get("section_header")
    tsi = _resolve_table_start_index(content, section_header, pending.get("table_start_index"))
    if tsi is None:
        print("WARNING: Could not resolve table start index, skipping table row insert", file=sys.stderr)
        return

    table_el = _find_table_element_by_start(content, tsi)
    if not table_el:
        print("WARNING: Could not find resolved table element, skipping table row insert", file=sys.stderr)
        return

    row_count_before = len(table_el.get("table", {}).get("tableRows", []))
    # Header row is index 0. Append below last existing row.
    insert_below_row_index = max(row_count_before - 1, 0)

    docs_request(token, "POST", f"/documents/{document_id}:batchUpdate",
                 payload={"requests": [{"insertTableRow": {
                     "tableCellLocation": {
                        "tableStartLocation": _make_location(tsi, tab_id=tab_id),
                        "rowIndex": insert_below_row_index,
                        "columnIndex": 0,
                     },
                     "insertBelow": True,
                 }}]})

    doc = docs_request(token, "GET", f"/documents/{document_id}", query={"includeTabsContent": "true"})
    content = _content_for_tab_id(doc, tab_id)

    row_data = pending["new_row"]
    cell_texts = [
        row_data.get("challenge", ""), row_data.get("date", ""),
        row_data.get("category", ""), row_data.get("status", ""),
        row_data.get("notes_references", ""),
    ]

    # The inserted row is now the last row; target by concrete index for determinism.
    inserted_row_index = row_count_before
    cell_indices = _find_table_row_cell_indices(content, tsi, inserted_row_index)
    if not cell_indices:
        print("WARNING: Could not find cell indices after table row insert", file=sys.stderr)
        return

    insert_reqs = []
    for ci, ct in zip(reversed(cell_indices), reversed(cell_texts)):
        if ct:
            insert_reqs.append(_make_insert_text(ci, ct, tab_id=tab_id))
            # Ensure table cell text is plain (non-bold) even if inherited styles exist.
            insert_reqs.append({
                "updateTextStyle": {
                    "range": _make_range(ci, ci + len(ct), tab_id=tab_id),
                    "textStyle": {
                        "bold": False,
                        "fontSize": {"magnitude": CHALLENGE_TRACKER_FONT_PT, "unit": "PT"},
                    },
                    "fields": "bold,fontSize",
                }
            })

    if insert_reqs:
        docs_request(token, "POST", f"/documents/{document_id}:batchUpdate",
                     payload={"requests": insert_reqs})


def _resolve_table_start_index(
    content: list,
    section_header: Optional[str],
    fallback_table_start_index: Optional[int],
) -> Optional[int]:
    """Find table start index near a specific section header; fallback to known index/first table."""
    current_heading: Optional[str] = None
    for element in content:
        if "paragraph" in element:
            para = element["paragraph"]
            style = para.get("paragraphStyle", {}).get("namedStyleType", "")
            if style in ("HEADING_1", "HEADING_2"):
                current_heading = extract_paragraph_text(para).strip()
        elif "table" in element:
            if section_header and current_heading == section_header:
                return element.get("startIndex")

    if fallback_table_start_index is not None:
        for element in content:
            if "table" in element and element.get("startIndex") == fallback_table_start_index:
                return fallback_table_start_index

    for element in content:
        if "table" in element:
            return element.get("startIndex")

    return None


def _find_table_element_by_start(content: list, table_start: int) -> Optional[dict]:
    for element in content:
        if element.get("startIndex") == table_start and "table" in element:
            return element
    return None


def _find_table_row_cell_indices(content: list, table_start: int, row_index: int) -> list[int]:
    table_el = _find_table_element_by_start(content, table_start)
    if not table_el:
        return []
    rows = table_el.get("table", {}).get("tableRows", [])
    if row_index < 0 or row_index >= len(rows):
        return []
    target_row = rows[row_index]
    indices = []
    for cell in target_row.get("tableCells", []):
        cc = cell.get("content", [])
        if cc and "paragraph" in cc[0]:
            elems = cc[0]["paragraph"].get("elements", [])
            if elems:
                indices.append(elems[0].get("startIndex", 0))
    return indices


def _get_table_rows(content: list, table_start: int) -> list[dict]:
    table_el = _find_table_element_by_start(content, table_start)
    if not table_el:
        return []
    return table_el.get("table", {}).get("tableRows", [])


def _extract_cell_text(cell: dict) -> str:
    txt = []
    for ce in cell.get("content", []):
        if "paragraph" in ce:
            txt.append(extract_paragraph_text(ce["paragraph"]))
    return "".join(txt).strip()


def _find_row_index_by_challenge(content: list, table_start: int, challenge: str) -> Optional[int]:
    rows = _get_table_rows(content, table_start)
    for idx, row in enumerate(rows):
        if idx == 0:
            continue
        cells = row.get("tableCells", [])
        if not cells:
            continue
        if _extract_cell_text(cells[0]).strip().lower() == challenge.strip().lower():
            return idx
    return None


def _cell_text_range(cell: dict) -> Optional[tuple[int, int]]:
    # Use first paragraph first textRun span; trim trailing newline only when present.
    for ce in cell.get("content", []):
        para = ce.get("paragraph")
        if not para:
            continue
        for pe in para.get("elements", []):
            tr = pe.get("textRun")
            if not tr:
                continue
            s = pe.get("startIndex")
            e = pe.get("endIndex")
            if s is not None and e is not None and e > s:
                content = str(tr.get("content") or "")
                end = e - 1 if content.endswith("\n") and e - 1 > s else e
                return (s, end)
    return None


def _cell_text_ranges(cell: dict) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    for ce in cell.get("content", []):
        para = ce.get("paragraph")
        if not para:
            continue
        for pe in para.get("elements", []):
            tr = pe.get("textRun")
            if not tr:
                continue
            s = pe.get("startIndex")
            e = pe.get("endIndex")
            if s is None or e is None or e <= s:
                continue
            content = str(tr.get("content") or "")
            end = e - 1 if content.endswith("\n") and e - 1 > s else e
            ranges.append((s, end))
    return ranges


def _update_table_row(token: str, document_id: str, pending: dict) -> None:
    # Resolve table location and target row by challenge text.
    tab_id = pending.get("tab_id")
    doc = docs_request(token, "GET", f"/documents/{document_id}", query={"includeTabsContent": "true"})
    content = _content_for_tab_id(doc, tab_id)
    tsi = _resolve_table_start_index(content, pending.get("section_header"), pending.get("table_start_index"))
    if tsi is None:
        print("WARNING: Could not resolve table for row update", file=sys.stderr)
        return
    row_idx = _find_row_index_by_challenge(content, tsi, pending.get("challenge", ""))
    if row_idx is None:
        print("WARNING: Could not locate challenge row for table update", file=sys.stderr)
        return

    rows = _get_table_rows(content, tsi)
    if row_idx >= len(rows):
        return
    cells = rows[row_idx].get("tableCells", [])
    # challenge,date,category,status,notes (internal shared table shape)
    updates = {
        1: pending.get("date"),
        2: pending.get("category"),
        3: pending.get("status"),
        4: pending.get("notes_references"),
    }
    current_texts = [_extract_cell_text(c) for c in cells]
    while len(current_texts) < 5:
        current_texts.append("")
    final_texts = current_texts[:5]
    # Keep first key column unchanged (target row key).
    for col_idx, new_text in updates.items():
        if new_text is None:
            continue
        if col_idx < len(final_texts):
            final_texts[col_idx] = str(new_text)

    # Safer row-update strategy for Google Docs tables:
    # create replacement row, fill values, then delete original row.
    docs_request(
        token,
        "POST",
        f"/documents/{document_id}:batchUpdate",
        payload={"requests": [{"insertTableRow": {
            "tableCellLocation": {
                "tableStartLocation": _make_location(tsi, tab_id=tab_id),
                "rowIndex": row_idx,
                "columnIndex": 0,
            },
            "insertBelow": True,
        }}]},
    )

    doc = docs_request(token, "GET", f"/documents/{document_id}", query={"includeTabsContent": "true"})
    content = _content_for_tab_id(doc, tab_id)
    new_row_idx = row_idx + 1
    new_cell_indices = _find_table_row_cell_indices(content, tsi, new_row_idx)
    if not new_cell_indices:
        print("WARNING: Could not locate replacement row cells for table update", file=sys.stderr)
        return

    insert_reqs: list[dict] = []
    for ci, ct in zip(reversed(new_cell_indices), reversed(final_texts)):
        if not ct:
            continue
        insert_reqs.append(_make_insert_text(ci, ct, tab_id=tab_id))
        insert_reqs.append({
            "updateTextStyle": {
                "range": _make_range(ci, ci + len(ct), tab_id=tab_id),
                "textStyle": {
                    "bold": False,
                    "fontSize": {"magnitude": CHALLENGE_TRACKER_FONT_PT, "unit": "PT"},
                },
                "fields": "bold,fontSize",
            }
        })
    if insert_reqs:
        docs_request(token, "POST", f"/documents/{document_id}:batchUpdate", payload={"requests": insert_reqs})

    docs_request(
        token,
        "POST",
        f"/documents/{document_id}:batchUpdate",
        payload={"requests": [{
            "deleteTableRow": {
                "tableCellLocation": {
                    "tableStartLocation": _make_location(tsi, tab_id=tab_id),
                    "rowIndex": row_idx,
                    "columnIndex": 0,
                }
            }
        }]},
    )


def _delete_table_row(token: str, document_id: str, pending: dict) -> None:
    tab_id = pending.get("tab_id")
    doc = docs_request(token, "GET", f"/documents/{document_id}", query={"includeTabsContent": "true"})
    content = _content_for_tab_id(doc, tab_id)
    tsi = _resolve_table_start_index(content, pending.get("section_header"), pending.get("table_start_index"))
    if tsi is None:
        print("WARNING: Could not resolve table for row delete", file=sys.stderr)
        return
    row_idx = _find_row_index_by_challenge(content, tsi, pending.get("challenge", ""))
    if row_idx is None or row_idx <= 0:
        return
    reqs = [{
        "deleteTableRow": {
            "tableCellLocation": {
                "tableStartLocation": _make_location(tsi, tab_id=tab_id),
                "rowIndex": row_idx,
                "columnIndex": 0,
            }
        }
    }]
    docs_request(token, "POST", f"/documents/{document_id}:batchUpdate",
                 payload={"requests": reqs})


def _delete_tool_line(token: str, document_id: str, pending: dict) -> None:
    tab_id = pending.get("tab_id")
    doc = docs_request(token, "GET", f"/documents/{document_id}", query={"includeTabsContent": "true"})
    content = _content_for_tab_id(doc, tab_id)
    target = (pending.get("tool_line") or "").strip()
    if not target:
        return
    # Delete the first exact matching paragraph line to remove tool from active list.
    for el in content:
        para = el.get("paragraph")
        if not para:
            continue
        txt = extract_paragraph_text(para).strip()
        if txt != target:
            continue
        s = el.get("startIndex")
        e = el.get("endIndex")
        if s is None or e is None or e <= s:
            return
        reqs = [{"deleteContentRange": {"range": _make_range(s, e, tab_id=tab_id)}}]
        docs_request(token, "POST", f"/documents/{document_id}:batchUpdate",
                     payload={"requests": reqs})
        return


def _replace_tool_line(token: str, document_id: str, pending: dict) -> None:
    tab_id = pending.get("tab_id")
    doc = docs_request(token, "GET", f"/documents/{document_id}", query={"includeTabsContent": "true"})
    content = _content_for_tab_id(doc, tab_id)
    old_line = (pending.get("old_line") or "").strip()
    new_line = (pending.get("new_line") or "").strip()
    section_header = (pending.get("section_header") or "").strip()
    if not old_line or not new_line or old_line == new_line:
        return

    in_section = not bool(section_header)
    section_level = _section_level_from_header(content, section_header) if section_header else 1
    for el in content:
        para = el.get("paragraph")
        if not para:
            continue
        style = para.get("paragraphStyle", {}).get("namedStyleType", "")
        txt = extract_paragraph_text(para).strip()

        if section_header and style in ("HEADING_1", "HEADING_2"):
            if txt == section_header:
                in_section = True
                continue
            if in_section and _is_next_section_heading(style, section_level):
                break
        if not in_section:
            continue
        if txt != old_line:
            continue

        s = el.get("startIndex")
        e = el.get("endIndex")
        if s is None or e is None or e <= s:
            return
        reqs = [
            {"deleteContentRange": {"range": _make_range(s, e, tab_id=tab_id)}},
            {"insertText": {"location": _make_location(s, tab_id=tab_id), "text": new_line + "\n"}},
        ]
        docs_request(token, "POST", f"/documents/{document_id}:batchUpdate",
                     payload={"requests": reqs})
        return


def _delete_entry_line(token: str, document_id: str, pending: dict) -> None:
    tab_id = pending.get("tab_id")
    doc = docs_request(token, "GET", f"/documents/{document_id}", query={"includeTabsContent": "true"})
    content = _content_for_tab_id(doc, tab_id)
    target = (pending.get("entry_line") or "").strip()
    section_header = (pending.get("section_header") or "").strip()
    if not target:
        return

    in_section = not bool(section_header)
    section_level = _section_level_from_header(content, section_header) if section_header else 1
    for el in content:
        para = el.get("paragraph")
        if not para:
            continue
        style = para.get("paragraphStyle", {}).get("namedStyleType", "")
        txt = extract_paragraph_text(para).strip()

        if section_header and style in ("HEADING_1", "HEADING_2"):
            if txt == section_header:
                in_section = True
                continue
            if in_section and _is_next_section_heading(style, section_level):
                break
        if not in_section:
            continue
        # Doc paragraphs often include [YYYY-MM-DD] (or REVIEW/SUPERSEDED) while delete targets
        # use logical text from format_entry_for_doc (value only). Match on parsed value.
        canon = (parse_entry_text(txt).value or "").strip()
        if canon != target.strip():
            continue

        s = el.get("startIndex")
        e = el.get("endIndex")
        if s is None or e is None or e <= s:
            return
        reqs = [{"deleteContentRange": {"range": _make_range(s, e, tab_id=tab_id)}}]
        docs_request(token, "POST", f"/documents/{document_id}:batchUpdate",
                     payload={"requests": reqs})
        return


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cmd_discover(args: argparse.Namespace) -> int:
    token = get_access_token()
    if args.auth_check_only:
        print("[OK] Auth verified.")
        return 0
    doc_id = discover_customer_doc(token, args.root_folder_id, args.customer)
    print(json.dumps({"customer": args.customer, "doc_id": doc_id}))
    return 0


def cmd_read(args: argparse.Namespace) -> int:
    token = get_access_token()
    config = load_config(args.config)
    doc, summary_content = fetch_document(token, args.doc_id)
    summary_tab_content, summary_tab_id = _content_for_tab_title(doc, ACCOUNT_SUMMARY_TAB_TITLE)
    if not summary_tab_content:
        summary_tab_content = summary_content
    metadata_content, metadata_tab_id = _content_for_tab_title(doc, ACCOUNT_METADATA_TAB_TITLE)
    dal_tab_content, dal_tab_id = _content_for_tab_title_strict(doc, DAILY_ACTIVITY_LOGS_TAB_TITLE)
    summary_map = parse_document(summary_tab_content, config)
    metadata_map = parse_document(metadata_content, config) if metadata_content else None
    section_map = _merge_tab_section_maps(summary_map, summary_tab_id, metadata_map, metadata_tab_id)
    if dal_tab_content is not None and dal_tab_id is not None:
        _merge_daily_activity_logs_from_dedicated_tab(
            section_map, dal_tab_content, dal_tab_id, config
        )

    output: dict[str, Any] = {
        "doc_id": args.doc_id,
        "title": doc.get("title", ""),
        "section_map": section_map_to_dict(section_map),
    }

    if args.include_internal:
        output["_internal"] = section_map_to_internal_dict(section_map)

    print(json.dumps(output, indent=2))
    return 0


def _run_lifecycle_tracker_parity_gate(customer_name: str, section_map: SectionMap) -> None:
    """Warn or raise if challenge-lifecycle.json is out of sync with Challenge Tracker rows."""
    repo_root = Path(os.environ.get("PRESTONOTES_REPO_ROOT", "")).resolve()
    if not os.environ.get("PRESTONOTES_REPO_ROOT"):
        repo_root = Path.cwd().resolve()
    parity_path = Path(__file__).resolve().parent / "challenge_lifecycle_parity.py"
    spec = importlib.util.spec_from_file_location("_pn_parity", parity_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load parity module from {parity_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    sec_tr = section_map.get("challenge_tracker")
    rows = list(sec_tr.rows) if sec_tr and sec_tr.rows else []
    warns, errs = mod.check_tracker_lifecycle_parity(repo_root, customer_name, rows)
    for w in warns:
        print(w, file=sys.stderr)
    if errs:
        raise RuntimeError(
            "\n".join(errs)
            + "\n\nFix: include matching [lifecycle_id:<id>] anchors in Challenge Tracker text "
            "(challenge cell and/or Notes & References) for every id in challenge-lifecycle.json, "
            "or pass --skip-lifecycle-parity-check for an emergency write."
        )


def cmd_write(args: argparse.Namespace) -> int:
    token = get_access_token()
    config = load_config(args.config)
    _, section_configs, field_strategies = build_config_lookups(config)

    mutations_path = Path(args.mutations)
    if not mutations_path.exists():
        raise FileNotFoundError(f"Mutations file not found: {args.mutations}")
    mutations_data = json.loads(mutations_path.read_text(encoding="utf-8"))
    mutation_list_all = mutations_data.get("mutations", mutations_data) \
        if isinstance(mutations_data, dict) else mutations_data
    runlog_mutations = [
        m for m in mutation_list_all
        if m.get("section_key") == "appendix"
        and m.get("field_key") == "agent_run_log"
        and m.get("action") == "append_with_history"
    ]
    mutation_list = [
        m for m in mutation_list_all
        if m not in runlog_mutations
    ]
    max_evidence_date: Optional[date] = None
    if args.max_evidence_date:
        try:
            max_evidence_date = datetime.strptime(args.max_evidence_date, "%Y-%m-%d").date()
        except ValueError as exc:
            raise RuntimeError("--max-evidence-date must be YYYY-MM-DD") from exc

    doc, content = fetch_document(token, args.doc_id)
    summary_content, summary_tab_id = _content_for_tab_title(doc, ACCOUNT_SUMMARY_TAB_TITLE)
    metadata_content, metadata_tab_id = _content_for_tab_title(doc, ACCOUNT_METADATA_TAB_TITLE)
    if not summary_content:
        summary_content = content
    if not metadata_content:
        metadata_content = summary_content
        metadata_tab_id = summary_tab_id

    needs_dal_tab = any(
        (m.get("action") or "") == "prepend_daily_activity_ai_summary" for m in mutation_list
    )
    dal_tab_content, dal_tab_id = _content_for_tab_title_strict(doc, DAILY_ACTIVITY_LOGS_TAB_TITLE)

    metadata_content = _ensure_account_metadata_section(
        token,
        args.doc_id,
        metadata_content,
        dry_run=args.dry_run,
        tab_id=metadata_tab_id,
    )
    metadata_content = _ensure_account_metadata_guidance_layout(
        token,
        args.doc_id,
        metadata_content,
        dry_run=args.dry_run,
        tab_id=metadata_tab_id,
    )
    content = _ensure_simple_section_exists(
        token,
        args.doc_id,
        summary_content,
        USE_CASES_HEADER,
        dry_run=args.dry_run,
        tab_id=summary_tab_id,
    )
    content = _ensure_simple_section_exists(
        token,
        args.doc_id,
        content,
        WORKFLOWS_HEADER,
        dry_run=args.dry_run,
        tab_id=summary_tab_id,
    )
    metadata_content = _ensure_simple_section_exists(
        token,
        args.doc_id,
        metadata_content,
        "Deal Stage Tracker",
        dry_run=args.dry_run,
        tab_id=metadata_tab_id,
    )
    content = _ensure_simple_section_exists(
        token,
        args.doc_id,
        content,
        ACCOMPLISHMENTS_HEADER,
        dry_run=args.dry_run,
        tab_id=summary_tab_id,
    )
    dal_tab_body_for_raw: Optional[list] = None
    dal_tab_id_for_raw: Optional[str] = None
    if dal_tab_id and dal_tab_content is not None:
        dal_tab_content = _ensure_simple_section_exists(
            token,
            args.doc_id,
            dal_tab_content,
            DAILY_ACTIVITY_LOGS_TAB_TITLE,
            dry_run=args.dry_run,
            tab_id=dal_tab_id,
        )
        dal_tab_body_for_raw = dal_tab_content
        dal_tab_id_for_raw = dal_tab_id
    elif needs_dal_tab:
        raise RuntimeError(
            "prepend_daily_activity_ai_summary requires a Google Doc tab titled exactly "
            f"{DAILY_ACTIVITY_LOGS_TAB_TITLE!r}. "
            f"Found tab titles: {_doc_tab_titles(doc) or ['(none — legacy single-tab doc?)']}"
        )
    else:
        content = _ensure_simple_section_exists(
            token,
            args.doc_id,
            content,
            DAILY_ACTIVITY_LOGS_TAB_TITLE,
            dry_run=args.dry_run,
            tab_id=summary_tab_id,
        )
    _style_account_metadata_guidance_text(
        token, args.doc_id, metadata_content, dry_run=args.dry_run, tab_id=metadata_tab_id
    )
    summary_map = parse_document(content, config)
    metadata_map = parse_document(metadata_content, config)
    section_map = _merge_tab_section_maps(summary_map, summary_tab_id, metadata_map, metadata_tab_id)
    if dal_tab_body_for_raw is not None and dal_tab_id_for_raw is not None:
        _merge_daily_activity_logs_from_dedicated_tab(
            section_map, dal_tab_body_for_raw, dal_tab_id_for_raw, config
        )
    original = copy.deepcopy(section_map)
    raw_content_by_tab: dict[str, list] = {
        (summary_tab_id or ""): content,
        (metadata_tab_id or ""): metadata_content,
    }
    if dal_tab_body_for_raw is not None and dal_tab_id_for_raw is not None:
        raw_content_by_tab[dal_tab_id_for_raw] = dal_tab_body_for_raw
    table_elements = find_table_elements(raw_content_by_tab, section_map, config)
    _dal_only = bool(mutation_list) and all(
        (m.get("action") or "") == "prepend_daily_activity_ai_summary" for m in mutation_list
    )
    if not _dal_only:
        covered_key_fields = _key_field_coverage_set(mutation_list)
        missing_key_fields = sorted(KEY_FIELD_COVERAGE_REQUIREMENTS - covered_key_fields)
        if missing_key_fields:
            missing_txt = ", ".join(f"{s}.{f}" for s, f in missing_key_fields)
            raise RuntimeError(
                "Planner coverage guard failed. Provide either a mutating action or "
                f"action='no_evidence' for required fields: {missing_txt}"
            )

    mutation_list, pre_skipped, auto_generated = _prepare_mutations_for_write(
        section_map,
        mutation_list,
        field_strategies,
        max_evidence_date=max_evidence_date,
    )
    applied, skipped = apply_mutations(section_map, mutation_list)
    skipped = pre_skipped + skipped
    applied.extend(_reconcile_challenges_with_tracker(section_map))
    applied.extend(_auto_cleanup_contacts(section_map))
    applied.extend(_cleanup_generic_tool_details(section_map))
    applied.extend(_auto_cleanup_tool_display_and_dedupe(section_map))
    applied.extend(_auto_populate_account_metadata(section_map))
    completeness_report = _compute_template_completeness_report(
        section_map, section_configs, applied, skipped
    )
    run_titles = [str(m.get("new_value", "")).strip() for m in runlog_mutations if str(m.get("new_value", "")).strip()]

    if getattr(args, "customer_name", None) and not getattr(args, "skip_lifecycle_parity_check", False):
        _run_lifecycle_tracker_parity_gate(args.customer_name, section_map)

    print(f"Mutations: {len(applied)} applied, {len(skipped)} skipped")
    if auto_generated:
        print(f"  + [auto] Added {len(auto_generated)} policy-generated mutation(s)")
    for a in applied:
        print(f"  + [{a['action']}] {a['section_key']}.{a.get('field_key', 'table')}: {a['message']}")
    for s in skipped:
        print(f"  - Skipped: {s.get('reason', '')}")
    _print_pre_skipped_section_summary(pre_skipped)
    counts: dict[str, int] = {}
    for status in completeness_report.values():
        base = status.split(":", 1)[0]
        counts[base] = counts.get(base, 0) + 1
    print(
        "Template completeness: "
        f"updated={counts.get('updated', 0)}, "
        f"unchanged={counts.get('unchanged', 0)}, "
        f"missing_evidence={counts.get('missing_evidence', 0)}, "
        f"blocked_by_policy={counts.get('blocked_by_policy', 0)}"
    )

    if not applied:
        compact_only_reqs = _compact_challenge_tracker_text(
            token,
            args.doc_id,
            dry_run=args.dry_run,
        )
        if compact_only_reqs:
            print(f"{'[DRY RUN] Would execute' if args.dry_run else 'Executed'} {compact_only_reqs} compact Challenge Tracker style request(s).")
        if run_titles:
            _append_agent_run_log_markdown(
                notes_doc_id=args.doc_id,
                notes_title=doc.get("title", ""),
                run_titles=run_titles,
                applied=applied,
                skipped=skipped,
                completeness_report=completeness_report,
                dry_run=args.dry_run,
                timestamp_format=args.runlog_timestamp_format,
                max_bytes=args.runlog_max_bytes,
            )
            print("No notes changes applied. External run-log entry appended.")
            return 0
        if compact_only_reqs:
            print("No notes content changes applied.")
            return 0
        print("No changes to apply.")
        return 0

    req_count = write_to_doc(
        token, args.doc_id, original, section_map,
        content, raw_content_by_tab, table_elements, dry_run=args.dry_run,
    )
    compact_reqs = _compact_challenge_tracker_text(
        token,
        args.doc_id,
        dry_run=args.dry_run,
    )
    _append_agent_run_log_markdown(
        notes_doc_id=args.doc_id,
        notes_title=doc.get("title", ""),
        run_titles=run_titles,
        applied=applied,
        skipped=skipped,
        completeness_report=completeness_report,
        dry_run=args.dry_run,
        timestamp_format=args.runlog_timestamp_format,
        max_bytes=args.runlog_max_bytes,
    )
    total_reqs = req_count + compact_reqs
    print(f"{'[DRY RUN] Would execute' if args.dry_run else 'Executed'} {total_reqs} API requests.")
    return 0


# ---------------------------------------------------------------------------
# Ledger append
# ---------------------------------------------------------------------------

LEDGER_REQUIRED_COLUMNS = [
    "Date", "Account Health", "Wiz Score", "Sentiment", "Coverage",
    "Open Challenges", "Aging Blockers", "Resolved Issues", "New Blockers",
    "Goals Changed", "Tools Changed", "Stakeholder Shifts", "Value Realized",
    "Next Critical Event", "Key Drivers", "Wiz Licensed Products",
    "Wiz License Purchase Dates", "Wiz License Expiration/Renewal",
    "Wiz License Evidence Quality",
]

LEDGER_YAML_TEMPLATE = """---
customer_name: {customer}
last_ai_update: {date}
ledger_version: 1
schema_version: 2
---

# {customer} — History Ledger

## Standard ledger row (required columns — core rules)

Append-only. One row per run; **do not edit prior rows**.

"""


def _build_ledger_row_from_doc(
    section_map: SectionMap,
    applied: list[dict],
    extra_columns: Optional[dict[str, str]] = None,
) -> dict[str, str]:
    """Build a ledger row dict from post-write doc state + applied mutations."""
    row: dict[str, str] = {col: "" for col in LEDGER_REQUIRED_COLUMNS}
    row["Date"] = TODAY

    tracker = section_map.get("challenge_tracker")
    if tracker and tracker.section_type == "table":
        open_count = sum(
            1 for r in tracker.rows
            if r.status.strip() in ("Open", "In Progress")
        )
        aging = []
        for r in tracker.rows:
            if r.status.strip() not in ("Open",):
                continue
            try:
                d = date.fromisoformat(r.date.strip())
                age = (date.today() - d).days
                if age > 30:
                    aging.append(f"{r.challenge.strip()[:40]} ({age}d)")
            except (ValueError, AttributeError):
                pass
        row["Open Challenges"] = str(open_count) if open_count else ""
        row["Aging Blockers"] = "; ".join(aging) if aging else ""

    resolved_this_run = [
        a for a in applied
        if a.get("section_key") == "challenge_tracker"
        and a.get("action") == "update_table_row"
        and "Resolved" in str(a.get("row", {}).get("status", ""))
    ]
    if resolved_this_run:
        row["Resolved Issues"] = "; ".join(
            str(a.get("target_value", ""))[:50] for a in resolved_this_run
        )

    new_this_run = [
        a for a in applied
        if a.get("section_key") == "challenge_tracker"
        and a.get("action") == "add_table_row"
    ]
    if new_this_run:
        row["New Blockers"] = "; ".join(
            str(a.get("row", {}).get("challenge", ""))[:50] for a in new_this_run
        )

    goal_changes = [
        a for a in applied
        if a.get("section_key") == "exec_account_summary"
        and a.get("field_key") == "top_goal"
    ]
    if goal_changes:
        row["Goals Changed"] = "; ".join(
            f"+{a.get('action', '')}:{str(a.get('new_value', ''))[:40]}" for a in goal_changes
        )

    tool_changes = [
        a for a in applied
        if a.get("section_key") == "cloud_environment"
    ]
    if tool_changes:
        row["Tools Changed"] = "; ".join(
            f"{a.get('action', '')}:{a.get('tool_key', a.get('field_key', ''))}"[:40]
            for a in tool_changes
        )

    stage_tracker = section_map.get("deal_stage_tracker")
    if stage_tracker and stage_tracker.section_type == "table":
        won = [r for r in stage_tracker.rows if r.date.strip().lower() in ("win", "tech win")]
        if won:
            row["Wiz Licensed Products"] = ", ".join(
                r.challenge.strip() for r in won
            )

    if extra_columns:
        for k, v in extra_columns.items():
            if k in row:
                row[k] = v

    return row


def _format_ledger_table_row(row: dict[str, str]) -> str:
    """Format a row dict as a markdown pipe-delimited row."""
    return "| " + " | ".join(row.get(col, "") for col in LEDGER_REQUIRED_COLUMNS) + " |"


def _format_ledger_header() -> str:
    """Format the standard ledger column headers."""
    header = "| " + " | ".join(LEDGER_REQUIRED_COLUMNS) + " |"
    sep = "| " + " | ".join(":---" for _ in LEDGER_REQUIRED_COLUMNS) + " |"
    return header + "\n" + sep


def cmd_ledger_append(args: argparse.Namespace) -> int:
    """Append one ledger row after a successful write."""
    customer = args.customer
    ledger_local = LOCAL_CUSTOMERS_BASE / customer / "AI_Insights" / f"{customer}-History-Ledger.md"
    ledger_gdrive = GDRIVE_CUSTOMERS_BASE / customer / "AI_Insights" / f"{customer}-History-Ledger.md"

    extra: dict[str, str] = {}
    if args.extra_columns:
        try:
            extra = json.loads(args.extra_columns)
        except json.JSONDecodeError:
            print("WARNING: --extra-columns is not valid JSON; ignoring.", file=sys.stderr)

    section_map: Optional[SectionMap] = None
    applied: list[dict] = []

    if args.doc_id and args.config:
        try:
            token = get_access_token()
            config = load_config(args.config)
            doc, summary_content = fetch_document(token, args.doc_id)
            summary_tab_content, summary_tab_id = _content_for_tab_title(doc, ACCOUNT_SUMMARY_TAB_TITLE)
            if not summary_tab_content:
                summary_tab_content = summary_content
            metadata_content, metadata_tab_id = _content_for_tab_title(doc, ACCOUNT_METADATA_TAB_TITLE)
            dal_tab_content, dal_tab_id = _content_for_tab_title_strict(doc, DAILY_ACTIVITY_LOGS_TAB_TITLE)
            summary_map = parse_document(summary_tab_content, config)
            metadata_map = (
                parse_document(metadata_content, config) if metadata_content else None
            )
            section_map = _merge_tab_section_maps(
                summary_map, summary_tab_id, metadata_map, metadata_tab_id
            )
            if dal_tab_content is not None and dal_tab_id is not None:
                _merge_daily_activity_logs_from_dedicated_tab(
                    section_map, dal_tab_content, dal_tab_id, config
                )
        except Exception as exc:
            print(f"WARNING: Could not read doc for ledger context: {exc}", file=sys.stderr)

    if args.applied_json:
        try:
            applied = json.loads(Path(args.applied_json).read_text(encoding="utf-8"))
            if not isinstance(applied, list):
                applied = []
        except Exception:
            pass

    if section_map is None:
        section_map = {}

    row = _build_ledger_row_from_doc(section_map, applied, extra)

    if args.dry_run:
        print(f"[DRY RUN] Would append ledger row to {ledger_local}")
        print(_format_ledger_table_row(row))
        return 0

    # Validate row has all required columns.
    missing = [c for c in LEDGER_REQUIRED_COLUMNS if c not in row]
    if missing:
        print(f"ERROR: Ledger row missing columns: {missing}", file=sys.stderr)
        return 1

    ledger_local.parent.mkdir(parents=True, exist_ok=True)

    if not ledger_local.exists():
        content = LEDGER_YAML_TEMPLATE.format(customer=customer, date=TODAY)
        content += _format_ledger_header() + "\n"
        content += _format_ledger_table_row(row) + "\n"
        ledger_local.write_text(content, encoding="utf-8")
        print(f"Created new ledger with first row: {ledger_local}")
    else:
        existing = ledger_local.read_text(encoding="utf-8")
        existing = re.sub(
            r"^last_ai_update:\s*.*$",
            f"last_ai_update: {TODAY}",
            existing,
            count=1,
            flags=re.MULTILINE,
        )
        if not existing.endswith("\n"):
            existing += "\n"
        existing += _format_ledger_table_row(row) + "\n"
        ledger_local.write_text(existing, encoding="utf-8")
        print(f"Appended ledger row: {ledger_local}")

    if ledger_gdrive.parent.exists():
        import shutil
        shutil.copy2(str(ledger_local), str(ledger_gdrive))
        print(f"Mirrored ledger to Google Drive: {ledger_gdrive}")
    else:
        print(f"WARNING: GDrive AI_Insights folder not found at {ledger_gdrive.parent}", file=sys.stderr)

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read and update customer notes Google Docs.")
    sub = parser.add_subparsers(dest="command", required=True)

    # discover
    p_disc = sub.add_parser("discover", help="Find customer notes Google Doc ID")
    p_disc.add_argument("--customer", required=True, help="Customer name")
    p_disc.add_argument("--root-folder-id", required=True,
                        help="Google Drive ID of MyNotes root folder")
    p_disc.add_argument("--auth-check-only", action="store_true",
                        help="Only verify auth, do not discover")

    # read
    p_read = sub.add_parser("read", help="Read and parse a customer notes Google Doc")
    p_read.add_argument("--doc-id", required=True, help="Google Doc ID")
    p_read.add_argument("--config", required=True,
                        help="Path to customer notes schema YAML/JSON")
    p_read.add_argument("--include-internal", action="store_true",
                        help="Include internal document indices in output")

    # write
    p_write = sub.add_parser("write", help="Apply mutations to a customer notes Google Doc")
    p_write.add_argument("--doc-id", required=True, help="Google Doc ID")
    p_write.add_argument("--config", required=True,
                         help="Path to customer notes schema YAML/JSON")
    p_write.add_argument("--mutations", required=True,
                         help="Path to mutations JSON file")
    p_write.add_argument("--dry-run", action="store_true",
                         help="Print planned changes without writing")
    p_write.add_argument(
        "--runlog-timestamp-format",
        default=DEFAULT_RUNLOG_TIMESTAMP_FORMAT,
        help=(
            "strftime format for audit log timestamps "
            "(default: '%(default)s', example with milliseconds: '%%Y-%%m-%%d %%H:%%M:%%S.%%fZ')"
        ),
    )
    p_write.add_argument(
        "--runlog-max-bytes",
        type=int,
        default=DEFAULT_RUNLOG_MAX_BYTES,
        help="Maximum primary markdown run-log size before rollover to archive (default: %(default)s bytes, 50KB).",
    )
    p_write.add_argument(
        "--max-evidence-date",
        default=None,
        help="Optional evidence cutoff date (YYYY-MM-DD). Mutations with newer evidence dates are skipped.",
    )
    p_write.add_argument(
        "--customer-name",
        default=None,
        help=(
            "Customer folder name (e.g. _TEST_CUSTOMER). When set, runs challenge-lifecycle.json vs "
            "Challenge Tracker parity checks (see docs/ai/references/customer-notes-mutation-rules.md)."
        ),
    )
    p_write.add_argument(
        "--skip-lifecycle-parity-check",
        action="store_true",
        help="Disable lifecycle ↔ Challenge Tracker parity checks for this write.",
    )

    # ledger-append
    p_ledger = sub.add_parser("ledger-append", help="Append one row to a customer's History Ledger")
    p_ledger.add_argument("--customer", required=True, help="Customer name")
    p_ledger.add_argument("--doc-id", default="", help="Google Doc ID (for reading post-write state)")
    p_ledger.add_argument("--config", default="custom-notes-agent/config/doc-schema.yaml",
                          help="Path to doc schema YAML")
    p_ledger.add_argument("--applied-json", default="",
                          help="Path to JSON file with list of applied mutation dicts")
    p_ledger.add_argument("--extra-columns", default="",
                          help="JSON string of extra column values to merge (e.g. Sentiment, Key Drivers)")
    p_ledger.add_argument("--dry-run", action="store_true", help="Print row without writing")

    args = parser.parse_args()

    if args.command == "discover":
        return cmd_discover(args)
    elif args.command == "read":
        return cmd_read(args)
    elif args.command == "write":
        return cmd_write(args)
    elif args.command == "ledger-append":
        return cmd_ledger_append(args)
    return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        cmd = " ".join(AUTH_LOGIN_CMD)
        print(f"\nAuth quick-fix:\n  {cmd}\nThen rerun.", file=sys.stderr)
        raise SystemExit(1)

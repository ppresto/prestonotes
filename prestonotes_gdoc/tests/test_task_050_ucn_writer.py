"""TASK-050 unit tests for the UCN GDoc writer.

Covers the three code-satisfiable acceptance bullets (constraint #5 / bullet 8
in the delegation packet):
    * Timestamp emission on ``append_with_history`` fields (§A / D1).
    * Lifecycle-authoritative Challenge Tracker reconciliation (§B / D2).
    * One ``appendix.agent_run_log`` entry per successful UCN run (§F / D6+D7).

Bullet 4 (Deal Stage Tracker motion capture, §E / D5) is exercised here too —
the task's per-run "defend" / "code" acceptance is runtime-deferred, but the
writer's own promotion logic is unit-testable and tested below.

Tests are deterministic: no network / GDoc API calls. The writer module is
loaded once via ``pn_gdoc_writer`` (see ``conftest.py``).
"""

from __future__ import annotations

from datetime import date


# ---------------------------------------------------------------------------
# §A (D1) — append_with_history timestamp emission
# ---------------------------------------------------------------------------


def test_append_with_history_entry_rendered_with_trailing_iso_date(pn_gdoc_writer):
    w = pn_gdoc_writer
    new_entry = w.Entry(value="Defend routing guidance unlocked", timestamp="2026-04-21")
    pre_existing = w.Entry(value="Legacy risk with no timestamp", timestamp=None)

    line_new = w._format_entry_line_for_section("exec_account_summary", "risk", new_entry)
    line_old = w._format_entry_line_for_section("exec_account_summary", "risk", pre_existing)

    # Roundtrip guarantee: new entry must carry "[YYYY-MM-DD]" suffix so a
    # subsequent `read` parses back with timestamp populated.
    assert line_new.endswith(" [2026-04-21]")
    parsed_back = w.parse_entry_text(line_new)
    assert parsed_back.timestamp == "2026-04-21"

    # Append-only contract: pre-existing null-timestamp entries stay as-is.
    assert "[20" not in line_old
    assert line_old == "Legacy risk with no timestamp"


def test_non_append_with_history_field_is_not_suffixed(pn_gdoc_writer):
    w = pn_gdoc_writer
    entry = w.Entry(value="AWS us-east-1", timestamp=w.TODAY)

    line = w._format_entry_line_for_section("cloud_environment", "csp_regions", entry)

    # csp_regions is `tools_list`-ish / single-value; must not decorate with
    # a trailing ISO date (user-facing cell stays clean).
    assert "[20" not in line
    assert line == "AWS us-east-1"


def test_appendix_agent_run_log_renders_with_timestamp_suffix(pn_gdoc_writer):
    w = pn_gdoc_writer
    entry = w.Entry(value="run_date=2026-04-21; sections_touched=foo", timestamp="2026-04-21")

    line = w._format_entry_line_for_section("appendix", "agent_run_log", entry)

    assert line.endswith(" [2026-04-21]")


def test_format_entry_does_not_double_stamp_when_value_already_ends_in_date(pn_gdoc_writer):
    w = pn_gdoc_writer
    # Edge case: raw value already includes a trailing ISO date; the formatter
    # must not append a second one (keeps doc text stable across re-runs).
    entry = w.Entry(
        value="Splunk renewal risk [2026-04-18]",
        timestamp="2026-04-21",
    )

    line = w._format_entry_line_for_section("exec_account_summary", "risk", entry)

    # Exactly one trailing date token in the rendered line.
    assert line.count("[2026-") == 1
    assert line.endswith("[2026-04-18]")


# ---------------------------------------------------------------------------
# §B (D2) — Lifecycle-authoritative reconciliation
# ---------------------------------------------------------------------------


def _make_section_map_with_tracker(w, rows):
    tracker = w.DocumentSection(
        key="challenge_tracker",
        header="Challenge Tracker",
        level=2,
        section_type="table",
        rows=list(rows),
    )
    return {"challenge_tracker": tracker}


def test_lifecycle_reconciler_flips_mismatched_status(pn_gdoc_writer):
    w = pn_gdoc_writer
    row = w.TableRow(
        challenge="SOC budget blocks Splunk PO",
        date="2026-04-21",
        category="Commercial",
        status="Open",
        notes_references="2026-03-28 Cloud close [lifecycle_id:ch-soc-budget]",
    )
    section_map = _make_section_map_with_tracker(w, [row])
    lifecycle = {
        "ch-soc-budget": {
            "current_state": "stalled",
            "history": [],
        },
    }

    changes = w._reconcile_with_lifecycle(section_map, "_TEST_CUSTOMER", lifecycle_override=lifecycle)

    assert row.status == "Stalled"
    assert len(changes) == 1
    ch = changes[0]
    assert ch["action"] == "reconcile_with_lifecycle"
    assert ch["lifecycle_id"] == "ch-soc-budget"
    assert ch["lifecycle_state"] == "stalled"
    assert ch["prior_status"] == "Open"
    assert ch["new_status"] == "Stalled"


def test_lifecycle_reconciler_noop_when_status_already_matches(pn_gdoc_writer):
    w = pn_gdoc_writer
    row = w.TableRow(
        challenge="Champion exit",
        date="2026-04-21",
        category="Risk",
        status="In Progress",
        notes_references="[lifecycle_id:ch-champion-exit]",
    )
    section_map = _make_section_map_with_tracker(w, [row])
    lifecycle = {"ch-champion-exit": {"current_state": "in_progress"}}

    changes = w._reconcile_with_lifecycle(section_map, "_TEST_CUSTOMER", lifecycle_override=lifecycle)

    assert row.status == "In Progress"
    assert changes == []


def test_lifecycle_reconciler_skips_row_without_anchor(pn_gdoc_writer):
    w = pn_gdoc_writer
    row = w.TableRow(
        challenge="Some untagged challenge",
        date="2026-04-21",
        category="Other",
        status="Open",
        notes_references="",
    )
    section_map = _make_section_map_with_tracker(w, [row])
    lifecycle = {"ch-soc-budget": {"current_state": "stalled"}}

    changes = w._reconcile_with_lifecycle(section_map, "_TEST_CUSTOMER", lifecycle_override=lifecycle)

    assert row.status == "Open"
    assert changes == []


def test_lifecycle_reconciler_ignores_unknown_state(pn_gdoc_writer):
    w = pn_gdoc_writer
    row = w.TableRow(
        challenge="something",
        date="2026-04-21",
        category="Other",
        status="Open",
        notes_references="[lifecycle_id:ch-x] context",
    )
    section_map = _make_section_map_with_tracker(w, [row])
    lifecycle = {"ch-x": {"current_state": "not_a_real_state"}}

    changes = w._reconcile_with_lifecycle(section_map, "_TEST_CUSTOMER", lifecycle_override=lifecycle)

    assert row.status == "Open"
    assert changes == []


# ---------------------------------------------------------------------------
# §E (D5) — Deal Stage Tracker motion capture
# ---------------------------------------------------------------------------


def _make_deal_stage_tracker(w, rows):
    return w.DocumentSection(
        key="deal_stage_tracker",
        header="Deal Stage Tracker",
        level=2,
        section_type="table",
        rows=list(rows),
    )


def test_deal_stage_advances_not_active_to_discovery(pn_gdoc_writer):
    w = pn_gdoc_writer
    defend_row = w.TableRow(
        challenge="defend",
        date="not-active",
        category="unverified",
        status="inactive",
        notes_references="no active opportunity",
    )
    section_map = {"deal_stage_tracker": _make_deal_stage_tracker(w, [defend_row])}

    applied = [{
        "section_key": "exec_account_summary",
        "field_key": "upsell_path",
        "action": "append_with_history",
        "full_change": "Pair with Wiz Defend routing guidance once budget unlocks (2026-04-18 QBR)",
        "message": "Appended new entry",
    }]

    changes = w._advance_deal_stage_from_applied(section_map, applied)

    assert defend_row.date == "discovery"
    assert defend_row.status == "active"
    assert "2026-04-18" in defend_row.notes_references
    assert len(changes) == 1
    assert changes[0]["action"] == "advance_deal_stage_from_upsell"
    assert changes[0]["subject"] == "defend"
    assert changes[0]["prior_stage"] == "not-active"
    assert changes[0]["new_stage"] == "discovery"


def test_deal_stage_picks_pov_evidence_over_discovery(pn_gdoc_writer):
    w = pn_gdoc_writer
    sensor_row = w.TableRow(
        challenge="sensor",
        date="not-active",
        category="unverified",
        status="inactive",
        notes_references="no active opportunity",
    )
    section_map = {"deal_stage_tracker": _make_deal_stage_tracker(w, [sensor_row])}

    applied = [{
        "section_key": "exec_account_summary",
        "field_key": "upsell_path",
        "action": "append_with_history",
        "full_change": "Timeboxed Wiz Sensor POV kicked off 2026-03-24",
    }]

    changes = w._advance_deal_stage_from_applied(section_map, applied)

    assert sensor_row.date == "pov"
    assert len(changes) == 1
    assert changes[0]["new_stage"] == "pov"


def test_deal_stage_noop_when_current_stage_already_higher(pn_gdoc_writer):
    w = pn_gdoc_writer
    cloud_row = w.TableRow(
        challenge="cloud",
        date="win",
        category="purchased",
        status="active",
        notes_references="enterprise SKU purchased 2026-03-28",
    )
    section_map = {"deal_stage_tracker": _make_deal_stage_tracker(w, [cloud_row])}

    applied = [{
        "section_key": "exec_account_summary",
        "field_key": "upsell_path",
        "action": "append_with_history",
        "full_change": "Wiz Cloud expansion talk (discovery only)",
    }]

    changes = w._advance_deal_stage_from_applied(section_map, applied)

    assert cloud_row.date == "win"  # not regressed
    assert changes == []


# ---------------------------------------------------------------------------
# §F (D6+D7) — agent_run_log entry injection
# ---------------------------------------------------------------------------


def _make_appendix_section(w):
    fld = w.SectionField(key="agent_run_log", label="Agent Run Log:", update_strategy="append_with_history")
    return w.DocumentSection(
        key="appendix",
        header="Appendix",
        level=1,
        section_type="fields",
        fields={"agent_run_log": fld},
    )


def test_appendix_run_log_healed_from_free_text_when_agent_log_empty(pn_gdoc_writer):
    """Mis-parsed read: compact run line under free_text → agent_run_log."""
    w = pn_gdoc_writer
    run_line = (
        "run_date=2026-04-21; sections_touched=a,b; entries_added=1; "
        "entries_skipped=0; skipped_reasons=; reconciled=;"
    )
    ft = w.SectionField(key="free_text", label=None, update_strategy="free_text", entries=[w.Entry("noise"), w.Entry(run_line)])
    ar = w.SectionField(key="agent_run_log", label="Agent Run Log:", update_strategy="append_with_history", entries=[])
    appendix = w.DocumentSection(
        key="appendix",
        header="Appendix",
        level=1,
        section_type="fields",
        fields={"free_text": ft, "agent_run_log": ar},
    )
    sm = {"appendix": appendix}
    w._heal_appendix_run_log_from_free_text(sm)
    assert len(ar.entries) == 1 and ar.entries[0].value == run_line
    assert len(ft.entries) == 1 and ft.entries[0].value == "noise"


def test_agent_run_log_entry_contains_required_keys(pn_gdoc_writer):
    w = pn_gdoc_writer
    section_map = {"appendix": _make_appendix_section(w)}
    applied = [
        {
            "section_key": "exec_account_summary",
            "field_key": "risk",
            "action": "append_with_history",
            "message": "Appended new entry",
        },
        {
            "section_key": "exec_account_summary",
            "field_key": "top_goal",
            "action": "append_with_history",
            "message": "Appended new entry",
        },
    ]
    skipped = [
        {
            "mutation": {"section_key": "company_overview", "field_key": "free_text"},
            "reason": "missing_evidence: no in-scope transcript signal",
        },
    ]
    reconciled = [
        {
            "action": "reconcile_with_lifecycle",
            "lifecycle_id": "ch-soc-budget",
            "lifecycle_state": "stalled",
            "new_status": "Stalled",
        },
    ]

    result = w._inject_agent_run_log_entry(
        section_map,
        applied=applied,
        skipped=skipped,
        reconciled=reconciled,
        completeness_report=None,
        lookback_window="2026-03-21 -> 2026-04-21 (30d)",
        transcripts_in_scope=8,
        dal_prepends_emitted=8,
    )

    assert result is not None
    entries = section_map["appendix"].fields["agent_run_log"].entries
    assert len(entries) == 1
    injected = entries[0]
    assert injected.timestamp == w.TODAY
    value = injected.value
    # Shape contract (task §F): every key MUST be present in the emitted line.
    for required in (
        "run_date=",
        "sections_touched=",
        "entries_added=",
        "entries_skipped=",
        "skipped_reasons=",
        "reconciled=",
        "lookback_window=",
        "transcripts_in_scope=8",
        "dal_prepends_emitted=8",
    ):
        assert required in value, f"missing key {required!r} in run_log value: {value}"
    # Reconciled summary must cite the lifecycle id and the new status.
    assert "ch-soc-budget" in value
    assert "Stalled" in value
    # Entries-added count excludes the agent_run_log entry itself.
    assert "entries_added=2" in value


def test_agent_run_log_entry_roundtrips_timestamp_via_formatter(pn_gdoc_writer):
    """End-to-end check: the injected entry must render with a trailing date
    when passed through `_format_entry_line_for_section`, so that a subsequent
    `read` of the Doc parses the timestamp back."""

    w = pn_gdoc_writer
    section_map = {"appendix": _make_appendix_section(w)}

    w._inject_agent_run_log_entry(
        section_map,
        applied=[{"section_key": "challenge_tracker", "field_key": "table", "action": "add_table_row"}],
        skipped=[],
        reconciled=[],
        completeness_report=None,
    )
    entry = section_map["appendix"].fields["agent_run_log"].entries[-1]
    line = w._format_entry_line_for_section("appendix", "agent_run_log", entry)

    assert line.endswith(f" [{w.TODAY}]")
    parsed_back = w.parse_entry_text(line)
    assert parsed_back.timestamp == w.TODAY


def test_agent_run_log_injection_returns_none_when_section_missing(pn_gdoc_writer):
    w = pn_gdoc_writer
    # No 'appendix' key in the section_map -> writer must noop (legacy Doc).
    result = w._inject_agent_run_log_entry(
        {},
        applied=[{"section_key": "exec_account_summary", "field_key": "risk", "action": "append_with_history"}],
        skipped=[],
        reconciled=[],
        completeness_report=None,
    )

    assert result is None


def test_today_constant_parses_as_iso_date(pn_gdoc_writer):
    # Guardrail: the timestamp we emit must parse as an ISO date. If someone
    # changes TODAY to a non-ISO string, re-reads will fail silently.
    w = pn_gdoc_writer
    parsed = date.fromisoformat(w.TODAY)
    assert parsed.isoformat() == w.TODAY


# ---------------------------------------------------------------------------
# TASK-074 — workflows → Accomplishments for vendor decommission / displacement
# ---------------------------------------------------------------------------


def test_route_workflow_mutation_rewrites_vendor_decommission_to_accomplishments(pn_gdoc_writer):
    w = pn_gdoc_writer
    m = {
        "section_key": "workflows",
        "field_key": "free_text",
        "action": "append_with_history",
        "new_value": "Decommissioned Prisma Cloud CSPM and consolidated findings in Wiz. [2026-04-01]",
        "reasoning": "Transcript: retirement initiative",
    }
    w._route_use_case_workflow_mutation(m)
    assert m["section_key"] == "accomplishments"
    assert "accomplishments.free_text" in m.get("reasoning", "") or "Accomplishments" in m.get("reasoning", "")


def test_route_workflow_mutation_leaves_process_heavy_win_in_workflows(pn_gdoc_writer):
    w = pn_gdoc_writer
    # Many workflow tokens: should not over-route a long runbook that mentions a single decommission in passing.
    long_narr = (
        "Jira triage, owner mapping, pivot tables, and monthly reporting. "
    ) * 8
    m = {
        "section_key": "workflows",
        "field_key": "free_text",
        "action": "append_with_history",
        "new_value": long_narr
        + " we also decommissioned a legacy scanner. "
        "trigger intake remediation closeout [2026-04-01]",
        "reasoning": "process",
    }
    w._route_use_case_workflow_mutation(m)
    assert m["section_key"] == "workflows"

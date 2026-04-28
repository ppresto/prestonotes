from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import date, timedelta
from pathlib import Path


def _load_wdc():
    path = Path(__file__).resolve().parents[1] / "wiz_doc_cache_manager.py"
    spec = importlib.util.spec_from_file_location("wiz_doc_cache_manager", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write_snapshot(
    seed_dir: Path, basename: str, query: str, saved_at: str, *, top_k: int = 1
) -> None:
    seed_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "query": query,
        "saved_at": saved_at,
        "source_tool": "wiz_docs_knowledge_base",
        "result_count": 1,
        "top_k": top_k,
        "results": [{"Title": "t", "Href": "h", "Score": 1, "Content": "c"}],
    }
    (seed_dir / f"{basename}.json").write_text(json.dumps(payload), encoding="utf-8")


def test_kb_snapshot_status_marks_stale_and_fresh(tmp_path: Path, capsys) -> None:
    wdc = _load_wdc()
    wdc.KB_SNAPSHOTS_DIR = tmp_path / "mcp_query_snapshots"
    initial_slug = "license"
    seed_dir = wdc.KB_SNAPSHOTS_DIR / initial_slug
    _write_snapshot(seed_dir, "license", "Licensing and Billing", str(date.today()))
    _write_snapshot(
        seed_dir,
        "license-workloadunits",
        "Licensing and Billing-Billable Units",
        str(date.today() - timedelta(days=10)),
    )

    args = argparse.Namespace(initial_slug=initial_slug, max_age_days=7, json=True, seed_file=None)
    try:
        wdc.cmd_kb_snapshot_status(args)
    except SystemExit as exc:
        assert exc.code == 1
    out = capsys.readouterr().out
    body = json.loads(out)
    assert body["state"] == "STALE"
    statuses = {row["path"]: row["status"] for row in body["files"]}
    assert statuses["license.json"] == "FRESH"
    assert statuses["license-workloadunits.json"] == "STALE"


def test_kb_snapshot_status_missing_expected_from_yaml(tmp_path: Path, capsys) -> None:
    wdc = _load_wdc()
    wdc.KB_SNAPSHOTS_DIR = tmp_path / "mcp_query_snapshots"
    seed_yaml = tmp_path / "seeds.yaml"
    seed_yaml.write_text(
        "version: 1\nseeds:\n"
        '  - initial_query: "licensing - wiz code - billable units"\n    results: 1\n'
        '  - initial_query: "licensing - wiz cloud - billable units"\n    results: 1\n',
        encoding="utf-8",
    )
    initial_slug = "licensing"
    seed_dir = wdc.KB_SNAPSHOTS_DIR / initial_slug
    seed_dir.mkdir(parents=True)
    _write_snapshot(
        seed_dir,
        "wiz-code-billable-units",
        "licensing - wiz code - billable units",
        str(date.today()),
    )
    args = argparse.Namespace(
        initial_slug=initial_slug, max_age_days=7, json=True, seed_file=seed_yaml
    )
    try:
        wdc.cmd_kb_snapshot_status(args)
    except SystemExit as exc:
        assert exc.code == 1
    body = json.loads(capsys.readouterr().out)
    by_path = {r["path"]: r["status"] for r in body["files"]}
    assert by_path["wiz-code-billable-units.json"] == "FRESH"
    assert by_path["wiz-cloud-billable-units.json"] == "MISSING"
    assert body["expected_from_yaml"] == 2


def test_build_envelope_parses_mcp_wrapped_content() -> None:
    wdc = _load_wdc()
    payload = {
        "content": [
            {
                "type": "text",
                "text": json.dumps(
                    {
                        "results": [
                            {
                                "Title": "Licensing and Billing",
                                "Href": "https://docs.wiz.io/docs/licenses",
                            }
                        ]
                    }
                ),
            }
        ]
    }
    envelope = wdc._build_envelope("Licensing and Billing", payload, str(date.today()))
    assert envelope["result_count"] == 1
    assert envelope["results"][0]["Title"] == "Licensing and Billing"


def test_build_envelope_rejects_payload_without_results() -> None:
    wdc = _load_wdc()
    payload = {"content": [{"type": "text", "text": "not json"}]}
    try:
        wdc._build_envelope("Licensing and Billing", payload, str(date.today()))
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "payload missing results list" in str(exc)


def test_kb_snapshot_save_slice_top_k_keeps_highest_score(tmp_path: Path, capsys) -> None:
    wdc = _load_wdc()
    wdc.KB_SNAPSHOTS_DIR = tmp_path / "mcp_query_snapshots"
    payload = {
        "results": [
            {"Title": "low", "Href": "https://docs.wiz.io/a", "Score": 0.1, "Content": "x"},
            {"Title": "high", "Href": "https://docs.wiz.io/b", "Score": 0.9, "Content": "y"},
        ]
    }
    import io
    import sys

    old_stdin = sys.stdin
    try:
        sys.stdin = io.StringIO(json.dumps(payload))
        args = argparse.Namespace(
            query="licensing - wiz cloud - billable units",
            initial_slug=None,
            chain_prefix=None,
            json_file=None,
            saved_at=str(date.today()),
            raw_sidecar=False,
            dedup_inline=False,
            top_k=None,
            slice_top_k=1,
        )
        wdc.cmd_kb_snapshot_save(args)
    finally:
        sys.stdin = old_stdin

    out_path = Path(capsys.readouterr().out.strip())
    saved = json.loads(out_path.read_text(encoding="utf-8"))
    assert saved["result_count"] == 1
    assert saved["results"][0]["Title"] == "high"
    assert saved["top_k"] == 1

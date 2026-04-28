from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_wdc():
    path = Path(__file__).resolve().parents[1] / "wiz_doc_cache_manager.py"
    spec = importlib.util.spec_from_file_location("wiz_doc_cache_manager", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_dedupe_kb_results_keeps_highest_score_per_href() -> None:
    wdc = _load_wdc()
    rows = [
        {"Title": "A", "Href": "https://docs.wiz.io/docs/foo", "Score": 0.5, "Content": "low"},
        {"Title": "B", "Href": "https://docs.wiz.io/docs/foo", "Score": 0.9, "Content": "high"},
        {"Title": "C", "Href": "https://docs.wiz.io/docs/bar", "Score": 0.8, "Content": "other"},
    ]
    out, meta = wdc.dedupe_kb_results(rows)
    assert meta["input_count"] == 3
    assert meta["output_count"] == 2
    assert meta["removed_count"] == 1
    hrefs = {r["Href"] for r in out}
    assert hrefs == {"https://docs.wiz.io/docs/foo", "https://docs.wiz.io/docs/bar"}
    foo = next(r for r in out if "foo" in r["Href"])
    assert foo["Content"] == "high"


def test_dedupe_normalizes_href_path_case() -> None:
    wdc = _load_wdc()
    rows = [
        {"Title": "x", "Href": "HTTPS://DOCS.WIZ.IO/docs/Foo", "Score": 1.0, "Content": "a"},
        {"Title": "y", "Href": "https://docs.wiz.io/docs/foo", "Score": 0.5, "Content": "b"},
    ]
    out, meta = wdc.dedupe_kb_results(rows)
    assert meta["output_count"] == 1
    assert out[0]["Content"] == "a"


def test_kb_query_category_and_snapshot_basename() -> None:
    wdc = _load_wdc()
    q = "licensing - wiz cloud - billable units"
    assert wdc.kb_query_category_dir(q) == "licensing"
    assert wdc.kb_query_snapshot_basename(q) == "wiz-cloud-billable-units"


def test_kb_query_single_segment_basename() -> None:
    wdc = _load_wdc()
    assert wdc.kb_query_category_dir("standalone") == "standalone"
    assert wdc.kb_query_snapshot_basename("standalone") == "standalone"


def test_kb_top_results_order_and_limit() -> None:
    wdc = _load_wdc()
    rows = [
        {"Title": "low", "Score": 0.1, "Href": "https://a"},
        {"Title": "high", "Score": 0.9, "Href": "https://b"},
        {"Title": "mid", "Score": 0.5, "Href": "https://c"},
    ]
    out = wdc.kb_top_results(rows, 2)
    assert len(out) == 2
    assert out[0]["Title"] == "high"
    assert out[1]["Title"] == "mid"


def test_envelope_apply_dedup_fields() -> None:
    wdc = _load_wdc()
    env = {
        "query": "q",
        "saved_at": "2026-01-01",
        "source_tool": "wiz_docs_knowledge_base",
        "result_count": 2,
        "results": [
            {"Title": "t", "Href": "https://x/y", "Score": 0.1, "Content": "a"},
            {"Title": "t2", "Href": "https://x/y", "Score": 0.9, "Content": "b"},
        ],
    }
    wdc.envelope_apply_dedup_fields(env)
    assert env["result_count_deduped"] == 1
    assert len(env["results_deduped"]) == 1
    assert env["results_deduped"][0]["Content"] == "b"

"""TASK-052: v2 materialize must not wipe round-1 call-records on disk."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


def _load_materialize_module() -> object:
    repo_root = Path(__file__).resolve().parent.parent.parent
    path = repo_root / "scripts" / "e2e-test-customer-materialize.py"
    spec = importlib.util.spec_from_file_location("e2e_test_customer_materialize", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_materialize_v2_preserves_existing_call_records(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("PRESTONOTES_REPO_ROOT", str(tmp_path))
    root = tmp_path
    cdir = root / "MyNotes" / "Customers" / "_TEST_CUSTOMER"
    v1 = root / "tests" / "fixtures" / "e2e" / "_TEST_CUSTOMER" / "v1"
    v2 = root / "tests" / "fixtures" / "e2e" / "_TEST_CUSTOMER" / "v2"
    (v1 / "Transcripts").mkdir(parents=True)
    (v2 / "Transcripts").mkdir(parents=True)
    (v1 / "Transcripts" / "2026-01-01-a.txt").write_text("a", encoding="utf-8")
    (v2 / "Transcripts" / "2026-02-01-b.txt").write_text("b", encoding="utf-8")

    (cdir / "Transcripts").mkdir(parents=True)
    (cdir / "call-records").mkdir(parents=True)
    prior = cdir / "call-records" / "from_round1.json"
    prior.write_text(
        json.dumps({"call_id": "round1", "extraction_confidence": "high"}), encoding="utf-8"
    )

    mod = _load_materialize_module()
    assert mod.cmd_apply(root, v2=True) == 0
    assert prior.is_file()
    data = json.loads(prior.read_text(encoding="utf-8"))
    assert data.get("call_id") == "round1"
    assert (cdir / "Transcripts" / "2026-02-01-b.txt").is_file()

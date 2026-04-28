"""Guard: e2e bump maps oldest narrative to earliest calendar date in the rolled window."""

from __future__ import annotations

import importlib.util
import sys
from datetime import date
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
_BUMP_NAME = "_e2e_bump_dates_st"


def _load_bump_module():
    p = REPO / "scripts" / "e2e-test-customer-bump-dates.py"
    spec = importlib.util.spec_from_file_location(_BUMP_NAME, p)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {p}")
    mod = importlib.util.module_from_spec(spec)
    # Register before exec so dataclass can resolve forward refs / module dict.
    sys.modules[_BUMP_NAME] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception:
        del sys.modules[_BUMP_NAME]
        raise
    return mod


@pytest.fixture(scope="module")
def bump():
    return _load_bump_module()


def test_assign_target_dates_preserves_narrative_order(bump) -> None:
    today = date(2026, 4, 27)
    PerCallTxt = bump.PerCallTxt
    files = [
        PerCallTxt(path=Path("x"), old_date=date(2026, 2, 21), slug="a"),
        PerCallTxt(path=Path("y"), old_date=date(2026, 5, 5), slug="b"),
    ]
    m = bump._assign_target_dates(files, today=today)
    older = m["2026-02-21-a"]
    newer = m["2026-05-05-b"]
    assert older < newer, f"oldest story should map to earlier calendar date: {older} vs {newer}"


def test_assign_target_dates_three_files_monotonic(bump) -> None:
    today = date(2026, 4, 27)
    PerCallTxt = bump.PerCallTxt
    files = [
        PerCallTxt(path=Path("a"), old_date=date(2026, 1, 1), slug="x"),
        PerCallTxt(path=Path("b"), old_date=date(2026, 2, 1), slug="y"),
        PerCallTxt(path=Path("c"), old_date=date(2026, 3, 1), slug="z"),
    ]
    m = bump._assign_target_dates(files, today=today)
    d1 = m["2026-01-01-x"]
    d2 = m["2026-02-01-y"]
    d3 = m["2026-03-01-z"]
    assert d1 < d2 < d3
    assert (today - d1).days >= (today - d2).days >= (today - d3).days

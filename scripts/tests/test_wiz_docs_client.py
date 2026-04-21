"""wiz_docs_client GraphQL response parsing."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import wiz_docs_client  # noqa: E402


def test_extract_docs_block_full() -> None:
    result = {
        "data": {
            "aiAssistantQuery": {
                "aiAssistantQueryResult": {
                    "docs": {
                        "text": "Hello **world**",
                        "links": [{"text": "Doc", "href": "https://docs.wiz.io/docs/x"}],
                    }
                }
            }
        }
    }
    out = wiz_docs_client.extract_docs_block(result)
    assert out is not None
    assert out["text"] == "Hello **world**"
    assert out["links"] == [{"text": "Doc", "href": "https://docs.wiz.io/docs/x"}]


def test_extract_docs_block_missing() -> None:
    assert wiz_docs_client.extract_docs_block({}) is None

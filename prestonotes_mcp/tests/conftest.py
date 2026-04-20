"""Shared test fixtures."""

import pytest


@pytest.fixture(autouse=True)
def reset_security_rate_limit() -> None:
    import prestonotes_mcp.security as sec

    sec._rate_count = 0
    sec._rate_bucket = 0
    yield

"""Pytest configuration for prestonotes_gdoc unit tests.

The writer lives in a hyphenated filename (``update-gdoc-customer-notes.py``)
which cannot be imported with normal ``import`` syntax. This conftest loads it
once via ``importlib`` and exposes the module under the ``pn_gdoc_writer``
fixture for all tests in this package.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

_WRITER_PATH = Path(__file__).resolve().parent.parent / "update-gdoc-customer-notes.py"
_WRITER_MODULE_NAME = "prestonotes_gdoc_writer"


def _load_writer_module() -> ModuleType:
    if _WRITER_MODULE_NAME in sys.modules:
        return sys.modules[_WRITER_MODULE_NAME]
    spec = importlib.util.spec_from_file_location(
        _WRITER_MODULE_NAME, _WRITER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load writer module from {_WRITER_PATH}")
    module = importlib.util.module_from_spec(spec)
    # Register BEFORE exec_module so @dataclass decorators inside the module
    # can resolve string annotations via sys.modules[cls.__module__].
    sys.modules[_WRITER_MODULE_NAME] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(_WRITER_MODULE_NAME, None)
        raise
    return module


@pytest.fixture(scope="session")
def pn_gdoc_writer() -> ModuleType:
    return _load_writer_module()

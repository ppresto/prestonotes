#!/usr/bin/env python3
"""Canonical entrypoint for Wiz cache management commands."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_legacy_module():
    path = Path(__file__).resolve().parent / "wiz_doc_cache_manager.py"
    spec = importlib.util.spec_from_file_location("wiz_doc_cache_manager", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> None:
    legacy = _load_legacy_module()
    parser = legacy.build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

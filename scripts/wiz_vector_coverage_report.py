#!/usr/bin/env python3
"""Compare wiz manifest doc:* entries vs on-disk docs and optional Chroma coverage."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

DEFAULT_MANIFEST = "docs/ai/cache/wiz_mcp_server/manifest.json"
DEFAULT_DOCS_DIR = "docs/ai/cache/wiz_mcp_server/docs"


def _load_manifest(repo: Path) -> dict:
    p = repo / DEFAULT_MANIFEST
    if not p.is_file():
        return {}
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return raw if isinstance(raw, dict) else {}


def _manifest_win_docs(manifest: dict) -> list[str]:
    out: list[str] = []
    entries = manifest.get("entries")
    if not isinstance(entries, list):
        return out
    for e in entries:
        if not isinstance(e, dict):
            continue
        if e.get("type") != "win_doc":
            continue
        eid = str(e.get("id") or "")
        if not eid.startswith("doc:"):
            continue
        name = eid[len("doc:") :].strip()
        if name:
            out.append(name)
    return sorted(set(out))


def _chroma_path_from_config(repo: Path) -> str:
    cfg_path = repo / "prestonotes_mcp" / "prestonotes-mcp.yaml"
    if not cfg_path.is_file():
        return ".vector_db/wiz_chroma"
    try:
        import yaml  # noqa: PLC0415

        cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
        rag = cfg.get("rag") if isinstance(cfg.get("rag"), dict) else {}
        cr = str(rag.get("chroma_path") or "").strip()
        return cr or ".vector_db/wiz_chroma"
    except Exception:
        return ".vector_db/wiz_chroma"


def _read_chroma(repo: Path, chroma_rel: str) -> dict[str, object] | None:
    try:
        import chromadb  # noqa: PLC0415
    except Exception:
        return None
    try:
        client = chromadb.PersistentClient(path=str((repo / chroma_rel).resolve()))
        col = client.get_collection("wiz_docs")
    except Exception:
        return None

    n = int(col.count())
    paths: set[str] = set()
    batch = 500
    offset = 0
    while offset < n:
        page = col.get(include=["metadatas"], limit=batch, offset=offset)
        for m in page.get("metadatas") or []:
            if isinstance(m, dict) and m.get("source_path"):
                paths.add(str(m["source_path"]))
        offset += batch

    prefix = DEFAULT_DOCS_DIR.rstrip("/") + "/"
    under_docs = {p for p in paths if p.startswith(prefix) and p.endswith(".md")}
    return {
        "chunks": n,
        "unique_source_paths": len(paths),
        "unique_under_wiz_docs": len(under_docs),
        "source_paths_sample": sorted(paths)[:20],
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Wiz manifest vs filesystem vs Chroma coverage.")
    p.add_argument("--repo-root", type=Path, required=True)
    args = p.parse_args(argv)
    repo = args.repo_root.resolve()

    manifest = _load_manifest(repo)
    doc_names = _manifest_win_docs(manifest)
    total_m = len(doc_names)
    docs_dir = repo / DEFAULT_DOCS_DIR
    present = 0
    missing: list[str] = []
    for name in doc_names:
        fp = docs_dir / f"{name}.md"
        if fp.is_file():
            present += 1
        else:
            missing.append(name)

    pct_fs = (100.0 * present / total_m) if total_m else 0.0
    print("## Manifest vs filesystem (win_doc doc:*)")
    print(f"manifest_doc_entries\t{total_m}")
    print(f"markdown_files_present\t{present}")
    print(f"percent_present\t{pct_fs:.1f}")
    if missing and len(missing) <= 30:
        print("missing_files\t" + ", ".join(f"{n}.md" for n in missing))
    elif missing:
        print(f"missing_files_count\t{len(missing)} (first 20: {', '.join(missing[:20])})")

    chroma_rel = _chroma_path_from_config(repo)
    stats = _read_chroma(repo, chroma_rel)
    print()
    if stats is None:
        print("## Chroma")
        print(
            "chroma_available\tno (import or collection failed; manifest/fs table above is still valid)"
        )
        return 0

    print("## Chroma (wiz_docs)")
    print(f"chroma_path\t{chroma_rel}")
    print(f"chunks_total\t{stats['chunks']}")
    print(f"unique_source_paths\t{stats['unique_source_paths']}")
    print(f"unique_paths_under_wiz_docs_md\t{stats['unique_under_wiz_docs']}")
    sample = stats.get("source_paths_sample") or []
    if sample:
        print("source_paths_sample\t" + "\n\t".join(str(x) for x in sample))

    u = int(stats["unique_under_wiz_docs"])
    cov = (100.0 * u / present) if present else 0.0
    print()
    print("## Indexed file coverage vs manifest docs present on disk")
    print(f"estimate_indexed_unique_files_vs_manifest_present_pct\t{cov:.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

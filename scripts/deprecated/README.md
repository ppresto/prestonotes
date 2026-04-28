# Deprecated scripts

Do **not** wire these into playbooks or CI unless you are explicitly reviving or auditing old behavior.

| Script | Notes |
|--------|--------|
| `lpi_kb_seed_refresh.py` | Headless `wiz_docs_knowledge_base` over Streamable HTTP. **Superseded** by Cursor **wiz-remote** MCP + `wiz_cache_manager.py kb-snapshot save` (and `scripts/materialize_licensing_kb_snapshots.py` for committed seed bodies). The repo root shim `scripts/lpi_kb_seed_refresh.py` exits **2** with migration instructions. |

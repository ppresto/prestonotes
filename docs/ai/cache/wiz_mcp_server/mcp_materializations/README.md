# MCP materializations

Markdown snapshots produced by **`scripts/materialize_wiz_mcp_docs.py`** (tenant GraphQL `aiAssistantQuery` / DOCS). One file per WIN **`doc_name`**: `<doc_name>.md`.

Files appear after the first successful **`mcp-materialize`** run. Safe to gitignore locally if you prefer not to commit generated content; CI tests use a temporary repo without calling the network.

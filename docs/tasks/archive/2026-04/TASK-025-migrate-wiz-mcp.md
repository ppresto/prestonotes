# TASK-025 — Migrate wiz-local MCP pack into this repo (`task-migrate-wiz-mcp`)

**Status:** `[x] COMPLETE` (2026-04-20)  
**Canonical source:** sibling checkout **`../prestoNotes.orig/wiz-mcp/`**.

---

## Shipped summary

- **`wiz-mcp/`** copied into repo (rsync excludes **`wiz-mcp.env`** and **`tmp/`** contents).
- **`.cursor/mcp.json`** merged: **`prestonotes`** + **`wiz-local`**; **`wiz-local`** uses **`envFile`** **`../.cursor/mcp.env`** so Wiz OAuth vars live in the same gitignored file as PrestoNotes (no required **`wiz-mcp/wiz-mcp.env`**).
- **`run-wiz-mcp-for-cursor.sh`** / **`diagnose.sh`** resolve credentials in order: **`wiz-mcp/wiz-mcp.env`** → **`.cursor/wiz-mcp.env`** → **`.cursor/mcp.env`**.
- **`wiz-mcp/README.md`**, root **`README.md`** (Wiz MCP subsection), **`.cursor/mcp.env.example`**, **`scripts/ci/required-paths.manifest`** updated.

---

## Goal (original)

1. **Copy** the **`wiz-mcp/`** directory from **`prestoNotes.orig`** into **this repo root** as **`wiz-mcp/`** (same layout: `config.sh`, `run-wiz-mcp-for-cursor.sh`, `setup-cursor.sh`, `diagnose.sh`, `write-wiz-dotenv.sh`, `wiz-mcp.env.example`, `.gitignore`, etc.).
2. **Configure** paths and credentials so **wiz-local** runs **`uv`** against your **clone of [wiz-sec/wiz-mcp](https://github.com/wiz-sec/wiz-mcp)** (`src/wiz_mcp_server/server.py`).
3. **Wire Cursor** so **`.cursor/mcp.json`** includes **both** **`prestonotes`** (existing) **and** **`wiz-local`** / optional **`wiz-remote`** — **without** overwriting the prestonotes entry.

---

## Required environment variables

### Wiz OAuth (`WIZ_CLIENT_ID`, `WIZ_CLIENT_SECRET`, `WIZ_ENV`)

Plain **`KEY=value`** lines. **PrestoNotes:** use **`.cursor/mcp.env`** (optional split: **`wiz-mcp/wiz-mcp.env`** or **`.cursor/wiz-mcp.env`**).

### **`wiz-mcp/config.sh`** or gitignored **`wiz-mcp/config.local.sh`**

| Variable | Typical default | Purpose |
|----------|-----------------|--------|
| **`UV_BIN`** | `/opt/homebrew/bin/uv` | `uv` used by launcher. |
| **`WIZ_MCP_CHECKOUT`** | `$HOME/Projects/wiz-mcp` | Path to **cloned** upstream wiz-mcp repo (not this pack). |
| **`WIZ_MCP_SERVER_DIR`** | `$WIZ_MCP_CHECKOUT/src/wiz_mcp_server` | Where **`mcp run server.py`** runs. |
| **`WIZ_MCP_DOTENV`** | `$WIZ_HELPER_ROOT/wiz-mcp.env` | First-choice credential **file** (optional if **`.cursor/mcp.env`** holds **`WIZ_*`**). |

### Runtime

**`run-wiz-mcp-for-cursor.sh`** sets **`WIZ_DOTENV_PATH`** to the resolved dotenv file (unsets inherited bad values).

---

## Acceptance (closed)

- [x] **`wiz-mcp/`** at repo root; scripts executable; **`wiz-mcp.env.example`** committed; **`wiz-mcp/wiz-mcp.env`** optional.
- [x] **`.cursor/mcp.json`** lists **prestonotes + wiz-local** with **`envFile`** on both where appropriate.
- [x] **`./wiz-mcp/diagnose.sh`** + **`scripts/ci/check-repo-integrity.sh`** pass when upstream checkout and **`.cursor/mcp.env`** are configured.

---

## References

- **Pack README:** [`wiz-mcp/README.md`](../../../../wiz-mcp/README.md)
- **Upstream server:** [https://github.com/wiz-sec/wiz-mcp](https://github.com/wiz-sec/wiz-mcp)

**Note:** Do **not** run orig **`setup-cursor.sh`** alone in this repo — it overwrites **`mcp.json`**.

# Wiz MCP — portable Cursor pack

Copy this entire **`wiz-mcp/`** directory into another repo, adjust **`config.sh`** (or **`config.local.sh`**), create credentials, wire Cursor, reload. Local MCP runs **`uv`** against your clone of the [Wiz MCP server](https://github.com/wiz-sec/wiz-mcp) repo.

## Prerequisites

- **macOS or Linux** with **bash**, **curl**.
- **[uv](https://docs.astral.sh/uv/)** on `PATH` (default in **`config.sh`**: `/opt/homebrew/bin/uv` — change if yours differs).
- A **clone of the Wiz MCP server** checkout; by default **`config.sh`** expects `~/Projects/wiz-mcp` with `src/wiz_mcp_server/server.py`.
- **1Password CLI** (`op`) if you use **`./write-wiz-dotenv.sh`** to materialize secrets.

## Setup

1. **Edit paths and defaults** in **`config.sh`** (top section):  
   **`UV_BIN`**, **`WIZ_MCP_CHECKOUT`**, **`WIZ_OP_ITEM`**, **`WIZ_ENV_DEFAULT`**.  
   For one-off overrides without editing tracked files, copy **`config.local.example.sh`** → **`config.local.sh`** (gitignored).

2. **Sign in to 1Password** (if using `op`):  
   `eval "$(op signin)"` or your usual flow.

3. **Wiz OAuth credentials** (plain `KEY=value`, no `export`, no `$(op …)` in the file):

   **PrestoNotes default:** put **`WIZ_CLIENT_ID`**, **`WIZ_CLIENT_SECRET`**, and **`WIZ_ENV`** in **`../.cursor/mcp.env`** (same file as Drive / gcloud). The launcher resolves dotenv in this order: **`wiz-mcp/wiz-mcp.env`** → **`.cursor/wiz-mcp.env`** → **`.cursor/mcp.env`**.

   **Standalone pack:** from **`wiz-mcp/`**:

   ```bash
   cd wiz-mcp
   chmod +x *.sh
   ./write-wiz-dotenv.sh
   ```

   Or copy **`wiz-mcp.env.example`** → **`wiz-mcp.env`** and paste **Client ID** / **Client Secret** from the Wiz console (Integrations → Wiz MCP).

4. **Point Cursor at the launcher** (stdio server):

   ```bash
   ./setup-cursor.sh
   ```

   This writes **`.cursor/mcp.json`** with an **absolute** path to **`run-wiz-mcp-for-cursor.sh`**. You can hand-edit **`mcp.json`** instead; the **`command`** must be that script so **`WIZ_DOTENV_PATH`** is set to **`wiz-mcp/wiz-mcp.env`** and not inherited from a broken shell environment.

5. **Reload Cursor**: **Developer → Reload Window**.

6. **Optional check**: `./diagnose.sh` — OAuth should report **HTTP 200**; artifacts go under **`tmp/`** (gitignored).

### Docs search without Cursor MCP (PrestoNotes)

Cursor’s **wiz-local** MCP uses stdio only inside the IDE. For **terminals, CI, or agent sandboxes** that share the same tenant credentials, PrestoNotes ships **`scripts/wiz_docs_search_cli.py`** — it loads **`WIZ_*`** from **`.cursor/mcp.env`** and calls the same **`aiAssistantQuery`** GraphQL as **`search_wiz_docs`**.

```bash
uv run python scripts/wiz_docs_search_cli.py --query "How do I install the Wiz sensor?"
```

### Credential file location

**`.cursor/wiz-mcp.env`** and **`wiz-mcp/wiz-mcp.env`** are still supported if you prefer a split file. Remove stale **`WIZ_DOTENV_PATH`** from your shell if it pointed at the wrong path (see troubleshooting).

## Troubleshooting

These notes sit **after** setup on purpose — most issues are environment or credential mismatches, not the MCP code.

| Symptom | What to check |
|--------|----------------|
| **“No .env file found”** / missing client vars | **`WIZ_CLIENT_ID`**, **`WIZ_CLIENT_SECRET`**, **`WIZ_ENV`** must be in one of: **`wiz-mcp/wiz-mcp.env`**, **`.cursor/wiz-mcp.env`**, or **`.cursor/mcp.env`** (PrestoNotes). Run **`./write-wiz-dotenv.sh`** or fill **`wiz-mcp.env.example`** manually. Reload Cursor. |
| **`WIZ_DOTENV_PATH` points at a directory** (e.g. `$HOME/.wiz`) | Invalid for python-dotenv — it must be a **file**. **`run-wiz-mcp-for-cursor.sh`** unsets inherited **`WIZ_DOTENV_PATH`** and sets it to **`wiz-mcp/wiz-mcp.env`**. If something else starts `uv` without the wrapper, fix that entrypoint or **`unset WIZ_DOTENV_PATH`** in your shell before testing. |
| **HTTP 400** on **`/oauth/token`** with a short **“Bad Request”** body | Usually **wrong client id/secret** for **`auth.${WIZ_ENV}.wiz.io`**. Use credentials from the **Wiz MCP integration** (or the SA that matches that tenant/region). Wrong 1Password item (e.g. **wiz-cli** item vs **API/MCP** SA) is a common cause. |
| **HTTP 401** | Rotate secret or fix **`WIZ_ENV`** (e.g. `app` → **`auth.app.wiz.io`**). |
| **Empty or masked secret from `op`** | Use **`--reveal`** on the concealed field (often **`credential`** or **`password`**). **`write-wiz-dotenv.sh`** tries **`credential`** and **`password`**; override with **`WIZ_OP_FIELD_SECRET`** in **`config.local.sh`** if your field label differs. |
| **`diagnose.sh` OAuth works but Cursor still fails** | Confirm **`mcp.json`** **`command`** is **`…/wiz-mcp/run-wiz-mcp-for-cursor.sh`**, not raw **`uv`**. Check **`~/.cursor/projects/.../mcps/...-wiz-local/`**: missing **`tools/`** and **`STATUS.md`** present usually means the server process exited on startup. |
| **Diagnose looks “green” only when you sourced something** | **`diagnose.sh`** reads **the file** only for the token step. If your shell exports **`WIZ_*`** from **`wizCLI.sh`** etc., Cursor’s child process might **not** inherit the same — always validate **`wiz-mcp.env`** and the wrapper script. |

**Verbose OAuth trace** (may include request details — do not share publicly):

```bash
WIZ_OAUTH_VERBOSE=1 ./diagnose.sh
```

Log file under **`tmp/oauth-VERBOSE-*.log`**.

## Layout

| Path | Purpose |
|------|---------|
| **`config.sh`** | Shared variables; optional **`config.local.sh`**. |
| **`run-wiz-mcp-for-cursor.sh`** | Cursor stdio: sets **`WIZ_DOTENV_PATH`**, runs **`uv`** → **`mcp run server.py`**. |
| **`write-wiz-dotenv.sh`** | Writes **`wiz-mcp.env`** via **`op`**. |
| **`setup-cursor.sh`** | Writes **`.cursor/mcp.json`** with absolute paths. |
| **`diagnose.sh`** | Dotenv + **`uv`** + OAuth + short MCP smoke; **`tmp/`** for headers/body. |
| **`wiz-mcp.env`** | Secrets (gitignored). |
| **`wiz-mcp.env.example`** | Template. |

**Remote fallback**: **`wiz-remote`** in **`mcp.json`** uses **`WIZ_REMOTE_MCP_URL`** from **`config.sh`** (default demo URL). Complete any OAuth step Cursor shows for that server if you use it.

# Playbook: Run License Evidence Check

Trigger: `Run License Evidence Check for [CustomerName]`

Purpose: create a reusable, evidence-scored commercial entitlement check that can be consumed by Update Customer Notes, Run Account Summary, Tech Acct Plan, and recommendation tasks.

> **Fixture customer:** **`_TEST_CUSTOMER`** is a first-class customer name for MCP + scripts (leading underscore is valid). In zsh/bash, quote Drive paths: `scripts/rsync-gdrive-notes.sh "_TEST_CUSTOMER"`.

> **v2 (TASK-007):** `wiz_search_wiz_docs` refers to your **Wiz product-docs MCP** in Cursor (name may differ). If unavailable, mark licensing claims **provisional**. Cache upserts use **`python3 ./scripts/wiz_doc_cache_manager.py`** (ported); create `docs/ai/cache/wiz_mcp_server/` as needed or skip upserts and tell the user.

---

## Communication Rule
At every step, tell the user what you are doing in plain English. Follow the format rules in `15-user-preferences.mdc`.

## End-of-run chat format
- Follow **`.cursor/rules/15-user-preferences.mdc`**.
- After multi-step work, include **`### Activity recap`** with verified evidence updates, provisional items, and next actions.
- State whether any customer file updates were applied or deferred.

---

## 1) Preflight
1. Run `./scripts/rsync-gdrive-notes.sh` from repo root.
2. Ensure Product Intelligence freshness:
   - read `./MyNotes/Internal/AI_Insights/Product-Intelligence.md`
   - if missing or `last_updated` > 7 days, run `Load Product Intelligence` first.
3. Load Wiz doc cache baseline:
   - `./docs/ai/cache/wiz_mcp_server/manifest.json`
   - `./docs/ai/cache/wiz_mcp_server/win_apis_doc_index.json`

## 2) Sources to Ingest
1. `./MyNotes/Customers/[CustomerName]/AI_Insights/[CustomerName]-AI-AcctSummary.md` (if exists)
2. `./MyNotes/Customers/[CustomerName]/AI_Insights/[CustomerName]-History-Ledger.md` (if exists)
3. latest transcript chunk in `./MyNotes/Customers/[CustomerName]/Transcripts/`
4. `./MyNotes/Customers/[CustomerName]/[CustomerName] Notes.md`
5. relevant tech acct plan files in `./MyNotes/Customers/[CustomerName]/AI_Insights/`

## 3) Verification Sequence (Mandatory)
1. Query Wiz docs first via MCP docs tool (`wiz_search_wiz_docs`) to validate current licensing/entitlement model.
   - Use customer-specific terms first (SKU names, feature names, integrations, deployment models) from the latest sources.
2. Immediately after targeted MCP retrieval, load relevant local cache docs from:
   - `./docs/ai/cache/wiz_mcp_server/docs/`
   - Use these to cross-check SKU mapping and entitlement assumptions.
3. Update cache metadata for every queried doc/url via:
   - `python3 ./scripts/wiz_doc_cache_manager.py upsert-doc ...`
   - `python3 ./scripts/wiz_doc_cache_manager.py upsert-url ...`
4. Apply customer evidence hierarchy to each SKU:
   - **Definitive**: order/renewal/explicit entitlement evidence
   - **Strong**: feature evidence requiring add-on entitlement
   - **Indicative**: operational usage signal(s)
   - **Unknown**: no reliable evidence
5. Never infer entitlement from a single usage signal.
6. Enforce SKU-first evaluation in outputs:
   - Primary SKUs: `Wiz Cloud`, `Wiz Defend & Sensor`, `Wiz Code`.
   - Map capability-level evidence beneath these SKUs; do not create capability-level purchased product assertions without definitive commercial evidence.

## 4) Required Outputs (In-Memory + Propagation)
1. Produce the license evidence check result in-memory for the current run:
   - `Last Updated` date
   - Wiz-doc links used for verification
   - SKU-by-SKU matrix:
     - `SKU`
     - `Commercial Status`
     - `Workloads`
     - `Evidence Quality`
     - `Evidence`
     - `Data Gaps`
     - `Action`
   - correction log:
     - what changed vs prior summary/ledger
     - what remains provisional
2. Do not create a standalone `[CustomerName]-License-Evidence-Check.md` file.
3. If summary/ledger values conflict with the in-memory check result, update:
   - `[CustomerName]-AI-AcctSummary.md` `Wiz Commercials`
   - `[CustomerName]-History-Ledger.md` license columns

## 5) Sync
- Mirror updated summary/ledger files to:
  - `$GDRIVE_BASE_PATH/Customers/[CustomerName]/AI_Insights/`

# Changing the customer Notes Google Doc template (v2)

v2 **does not** ship `run-main-task.py` or Python “section builder” modules in this repo. The Docs API client is **`prestonotes_gdoc/update-gdoc-customer-notes.py`**; it reads **YAML** under **`prestonotes_gdoc/config/`** (`doc-schema.yaml`, `config/sections/*.yaml`, `section-sequence.yaml`).

## When you add or change a section

1. Edit **`prestonotes_gdoc/config/doc-schema.yaml`** and the matching **`config/sections/*.yaml`** policy for that section.
2. Align **`prestonotes_gdoc/config/section-sequence.yaml`** with load order.
3. Update prompts under **`prestonotes_gdoc/config/prompts/`** if the model needs new boundaries (MCP resources `prestonotes://prompts/*` may mirror these files).
4. Validate with **`read_doc`** (parse/structure) and, when write tools exist, **`write_doc`** with **`dry_run=true`** before applying.

## Mutations

Approved changes are expressed as **mutation JSON** and applied through MCP **`write_doc`** (TASK-003+), not an in-repo pipeline runner.

## Legacy v1 reference

The old LLM-first pipeline (`run-main-task.py`, `sections/*_section.py`, long “CreateNewSection” prompts) remains readable under **`../prestoNotes.orig/custom-notes-agent/`** for history only — it is **not** part of the v2 runtime layout.

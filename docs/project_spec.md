# PrestoNotes v2.0: Project Specification

## 1. Project Overview & Philosophy
PrestoNotes is a "Solution Engineering as Code" engine. It autonomously transforms raw customer interactions (transcripts, meeting notes) into highly structured, verifiable account intelligence (Exec Summaries, technical recommendations, and GDoc trackers).

**Core Architectural Directives:**
* **State is Code**: The LLM does not perform math, date tracking, or raw string formatting for external documents. Python handles all deterministic file operations and API writes.
* **Context is Modular**: Brute-force loading of historical transcripts is strictly forbidden to prevent context window bloat. The AI only reads the Account Summary, the History Ledger, and specifically selected recent transcripts.
* **Parallel Orchestration**: Heavy analysis is split across specialized domain advisors (SOC, APP, VULN, ASM, AI) that run concurrently in Cursor.
* **Retrieval is RAG-Based**: Large product documentation is indexed into a local vector database, enabling precise tool-based retrieval rather than context-window flooding.

## 2. MVP Objectives
* **Generate the Detailed Account Summary**: Autonomously build a highly structured Markdown report (matching the Dayforce account template) using verified quotes, timeline tracking, and discrepancy auditing.
* **Update Customer Notes (Google Docs)**: Surgically update the Exec Account Summary, Daily Activity Logs, and Account Metadata tabs without hallucinating past events.

## 3. Directory Structure
PrestoNotes v2.0 is a greenfield repository. Legacy code from `../prestoNotes` is used strictly as a read-only reference library.

```text
prestonotes/
├── .cursor/
│   ├── agents/                # DEV AGENTS (planner, coder, qa, doc)
│   ├── rules/                 # APP PERSONAS & execution rules (*.mdc)
│   └── skills/                # Dev pipeline scripts (lint.sh, test.sh)
├── docs/
│   ├── project_spec.md        # Master architectural specification (this file)
│   └── tasks/                 # Ephemeral dev task files for tracking work
├── prestonotes_mcp/           # Python environment for deterministic logic
│   ├── tools/                 # Python scripts for gdoc, ledger, and rag
│   ├── ingestion/             # Scripts for pulling/migrating legacy Wiz docs
│   └── .vector_db/            # ChromaDB local storage (git-ignored)
├── MyNotes/                   # Local customer data directory (git-ignored)
├── pyproject.toml             # uv package manager config
└── .gitignore

## 4. Phase 1: The "Dumb" Python MCP Layer
Python handles all file I/O, deterministic math, image processing, and API writes. No LLM reasoning logic lives here.

Vision & Processing: read_diagram_base64 accepts a file path to an architecture diagram, converts the image into a Base64 string, and passes it back to Cursor.

State Management: write_call_record, write_gdoc_tabs, and update_ledger handle JSON formatting, GDoc authentication, and date math.

Knowledge & Local RAG: build_vector_db.py parses legacy tier manifests and ingests them into ChromaDB. wiz_knowledge_search exposes this to Cursor as an MCP tool.

## 5. Phase 2: Sub-Agent Personas (.cursor/rules/)
These .mdc rules define the strict boundaries, contexts, and tools for the application runtime.

100-planner.mdc: The UI Agent. Reads baseline context, delegates to Extractor/Advisors, builds final JSON payload.

101-extractor.mdc: Mines facts, extracts verbatim quotes, sentiment shifts, challenges. Returns strict JSON.

102-summary_builder.mdc: Compiles the Dayforce-style narrative. Tracks discrepancies, applies evidence tags.

200-level-advisors (SOC, APP, VULN, AI, ASM): Look up gaps using wiz_knowledge_search MCP only. Generates technical recommendations mapped to Wiz.

## 6. Phase 3: MVP Execution Flows
Flow A: Generate Detailed Account Summary

User Triggers: "Run Account Summary for [CustomerName]."

Orchestrator/Planner -> Extractor -> Advisors (Parallel) -> Summary Builder -> Outputs local Markdown file.

Flow B: Update Customer Notes (GDoc & Ledger)

User Triggers: "Update Customer Notes for [CustomerName]."

Orchestrator/Planner formats GDoc_Update.json payload based on Extractor/Advisor outputs.

Orchestrator/Planner presents planned updates for human approval.

Execution: Invokes write_gdoc_tabs and update_ledger MCP tools.

## 7. Legacy Referencing Rules
Rule 1: NEVER copy monolithic .md playbooks into the new repository. We are migrating to .mdc rules.

Rule 2: Reference legacy Python scripts strictly to extract API auth and FastMCP logic, but strip out any LLM prompts or complex reasoning before porting.

## 8. Development Workflow & Agentic SDLC
To build and extend PrestoNotes v2.0, all development must strictly follow our 4-phase parent/child Agentic workflow:

Phase 1 (Spec): The @planner reads this spec, creates an ephemeral task file in docs/tasks/<task>.md, and explicitly requests user approval.

Phase 2 (Code): Once approved, @planner delegates to @coder. Coder MUST follow Test-Driven Development (TDD), writing tests before implementation.

Phase 3 (Verify & Doc): Once code is complete, @planner launches @qa and @doc in parallel to run test scripts and update README.md.

Phase 4 (Commit): Pipeline halts if QA fails after 3 attempts. Only when both QA and Doc report success is the feature ready for commit.

## 9. Tech Stack & Quality Standards
Python: Managed exclusively via uv. No pip or conda.

Testing: pytest for all Python logic.

Linting & Formatting: ruff for Python. biome for any JavaScript.

Definition of Done: A dev task is only complete when the target feature is implemented, covered by a passing test case, passes all linters, and has its ephemeral task file marked as [x] COMPLETE.
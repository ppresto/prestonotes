# TASK-032 — Follow-ups, gaps, and recommendations

**Status:** [ ] OPEN (backlog)  
**Legacy Reference:** `docs/tasks/INDEX.md`; `docs/project_spec.md` §9 TASK-020–022.

## Related MVP tracking

- **`TASK-034`** — Five MVP flows (bootstrap, PI, context, AI summary, UCN) — single readiness matrix.

## Open from spec (Stage 4)

- [ ] **TASK-020** — Harden vector DB tests per spec (`test_vector_db.py` naming / coverage).
- [ ] **TASK-021** — `wiz_knowledge_search` tool polish (max_results, error hints) if gaps remain after ingest.
- [ ] **TASK-022** — Domain advisors: prefer `wiz_knowledge_search` when Chroma populated; fallback to wiz-local search.

## Wiz cache / MCP enhancements

- [ ] Optional: **diff** MCP snapshot vs static `docs/*.md` in playbooks when both exist.
- [ ] Rate-limit telemetry: log GraphQL 429 / backoff in `materialize_wiz_mcp_docs.py`.
- [ ] CI: mock-only tests already run; optional nightly job (self-hosted) with `WIZ_*` for live smoke.

## Cleanup

- [ ] Archive TASK-028, TASK-029, TASK-031 to `docs/tasks/archive/2026-04/` when housekeeping policy applies (INDEX links remain to archive).

## Output / Evidence

Track completions in this file and in `docs/tasks/INDEX.md`.

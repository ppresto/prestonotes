# Customer Notes — Account Metadata tab (mutations)

> Part of the **Customer Notes** Google Doc mutation reference pack. Hub: [README.md](./README.md).

The **Account Metadata** tab maps to `section_key` **`account_motion_metadata`** in `prestonotes_gdoc/config/doc-schema.yaml` (`exec_buyer`, `champion`, `technical_owner`, `sensor_coverage_pct`, `critical_issues_open`, `mttr_days`, `monthly_reporting_hours`).

## Controlled fields (from fact extraction)

- `stakeholders`: `exec_buyer`, `champion`, `technical_owner`
- `outcome_metrics`: `sensor_coverage_pct`, `critical_issues_open`, `mttr_days`, `monthly_reporting_hours`

## Strict write rules

- Only set controlled values listed in schema / playbook.
- **`exec_buyer`**, **`champion`**, and **`technical_owner`** must only be updated when **explicitly stated** in that day's source evidence (`explicit_statement=true` in mutation payload). Do not infer from role or title hints.
- For numeric metrics (`sensor_coverage_pct`, `critical_issues_open`, `mttr_days`, `monthly_reporting_hours`), only populate when transcripts state the number **verbatim**; otherwise skip with an explicit skip reason (see `.cursor/rules/21-extractor.mdc` § Per-section GDoc extraction).

## Related

- Fact-extraction categories for metadata also appear under **Account motion** in [mutations-account-summary-tab.md](./mutations-account-summary-tab.md#fact-extraction-categories) (same corpus; different tab in the Doc).

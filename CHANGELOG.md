# Changelog

All notable changes to `dqar-contracts` are documented here.

## [1.1.0] - 2026-06-22

### Added

- `dqar_contracts.measures.MeasureSQLLoader` — loads `MeasureSpec` from
  contracts-packaged JSON artifacts; consumers load from contracts, never hardcode SQL
- `dqar_contracts.measures.MeasureNotFoundError` — raised when no artifact exists
  for the requested `(measure_id, measurement_period)` pair
- `dqar_contracts.shared.Engagement` — DQAR engagement context (Pydantic model)
- `dqar_contracts.shared.MeasurementPeriod` — enum of supported measurement periods
- `dqar_contracts.shared.OrganizationRef` — health plan / organization reference
- `dqar_contracts.shared.MeasureId` — stable measure identifier (Pydantic model)
- `dqar_contracts.shared.MeasureSpec` — measure's executable spec including SQL and ViewDefinition refs
- `dqar_contracts.shared.ViewDefinitionRef` — SQL-on-FHIR ViewDefinition reference
- Packaged measure-SQL artifact directory `measures/sql/` (seed: `MY2026/CIS-E.json`)
- `pydantic>=2.0` dependency

## [1.0.0] - 2026-06-15

Initial release.

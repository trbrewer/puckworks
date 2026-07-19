# Experimental campaign catalog — schema

`experimental_campaigns.yml` is the machine-readable list of the measurements Puckworks needs. It is
validated by `python tools/experimental_data_needs.py verify` against the live registry (components,
gates), the quantity ontology (`puckworks.product.quantity_semantics`), and the structured
measurement-agenda blockers.

## Top-level

- `schema_version` — integer.
- `evidence_levels` — the finite evidence vocabulary (`protocol_only`, `feasibility_pilot`,
  `controlled_replicated`, `holdout_independent`, `cross_condition_replication`).
- `campaigns` — a list, ordered by `campaign_id` (`EXP-NNN`), each with the fields below.
- `deferred_blockers` (optional) — measurement-agenda blocker IDs deliberately not yet mapped to a
  campaign (must be explicit; the verifier fails on an unmapped, non-deferred blocker).

## Required per-campaign fields

- `campaign_id` — `EXP-NNN` (unique, sorted).
- `title`, `status`, `priority`.
- `scientific_question` — the question the data answers.
- `decision_enabled` — the model / gate / adapter decision it unblocks.
- `target_components` — registered component IDs (validated).
- `target_gates` — real gate function names (validated). A campaign must name at least one component or
  gate.
- `quantity_definitions` — quantity IDs from `quantity_semantics` (validated).
- `required_observables` — list of `{name, unit, reference_basis}`; `unit` from the finite unit
  vocabulary.
- `required_metadata` — list.
- `current_evidence` — an evidence level.
- `evidence_gap`, `evidence_ceiling`.
- `measurement_agenda_blockers` — `quantity_semantics.measurement_agenda()` blocker IDs this campaign
  would resolve (every real blocker must be mapped here or deferred).
- `related_issues` — `#NNN` references.
- `code_rights_expectation`, `data_rights_expectation`, `output_rights_expectation`.
- `data_license_status`, `submission_instructions`.

## Optional design/instrument fields

`prescribed_vs_measured`, `design_factors`, `controls`, `replication_design_status`,
`instrument_requirements`, `calibration_requirements`, `synchronization_requirements`, `raw_file_schema`,
`processed_file_schema`, `uncertainty_requirements`, `quality_control_checks`, `preregistered_analysis`,
`acceptance_calculation`, `holdout_requirement`, `recommended_repository`.

## No invented values

Where a sample size, sampling rate, sensor tolerance, or acceptance threshold is unknown, record one of
`DESIGN_CALCULATION_REQUIRED`, `SENSOR_SELECTION_REQUIRED`, `PILOT_REQUIRED` (and explain what analysis
would set it). No measured value is presented as data. No wall-clock field and no private absolute path
may appear (the verifier rejects both).

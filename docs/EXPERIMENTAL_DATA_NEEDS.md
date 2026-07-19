# Experimental data Puckworks needs

Puckworks turns espresso papers into typed components and checks them with validation gates. To move a
model from *reproduced* to *independently validated* — and to unlock new adapters honestly — we need
**more measurements**. This page describes what to collect, how to collect it, and which scientific
decision each dataset would enable. Its audience is maintainers, academic collaborators, espresso
researchers, machine/grinder manufacturers, and technically capable community contributors.

The machine-readable catalog is [`data_requests/experimental_campaigns.yml`](data_requests/experimental_campaigns.yml)
(schema: [`experimental_campaign_schema.md`](data_requests/experimental_campaign_schema.md)); validate it
with `python tools/experimental_data_needs.py verify`. Executable protocol + submission templates live in
[`data_requests/templates/`](data_requests/templates/).

## 1. Why more measurements are needed

Most Puckworks components today are *reproductions* of a single paper's own data, or *calibrations*.
That is enough to check the code and reconstruct the source curve, but it is **not** independent
validation, and it cannot tell us whether a model transfers to a different machine, grinder, or coffee.
Each campaign below names the exact model, gate, or adapter decision the data would unblock.

## 2. Evidence levels

- **protocol only** — a documented plan; no data.
- **feasibility / pilot** — a small dataset that shows the measurement is possible and informs the design.
- **controlled replicated** — a designed, replicated dataset with recorded uncertainty.
- **holdout independent** — data predeclared as a holdout, never used for fitting.
- **cross-condition replication** — replication across machines, grinders, and coffees.

## 3. What each kind of data does (and does not) establish

- **Fitting / calibration** tunes parameters; it is *not* validation.
- **Code verification** shows the implementation matches the paper; it is *not* validation of the physics.
- **Reconstruction** reproduces the authors' own curve; it does *not* generalize.
- **Independent validation** compares predictions to *independent* observations.
- **Mechanism discrimination** distinguishes competing explanations.
- **Transfer / generalization** measures how far a validated result carries to new conditions.

A dataset advances exactly one of these — the campaign records which.

## 4. Current priority campaigns

The table below is generated from the catalog (do not hand-edit between the markers).

<!-- BEGIN GENERATED CAMPAIGN TABLE -->
| Campaign | Priority | Decision enabled | Target components | Evidence | Blockers mapped |
|---|---|---|---|---|---|
| **EXP-001** Synchronized whole-shot telemetry and cup chemistry | 1 | validation of cameron2020.extraction_bdf against independent whole-shot observations | `cameron2020.extraction_bdf` | feasibility_pilot | — |
| **EXP-002** Initially dry puck infiltration and physical first drip | 1 | validation of foster2025.infiltration; clean-room inputs for the future | `foster2025.infiltration` | feasibility_pilot | — |
| **EXP-003** Grinder-specific particle-size, packing, and permeability map | 1 | validation of wadsworth2026 grind/permeability; defensible per-grinder input adapters (e.g. the EK43-dial input needed by pannusch2024.solver) | `wadsworth2026.permeability`, `wadsworth2026.grindmap` | controlled_replicated | `pannusch2024.solver#1` |
| **EXP-004** Poroelastic deformation, pressure, and flow | 2 | independent test of waszkiewicz2025.poroelastic coupling | `waszkiewicz2025.poroelastic` | feasibility_pilot | — |
| **EXP-005** Time-dependent bed-mechanism discrimination (kappa(t)) | 2 | mechanism discrimination for the coupled-bed / swelling components | `mo2023_2.swelling`, `brewer2026.coupled_kappa_t` | protocol_only | — |
| **EXP-006** Species-resolved fractional extraction | 1 | validation of pannusch2024 / romancorrochano2017 / native chemistry; enables a per-species input mapping for pannusch2024.solver | `pannusch2024.solver`, `romancorrochano2017.extraction` | feasibility_pilot | `pannusch2024.solver#0` |
| **EXP-007** Spatial flow/channeling and local extraction | 2 | test bed heterogeneity for brewer2026.streamtube and the bed-cell inventory boundary that mo2023_2.coupled_bed requires | `brewer2026.streamtube`, `mo2023_2.coupled_bed` | feasibility_pilot | `mo2023_2.coupled_bed#0` |
| **EXP-008** Cross-machine, cross-grinder, cross-coffee replication | 2 | transfer/generalization limits; prevents single-rig validation becoming a universal claim | `cameron2020.extraction_bdf` | protocol_only | — |
<!-- END GENERATED CAMPAIGN TABLE -->

Priority-1 campaigns (EXP-001, EXP-002, EXP-003, EXP-006) unblock the most decisions; the others extend
coverage and transfer.

## 5. How to collect and document data

Collect **raw, instrument-native** files and never overwrite or smooth them. Record a monotonic elapsed
time base separately from any wall-clock timezone. Preserve every replicate and every excluded run with
its reason. Distinguish clearly between *prescribed* and *measured* quantities (e.g. prescribed pressure
vs measured pressure, target beverage mass vs achieved). Keep calibration records. See the protocol packs
and the raw-data principles in [`data_requests/templates/`](data_requests/templates/).

Puckworks will **not** invent a value it does not have: where a sample size, sampling rate, sensor
tolerance, or acceptance threshold is unknown, a campaign records `DESIGN_CALCULATION_REQUIRED`,
`SENSOR_SELECTION_REQUIRED`, or `PILOT_REQUIRED`, and explains what analysis would set it.

## 6. How to submit data

1. Open an **Experimental data proposal** issue *before* collecting or uploading large files.
2. Confirm the scientific question, fields + units, rights, privacy, and expected evidence level.
3. Collect raw data without overwriting or smoothing it; preserve replicates and exclusions.
4. Deposit large raw data in a stable external repository (Zenodo / OSF) with a DOI where possible.
5. Submit to Puckworks: metadata, a data dictionary, checksums, a licence, calibration records,
   uncertainty, analysis code, and the external DOI/link — not the raw bulk files.
6. Maintainers update `puckworks/data/MANIFEST.csv` **only after acceptance**.
7. Validate mechanically.
8. A gate is added in a **separate** scientific PR.
9. A data submission **never** auto-authorizes a model implementation or an evidence upgrade.

Use the [experimental-data submission issue form](../.github/ISSUE_TEMPLATE/experimental-data-submission.yml).

## 7. Rights, privacy, and redistribution

Only data whose redistribution the contributor can grant may be accepted. Recommended licences are
**CC BY 4.0** or **CC0**, but these are not mandatory when a contributor cannot grant them — in that case
the data can still inform a private analysis without being committed. No private, personally identifying,
or unlicensed third-party data may be committed to this repository.

## 8. How accepted data become model gates

Accepted, licensed data are recorded in the manifest, then a **separate** scientific PR wires a validation
gate. The gate — not the raw submission — is what a status promotion depends on (see `docs/ROADMAP.md`
§7.1). Reconstruction, calibration, and independent validation are labelled distinctly and never
conflated.

## 9. What Puckworks will not infer from an insufficient dataset

- a universal grinder-dial → particle-size mapping;
- an absolute yield from a relative trend;
- a cross-model winner, average, or ratio on incompatible quantities;
- validation from model agreement;
- a transfer claim beyond the conditions actually sampled;
- a missing value treated as zero.

# Proposed `BLOCKED_INTAKE.md` status update

Prepared 2026-07-12 after requirement verification and source search.

## Tier 1

### G1 — coffee-bed water-retention curve θ(ψ) + K_r

**Status: OPEN EXPERIMENT / AUTHOR SEARCH — no qualifying public curve located.**

A 2025 time-resolved infiltration study was checked and explicitly remains a sharp-front,
binary wet/dry model. It states that continuous saturation requires coffee-bed
permeability–saturation and capillary-pressure–saturation data. The measurement schema,
protocol and request template are in this sourcing bundle.

### G3 — measured pump characteristic

**Status: OPEN REQUEST / BENCH MEASUREMENT — no public DE1 Q(P) curve located.**

Official Decent material documents a firmware pump model and voltage/frequency-dependent scalar
flow calibration, not paired pressure–flow bench data. A measurement schema, bench protocol and
request template are in this bundle.

### G10 — coffee-liquor rheology

**Status: PARTIALLY SOURCED.**

Khomyakov et al. (2020), CC BY 3.0, supplies measured kinematic viscosity and published
dynamic-viscosity regression coefficients for 15–70 wt% dry solids at 20–80 °C. Those tables
are transcribed in this bundle. The regression is quarantined because literal evaluation of
the printed equation does not reproduce the measured-table trend. Do not mark G10 resolved because:

- espresso-relevant concentrations below 15 wt% are uncovered;
- the printed density equation contradicts the paper's stated temperature trend;
- the printed viscosity equation/temperature convention is internally inconsistent with Table 1;
- the material is industrial coffee extract rather than a dedicated espresso-liquor series.

Next targets: Telis-Romero 2000/2001 full data and author clarification of the density sign.

### G2 — transient-discharge validation

**Status: SOURCE LOCATED; RAW DATA / DIGITIZATION PENDING.**

The Ellero & Navarini 2019 paper and an open conference version provide the forcing sequence,
dimensionless-to-SI time scale and an experimental overlay. The original point series is not
published in machine-readable form. Ask authors/ASIC/illy for the 1993/1997 series; digitize the
2019 overlay in parallel with an explicit `figure_digitized` label.

### 0.6 — Wadsworth PSD archive

**Status: PENDING AUTHORS / PUBLISHER.**

An institutional copy of the article is public, but the 22-sample R/R_min/R_max archive is not
discoverable in a persistent repository. Send the included follow-up requesting a direct ZIP or DOI.

## Tier 2

### 0.8 — Bruno 2026 Table 2

**Status: ✅ RESOLVED FOR INTAKE.**

`bruno2026_roasted_composition.csv` contains the exact 4 × 10 Table 2 values, with mean, SD,
units, species, roast profile, n=3, source DOI and CC BY 4.0 attribution.

Repository work remaining: copy to `puckworks/data/`, add a loader/smoke test and MANIFEST row.

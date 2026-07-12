# BLOCKED_INTAKE sourcing review

**Repository reviewed:** [https://github.com/trbrewer/puckworks/blob/main/puckworks/data/BLOCKED_INTAKE.md](https://github.com/trbrewer/puckworks/blob/main/puckworks/data/BLOCKED_INTAKE.md)  
**Search date:** 2026-07-12  
**Scope:** verify each listed data requirement, identify qualifying primary sources, transcribe
legally reusable tables where possible, and provide acquisition instruments for true gaps.

## Executive decision table

| Item | Verified requirement | Current result | Sprint impact |
|---|---|---|---|
| **0.8 Bruno Table 2** | Four roasted origins × ten compounds, mean ± SD and units | **Fully sourced and transcribed** | Ready for repo intake now |
| **G10 rheology** | Coffee-extract viscosity and density versus solids/TDS and temperature | **Partially sourced**: measured kinematic-viscosity grid; density and printed dynamic-viscosity regression quarantined | Provides a source table, but does not yet supply a production closure |
| **G2 transient discharge** | Historical direct/inverse-discharge evidence or Ellero/Navarini data | **Primary source located**; protocol and experimental overlay found, raw points absent | Ready for author request and figure digitization |
| **0.6 Wadsworth PSD** | R/R_min/R_max arrays for two coffees × eleven grinds | **Article and institutional record located; ZIP still absent** | Remains author/publisher dependent |
| **G3 pump curve** | Measured paired pressure–flow characteristic, DE1 preferred | **No qualifying public curve found** | Requires DE1 engineering data or a bench sweep |
| **G1 retention/K_r** | Saturation-resolved θ(ψ) and K_r, or fitted VG/BC parameters in real units | **No qualifying coffee-bed dataset found** | Requires a targeted experiment or unpublished group data |

## Requirement verification

### G1 — coffee-bed retention and relative permeability

The repository requirement is correctly specified. Richards' equation needs two constitutive
closures: θ(ψ) or S_e(ψ), and K_r(S_e) or K_r(ψ). A front-position trace h(t) does not identify
the saturation profile behind the front and therefore cannot close the model.

The closest recent coffee-specific source checked—*Dynamics of liquid infiltration into an
espresso coffee bed*—uses time-resolved CT but deliberately adopts a binary saturated/dry,
sharp-front model. The authors explicitly state that continuous saturation would require
permeability–saturation and capillary-pressure–saturation data. That confirms the repository's
negative filter rather than filling the gap.

**Decision:** G1 remains a real experimental gap. The bundle includes a strict CSV schema,
minimum experiment and author-request message. Do not accept sorption isotherms versus water
activity, total water-holding capacity, or front position alone as substitutes.

### G3 — measured pump characteristic

The requirement also stands. Official Decent documentation says DE1 firmware estimates flow
from a pump physics model and applies a flow-calibration adjustment because pump behavior depends
on mains voltage and frequency. The app's graphical calibrator aligns scale-derived flow with
pump-estimated flow. These materials verify the existence of a model and scalar calibration;
they do not publish the paired measured Q(P) surface needed by RC-3.

The public DE1app source likewise exposes flow-calibration variables rather than an engineering
bench table.

**Decision:** no qualifying public DE1 pump curve was found. Use the included pressure-sweep
protocol or send the prepared request to Decent. Voltage, frequency, hardware revision, water
temperature, pressure node and pump command must be recorded.

### G10 — coffee-liquor viscosity and density

Khomyakov et al. (2020) is an open source for part of this gap. It reports measured kinematic
viscosity across 15–70 wt% dry solids and 20–80 °C, plus printed dynamic-viscosity power-law
coefficients. The exact tables are included, but the regression is not ready for use.

However, it does not fully meet the repository's likely espresso-use domain:

- the lowest solids fraction is 15 wt%, so lower-TDS beverage conditions are outside the data;
- the samples are industrial coffee extract;
- the density equation is internally inconsistent: the prose says density decreases with
  temperature while the printed `+0.8 T` term makes it increase;
- the authors describe the viscosity regressions as approximate;
- literal evaluation of the printed viscosity equation with T in °C does not reproduce values
  implied by the measured table, so its convention or typesetting must be clarified.

The older Telis-Romero papers are stronger acquisition targets because their reported domains
extend to 10 wt% solids and up to 82–92 °C.

**Decision:** mark G10 `PARTIALLY SOURCED`. Preserve the measured kinematic-viscosity table as
source data, but do not silently extrapolate below 15 wt% and do not promote either the density
or dynamic-viscosity equation until both source conflicts are clarified.

### G2 — transient-discharge validation

The named 2019 Ellero & Navarini source was verified. An open conference version includes the
direct/inverse forcing schedule, the conversion τ_v = 0.16 s for the experiment, and a plotted
experimental comparison. It identifies the relevant ASIC lineage and demonstrates exactly why
the data are useful for mobile-fines dynamics.

The source is not a raw-data release. The experimental points are embedded in a figure and the
historical ASIC proceedings remain difficult to obtain.

**Decision:** G2 is no longer a blind literature search; it is a defined acquisition/digitization
task. Request the raw series from Ellero/Navarini/illy/ASIC, while digitizing the plotted overlay
as a labeled fallback. Do not call the digitized points raw data.

### 0.6 — Wadsworth 22-sample PSD archive

The 2026 article and an institutional repository record are public and confirm two coffees at
eleven grind settings. The publisher advertises supplementary material, but no persistent
figshare/Dryad/Zenodo archive or directly retrievable ZIP was found. The ledger's author-contact
status is therefore accurate.

**Decision:** remains blocked on delivery. The included follow-up asks for either a direct ZIP
or data DOI and names the exact arrays required.

### 0.8 — Bruno 2026 roasted chemistry

The open Scientific Reports paper states that Table 2 contains final roasted compositions for
Mexico and Rwanda Arabica plus Nicaragua and Indonesia Robusta, reported as mean ± SD over three
measurements. Non-lipid analytes are mg/kg roasted coffee powder; lipids are dry-basis % w/w.

**Decision:** fully unblocked. The bundle contains exact long- and wide-format transcriptions
under CC BY 4.0. Copy the long file to the intended repository path, add the MANIFEST row and
write a loader smoke test.

## Files supplied

### Ready for repository intake

- `bruno2026_roasted_composition.csv`
- `bruno2026_roasted_composition_wide.csv`
- `khomyakov2020_kinematic_viscosity.csv` — source table only, with a 15–70 wt% domain guard

### Quarantined source transcriptions and diagnostics

- `khomyakov2020_dynamic_viscosity_regression.csv`
- `khomyakov2020_regression_consistency_FLAGGED.csv`
- `khomyakov2020_density_equation_FLAGGED.csv`

The three files above preserve source information but are not production closures.

### Acquisition support

- `g1_retention_measurement_template.csv`
- `G1_EXPERIMENT_PROTOCOL.md`
- `G1_DATA_REQUEST_EMAIL.md`
- `g3_de1_pump_curve_template.csv`
- `G3_BENCH_PROTOCOL.md`
- `G3_DATA_REQUEST_EMAIL.md`
- `g2_transient_discharge_digitization_template.csv`
- `G2_TRANSIENT_DISCHARGE_SOURCE_NOTES.md`
- `WADSWORTH_FOLLOWUP_EMAIL.md`
- `G10_AUTHOR_CLARIFICATION_EMAIL.md`

### Tracking

- `SOURCE_MANIFEST.csv`
- `BLOCKED_INTAKE_PROPOSED_UPDATE.md`
- `TIER3_LEADS.md`

## Recommended sprint order

1. **Close 0.8 immediately:** ingest Bruno Table 2, add the manifest row, loader and smoke test.
2. **Land G10 as a bounded source table:** add the measured kinematic-viscosity grid with an
   explicit domain guard; keep both printed closure equations quarantined.
3. **Start G2 digitization and correspondence in parallel:** the source and axis schedule are now
   known.
4. **Send Wadsworth follow-up and DE1 request together:** both are low-effort correspondence.
5. **Treat G1 as an experiment-design sprint, not another generic web search.** The literature
   checked now reinforces that the constitutive measurement itself is missing.

## Primary sources

- Repository intake ledger: https://github.com/trbrewer/puckworks/blob/main/puckworks/data/BLOCKED_INTAKE.md
- G1 acceptance card: https://github.com/trbrewer/puckworks/blob/main/docs/cards/g1_retention_search_target.md
- Sprint status: https://github.com/trbrewer/puckworks/blob/main/docs/SPRINTS.md
- Bruno et al. 2026: https://www.nature.com/articles/s41598-026-43923-9
- Khomyakov et al. 2020: https://doi.org/10.1088/1755-1315/548/2/022040
- Foster et al. 2025 infiltration study: https://pubs.aip.org/aip/pof/article/37/1/013383/3332668/Dynamics-of-liquid-infiltration-into-an-espresso
- Decent flow-calibration documentation: https://decentespresso.com/blog/perfectly_calibrating_decent_flow_measurements
- Decent graphical calibrator: https://decentespresso.com/blog/whats_new_in_de1app_v145
- Ellero & Navarini open conference manuscript: https://upcommons.upc.edu/bitstreams/7992d37d-d17a-40cc-9f93-7d8e2bd8486d/download
- Ellero & Navarini JFE DOI: https://doi.org/10.1016/j.jfoodeng.2019.05.038
- Wadsworth institutional record: https://strathprints.strath.ac.uk/95930/

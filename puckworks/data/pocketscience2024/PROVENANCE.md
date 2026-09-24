# Provenance — pocketscience2024 (radially sectioned edge/center extraction yield)

## SCI-MD-RADIAL-OBS-001 source inspection correction (2026-09-24)

The historical account below is retained, with these source-verified corrections
taking precedence for new assay use. See the [executable measurement map](../../../docs/analysis/sci_md_radial_obs_001/MEASUREMENT_MAP.md)
for formulas, cell locators, units and qualified observables. The original workbook
is held through the configured external-data resolver, not in this checkout.

The [primary workflow](https://pocketsciencecoffee.com/2024/01/07/espresso-water-flow-part-0-workflow/)
reports a nominal flat 6-bar DE1 programme and compares metal screen with paper on
top. N is not a bare puck; this does not qualify true puck-inlet pressure.
The workbook has different sheet calculations: Sworks corrects recovery using
literal LRR and divides recovered solubles by inferred original section mass;
VST has no LRR correction and subtracts solubles per dried residue mass. Only
Sworks enforces the initial-mass-weighted shot-EY identity. Y54 uses unfiltered
TDS despite its filtered label. Existing rounded card means are preserved as a
comparison artifact, not corrected silently. The q constants are original-total
ratios by their formulas/headers, with raw calibration measurements unavailable;
no measured cutter radius follows.

The permission record is attribution-required use, but the actual expanded grant
text was not found in targeted source holdings/notices. New per-shot rows and
condition aggregates remain private; do not follow the old force-track suggestion
without verifying actual grant scope. `pocketscience2024/workbook_assay_reconstruction`
is a new explicitly registered external subset, not an alias for the old CSVs.
Solid depletion is not identified without retained-liquid, initial-inventory,
handling and recovery assumptions. Exact sheet-specific operational composites
remain usable. PHYSICAL_VALIDATION=NOT_ESTABLISHED.


**Card:** `docs/cards/pocketscience2024.md` (verdict: data-only; no model, no gate
against the source itself).

**Source / citation (required on any use).** Pocket Science Coffee (pseudonymous author),
"Espresso Water Flow Part 1: Dispersion, Puck Screens and Baskets," blog post, 27 Feb 2024.
<https://pocketsciencecoffee.com/2024/02/27/espresso-water-flow-part-1-dispersion-puck-screens-and-baskets/>
BibTeX key `pocketscience2024` (`docs/literature_search/references.bib`). Plots and
Monte-Carlo error analysis by Jonathan Gagné. **No DOI; not peer-reviewed.** Data used
**with the author's permission (Tim, 2026-07-13), attribution/citation required.** A destructive-sectioning
experiment on a Decent DE1 measuring edge vs. center extraction yield across dispersion
block (brass/teflon), puck screen (Y/N), basket (VST18 / Sworks High Flow), and shot
style confounded with grinder (Niche↔traditional, Superjolly MP64↔turbo).

## What is tracked here (derived, card-faithful)
- `edge_ey_condition_means.csv` — the 12-condition summary table transcribed **from the
  card** (§Parameters). Columns: basket, shot_style, grinder, puck_screen,
  dispersion_block, ey_center_pct, ey_edge_pct, edge_yield_loss_pct (fractional edge loss
  ×100, negative = edge under-extracted), shot_ey_filtered_pct, outer_mass_frac_of_dose,
  n_shots (`4-5`; 5 nominal, 3 rejects across the 60-shot campaign, excluded), provenance.
  Units: percent throughout (registry EY %); no SI conversion (dimensionless yields).
- `lrr_scalars.csv` — grinder-level liquid-retained-ratio means (Niche 3.38, Superjolly
  MP64 3.30; n=5 each), lumped post-flush retention. **NOT** an in-shot dead-water figure
  and **NOT** a retention curve θ(ψ): does not satisfy the G1 search target.

## What is NOT tracked (raw workbook)
The raw `Espresso water flow experiment.xlsx` (3 sheets, 60 shots × ~47 columns), the
per-sheet CSVs, and the source PDF are held locally under this directory but are
**gitignored** — now purely a **repo-size** choice (a 138 KB binary workbook + a 2.3 MB
PDF), not a licensing one: use is permitted with attribution (see above). The tracked
card-derived summary + citation are sufficient for the stated offline gate use. If a
per-shot transcription check or finer analysis is needed, force-track the raw sheets
(they are available locally).

## Carried corrections / caveats (from the card)
- **Column-label erratum:** the VST18 raw sheet labels its 0.31 as "outer to inner section
  ratio by mass," but the values (outer 5.56 g / dose 17.9 g = 0.31) show it is
  outer-to-**total** — the same quantity as the Sworks sheet's correctly labeled 0.34. The
  derived CSV carries the corrected meaning (`outer_mass_frac_of_dose`).
- Raw-mean edge losses here differ from Gagné's Monte-Carlo figures (e.g. worst −32% here
  vs. ~−37% combined in his Fig. 3): two readings of the same raw data (different
  resampling + scaling). The tracked table is the raw condition means.
- Section EYs are anchored to shot EY **by construction** (not independent of the beverage
  measurement); two-zone radial resolution only (no depth); single DE1; shot style
  confounded with grinder; VST18×brass cells absent (12 of 16).

## Registry use (offline only)
Validation target for any future radially resolved bed_dynamics/extraction variant
(reproduce the sign structure: large negative edge loss only for traditional basket ×
traditional shot × no screen; near-zero for modern basket + screen) and a prior-shaping
caution for `brewer2026.streamtube` σ (a grind-driven lognormal σ silently absorbs this
boundary-condition heterogeneity when calibrated on shot-level data). No contract consumes
it under v0.1 (no radial coordinate / inlet-uniformity field). **Does not close G1 or G9.**

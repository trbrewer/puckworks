# Model card: Pocket Science Coffee 2024 — radially sectioned extraction yield (dispersion, puck screens, baskets)

**Paper/thesis:** Pocket Science Coffee (pseudonymous author), "Espresso Water Flow Part 1: Dispersion, Puck Screens and Baskets," blog post, 27 Feb 2024 — <https://pocketsciencecoffee.com/2024/02/27/espresso-water-flow-part-1-dispersion-puck-screens-and-baskets/> (BibTeX key `pocketscience2024`). No DOI; not peer-reviewed. Plots and Monte-Carlo error analysis by Jonathan Gagné (credited collaborator). Raw workbook (`Espresso_water_flow_experiment.xlsx`, 3 sheets) published alongside the post and held in intake. **Data used with the author's permission (Tim, 2026-07-13); attribution/citation required on any use.**
**Stage(s):** bed_dynamics (radial extraction heterogeneity), observables (partitioned EY) · **Kind:** calibration (data source only)
**Status:** intaken 2026-07-13 (data-only; card-derived 12-condition edge/center EY summary + LRR scalars tracked with a MANIFEST row + loader + smoke test; raw workbook gitignored, not redistributed — see `puckworks/data/pocketscience2024/PROVENANCE.md`). No gate against the source (verdict: data-only).

## Scope and mechanism
Not a model. A destructive-sectioning experiment measuring **edge vs. center extraction yield** on a Decent DE1, factorial over: dispersion block (old brass vs. new teflon), puck screen (with/without), basket (VST 18 g traditional taper vs. Sworks High Flow "modern" full-coverage), and shot style confounded with grinder (Niche Zero traditional ~45 g/40 s vs. Superjolly + SSP MP64 turbo ~40 g/15 s). After each shot the spent puck is cut into a central disc and an outer annulus (outer section ≈ 31–34% of dose by mass; for a 29 mm basket radius this puts the cut at r ≈ 23.5–24 mm); each section's remaining solubles are recovered by immersion, TDS-measured, and back-computed into a per-section EY, scaled so the mass-weighted section EYs match the directly measured shot EY. 12 conditions × 5 shots (3 rejected samples). The headline mechanism probed: how evenly water is delivered to and drained from the puck controls local extraction at the perimeter.

## Governing equations
None to implement. Two registry-relevant constructions in the source, both descriptive:
1. **Yield-loss metric** (source's definition, stated in prose): fractional edge yield loss = (EY_edge − EY_center)/EY_center. Negative = edge under-extracted.
2. **Gagné radial EY profile** (Fig. 8 top): a plotting construction — quarter-ellipse stitched onto a rectangle, rectangle width tied to basket width, ellipse depth set by edge EY, sections rescaled so the area-integral matches shot EY. This is a visualization ansatz with no physics; do not register it. Any radial extraction profile model fit to this data would be a registry-side construction `[RS]`.

Section-EY bookkeeping in the workbook (dry/wet section weights, immersion TDS, LRR correction for retained liquid) is a mass-balance chain, fully reconstructible from the published columns.

## Parameters
No model parameters. Key measured quantities (condition means, computed `[RS]` from the raw per-shot workbook rows, rejects excluded; n = 4–5 per condition; teflon = new dispersion, brass = old):

| basket | shot style / grinder | screen | block | EY_center (%) | EY_edge (%) | edge loss (%) | shot EY filt. (%) | source |
|---|---|---|---|---|---|---|---|---|
| VST18 | traditional / Niche | N | teflon | 20.7 | 14.0 | −32.1 | 19.4 | measured |
| VST18 | traditional / Niche | Y | teflon | 22.1 | 18.9 | −14.5 | 21.9 | measured |
| VST18 | turbo / SJ MP64 | N | teflon | 18.7 | 19.3 | +2.8 | 20.3 | measured |
| VST18 | turbo / SJ MP64 | Y | teflon | 19.6 | 19.6 | +0.3 | 21.0 | measured |
| Sworks | traditional / Niche | N | teflon | 22.5 | 20.6 | −8.6 | 21.8 | measured |
| Sworks | traditional / Niche | Y | teflon | 23.3 | 22.9 | −1.5 | 23.2 | measured |
| Sworks | traditional / Niche | N | brass | 22.3 | 19.5 | −12.3 | 21.3 | measured |
| Sworks | traditional / Niche | Y | brass | 23.0 | 19.9 | −13.7 | 21.9 | measured |
| Sworks | turbo / SJ MP64 | N | teflon | 21.6 | 22.2 | +2.3 | 21.8 | measured |
| Sworks | turbo / SJ MP64 | Y | teflon | 21.8 | 21.8 | −0.1 | 21.8 | measured |
| Sworks | turbo / SJ MP64 | N | brass | 21.3 | 20.9 | −1.9 | 21.2 | measured |
| Sworks | turbo / SJ MP64 | Y | brass | 21.0 | 20.1 | −4.2 | 20.7 | measured |

Note these raw-mean edge losses differ somewhat from Gagné's Monte-Carlo figures (e.g., worst case −32% here vs. ~−37% combined average in Fig. 3) — his pipeline resamples with assumed measurement errors and a different scaling; treat his figure values and this table as two readings of the same raw data.

Supporting scalars:

| quantity | value | units | source |
|---|---|---|---|
| dose | 17.9–18.1 | g | measured |
| output | ~40 (turbo) / ~45 (traditional) | g | measured |
| shot duration | 13–17 (turbo) / 31–46 (traditional) | s | measured |
| outer-section mass fraction of dose | 0.31 (VST18), 0.34 (Sworks) | — | measured |
| LRR (liquid retained ratio), Niche grind | 3.38 (mean, n=5) | g water / g dose | measured, separate flush shots (~285 g water) |
| LRR, Superjolly MP64 grind | 3.30 (mean, n=5) | g water / g dose | measured, n=5 |
| Gagné MC assumed TDS error | 0.01 (uniform) | % TDS | assumed |
| Gagné MC assumed weight error | 0.1 (uniform) | g | assumed |
| basket hole geometry, puck screen spec, water temp, pressure profile | not provided | — | — |

**Column-label erratum `[RS]`:** the VST18 sheet labels its 0.31 as "outer to inner section ratio by mass," but the row values (e.g., outer 5.56 g / dose 17.9 g = 0.31) show it is outer-to-**total** — same quantity as the Sworks sheet's correctly labeled 0.34. Carry the corrected label on transcription.

## Calibration and validation offered by the source
None in the model sense — there is nothing fitted. Internal quality controls the source does provide: (i) an independent mass-balance check per shot (calculated vs. weighed remaining puck mass, typically within ±3%, worst ~9%; three shots flagged "Reject sample" where sectioning failed); (ii) duplicate TDS readings (filtered and unfiltered) per shot; (iii) Gagné's Monte-Carlo propagation of assumed TDS/weight errors into 95% CIs on the yield-loss means. No replication on a second machine, second basket specimen, or by another operator. The section-EY scaling is anchored to shot EY *by construction*, so section EYs are not independent of the beverage measurement — a deliberate choice (mass loss during transfer) the author discloses.

## Assumptions and validity range
- **Two-zone radial resolution only.** "Center" is ~66–69% of the puck mass; all sub-structure inside r ≈ 23.5 mm is averaged away. No axial (depth) resolution at all.
- **Shot style is confounded with grinder** (Niche Zero ↔ traditional, SJ MP64 ↔ turbo). "Turbo shots suffer less edge loss" cannot be separated from burr-set/PSD effects within this design.
- Single DE1 machine; findings on dispersion blocks are DE1-specific (the author says so explicitly — unknown transfer to machines with less even upstream dispersion). Single specimen of each basket; puck screen make/thickness unspecified in the captured text.
- No brass-block runs with the VST18 basket — the factorial is incomplete (12 of 16 cells).
- Immersion recovery of remaining solubles assumes the soak extracts the same soluble pool the refractometer calibrates for; retained-liquid correction uses grind-level LRR means, not per-shot values.
- LRR measured on long flush shots (~285 g water through 14 g dose), i.e., a fully saturated, post-flush lumped retention — not comparable to in-shot dead-water (foster2025 W_dead ≈ 8.8 g ≈ 0.4–0.5 g/g) and **not** a retention curve θ(ψ): it does not satisfy the G1 search target.
- n = 5 per condition with per-shot edge-loss scatter of the same order as some condition means (see Figs. 1–3 error bars); only the large effects (traditional basket + traditional shot edge loss; puck-screen mitigation) are clearly resolved.

## Interface mapping
Inputs consumed: none. Outputs produced: none under contracts v0.1 — there is no radial coordinate anywhere in BedState or ShotResultState, and no inlet-distribution field in MachineState. Uses are all offline:
- **Validation target** for any future radially resolved extension of the extraction/bed_dynamics chain (e.g., a two-zone streamtube variant with an edge zone): the 12-condition table above is the gate data.
- **Prior-shaping** for brewer2026.streamtube's σ: the data shows a machine/basket **boundary-condition** contribution to heterogeneity that a grind-driven lognormal σ silently absorbs when calibrated on shot-level data. Any σ fitted to traditional-basket DE1 shots inherits an edge deficit of order 15–30% fractional EY at the perimeter.
Coupling: offline data ingest only; nothing here should ever be runtime. No adapters; a contract extension (radial zones or inlet-uniformity descriptor) would be required before any component could consume this quantitatively.

## Extractable data
- **All three workbook sheets → `data/pocketscience2024_edgeEY.csv`**: 60 shots × ~47 columns (12 conditions; 3 rejects flagged). Raw data IS published (workbook linked from the post; held in intake) — highest-grade provenance this source can offer. Transcribe raw columns, not the derived ones, and carry the outer-fraction label correction.
- **Condition-means table** (above) → small summary CSV with n and reject notes.
- **LRR sheet** (10 flush shots, 2 grinders) → lumped retention scalars; park beside foster2025 W_dead with a units/definition caveat.
- Gagné Figs. 1–3 (yield-loss distributions with 95% CIs) and Figs. 4–8 (box-function EY profiles, shot-EY legends) are derived views of the same workbook — no digitization needed.

## Overlaps and conflicts
- **brewer2026.streamtube (complements, and cautions):** streamtube heterogeneity is grind-driven and radially unstructured; this dataset isolates a *deliberate* radial component driven by dispersion/basket boundary conditions. It is both the first candidate validation set for a radial two-zone variant and a warning that σ(φ₁) calibrated on shot data conflates the two heterogeneity sources.
- **cameron2020.extraction_bdf (complements):** quantifies the cost of the 1-D radially homogeneous assumption — negligible in the best condition (modern basket + screen + even dispersion, |edge loss| ≲ 2%) and up to −32% fractional edge EY in the worst (traditional basket, traditional shot, no screen).
- **foster2025.infiltration (complements):** sharp-front wetting assumes a uniform inlet; the traditional-basket/traditional-shot edge deficit is consistent with non-uniform inlet delivery and speaks to fine-grind-dip hypothesis #2 (incomplete wetting) — but as evidence of spatial unevenness, not as constitutive data.
- **g1_retention_search_target (does NOT satisfy):** LRR is a lumped scalar; no θ(ψ), no saturation resolution. Do not close G1 on this.
- **mckeonaloe2022 / schulman2011 basket cards + gap G9 (complements):** those sources give exit-hole *geometry*; this is the first *functional*, extraction-level measurement on file of basket hole-coverage effects (VST vs. full-coverage Sworks). It measures EY consequences, not resistance, so it informs but does not close G9.
- No competition with any registered component; nothing here models anything.

## Implementation estimate
Effort S: transcribe three sheets + condition summary with reject flags and the label erratum; no gate possible against the source itself (nothing to reproduce beyond re-deriving section EYs from raw columns, which is a worthwhile transcription check). Gate design for future use: a radially resolved bed_dynamics/extraction variant must reproduce the sign structure of the 12-condition table (large negative edge loss only for traditional basket × traditional shot × no screen; near-zero for modern basket + screen) before its edge-zone parameters are trusted. Dependencies: a radial/inlet-uniformity contract extension; basket geometry from the mckeonaloe/schulman cards if the basket effect is to be parameterized.

VERDICT: data-only — no model, hobbyist provenance, but the registry's only radially resolved extraction-yield dataset, with published raw per-shot data quantifying a boundary-driven heterogeneity source no registered component represents — effort S.

# Model card: schulman2011 — basket geometry → shot-weight response (Home-Barista basket study)

**Paper/thesis:** J. Schulman ("another_jim"), "How filter baskets affect espresso taste and barista technique," Home-Barista.com blog/forum study, August 25, 2011. No DOI; non-peer-reviewed community study (52-post thread; only page 1 of 6 available in this intake — see caveats).
**Stage(s):** flow · **Kind:** calibration
**Status:** proposed

## Scope and mechanism

Empirical study of how filter-basket exit geometry (total hole area, base diameter, hole-grid pattern, hole diameter mean and variance) controls shot weight at fixed shot time. Three parts: (1) optical measurement of hole-size distributions of 14 baskets (8 types) via pixel-counting on photographs; (2) 84 shots (6 doses × 14 baskets, one coffee/grinder/machine, fixed 25 s) regressed against dose and basket geometry with a lumped flow/dwell model; (3) a sensory scale-invariance test at fixed brew ratio 0.67. The mechanism proposed is that basket exit area is a co-controlling resistance alongside the puck itself — directly relevant to the registry's screen-resistance question. The sensory part (part 3) has no mathematical model and is carried here as observational findings only, not a separable card.

## Governing equations

The source presents one lumped model, in prose (no equation numbers exist; labels below are ours):

(S1) W_shot = Q̄ · (t_shot − t_dwell)

(S2) Q̄ ∝ H_ar / (m_dose + a)

(S3) t_dwell ∝ (m_dose + b) / H_ar

with t_shot = 25 s fixed, so the fitted regressors are H_ar/(m_dose + a) and (m_dose + b)/(m_dose + a). The author reports that different (a, b) pairs fit equally well provided a ≠ b; the final model **omits b entirely and sets a = 1** (implicitly in grams — units never stated).

Symbols:
- W_shot — beverage mass out (g)
- Q̄ — average volumetric/mass flow over the shot (units never defined; effectively a regression construct)
- t_shot — total shot time, fixed at 25 s
- t_dwell — dwell time before flow starts (pre-infiltration delay), s
- H_ar — total open hole area of the basket base (units not stated; plausibly mm², see Extractable data)
- m_dose — dry coffee dose (g)
- a, b — lumped constants; a = 1, b dropped

The proportionality constants in (S2)–(S3) are themselves modeled as functions of base diameter, grid pattern (square vs hexagonal), average hole diameter, and hole-diameter variance. **The fitted coefficient values are not reported anywhere in the available pages** — only the sign/direction of each effect (see Parameters). Nothing has been simplified away by us; the model as published is already maximally lumped.

## Parameters

| symbol | value | units | source |
|---|---|---|---|
| a (flow offset) | 1 | g (implied) | assumed by author (chosen, not fitted) |
| b (dwell offset) | omitted from final model | — | — |
| coefficient on H_ar/(m_dose+1) | not provided | — | fitted (value unpublished) |
| coefficient on base diameter | not provided (direction: smaller base → lower flow, longer dwell) | — | fitted (value unpublished) |
| coefficient on grid pattern | not provided (direction: square grid → longer dwell) | — | fitted (value unpublished) |
| coefficient on hole-size variance | not provided (direction: lower variance → lower flow, shorter dwell; author flags it may act categorically, since only VST baskets have low variance) | — | fitted (value unpublished) |
| coefficient on average hole diameter | not provided (direction: larger holes → more flow, less dwell) | — | fitted (value unpublished) |
| t_shot | 25 | s | nominal (protocol) |
| target brew ratio (part 3) | 0.67 | g/g (dose/shot) | nominal (protocol) |

The model is **not reconstructible** from the source: it is a regression whose coefficients were never published.

## Calibration and validation offered by the source

- Fit set: 84 shots, one coffee (Metropolis Red Line), one grinder, one machine, fixed 25 s, dose varied ±0.5–1 g around a per-basket center targeting brew ratio 0.67.
- Physical model explains **R² ≈ 0.76** of shot-weight variation; a categorical model (separate line per basket type) explains ≈ 0.78; per-individual-basket lines ≈ 0.82 (difference from 0.78 reported as not significant).
- **No holdout of any kind**: the R² is in-sample on the same 84 shots the coefficients were fit to. This is fit quality, not validation. Author acknowledges high noise (end-of-shot flow dominance makes shot weight sensitive to small dwell/timing differences).
- Basket-geometry measurements (part 1) are the strongest empirical element: VST hole-size standard deviations ~3× tighter than other brands, and VST hole area staggered in proportion to nominal size — a verification of manufacturer claims, independent of the flow model.
- Part 3 (taste): five baskets at scale-invariant dose (ratio 0.67 in 25 s) were indistinguishable **cold** and easily distinguished **hot** (higher dose → "punchier"/more astringent crema structure). Single-protocol informal tasting, no blind-panel methodology reported in the available pages; treat as hypothesis-level.

## Assumptions and validity range

- Single machine, coffee, grind setting, temperature; fixed 25 s shots. All coefficients confound the puck resistance of that one grind with basket resistance — the model cannot separate the two.
- Basket exit treated as the only geometry that matters; puck state (porosity, k, compaction) never enters. Silent on pressure, temperature, and profile dependence (machine ran one profile).
- Dose range ~8–18 g; brew ratio range ~0.5–1.0 (occasionally exceeded). Extrapolation outside 58 mm-top baskets unsupported.
- t_dwell conflates infiltration delay with headspace fill; no physical decomposition.
- Sensory scale-invariance claim conditioned on same coffee, grind, time, ratio; the hot-taste non-invariance is attributed to crema structure, explicitly not to extraction chemistry — untested assertion.
- Fails as a predictive component: unpublished coefficients, non-SI/undefined units, in-sample-only fit.

## Interface mapping

Inputs consumed (were it implemented): BedState.dose_kg; basket descriptors that have **no current contract home** (H_ar, base diameter, grid, hole stats) — would require a BasketState or extension of BedState.
Outputs produced: ShotResultState.beverage_g at fixed t_shot (25 s only).
Couplings: none viable at runtime. The genuine value is an **offline calibration chain**: the part-1 hole-area table supports an exit-screen resistance estimate in series with puck resistance (kappa or k_m2 priors), addressing the wadsworth2026 tamped-regime reconciliation ("phi_c ~ 0.11 **or** screen resistance"). Adapter needed: unit resolution for H_ar (see below) before any quantitative use.

## Extractable data

- **Basket geometry table (post #2)** — the asset. 12 rows visible: basket ID, base diameter, average hole size, hole-size SD, total hole area, grid pattern. Worth transcribing to `puckworks/data/schulman2011_baskets.csv` with caveats:
  - Units never stated. Plausible reading: base diameter in 0.1 mm (310 → 31.0 mm; VST 494 → 49.4 mm vs 58 mm top), hole mean/SD in µm, H_ar in mm². Must be sanity-checked (e.g., VST published specs) before use — tag any resolution `[RS]`.
  - Column caption says grid is coded hexagonal = 0 / square = 1, but the data column contains letters `s`/`h` — internal inconsistency, flagged.
  - Text says 14 baskets; only 12 rows are visible (Faema singles pair apparently truncated in the scrollable block). Full-thread fetch needed for the missing rows.
- Hole-size distribution figure (densities for VST 15/18/22 vs other doubles) — qualitative; transcription optional.
- Raw 84-shot dose/shot-weight data: shown only as figures ("Brew Ratio to Dose of Fourteen Baskets"); point-level data not published, no code/data release. Digitization possible but low value given the confounds.
- Equivalent-dose anchor (post #10): at this grind, ratio-0.67-in-25-s doses are 14–15 g in conventional doubles vs 17 g in VST18/Strada — a useful single calibration anchor.

## Overlaps and conflicts

- **Backlog: screen resistance (wadsworth2026.permeability reconciliation).** Direct complement. This is the only source in-registry with per-basket total exit hole area — the missing geometric input for a series-resistance term. That, not the regression, is why this card exists.
- **foster2025.infiltration:** t_dwell here is a crude empirical cousin of Foster's first-drip time (6.4–7.8 s predicted vs 7.0 s observed). Foster supersedes it physically; Schulman's dwell adds nothing runtime-usable but its dose-dependence direction (larger dose → longer dwell) is a qualitative consistency check.
- **cameron2020.extraction_bdf / observables backlog:** the hot-vs-cold scale-invariance finding suggests crema/serving-scale effects live outside extraction chemistry — supports keeping sensory kernels in observables rather than complicating extraction. Hypothesis-level only.
- **brewer2026.streamtube:** no overlap; basket exit is downstream of bed heterogeneity. Competes with nothing; supersedes nothing.

## Implementation estimate

No implementation of the regression (coefficients unpublished, confounded, in-sample). Work item is data intake + one derived quantity: transcribe the basket table, resolve units against published VST specs, fetch remaining thread pages for the missing Faema-single rows and any later corrections, and compute an order-of-magnitude exit-orifice resistance per basket for the G-series screen-resistance gate. Effort S; no dependencies; gate = does adding the derived screen resistance move the Wadsworth tamped-regime reconciliation away from the implausible phi_c ~ 0.11.

VERDICT: data-only — the regression is unrecoverable and confounded, but the basket hole-geometry table is the registry's only quantitative input for the open screen-resistance question — effort S.

# Model card: McKeon Aloe 2021 pre-wetting capillary imbibition

**Paper/thesis:** R. McKeon Aloe, "Espresso Pre-wetting as Opposed to Pre-infusion: Residuals of a transparent portafilter experiment on pre-infusion," Medium (TDS Archive / Coffee Data Science), Jan 18, 2021. No DOI; blog post.
**Stage(s):** infiltration · **Kind:** calibration
**Status:** proposed

## Scope and mechanism
Zero-applied-pressure wetting ("pre-wetting") of a loose coffee bed in a transparent Kompresso column: hot water poured on top through a paper filter, no pressure applied, wetting-front depth tracked by video image processing (row-sum + threshold on 4K/60 FPS footage). Tests the classical capillary-imbibition prediction that penetration depth scales with √t (Lucas–Washburn form, cited via a general-theory link, not derived). The stated point is conceptual: pre-wetting (capillary-driven, slow, may leave the puck incompletely wet) is a distinct regime from pre-infusion (pressure-driven at 1–2 bar).

## Governing equations
The post implements exactly one relation (unnumbered; quoted as "Vertical Distance = constant*sqrt(time)"):

1. h(t) = C·√t (+ b as fitted)
   - h — wetting-front penetration depth. **Units: pixels** in the source; no pixel→length calibration is given.
   - t — time since water contact, s (axis spans 0–48 s).
   - C — lumped imbibition coefficient; fitted C = 77.184 px·s^(−1/2).
   - b — fitted intercept, 28.847 px (physically an artifact of thresholding/initial surface pooling; the theory implies b = 0, and the author does not discuss it).

No decomposition of C into k, p_c, μ, φ is attempted; the Washburn constant is treated as a single lumped fit parameter. Nothing is simplified away by this card — the source contains no further equations.

## Parameters
| symbol | value | units | source (measured/fitted/nominal) |
|---|---|---|---|
| C | 77.184 | px·s^(−1/2) | fitted (single video, least squares) |
| b | 28.847 | px | fitted |
| R² | 0.9857 | — | fitted |
| px→m scale | not provided | m/px | — (column has embossed volume marks, ~visible in figures, but no calibration stated) |
| dose, grind, bed depth, tamp | not provided | — | — |
| water temperature | "hot" | — | assumed (unquantified) |

## Calibration and validation offered by the source
Author's validation: a linear fit of front position against √t over one ~48 s video, R² = 0.9857 ("very strong correlation which confirms... capillary action predictions"). That is the entirety of the evidence: **n = 1 trial, one grind, one bed prep, pixel units, no repeats, no independent prediction** — the same data both motivates and "confirms" the √t law, so this is a consistency check, not validation. Visible in the Flow-Level-vs-√t plot: systematic deviation below the fit line for t ≲ 1 s (the fitted positive intercept absorbs early-time misfit), which the author does not address.

## Assumptions and validity range
- Zero applied pressure only; gravity and evaporation ignored (gravity acts along the flow direction here and is silently folded into C).
- Loose, untamped bed in a plastic column with a paper filter on top — not a tamped 58 mm basket geometry; wall effects in a narrow transparent column unquantified.
- Front assumed sharp and horizontal; the row-sum/threshold method reports a column-averaged front and cannot see interior fingering.
- Valid (per the data shown) over ~0–48 s and ~530 px of penetration in one configuration; silent on: pressure-driven infiltration, temperature dependence, grind dependence, fines, swelling, partial saturation behind the front, and any tamped-bed regime.
- Failure modes: the fit visibly breaks at early time (t ≲ 1 s); no basis for extrapolation to any other bed.

## Interface mapping
Inputs consumed: none usable — no BedState fields are reported (no k, porosity, depth in physical units). Outputs produced: in principle a prior on the lumped capillary coefficient C_eff in foster2025.infiltration's zero-pressure limit s(t) = √(2 k p_c t / (μ φ_T)), but the pixel units make even that non-transferable without a scale the source does not give. Couplings: none runtime; at most an offline qualitative check that the capillary-only branch of foster2025 produces √t front motion (it does by construction). No adapters worth building.

## Extractable data
- Flow-Level-vs-Time and vs-√t plots (one trace each): digitizable, but in pixels with unknown scale, unknown dose/grind — **not worth transcribing** into puckworks/data/.
- Raw video and code: not published; author active online, plausibly available-on-request, but the missing metadata (scale, dose, grind, temperature) caps the value regardless.

## Overlaps and conflicts
- **foster2025.infiltration (registered, gated): superseded by it.** Foster's sharp-front model contains the capillary term p_c explicitly, covers both the zero-pressure limit (which reduces to exactly this √t law) and the pump-driven case, and is gated on 1 s-resolution micro-CT rather than a thresholded video in pixels. This post adds a qualitative anecdote that √t imbibition holds in loose coffee — nothing Foster's micro-CT doesn't establish better.
- **grudeva2023 / grudeva2025 (infiltration↔extraction):** no contact; no extraction, no TDS.
- Conceptual note worth keeping (in prose, not as a component): the pre-wetting ≠ pre-infusion distinction maps onto the unsaturated-flow / incomplete-wetting backlog hypothesis for the fine-grind EY dip — an incompletely pre-wet puck is the failure mode that hypothesis invokes. The post asserts the distinction; it does not test it against extraction outcomes.

## Implementation estimate
None warranted. Any gate this could motivate (√t front motion at zero pressure) is already implied by, and better tested within, foster2025.infiltration's capillary branch.

VERDICT: skip — single uncalibrated pixel-unit trial confirming a √t law that the registered, micro-CT-gated foster2025.infiltration already contains as its zero-pressure limit, with no transcribable data — effort S

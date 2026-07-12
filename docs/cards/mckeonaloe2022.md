# Model card: McKeon Aloe 2022 — Wafo vs VST basket hole geometry

**Paper/thesis:** R. McKeon Aloe, "Wafo vs VST: Espresso Filter Basket Analysis," Medium (Coffee Data Science), 27 Dec 2022. No DOI; blog post, not peer-reviewed.
**Stage(s):** flow (exit-boundary geometry), observables (none) · **Kind:** calibration (data source only)
**Status:** proposed (card-only)

## Scope and mechanism
Not a model. An imaging measurement of basket exit-hole geometry for two 58 mm baskets: one Wafo Classic and one VST (single specimen each). The author photographed each basket floor from the coffee side ("top") and the exit side ("bottom"), manually aligned the images in Procreate, and measured per-hole diameters on both faces, giving per-hole taper (top/bottom ratio), diameter distributions, and total open-area fraction per face. No flow measurement, no resistance model, no equations — the author explicitly defers "how changing the size difference affects flow" to future work.

## Governing equations
None. Nothing to implement. Any exit-resistance use of this data (e.g., an orifice-plate ΔP = f(open-area, hole count, plate thickness) closure for the backlog basket/screen-resistance gap) would be a registry-side construction `[RS]`, not from this source.

## Parameters
No model parameters. Measured geometric quantities (all read from figures; no tables, no stated uncertainties, no pixel-scale calibration reported):

| symbol | value | units | source |
|---|---|---|---|
| Wafo Classic open-area fraction, exit face ("bottom") | 6.2 | % | measured (n = 1 basket) |
| Wafo Classic open-area fraction, coffee face ("top") | 8.8 | % | measured (n = 1) |
| VST open-area fraction, exit face | 2.1 | % | measured (n = 1) |
| VST open-area fraction, coffee face | 2.7 | % | measured (n = 1) |
| Wafo mean hole diameter, exit face | ≈ 245 | µm | measured, read off bar chart |
| Wafo mean hole diameter, coffee face | ≈ 290 | µm | measured, read off bar chart |
| VST mean hole diameter, exit face | ≈ 255 | µm | measured, read off bar chart |
| VST mean hole diameter, coffee face | ≈ 290 | µm | measured, read off bar chart |
| hole-diameter std, all four cases | ≈ 30 | µm | measured, read off bar chart |
| hole count per basket | not provided | — | — |
| plate thickness / hole depth | not provided | — | — |
| pixel-to-µm calibration method | not provided | — | — |

Distribution shape (from figures): Wafo exit-face distribution peaks near 245 µm (~9% of holes per bin), coffee-face near 285–300 µm; span roughly 70–380 µm. VST coffee-face is tightly peaked near 310 µm (17% per bin) while the exit-face is broad (~200–290 µm, weakly bimodal) with a long tail the author himself attributes possibly to photography error. Both baskets show mean top/bottom ratio > 1 (holes taper, wider on the coffee side, so the exit face is flow-limiting), and the ratio declines with exit-hole diameter (~1.5 at 200 µm to ~1.0 at 300+ µm) in both — consistent in mean and spread between the two baskets.

## Calibration and validation offered by the source
None. No repeat measurements, no second specimen, no comparison against manufacturer specs or an independent metrology method, no uncertainty quantification. The author flags unquantified photography/alignment error explicitly for the VST bottom-face tail. Treat every number above as single-specimen, uncalibrated-scale imaging.

## Assumptions and validity range
- n = 1 per basket model; no manufacturing-lot variability information.
- Manual image alignment; optical diameter of a countersunk/tapered hole photographed at a distance is not a bore measurement — systematic bias unknown and unquantified.
- Silent on: hole count, plate thickness, hole shape along the bore (only two end diameters), actual flow resistance, clogging/fines interaction, and every other basket model on the market.
- The "top vs bottom" taper finding is the one qualitatively robust result (appears in both baskets with consistent trend); absolute diameters and especially the open-area percentages inherit the unstated pixel calibration and should be treated as ±unknown.

## Interface mapping
Inputs consumed: none. Outputs produced: none under contracts v0.1 — there is no exit-boundary/basket field in BedState or FlowLaw. If the basket/screen-resistance gap (ROADMAP G9) is taken up, this data would seed an offline prior for an exit-resistance parameter (open-area fraction + mean exit diameter → orifice/perforated-plate ΔP term); that requires (i) a contract extension for an exit boundary term and (ii) hole count and plate thickness from another source. Coupling: offline data ingest only; nothing here should ever be runtime.

## Extractable data
- The four open-area percentages and eight mean/std diameters above → `data/mckeonaloe2022_baskets.csv` (trivial; already transcribed in this card).
- Hole-diameter histograms (Wafo fig. "Hole Size Distribution from Top and Bottom"; VST equivalent) — digitizable but low value given single-specimen, uncalibrated provenance.
- Top/bottom-ratio vs exit-diameter scatter (combined Wafo+VST overlay) — worth digitizing only if an exit-resistance closure needs the taper–diameter correlation.
- No raw data or code published; per-hole data exists (author generated it) but only as figures. Author has a companion post (IMS Big Bang, Jun 2023) and promised Wafo SOE/Spirit data — same provenance class.

## Overlaps and conflicts
- **wadsworth2026.permeability (complements):** the tamped-regime reconciliation names "φ_c ~ 0.11 or screen resistance" as competing explanations; this is the first basket exit geometry on file and gives a first-order input for bounding the screen-resistance branch. Note, however, that the grudeva2025 κ adjudication (κ ≈ 2.2×10⁻¹⁵ m², LOG Issue 2a) already shrank the gap that sieve resistance was invoked to explain — the demand for this data is weaker than when G9 was opened.
- **ROADMAP G9 basket/screen resistance (direct hit, weakly):** supplies geometry, not resistance. A usable G9 closure still needs hole count, plate thickness, and ideally a measured ΔP-vs-flow curve on a bare basket — none of which this source has.
- **mo2023 (no conflict):** its periodic-boundary SPH explicitly omits basket/screen resistance; this data is the missing boundary those simulations idealize away.
- No competition with any registered component; nothing here models anything.

## Implementation estimate
Effort S: transcribe the 12 scalars with a provenance-caveat column; optionally digitize the ratio scatter. No gate is possible against this source alone (nothing to reproduce). Gate design for eventual G9 use: an orifice-plate estimate built on these open-area fractions must be checked against a bare-basket ΔP–flow measurement from an independent source before entering any resistance budget. Dependency: hole count and plate thickness from manufacturer specs or a metrology source.

VERDICT: data-only — no model and single-specimen hobbyist imaging, but it is the only basket exit-geometry data on file and the taper + open-area numbers are a cheap seed for the G9 screen-resistance bound — effort S.

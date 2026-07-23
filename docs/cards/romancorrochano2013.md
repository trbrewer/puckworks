# Model card: Roman-Corrochano 2013 conference summary (permeability rig)

**Paper/thesis:** Roman Corrochano B., Melrose J., Fryer P., Bakalis S., "Optimising Coffee Extraction Using a Multiscale Approach," conference proceedings summary (2-page extended abstract; venue not stated in the document; affiliation Mondelēz Global Coffee Technology Centre / Univ. of Birmingham). No DOI printed.
**Stage(s):** packing · **Kind:** calibration
**Status:** card-only

## Scope and mechanism
Two-page precursor summary of the steady-state permeability programme fully documented in the author's 2017 EngD thesis (carded as `romancorrochano2017_permeability`). Reports: a custom pressure rig measuring ΔP–Q for roast-and-ground beds over initial densities 360–480 kg/m³ and four Sauter diameters (d[3,2] = 79.73, 102, 113, 132 µm), fitted to Darcy's law; porosity estimated both by Kozeny–Carman fitting and by direct Hg-porosimetry/He-pycnometry with a bed-compression correction; and a steady-state drink-volume simulation. No equations are printed — Darcy and K–C are cited by name only.

## Governing equations
None transcribed in the abstract. The working equations (Darcy fit; K–C forms) are exactly thesis Eqs. 3.39–3.43 already transcribed in `romancorrochano2017_permeability.md`. Nothing here would be implemented from this document.

## Parameters
| symbol | value | units | source |
| --- | --- | --- | --- |
| κ (typical range) | 10⁻¹³ – 10⁻¹⁴ | m² | measured (Darcy fit; note: text prints "10¹³" — sign typo for 10⁻¹³) |
| ε_bed (typical range) | 0.09 – 0.19 | – | fitted (K–C) / measured (porosimetry+pycnometry) |
| initial bed density range | 360 – 480 | kg/m³ | measured (set) |
| d[3,2] tested | 79.73, 102, 113, 132 | µm | measured |
| max bed-height compression | up to 35 %, mostly in first 30–60 s | – | measured |
| simulated vs typical shot | ~25–30 ml in 10–15 s | ml, s | nominal comparison ("compared well"; no error metric) |

## Calibration and validation offered by the source
Fitted vs directly measured porosity "compared well" except at 480 kg/m³ (attributed to particle deformation under high axial compaction) — no numbers given. Drink-volume simulation "compared well" to a typical 25–30 ml in 10–15 s — a qualitative order-of-magnitude check against folklore shot parameters, not a validation. All quantitative validation content lives in the thesis (Table 6.1 and the poor blind-prediction record of the K–C models, already documented on the 2017 card); nothing here upgrades or contradicts it.

## Assumptions and validity range
- Steady-state Darcy only; the abstract itself flags the large early-time transient (35 % height loss in 30–60 s) as outside the fitted model — same limitation as the thesis card.
- Silent on everything else (fines migration, CO₂, temperature, tamped vs untamped protocol details); the thesis card covers these.

## Interface mapping
Same as `romancorrochano2017_permeability`: would inform BedState.k priors from GrindState + porosity, offline calibration only. No adapter or coupling considerations beyond that card; this document adds no interface content of its own.

## Extractable data
- Figure 1 (ΔP vs Q, 4 grinds with error bars) and Figure 2 (κ vs d[3,2] with K–C iso-porosity curves and measured points at 3 densities) contain data points, but these are early/partial views of the same experimental campaign as thesis Table 6.1 and Ch. 6.2 curves, which are the higher-fidelity transcription targets already named on the 2017 card. Digitising these figures would duplicate that at lower precision. No raw data or code published.

## Overlaps and conflicts
- SUPERSEDED by `romancorrochano2017_permeability` (thesis, same authorship and campaign): the thesis provides the equations, the fitted per-grind n values, Table 6.1 with uncertainties, and the honest blind-prediction failure record — none of which appear here. The abstract adds no result absent from the thesis.
- Only marginal unique detail: explicit d[3,2] values for the four grinds (79.73–132 µm), useful as a cross-check on the thesis grind labels ΨB–ΨE if that mapping is ever needed; note it in the 2017 card's data notes rather than transcribing anything from here.
- No interaction with wadsworth2026.permeability, brewer2026.pack_generator, or backlog items beyond what the 2017 card already records.

## Implementation estimate
S (nothing to implement). If the ΨB–ΨE ↔ d[3,2] mapping matters during Table 6.1 transcription, copy the four diameters into that dataset's provenance notes; otherwise no action.

VERDICT: skip — conference-abstract precursor of the already-carded 2017 EngD thesis with no equations, no tables, and no result not superseded there; at most a one-line d[3,2] cross-reference for the thesis card — effort S

# Model card: Schulman 2011 filter-basket geometry & flow study

**Paper/thesis:** J. Schulman (another_jim, Team HB), "How filter baskets affect espresso taste and barista technique," Home-Barista.com blog study, August 2011. No DOI. Hole-size distributions measured by J. Weiss (image analysis, pixel counting on photographed basket bases). NOT peer-reviewed — enthusiast study, but the measurement dataset is unique.
**Stage(s):** flow (basket exit boundary), observables (dose→shot-weight response) · **Kind:** calibration
**Status:** card-only

## Scope and mechanism
Three-part study of 14 commercial filter baskets (8 types: Faema single/double, La Marzocco single/double, MicroFine double, OEM triple, VST 15/18/22): (1) measured hole-size distributions, total hole area, base diameter, and grid pattern per basket; (2) an 84-shot dose-response campaign (6 doses × 14 baskets, fixed 25 s shot time, one grinder/coffee/machine) fitted with a semi-empirical flow/dwell model driven by the measured geometry; (3) a taste test of scale invariance (not registry-relevant beyond the observation that crema/mouthfeel is dose-scale-dependent). The uploaded material is the Part-1 data table only; the flow model below is documented from the source article. No pressure-drop or resistance measurements were made — basket hydraulic resistance must be inferred, not read off.

## Governing equations
Semi-empirical, no equation numbers in source (labels (i)–(iii) assigned here):

(i)  W_shot = F̄ · (t_shot − t_dwell), with t_shot = 25 s fixed.
(ii) F̄ ∝ A_h / (m_dose + a) — average flow term.
(iii) t_dwell ∝ (m_dose + b) / A_h — dwell-time term.

Symbols: W_shot beverage mass [g]; F̄ average flow [g/s]; t_dwell time to first flow [s]; A_h total hole area [mm²]; m_dose dry dose [g]; a, b additive constants [g]. The author reports the fit is insensitive to (a, b) provided they differ; the final model sets a = 1 and drops b. The proportionality coefficients are stated to depend on base diameter (conicality), grid pattern (square vs hexagonal), mean hole diameter, and hole-size variance — **no coefficient values are published**, so the model is not implementable as printed. Reported sign/direction of effects: smaller base diameter slows flow and lengthens dwell; square grid lengthens dwell; larger mean hole diameter increases flow and shortens dwell; smaller hole variance appeared to slow flow and shorten dwell, but the author himself flags this as possibly a categorical VST effect rather than a physical one (only VSTs had low variance).

## Parameters
| symbol | value | units | source |
|---|---|---|---|
| t_shot | 25 | s | nominal (protocol) |
| a | 1 | g | assumed (author's simplification) |
| b | omitted | g | assumed (dropped from final model) |
| flow/dwell coefficients | not provided | — | fitted (values unpublished) |
| A_h, d̄_hole, σ_hole, D_base, grid | see data table below | mm², µm, µm, mm, H/S | measured (per basket) |

Measured geometry (the uploaded table; base diameter column in source is mm × 10⁻¹; all baskets 58 mm at top):

| basket | D_base [mm] | d̄_hole [µm] | σ_hole [µm] | A_h [mm²] | grid |
|---|---|---|---|---|---|
| Faema single 1 | 28.8 | 396.7 | 37.5 | 28.2 | H |
| Faema single 2 | 28.8 | 382.2 | 25.9 | 27.5 | H |
| LM single 1 | 31.0 | 367.2 | 28.2 | 37.9 | S |
| Faema double 1 | 43.0 | 285.8 | 39.2 | 36.6 | H |
| Faema double 2 | 43.0 | 286.3 | 48.1 | 36.9 | H |
| MicroFine double 1 | 43.0 | 342.3 | 30.8 | 59.3 | S |
| MicroFine double 2 | 43.0 | 366.8 | 38.8 | 68.5 | S |
| LM double 1 | 43.0 | 401.9 | 50.7 | 81.9 | S |
| LM double 2 | 43.0 | 409.9 | 46.3 | 85.0 | S |
| VST 15 | 49.4 | 310.6 | 14.3 | 54.3 | H |
| VST 18 | 49.4 | 351.2 | 9.8 | 69.3 | H |
| VST 22 | 49.4 | 377.1 | 15.4 | 80.0 | H |
| OEM triple 1 | 48.9 | 384.0 | 41.5 | 87.7 | H |
| OEM triple 2 | 48.9 | 387.0 | 42.5 | 88.7 | H |

## Calibration and validation offered by the source
- Dose-response campaign: 84 shots. Categorical model (one line per basket type) explains ~78% of shot-weight variation; per-individual-basket, ~82% (difference not significant). The physical model (i)–(iii) with geometry-driven coefficients explains ~76% — i.e., measured geometry recovers nearly all the explainable between-basket signal.
- All on ONE machine, ONE coffee (Metropolis Red Line), ONE grinder, ONE grind setting, fixed 25 s. The author explicitly states generalization is an assumption.
- The fit is internally circular in the usual sense: coefficients fitted to the same 84 shots they explain; no holdout.
- Headline geometry finding: VST manufacturing tolerance (σ_hole 9.8–15.4 µm) is ~3× tighter than all other baskets (25.9–50.7 µm); VST hole area scales with nominal gram size. MicroFine's precision claim NOT supported. VST's commercial-consistency claim also NOT supported by the shot data — shot-to-shot noise dominates, and the steeper VST dose-response (narrower dosing range) amplifies dose/grind errors, offsetting tolerance gains.

## Assumptions and validity range
- Hole areas from image analysis of the basket base face; holes in stamped baskets are typically tapered, and the source does not state which face (narrowest section governs resistance) — treat A_h as face-side area with unknown bias.
- No ΔP, no flow-resistance measurement anywhere: the study never separates basket resistance from puck resistance; the dwell/flow terms lump both.
- Single-machine/coffee/grind campaign; fixed-time shots accentuate end-of-shot flow differences (author's own caveat).
- Wear, clogging, and partial hole blockage by fines not measured — precisely the mechanism by which basket resistance could become non-negligible.
- Silent on: pressure dependence, temperature, puck–screen interface cake formation, hole-pattern spatial layout (only grid type recorded), 58 mm-top geometry variants beyond base diameter.
- [RS] Order-of-magnitude check: open-area fraction is ~1–3% of basket cross-section (A_h 28–89 mm² vs ~2640 mm²). Treating the holes as sharp-edged orifices (C_d ≈ 0.6) at 2 mL/s gives ΔP ~ O(1–10 Pa) — utterly negligible against ~9 bar. Clean-basket exit resistance CANNOT explain the G9 κ gap; any real screen resistance must come from fines caking/clogging at the exit, which this dataset constrains only indirectly (hole size vs fines size).
- [RS] Hole diameters (286–410 µm) are ~10× typical fines (~25–50 µm): baskets do not sieve fines; exit of mobile fines is unimpeded by clean holes.

## Interface mapping
Inputs consumed: none at runtime.
Outputs produced (as calibration data): per-basket exit-geometry constants — A_h, d̄_hole, σ_hole, D_base — usable as parameters of any future basket/screen exit-resistance term. No current contract carries these; a `BasketState` (or extension of BedState with exit-boundary fields) would be needed, per the same pattern as the missing Forchheimer field flagged on mo2023.
Couplings: offline only. The flow model (i)–(iii) cannot be a runtime component (coefficients unpublished, dimensional bookkeeping absent); its value is as a functional-form sanity check that shot weight ≈ A_h/(dose)-driven at fixed time.

## Extractable data
- The uploaded table → `data/schulman2011_baskets.csv` (14 baskets × 6 fields). Transcribable now; the only multi-brand basket hole-geometry dataset on file.
- Dose vs shot-weight raw data (84 shots): published as graphs only — digitizable at low priority; per-type fitted slopes would need re-estimation from the plot.
- VST vs conventional-double hole-size frequency distributions: figure only, qualitative value.
- No code, no raw data files published; Weiss's image-analysis program not released.

## Overlaps and conflicts
- **ROADMAP G9 (basket/screen resistance):** direct data input, and the [RS] orifice estimate above sharpens G9's framing — clean-exit resistance is negligible, so G9 should be restated as a clogging/caking question. Consistent with the grudeva2025 adjudication already weakening the "sieve resistance explains a 10× κ gap" narrative.
- **wadsworth2026.permeability:** the "φ_c ~ 0.11 or screen resistance" reconciliation can now be checked against real open-area numbers; this dataset supplies the screen side.
- **romancorrochano2017_permeability:** its Table 6.1 tamped-κ confrontation with Wadsworth names screen resistance as a possible reconciler — same G9 thread; this card supplies the geometry that bounds it.
- **fasano2000_partI / brewer2026 (fines migration):** hole size ≫ fines size means the exit boundary does not retain migrating fines — relevant boundary condition for the mobile-fines transport backlog item (fines leave; they don't accumulate at a clean screen unless bridging occurs).
- **cameron2020 / foster2025:** both treat the basket exit as a free boundary; this dataset justifies that treatment for clean baskets.
- No registered component competes; nothing is superseded.

## Implementation estimate
Effort S: transcribe one table, add the [RS] orifice bound as a documented note on G9. No equations worth implementing (coefficients unpublished, single-rig fit). Gate design if a screen-resistance term is ever added: predicted ΔP contribution from clean-hole geometry must be ≲ 10 Pa for these baskets, else the term is wrong.

VERDICT: data-only — the flow model is unimplementable (fitted coefficients unpublished, single-rig, non-peer-reviewed), but the 14-basket hole-geometry table is the only dataset on file that quantifies the basket exit boundary and it decisively reframes G9 from "sieve resistance" to "clogging/caking" — effort S

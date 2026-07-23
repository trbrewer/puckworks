# Model card: Roman-Corrochano 2017 permeability

**Paper/thesis:** Roman-Corrochano, B. "Advancing the Engineering Understanding of
Coffee Extraction." EngD thesis, University of Birmingham (submitted Dec 2015,
awarded 2017). No DOI assigned; University of Birmingham e-theses repository
(etheses.bham.ac.uk). Ch. 3.4.3 (models), Ch. 6 (hydrodynamics).
**Stage(s):** packing (informs BedState.k / kappa priors) · **Kind:** calibration
**Status:** card-only

## Scope and mechanism
Two Kozeny–Carman-family constitutive models for the steady-state permeability κ of
roast-and-ground coffee beds. Model 1 corrects the classic monosized K–C form for a
non-spherical, distributed material by using a sphericity-weighted Sauter mean diameter
(Φ d[3,2]). Model 2 extends Model 1 by making bed tortuosity porosity-dependent through
a semi-empirical bimodal-sphere correlation (Dias et al. 2006). Both are steady-state,
fully-extracted-bed permeabilities; the thesis also documents (qualitatively) the strong
NON-steady-state transient (CO₂ expulsion, consolidation, particle removal) that the
constitutive models do not capture.

## Governing equations
Base Kozeny–Carman derivation (thesis Eqs. 3.39–3.40):
- (3.39) κ = ε_bed³ / ( 2 τ_bed² S_v² (1−ε_bed)² )
- (3.40) κ = ε_bed³ d_s² / ( 180 (1−ε_bed)² )  — monosized spheres (S_v=6/d_s, τ_bed=1.58 → 180)

Model 1 (sphericity- and PSD-corrected, thesis Eq. 3.41), d_s = Φ d[3,2]:
- (3.41) κ = ε_bed³ (Φ d[3,2])² / ( 180 (1−ε_bed)² )

Model 2 (porosity-dependent tortuosity, thesis Eqs. 3.42–3.43):
- (3.42) τ_bed = (1/ε_bed)ⁿ    (Dias et al. 2006; n = 0.4 loose … 0.5 dense random packed spheres)
- (3.43) κ = ε_bed³ (Φ d[3,2])² / ( 72 (1/ε_bed)^{2n} (1−ε_bed)² )

Symbols: κ permeability (m²); ε_bed bulk bed porosity (–); d_s effective sphere
diameter (m); d[3,2] Sauter (volume/surface) mean diameter (m); Φ sphericity (–);
S_v surface-to-volume ratio (m⁻¹); τ_bed bed tortuosity (–); n packing exponent (–);
180/72 K–C pre-factor groupings.

## Parameters
| symbol | value | units | source (measured/fitted/nominal/assumed) |
| --- | --- | --- | --- |
| n (Dias literature range) | 0.4 (loose) – 0.5 (dense) | – | nominal (Dias et al. 2006) |
| n (fitted per grind, this work) | 0.27 (ΨB), 0.33 (ΨC), 0.64 (ΨD), 1.01 (ΨE) | – | fitted (R²=0.81–0.98) |
| effective K–C pre-factor (from fitted n) | 189–1330 | – | fitted (derived) |
| Φ sphericity | ~0.75 | – | measured |
| d[3,2] (dry / wet measured) | grind-dependent | µm | measured |
| ε_bed (steady state) | grind/density dependent | – | measured/derived |
| τ_bed (monosized ref) | 1.58 | – | nominal |
| experimental κ (espresso beds) | 3.4×10⁻¹³ … 2.6×10⁻¹⁴ | m² | measured (Darcy, Table 6.1) |

## Calibration and validation offered by the source
Validated against the author's own steady-state Darcy permeabilities (Table 6.1: 4 grinds
ΨB–ΨE × 3 initial bed densities 360/400/480 kg m⁻³), measured on fully-extracted,
axially-compacted + hydrodynamically-consolidated ("tamped/espresso") beds. As a blind
predictor the models are POOR: Model 1 relative error grows with grind size (30 % for ΨB
to 520 % for ΨE); Model 2 with n=0.5 only improves the coarsest to ~340 %. Agreement is
recovered only by FITTING n per grind (0.27–1.01), and the fitted n does not track the
expected packing physics (finer, more-consolidated beds got LOWER n, opposite to the
loose→dense argument), so n absorbs unmodelled effects (particle fracture, elongation,
CO₂, particle loss). The author attributes the disagreement to hydrodynamic forces on the
grinds. Steady-state κ range (10⁻¹³–10⁻¹⁴ m²) agrees with literature values it cites.

## Assumptions and validity range
- Steady-state, fully-extracted bed only. Explicitly NOT valid during the first ~10–30 s:
  Ch. 6.4 documents a large non-steady transient (flow can drop to a drip then recover)
  driven by consolidation, CO₂ expulsion, and 1–3 % particle removal — none in κ(ε,d).
- Bundle-of-capillaries K–C assumption; single sphericity; single d[3,2]. No fines/coarse
  bimodal permeability split beyond what n absorbs.
- Model 1 assumes monosized K–C physics (known to fail for bimodal PSD). Model 2's n is
  material/packing dependent and here becomes an unphysical fit parameter for RGC.
- Silent on swelling (none observed here), channelling, and pressure/history-dependent κ,
  though the thesis names all three as likely non-steady contributors.

## Interface mapping
Inputs consumed: GrindState (sphericity Φ, d[3,2] via mean/boulder radius, fines_fraction)
+ BedState.porosity. Outputs produced: BedState.k (κ) as an offline prior.
Couplings: OFFLINE CALIBRATION provider (grind+packing → k prior), not a runtime component.
Adapters: needs a Sauter-diameter and sphericity adapter from GrindState; Model 2 needs a
per-grind n supplied as a fitted input (it is not predictive standalone).

## Extractable data
> **SUPERSEDED (2026-07-22):** the Table 6.1 tamped-κ transcription target is now served by the
> DOI'd CC-BY **version of record `romancorrochano2015`** (`romancorrochano2015_table2()` — the
> same campaign's K with SDs + Tukey groups, fully printed). Prefer that landed dataset as the
> tamped-κ source; the thesis (2017) card remains the record for the Deff map / partition K(T) /
> hindrance tables not printed in the 2015 paper.
- Table 6.1 → data/romancorrochano2017_permeability_table1.csv: experimental κ for
  4 grinds × 3 initial bed densities with uncertainties and ANOVA groupings. HIGH value —
  these are TAMPED/consolidated espresso-bed permeabilities, precisely the regime the
  registry flags as a gap.
- Fitted n and K–C pre-factors per grind (Fig. 6.13 text).
- Ch. 6.2 permeability vs bed density/aspect-ratio/temperature and flaked-coffee series;
  Ch. 6.4 non-steady flow-rate/ΔP transients (qualitative).
Raw data/code: none published; Table 6.1 transcribable; Ch. 6 curves need plot digitising.

## Overlaps and conflicts
- COMPETES with / is LOWER-fidelity than wadsworth2026.permeability (registry #6): both
  give k(grind, porosity). Wadsworth's percolation form k∝φ_p^4.4 with angularity exp(αR)
  is validated on UNTAMPED beds (φ_p 0.37–0.67) and is parameter-free; Roman-Corrochano's
  K–C models are NOT predictive without a fitted per-grind n. But they are COMPLEMENTARY on
  regime: Wadsworth's tamped case is acknowledged extrapolation, and Table 6.1 supplies
  real TAMPED/consolidated κ that could test the wadsworth "phi_c ~ 0.11 or screen
  resistance" reconciliation directly, and the Cameron flux-table tamped gap.
- COMPLEMENTS backlog "flow: Forchheimer/inertial correction" (author blames hydrodynamic
  forces — inertial regime candidate) and "bed_dynamics: pressure/history-dependent
  kappa(t)" (Ch. 6.4 transient is exactly that competing rising-flow explanation:
  CO₂ + consolidation, not swelling).
- Overlaps brewer2026.pack_generator conceptually (bimodal packing → κ) but adds no new
  synthetic-pack physics.

## Implementation estimate
Effort S. Eqs. 3.41 and 3.43 are one-line closures. As a κ-prior provider they are trivial
to add, but as PREDICTORS they are weak (need fitted n), so implementing the equations is
low value vs implementing the data. Gate design: (i) reproduce Table 6.1 κ range from
(ε_bed, Φ d[3,2]) with Model 2 + reported fitted n; (ii) confront Table 6.1 tamped κ with
wadsworth2026 tamped extrapolation and record whether φ_c~0.11 / screen resistance is
needed. Dependency: transcribe Table 6.1 first.

VERDICT: data-only — the two K–C closures are lower-fidelity than the registered Wadsworth
model and only fit with an unphysical per-grind n, but Table 6.1's tamped/consolidated
permeabilities fill a named validation gap — take the data, skip the equations — effort S.

# Model card: Vaca Guerra 2023a — PSD-aware bed compression + modified Kozeny–Carman permeability

**Paper/thesis:** Vaca Guerra, M., Harshe, Y.M., Fries, L., Rothberg, S., Palzer, S.,
Heinrich, S. "Influence of particle size distribution on espresso extraction via packed
bed compression." *Journal of Food Engineering* 340 (2023) 111301.
DOI: 10.1016/j.jfoodeng.2022.111301. **Document carded: the revised preprint dated
2022-09-27** (equation/table numbering may differ trivially from the version of record;
spot-check before citing page-level details). This is "target (1)" named on
`vacaguerra2025_leseprobe.md`.
**Stage(s):** packing (produces BedState.porosity from tamp stress; informs BedState.k
priors) · **Kind:** calibration
**Status:** data-intaken (2026-07-25) — Table C.1, Tables 1–3, and Fig. 12 digitized
(Tim drop) → `puckworks/data/vacaguerra2023a/` + loaders + 5 MANIFEST rows; the three
discriminating computations landed in `puckworks/analysis/vacaguerra2023a.py`
(CI-tested, `tests/test_vacaguerra2023a.py`): **the Eq-9/10 β-sign error is RESOLVED
(−k₃β/−x₃β)** — the printed +β gives unphysical ω 0.48–0.62 while −β gives ω 0.31–0.37
matching Table C.1 + the Fig-9 fits; the Fig-12 cross-device compression validation
recomputes to **R²=0.942** (authors ~0.93); an independent Darcy **K** from Table C.1
reproduces the authors' measured range (7/9 in band, all order-of-magnitude); and the
**`wadsworth2026.permeability` cross-eval** shows that model — validated untamped
(φ_p 0.37–0.67) — **overpredicts vacaguerra's measured tamped K by ~13–31× (median 23×)**
when extrapolated to ε₀ 0.24–0.36, the overprediction growing as ε₀ drops below the 0.37
floor (tightest bed 25×, loosest 15×). **Still owed:** a full registered component
(offline σ→ε₀→K closure) and a µ→G10-renormalized λ refit.

## Scope and mechanism
Two chained empirical closures on one dark-roast arabica material. (i) A dry-bed
compression model: fit the coarse fraction (d_p > 100 µm) of the bimodal PSD with
Rosin–Rammler parameters α (mean size) and β (uniformity), then predict dry bed porosity
ε₀ under axial tamp stress σ via a compressibility law whose two constants — initial
porosity ω and compression factor φ — are ANOVA response surfaces in (α, β). (ii) A
modified Kozeny–Carman correlation predicting steady-state extraction permeability K from
that dry porosity plus PSD descriptors (ψ, d[3,2], β), with fitted porosity exponent 4.3,
β exponent 0.43, and empirical constant λ = 7.5. Central empirical finding: low
permeability is not exclusive to fine grinds — lowering size uniformity β (widening the
coarse fraction) at constant or even larger α reaches the same low ε₀ and K. Both closures
are offline: dry-bed initial conditions in, scalar porosity/permeability out; nothing is
time-resolved.

## Governing equations
Compression (their §2.1; the paper FITS Eq. 2, not Eq. 1 — Fig. 9 caption is explicit):
- (1) ε₀ = ω e^(−φσ)
- (2) ε₀ = ω / (1 + φσ)  — stated as "the first order" of (1). **Flag (same defect as
  leseprobe Eqs. 1.9/1.10): (1) and (2) are not equivalent beyond first order in φσ, and
  neither has a residual close-pack porosity floor (ε₀ → 0 as σ → ∞).** Harmless inside
  the fitted range (σ ≤ 1.24×10⁵ Pa) but do not extrapolate.
  **Symbol-swap flag vs. leseprobe:** the dissertation excerpt writes ε_bed = ε₀ exp(−ωσ),
  i.e. ω is there the compression factor (Pa⁻¹) and ε₀ the repose porosity; here the roles
  are renamed — ω (−) is the initial porosity and φ (Pa⁻¹) the compression factor. Any
  cross-referencing between the two cards must map (leseprobe ε₀, ω) → (here ω, φ).

PSD characterization (§2.5):
- (8) Q₃(x) = 1 − e^(−(x/α)^β) — Rosin–Rammler, fitted ONLY to the coarse fraction
  (d_p > 100 µm) of each cumulative volume distribution; average R² = 0.97. Fines are
  defined as the volume fraction below 100 µm and are NOT a model input.

ANOVA response surfaces (§3.3), coefficients in Parameters:
- (9)  φ = 1 / (k₁ − k₂α + k₃β + k₄αβ + k₅α²)
- (10) ω = x₁ − x₂α + x₃β + x₄αβ
  **Sign-error flag (ours, from reproduction): the +k₃β and +x₃β terms as printed are
  inconsistent with the paper's own figures.** With the printed signs, Eq. 9 gives
  φ ≈ 2–3.5×10⁻⁶ Pa⁻¹ across the design domain, whereas Fig. 10's contours span
  5×10⁻⁶–1×10⁻⁵ and Fig. 9's per-PSD fits are 6.9×10⁻⁶–1.26×10⁻⁵. Flipping the β term
  to −k₃β reproduces Fig. 10 well (e.g. (α = 311 µm, β = 1.4): printed signs → 3.5×10⁻⁶;
  −k₃β → 9.9×10⁻⁶ vs. the plotted 1×10⁻⁵ contour; (427 µm, 1.95): −k₃β → 4.6×10⁻⁶ vs.
  plotted ≈ 5×10⁻⁶). Identically for Eq. 10: printed signs give ω(427 µm, 1.4) = 0.48 vs.
  Fig. 11's plotted 0.32; −x₃β gives 0.31. The likely cause is negative fitted
  coefficients k₃, x₃ whose signs were dropped when tabulated. Carried as a dual variant:
  (as-printed) vs. (β-term negated). Discriminating computation, required before any use:
  regenerate the full Fig. 10 and Fig. 11 surfaces under both sign conventions and accept
  the one matching the published contours; then verify the composed ε₀(σ; α, β) against
  Fig. 13 (R² = 0.93 surface at 200 N / 60 mm).
  Secondary flag: §3.3's claim that ω's β-dependence "decreases with the mean particle
  size" appears inverted relative to Fig. 11 (contour spacing widens toward large α, and
  ∂ω/∂β = −x₃ + x₄α grows with α under the corrected signs). Trust the figure.

Permeability (§2.3, §3.7):
- (5) Q = (K A / (µ L)) ΔP — Darcy, used to measure K from extraction operating points;
  stated valid Re_p < 10.
- (6) K = ε_bed³ / (2 τ² S_v² (1 − ε_bed)²); (7) K = ε_bed³ d[3,2]² / (180 (1 − ε_bed)²)
  — baseline K–C with τ = 1.58, S_v = 6/d[3,2]; quoted as the closure that FAILS for
  wide/bimodal PSDs (motivation, not implemented).
- (11) K = (ψ d[3,2])² ε_bed^4.3 β^0.43 / (72 λ² (1 − ε_bed)²), λ = 7.5 — the proposed
  modified K–C. ε_bed here is the DRY bed porosity ε₀ (their deliberate choice; see
  Assumptions). Note 72λ² = 4050, i.e. an effective pre-factor 22.5× the monosized 180 —
  same direction as the registry-wide "nominal K–C overpredicts" theme. Higher β (more
  uniform) → higher K; wider distributions percolate slower.

Symbols: ε₀ dry bed porosity from compression (−); ω initial (repose) bed porosity (−);
φ intrinsic compression factor (Pa⁻¹); σ axial compression stress (Pa); Q₃ cumulative
volume fraction (−); x particle size (m); α coarse-fraction volumetric mean size (m);
β size uniformity factor (−, lower = wider); k₁…k₅, x₁…x₄ empirical ANOVA coefficients
(units in Parameters); Q volumetric flow (m³ s⁻¹ for (5) to close; text reports ml s⁻¹);
K permeability (m²); A bed cross-section (m²); µ brew viscosity (Pa s); L bed length (m);
ΔP pressure drop (Pa); ε_bed bed porosity (−); τ tortuosity (−); S_v volume-specific
surface area (m⁻¹); d[3,2] Sauter mean diameter (m); ψ sphericity (−); λ empirical
constant (−). Nothing has been simplified away.

## Parameters
| symbol | value | units | source (measured/fitted/nominal/assumed) |
| --- | --- | --- | --- |
| k₁ | 3.15×10⁵ | Pa | fitted (ANOVA, Table 2; sign of k₃ under dispute, see flag) |
| k₂ | 1.59×10⁹ | Pa/m | fitted (Table 2) |
| k₃ | 6.65×10⁴ | Pa | fitted (Table 2; likely −6.65×10⁴, see sign-error flag) |
| k₄ | 5.76×10⁸ | Pa/m | fitted (Table 2) |
| k₅ | 1.27×10¹² | Pa/m² | fitted (Table 2) |
| x₁ | 0.48 | − | fitted (ANOVA, Table 3) |
| x₂ | 8.5×10² | 1/m | fitted (Table 3) |
| x₃ | 6.24×10⁻² | − | fitted (Table 3; likely −6.24×10⁻², see sign-error flag) |
| x₄ | 4.64×10² | 1/m | fitted (Table 3) |
| per-PSD (ω, φ) examples (Fig. 9) | (0.36, 6.875×10⁻⁶), (0.34, 1.007×10⁻⁵), (0.28, 1.257×10⁻⁵) | (−, Pa⁻¹) | fitted (Eq. 2 to 9-stress sweeps) |
| λ | 7.5 | − | fitted (to own extraction K data) |
| ε₀ exponent | 4.3 | − | fitted (same fit) |
| β exponent | 0.43 | − | fitted (same fit) |
| τ (baseline K–C only) | 1.58 | − | nominal |
| Dist. A: α, β, d[3,2], fines, ψ | 224 µm, 1.95, 101.7 µm, 30.03 %, 0.80 | — | measured (Table 1) |
| Dist. B: α, β, d[3,2], fines, ψ | 296 µm, 1.95, 131.6 µm, 24.00 %, 0.79 | — | measured (Table 1; Fig. 6 caption says d[3,2] = 126 µm — internal discrepancy, Table 1 preferred) |
| Dist. C: α, β, d[3,2], fines, ψ | 427 µm, 1.40, 135.5 µm, 25.45 %, 0.79 | — | measured (Table 1; Fig. 6 says 135 µm ✓) |
| ρ_solid (dark roast 100 % arabica) | 1304 ± 9.1 | kg/m³ | measured (He pycnometry, App. A) |
| ε_particle open / closed / total | 0.30–0.46 (avg 0.38) / 0.13–0.37 / 0.515 avg | − | measured (Hg porosimetry + pycnometry; closed rises with particle size) |
| ρ_particle | 632.7 | kg/m³ | derived (Eq. A.2, single average used everywhere) |
| µ brew viscosity | 3.5×10⁻³ at 65 ± 5 °C | Pa s | measured (own viscosimeter, "results not included"; see G10 conflict flag) |
| basket D × H | 5.9 × 2.65 | cm | measured (set) |
| initial bed length L₀ (avg) | 2.55 | cm | measured |
| brew temperature | 88 ± 2 | °C | nominal (set) |
| beverage mass | 50 | g | nominal (set) |
| compression stresses (rheometer) | 2, 4, 7, 9, 15, 25, 40, 55, 75 | kPa | measured (set) |
| texture-analyzer force range | 50–350 (validated to 350 N = 1.24×10⁵ Pa at 60 mm) | N | measured (set) |
| fines threshold / fines fraction (DoE) | 100 / 25 ± 4 | µm / % | nominal (definitional) / measured |
| ε₀ range, compression experiments | 0.19–0.32 (at max stress) | − | measured |
| ε₀ range, extraction beds | 0.24–0.38 | − | measured (Table C.1) |
| K measured range | 1.8×10⁻¹⁴ – 3.6×10⁻¹³ | m² | measured (Darcy, 10 s → end window) |
| K consistency threshold | ε₀ ≲ 0.30 → consistent low-K shots | − | measured (observed, Fig. 14) |
| pump characteristic (ULKA N15) | not provided | — | — (measured by authors, curve not published; K values depend on it) |

Numeric flag inherited/confirmed: §1 quotes the literature permeability range as
"8×10⁻¹³ to 3×10⁻¹⁴ m²" citing Corrochano et al. — the same misquote already flagged on
`vacaguerra2025_leseprobe.md` (registry's carded primary range: 2.59×10⁻¹⁴–4.38×10⁻¹³ m²).
This paper is evidently the misquote's origin; do not propagate.

## Calibration and validation offered by the source
Compression model — the strong half. Fitted on FT4 powder-rheometer sweeps (6 PSDs ×
9 stresses × 3 samples); ANOVA surfaces: φ model R² = 0.96, adjusted 0.93, predicted 0.73
(Fig. 10); ω model R² = 0.91 / 0.87 / 0.71 (Fig. 11). Then validated in a DIFFERENT
device (texture analyzer), different vessels (60 mm stainless portafilter and 50 mm
acrylic), on 7 additional PSDs beyond the training set: measured vs. calculated dry
porosity R² = 0.93 (Fig. 12), holding over α = 224–484 µm, β = 1.3–2.27, fines 17–32 %,
up to 350 N. This is genuine cross-device, extended-range validation — by registry
validation-strength standards, experimentally gated on an independent apparatus, though
same lab, same single coffee. Wall-friction negligibility separately checked across three
vessel diameters/materials (Fig. B.1; differences within scatter).

Permeability Eq. 11 — the weak half. The exponents (4.3, 0.43) and λ = 7.5 are fitted to
the SAME 9 extraction operating points (3 PSDs × 3 dosages, Table C.1) that the equation
is then compared against; adjusted R² = 0.94 (Fig. 15). This is post-fit reconstruction,
not validation — 3 free parameters on 9 averaged points, one coffee, one machine, one
temperature. The authors themselves say applicability "still ha[s] to be tested" when
temperature, roast, fines fraction, or basket geometry change. Never cite Fig. 15 as
predictive skill.

## Assumptions and validity range
- Single material: one dark-roast 100 % arabica. Authors state coefficients (Tables 2–3)
  require recalibration for other roasts (roast alters particle porosity and granular
  mechanics). λ, 4.3, 0.43 similarly single-material.
- Compression model domain: α 224–484 µm, β 1.3–2.27, fines 17–32 %, σ up to 1.24×10⁵ Pa.
  Fines fraction is NOT an input; its non-influence is asserted from packing theory
  (small/large ratio ≈ 7–10) and only implicitly tested inside 17–32 %.
- Eq. 2 fits poorly below ~10 kPa (rapid rearrangement stage, §3.2) — acknowledged;
  espresso tamp range 30–60 kPa is inside the good region. No porosity floor: invalid as
  σ → ∞.
- Permeability uses the DRY bed porosity ε₀ as the predictor — a deliberate methodological
  choice (§Appendix C) NOT to consolidation-correct porosity, explicitly diverging from
  Corrochano et al.; bed consolidation δL (1.06–1.31 mm) corrects only L. Consequence:
  ε in Eq. 11 is not the same physical quantity as Corrochano's ε_ss, and the two closures'
  porosity axes are incommensurable without an adapter.
- Steady window only: averages from 10 s after first flow to shot end; the transient
  (which IS most of a real shot's character) is excluded, and the final wet-bed porosity
  "was not determined in this work."
- λ is a black box: swelling, fines migration, erosion, roughness are all folded in and
  explicitly cannot be separated (§3.7).
- Darcy regime assumed (Re_p < 10); no Forchheimer/inertial term. Flow is pump-limited
  (ULKA N15 curve measured but not published) — high-K rows of Table C.1 carry the pump
  characteristic implicitly.
- **µ convention conflict (G10):** K is computed with µ = 3.5 mPa s at 65 °C from their
  own unpublished measurement. Registry G10 sources (telisromero2000/2001) put coffee
  extract at espresso-window solids nearer ~0.5–1 mPa s at that temperature, and
  `romancorrochano2015` used hot-water viscosity at 80 °C. Since K ∝ µ at fixed (Q, ΔP),
  this inflates their K roughly 3–7× relative to the other carded conventions. Internal
  consistency is preserved (λ absorbed the choice), but cross-source K comparisons —
  including against the Wadsworth band and Corrochano Table 2 — must renormalize µ first.
  Discriminating computation: recompute K from Table C.1 under the G10 viscosity closure
  and re-fit λ; record both variants.
- Silent on: temperature dependence, pre-infusion/wetting, κ(t) evolution, CO₂, channeling,
  radial non-uniformity, any per-species extraction outcome (EY/TDS never measured here).

## Interface mapping
Inputs consumed: GrindState — partially. Needs (α, β) of the coarse fraction, d[3,2], ψ;
GrindState v0.1 carries only (setting, fines_fraction, boulder_radius_m, mean_radius_m).
Adapters needed: (i) the Sauter/sphericity adapter already named on the Corrochano cards;
(ii) a NEW Rosin–Rammler adapter (α, β) ↔ GrindState radii — β has no home in the current
contract and is this paper's central variable, making it the registry's most concrete
candidate for a GrindState extension (backlog "grind: PSD models beyond bimodal" — note
this stays inside the bimodal/100 µm-split framing, it just adds a width descriptor to the
coarse tail). (iii) Tamp stress σ is consumed but exists in NO contract — BedState.sigma
is the streamtube lognormal heterogeneity σ (brewer2026), a symbol collision that must not
be conflated; a tamp-stress field (packing input) would need adding.
Outputs produced: BedState.porosity (dry, pre-wetting — chain Eqs. 10 → 9 → 2) and a
BedState.k_m2 prior (Eq. 11). Couplings: offline calibration chain only — no runtime
component; σ_tamp + PSD → ε₀ → K, evaluated once per configuration. No coupling into
extraction or bed_dynamics is offered or implied.

## Extractable data
- **Table C.1 → data/vacaguerra2023a_tableC1.csv (PRIMARY).** 9 operating points:
  distribution × dosage (22.2/19.86/17.5 g) × (ε₀, ΔP ± sd, Q ± sd, δL ± sd). Enables:
  independent K recomputation, the µ-renormalization variant, the Eq. 11 sign/λ re-fit,
  and cross-evaluation against wadsworth2026.permeability on shared (ε, PSD) points.
- Tables 1–3 (PSD descriptors; ANOVA coefficients): small, fully transcribed above; this
  card is the record.
- Fig. 9 legend (ω, φ) per-PSD fit triplets: transcribed above.
- Fig. 8 (ρ_bulk vs. σ, 6 PSDs × 9 stresses, with error bars): digitization candidate ONLY
  if the sign-error gate forces a re-fit of Eqs. 9–10 from raw compression data; otherwise
  the surfaces + Fig. 12 suffice. Medium value, deferred.
- Figs. 12–15 are reproducible from the transcribed equations + Table C.1; do not digitize.
- No raw data, no code, no data-availability statement in the preprint.

## Overlaps and conflicts
- **`vacaguerra2025_leseprobe` (skip):** this card supersedes its Eqs. 1.9/1.10 skeleton —
  the parameters the excerpt lacked are here. Symbol-swap between the documents flagged
  above (leseprobe's ω is this paper's φ).
- **`wadsworth2026.permeability` (registered, packing/calibration):** direct COMPETITOR,
  with complementary domains — Wadsworth is validated untamped (φ_p 0.37–0.67) and
  extrapolates into the tamped regime; Eq. 11 is fitted exactly there (ε₀ 0.24–0.38) and
  nowhere else. Different functional families (percolation k(R, φ_p)·exp(αR) angularity
  vs. modified K–C with β^0.43). Named discriminating computation: evaluate both on the
  Table C.1 (ε₀, d[3,2], ψ, β) points after µ renormalization; divergence localizes where
  the Wadsworth tamped extrapolation (phi_c ~ 0.11 / screen-resistance question) breaks.
- **`romancorrochano2015` / `romancorrochano2017_permeability` (packing/calibration):**
  competes on the same question (K–C-family closure for RGC beds) with three deliberate
  methodological divergences: dry-ε₀ predictor vs. consolidation-corrected ε_ss;
  fresh-extracting bed (10 s → end) vs. fully-extracted 600 s pre-circulated bed; µ = 3.5
  mPa s brew vs. hot water. Both agree the monosized K–C prefactor is far too small
  (Corrochano fitted n → effective prefactors 196–1330; here 72λ² = 4050 with a steeper
  ε^4.3), but the numbers are not directly comparable across the porosity and viscosity
  conventions. Neither supersedes the other; carry both as rival BedState.k priors.
- **`abedi2025` (packing, skip):** superseded — this work is the "properly characterized
  measurement (with PSD and K)" abedi's card said to await: characterized PSDs, tamp-range
  stresses, a fitted stress–porosity closure, and negligible-wall-friction evidence
  (Fig. B.1) replacing abedi's uncharacterized φ_w narrative.
- **`brewer2026.pack_generator` (registered, packing/calibration):** complement — ε₀(σ; α, β)
  can supply the target porosity a generated pack should hit for a given tamp, but offers
  no microstructure; no conflict.
- **`cameron2020_si` deferred tamp question (Fig. S2, shot time vs. tamp force):** this
  paper supplies the missing σ → ε₀ link that would make that 16-point curve quantitative;
  if the tamp-sensitivity item ever activates, chain them.
- **Backlog "bed_dynamics: κ(t)":** untouched by design (dry-porosity predictor, static);
  the RTD/Bodenstein paper (leseprobe target 3, Vaca Guerra 2023b) remains the acquisition
  for that item.
- **Backlog "grind: PSD models beyond bimodal":** partially addressed — adds β as a second
  coarse-tail descriptor with demonstrated physical leverage, but stays inside the bimodal
  100 µm-split framing.

## Implementation estimate
Effort M. Two small algebraic closures plus one CSV, but gated: (Gate 1, blocking)
resolve the Eq. 9/10 sign error by regenerating Fig. 10/11 surfaces under both sign
conventions and the composed Fig. 13 surface — accept the variant matching all three;
(Gate 2) recompute Table C.1 permeabilities and re-fit λ under the G10 viscosity closure,
recording (λ_as-published, λ_renormalized) as dual variants; (Gate 3) cross-evaluate
Eq. 11 vs. wadsworth2026.permeability on the Table C.1 points. Dependencies: the
Sauter/sphericity adapter (exists as a named need), a new (α, β) Rosin–Rammler adapter,
and a decision on where tamp stress lives in the contracts (currently nowhere; symbol
collision with BedState.sigma must be avoided). Single-roast coefficients: mark the
component as material-scoped in the registry entry.

VERDICT: calibration-provider — the registry's first parameterized σ→porosity→K chain, with genuinely cross-device-validated compression surfaces and printed coefficients, landing exactly on the tamped regime where wadsworth2026 extrapolates; gated on a demonstrable printed sign error and a viscosity-convention renormalization, and its permeability closure is post-fit (R²=0.94 on its own 9 points), never blind-tested — effort M

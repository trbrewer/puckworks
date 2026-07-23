# Model card: Roman-Corrochano 2015 permeability (journal version of record)

**Paper/thesis:** Roman Corrochano, B., Melrose, J.R., Bentley, A.C., Fryer, P.J., Bakalis, S.
"A new methodology to estimate the steady-state permeability of roast and ground coffee in
packed beds." *Journal of Food Engineering* 150 (2015) 106–116.
DOI: 10.1016/j.jfoodeng.2014.11.006. Open access, CC BY 3.0.
**Stage(s):** packing (informs BedState.k / kappa priors) · **Kind:** calibration
**Status:** card-only

## Scope and mechanism
Peer-reviewed journal version of the SAME steady-state permeability campaign already carded
from the author's EngD thesis (`romancorrochano2017_permeability`, thesis Ch. 3.4.3 + Ch. 6)
and its conference precursor (`romancorrochano2013`, verdict skip). Darcy-law fits of
ΔP–Q data on fully-extracted, tamped + hydrodynamically-consolidated beds (4 bimodal grinds
A–D × 3 initial densities 360/400/480 kg m⁻³, triplicate), plus two Kozeny–Carman-family
closures: Model 1 (sphericity-weighted Sauter K–C) and Model 2 (porosity-dependent
tortuosity, Dias et al. 2006). No new physics relative to the thesis card; this card exists
to (i) fix the citable publication of record for the dataset and (ii) capture the fully
printed data tables, which the thesis card could only name as targets.

## Governing equations
Identical to `romancorrochano2017_permeability` (do not re-implement from here):
- Paper Eq. (1) = Darcy: Q = K A ΔP / (μ L) — Q volumetric flow rate (m³ s⁻¹), A bed
  cross-section (m²), ΔP pressure drop across bed (Pa), μ viscosity (Pa s), L bed length
  (m), K permeability (m²). Thesis equivalent: Darcy fit underlying Table 6.1.
- Paper Eq. (2) = thesis Eq. 3.39 (general capillary-bundle K–C, tortuosity τ, S_v).
- Paper Eq. (3)/(5a) = thesis Eqs. 3.40–3.41 (Model 1): K = ε³(Φd[3,2])² / (180(1−ε)²).
- Paper Eq. (4) = thesis Eq. 3.42: τ = (1/ε)ⁿ, n ∈ [0.4 loose, 0.5 dense] (Dias 2006).
- Paper Eq. (5b) = thesis Eq. 3.43 (Model 2): K = ε³(Φd[3,2])² / (72 (1/ε)²ⁿ (1−ε)²).
- Paper Eqs. (6a)–(9): density/porosity bookkeeping — ρ_bulk = ρ_particle(1−ε_bed);
  ρ_particle = ρ_solid(1−ε_particle); consolidation degrees λ_depth (8a), λ_length (8b),
  λ_average (8c); consolidation-corrected steady-state porosity
  ε_ss = (ε_bed − λ_avg)/(1 − λ_avg) (Eq. 9, after Hekmat et al. 2011).
Symbols otherwise as on the thesis card.

## Parameters
| symbol | value | units | source (measured/fitted/nominal/assumed) |
| --- | --- | --- | --- |
| d[3,2] (A/B/C/D) | 79.73±0.48 / 101.60±0.20 / 112.86±1.08 / 131.36±2.06 | µm | measured (Table 1, dry laser diffraction) |
| Φ sphericity (all grinds) | 0.75 | – | measured/averaged (per-grind means 0.71–0.80; single value adopted) |
| ρ_solid intrinsic | 1337 ± 2.31 | kg m⁻³ | measured (He pycnometry) |
| ε_particle open | 0.37–0.47 (no size trend) | – | measured (Hg porosimetry, 40 µm cutoff, θ=130° assumed) |
| ε_particle closed | 0.07–0.14 (rises with size) | – | measured (pycnometry difference) |
| ε_particle total | 0.50–0.57; 0.53 adopted | – | measured / assumed (single average used in Eq. 6b) |
| λ steady-state consolidation | 0 % (D, 480 kg m⁻³) – 31 % (A, 360 kg m⁻³) | – | measured |
| ε_ss (consolidated beds) | 0.12–0.33 | – | derived (Eqs. 6a + 9) — all below random-close-pack 0.36 |
| n fitted per grind (A/B/C/D) | 0.28 / 0.33 / 0.64 / 1.01 | – | fitted (R² 0.81–0.98; Fig. 15) |
| effective K–C pre-factor | 196–1330 | – | fitted (derived from n) |
| K experimental | see Extractable data (Table 2) | m² | measured (Darcy fit, R² > 0.97) |
| Re_p range | 0.04–4 | – | derived (laminar; Darcy justified) |
| water temperature | 80 | °C | nominal (set) |

Note: thesis card lists fitted n = 0.27 for the finest grind vs 0.28 in Fig. 15 here —
rounding-level discrepancy, harmless, recorded to avoid rediscovery. Grind mapping
A/B/C/D (paper) ↔ ΨB/ΨC/ΨD/ΨE (thesis), confirmed by matching d[3,2] and fitted n.

## Calibration and validation offered by the source
Same record as the thesis card, in published form. Darcy fits: R² > 0.97 throughout;
K = 2.59×10⁻¹⁴ – 4.38×10⁻¹³ m², consistent with King (2008)/Navarini et al. (2009).
As blind predictors both closures FAIL on these consolidated beds: Model 1 error grows
from 31 % (A) to 521 % (D); Model 2 with literature n = 0.5 improves only the coarse end
(338 % for D). Agreement requires FITTING n per grind (0.28–1.01), i.e. the closure is
descriptive, not predictive; fitted n exceeds the physical Dias range (≤0.5) at the coarse
end and absorbs unmodelled consolidation/structure effects. Circularity caveat: models are
tested against the authors' own K data using porosities corrected by their own
consolidation measurements — no independent dataset. Erratum-level note: the paper's prose
("values lie between 3.36×10⁻¹³ and 2.59×10⁻¹⁴") omits its own largest tabulated value
(4.38×10⁻¹³, grind D at 400 kg m⁻³); use Table 2, not the prose range.

## Assumptions and validity range
- Steady-state, FULLY-EXTRACTED beds only (600 s pre-circulation). Explicitly not valid
  during the first 60–80 s transient, i.e. the entire time window of a real espresso shot —
  the authors say so themselves and defer transient permeability to future work.
- Laminar Darcy regime (Re_p 0.04–4); no Forchheimer term.
- Single sphericity (0.75) and single total particle porosity (0.53) applied to all grinds.
- Dry-dispersed PSD as model input; authors note wet-measured d[3,2] would significantly
  under-predict K (no wet numbers given).
- Consolidation folded into a scalar porosity correction (Eq. 9); the paper's own
  conclusion is that this is insufficient (tortuosity/structure changes dominate).
- Silent on: swelling under pressure (flagged as unresolved), fines migration (transient
  reinterpreted as rig refill + wetting front, contra Petracco & Liverani 1993),
  temperature dependence of K, channelling.

## Interface mapping
Identical to `romancorrochano2017_permeability`: GrindState (Φ, d[3,2], fines_fraction) +
BedState.porosity → BedState.k as an OFFLINE calibration prior; Model 2 additionally needs
a fitted per-grind n supplied as input. No runtime coupling. No new adapters beyond the
Sauter/sphericity adapter already named on the thesis card. For data use, Table 2 rows map
directly onto (GrindState, BedState.porosity via ε_ss, BedState.k) tuples.

## Extractable data
- **Table 2 → data/romancorrochano2015_table2.csv** (PRIMARY; supersedes the thesis
  Table 6.1 transcription target — same campaign, but this is the DOI'd CC-BY version and
  the full table with SDs and Tukey groupings is printed). K (m²), mean ± SD of triplicate
  beds; letters = Tukey groups (α = 0.05):

  | grind | 360 kg m⁻³ | 400 kg m⁻³ | 480 kg m⁻³ |
  | --- | --- | --- | --- |
  | A | 7.65±0.82×10⁻¹⁴ (a,b) | 4.94±0.32×10⁻¹⁴ (c) | 2.59±0.25×10⁻¹⁴ (d) |
  | B | 1.37±0.08×10⁻¹³ (e) | 1.18±0.09×10⁻¹³ (e) | 4.87±0.09×10⁻¹⁴ (c) |
  | C | 2.39±0.49×10⁻¹³ (f) | 1.93±0.10×10⁻¹³ (f) | 6.44±0.35×10⁻¹⁴ (b) |
  | D | 3.36±0.58×10⁻¹³ (h) | 4.38±0.40×10⁻¹³ (g) | 8.95±0.75×10⁻¹⁴ (a) |

- Table 1 (d[3,2] per grind) and the porosity/consolidation constants above → provenance
  block of the same CSV.
- Fig. 6b (steady-state consolidation degree per grind × density), Fig. 7 (bulk density vs
  applied axial force, A–D), Fig. 13 (ε_ss vs d[3,2] × density) — plot digitising only if
  the wadsworth tamped-reconciliation gate needs per-bed ε_ss beyond the 0.12–0.33 range.
- Raw data/code: none published.

## Overlaps and conflicts
- SAME CAMPAIGN as `romancorrochano2017_permeability` (thesis) — this card does not
  compete with it; it is the publication of record for the dataset. Proposed division of
  labour: thesis card remains the equation/failure-mode record (it carries Ch. 6.4
  transient material absent here); THIS card is the data provenance anchor. Thesis card's
  "Table 6.1" extractable-data item should be redirected here (registry edit, changelog).
- SUPERSEDES `romancorrochano2013` for every purpose that card retained (the d[3,2]
  cross-reference now lives in Table 1 here).
- Same relation to `wadsworth2026.permeability` (registry #6) as the thesis card: the K–C
  closures are lower fidelity and non-predictive, but Table 2 supplies real
  TAMPED/consolidated (ε_ss 0.12–0.33) permeabilities that directly test Wadsworth's
  tamped extrapolation and the "φ_c ~ 0.11 or screen resistance" reconciliation.
- Feeds backlog "bed_dynamics: pressure/history-dependent kappa(t)": the 60–80 s transient
  and 0–31 % consolidation are the published trace of exactly that mechanism; note the
  authors' reinterpretation of the transient (rig refill + wetting front, not fines
  migration) as a documented counter-hypothesis.
- No new interaction with brewer2026.pack_generator or foster2025.infiltration.

## Implementation estimate
Effort S: transcribe Table 2 + provenance constants into data/; add a changelog entry
retargeting the thesis card's transcription item to this source; no equations to implement
(already carded, and weak as predictors). Gate design unchanged from the thesis card:
confront Table 2 tamped K with the wadsworth2026 tamped extrapolation and record the
outcome for the φ_c/screen-resistance question.

VERDICT: data-only — journal version of record for the already-carded thesis permeability
campaign; equations duplicate `romancorrochano2017_permeability` and remain non-predictive,
but the fully printed Table 2 (tamped-bed K with SDs and ANOVA groups) is the registry's
named transcription target with clean CC-BY provenance — take the table, skip the models —
effort S

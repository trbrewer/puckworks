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
Raw data/code: no authenticated Figure6.23 raw records or run-level pairing found in the bounded holdings check; this does not establish absence. Table6.1 is served by the2015 intake; Figure6.23 now has bounded raster readings (below).

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


## Figure 6.23 transient pressure-flow intake (2026-10-21)

[SCI-MD-CORROCHANO-PRESSURE-FLOW-001](../analysis/sci_md_corrochano_pressure_flow_001/RESULT.md)
adds `romancorrochano2017/fig6_23_pressure_flow_temperature`, loaded by
`rc17_fig6_23_pressure_flow()`. G1 / NO_GOVERNING_PHYSICS_CHANGE;
RESEARCH_ONLY / RETROSPECTIVE / TARGET_EXPOSED / SOURCE_INTERNAL.
PHYSICAL_VALIDATION=NOT_ESTABLISHED. No permeability mechanism is implemented.

Figure6.23 (printed266/PDF291) uses Psi_B, initial400kg/m³,15°C/80°C.
Three repetitions are stated; no authenticated individual pressure-flow pairing
is recovered. Native-image enclosures cover44/48 requested condition-panel slots;
the full60s bands exceed visible endpoints. One hot upper-flow fragment is
recoverable only over25–55s. Cold condition envelopes resolve a decline in
**inlet-referenced apparent conductance** Q_meter/DeltaP_bed_reported on both
separate grids. Complete hot-condition envelopes do not resolve temporal change;
the late hot fragment has a small secondary-grid recovery under the declared
reading bounds. Every supported cold condition envelope lies above the hot one.
These are finite figure-level comparisons, not individual physical-brew counts.

The upstream ultrasonic meter precedes the heaters; its volume reference and
mapping to through-bed discharge remain unqualified. Reported bed pressure
subtracts Q-dependent empty-cell losses from a pre-cell transducer; it is not a
direct two-tap differential. Figure3.3's printed positive-intercept polynomial
gives25200Pa at1e-5m³/s while the displayed calibration is near21000Pa. The intake
uses reported pressure, applies no second correction, and records low hot flows
below calibration observations and floor indications without physical-zero claims.
Generic20°C methods versus figure-specific15°C remain distinct. Figure6.20's
other-condition inferred viscosity and printed Pa s unit do not supply a
synchronized viscosity bound. Equal-alpha/common-geometry viscosity ratios are
explicitly conditional. See the source reconciliation for fixed-property,
pressure-equivalence, storage and timing premises. Same Corrochano/Melrose
campaign; historical steady-state tables and their evidence strengths unchanged.


## Figure 6.9 chamber/consolidation comparison (2026-10-21)

[SCI-MD-CORROCHANO-ASPECT-RATIO-CONSOLIDATION-001](../analysis/sci_md_corrochano_aspect_ratio_consolidation_001/RESULT.md)
adds `romancorrochano2017/fig6_9_aspect_ratio` and loader
`rc17_fig6_9_aspect_ratio()`: four vector-recovered means and eight displayed
error endpoints at initial 480 kg/m³ and nominal 80°C. G1 / research only /
retrospective / target exposed / source internal; NO_GOVERNING_PHYSICS_CHANGE.
PHYSICAL_VALIDATION=NOT_ESTABLISHED. No fitted thesis closure is implemented.

Fine Psi_B (journal A) mean ratio is 2.39754 [2.37198, 2.42385] under shared-axis
reading bounds; fixed adopted-average/grind-specific porosity routes predict
9.58008/5.55695 and require conditional residual prefactor ratios 0.25026/0.43145.
Coarse Psi_E (journal D) ratio is 0.93852 [0.936648, 0.940386] against nominal
equal-consolidation R_KC=1. These are nominal/reading mismatches, not physical
rejections. No coarse material fit, paired-bed prefactor or causal attribution.

Geometry contributes H0=4.32675 (equal initial volume) or 4.37838 (printed
dimensions), with a separate fine length factor 0.87. Under explicit common
viscosity/valid-observer premises, fine conductance ratios are 9.0250/9.1327 and
coarse 4.0607/4.1092. These are representative states, not mean bed conductances.
The source's full-chamber 10.37/4.06 arithmetic is reproduced separately.

The 13% Psi_B statement is supported by Figure6.1e's two-method average and
p.230, not the miscited Psi_C panel6.1b or Psi_B depth-only endpoint. Narrow bars
are linked to Table6.1/journal Table2 aggregate presentations without counting
them twice; exact bed identity and literal thesis 9.00 versus journal 8.95
precision remain unresolved. Wider-cell correction reused the original without
calibration, including wall losses; #349's polynomial/curve discrepancy persists.
Figure6.8 supports qualitative resistance ordering only. Actual merged
temperature-consolidation result remains inaccessible; synthesis is UNAVAILABLE,
not inferred or rerun. Same campaign, no production/EWP/lock change or successor.

## Figure 6.22 fixed reported-flow rescaling (2026-10-22)

[SCI-MD-CORROCHANO-HYDRATION-FLOW-RESCALING-001](../analysis/sci_md_corrochano_hydration_flow_rescaling_001/RESULT.md)
adds `romancorrochano2017/fig6_22_hydration_flow` and loader
`rc17_fig6_22_hydration_flow()`: six graphical histories,15 curve chunks,nine
bounded joins, original page coordinates. At Psi_E/initial400kg/m³ the reported
mean-flow ratio alone does not align published HR/HR_max under the declared
published-clock/support/graphical-reading contract. Both caption21/122 and
prose209/1220 separate complete represented-condition envelopes at PRIMARY
60/70/80s and SECONDARY65/75s. Caption60s D=[−0.249834,−0.044467] outward rounded.
26/30 rescaled and10/15 same-clock envelopes are complete; all requested
unsupported rows and nine descriptive graphical pairings are retained.

G1 / RESEARCH_ONLY / RETROSPECTIVE / TARGET_EXPOSED / SOURCE_INTERNAL /
NO_GOVERNING_PHYSICS_CHANGE / PHYSICAL_VALIDATION=NOT_ESTABLISHED.
HR_max rule/window, flow-mean window, common physical start and instrument-file
identities remain unauthenticated. Q_mean*t is a mean-throughput proxy, not
actual volume. No absolute-HR law, population behavior or mechanism is excluded;
no new campaign. Existing meter/corrected-pressure qualifications persist.
PDF/source artwork remain external; thesis rights are not the software licence.


## Dry-loading measurement constraint (Figure 6.2)

[SCI-MD-CORROCHANO-DRY-COMPACTION-001](../analysis/sci_md_corrochano_dry_compaction_001/RESULT.md)
adds `romancorrochano2017/fig6_2_dry_compaction` and loader
`rc17_fig6_2_dry_compaction`: twelve graphical sample curves, 76 unique vector
chunks painted twice, distinct legend provenance and full two-axis reading support.
Applied force (N) and dry bulk density (kg/m³) are preserved. Same-sample force
increments precede grind aggregation; the finite null permits only constant
sample-specific force offsets. All 156 declared sample requests and twelve grind
comparisons remain visible, including unsupported/ambiguous dispositions.
Source method: Z030 tester, nominal0.1 mm/s, maximum300 N; actual drawn endpoints
control reading support. Instrument IDs/calibration/zero and preparation histories
remain unresolved. Graphical bounds are not population or instrument uncertainty.
The original #352 source-internal, target-exposed analysis supplies no constitutive law,
modulus, wet-bed mechanism or EWP validation; its original scope did not test horizontal
density shifts. The qualified new comparison below extends only that named scope.
PHYSICAL_VALIDATION=NOT_ESTABLISHED; no independent campaign is added.


## Density-at-force additive offsets (Figure 6.2; 2026-10-22)

[SCI-MD-CORROCHANO-DENSITY-SHIFT-001](../analysis/sci_md_corrochano_density_shift_001/RESULT.md)
reuses the accepted `romancorrochano2017/fig6_2_dry_compaction` geometry. Under the
retained graphical-reading contract, the twelve represented dry-loading curves
cannot share one density-at-force response whose only sample-specific freedom is
a constant additive density offset: `rho_j(F_k)=b_j+h_k`, with unrestricted finite
constants and no fitted curve. Common density-calibration intercept cancellation
retains full independent trace allowances; the common positive slope scales the
page-coordinate contrast directly. Primary 25→250 N separates 5/66 sample pairs;
all 15 declared force intervals separate 10/990. All 72 readings, 180 increments,
990 sample comparisons, 60 complete grind envelopes and 90 grind comparisons are
retained with full support and zero ambiguity/numerical unresolved cases. All 90
complete-grind comparisons overlap; sample separation establishes no whole-grind
ordering. These counts are reporting rows, not independent replications.

B1−E2 at 25→250 N has common-scale contrast [2.831595, 33.989302] kg/m³, rounded
outward. Primary interval and B1/E2 were previously exposed; their preview values
were not inputs or regression oracles. The conclusion connects to horizontal
density shifts `F_j(rho)=G(rho-b_j)` only under a common single-valued inverse
loading branch over the tested forces. Arbitrary non-injective G with different
branch selections, both force and density offsets simultaneously, density
rescaling, relative-initial-state strain and broader preparation effects remain
untested. Separate rejection of force offsets in #352 and density offsets here
does not reject a common curve with both offsets. b_j is not measured initial density.

G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE / TARGET_EXPOSED /
SOURCE_INTERNAL. PHYSICAL_VALIDATION=NOT_ESTABLISHED. Graphical calibration does
not quantify or remove instrument calibration, force zero, compliance, initial
states or per-run preparation histories. No population/significance, modulus,
constitutive law, mechanism, wet-bed/permeability or EWP claim follows. Same dataset
and thesis/journal campaign; no new loader, cohort or experiment. #352's source,
producer, tests and historical analysis bundle remain byte-identical.

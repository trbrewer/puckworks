# Model card: Roman-Corrochano 2017 multi-scale extraction

**Paper/thesis:** Roman-Corrochano, B. "Advancing the Engineering Understanding of
Coffee Extraction." EngD thesis, University of Birmingham (submitted Dec 2015,
awarded 2017). No DOI assigned; University of Birmingham e-theses repository
(etheses.bham.ac.uk). Ch. 3 (models), Ch. 4–5 (particle scale), Ch. 7 (bed scale).
**Stage(s):** extraction, grind (microstructure→Deff), bed_dynamics (lumped bed) · **Kind:** runtime
**Status:** card-only

## Scope and mechanism
Diffusion-limited solid–liquid extraction resolved at two coupled scales. At the
particle scale, coffee grains are homogeneous spheres of fixed volume; a species
diffuses radially (1D) with an effective diffusion coefficient Deff, out through
a partition-controlled surface into a well-mixed liquid. The continuously bimodal
grind is discretised into size classes (baseline: a fine class ~40 µm and a coarse
class at d[4,3]); soluble solids may be one lumped species or several molecular-weight
species solved simultaneously. At the bed scale, the per-class particle flux feeds a
well-mixed (spatially lumped) bed pore concentration that is swept out convectively at
the column flow rate. External film resistance is neglected (Biot check + well-stirred
assumption); the bed is assumed fully wetted at t=0, so the wetting front is out of scope.

## Governing equations
Particle scale, for size class i and species β (thesis Eqs. 3.28–3.34):

Diffusion (Fick's 2nd law, spherical):
- (3.28) ∂C_s,i^β/∂t = Deff,i^β ( ∂²C_s,i^β/∂r² + (2/r) ∂C_s,i^β/∂r )
- (3.29) IC: t=0, C_s,i^β = C_s,i,0^β for 0≤r≤R_i
- (3.30) BC centre: ∂C_s,i^β/∂r = 0 at r=0 (symmetry)
- (3.31) BC surface: C_s,i^β = C_b,i^β / K_i^β at r=R_i (partition equilibrium; no film resistance)

Flux out of a class and bulk build-up:
- (3.32) J_i^β = −Deff,i^β (∂C_s,i^β/∂r)|_{r=R_i} · ( ν_i m / (V_i ρ_particle) )
  — flux from the average particle scaled by the number of particles in the class
- (3.33) C_b,pre^β(t) = ( ∫₀^texp Σ_i J_i^β · 4π(R_i Φ)² dt ) / V_b
- (3.34) y_pre(t) = ( Σ_β C_b,pre^β V_b ) / m

Bed scale (thesis Eqs. 3.35–3.38). Full PDE:
- (3.35) ∂C_bed,i^β/∂t = Σ_i [3(1−ε_bed)/(ε_bed R_i)] ν_i J_i^β − u_p ∂C_bed,i^β/∂z

Reduced to an ODE via the del Valle & de la Fuente (2006) linear-axial-profile
simplification (valid when bed length ≈ 2·bed radius):
- (3.36) dC_bed,i^β/dt = Σ_i [3(1−ε_bed)/(ε_bed R_i)] ν_i J_i^β − Q C_bed,i^β/(V_bed ε_bed)
- (3.37) yield y_pre(t) = ( ∫₀^texp Σ_β Σ_i C_bed,i^β Q dt ) / m
- (3.38) strength S_pre(t) = ( ∫₀^texp Σ_β Σ_i C_bed,i^β Q dt ) / ( ∫₀^texp Q dt )

At the bed scale the particle surface BC (3.31) uses C_bed in place of C_b.

Symbols: C_s = concentration in solid pore space (kg m⁻³); C_b / C_bed = liquid
concentration (bulk vessel / bed pore); r radial coord, R_i class radius (m);
Deff effective diffusion coefficient (m² s⁻¹); K partition coefficient (–);
ν_i class volume fraction (–); V_i average-particle volume, V_b vessel volume,
V_bed bed volume (m³); m coffee mass (kg); ρ_particle particle density (kg m⁻³);
Φ sphericity (–); ε_bed bed porosity (–); u_p pore velocity (m s⁻¹); Q flow rate
(m³ s⁻¹); z axial coord; i size class, β species.

## Parameters
| symbol | value | units | source (measured/fitted/nominal/assumed) |
| --- | --- | --- | --- |
| Deff (low MW, caffeine proxy) | 19.2–37.0 ×10⁻¹¹ (per grind) | m² s⁻¹ | measured (microstructural, Table 4.9, 80 °C) |
| Deff (medium MW, galactomannan DP20) | 5.5–10.6 ×10⁻¹¹ | m² s⁻¹ | measured (Table 4.9, 80 °C) |
| Deff (high MW, galactomannan DP45) | 1.8–3.7 ×10⁻¹¹ | m² s⁻¹ | measured (Table 4.9, 80 °C) |
| Deff (very high MW) | 0.079–0.16 ×10⁻¹¹ | m² s⁻¹ | measured (Table 4.9, 80 °C) |
| Db (caffeine, 80 °C) | 18.9 ×10⁻¹⁰ | m² s⁻¹ | nominal (Poling et al. 2008) |
| Db (med/high/vhigh MW, 80 °C) | 54.3, 18.7 ×10⁻¹¹; 7.7–8.5 ×10⁻¹² | m² s⁻¹ | measured/estimated (Stokes–Einstein + DLS, Table 3.4) |
| Hm (microstructural hindrance) | 5–10 (rises with grind size) | – | measured (τ_particle/ε_total, Table 4.8) |
| K (partition, S=1) | 0.42 (20 °C), 0.57 (50 °C), 0.61 (80 °C) | – | fitted (equilibrium data, Table 4.10) |
| y₀ (extractable SS, finest grind ΨA) | 31.7 ± 0.4 (dilute); 32.15 (equilibrium) | kg SS / 100 kg RGC | measured |
| sphericity Φ | ~0.75 (decreases with size) | – | measured |
| ε_particle (total) | 0.50–0.65 (ΨE 0.57; avg 0.53) | – | measured (He pycnometry + Hg porosimetry) |
| τ_particle (CPSM) | 3–7 (rises with grind size) | – | measured (Hg hysteresis, CPSM) |
| fine-class mean size | ~40 (biological cell) | µm | measured |
| swelling factor S | 1 (no swelling observed) | – | assumed/measured |
| Deff used for espresso demo (ΨE, low MW, 85 °C) | 25.7 ×10⁻¹¹ | m² s⁻¹ | measured (this work) |

## Calibration and validation offered by the source
Stirred-vessel (particle scale): with a single fitted Deff, MPE 6–17 %; the curve
could NOT be fully described by one Deff because of chemical heterogeneity, so four
MW-class Deff improve agreement to MPE 5–8 % (Table 5.3, Fig. 5.11/5.13). These are
fits, not blind predictions.
Bed scale: the strongest claim is parameter-free — using the microstructural
(non-fitted) medium-MW Deff, predicted espresso yields gave MPE 9–14 % across all 15
tested flow/density conditions (Fig. 7.4, Ch. 8 conclusion). Authors call this
"acceptable... no parameters were fitted."
External espresso data: model reproduced literature cumulative profiles for caffeine,
trigonelline and chlorogenic acids from Illy Hyper-espresso (Navarini et al. 2008) and
a traditional machine (Caprioli et al. 2014), using average (not time-resolved) flow
and K=1 (Fig. 7.21). Caveat stated by the author: average-flow input under-predicts
early time; nicotinic acid's linear profile was NOT captured. Espresso comparisons are
dimensionless-yield overlays (visual), not tabulated error.

## Assumptions and validity range
- Diffusion is rate-limiting; wetting/penetration assumed instantaneous (capillary,
  contact-angle evidence). Silent on the transient wetting front (bed assumed wet at t=0).
- No swelling; fixed particle volume; homogeneous sphere of fixed Φ.
- No external film resistance (Biot small); well-mixed vessel / well-mixed bed pore space.
- Bed model is spatially lumped: axial concentration assumed linear (valid only for
  L ≈ 2·R_bed); no axial dispersion; convection axial only. Not a resolved 1D column.
- Deff concentration-independent (dilute limit). Single K per species; K(T) fit on only
  3 points (Arrhenius R²=0.91).
- Microstructural Deff derived on DRY grinds → Hm likely over-estimated vs wetted (author
  flags 8–9 here vs Spiro's ~4). Validated regime: 72–85 °C, ~1 ml s⁻¹ espresso flow,
  6.5–7.5 g beds, low-to-medium MW species. Silent on temperature transients, aroma/gas,
  and per-species chemistry beyond the 4 MW proxies.

## Interface mapping
Inputs consumed: GrindState (fines_fraction, mean/boulder radius → size classes;
sphericity) ; BedState (porosity, dose, depth, area, k for flow) ; MachineState
(P_of_t/profile → Q). Needs Deff per class (from grind microstructure) and K.
Outputs produced: ShotResultState (EY_pct via y_pre, tds_pct via S_pre, traces).
Couplings: RUNTIME in the extraction chain. Particle→bed coupling is the flux term J_i^β
(runtime). Deff-from-microstructure is an offline CALIBRATION provider (Table 4.9 → k/Deff
priors). Adapters: contract has one Deff/κ per bed; this model wants per-size-class,
per-MW-species Deff arrays → needs a multi-species/multi-class adapter. The lumped-bed
ODE is an alternative solver to a resolved column, so a solver-mode flag is needed.

## Extractable data
- Table 4.9 → data/romancorrochano2017_deff_mw.csv: parameter-free microstructural Deff,
  80 °C, 8 grinds × 4 MW classes with uncertainties (HIGH value — a full grind→Deff map).
- Table 4.10 → K(T) at 20/50/80 °C, S=1.
- Table 3.4 → Db by MW category (proxy compounds, hydrodynamic radii).
- Table 4.6/4.7/4.8 → particle porosity, CPSM tortuosity, Hm by grind.
- Ch. 5 fitted Deff tables (5.2–5.6) and MPE tables; Ch. 7 flow/temperature conditions
  (Tables 7.1–7.2) and espresso demo parameters (Table 7.5).
Raw data/code: no repository published; figures are extraction-yield curves (transcribe
from plots). Tables above are directly transcribable from the PDF.

## Overlaps and conflicts
- COMPETES with cameron2020.extraction_bdf (registry #1): both are runtime saturated
  diffusion+dissolution extraction with a fines/coarse two-population grind. Differences:
  Cameron adds nonlinear surface dissolution and a per-bed-volume inventory (EY ceiling
  29.6 %); Roman-Corrochano is pure Fickian diffusion + partition BC, adds an explicit
  MW-resolved Deff spectrum and a parameter-free microstructural Deff route, but uses a
  LUMPED bed (linear axial profile) vs Cameron's resolved column. Complementary on the
  "EY ceiling / entrapment" question: y₀ decreasing with coarser grind (size-exclusion
  entrapment) is an independent mechanism for the same fine-grind behaviour Cameron
  hits via inventory.
- COMPLEMENTS brewer2026.streamtube: offers an alternative (chemical heterogeneity, not
  channelling) explanation for why one Deff/one closure under-fits — discriminable data.
- Speaks to backlog "extraction: multi-class solute chemistry" (4 MW proxies → testable)
  and "infiltration↔extraction coupling" (this model explicitly assumes wet-at-t=0, the
  gap foster2025 fills).

## Implementation estimate
Effort M. Particle-scale spherical diffusion PDE (method-of-lines, already the registry's
comfort zone) plus a lumped-bed ODE — both were solved in COMSOL but are elementary to
reimplement. Real cost is the multi-species/multi-class bookkeeping and a solver-mode flag
for lumped vs resolved bed. Gate design: (i) reproduce stirred-vessel MPE 5–8 % with 4-MW
Deff on a transcribed curve; (ii) parameter-free bed gate — feed Table 4.9 medium-MW Deff,
require MPE ≤14 % on the espresso conditions; (iii) cross-check y₀ entrapment vs Cameron's
EY ceiling. Dependency: transcribe Table 4.9/4.10 first.

VERDICT: implement-later — strong parameter-free grind→Deff→espresso-yield chain that
directly stress-tests Cameron, but the lumped bed and dry-grind Hn caveats make it a
second extraction reference rather than a first; land the Table 4.9 data now — effort M.

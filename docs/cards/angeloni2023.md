# Model card: Angeloni/Giacomini 2023 3D multi-species percolation (FeFlow)

**Paper:** Angeloni, S.; Giacomini, J.; Maponi, P.; Perticarini, A.; Vittori, S.; Cognigni, L.; Fioretti, L. "Computer Percolation Models for Espresso Coffee: State of the Art, Results and Future Perspectives." *Appl. Sci.* **2023**, *13*, 2688. DOI 10.3390/app13042688
**Stage(s):** extraction · flow · observables · **Kind:** calibration
**Status:** card-only

## Scope and mechanism
Full 3D saturated percolation of an espresso puck: Richards + Darcy flow, an advection–diffusion–reaction (ADR) equation for **each of 8 named chemical species** (caffeine CF, total chlorogenic acids CQA, trigonelline TR, citric CA, acetic AA, tartaric TA, ferulic FA, lipids LP), a companion solid-phase balance per species, and a convective–diffusive heat equation — all solved as one coupled system in FeFlow Demo 7.2 on a cylindrical VST-basket domain. Extraction from grain to liquid is a first-order-in-solid dissolution term (their Eq. 8) whose rate α is a fitted polynomial in water temperature and pressure (Eq. 9). This is the multi-species, spatially-resolved successor to the same group's Giacomini 2020 [their ref 17]; imbibition (first 5 s) is explicitly excluded — the model runs post-wetting on a saturated bed. Its practical value to puckworks is the **per-species chemical campaign** (66 shots, Arabica + Robusta), not the coupled solver.

## Governing equations
System (1), in cylinder C for t ∈ (0, τ), with Q = 0 imposed for the coffee case (no internal water source/sink):

1. **Richards (mass):** S₀ ∂h/∂t + ∇·q = Q
2. **Darcy:** q = −K f_μ · (∇h + χ e)
3. **ADR, liquid/solid species k** (k = CF, CQA, TR, CA, AA, TA, FA, LP; N_ls = 8):
   ε ∂C_k/∂t + q·∇C_k + ∇·j_k = R_k − C_k Q, with Fick flux j_k = −D_k·∇C_k
4. **Solid species m** (N_s = 8, one per species, superscript s = matrix-bound):
   ε_s ∂C_m^s/∂t = R_m^s, ε_s = 1 − ε
5. **Heat:** (ε ρ_c + ε_s ρ^s c^s) ∂T/∂t + ρ_c q·∇T − ∇·(Λ·∇T) = H_e − ρ_c(T − T₀)Q

Hydrodynamic dispersion tensor, their Eq. (2):
6. D_k = [ε D_k + β_T^k ‖q‖] I + (β_L^k − β_T^k) (q⊗q)/‖q‖
   *(symbol collision: D_k denotes both this tensor and, inside it, the scalar molecular diffusivity — flagged, not resolved by the authors.)*

Thermal hydrodynamic conductivity tensor, their Eq. (3):
7. Λ = [ε Λ + ε_s Λ^s + ρ_c γ_T ‖q‖] I + ρ_c(γ_L − γ_T) (q⊗q)/‖q‖
   *(same reuse: Λ is both the fluid thermal conductivity and the assembled tensor.)*

Dissolution / reaction closure, their Eq. (8):
8. R_k = −α_k (1 − ε) C_k^s , R_k^s = +α_k (1 − ε) C_k^s
   First-order in solid loading; **no saturation cap and no liquid-concentration deficit term** — all T,p sensitivity is pushed into α_k (contrast Cameron/Egidi, which carry a c_sat cap and a deficit driving force).

Dissolution-rate surrogate, their Eq. (9), per species k, granulometry r ∈ {O,C,F}, variety v ∈ {A,R}:
9. α_k^{r,v} = A₀ + a T_z0 + b p_z0 + c T_z0² + d p_z0² + f T_z0 p_z0 + l T_z0² p_z0 + m T_z0 p_z0²
   Coefficients {A₀,a,b,c,d,f,l,m} in Appendix A (Tables A1–A6); l,m are nonzero only for CQA, so most species use 6 fitted coefficients.

Boundary/initial conditions: hydraulic head Eq. (4) (Dirichlet h=h_z0 on top Γ₁; no-flow on lateral Γ₂; filter-admittance outflow q·n = −Φ_h min{h_C − h, 0} on bottom Γ₃; pressure IC p = p₀(z)); species Eq. (5) (Neumann on Γ₁,Γ₂; admittance outflow −(D_k∇C_k)·n = −Φ_k min{C_kC − C_k, 0} on Γ₃; C_k(·,0)=0); solid IC Eq. (6) C_m^s = C₀^s; temperature Eq. (7) (T=T_z0 on Γ₁; Neumann on Γ₂,Γ₃; T=T₀ IC). Linear initial pressure profile p₀(z) = (z/−H)(1 − p_z0) + p_z0 *(dimensionally inconsistent as printed — mixes a bar-valued p_z0 with the dimensionless (1 − p_z0) factor; almost certainly a normalization typo).*

Symbols: h hydraulic head [m], h = ψ + z, ψ = p/ρ₀g; q Darcy flux; S₀ specific storage; K hydraulic-conductivity tensor; f_μ viscosity relation and χ buoyancy coefficient (**functional forms never given in the paper**); ε porosity, ε_s = 1−ε; C_k liquid conc., C_k^s solid conc.; D_k molecular diffusivity; β_L,β_T longitudinal/transverse dispersivity; R_k, R_m^s reaction rates; α_k dissolution rate; Φ_h, Φ_k filter admittances; C_kC concentration threshold; T temperature, T_z0 inlet-water temp, T₀ initial bed temp; ρ_c, ρ^s c^s fluid/solid volumetric heat capacity; Λ, Λ^s fluid/solid thermal conductivity; γ_L,γ_T thermal dispersivities; H_e heat source (taken 0, not stated explicitly).

## Parameters
| symbol | value | units | source (measured/fitted/nominal/assumed) |
|---|---|---|---|
| ε_O / ε_C / ε_F | 0.305 / 0.330 / 0.276 | – | nominal (ε_O from literature mean; ε_C,ε_F scaled by PSD fines-peak volume rule) |
| K = k_r(p_z0), optimal | 2.60e−9 p² − 6.50e−8 p + 5.08e−7 | (m/s, p in bar) | fitted (interpolated to match numerical↔real flow rate) |
| K = k_r(p_z0), coarse | 3.90e−9 p² − 1.05e−7 p + 8.50e−7 | (m/s) | fitted |
| K = k_r(p_z0), fine | 1.20e−9 p² − 3.17e−8 p + 2.56e−7 | (m/s) | fitted |
| h_z0 (6/9/12 bar) | 61.18 / 91.78 / 122.37 | m | derived (h_z0 = p₀(0)/ρ₀g, ρ₀=1000) |
| Φ_h | 6.5e−5 | 1/s | fitted (trial-and-error) |
| h_C | 0 | m | assumed |
| Φ_k (all species) | 30 | mm/s | fitted (trial-and-error) |
| C_kC (all species) | 0 | mg/L | assumed |
| C₀^s Arabica (CF/CQA/TR/CA/AA/TA/FA/LP) | 12540 / 22130 / 7970 / 39970 / 11870 / 7700 / 790 / 138700 | mg/L (=mg/kg, 1 kg=1 L assumed) | measured (R&G assay, §3.1) |
| C₀^s Robusta | 18580 / 16080 / 5960 / 40920 / 27910 / 5970 / 1060 / 96200 | mg/L | measured (R&G assay) |
| S₀ | 1e−3 | 1/m | nominal (hydrogeology default; dubious for a rigid puck) |
| β_L / β_T | 1 / 0.1 | m | nominal (groundwater default; **≫ bed depth**) |
| D_k (all 8 species) | 1e−9 | m²/s | nominal (uniform across species incl. lipids) |
| ρ_c | 4.18 | MJ/(m³·K) | nominal |
| ρ^s c^s | 3.184 | MJ/(m³·K) | nominal |
| Λ (fluid) / Λ^s (solid) | 0.673 / 0.337 | W/(m·K) | nominal |
| γ_L / γ_T | 0.5 / 0.05 | m | nominal (≫ bed depth) |
| τ_O / τ_C / τ_F | 20 / 13 / 35 | s | measured (per-granulometry shot time) |
| T₀ (initial bed temp) | 70 **(text)** vs 100 **(Table 8)** | °C | nominal — **internal conflict, flagged** |
| R (basket inner radius) | 29.25 | mm | measured (VST Competition) |
| H (bed height) | 13.88 | mm | measured (mean; swelling/consolidation neglected) |
| mesh | 3486 prisms / 2160 nodes / 8 cross-sections | – | assumed |
| α_k^{r,v} coefficients | Tables A1–A6 (A₀ ranges ±10⁴–10⁶) | (mixed) | fitted (response-surface regression, no physical interpretation) |

Never provided: f_μ, χ closures; H_e; K tensor units (inferred m/s from head balance); molecular diffusivity per-species differentiation.

## Calibration and validation offered by the source
**This is a fitted surrogate, and the validation tests interpolation, not mechanism.** The dissolution rate α_k(T,p) is a per-species × per-granulometry × per-variety polynomial (Eq. 9, up to 8 coefficients each, Tables A1–A6), fitted by an approximation problem to reproduce the lab chemical assays; the hydraulic-conductivity law k_r(p), the admittances Φ_h,Φ_k, and thresholds C_kC are also tuned by trial-and-error. Because all T,p dependence lives in the fitted α, the mechanistic core (Eq. 8, first-order in solid loading) carries little independent predictive weight.

Calibration grid: 27 (T,p,granulometry) points per variety (T = 88/93.4/98 °C, p = 6/9/12 bar, r = O/C/F), dose 20 ± 0.1 g, beverage 40 ± 2 g, 1:2 ratio, tamp 20 kgF, duplicates. Calibration agreement (Figs. 3–18, Arabica + Robusta): "good" for CF, CQA, TR, TA, FA; weaker for CA, AA, LP (numerical curves smooth over lab peaks; AA's dissolution coefficient is "not smooth"). In-silico beverage volume 39.4–40.9 cm³ (brackets 40 ± 2). 

Validation: **6 off-grid (T,p) points per variety** at the same granulometries/varieties (Tables 9–10), i.e. interpolation inside the fitted (T,p) envelope. Mean % error per species (Table 11): Arabica CF 9.1, CQA 9.4, TR 10.4, CA 31.0, AA 40.2, TA 9.7, FA 9.8, LP 27.5; Robusta CF 9.2, CQA 13.6, TR 11.7, CA 11.3, AA 19.5, TA 11.1, FA 13.7, LP 45.5. Per-point errors reach 96% (Arabica CA), 76% (Arabica LP), 157% (Robusta LP, point (96,9,O)). Author self-assessment: "mean error around 10% in most cases," CA/AA/LP explicitly the worst. **Read this as a response-surface interpolation check, not a validation of extraction physics.** No independent test set (different machine/coffee/basket), no held-out granulometry or variety, no positivity/mass-conservation proof stated for this coupled implementation. Coincidentally strong per-compound EY figures (CF 82.6/80.5%, CQA 75.4/75.7%, OA 83.2/86.5%, FA 71.8/74.8%, TR 85/92% for A/R) come from the assay, not the model.

## Assumptions and validity range
- Post-imbibition saturated bed; first 5 s (wetting) discarded — no first-drip transient, no dry-front (contrast foster2025).
- Isotropic, homogeneous porous medium; porosity set by granulometry alone (tamp, swelling, consolidation neglected; fixed H = 13.88 mm).
- Fines (< 100 µm) erosion/transport dropped ("does not significantly interfere"); crema/clog phenomena out of scope by the authors' own statement.
- Dissolution has **no saturation cap and no concentration-deficit driving force**; α absorbs all T,p behavior, so extrapolation outside the fitted 88–98 °C / 6–12 bar box is unsupported.
- Uniform molecular diffusivity 1e−9 m²/s for all species including lipids; dispersivities (β 1 m, γ 0.5 m) far exceed the 14 mm bed — physically these are groundwater-scale numbers reused wholesale, effectively strong numerical dispersion.
- Blends assumed to interpolate linearly between pure Arabica and Robusta (asserted, not tested).
- Validated only within: VST 20 g basket, 1:2 ratio, τ 13–35 s, the specific Simonelli/Victoria Arduino machine + Mythos grinder, one Arabica and one Robusta blend. Silent on: gushers/chokes, non-cylindrical baskets (claimed as a strength but not shown), lungo ratios, other equipment, the T₀ discrepancy's effect on heat transport.
- Numerics: FeFlow Demo 7.2 (closed proprietary solver), Kantorovich semidiscretization, quadratic/linear Galerkin, Adams–Bashforth/Crank–Nicolson; not independently reproducible without the tool.

## Interface mapping
Inputs consumed: **GrindState** (granulometry → ε_O/C/F and the k_r(p) branch; fines_fraction unused, fines discarded); **BedState** (depth_m ↔ H, area ↔ R, porosity ↔ ε; note their K is a *fitted hydraulic conductivity*, not our k_m2 permeability); **MachineState** (bar overpressure → h_z0 and k_r(p); inlet temperature → T_z0). Initial solid inventory C₀^s (Table 7) is an external measured input.
Outputs produced: **ShotResultState** — per-species cup amounts (→ traces), EY_pct (per species, via C₀^s and cup mass), tds (from total-solids assay lineage), beverage_g (in-silico 39.4–40.9 cm³).
Couplings: a **mega-coupled runtime** (Richards + Darcy + 8×ADR + 8×solid + heat) that would force flow, heat, and extraction into one solver — the failure mode puckworks avoids. Adapters required if ever run: bar→hydraulic-head (h_z0 = p₀(0)/ρ₀g), our κ/k_m2→their K (a permeability-to-conductivity, and then a *fit-to-flow* map, which is not physically portable), and the machine-specific α(T,p) surrogate. **Prefer offline data intake**; coupling is not recommended.

## Extractable data
- **Tables 4 + 5 → data/angeloni2023_bioactives.csv** — per-species g/L (TR, TA, AA, CA, 3-CQA, 5-CQA, CF, FA, 3,5-diCQA, plus totCQA, totOA) for all 66 shots (33 Arabica + 33 Robusta) with T/p/granulometry from Table 1. **Highest value in the paper** — directly serves the "multi-class solute chemistry" backlog; independent of Cameron and of egidi2024 (different varieties, wider T×p×grind design, resolved acids).
- **Table 2 → data/angeloni2023_total_solids.csv** — 66 shots, TS (g/100 mL) + %RSD.
- **Table 3 →** total lipids (g/100 mL) + %RSD, 66 shots.
- **Table 7 →** measured R&G source concentrations C₀^s per species per variety (extraction inventory priors).
- **Table 1 →** the 66-shot condition matrix (T, p, r) including 12 off-grid points.
- Tables 9–11 → per-species validation errors (useful as an accuracy benchmark if we ever fit our own surrogate on this data).
- §3.1.2 prose → per-compound EY (A/R) and R&G g/kg assays.
- Appendix A (A1–A6) → α(T,p) coefficients, only if replicating their dissolution surrogate.
- Fig. 2 → Arabica/Robusta PSD curves (grind backlog, low priority).
- Availability: "Data are contained within the article" — **no repository, no code** (proprietary FeFlow), no raw HPLC traces. Transcription from the article tables is the only route.

## Overlaps and conflicts
- **cameron2020.extraction_bdf (complements; does not supersede):** both extraction runtime. Cameron is a single lumped solute with a per-bed-volume inventory (EY ceiling 29.6%) and a mechanistic deficit law; this is 8 named species but via a machine-specific fitted α(T,p) and a mega-coupled 3D solver with no saturation cap. Lower mechanistic interpretability — no reason to swap runtimes — but its **per-class solute data give targets Cameron's single-species model cannot currently be tested against.**
- **egidi2024 (sibling; complementary data):** same group, later 1D single-species RBF model, also VERDICT data-only. Its EY/TDS campaign (Arabica, 2 T × 2 p × 3 grind) and this paper's per-species campaign (A+R, 3 T × 3 p × 3 grind, 8 species) are *different, non-overlapping datasets* — hold both.
- **Backlog "extraction: multi-class solute chemistry" — primary hit.** This paper is the best data intake seen for that slot (supersedes the earlier-flagged Giacomini 2022 reduced model as a *data* source; that ref is a lower-fidelity multi-species solver, this one ships the assays).
- **Backlog "observables: temperature effects":** the heat equation + T-dependent α touch this, but as a fitted surrogate on one machine — weak as a temperature model; the data (T-resolved species) is the usable part.
- **wadsworth2026.permeability / flow backlog (no conflict):** their K is fitted to reproduce measured flow, not an independent permeability; it neither validates nor competes with the percolation-k work — it simply sidesteps permeability.
- **foster2025.infiltration (complements/conflicts):** this model discards imbibition, exactly foster2025's domain; the infiltration↔extraction coupling backlog item would supersede the saturated-start assumption here.

## Implementation estimate
Data intake: **S** — transcribe Tables 4+5 (the multi-species csv), Tables 2/3/7, and the condition matrix (Table 1); add an extraction-gate case that checks whether our chain lands within these per-species ranges at matched (T,p,grind). No runtime port recommended: the coupled FeFlow system would be **L** to reimplement, would force runtime coupling of flow/heat/extraction, depends on a proprietary solver and a non-portable fitted α(T,p), and would duplicate cameron2020 at lower interpretability. Gate design: per-species amount bracketing by (variety, granulometry), mirroring Tables 9–11.

VERDICT: data-only — the coupled FeFlow model is a mega-coupled system with a machine-specific fitted α(T,p) response surface (validation is interpolation within the fit, not mechanism), but Tables 2–5 and 7 are the richest independent multi-species extraction dataset in the registry and land squarely on the "multi-class solute chemistry" backlog — effort S

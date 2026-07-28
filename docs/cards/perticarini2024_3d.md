# Model card: Perticarini 2024 3D percolation model + RBF head-only flow solver

**Thesis:** Perticarini, A. "Predictive Models in Espresso Coffee Percolation." Ph.D. thesis, Università degli Studi di Camerino, School of Advanced Studies, Materials Sciences, XXXVI cycle. PDF dated Nov 2023, deposited 28 Feb 2024. No DOI. Chapter 2 §2.3 + Chapter 4 §4.2 (3D model) and §4.3 (RBF flow solver).
**Underlying publications:** the 3D model is Giacomini, Khamitova, Maponi et al., *Int. J. Multiphase Flow* (2020) [thesis ref 23]; the calibration/validation campaign is **Angeloni et al., *Appl. Sci.* 13:2688 (2023) [ref 24] — already registered as angeloni2023**.
**Stage(s):** extraction · flow · observables · **Kind:** calibration
**Status:** card-only

## Scope and mechanism
Full 3D saturated percolation on a cylindrical VST-basket domain: Richards + Darcy for the
hydraulic head, an advection–dispersion–reaction equation per chemical species with a
companion solid-phase balance, and a convective–diffusive heat equation, solved as one
coupled system. Eight species (CF, CQA, TR, CA, AA, TA, FA, LP), Arabica and Robusta,
33 shots each. This is a re-presentation of the already-registered angeloni2023 — same
system, same closures, same parameters, same calibration and validation tables, same FeFlow
Demo 7.2 solver. §4.3 adds the one element not in angeloni2023: the **flow subsystem alone**
(Richards + Darcy, no species, no heat) re-discretised with polyharmonic RBF collocation in
MATLAB, run at three inlet pressures as a preliminary check of the discretisation.

## Governing equations
System (2.75) with BCs (2.76)–(2.79) is equation-for-equation the system already transcribed
in full on **angeloni2023** (their system (1), Eqs. (2)–(9), BCs (4)–(7)). Not re-transcribed
here. Correspondence: thesis (2.75)₁ = Richards S₀ ∂h/∂t + ∇·q = 0; (2.75)₂ = Darcy
q = −K f_μ(∇h + χe); (2.75)₃ = species ADR ε ∂C_k/∂t + q∇C_k + ∇·j_k = R_k; (2.75)₄ = solid
ε_s ∂C_k^s/∂t = R_k^s; (2.75)₅ = heat. Dissolution closure (4.28) = angeloni Eq. (8);
α_k^{r,v}(T,p) polynomial (4.29) = angeloni Eq. (9), same eight coefficients, same Tables.
Derivation detail the journal paper omits and the thesis supplies: the specific storage is
S₀ = gρ(εβ + C_v) with C_v = dε/dp a consolidation coefficient and β the water
compressibility (their 2.59–2.65) — i.e. **S₀ nominally encodes bed consolidation**, then is
set to a constant hydrogeology default, which is worth recording as a route the lineage left
unused (relevant to the kappa(t) compaction backlog, though no coffee-specific C_v is given).

§4.3 solves only the flow subsystem, their (4.30), by PA-RBF collocation (polyharmonic r³,
m = 3) in space and Crank–Nicolson in time, with the boundary conditions imposed at the new
time level; discrete form (4.34)/(4.36). The filter is represented, as in the parent model,
by the admittance outflow q·n = −Φ_h min{h_C − h, 0} on the bottom face.

Transcription notes carried over: the linear initial pressure profile p₀(z) = (z/−H)(1 − p_z0)
+ p_z0 is dimensionally inconsistent as printed (already flagged on angeloni2023); the
functional forms of f_μ and χ are never given, and §4.3 simply sets f_μ = 1, χ = 0.

## Parameters
3D model (§4.2): identical to the angeloni2023 table — ε_O/C/F = 0.305/0.330/0.276,
k_r(p_z0) quadratics per granulometry, h_z0 = 61.18/91.78/122.37 m at 6/9/12 bar,
Φ_h = 6.5e−5 1/s, Φ_k = 30 mm/s, C_kC = 0, C₀^s per variety (Table 4.20), S₀ = 1e−3 1/m,
β_L/β_T = 1/0.1 m, D_k = 1e−9 m²/s, τ_O/τ_C/τ_F = 20/13/35 s, R = 29.25 mm, H = 13.88 mm,
mesh 3486 prisms / 2160 nodes. **The T₀ conflict flagged on angeloni2023 resolves in the
thesis's favour of neither value: §4.2.3 text says T₀ = 70 °C, its own Table 4.21 says
T₀ = 100 °C.** The conflict is reproduced verbatim, not fixed.

§4.3 RBF flow experiment (Table 4.31) — the only parameter set unique to this document:
| symbol | value | units | source |
|---|---|---|---|
| H | 13.77e−3 | m | measured (single granulometry) |
| S₀ | 1e−5 | 1/m | nominal — **100× smaller than the 1e−3 used in §4.2**, unexplained |
| Φ_H | 2.2e−5 | 1/s | assumed — **3× smaller than the 6.5e−5 fitted in §4.2**, unexplained |
| f_μ | 1 | – | assumed |
| χ | 0 | – | assumed (buoyancy off) |
| h_C | 0 | m | assumed |
| τ | 20 | s | nominal |
| ρ₀ | 997 | kg/m³ | nominal |
| K (isotropic, constant) | 1.68e−7 | m/s | assumed — **not the k_r(p_z0) law of §4.2**, and no provenance |
| p₀ (inlet) | 6, 9, 11 | bar | imposed |
| N (nodes), N_t | 310, 5000 | – | assumed |

## Calibration and validation offered by the source
**§4.2 (3D model): nothing new.** Calibration on 27 (T, p, grind) points per variety and
validation on 6 off-grid (T, p) points per variety, with mean per-species errors (Table 4.30)
CF 9.1/9.2, CQA 9.4/13.6, TR 10.4/11.7, CA 31.0/11.3, AA 40.2/19.5, TA 9.7/11.1, FA 9.8/13.7,
LP 27.5/45.5 (Arabica/Robusta) — identical to angeloni2023 Table 11. Per-point errors reach
96.1 % (Arabica CA), 76.0 % (Arabica LP) and 157 % (Robusta LP). The assessment on
angeloni2023 stands unchanged and is not restated: α_k(T,p) is fitted to reproduce these same
assays, K is fitted to match measured flow rate, and Φ_h/Φ_k/C_kC are trial-and-error tuned,
so the exercise measures response-surface interpolation inside the fitted envelope, not
extraction physics.

**§4.3 (RBF flow solver): no validation, and the one quantitative claim is circular.** The
result is that the head falls linearly through the bed and the water "exits respectively with
a pressure of 2, 3, 3.5 bar approximately" for 6, 9, 11 bar inlet (Figs. 4.29–4.31; the
colourbars bracket h ≈ 20 m at the outlet for the 6 bar case, consistent with 2 bar). The
authors call this "in good agreement with laboratory measurements and other simulation
results" but present **no measurement and no comparison** — no flow rate, no shot time, no
pressure trace, no cross-check against the FeFlow solution of the same subsystem. The
residual outlet pressure is a direct arithmetic consequence of the chosen Φ_H = 2.2e−5 1/s
against K = 1.68e−7 m/s over H = 13.77 mm; neither number is measured, and Φ_H differs from
the §4.2 value by 3×. The authors themselves list "a detailed validation against laboratory
measurements" as future work. Treat the 1/3-of-inlet-pressure outlet residual as a **free
parameter's shadow, not a finding**.

## Assumptions and validity range
All assumptions carried on angeloni2023 apply unchanged: post-imbibition saturated bed (first
~5 s discarded), isotropic homogeneous medium, porosity a function of granulometry alone,
fines erosion and transport explicitly dropped, dissolution with no saturation cap and no
concentration-deficit driving force, groundwater-scale dispersivities (β_L = 1 m, γ_L = 0.5 m)
on a 13.9 mm bed, uniform D_k = 1e−9 m²/s for all eight species including lipids, blends
assumed to interpolate linearly between pure varieties, and validity confined to the fitted
88–98 °C × 6–12 bar box on one machine, one grinder, one basket, two blends.
Additional to the §4.3 solver: single constant scalar K (so no pressure- or grind-dependence),
buoyancy and viscosity-temperature coupling switched off (χ = 0, f_μ = 1), no species and no
heat, no reported CFL/conditioning behaviour for the dense PA-RBF differentiation matrices at
N = 310 in 3D, and no mesh/node refinement study. Silent on: whether the linear head profile
survives a pressure- or saturation-dependent K, and on the whole question the outlet residual
gestures at — how much of the pressure drop the basket screen actually carries.

## Interface mapping
Unchanged from angeloni2023: a mega-coupled runtime (Richards + Darcy + 8×ADR + 8×solid +
heat) that would force flow, heat and extraction into a single solver — the failure mode the
registry exists to avoid — with adapters needed for bar→hydraulic-head, k_m2→their fitted
hydraulic conductivity K, and a machine-specific α(T,p) surrogate that is not physically
portable. **Prefer offline data intake; do not couple.**
The §4.3 subsystem in isolation would map to the **flow** stage: consuming BedState
(depth_m ↔ H, area ↔ R, k_m2 → K via μ, ρg) and MachineState (bar → h_z0 Dirichlet), and
producing q(t) and an outlet head. That is the shape a G9 screen-resistance component would
take, and Φ_h is the right *kind* of parameter for it — but with Φ_h unmeasured and given two
different values 3× apart within one document, nothing here can populate it.

## Extractable data
**Nothing new.** Tables 4.15–4.18 (condition matrix, total lipids, bioactives Arabica,
bioactives Robusta), Table 4.20 (R&G inventories C₀^s), Tables 4.28–4.30 (validation errors)
and Tables 4.22–4.27 (α coefficients) are the same tables already scoped for transcription on
**angeloni2023** (its Tables 1–5, 7, 9–11, Appendix A). Transcribe from the journal article,
which is the citable source and carries the %RSD columns in the same form; do not create a
second copy from the thesis. Figure 4.12 (Arabica/Robusta PSD, O/C/F) likewise duplicates
angeloni2023 Fig. 2.
The §4.3 experiment yields no data — Figures 4.29–4.31 are simulation renderings of h with no
measured comparator, and the extractable content is one sentence of approximate outlet
pressures. Not worth digitising.
Availability: no repository, no code; FeFlow Demo 7.2 is proprietary, and the MATLAB RBF
solver is described but not released.

## Overlaps and conflicts
- **angeloni2023 (registered card) — supersedes this in full for §2.3/§4.2.** Same model,
  same closures, same parameters, same 66-shot campaign, same validation tables; the journal
  article is the citable source and has the fuller appendix presentation. The thesis adds
  only the derivation chain for S₀ (the consolidation coefficient C_v) and reproduces the
  T₀ = 70 vs 100 °C conflict verbatim, confirming it is an upstream error rather than a
  typesetting accident in the journal version.
- **khamitova2020 (same lineage, earlier).** The 2-compound, single-variety precursor of the
  same FeFlow system; unchanged by this document.
- **egidi2018 (skip).** Shares the Richards/Galerkin framing and part of the author group but
  is soil hydrology; the §4.3 solver is the coffee-side counterpart and is, if anything,
  *less* tested than egidi2018's code-vs-code verification — that paper at least compared
  four solvers on the same problem, whereas §4.3 compares nothing.
- **perticarini2024 (companion card, this thesis).** The reduced 1D model is the composable
  alternative to this system for the multi-class-solute backlog, and the two disagree on
  porosity within one document (1 − φ = 0.173 / 0.30 here vs ε = 0.305) and on dissolution
  closure (deficit + cap + interaction product vs first-order-in-solid with fitted α(T,p)).
  Carry both closures as dual variants.
- **wadsworth2026.permeability / G9 basket-screen resistance (touches, cannot inform).** The
  §4.3 outlet residual of ~1/3 of inlet pressure is exactly the *kind* of claim G9 needs —
  the registry's Wadsworth/Cameron reconciliation already implies either φ_c ≈ 0.11 or a
  screen resistance — but here it follows from an unmeasured Φ_H that the same thesis states
  twice with a 3× discrepancy. **Record the question, not the number.** The discriminating
  computation, if this is ever pursued: back out Φ_h from DE1 fixture A by fitting the
  measured P(t)/flow with a bed-only Darcy resistance and attributing the residual to the
  screen, then check whether either published Φ_h (6.5e−5 or 2.2e−5 1/s) is consistent.
- **brewer2026.lb_reference / lb_taichi (no conflict).** Those are verified single-phase
  solvers; §4.3 is an unverified head solver and offers them nothing.
- **Backlog "bed_dynamics: kappa(t) compaction/swelling" (weak pointer).** S₀ = gρ(εβ + C_v)
  with C_v = dε/dp is the one place this lineage writes down a consolidation route, and then
  discards it by fixing S₀. No coffee C_v value exists here or, as far as the registry knows,
  anywhere.

## Implementation estimate
Nothing to implement. A runtime port of the coupled system would be **L**, would duplicate
angeloni2023, would depend on a proprietary solver and a non-portable fitted α(T,p), and is
already declined on that card. The §4.3 solver is **M** to reimplement and would buy an
unverified duplicate of a subsystem the registry can already solve two ways
(brewer2026.lb_reference, lb_taichi) with far better verification. No gate is proposed
because there is nothing here to gate against.

VERDICT: skip — §2.3/§4.2 is an equation-for-equation re-presentation of the registered angeloni2023 with the same parameters, the same 66-shot campaign, the same interpolation-only validation and the same unresolved T₀ conflict, and the one novel element, §4.3's RBF head solver, reports no measurement, no cross-solver comparison and an outlet-pressure result that follows directly from an unmeasured filter admittance quoted twice at values 3× apart — effort L

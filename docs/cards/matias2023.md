# Model card: Matias 2023 continuum dissolution–transport with plug invasion front

**Paper:** Matias, A.F.V., Valente-Matias, D.F., Neng, N.R., Nogueira, J.M.F., Andrade Jr., J.S., Coelho, R.C.V., Araújo, N.A.M., “Continuum model for extraction and retention in porous media,” *Physics of Fluids* **35**(12), 123611 (2023), [DOI 10.1063/5.0176273](https://doi.org/10.1063/5.0176273). Publisher-deposited Crossref metadata authenticates the journal citation. Numerical Figure 3 identity remains [arXiv:2304.03161v2](https://arxiv.org/abs/2304.03161v2), revised 19 December 2023; see [source qualification](../analysis/sci_md_matias_caffeine_fraction_shape_001/SOURCE_NOTES.md).
**Stage(s):** extraction (with a degenerate infiltration gate) · **Kind:** calibration
**Status:** model card-only in Puckworks; empirical Figure 3 intake and bounded one-rate representation benchmark complete (data-only). EWP analytical quasi-steady references remain NO_EXPERIMENTAL_VALIDATION.

## Scope and mechanism
1D (in practice) continuum advection–diffusion–dissolution model for a single lumped solute (caffeine) leaving a fixed solid matrix, gated by a plug-like water-invasion front: dissolution at position x switches on only after the front arrives at t* = x·u_m/‖u_m‖². Dissolution is a linear-driving-force mass-transfer law between a solid-surface concentration C_s (which depletes) and the bulk liquid concentration C_l; hydrodynamic dispersion enters via a Taylor–Aris closure. Solid matrix is static: no swelling, erosion, porosity change, or intragranular diffusion. Benchmarked three ways: capsule-espresso caffeine-vs-volume data (Pe ~ 10⁵), 2D lattice-Boltzmann pore-scale simulations (Pe ~ 10²), and an analytical quasi-steady solution for the slow-mass-transfer limit.

## Governing equations
Dimensional transport, their Eq. (3) (simplified from the general Eq. (1) with uniform u_m, D*):

C̊ + u_m·∇C = D*∇²C + S·Θ(t/t* − 1)

- C(x,t): solute concentration in liquid; u_m: REV-averaged interstitial velocity (magnitude ‖u_m‖, plug direction ê_v); Θ: Heaviside; t* = x·u_m/‖u_m‖² (Eq. 4), first arrival of the invading front at x.
- D*: hydrodynamic dispersion coefficient, Taylor–Aris parallel-plate form, Eq. (2): D* = D[1 + (‖u‖L/D)²/210], D molecular diffusivity, L plate spacing / characteristic length. For the pore-scale comparison they instead correct D for an array of circles, Eq. (25): D* = D / {(1 − (π/4)ν²)[ν∫₀^{π/2} (cos φ)^{1/3} dφ/(1 − ν cos φ) + 1 − ν]}, ν = R/(l/2), R circle radius, l center spacing.

Dissolution source, Eqs. (6), (8): ṁ = k_c(C_s − C_l)A, S = ṁ/v_l = k_c(C_s − C_l)A/v_l, with k_c the mass-transfer coefficient (k_c ≡ D/h, h the interface transition width), C_s the microscopic surface concentration, C_l the bulk liquid concentration, A the interface surface area in the REV, v_l the REV liquid volume. Buffering (saturation cap) is stated as representable but neglected (C_s ≪ C_sat assumed).

Solid depletion, Eq. (9): C̊_s = −(ṁ/v_s)·Θ(t/t* − 1), v_s the REV solid volume. Total inventory Eq. (7): m_T = ∫C_s dV. Intragranular diffusion neglected; the authors suggest it as a possible explanation of late-stage deviation, not a demonstrated cause.

Dimensionless form, Eqs. (10)–(15): with x → Lx, t → (L/U)t,

C̊ + ∇·C = (1/Pe)∇²C + ξ(Sh/Pe)Θ(t/t* − 1)  (12)
C̊_s = −ξ_s(Sh/Pe)Θ(t/t* − 1)  (13)

ξ = A/v_l, ξ_s = A/v_s; Pe = UL/D (14); Sh = k_c L/D (15). Note Eq. (12) as printed has ∇·C rather than u·∇C and the source lacking the (C_s − C_l) driving-force factor that Eqs. (8)–(9) carry — transcribed as written; the dimensional Eqs. (3)+(8)+(9) are the self-consistent set an implementation should use.

BCs/ICs, Eqs. (16)–(20): C(t, x₀) = 0 (inlet), ∇C·n̂ = 0 (outlet), C(0,x) = 0, C_s(0,x) = C_i with C_i = m_T/(LπR_e²), R_e the machine-outlet radius.

Analytical quasi-steady limit (k_c T_e/L ≪ 1, T_e extraction time), Eqs. (21)–(24), (C2): Pe ∂C/∂x = ∂²C/∂x² + Sh ξ(C_s − C), C(0) = 0, ∂C/∂x(L) = 0, giving outlet limits C(L) = C_s[1 − 1/cosh(L√(Sh ξ))] for Pe ≪ 1 and C_s(1 − e^{−L Sh ξ/Pe}) ∝ Pe⁻¹ for Pe ≫ 1; full closed form Eq. (C2) with Δ = √(Pe² + 4Sh ξ), S± = (Pe ± Δ)/2.

## Parameters
| symbol | value | units | source |
|---|---|---|---|
| L (cake height) | 10⁻² | m | nominal (Illy & Viani, their ref. 12) |
| ‖u_m‖ | 10⁻² | m/s | nominal (no measurement described) |
| D | 10⁻⁹ | m²/s | nominal (Cussler, their ref. 32) |
| k_c | 10⁻¹ | m/s | **fitted** — text states k_c is the single free parameter tuned to the caffeine curve; Table I nonetheless cites a textbook (their ref. 33) beside it. Carry as fitted. |
| m_T (total caffeine) | 70 | mg | measured (Soxhlet, one capsule) |
| C_i | 1.4×10⁵ | mg/m³ | derived (Eq. 20 from m_T, L, R_e) |
| R_e (outlet radius) | 4×10⁻³ | m | measured/nominal (machine) |
| T_e | 50 | s | measured |
| dose | 5.57943 | g | measured (one capsule) |
| A, v_l, v_s, ξ, ξ_s (espresso case) | not provided | — | — (folded into the fitted k_c·A/v_l product; not separable from this paper) |
| Pe (espresso) | ~10⁵ | – | derived |
| Sh/Pe (espresso) | ~10 | – | derived (Appendix B) |

Pore-scale/LB parameters (Table II, lattice units) are simulation settings, not physical calibration; not transcribed here beyond D = 1/3×10⁻², D* = 2/3×10⁻¹, k_c = 10⁻³, u = 10⁻², domain 240×24.

Plausibility flag (ours, not the authors'): k_c = 0.1 m/s is orders of magnitude above typical liquid-side dissolution mass-transfer coefficients (10⁻⁶–10⁻⁴ m/s); via k_c = D/h it implies h = 10 nm. As fitted it lumps unresolved surface area (A/v_l is never measured), so it must not be reused as a physical constant elsewhere.

## Calibration and validation offered by the source
1. **Espresso experiment (Fig. 3):** caffeine concentration per 5 mL vial vs cumulative volume (10 vials × 4 replicate extractions, HPLC-DAD, calibration R² = 0.9999, Eq. A1: I = 77.221 [L·mg⁻¹]·[caffeine]). The authors report agreement of their continuum solution, with k_c fitted to the same aggregate curve, and suggest internal diffusion as a possible explanation of late-stage deviation. The completed ten-fraction benchmark below separately quantifies the cost of one-rate representation after finite-bin averaging; it does not test the full continuum model. This is post-fit reconstruction with one free parameter against one curve — no held-out condition, no error metric, no parameter sweep of the recipe. Not independent validation.
2. **Pore-scale LB comparison (Fig. 4, Pe ≈ 10²):** continuum solution vs 2D LB with cylinders; hydrodynamic dispersion D* was "the only fitting parameter, estimated using the Taylor-Aris dispersion" — i.e., the closure form supplied the fitted value. Agreement in curve shape and peak timing; concentration rises before front arrival because the plug front only gates dissolution, not diffusion (authors state the approximation is valid for very large Pe).
3. **Analytical limit (Figs. 5, 10):** quasi-steady solution vs LB for circle arrays and point sources across Pe = 10⁻²–10²·⁺ and several source densities ξ; agreement in both Pe limits, requiring the pore-geometry-corrected D* (Eq. 25) for circles and no correction for point sources. This is verification (model vs model with all parameters defined), and it is the strongest-gated piece of the paper.
4. **Invasion-term error study (Appendix B, Fig. 9):** dropping the Heaviside gate produces relative error growing linearly with Sh/Pe, stabilizing by Sh/Pe = 10²; at espresso conditions (Sh/Pe ~ 10) the gate matters, particularly at early times.

## Assumptions and validity range
- Single lumped solute; no multi-species chemistry.
- Static solid matrix: no swelling, erosion, fines migration, or porosity/velocity evolution (authors flag this as future work; contrast their own refs. 8, 9, 14).
- No intragranular diffusion — a source-proposed possible mechanism, not established by the aggregate sequence. No approximately-30-mL cutoff is qualified by this task; all ten fractions are retained.
- C_s ≪ C_sat assumed: no saturation/buffering. Invalid where the liquid approaches saturation (e.g., early ristretto-like regimes, low-flow high-dose beds) — exactly the regime grudeva2025's saturated plateau addresses.
- Uniform porosity, uniform velocity, plug (flat) invasion front normal to flow; no pressure, no permeability, no machine coupling — u_m is prescribed, not solved.
- Front gates dissolution only, not transport: solute can diffuse ahead of the water front (unphysical); acceptable per authors only at very high Pe.
- Isotropic uniform dispersion via a parallel-plate Taylor–Aris formula at Pe where its own applicability is stretched; needs geometry-specific correction (Eq. 25) even for regular circle arrays.
- Quasi-steady analytic branch valid only for k_c T_e/L ≪ 1 — explicitly not the espresso regime (espresso has Sh/Pe ~ 10, fast transfer).

## Interface mapping
Inputs consumed: BedState (depth_m → L, area via R_e, porosity only implicitly through ξ); a prescribed superficial/interstitial velocity (no MachineState coupling — would need a flow stage upstream); GrindState not consumed (no particle-size dependence anywhere; A/v_l is lumped into the fitted k_c).
Candidate model output: c_exit(t); a finite-vial adapter must integrate concentration over each collection window. The empirical caffeine intake alone supplies neither TDS/EY nor a time/mass mapping. No runtime interface is added by this benchmark.
Couplings: none worth building at runtime. As a component it would duplicate cameron2020.extraction_bdf and the grudeva reduced model at strictly lower fidelity (no two-population inventory, no saturation region, no grind coupling, velocity prescribed). Its Heaviside front is a degenerate constant-velocity special case of the front the registry already has (foster2025.infiltration; grudeva s_w(t)). Offline value: Eq. (24)/(C2) analytic limits are cheap closed-form verification targets for any extraction-stage solver's advection–dissolution kernel (Pe and Sh sweeps against exact answers).

## Qualified empirical intake and use limits

`matias2023/fig3_caffeine_fractions` contains all ten aggregate caffeine means,
ten vertical SE segments and ten horizontal segments from Figure 3. Nominal
finite-vial windows are [0,5],...,[45,50] mL; mg/L is concentration per vial,
not instantaneous outlet concentration or a cumulative cup average. Four
extractions contribute to each aggregate; forty individual concentrations are
not available in the inspected public materials. Temperature was uncontrolled.
General espresso settings at the beginning of Section II are background, not
authenticated settings for these extractions.

[Benchmark and exact certificates](../analysis/sci_md_matias_caffeine_fraction_shape_001/RESULT.md):
minimum multiplicative factors are N ≈1.201496385, G ≈1.200389045,
P_outer ≈1.124890709 and P_inner ≈1.127058491. All are positive discrepancies:
exact one-rate compression loses supported aggregate shape under nominal equal
windows. The G/P optima use conservative rectangular relaxations of shared
figure calibration. P brackets every admissible displayed-SE endpoint reading;
SE is descriptive sensitivity, not a simultaneous confidence region. Native
PDF geometry recovers covered bars and the last clipped marker/segment.
Horizontal semantics remain undocumented; actual unequal-volume robustness
is NOT_ESTABLISHED. Graphical precision is distinct from HPLC precision.

Eligible uses: offline source-specific finite-fraction observation comparisons,
exact one-rate representation cost, graphical and displayed-extent sensitivity,
and adjacent ratio/curvature diagnostics. Blocked uses: independent validation,
statistical rejection/equivalence, practical adequacy without an authorized
tolerance, causal mechanism inference, production calibration, physical-rate
identification, and unequal-volume robustness. An aggregate can curve even when
individual extractions are exponential; that explanation is neither fitted nor
established, and cannot rescue arbitrary shapes by assumption. Failure of this
narrower family does not reject the complete Matias continuum model.
PHYSICAL_VALIDATION=NOT_ESTABLISHED.

The one-capsule Soxhlet measurement (5.57943 g, 70 mg) and Table I are separate
inventory/model context, not a common four-shot dose or normalization. Eq. A1
and the HPLC protocol remain methodological references. Figs. 4, 5 and 10 are
model-vs-model verification material, not additional experimental observations.
Source-derived intake: Matias et al., CC BY 4.0; first-party code: repository MIT.

## Overlaps and conflicts
- **cameron2020.extraction_bdf (competes, lower fidelity):** same stage; Cameron has two grain populations, per-bed-volume inventory, saturation-aware kinetics, and experimental gates. No reason to swap.
- **grudeva2023 / grudeva2025 (superseded by, on physics):** the Heaviside-gated dissolution here is a cruder instance of the registry's reference infiltration↔extraction formulation — constant-velocity front, no saturated plateau, no boulder pore-fill, no fixed-pressure branch. Matias independently confirms the qualitative claim that front gating matters at espresso Sh/Pe (Appendix B) — worth one citation line in the ROADMAP coupling note, nothing more.
- **foster2025.infiltration (complements trivially):** t* = x/‖u_m‖ is the zeroth-order front foster2025 replaces with pump/headspace/capillary physics.
- **egidi2018/2024 precedent:** same card class — continuum single/lumped-solute extraction with prescribed q, verdict data-only on the strength of its dataset; Matias lands identically but with a smaller dataset (one recipe, one coffee).
- **ellero2019_jfe / mo2021 / mo2023 (adjacent, cited kin):** Matias 2021 (their ref. 14) is this group's swelling/erosion pore-scale line; this paper deliberately excludes those mechanisms. No conflict.
- **Backlog "multi-class solute chemistry":** single-species only; contributes aggregate finite-vial caffeine concentrations, without a shared Soxhlet normalization or a new model.

## Implementation estimate
As runtime: not recommended (duplicative). Figure 3 intake and bounded shape benchmark are complete. Table I remains context. Optional future analytical verification gates from Eq. (24)/(C2) (analytic outlet concentration vs our extraction kernel at Pe ≪ 1 and Pe ≫ 1, and the Sh/Pe front-gating error trend of Fig. 9) — closed-form, parameter-free, cheap.

VERDICT: data-only — physics duplicates registered extraction/coupling components at lower fidelity with a single fitted parameter and post-fit-only experimental comparison, but the qualified aggregate caffeine finite-fraction series (Fig. 3) and the closed-form Pe/Sh verification limits (Eqs. 24/C2) have distinct empirical and verification uses. No production adoption.

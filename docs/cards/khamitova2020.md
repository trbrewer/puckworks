# Model card: Khamitova 2020 3D percolation model (caffeine + CQA + fines, FeFlow)

**Paper/thesis:** G. Khamitova, "Advanced experimental and analytical study for the optimization of the Espresso Coffee extraction," Ph.D. Dissertation, University of Camerino, School of Advanced Studies, XXXII Cycle (Chemical and Pharmaceutical Sciences and Biotechnology), supervisor Prof. Sauro Vittori, Camerino, 20 April 2020. Model in **Chapter 5 ("Study 3. Mathematical simulation model"), §5.2–5.4.** No DOI. Developed as an "interdisciplinary collaboration with mathematicians" (Camerino group — Galerkin scheme cited to Egidi et al. 2018).
**Stage(s):** flow, extraction, observables (+ qualitative bed_dynamics for fines) · **Kind:** calibration
**Status:** card-only

## Scope and mechanism
3D axisymmetric saturated percolation of an espresso puck (cylinder, symmetry axis z), solving one coupled system: Richards mass balance + Darcy flux for the fluid, an advection–dispersion–reaction (ADR) transport equation for each traced compound, a companion matrix-bound solid balance per compound, and a convective–diffusive heat equation. The implemented case (§5.4.1) traces three compounds — caffeine (C), total chlorogenic acids (CQA), and **Fines** (<100 µm particles treated as an advected/dispersed tracer). Grain→liquid transfer is a **lumped first-order-in-solid-loading dissolution** term R_k = α_k C_k^s (no intra-grain diffusion, no saturation cap, no liquid-deficit driving force); all T,p sensitivity is pushed into the fitted rate α_k(T,p). Imbibition (first ~5 s) is discarded; the bed starts saturated. This is a **precursor** of the same group's later multi-species FeFlow model (Giacomini 2020 → angeloni2023).

## Governing equations
FeFlow/Diersch (2013) groundwater-transport template applied to coffee. General system, their **formula (1)**, prescribed in cylinder C, t ∈ (0, τ):

1. **Richards (fluid mass):** S₀ ∂h/∂t + ∇·q = Q
2. **Darcy flux:** q = −f_μ K·(∇h + χ e), e = (0,0,1)ᵀ
3. **ADR, liquid/solid compound k** (N_ls eqns): ∂(ε C_k)/∂t + ∇·(q C_k) + ∇·j_k = ε R_k
   Fick flux (their unnumbered eq.): j_k = −D_k·∇C_k
   Dispersion tensor: D_k = ε D_k I + D_mech, D_mech = β_T^k‖q‖ I + (β_L^k − β_T^k)(q⊗q)/‖q‖
   Molecular part via Millington tortoisity: D_k ≈ ε^(4/3) D_k (saturated, θ≈ε)
4. **Solid compound m** (N_s eqns, matrix-bound, no transport): ∂(ε_s C_m^s)/∂t = ε_s R_m^s, ε_s = 1 − ε
5. **Heat:** (ρc ε + ρ_s c_s ε_s) ∂T/∂t + ∇·(ρc q T) − ∇·(Λ·∇T) = H_e
   (Λ assembled like D_k, with thermal dispersivities γ_L, γ_T; H_e internal energy source/sink.)

**Boundary/initial conditions.** Hydraulic head **eq. (4)**: Dirichlet from imposed inlet pressure on top Γ₁; Neumann (no-flow) on lateral Γ₂; filter-admittance outflow on bottom Γ₃ — outward flux Φ_h(h − h_C) activates once h > h_C (Φ_h = filter admittance). Linear initial pressure profile p₀(z) from p_z0 at top to atmospheric at bottom. Concentrations **eq. (5)**: Neumann on Γ₁,Γ₂; admittance outflow Φ_k(C − C_kC) on Γ₃ once C > C_kC. Solid **eq. (6)**: initial condition only, C_m^s(·,0) = C₀^s. Temperature **eq. (7)**: Dirichlet T = T_z0 (inlet) on Γ₁; Neumann on Γ₂,Γ₃; IC T₀ = 70 °C.

**Implemented system, their formula (8)** (Q = 0; k ∈ {C, CQA, Fines}): three copies of eq. (3), three copies of eq. (4)-solid, plus the heat eq. Each compound appears in **both** liquid (transported) and solid (matrix-bound) phases.

**Dissolution closure**, their **formulas (12)–(13)**:
- R_k = α_k C_k^s, R_k^s = −α_k C_k^s (mass leaves solid, enters liquid; one-to-one k↔m)
- α_k(T,p) = a_k + b_k T + c_k p + d_k T² + e_k p² + f_k T·p — second-order polynomial in inlet temperature and pressure (caption: polynomial for caffeine, a Gaussian law for CQA; six fitted coefficients a–f per compound in **Table 5.9**). Fines use a **constant** α (qualitative compact-layer reproduction only).

**Symbols** (Table 5.1): h hydraulic head [m], h = ψ + z, ψ = p/ρ₀g; q Darcy flux; S₀ specific storage, S₀ = ρ₀g(εγ + V) with γ fluid- and V matrix-compressibility; f_μ viscosity relation function; χ buoyancy coefficient (Oberbeck–Boussinesq); K hydraulic-conductivity tensor; ε porosity, ε_s = 1−ε; C_k liquid conc., C_k^s solid conc.; j_k hydrodynamic dispersion flux; D_k molecular diffusivity; β_L,β_T longitudinal/transverse dispersivity; T* = θ^(7/3)/ε Millington tortuosity; R_k, R_m^s reaction rates; α_k dissolution rate; Φ_h,Φ_k filter admittances; h_C,C_kC thresholds; T temperature, T_z0 inlet temp, T₀ initial bed temp; ρc, ρ_s c_s fluid/solid volumetric heat capacity; Λ,Λ_s fluid/solid thermal conductivity; γ_L,γ_T thermal dispersivities; H_e energy source. **f_μ and χ constitutive forms are deferred to Diersch (2013), not written out.**

## Parameters
Flow/transport parameters are stated to be "standard values for transport processes in hydrogeology (Diersch 2013)"; the extraction-controlling ones (α_k, Φ_k, C_kC, caffeine dispersivities) are trial-and-error calibrated to a companion (unreported) dataset.

| symbol | value | units | source |
|---|---|---|---|
| R (basket inner radius) | 29.25 | mm | measured (VST 20 g basket) |
| H (pod height) | 14.14 / 13.85 / 13.77 / 13.74 (10/15/20/30 kgF); ~13.88 mean | mm | measured |
| ε (porosity) | ε₁₀ = 0.32; ε₁₅ = 0.314; ε₂₀ = 0.305; ε₃₀ = 0.297 | – | fitted (ε₁₀ set within a 0.30–0.35 range from a "forthcoming" study; others scaled ∝ pod volume) |
| K (hydraulic conductivity, isotropic diag) | ≈ 1.2 × 10⁻⁴ | m/s | fitted (chosen to match observed flow rate) |
| T₀ (initial bed temp) | 70 | °C | assumed |
| T_z0 (inlet) | 88 / 93 / 98 | °C | measured (imposed) |
| p_z0 (inlet) | 7 / 9 / 11 | bar | measured (imposed) |
| Fines threshold | <100 µm = 26 % of ground-coffee volume (=mass, ρ assumed uniform) | – | measured (Mastersizer 3000, Fig. 5.2) |
| solid density (in ρ_s c_s) | 0.8 | g/cm³ | measured ("forthcoming" porosity study) |
| Λ_s | = Λ/2 (water) | W/m·K | assumed |
| S₀, D_C, D_CQA, β_L, β_T | Table 5.10 (hydrogeology-standard; β_L > β_T by 1–2 orders; caffeine dispersivities set high) | mixed | nominal / fitted |
| α_k coefficients a–f | Table 5.9 (per compound) | mixed | fitted |
| Φ_k, C_kC, C₀^s | Table 5.8 | mixed | fitted / derived-from-assay |

Exact digits of Tables 5.9/5.10/5.8 are rig- and compound-specific calibration artifacts (not portable); values are in the source and not reproduced here.

## Calibration and validation offered by the source
Simulation vs. the authors' own HPLC-VWD lab means (Tables 5.3, 5.2) across all 36 (T, p, tamping) conditions, Figures 5.3 (caffeine) and 5.4 (CQA), errors in Table 5.11. Headline: **average error ≈ 6 % for caffeine, ≈ 3.6 % for CQA.** Simulated total liquid volume 39.5–41.7 cm³ vs. the fixed 40 g target (mass≈volume assumed) — but this is imposed by construction (K fitted to the flow rate, brew ratio fixed 1:2), not a prediction.

**This validation is circular / post-fit reconstruction, stated plainly:** the dissolution rate α_k is fitted per (T, p) to reproduce these same extraction levels and then curve-fit over (T, p); K is fitted to the flow rate; Φ_k, C_kC, and caffeine dispersivities are trial-and-error tuned to "data similar to" the validation set. The 6 %/3.6 % agreement therefore measures the fit's flexibility, not predictive skill. The authors describe the whole exercise as a "preliminary" test. Note also the model is nearly **flat in pressure** (Fig. 5.3: pressure sensitivity "almost inappreciable") — it captures magnitude, not the (weak) measured trends. Fines transport (Fig. 5.5) is **qualitative only**: a compact bottom layer forms, but with no characteristic fines size, no compact-layer height, and no fines-in-cup mass, so clogging cannot be represented and nothing is validated.

## Assumptions and validity range
- Homogeneous, isotropic, rigid porous medium; **no swelling, no consolidation** (pod height fixed).
- **Saturated flow only**; imbibition (first ~5 s) discarded — silent on the wetting transient and early TDS.
- Darcy regime: pore Re ≈ 10⁻¹, so **Brinkman and Forchheimer terms both dropped** (Forchheimer justified out because Re < 10). Directly opposes the registry's gusher-regime Forchheimer backlog (Fo ~ 0.3–0.9 at Cameron density) — this model is for the slow-flow regime and cannot speak to inertial correction.
- Liquid/solid decoupling via a compressibility-based porosity(pressure) closure; solid momentum never solved.
- Oberbeck–Boussinesq (density varies only in buoyancy); local thermal equilibrium after imbibition; T₀ uniform 70 °C (unmeasured guess).
- Fickian (not Maxwell–Stefan) diffusion; single lumped CQA; caffeine near-constant by construction (its α polynomial's leading term dominates).
- Fixed brew ratio 1:2, fixed 25 s, single coffee (100 % Arabica), single grind. **Silent on:** transient/kinetic profiles, EY vs. time, TDS, sensory, grind/PSD effects (held constant), variety, unsaturated fine-grind flow.

## Interface mapping
Inputs consumed: MachineState (P_of_t → imposed inlet pressure/temperature), BedState (porosity ε, geometry H, R; K would need supplying), GrindState (fines fraction → Fines C₀^s; PSD held fixed). Outputs produced: ShotResultState-adjacent per-compound cup concentrations (mg/40 mL) and beverage volume; **no EY_pct, no tds_pct, no time traces** as delivered (means only).
Couplings: **offline calibration chain, not runtime.** The dissolution rates and K are fit to the rig's own data before any prediction, so the model can only reproduce, not forecast, a new configuration. Would need a full FeFlow-class 3D coupled solver (Richards+ADR×3+heat) to run — large, and it duplicates the angeloni2023 solver.

## Extractable data
The model is superseded (below); the **chemical campaign is the only transcribable asset**, and it is the *only tamping-force-resolved* multi-compound set in this lineage:
- **Tables 5.2–5.5** — total CQA, caffeine, trigonelline, nicotinic acid in EC (mg/40 mL and mg/mL, +RSD) across 3 T × 3 p × 4 tamping = 36 conditions (duplicate; 72 shots). Rig: VA388 Black Eagle, Mythos 2 grinder, VST 20 g Competition basket, 100 % Arabica "Cibao Altura," 20 g→40 g, 25±1 s.
- **Table 5.6** — ground-coffee assay (mg/10 mL per 1 g) for the four compounds (feeds C₀^s).
- **Figure 5.2** — ground-coffee PSD (Mastersizer 3000); 26 % <100 µm by volume.
Weak discriminating power: variation across all conditions is "quite narrow" (~2–3× RSD), means only, no time series, non-standard 20 g dose. Raw per-condition means are in-thesis; per-shot raw and the α-calibration dataset are unreported (available-on-request at best). No code published.

## Overlaps and conflicts
- **angeloni2023 (extraction/flow/observables, calibration) — SUPERSEDES this card.** Same Camerino/Vittori group, same FeFlow Richards+Darcy+ADR+solid+heat system (their formula (1) is *identical* in structure), same first-order fitted-α(T,p) dissolution closure (their Eq. 8–9 = this thesis's formulas 12–13), same VST cylinder, same imbibition exclusion. angeloni2023 does it with **8 species, Arabica + Robusta, O/C/F granulometry, 66 shots, full coefficient appendix** — strictly higher fidelity and more data. This thesis is the 2-compound, single-variety, single-grind precursor.
- **Only non-redundant element vs. angeloni2023:** the **Fines advected-tracer** (compact-layer formation). But it is qualitative, size-less, mass-non-conserving, and does **not** satisfy the backlog's "mass-conserving 5-state mobile-fines transport" nor brewer2026.streamtube's fines migration.
- **egidi2024 (extraction, runtime)** — same group, later, but a *different* physical model (1D, intra-grain spherical diffusion, quadratic dissolution, c_sat cap). This thesis's lumped first-order α closure is lower-fidelity chemistry than egidi2024/Cameron.
- **egidi2018 (infiltration)** — same first author of the numerical lineage; unrelated soil-Richards content.
- **grudeva2025 (infiltration/extraction, runtime)** — competing lineage; grudeva *models* imbibition and gives mechanistic (parameter-free) validation, which this model explicitly does not.
- **Backlog "multi-class solute chemistry"** — the data partially touches this (4 compounds) but with weak effect sizes; angeloni2023's campaign already dominates it.

**Erratum flags (thesis cross-references):** §5.3.3 attributes the caffeine values to "Table 5.4," but caffeine is Table 5.3 (5.4 is trigonelline); §5.4.4 discussion swaps Figure 5.3 (caffeine) and Figure 5.4 (CQA). Content is internally identifiable; labels are transposed.

## Implementation estimate
No model implementation warranted — the coupled 3D solver would replicate angeloni2023 (L effort) for lower fidelity. If the tamping-resolved tables are wanted, transcribe Tables 5.2–5.6 to `puckworks/data/khamitova2020_tamping/` (effort S) as a weak-effect reference; tag "tamping ≈ null on per-species EY at fixed 1:2 ratio, narrow variation."

VERDICT: data-only — model is a lower-fidelity precursor superseded by angeloni2023 (same group/solver/closure, fewer species, circular validation), but its Tables 5.2–5.6 are the registry's only tamping-force-resolved multi-compound EC chemistry, worth transcribing despite weak effect sizes — effort S.

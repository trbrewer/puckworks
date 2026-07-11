# Model card: Grudeva 2026 infiltration-coupled extraction

**Paper/thesis:** Grudeva, Moroney & Foster, "A multiscale model for espresso brewing: asymptotic analysis and numerical simulation," Eur. J. Appl. Math. 37(2), 496–519 (2026; online 27 May 2025). DOI 10.1017/S095679252500018X. Open access; supplementary material (uploaded here) contains the fixed-pressure flow variant, the front conservation derivation, the boulder-flux closed form, the unsaturated variant, and both numerical schemes.
**Stage(s):** infiltration, extraction · **Kind:** runtime
**Status:** proposed

*Intake note: only the SI PDF was uploaded; the main paper (equations 1–75, Tables 1–2, results) was read from the open-access Cambridge version and this card is written against both.*

## Scope and mechanism
Two-population (fines/boulders) 1D extraction model that, unlike Cameron 2020, starts from a dry bed: a sharp wetting front sweeps down the bed and extraction at each depth begins only once the front has passed. Boulders are porous (internal fraction φ_lb) and are refilled with front-local liquid on wetting, so solubles are carried *into* boulders at the front — an early-shot sink absent from saturated-bed models. Intragranular transport is resolved as Fickian diffusion in spheres (pseudo-2D, Newman-model structure), with a saturation-capped linear surface mass transfer. A matched asymptotic analysis in ε (surface-transfer timescale / wetting timescale, ~10⁻³) collapses the bed into a saturated region behind the front, a slender fines-dissolution layer at the moving saturation interface s_d(t), and a slowly-extracting boulder-limited region at the inlet, yielding a reduced model that is ~100× cheaper than the full PDE system and predicts the outlet concentration trace, including the initial fully-saturated first-drip plateau and subsequent blonding decay.

## Governing equations
Dimensionless full model (their Eqs. 23–29); z scaled by bed depth L*, t by wetting time t*_w = φ_T L*/q*_app, all concentrations by c*_sat, q by q*_app, r_i by grain radius a*_i.

1. Liquid transport, wet region (23): (φ_l/φ_T) ∂c_l/∂t + ∂F_l/∂z = G_f + G_b, with F_l = −D_eff ∂c_l/∂z + q c_l.
2. BCs (24): c_l|_{z=0} = 0; front pillbox condition −ṡ_w c_l + F_l|_{z=s_w} = 0 for t < 1 (dimensional form with boulder sink, their Eq. 11 / SI Eq. B8); ∂c_l/∂z|_{z=1} = 0 for t ≥ 1.
3. Grain diffusion (25)–(26), i = b, f: ∂c_i/∂t + (1/r_i²) ∂(r_i² F_i)/∂r_i = 0, F_i = −D_si ∂c_i/∂r_i; F_i|_{r_i=0} = 0, F_i|_{r_i=1} = Q_i G_i.
4. Surface transfer (27): G_i = (b_i/ε) × {0 if z > s_w(t); 1 − c_l if c_i|_{r_i=1} ≥ 1; c_i|_{r_i=1} − c_l otherwise}.
5. Boulder refill at the front (28): c_b|_{z=s_w} = c_b,init + φ_lb c_l|_{z=s_w}; c_f|_{z=s_w} = c_f,init.
6. Flow and front, fixed-flow case (29): q ≡ 1, s_w(t) = t for t ≤ 1, else 1. (Fixed-pressure variant: SI Eqs. A1–A3, Darcy with P|_{z=0} = P_app and zero overpressure at the front; solves for q(t) and s_w(t).)

Asymptotically reduced model (what would actually be implemented for production runs):

7. Saturation-front ODE (74): ds_d/dt = q [ (φ_l/φ_T + 1/(3Q_f)) (c_f,init − c_l^(i)|_{z=s_d}) / (1 − c_l^(i)|_{z=s_d}) ]⁻¹, s_d|_{t=0} = 0.
8. Region-(i) liquid transport (67): (φ_l/φ_T + 1/(3Q_f)) ∂c_l/∂t + q ∂c_l/∂z = G_b, c_l|_{z=0} = 0; reduced to an ODE along characteristics via (72)–(73).
9. Boulder flux closed form (71, derived in SI Sec. C): G_b(z,t) = (2D_sb/Q_b) Σ_{n≥1} e^{−n²π²D_sb(t−t₀)} [c_b|_{t=t₀} − c_l(z,t₀) − ∫_{t₀}^t ċ_l(z,τ) e^{n²π²D_sb τ} dτ], where t₀ = s_d⁻¹(z) is front-passage time at depth z.
10. Exit concentration (75): c_exit = 0 for t < 1; = 1 (saturated) for 1 < t < s_d⁻¹(1); = c̃|_{χ=1} thereafter.
11. Unsaturated variant (SI Sec. D, Eqs. D5–D7): if solving (74) ever gives s_d > s_w, the saturated region ceases to exist; region-(i) transport is replaced by (D7) with modified boulder initial condition (D6). This is about solute saturation of the liquid, NOT incomplete water wetting — do not conflate with the fine-grind unsaturated-flow backlog item.

Symbols: c_l, c_f, c_b solubles concentrations in liquid / fines / boulders; φ_l, φ_f, φ_b bed volume fractions (liquid, fines, boulders); φ_T = φ_l + φ_b φ_lb total porosity; s_w, s_d wetting and saturation fronts; Q_i = φ_T/(a*_i b*_i) with b*_i = 3φ_i/a*_i; ε = q*_app/(k* L* b*_typ); D_si, D_eff dimensionless grain and liquid diffusivities. Nothing has been simplified away here beyond the paper's own choices, but note the authors set φ_lb = 0 in all verification runs (numerical convenience, acknowledged as possibly unphysical).

## Parameters
| symbol | value | units | source (per their Table 1 superscripts) |
|---|---|---|---|
| φ_f | 0.1–0.25 | – | fitted, comparable to literature |
| φ_l | 0.1–0.2 | – | fitted, comparable to literature |
| φ_lb | 0.35–0.55 | – | fitted, comparable to literature (set to 0 in verification runs) |
| D*_sf | 1×10⁻⁹ | m² s⁻¹ | fitted |
| D*_sb | 1×10⁻⁹ | m² s⁻¹ | fitted (assumed equal to D*_sf; authors flag this) |
| D*_eff | 1×10⁻⁸ | m² s⁻¹ | fitted |
| c*_f,init, c*_b,init | 3.1×10² | kg m⁻³ | fitted |
| c*_sat | 2.24×10² | kg m⁻³ | fitted, comparable to literature |
| a*_b | 2.29×10⁻⁴ | m | literature (Moroney 2015/2019) |
| a*_f | 3.65×10⁻⁶ | m | literature |
| k* | 1×10⁻³ | m s⁻¹ | literature |
| q*_app | 1.52×10⁻³ | m s⁻¹ | fitted |
| μ* | 3.15×10⁻⁴ | Pa s | literature |
| κ* | 2.2×10⁻¹⁶ | m² | fitted |
| P*_app | 9.2×10⁻⁶ (as printed) | Pa | experiment — almost certainly a typo; 9.2×10⁵ Pa (9.2 bar gauge) is the physically sensible value, but the printed number is what the paper gives |
| L* | 8.4×10⁻³ | m | experiment |
| t*_w | 5 | s | experiment |
| ε | 10⁻³ | – | derived (Table 2); verification runs use 10⁻² down to 3×10⁻³ only |
| Table 2 dimensionless set | D_eff 8×10⁻⁴, D_sf 300.24, D_sb 8×10⁻², Q_f 0.104, Q_b 0.380, b_f 1.99, b_b 7.9×10⁻³, c_i,init 1.388 | – | derived |

Verification-run bed fractions (their Eq. 76) differ from Table 1: φ_f = 0.64, φ_b = 0.16, φ_l = 0.2, φ_lb = 0 — chosen for numerics, not physical realism (φ_f = 0.64 is far outside any measured fines fraction).

## Calibration and validation offered by the source
**Verification only, no experimental validation of outputs.** The paper compares numerical solutions of the full model (MATLAB, FE + control-volume, ode15s; SI Sec. E.1) against the reduced model (Python, first-order upwind/Euler; SI Sec. E.2) for ε = 10⁻², 6×10⁻³, 3×10⁻³: the discrepancy decreases as ε shrinks (their Fig. 5), consistent with the asymptotic error being O(ε)-ish, though they cannot reach the physically relevant ε = 10⁻³ because the full model becomes prohibitively expensive. Reported speed at ε = 10⁻²: ~10 s reduced vs ~1000 s full at matched 3-digit accuracy. The only experimental touchpoint is qualitative: first drips segregated from café-style shots show a recipe-independent concentration, interpreted as the saturation plateau the model predicts (their Sec. 2.7) — details deferred to a "forthcoming article." Comparison to time-resolved outlet concentration data is explicitly future work. Do not treat this component as experimentally gated by the source.

## Assumptions and validity range
- Fixed inlet flow rate in the main analysis (q ≡ 1, front moves linearly); fixed-pressure variant only in SI and not carried through the asymptotics.
- Darcy flow, constant viscosity and density (viscosity of concentrated coffee liquor is known to be higher; ignored).
- Sharp wetting front, fully saturated water behind it; instantaneous wetting and internal dissolution at the grain scale; no swelling; no channeling (1D homogeneous bed).
- Partition coefficient unity between grain surface and liquid.
- Model cannot properly represent c_b > c_sat after front refill: solid solubles should stay immobile until local pore concentration drops, but the homogenised description dissolves them instantly (authors' acknowledged shortcoming, their §2.5).
- Reduced model valid only for ε ≪ 1 (fast surface transfer) AND the saturated-layer regime (fines rich enough and fast enough to saturate the liquid); the SI unsaturated variant covers the other regime but was not numerically demonstrated.
- D_sf = D_sb assumed for lack of data; reduced model is insensitive to D_sf (limit D_sf → ∞) but directly sensitive to D_sb, which is fitted, not measured.
- Silent on: temperature, multi-species chemistry (named as future work), fines migration, bed compaction/permeability evolution, gusher/inertial regimes, headspace and pump dynamics.

## Interface mapping
Inputs consumed: GrindState.fines_fraction and radii → φ_f, φ_b, a*_i; BedState.depth_m, porosity (→ φ_l, φ_T), dose (→ c_i,init inventory); MachineState → q*_app for the fixed-flow case, or P_of_t + BedState.k for the SI fixed-pressure variant (adapter: Darcy q(t) from recorded pressure, which is exactly foster2025's recorded-pressure mode).
Outputs produced: ShotResultState.traces (c_exit(t), first-drip time, saturation-plateau duration), EY_pct/tds_pct by integrating the outlet flux.
Couplings: runtime, in the shot chain. This is the registry's missing infiltration↔extraction coupling implemented as a single component: extraction per depth cell starts at front passage t₀(z) by construction. Natural composition: drive s_w(t) from foster2025.infiltration (pump/headspace/capillary physics) instead of the trivial linear front, then feed t₀(z) into the reduced extraction equations — an adapter at the s_w(t) interface, no change to the extraction core. c_sat-capped transfer maps onto Cameron's saturation logic; inventory bookkeeping must be reconciled with cameron2020's per-bed-volume c_s0 = 118/φ_s convention (Grudeva measures c_b per grain volume incl. internal pores — different reference volume, adapter needed).

## Extractable data
- Table 1 → data/grudeva2026_table1.csv: the authors' attempt at a first "complete" espresso parameter set (flag the P*_app typo and the fitted/literature/experiment provenance per row).
- Table 2 dimensionless values (small, include in same csv).
- Reduced-model Python solver is published: github.com/YoanaGrudeva/espresso-model (SI ref [1]) — transcribable and directly gateable. Full-model MATLAB code is not stated to be published.
- Figures 3–5 are model-vs-model curves (verification, not measurement) — worth digitising only as gate targets, not as reference data. No experimental tables. Time-resolved outlet-concentration data is promised in a follow-up paper; watch for it — that dataset would raise this component's value considerably.

## Overlaps and conflicts
- **cameron2020.extraction_bdf (extraction, runtime):** direct competitor and lineal descendant (Foster is senior author on both; model built explicitly on Cameron's homogenisation). Grudeva adds the dry-bed infiltration phase, boulder refill sink at the front, and an asymptotic reduction; Cameron has the stronger experimental grounding (flux tables, Tables 2/7/8) and a validated implementation. They should coexist: Cameron as the gated saturated-bed workhorse, Grudeva as the infiltration-aware variant whose early-time transient Cameron cannot produce.
- **foster2025.infiltration (infiltration, runtime):** complementary, same group. Foster 2025 supplies real infiltration physics (pump, headspace, capillarity, micro-CT-gated); Grudeva's front is trivial under fixed flow. Composing them discharges Foster's card backlog line "coupling extraction start to front passage per depth cell = solver backlog."
- **Registry backlog:** direct hit on "infiltration↔extraction coupling: delay extraction per depth cell until front passage (changes early TDS transient)" — this paper *is* that item, with the added claim that a large share of total extraction happens pre-first-drip. Touches the multi-class solute backlog only as stated future work. Its SI "unsaturated" case is solute-side and does NOT address the fine-grind incomplete-wetting hypothesis (Foster 2025's k→0 tubes); keep the two uses of "unsaturated" distinct in the registry notes.
- No conflict with wadsworth2026.permeability or the brewer2026 components; κ* here is a single fitted scalar, inferior to the calibration chain already registered.

## Implementation estimate
Reduced model: port/wrap the published Python solver (Eqs. 73–75 + 74 + boulder CV scheme, SI E.2), M effort; the full model (SI E.1) is not worth reimplementing except as a one-off verification twin. Gate design (verification-based, like lb_reference, since the source offers no experimental gate): (1) reproduce their Fig. 4 outlet trace and Fig. 5 ε-convergence with their code and parameters (Eq. 76 set, φ_lb = 0); (2) recover c_exit plateau duration s_d⁻¹(1) − 1 analytically from (74) with constant c_l as a sanity check; (3) after coupling to foster2025's s_w(t), check first-drip time consistency against the DE1 fixture A W_dead/first-drip gate already held. Dependencies: adapter for c_init reference-volume convention vs cameron2020; adapter from MachineState.P_of_t to q(t) if not using fixed flow.

VERDICT: implement-now — it is the exact infiltration↔extraction coupling at the top of the backlog, with a published cheap solver, and verification gates are constructible even though the source offers no experimental validation — effort M

# Model card: Moroney 2016 asymptotic extraction

**Paper/thesis:** Moroney, Lee, O'Brien, Suijver, Marra, "Asymptotic analysis of the dominant mechanisms in the coffee extraction process," SIAM J. Appl. Math. 76(6), 2196–2217 (2016). DOI 10.1137/15M1036658
**Stage(s):** extraction · **Kind:** calibration (closed-form surrogate for fitting extraction curves and estimating post-saturation initial conditions; runtime coupling would be forced — constant-ΔP assumption is baked into the solution)
**Status:** card-only

## Scope and mechanism
Matched-asymptotic reduction of the Moroney 2015 (Chem. Eng. Sci. 137, 216–234, their ref [14]) double-porosity extraction model for a saturated packed cylindrical bed under pressure-driven flow (1 L at 90 °C, ΔP = 2.3 bar — low-pressure espresso-like, not 9-bar). Two soluble populations: fast surface dissolution from broken cells (fines/grain surfaces) and slow diffusion out of intact grain kernels. The small parameter ε = t_a/t_d (advection over grain-diffusion timescale) yields an inner (advection, t_a ≈ 5.4 s) layer where surface dissolution dominates and an outer (bulk diffusion, t_d ≈ 42 s) region where kernel diffusion dominates; composite closed-form solutions relate exit concentration explicitly to process parameters. Fine-grind initial conditions are presented; the coarse-grind case follows the same steps with a linear initial profile.

## Governing equations
Dimensional simplified system (fine grind), their Eqs. (2.12)–(2.17); p*_h eliminated via Darcy solution p*_h = (ΔP/L)z* of Eq. (2.2); v-phase pressure transfer neglected (p*_h = p*_v); φ*_v ≈ φ_v^∞; kernel solids assumed pre-dissolved (ψ*_v = 0, Eq. (2.6) dropped):

(2.12) ∂c*_h/∂t* = [k²_sv1 φ²_h / (36κμ(1−φ_h)²)] (ΔP/L + ρg) ∂c*_h/∂z* + φ_h^{1/3} D_h ∂²c*_h/∂z*² + D^b ∂²c*_h/∂z*² − α* [(1−φ_h)/φ_h] φ_v^{∞4/3} D_v (6/(k_sv2 l_l))(c*_h − c*_v) + β* [(1−φ_h)/φ_h] (12 D_h φ_cd/(k_sv1 m))(c_sat − c*_h) ψ*_s

(2.13) ∂c*_v/∂t* = α* φ_v^{∞1/3} D_v (6/(k_sv2 l_l))(c*_h − c*_v)

(2.14) ∂ψ*_s/∂t* = −β* (12 D_h φ_cd/(k_sv1 m)) ((c_sat − c*_h)/c_s) r_s ψ*_s

with c*_h(z*,0)=c_sat, c*_v(z*,0)=η c_sat, ψ*_s(z*,0)=ψ*_s0, c*_h(L,t*)=0, ∂c*_h(0,t*)/∂z*=0 (2.16–2.17). Diffusion/dispersion terms are then dropped: advection/diffusion ratio ~10⁷ (2.20).

Symbols: c*_h, c*_v = coffee concentration in inter-/intragranular pores; ψ*_s = fraction of initial surface coffee remaining; φ_h = intergranular porosity; φ_v^∞ = final intragranular porosity; φ_cd = soluble coffee volume fraction (dry grains); r_s = 1/φ_s,sd; k_sv1, k_sv2 = Sauter mean diameters (all grains; grains > 50 µm); l_l = mean volume-weighted grain radius; m = coffee cell diameter; D_h = D_v = solute diffusivity; c_sat = solubility; c_s = solid coffee density; κ = Kozeny–Carman shape factor; μ, ρ = fluid viscosity, density; α*, β* = fitting coefficients on the two mass-transfer terms.

Timescales (2.22): t_d = k_sv2 l_l/(6α*φ_v^{∞1/3}D_v), t_s = k_sv1 m φ_h/(12β*D_h φ_cd ψ*_s0(1−φ_h)), t_a = 36L²κμ(1−φ_h)²/(k²_sv1 φ²_h(ΔP+ρgL)). Fine grind: t_s = 1.042 s, t_a = 5.356 s, t_d = 42.231 s.

Dimensionless groups (2.25–2.26): ε = t_a/t_d = 0.127; a1 = φ_v^∞(1−φ_h)/φ_h = 2.81 (intra/intergranular volume ratio); a2 = t_a/t_s = 5.139; a3 = c_sat r_s φ_h/(c_s(1−φ_h)ψ*_s0) = 0.473 (pore mass capacity / initial surface coffee).

Implemented output would be the composite solutions, their Eqs. (3.64)–(3.66) — piecewise in the characteristic variable z+t with Heaviside switching at z+t = 1 (first wash-through), e.g. leading-order exit behavior from (3.45):
c_h0(z,t) = 1 for z+t < 1; (e^{a2} − e^{a2 z}) / (e^{a2} − e^{a2 z} + e^{a2(z + a3(z+t−1))}) for z+t > 1,
plus O(ε) inner corrections for z+t < 1 (3.56) and the outer (bulk-diffusion) solutions (3.61)–(3.62) with matched f1 = η, f2 = (1/a3 + 1)(1−z) (3.60). Brew strength / EY follow by integrating exit concentration.

## Parameters
| symbol | value | units | source |
|---|---|---|---|
| φ_v^∞ | 0.7034 | – | derived from measured soluble mass fraction [14] |
| φ_h | 0.2 | – | nominal |
| c_s | 1400 | kg m⁻³ | nominal |
| φ_cd | 0.143435 | – | measured [14] |
| φ_s,sd | 0.11 | – | measured/derived [14] |
| φ_s,bd | 0.033435 | – | measured/derived [14] |
| α* | 0.1833 | – | fitted (to extraction profile) |
| β* | 0.0447 | – | fitted (to extraction profile) |
| γ* | not provided | – | not determinable (no c*_v data); assumption γ* ≥ β* only |
| ΔP | 230 000 | Pa | measured |
| L | 0.0405 | m | measured |
| k_sv1 | 27.35 | µm | measured (grind PSD) |
| k_sv2 | 322.49 | µm | measured (grind PSD) |
| l_l | 282 | µm | measured (grind PSD) |
| D_h = D_v | 2.2 × 10⁻⁹ | m² s⁻¹ | nominal (caffeine in water) |
| ρ | 965.3 | kg m⁻³ | nominal (water, 90 °C) |
| μ | 0.315 × 10⁻³ | Pa s | nominal (water, 90 °C) |
| m | 30 | µm | nominal |
| c_sat | 212.4 | kg m⁻³ | nominal |
| κ | 3.1 | – | nominal (Kozeny–Carman) |
| η | 0.5 | – | assumed (initial intragranular concentration level) |
| ψ*_s0 | 0.7304 | – | derived from assumed initial condition |
| g | 9.81 | m s⁻² | nominal |

## Calibration and validation offered by the source
Composite solutions compared against numerical (method-of-lines) solutions of the reduced system (3.21)–(3.26) and against experimental exit-concentration data from [14] (JK drip filter grind), Figs. 5–10. Agreement is presented graphically only — no error metrics are reported. Inner and outer solutions each agree well with numerics in their regions of validity; the composite for c_h disagrees with numerics at short times for z+t > 1 because the inner solution there is only available at leading order (missing O(ε) term, acknowledged). The claim is qualitative: the reduced system "can still reproduce the experimentally determined extraction profile." Note the fit is partly circular in that α*, β* were fitted to the same class of extraction profiles; c*_v and ψ*_s are validated against numerics only (no data exists). ε = 0.127 is not deeply small — truncation error is ~13% at first order.

## Assumptions and validity range
- Saturated bed only; unsaturated infiltration and draining explicitly excluded — initial conditions after saturation must be estimated (ψ*_s0, η, c*_h0 profile).
- Constant ΔP with linear pressure profile (Eq. 2.2 solved once); no time-varying machine profile, no flow–extraction feedback (permeability constant; Kozeny–Carman with fixed κ).
- Isothermal; single lumped solute; 1D homogeneous cross-sections (no channeling or bed heterogeneity).
- p*_h = p*_v (h↔v fluid transfer neglected); φ*_v ≈ φ_v^∞ (requires φ_s,sd + φ_s,bd ≪ φ_v^∞); kernel solids pre-dissolved at saturation (ψ*_v0 = 0), valid only if kernel dissolution is much faster than kernel diffusion.
- ε ≪ 1 with a1, a2, a3 = O(1); breaks for very coarse grinds/low ΔP (ε grows) and for regimes where diffusion/dispersion matter (very slow flow).
- Fine-grind initial condition c*_h(z,0) = c_sat presented; coarse grind requires a different assumed initial profile.
- Silent on: fines migration, bed compaction/swelling, temperature effects, multi-component chemistry, gushers/inertial flow.

## Interface mapping
Inputs consumed: BedState (depth_m → L, porosity → φ_h; k is internally Kozeny–Carman from k_sv1, φ_h, κ — conflicts with supplying BedState.k directly), GrindState (needs an adapter: registry contract carries fines_fraction/boulder_radius/mean_radius, model needs Sauter diameters k_sv1, k_sv2 and l_l from the PSD), MachineState (constant ΔP only — cannot consume P_of_t arrays without violating the derivation).
Outputs produced: exit concentration trace c*_h(0,t) → ShotResultState.tds_pct/EY_pct by integration.
Couplings: offline calibration chain — fit (a2, a3, ε, η) or (α*, β*) to measured extraction curves in seconds (no PDE solve), then hand parameter priors to cameron2020.extraction_bdf. Not recommended as a runtime extraction stage while cameron2020 occupies that slot at higher fidelity.

## Extractable data
- Table 1: complete parameter set for the [14] cylindrical brewing-chamber experiments → data/moroney2016_table1.csv (transcribable now; complements Cameron's tables as an independent fine-grind parameterization).
- Fig. 6(a): experimental exit-concentration points (nondimensional, JK drip filter grind) — digitizable, but the primary data lives in Moroney 2015 [14] (Chem. Eng. Sci.). **DONE (2026-07-22):** `[14]` is now carded and landed as `moroney2015` (`moroney2015_data()`) — the primary Philips dataset (Tables 1–2 + Figs 1–12, three Δp permeability anchors, five-grind batch sweep, per-species kinetics, measured κ=3.1). The "[14]" derived-parameter provenance in this card's parameter table resolves there.
- No code or raw data published with this paper.

## Overlaps and conflicts
- **cameron2020.extraction_bdf** (extraction, runtime): same model family — two-population fast-surface/slow-kernel extraction; this is the closed-form, constant-ΔP, truncated-in-ε analog. Competes at lower fidelity as a runtime stage; complements strongly as a fast-fitting surrogate and as an analytic sanity gate (limits any two-population implementation should reproduce).
- **foster2025.infiltration** (infiltration, runtime): complementary in exactly the way the registry backlog anticipates — Moroney explicitly does not model infiltration and must guess ψ*_s0, η, and the initial c*_h profile; Foster's front passage can supply those initial conditions. This paper defines the receiving side of the infiltration↔extraction coupling contract.
- **wadsworth2026.permeability** (packing, calibration): competing permeability closure — Kozeny–Carman κ = 3.1 here vs. percolation k(R, φ_p); same tamped-regime tension already noted for Cameron's flux table.
- Backlog "extraction: multi-class solute chemistry": authors flag the multi-constituent extension as future work; nothing usable here yet.
- The well-mixed (French-press) asymptotics are in a separate paper (their ref [15], J. Math. Industry 2016) — out of scope for this card.

## Implementation estimate
Small: composite solutions (3.64)–(3.66) are explicit piecewise expressions; a fitting wrapper over (ε, a2, a3, η) is a few dozen lines. No dependencies beyond numpy/scipy.optimize. Gate design: (1) reproduce Fig. 6 exit-concentration curve from Table 1 parameters (composite vs. digitized curve); (2) cross-check the asymptotic solution against cameron2020's BDF solver configured to the equivalent two-population limit at matched parameters — a mutual-validation gate the registry currently lacks.

VERDICT: calibration-provider — closed-form two-timescale surrogate that fits extraction curves in seconds and formalizes the initial-condition handoff from infiltration, but constant-ΔP and truncated-ε assumptions rule out runtime use alongside cameron2020 — effort S

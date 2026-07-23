# Model card: Moroney 2019 extraction-uniformity CFD

**Paper/thesis:** Moroney, O'Connell, Meikle-Janney, O'Brien, Walker, Lee, "Analysing extraction uniformity from porous coffee beds using mathematical modelling and computational fluid dynamics approaches," PLoS ONE 14(7): e0219906 (2019). DOI 10.1371/journal.pone.0219906
**Stage(s):** flow · extraction · observables · **Kind:** calibration (the physics is a reduced, deliberately simplified subset of what cameron2020 already runs at runtime; the paper's usable content is fitted parameters, experimental traces, and a uniformity observable — runtime coupling would be forced and redundant)
**Status:** card-only

## Scope and mechanism
Couples a spatially resolved (2-D axisymmetric, ANSYS Fluent Euler–Euler) or 1-D Darcy-like flow model of a static saturated packed bed to a linear-driving-force extraction model with one or two representative grain sizes, in order to quantify *extraction uniformity* — the spatial distribution of local extraction yield within the bed — rather than just bed-averaged EY. Flow → extraction coupling is strictly one-way (constant porosity, constant permeability; flow solved once, then advected extraction on top). Validated against a Philips Research cylindrical brew-chamber dataset (59 mm chamber, 60 g dose, 250 ml min⁻¹, 90 °C, ~1 L — espresso-like pressures but drip-filter brew ratio), then applied predictively to a 60° truncated-cone (pour-over-like) geometry where flow acceleration toward the narrow outlet produces strong axial+radial EY gradients. Introduces an espresso-adapted brewing control chart with horizontal error bars = std. dev. of local EY in the bed as a uniformity observable.

## Governing equations
**CFD flow (their Eqs. 2, 4–6).** Steady incompressible liquid phase in a static solid bed (v⃗_s = 0, α_s constant):
∇·v⃗_l = 0 (2)
α_l ρ_l ∇·(v⃗_l v⃗_l) = −α_l ∇p_l + α_l ρ_l g⃗ + F⃗_drag (4)
F⃗_drag = K_sl (v⃗_s − v⃗_l) (5)
K_sl = 150 α_s(1−α_l)μ_l / (α_l d_s²) + 1.75 ρ_l α_s |v⃗_s − v⃗_l| / d_s (Gidaspow, α_s < 0.8) (6)
The first term of (6) is Kozeny–Carman; the second is an Ergun-type inertial term (present in the CFD but negligible at the velocities considered — authors state the model is "close to Darcy's law"). Darcy permeability relation: k_sl = α_l² μ_l / K_sl (16).

**Extraction (their Eqs. 7–12).** Interfacial area per unit volume A_i = α_s A_s = 6α_s/d_s (spherical grains) (7). Linear-driving-force transfer between grain intragranular-pore concentration c_s and intergranular liquid concentration c_l:
∂(c_l α_l)/∂t + ∇·(v⃗_l c_l α_l) = h_sl A_i (c_s − c_l) (8)
∂(c_s φ_v α_s)/∂t = −h_sl A_i (c_s − c_l) (9)
which with constant fractions reduce to (10)–(11). Initial grain concentration c_s0 = φ_0 ρ_s / φ_v (12) — assumes grains initially wet with all soluble coffee pre-dissolved in the intragranular pore space (no partition coefficient). Authors note (12) yields values above the theoretical saturation concentration of Moroney 2015 early in extraction — a knowingly incorrect instantaneous-wetting/dissolution assumption accepted for simplicity.

**Two-grain extension (their Eqs. 13–15),** subscripts 1 (small) and 2 (large):
∂c_l/∂t + ∇·(v⃗ c_l) = [6h_sl1 α_s1/(α_l d_s1)](c_s1 − c_l) + [6h_sl2 α_s2/(α_l d_s2)](c_s2 − c_l) (13)
∂c_si/∂t = −[6h_sli/(φ_vi d_si)](c_si − c_l), i = 1,2 (14)–(15)

**1-D cylindrical reduction (their Eqs. 17–27).** Darcy momentum, z-only; BCs p_l(0,t)=Δp, p_l(L,t)=0 (17) or v_l(0,t)=Q/(α_l A), p_l(L,t)=0 (18); solutions v_l = −(α_l/K_sl)(Δp/L − ρ_l g) (19), p_l = (Δp/L)(L−z) (20). Extraction: single grain (21)–(22) with mass diffusivity D_v via h_sl = D_v/d_s; two-grain (23)–(25) with h_sli = D_v/d_si; axial solute diffusion neglected (advection-dominated); c_l(0,t)=0 (26); fully wetted ICs c_l(z,0)=0, c_s(z,0)=c_s0 (27).

**1-D truncated-cone reduction (their Eqs. 28–30).** Area-corrected 1-D along cone axis, half-angle θ_c, bed inlet z=0 to outlet z=L_B, virtual vertex at L_c > L_B:
r(z) = (L_c−z)tanθ_c, A(z) = π(L_c−z)²tan²θ_c (28)
v_l(z) = Q / [α_l π(L_c−z)² tan²θ_c] (29)
p_l(z) = [K_sl Q/(π α_l² tan²θ_c)] · (L_B−z)/[(L_c−L_B)(L_c−z)] − ρ_l g(L_B−z) (30)
Symbols: α_l, α_s = liquid/solid volume fractions; v⃗_l = liquid velocity; p_l = liquid pressure; μ_l, ρ_l = liquid viscosity, density; d_s = representative grain diameter; K_sl = drag/permeability coefficient; c_l, c_s = solute concentration in intergranular liquid / intragranular pores; h_sl = mass-transfer coefficient; φ_v = intragranular porosity; φ_0 = soluble-coffee volume fraction of grain; ρ_s = coffee true density; Q = volumetric flow rate; Δp = bed pressure drop; A, L = bed cross-section, height. Nothing was simplified away in transcription beyond the authors' own reductions.

## Parameters
Table 2 (per grind, per model configuration; c_s here is the initial value c_s0):

> **ERRATUM (author-confirmed, via `cooper2021`).** The `h_sl` values printed below are the
> CFD-scaled values reported in the 2019 paper; the true mass-transfer coefficients are
> `h_sl(true) = h_sl(reported) / ρ_l`, ρ_l = 965.3 kg m⁻³ (a silent ~10³ correction), and the
> paper used species-specific diffusivities `D_vi = h_sli·d_si` (not a single D_v). The landed
> `data/moroney2019/table2.csv` carries both the reported and the corrected columns. **Any
> transcription-check gate (reproduce the 1-D two-grain c_exit RMSE 5.81/6.23 kg m⁻³) MUST use
> the corrected column or it fails by construction.** See `docs/cards/cooper2021.md`.

| symbol | Fine: single | Fine: 2G small | Fine: 2G large | Coarse: single | Coarse: 2G small | Coarse: 2G large | units | source |
|---|---|---|---|---|---|---|---|---|
| d_s | 3.1823×10⁻⁵ | 2.517×10⁻⁵ | 5.63×10⁻⁴ | 4.5802×10⁻⁵ | 3.536×10⁻⁵ | 9.26×10⁻⁴ | m | fitted (one size fixed from PSD, the other fitted to observed Δp) |
| α_s | 0.8 | 0.5 | 0.3 | 0.75 | 0.45 | 0.3 | – | fitted/assumed (chosen jointly with d_s to match Δp) |
| c_s0 | 358.587 | 358.587 | 358.587 | 305 | 305 | 305 | kg m⁻³ | derived via Eq. 12 from measured max yields |
| h_sl | 4.31562×10⁻⁴ | 5.1207×10⁻⁴ | 1.43×10⁻³ | 9.5285×10⁻⁴ | 1.661×10⁻⁴ | 2.901×10⁻⁴ | m s⁻¹ | fitted (1-D model to exit-concentration data) |

| symbol | value | units | source |
|---|---|---|---|
| ρ_s (true density) | 1400 | kg m⁻³ | measured (Moroney 2015, same coffees) |
| φ_v | 0.56 | – | measured (Moroney 2015) |
| φ_0 fine / coarse | 0.143 / 0.122 | – | derived from measured maximum yields |
| Q | 250 | ml min⁻¹ | measured (set point) |
| dose | 60 | g | measured |
| chamber ID | 59 | mm | measured |
| water T | 90 | °C | measured (set point) |
| Δp fine / coarse (expt) | 2.3 / 0.65 | bar | measured |
| Brix→concentration | 1 °Brix = 8.25 g l⁻¹ | – | measured calibration (Moroney 2015) |
| cone θ_c (half of 60° apex) / outlet R | 30° apex-half / 0.018 | °, m | nominal (design study) |
| D_v | not provided | m² s⁻¹ | not provided (only h_sl values reported; the stated h_sl = D_v/d_s relation is not consistent across the fitted pairs, so a single D_v cannot be recovered) |

Table 1 PSD summary: fine (Jacobs Krönung drip grind) d₃,₂ = 27.34 µm, d₄,₃ = 457.84 µm, 25.52 vol% < 100 µm; coarse (Illy, Cimbali #20) d₃,₂ = 37.78 µm, d₄,₃ = 823.02 µm, 15.08 vol% < 100 µm.

## Calibration and validation offered by the source
Post-fit reconstruction only, on the cylindrical case; the conical case is entirely unvalidated prediction.
- Pressure: fine-grind CFD Δp = 2.319 bar vs. experiment 2.3 bar; coarse 0.657 vs. 0.65 bar. This agreement is circular — the representative grain size / volume fraction was *selected to fit* the observed velocity–pressure relationship (stated explicitly). What it does establish: Darcy suffices for this bed, and the CFD pressure profile is linear (uniform resistance), consistent with the 1-D assumption.
- Exit concentration (cylindrical): single-grain model fits the initial fast regime but cannot capture the slow tail (both grinds). Two-grain model: 1-D RMSE drops from 7.80 → 5.81 kg m⁻³ (fine) and 11.65 → 6.23 kg m⁻³ (coarse); residual error concentrated in the early post-saturation transient. h_sl values were fitted with the 1-D model to the same curves, so this is fit quality, not independent validation. CFD and 1-D agree closely with each other in the cylinder (verification, not validation).
- Mesh verification (conical CFD): grid-convergence study, order of convergence p = 1.85, GCI₂,₃ = 0.016%, GCI₁,₂ = 0.005% (safety factor 1.25) — solid verification hygiene.
- The uniformity results themselves (extraction maps, σ(EY) error bars, Fig. 9–10) have **no experimental counterpart anywhere in the paper**; local EY was not measured.

## Assumptions and validity range
- Saturated bed only; infiltration explicitly excluded (authors note the initial exit concentration would in reality be high, not zero — the control-chart trajectories start from an artificial origin).
- Static, incompressible solid: no consolidation, swelling, fines migration, or grain motion; α_s, φ_v, permeability constant in time and space (uniform microstructure). Authors explicitly list fines segregation, poor tamping, incomplete wetting, and non-uniform water delivery as uniformity drivers *outside* the model.
- One-way flow→extraction coupling; isothermal; single lumped solute; spherical grains (real sphericity 0.75–0.85 acknowledged, ignored).
- Instantaneous wetting/pre-dissolution IC (Eq. 12) overshoots the saturation ceiling early in the shot — early-time c_l is not trustworthy.
- 1-D cone model accurate only for small wall taper; at 60° apex it underpredicts Δp vs. CFD by ~12–14% (7.35 vs. 8.4 bar fine; 1.63 vs. 1.89 bar coarse).
- Conical geometry is pour-over/drip, not an espresso basket; brew ratio (60 g : 1 L) is drip-filter — final states are far over-extracted relative to espresso practice.
- Silent on: pressure-dependent κ(t), multi-species chemistry, temperature, channeling/recirculation (none observed in these geometries, but the method also assumed the homogeneity that would preclude them).

## Interface mapping
Inputs consumed: BedState (porosity → α_l, area/depth → A, L; note the model builds permeability internally from fitted (d_s, α_s) via Gidaspow — supplying BedState.k directly conflicts, adapter would have to invert Eq. 6/16), GrindState (needs the same PSD→representative-sizes adapter as moroney2016: contract carries fines_fraction/radii, model wants per-population d_si and α_si, and here the large size is a pressure-fit, not a PSD statistic), MachineState (fixed Q or fixed Δp, steady only — cannot consume P_of_t).
Outputs produced: c_exit(t) → ShotResultState.tds_pct/EY_pct traces; plus a *candidate new observable* not in ShotResultState: σ(EY) across the bed (spatial std. dev. of local extraction yield) as plotted on their Fig. 10 control chart.
Couplings: offline only. As a runtime extraction stage it would duplicate cameron2020 at lower fidelity (linear driving force, no dissolution nonlinearity, no saturation ceiling). Its legitimate registry roles: (a) parameter/data source (Tables 1–2, measured Δp at fixed Q); (b) definition source for a uniformity observable; (c) documented evidence that in a homogeneous cylindrical bed the flow field is essentially 1-D — which pushes explanations of the pocketscience2024 edge-vs-center EY gap toward wall/boundary/microstructure effects this model excludes, not bulk geometry.

## Extractable data
- Table 2 (all six parameter columns) → data/moroney2019_table2.csv — transcribable now; independent fine+coarse two-population parameterization to set against Cameron's.
- Table 1 PSD summary stats → fold into the grind data ledger; full PSD curves only as Fig. 3 (digitizable, log-x, bimodal).
- Fig. 6(a)–(d): experimental exit-concentration points, fine and coarse, ~0–230 s at 250 ml min⁻¹ — digitizable; but this is the same Philips dataset as Moroney 2015 (Chem. Eng. Sci.), already flagged as the higher-priority primary acquisition target. If Moroney 2015 is acquired, digitizing Fig. 6 here becomes redundant except for the coarse grind (check whether 2015 includes it).
- Measured Δp {2.3, 0.65} bar at Q = 250 ml min⁻¹, 60 g, 59 mm chamber, with Table 1 PSD → two clean permeability anchor points for wadsworth2026.permeability cross-checks (bed height not stated numerically in text — recover from Moroney 2015/2016: L = 0.0405 m appears in moroney2016 for the fine case).
- S1/S2 Appendices (control-chart construction; extraction-variation calculation) and S1/S2 videos exist; no code or raw data files published ("all relevant data within the manuscript and SI").

## Overlaps and conflicts
- **cameron2020.extraction_bdf** (extraction, runtime): competes, lower fidelity — same two-population idea but linear driving force with fitted h_sl, no nonlinear surface dissolution, no per-bed-volume inventory/EY ceiling; pre-dissolution IC knowingly violates the saturation ceiling Cameron-family models respect. Do not implement as runtime.
- **moroney2016** (extraction, calibration): same group, same underlying Philips dataset; moroney2016 is the *higher*-fidelity closed-form treatment (double-porosity with explicit surface + kernel physics), this paper is the coarser LDF version whose novelty is spatial resolution, not kinetics. Complementary only via Table 2 and the coarse-grind data.
- **wadsworth2026.permeability** (packing, calibration): competing permeability closure again (Kozeny–Carman/Gidaspow with pressure-fitted d_s vs. percolation k(R, φ_p)); the two Δp anchors here are usable gate data.
- **brewer2026.streamtube** (bed_dynamics, runtime): complementary framing — both quantify EY dispersion, but streamtube attributes it to lognormal permeability heterogeneity while this paper holds microstructure uniform and derives dispersion from geometry + grain-size populations. σ(EY) here is a floor: the non-uniformity that exists *even in a perfectly homogeneous bed*.
- **pocketscience2024** / candidate radial-evenness gap: this paper's cylindrical result (essentially 1-D flow, uniform resistance) is negative evidence for bulk-flow explanations of edge under-extraction — supports framing that gap around wall effects, water delivery, and microstructure heterogeneity.
- Backlog "observables: scale/measurement kernels": the σ(EY)-on-control-chart construction (Fig. 10, S1 Appendix) is a concrete candidate uniformity observable; also a registry-side reminder that identical (TDS, EY) points can hide very different local-EY distributions.
- Backlog "flow: Forchheimer/inertial": Eq. 6's Ergun term is present but declared negligible here (≤2.3 bar, 250 ml min⁻¹) — consistent with low-Fo expectations, no usable Fo data.
- The conical geometry is out of scope for espresso baskets (schulman2011 geometry ledger governs those); relevant only if the registry ever adds pour-over.

## Implementation estimate
Nothing to implement as a component. If the σ(EY) observable is later adopted, it is an S-effort post-processor over any spatially resolved extraction field (streamtube per-tube EYs would supply it directly). Data transcription (Table 2, Δp anchors, PSD stats, optionally coarse-grind Fig. 6 digitization) is S. Gate design if data is adopted: reproduce the 1-D two-grain c_exit(t) RMSE figures (5.81 / 6.23 kg m⁻³) from Table 2 parameters as a transcription check. **LANDED (2026-07-23):** a `code_verification` gate `gate_moroney2019_ldf_verification` (solver `puckworks/analysis/moroney2019_ldf.py`) now solves the 1-D two-grain LDF reduction (Eqs 17–27) with the cooper2021-corrected h_sl and verifies mass-budget closure, the fast/slow two-timescale exit structure, and the erratum by physical plausibility (corrected D_v ≤ free aqueous diffusion; reported values exceed it). The **RMSE-5.81/6.23 step is still owed** — reproducing it needs moroney2019's own Fig-6 exit-concentration digitization (not in the registry); the current gate is verification, not a fit.

VERDICT: data-only — the kinetics duplicate cameron2020/moroney2016 at lower fidelity and the uniformity results are unvalidated, but Table 2's independent fine/coarse two-population fit, two clean Δp–Q permeability anchors, the coarse-grind extraction curve, and the σ(EY) observable definition are worth holding — effort S

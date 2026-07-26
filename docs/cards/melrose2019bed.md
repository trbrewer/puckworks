# Model card: Melrose 2019 packed-bed polydisperse diffusion kinetics

**Paper/thesis:** Melrose, J.R., Corrochano, B.R., Bakalis, S. "Polydisperse diffusion kinetics of Coffee Brewing — modelling packed beds." Pre-print, 26/09/2019 (companion to the batch pre-print Melrose et al. 2019). No DOI. Underlying experimental data: Corrochano, B. (2017), EngD thesis, Univ. Birmingham. Model equations detailed in Melrose et al. (2014, 2018b).
**Stage(s):** extraction (primary), bed_dynamics (axial-layer pore-space coupling), grind (PSD → two representative sizes) · **Kind:** calibration (needs a measured flow trace as input; runtime coupling would be forced and would duplicate registered extraction)
**Status:** **reviewed 2026-07-25 — data-only, intake BLOCKED and logged.** No runtime port (it is the foundational Melrose base already present at equal-or-higher fidelity via romancorrochano2017/mo2023_2, and it cannot run standalone — it consumes a *measured* flow trace, not a pressure model). The wanted data is figure-only (Figs 1, 2, 8) and the parameter set is incomplete without the batch companion (Y_max + PSD, Melrose 2019 Table 1), so intake needs a **digitization drop + companion acquisition** — logged in `puckworks/data/BLOCKED_INTAKE.md`. Highest-value item is **Fig. 2**: measured transient flow-resistance traces (rise to a maximum at ~20–50 s, then decline to 60–80 s), which are direct *measured* evidence for the κ(t) backlog, where the registry currently has mostly model-side claims.

## Scope and mechanism
Total yield vs. time for espresso-scale packed-bed brewing, modelled as diffusive release of two representative solute species from two representative particle sizes (one fine, one coarse). Inside each particle the diffusion equation is solved with a time-varying surface boundary condition equal to the bed pore-space concentration of its axial layer; particles act as source terms in a convected-flow bed divided into 10–20 axial cylindrical layers. Grind enters through the coarse representative radius (d₄,₃(Co.)/2) and a surface-fines fraction θ_fs that lumps fast-release from fines and broken cell-pockets. Flow is **not modelled**: the measured, transient flow-rate profile is imposed as input. Headline finding: unlike the dilute batch case, packed-bed yield curves do **not** collapse to universal reduced units, so each of 16 runs (4 grinds × 2 packing densities × 2 flow regimes) is fit individually; the fast-release fraction θ_fs is lower in the bed than in batch.

## Governing equations
Concentration/yield definitions (their Eqs. 1–3):
- (1) S(t) = 100·M_e(t)/M_brew(t)   — strength (% w/w)
- (2) Y(t) = 100·M_e(t)/W           — yield (% of dry coffee mass)
- (3) C₀ = Y_max·ρ_g                — initial volumetric solute concentration in a model particle

Predicted reduced yield from the two independent representative species (their Eq. 4):
- (4) Y_sim(t_i)/Y_max = W_mol·Ỹ_mol(t_i, θ_fs) + (1 − W_mol)·Ỹ_cho(t_i, θ_fs)

Weight fixed by matching the longest experimental time point t_n (their Eq. 5), valid because Ỹ_m(t,θ) > 0.95 once t_n > 0.2·τ(R), τ(R) = (R_co)²/D_mol:
- (5) W_mol = [ Y_expt(t_n)/Y_max − Ỹ_cho(t_n, θ_fs) ] / [ Ỹ_mol(t_n, θ_fs) − Ỹ_cho(t_n, θ_fs) ]

Bed-extraction-efficiency closure (their §4.2, from Melrose 2018b), a lightweight diagnostic that ranks reduced-yield curves without a full solve:
- g̃ = τ(R) / τ_bed,   τ(R) = R²/D,   τ_bed = time for a water volume equal to the coffee-particle volume in the bed to flow through it. Smaller g̃ ⇒ lower reduced yield at equal reduced time (finer grind ⇒ smaller g̃; this reverses the batch ordering).

Discussion-level flux identity (their Eq. in §5, not implemented as such): J = A·D·∇C — motivates why bed effects on the effective particle surface area A are folded into θ_fs and re-fitted D.

The four fit parameters are {θ_fs; D_mol; D_cho; W_mol}. The full inside-particle diffusion PDE and the layered-bed convection equations are given only by reference (Melrose 2018b); they are not reproduced in this pre-print and would be needed for any implementation.

**Symbols:** M_e mass of solubles released; M_brew brew mass; W dry coffee dose; Y_max limiting dilute long-time yield (per grind); ρ_g coffee-particle mass density; C₀ initial volumetric particle concentration; D_mol, D_cho hindered in-grain diffusivities of the low-MW ("molecular") and high-MW ("cho") representative species; θ_fs volume fraction assigned to fine particles (fast-release surrogate); W_mol soluble-mass fraction carried by D_mol; τ(R) intra-grain diffusion time; R_co = d₄,₃(Co.)/2 coarse representative radius; g̃, τ_bed bed-efficiency quantities; Ỹ_mol, Ỹ_cho simulated reduced single-species yields.

## Parameters
| symbol | value | units | source |
|---|---|---|---|
| ρ_g | 760 | kg m⁻³ | nominal (average over all PSDs) |
| R_fine | 20 | µm | assumed (fixed from earlier work; batch optimum was ~30) |
| R_coarse | d₄,₃(Co.)/2 | µm | measured (PSD; per grind, values in Melrose 2019 companion Table 1) |
| D_fine (low-MW / high-MW) | 10⁻⁹ / 10⁻¹⁰ | m² s⁻¹ | nominal (bulk values, fixed for fines) |
| D_mol (coarse, fitted) | 2–5 ×10⁻¹⁰ (θ_fs=0.15); ~10⁻⁹ HF, ~0.6×10⁻⁹ LF at θ_fs=0 | m² s⁻¹ | fitted |
| D_cho (coarse, fitted) | 0.2–1.4 ×10⁻¹¹ | m² s⁻¹ | fitted |
| θ_fs | 0–0.25 (global best 0.15; LF 0–0.15, HF 0.15–0.2; grind B ~0.25 LF) | – | fitted |
| W_mol | 0.55–0.75 | – | fitted |
| grinds B/C/D/E d₄,₃ | 200 / 260 / 325 / 360 | µm | measured |
| fine fraction (<100 µm) B/C/D/E | 36 / 27 / 20 / 17 | % vol | measured |
| Y_max | measured for B,E; interpolated for C,D | % | measured/interpolated (values in companion, **not provided here**) |
| bed diameter | 3.7 | cm | measured |
| dose / bulk density / height | 9.5 g @ 480 kg m⁻³, height 1.8 cm; 8 g @ 400 kg m⁻³ | g / kg m⁻³ / cm | measured |
| applied overpressure HF / LF | 3.75 / 1.75 | bar | measured (fixed head) |
| mean flow HF / LF | 3.7 / 1.3 | mL s⁻¹ | measured (transient; Fig. 2) |
| inlet / outlet temperature | 85 / 60→75–80 | °C | measured |
| bed porosity | 0.1–0.2 | – | measured/reported |
| particle porosity (wetted) | 0.5–0.7 | – | reported |
| g̃ (HF400: E/D/C/B) | 22 / 18 / 9 / 5 | – | derived |
| example fits {θ_fs; D_mol/10⁻¹⁰; D_cho/10⁻¹¹; W_mol} | batch E {0.4;5;1;0.71}; bed E400LF {0.05;4;0.8;0.62}; D400LF optimum {0.2;3;0.8;0.65}, MPE 0.2% | – | fitted |

## Calibration and validation offered by the source
Validation is **post-fit reconstruction, per run**, not independent prediction. Fits are to yield-vs-time by direct grid search minimising MPE; W_mol is pinned to the longest time point (Eq. 5). At θ_fs = 0.15 all 16 sets reach MPE < 1.1 %; the D400LF example reaches MPE 0.2 %. Because no reduced-unit collapse holds in the bed, there is no universal parameterization — each set has its own {θ_fs, D_mol, D_cho, W_mol}, and low MPE reflects a 4-parameter fit to ~8 points per curve. The one genuinely predictive test (Fig. 4, E400LF): batch-fit parameters *overpredict* the bed yield even after the pore-space-concentration depression is included; swapping only θ_fs and W_mol to bed values (keeping batch D's) gives a "fair" prediction — i.e. the diffusion constants transfer batch→bed but the fast-release fraction and weight do not. Fitted D's at θ_fs = 0 run higher than physically expected for hindered diffusion (up to ~10⁻⁹ m² s⁻¹), which the authors flag themselves as unphysical, favouring the θ_fs ≈ 0.15 fits.

## Assumptions and validity range
- Coarse range 200–400 µm; fine fraction 17–36 %; espresso-scale bed (3.7 cm dia, ~1.8 cm deep); transient-flow regime characteristic of espresso.
- Homogeneous spherical particles; all real microstructure/heterogeneity absorbed into hindered D's; **particle surface area A held fixed in time** (acknowledged as the main missing physics).
- Release starts only once the bed is filled — no infiltration/wetting/filling-stage release (contrast foster2025).
- **Requires the measured transient flow-rate trace Q(t) as input**; there is no flow/permeability model. The observed rise-to-maximum bed resistance at ~20–50 s then decline to 60–80 s (attributed qualitatively to fines plugging + gas/CO₂ release) is data, not modelled.
- Volumetric-concentration formulation (pore-intrinsic alternative gives "slight" differences).
- Time-scales too short (<~80 s) to reveal the very-high-MW/colloidal species that batch fits needed for grind B beyond 100 s.
- Silent on / not modelled: temperature transient (85→75–80 °C water/grain mixing), gas & CO₂ effects, fines migration/plugging, channelling, bed consolidation, permeability evolution — all either folded into fixed-A + per-run refitting or discussed only qualitatively (§5).
- No collapse ⇒ parameters are per-run and not portable across grind/density/flow.

## Interface mapping
Inputs consumed: GrindState (PSD → coarse d₄,₃(Co.)/2 + fixed fine R=20 µm + fines fraction; needs the same PSD→representative-sizes adapter as moroney2016/romancorrochano2017); BedState (porosity, dose_kg, depth_m, area_m2); a per-grind Y_max (external scalar, not in any contract); and a **measured flow trace Q(t)** — consumed as a ShotResultState.traces input, *not* MachineState.P_of_t. · Outputs produced: Y(t), S(t) → ShotResultState.EY_pct / tds_pct / traces.
Couplings: **offline / calibration only.** Cannot run standalone in the shot chain because it takes measured flow as input rather than pressure; as a runtime extraction stage it would duplicate cameron2020 and romancorrochano2017 at similar-or-lower fidelity. Legitimate registry roles: (a) transcribable espresso-scale bed-brew data; (b) the g̃ = τ(R)/τ_bed closure as a cheap bed-extraction-efficiency diagnostic that predicts the reduced-yield ordering (E≅D>C>B) without a full solve.

## Extractable data
- **Fig. 1a (LF) / 1b (HF):** yield vs time, grinds B/C/D/E × 480/400 kg m⁻³, ~8–9 points each → data/melrose2019bed_yield_time.csv. Symbol convention fully defined in caption. Espresso-scale packed-bed brew curves.
- **Fig. 2:** transient flow-rate traces (HF and LF, multiple runs) showing resistance rise to max at ~20–50 s then decline to steady state at 60–80 s → data/melrose2019bed_flow_transient.csv. **Direct evidence for the bed_dynamics κ(t) backlog item** (rising-then-falling permeability). Many overlapping traces — digitize representative HF/LF envelopes.
- **Fig. 4:** E400LF bed data + batch E data co-plotted with four fit lines (batch-vs-bed comparison).
- **Figs. 5 & 7:** MPE landscape vs D_mol (D400LF) and MPE sensitivity vs θ_fs (all sets) — fit-quality maps.
- **Figs. 8a/8b/8c:** fitted D_mol, D_cho, W_mol vs d₄,₃ for θ_fs = 0 and 0.15, LF/HF → parameter-vs-grind maps → data/melrose2019bed_fits.csv.
- Reported point fits and g̃ values (see Parameters).
- Raw data/code: **none published** (pre-print); underlying data is the Corrochano 2017 thesis. Y_max and PSD live in the batch companion (Melrose 2019, Table 1), **not in this paper** — acquire the companion to complete the parameter set.

## Overlaps and conflicts
- **romancorrochano2017_extraction / _permeability (same dataset, same author):** this pre-print re-analyses the *same* Corrochano-2017 packed-bed brews with the Melrose two-species diffusion model. Same-provenance data; complementary treatments — romancorrochano2017 gives the fuller multi-scale extraction + parameter-free microstructural Deff route, this gives the g̃ closure and the specific 4-parameter bed fits. Not new experimental data relative to that thesis, but more cleanly packaged for the bed curves + flow transients.
- **mo2023 (bed_dynamics/extraction, runtime):** mo2023 explicitly extends "the classic Melrose/Li 1-D two-population coarse-grained extraction model" — **this is that base model.** mo2023 supersedes it by adding swelling and a fixed-Δp Carman–Kozeny flow closure (this paper has *no* flow model at all).
- **cameron2020.extraction_bdf (registry #1, runtime):** competes at lower fidelity — pure hindered diffusion + partition BC, no surface-dissolution nonlinearity, no per-bed-volume EY ceiling; and needs measured flow.
- **moroney2019 (LDF):** sibling; the paper explicitly contrasts its diffusion approach against Moroney's first-order rate equations.
- **foster2025.infiltration (registry #7):** this model discards filling/wetting (release starts at bed-filled). The early-time yield *depression* here is a pore-space-concentration/diffusion effect, distinct from foster2025's infiltration delay; the infiltration↔extraction coupling backlog would supersede the saturated-start assumption.
- **bed_dynamics κ(t) backlog:** Fig. 2 flow transients complement it directly (measured rising-then-falling resistance, attributed to fines plugging + gas).
- **brewer2026.streamtube:** no channelling/heterogeneity here (homogeneous axial layers); the per-run g̃ scatter is an alternative bed-efficiency framing rather than a lognormal-tube one.

## Implementation estimate
No runtime port recommended: it duplicates registered extraction, requires a measured flow trace instead of a pressure model, and its full particle/bed PDEs are only referenced (Melrose 2018b), not printed here — reconstructing them would be **L** and would land at romancorrochano2017/mo2023 fidelity with worse portability. Data intake is **S**: digitize Figs. 1, 2, 8; transcribe the reported point fits and g̃ values; add the flow-transient trace to the κ(t) evidence set. Dependency/gate: Y_max and PSD must be pulled from the batch companion (Melrose 2019) before the fitted parameters are usable; the g̃ ranking (E≅D>C>B) is a cheap sanity gate for any bed-extraction-efficiency closure the registry adds.

VERDICT: data-only — the model is the foundational Melrose two-particle/two-species diffusion base already present at equal/higher fidelity (romancorrochano2017, extended by mo2023) and can't run standalone without a measured flow trace, but its espresso-scale packed-bed yield curves, transient flow-resistance traces (κ(t) backlog), and θ_fs/D/W_mol fit-vs-grind maps are worth transcribing — effort S.

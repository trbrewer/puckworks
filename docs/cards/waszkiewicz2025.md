# Model card: Waszkiewicz 2025 poroelastic flow regulation

**Paper:** Waszkiewicz, Myck, Białas, Puciata-Mroczynska, Dzikowski, Szymczak, Lisicki, "Under pressure: poroelastic regulation of flow in espresso brewing," arXiv:2512.21528 [physics.flu-dyn] (Dec 2025). No journal DOI yet; code+data DOI on Zenodo.
**Stage(s):** bed_dynamics, flow · **Kind:** runtime
**Status:** card-only

## Scope and mechanism
Quasi-static 1D poroelastic model of a saturated, tamped coffee bed: Darcy flow with a porosity-dependent Carman–Kozeny permeability, coupled to Terzaghi effective stress and a linear (Hookean) strain–porosity constitutive law (Hewitt et al. 2016 hydrogel-pack model, simplified). Pressure compacts the bed, reducing permeability, so the equilibrium pressure–flow curve is Darcy-linear below ~5 bar and saturates in the 9-bar brewing regime. A time-dependent extension makes the stress-free porosity Φ(t) proportional to the dissolved mass fraction, giving a closed-form predictor of Q(t) during the shot from two rig-calibration constants (P_c, Q_c) plus the dissolution curve. Explicitly does NOT model the first ~5–10 s (unsaturated wetting, air expulsion, swelling).

## Governing equations
Numbering follows the paper.

1. Local Darcy flow, superficial velocity (Eq. 2): u(z) = (k(φ(z))/μ) dp/dz.
2. Mechanical equilibrium / Terzaghi effective stress (Eq. 3): ∂/∂z (σ(z) + p(z)) = 0, with u(z) = const (mass balance).
3. Integrated (Kirchhoff) pressure–flow relation (Eqs. 5–7): Q = K(P)·A/(μ h₀), where K(σ) = ∫₀^σ k(φ(σ′)) dσ′, boundary conditions σ(z=h₀)=0 (free surface), σ(z=0)=P (basket mesh).
4. Carman–Kozeny closure (Eq. 8): k(φ) = (d_p²/κ)·φ³/(1−φ)², κ = 150.
5. Constitutive laws (Eqs. 9–10): strain e = (Φ−φ)/(1−φ); σ = Y e. Hence (Eq. 11): k(σ) = (d_p²/κ)·(Φ−σ/Y)³ / [(Φ−1)²(1−σ/Y)], valid for σ < ΦY; pores close completely at σ = ΦY.
6. Normalisation (Eqs. 13–14): P̂ = P/(YΦ), Q̂ = Q/Q_m(Φ), Q_m(Φ) = Q_ref·F(Φ), Q_ref = A d_p² Y/(κ μ h₀), F(Φ) = [Φ(Φ(11Φ−15)+6) − 6(Φ−1)³ ln(1−Φ)] / [6(Φ−1)²].
7. Universal equilibrium curve, Φ→0 limit of Eq. 15 (Eq. 16): Q̂ ≈ P̂(4 − 6P̂ + 4P̂² − P̂³). The authors show Φ-dependence of the shape is negligible over physical Φ, so Y, d_p, Φ never need to be known separately — only the calibration pair (P_c, Q_c) = (Y Φ_m, Q_m(Φ_m)).
8. Time-dependent extension (Eqs. 17–18): Q(t) = Q_c · [F(Φ(t))/F(Φ_m)] · Q̂(P Φ_m / (P_c Φ(t))), with Φ(t) = m_d(t)/m₀.
9. Empirical dissolution kinetics (Eqs. 19–20): TDS(t) = (k_t/2)[1 − tanh((t−ℓ_t)/m_t)]; m_d(t) = (k_m/2)[1 + tanh((t−ℓ_m)/m_m)]. Φ_m = k_m/m₀.

Symbols: Q volumetric/mass flow; u superficial velocity; A bed cross-section; h₀ initial bed height; μ viscosity; p pore pressure; σ matrix (effective) stress; P basket gauge pressure; φ local porosity; Φ stress-free porosity; e strain; Y Young's modulus of the wetted bed; d_p effective pore diameter; κ Kozeny constant; m₀ dose; m_d dissolved mass. Nothing is simplified away beyond the authors' own Φ→0 limit (Eq. 16), which they justify numerically (Fig. 4).

## Parameters
| symbol | value | units | source |
|---|---|---|---|
| κ | 150 | – | nominal (Carman–Kozeny literature) |
| Q_c | 1.90 ± 0.15 | g/s | fitted (60 brews, 11 pressures) |
| P_c | 12 ± 3 | bar | fitted (same fit) |
| k_t | 25.6 ± 1.3 | % | fitted (TDS sigmoid) |
| ℓ_t | 20.9 ± 0.9 | s | fitted |
| m_t | 8.8 ± 1.5 | s | fitted |
| k_m | 2.257 ± 0.001 | g | fitted (dissolved-mass sigmoid) |
| ℓ_m | 19.83 ± 0.01 | s | fitted |
| m_m | 9.34 ± 0.02 | s | fitted |
| Φ_m | ≈ 0.122 | – | derived (k_m/m₀) |
| m₀ | 18.50 ± 0.05 | g | measured (dose) |
| Y | not provided for wet grounds | bar | ~400 bar quoted for whole roasted beans (literature reference only, not used) |
| d_p | not provided | m | folded into Q_c; ~6 µm inferred order-of-magnitude in Discussion |

Rig context: Sanremo Zoe, 58 mm basket, Fiorenzato F64 at 1.9, single Brazilian light-medium roast, 20 kg tamp, WDT. Calibration constants are per-rig, per-coffee, per-grind.

## Calibration and validation offered by the source
Equilibrium: 60 brews at 11 basket pressures (~1–12.5 bar), long-run flow = mean of t = 110–120 s. Two-parameter fit (Q_c, P_c) of Eq. 16 reproduces Darcy-linear behaviour < 5 bar and saturation above (Fig. 6). No goodness-of-fit statistic is reported; P_c = 12 ± 3 bar sits at the edge of the measured range and carries 25% uncertainty, so the plateau constrains it weakly. The highest-pressure point (~12.5 bar) dips below the fit — the model is monotone up to P̂ = 1 and cannot produce the slight flow *decrease* the data (and Fig. 5C) hint at at the highest pressures.

Time-dependent: with Φ(t) from the fitted m_d(t) and NO additional free parameters, Q(t) at 9 bar approximately matches the measured flow ramp (Fig. 8A); the authors state it "fails to grasp the quantitative dynamics" at the lowest pressures and "becomes increasingly accurate at higher pressures" (Fig. 8B). No error metrics given; call this semi-quantitative. Note a soft circularity: m_d(t) is derived from TDS(t)×Q(t) measured on the same rig, so the time-dependent validation is not fully out-of-sample.

Supporting evidence: control experiment with 200 µm glass beads (negligible resistance → naive CK+grind-size Darcy overestimates flow ×10³); pre/post-brew µ-CT at 20 µm showing swelling, horizontal delaminations, and basket lift-off; repeated on/off brewing raises flow without extra dissolution (channeling via delamination, Fig. 10).

## Assumptions and validity range
- Quasi-static, 1D, fully saturated; silent on the first ~5–10 s (wetting/air expulsion/swelling) — the regime Foster 2025 owns.
- Linear Hookean elasticity; homogeneous bed; no plasticity or hysteresis, yet Fig. 10 shows strong history dependence (delamination) the model cannot represent.
- Carman–Kozeny: authors themselves say it is "of little predictive value" and breaks down as Φ→0; universal-curve insensitivity to Φ may be an artifact of this closure.
- Φ(t) = m_d(t)/m₀ attributes all porosity change to dissolution while their own CT shows large swelling; this identification is untested independently.
- Predicts complete flow shut-off for P > ΦY — offered as qualitative only.
- No fines migration, no channeling, no temperature dependence; single coffee/grind/dose; constants not transferable without re-calibration.
- Time-dependent model quantitatively wrong at low pressures (< ~5 bar), where plain Darcy suffices anyway.

## Interface mapping
Inputs consumed: MachineState.P_of_t as BASKET pressure — the paper's quadratic brewer pressure-drop calibration (Fig. 2B) is exactly the pump→basket adapter our "machine mode" backlog wants; BedState.area_m2, depth_m; dissolved-mass trajectory m_d(t) either from the empirical sigmoid (Eq. 20, calibration constants) or, better, from cameron2020.extraction_bdf's running extracted mass.
Outputs produced: Q(t) trace → ShotResultState.traces / beverage_g; equivalently a pressure- and time-dependent effective kappa replacing the constant BedState.kappa.
Couplings: runtime, cheap (closed-form algebra per timestep). Natural two-way coupling with extraction (extraction gives m_d(t) → Φ(t) → Q(t) → advection back into extraction). Adapter needed: per-rig (P_c, Q_c) calibration step — a small offline calibration chain feeding a runtime component. Fits the registry pattern without forcing a mega-model.

## Extractable data
All data and analysis code public (GitHub + Zenodo) — top rank per registry value ceiling. Worth transcribing into puckworks/data/:
- Long-run flow vs basket pressure, 11 points with SE (Fig. 6) → gate target.
- P(t), mass(t), Q(t) traces at 11 pressures, 60 brews (Fig. 5) — validation set for any bed_dynamics/flow component, including the rising-flow residual question.
- Time-resolved TDS(t) in 5 s fractions (Fig. 7B) and derived m_d(t) — first per-interval TDS dataset in the registry; validation data for the extraction stage independent of Cameron.
- Brewer pressure-drop quadratic calibration (Fig. 2B) — machine-stage pipe resistance.
- Mastersizer PSD (Fig. 3, bimodal ~50/100–200 µm) — grind stage.
- Pre/post-brew CT slices (Fig. 9) — qualitative; raw volumes availability unclear, check repo.

## Overlaps and conflicts
- Directly fills the open backlog item "bed_dynamics: pressure/history-dependent permeability kappa(t) (compaction/swelling — competing explanation for rising-flow residual)": this IS that competing explanation, with data. Their dissolution-driven Φ(t) is an alternative to fines-migration (brewer2026.streamtube Rung B) for the rising-flow transient — the Fig. 5 traces let both be tested against the same data.
- Competes with brewer2026.streamtube's channeling closure as the explanation for non-Darcy behaviour; simultaneously supports channeling as a *separate* pathology (Fig. 10 delamination experiment). Not mutually exclusive; the equilibrium saturation curve is evidence streamtube's lognormal alone doesn't capture.
- Complements wadsworth2026.permeability: opposite closure choice (CK vs percolation), and their glass-bead control + ~6 µm effective pore estimate is independent support that tamped-bed resistance is not set by grain size — consistent with Wadsworth's tamped-regime gap and the phi_c ≈ 0.11 reconciliation. A percolation-form k(φ) inside this poroelastic framework (they suggest exactly this) would merge the two.
- Complements foster2025.infiltration cleanly by regime: Foster owns t < ~10 s dry-bed wetting; this model owns the saturated remainder. Together they nearly span the shot.
- Touches cameron2020.extraction: their claim that most solubles dissolve "almost instantaneously" (sigmoidal TDS, ~20 s timescale set by flow, not kinetics) tensions Cameron's diffusion-limited boulder population; the TDS(t) fractions are a discriminating dataset.
- Provides machine-stage calibration data (brewer quadratic) for the "machine mode" backlog.

## Implementation estimate
Small: Eqs. 16, 14, 18–20 are closed-form; a standalone component with (P_c, Q_c, Φ_m) config is a few dozen lines. Gate: reproduce Fig. 6 fit (Q_c = 1.90 g/s, P_c = 12 bar against their published 11-point curve) and the 9-bar Q(t) trace of Fig. 8A from their Zenodo data. Coupling Φ(t) to cameron2020's dissolved mass instead of the empirical sigmoid is a second step (M) and changes early-shot advection — pairs with the infiltration↔extraction coupling backlog.

VERDICT: implement-now — closed-form, fills the bed_dynamics pressure-dependent-permeability backlog with the first public rig dataset (traces, TDS fractions, calibration curve) to gate it against — effort S

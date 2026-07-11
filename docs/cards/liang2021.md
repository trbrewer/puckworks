# Model card: Liang 2021 immersion equilibrium desorption

**Paper:** Liang, Chan & Ristenpart, "An equilibrium desorption model for the strength and extraction yield of full immersion brewed coffee," Sci. Rep. 11, 6904 (2021). DOI 10.1038/s41598-021-85787-1
**Stage(s):** extraction, observables · **Kind:** calibration
**Status:** proposed

## Scope and mechanism
Pseudo-equilibrium desorption model for FULL IMMERSION brewing (steeping/cupping),
not flow extraction. All chemical species are lumped into a single averaged
adsorption/desorption equilibrium with constant K; at steady state a fixed fraction
K·Emax of the grounds' mass dissolves, independent of brew ratio, while TDS scales
inversely with brew ratio. A companion measurement model corrects the standard
oven-drying extraction measurement for brew retained in spent grounds and for
volatilization during baking. The paper is silent on transient kinetics by design
(no rate constants reported); it predicts endpoints only.

## Governing equations
Equation numbers are the paper's.

1. Brew ratio (Eq. 1): R_brew = M_w / M_g, with M_w water mass, M_g dry grounds mass.
2. Species balance and equilibrium (Eqs. 2–8): adsorbed vs dissolved concentrations
   C_A = M_A/M_L, C_D = M_D/M_L (per liquid mass M_L); conservation M_A + M_D = M_tot
   with M_tot = E_max·M_g (Eqs. 4–5); steady state dC_A/dt = 0 gives
   C_D = K·C_tot with K = k_D/(k_D + k_A) (Eqs. 7–8). k_D, k_A are first-order
   desorption/adsorption rate constants (never individually determined).
3. Equilibrium TDS (Eq. 11): TDS = K·E_max / (R_brew + K·E_max);
   simplified (Eq. 12) TDS ≈ K·E_max / R_brew for R_brew >> K·E_max.
4. Equilibrium extraction yield (Eqs. 13, 15, 17): E = M_d/M_g = K·E_max,
   independent of R_brew; measurement form E = TDS/(1−TDS)·R_brew (Eq. 17).
5. Oven-drying measurement kernel (Eqs. 18–24):
   E_oven = (M_g − M_dried)/M_g (Eq. 18);
   E_oven = K·E_max·(1 − R_ret/(R_brew + K·E_max)) + R_vol (Eq. 22),
   ≈ K·E_max·(1 − R_ret/R_brew) when R_vol negligible and R_brew >> K·E_max (Eq. 23);
   retention ratio from measurables: R_ret = R_brew/(1−TDS) − M_brew/M_g (Eq. 24).
   R_ret = M_ret/M_g (liquid retained in spent grounds), R_vol = M_vol/M_g
   (solids volatilized during baking).
Nothing is simplified away here beyond the paper's own approximations, which are
stated with their conditions.

## Parameters
| symbol | value | units | source |
|---|---|---|---|
| E_max | 0.30 | – | nominal (assumed "with perfect confidence"; cites Moroney) |
| K (1-L brews, blend) | 0.717 ± 0.007 (95% CI) | – | fitted (conditional on E_max = 0.3) |
| K·E_max (1-L, lumped) | 0.215 ± 0.002 | – | fitted |
| K (cupping, caffeinated) | 0.792 ± 0.004 | – | fitted (conditional on E_max = 0.3) |
| K (cupping, decaf) | 0.726 ± 0.006 | – | fitted (conditional on E_max = 0.3) |
| K·E_max (cupping, caf / decaf) | 0.240 ± 0.002 / 0.218 ± 0.002 | – | fitted |
| E at equilibrium (1-L, R_brew ≥ 3) | 20.70 ± 1.08 | % | measured (via Eq. 17, no fit) |
| E (cupping, caf / decaf) | 23.9 ± 0.6 / 22.2 ± 0.4 | % | measured |
| R_ret (1-L average) | 2.48 ± 0.19 | g/g | measured (via Eq. 24) |
| R_vol | 0.0234 ± 0.006 (direct) / 0.0228 (regressed intercept) | g/g | measured / fitted |
| k_D, k_A individually | not provided | 1/s | – |

Only the ratio K is identifiable; the kinetic constants are not.

## Calibration and validation offered by the source
99 TDS values from 1-L brews across R_brew 2–25, 80–99 °C, grind settings 2–6:
Eq. 11 fit with single K; inverse-ratio linear check (Eq. 12) gives R = 0.999,
p = 3.66e-105. Cupping (5 Peet's roasts, R_brew 12–21): R = 0.992 (caf) and
0.997 (decaf). Caveat on circularity: the TDS-vs-R_brew fit determines K from
the same data it describes, so the fit quality mainly validates the 1/R_brew
functional form. The genuinely independent predictions that were confirmed are:
(a) E is flat in R_brew (~21% over R_brew 3–25, computed from TDS with no fitted
parameter); (b) E is insensitive to temperature (80–99 °C), grind (x50 579–1311 µm,
though weakly negatively correlated, spread within ~4 pts), and roast level
(four regular roasts indistinguishable); (c) E_oven under-reads E with the
R_ret/R_brew structure of Eq. 23, with the residual gap quantitatively consistent
with the independently measured R_vol ≈ 2.3%. Decaf sits systematically lower
(K·E_max 0.218 vs 0.240). Cupping K exceeds 1-L K for the same nominal E_max;
authors flag the discrepancy (degassing/day-of-roast confound) as unresolved.

## Assumptions and validity range
- Full immersion at pseudo-equilibrium only; transient dynamics deliberately
  excluded (equilibrium reached ~20 min at R_brew ≥ 12, ~45–90 min at R_brew = 5).
- Single lumped species; no composition information (explicitly cannot
  distinguish brews with equal TDS/E but different chemistry).
- Fails at R_brew = 2 ("moist sludge", below R_ret ≈ 2.5, incomplete wetting);
  authors excluded these points. Validity R_brew ≥ 3.
- Hot brews 80–99 °C only; cold brew (4–24 °C) explicitly untested.
- Neglects evaporation and water adsorbed to grounds (Eq. 10); neglects
  volatilization of dissolved solids in the brew itself.
- E_max = 0.3 is assumed, not measured; all quoted K values inherit this.
- Says nothing about flow/percolation brewing — NOT a model of espresso
  extraction and cannot be placed in the runtime shot chain.

## Interface mapping
Inputs consumed: none from the shot chain (R_brew, temperature, grind are
protocol inputs, not contract fields). Outputs produced: none directly;
informs priors/consistency checks.
Couplings: offline calibration only. Two uses: (1) an equilibrium-ceiling
consistency check for extraction — K < 1 formalizes that even at infinite time
not all soluble mass (E_max) dissolves, bounding long-time EY at ~21–24% under
immersion conditions, below cameron2020's saturated-inventory ceiling of 29.6%;
(2) the oven-drying/retention kernel (Eqs. 18–24) is a measurement-kernel
prototype for the observables stage — any component comparing predicted EY to
practitioner oven-dry or retained-liquid measurements needs exactly this
correction. Adapter: trivial (scalar algebra); no state contracts touched.

## Extractable data
- Fig. 3: 99 equilibrium TDS values vs R_brew (with temperature/grind labels) —
  digitize to data/liang2021_fig3.csv; the fitted K and K·E_max are in-text.
- Fig. 4: paired E and E_oven vs R_brew (99 points each) — the E_oven branch is
  the useful one (retention-kernel validation).
- Fig. 5: cupping TDS and E vs R_brew for 5 roast levels incl. decaf.
- Table 1: full brewing protocol matrix (transcribable as-is).
- Supplementary Fig. S1: PSDs for grinder settings 2–6 (Sympatec laser), x50
  580–1310 µm — useful grind-stage reference for a second grinder.
- No code or raw data repository; open-access PDF + supplementary figures only,
  so everything must be digitized from plots.

## Overlaps and conflicts
- cameron2020.extraction_bdf: complements. Cameron models rate-limited flow
  extraction with per-bed-volume inventory (ceiling 29.6% ≈ E_max here); Liang
  gives the equilibrium endpoint of the desorption isotherm (K·E_max ≈ 0.215).
  The K < 1 equilibrium partition is an atom Cameron's dissolution kinetics
  do not carry — worth a gate: does cameron2020 run to ~30% or ~21% EY in the
  long-time immersion limit?
- Open backlog "observables: scale/measurement kernels": the E_oven/R_ret/R_vol
  analysis is a ready-made measurement kernel, and R_ret (liquid retained per
  gram of grounds, ~2.5 g/g in immersion) is conceptually adjacent to the fitted
  W_dead in foster2025 (retained-water accounting), though regimes differ.
- Open backlog "extraction: multi-class solute chemistry": counterpoint — this
  paper demonstrates how far a single lumped species goes at the TDS/EY level,
  a useful null model against which multi-class components must show added value.
- No conflict with wadsworth2026 or the flow/bed_dynamics components (no
  permeability or transport content).

## Implementation estimate
Small: closed-form algebra, no ODEs. Main cost is digitizing Figs. 3–5 for the
data/ folder and writing the equilibrium-limit gate against cameron2020.
No dependencies. Gate design: reproduce K·E_max = 0.215 ± 0.002 from digitized
Fig. 3 by refitting Eq. 11 (R_brew ≥ 3), and reproduce the Eq. 23 E_oven curve
with measured R_ret, R_vol.

VERDICT: calibration-provider — supplies the equilibrium extraction ceiling (K·E_max) as a long-time consistency check on cameron2020 and a transcribable oven-drying/retention measurement kernel for the observables backlog, at closed-form cost — effort S

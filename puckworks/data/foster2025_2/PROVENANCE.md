# foster2025_2 (machine mode) — data provenance

Source card: `docs/cards/foster2025_2.md` (ROADMAP items 0.11 / 1.6).

**Origin:** Foster, Lee, Moroney, Prjamkov, Salamon, Smith, Petrassem-de-Sousa,
Vynnycky, *"Dynamics of liquid infiltration into an espresso bed using
time-resolved micro-computed tomography,"* **Phys. Fluids 37, 013383 (2025)**,
DOI `10.1063/5.0245167`. **No code or data repository published** (card + §5.8);
CT figures must be hand-digitized.

## Files
| file | source | extraction | content |
|---|---|---|---|
| `foster2025_params.csv` | card Table I/II | **transcription** | fine-grind machine-mode params (L, H0, A, Q_m, R_f, p_m, β, fitted k/φ_T, t_shift) + reported t_p/t_s. |

## Landed (1.6, 2026-07-11)
`foster2025.machine_mode` (machine, runtime): the pump/headspace/front ODE
(Eqs. 2-27) ported from the card. **Reproduces t_p = 0.823 s, t_s = 6.669 s**
from the Table I/II parameters (verification-gated). The reported times are the
model times plus the fitted `t_shift = 0.796 s` start alignment — a detail caught
by checking against the published values (model t_p = 0.027 s, t_s = 5.87 s).

## Digitized figures landed (Tim, 2026-07-11) — validation complete
- `fig15_flow_pressure.csv` — **Q_norm = bed flow min(Q_p, f)/Q_m (Eq 18)**, NOT
  pump flow (the earlier confusion). Model reproduces the flow-minimum
  **Q/Qm = 0.181 at t = 2.0 s** with RMSE 1e-4 → the **P2 null baseline** for
  Sprint 9. (Tim reproduced this curve by solving Eqs 32-38, so it is a
  verification of the port, not a pixel trace.)
- `fig12_14_fitted_curves.csv` — s_fit/w_fit/H_fit (paper's exact ODE) + CT data
  (s_data/H_data). Model matches the fitted curves to **line width** (s RMSE
  0.002 mm, H RMSE 0.053 mm) and brackets **4-5/8** CT points within error
  (qualitative-good, matching the paper's own claim).
- `fig6_front_position.csv`, `fig8_headspace.csv` — whole-bed-fit s(t) / -H(t).
  NOTE (per Tim's README): these use a DIFFERENT analysis than Fig 12-14
  (whole-bed sigmoid vs 5-line mean) and differ by ~1 s onset — the gate
  validates against Fig 12-14, which is the model's own comparison basis.

See `README_digitization.md` for the full digitization methodology + caveats.

## Dated scope correction — 2026-10-03

MODEL-FOSTER2025-POSTSAT-001 preserves the historical entries above. The old
machine solver stopped at saturation and held H constant afterwards; the old
Figure 15 flow gate scored only ponding through saturation. Its early passing
result did not qualify the tail. The corrected existing component integrates
source Eq. 29/38 and compares both normalized bed inflow and absolute headspace
pressure through reported 10 s, with dimensional and rounded-fixture cases
reported separately in `docs/analysis/model_foster2025_postsat_001/`.
Canonical dataset IDs are `foster2025_2/params`, `foster2025_2/fig15_flow`, and
`foster2025_2/fig12_14_curves`. No data bytes, roles, rights or fitting changed.
Figure 15 is equation-generated verification; Figure 12–14 retains the I-045
post-fit/same-campaign role. PHYSICAL_VALIDATION=NOT_ESTABLISHED.

## Dated radial observer intake — 2026-10-24

`foster2025_2/fig8_fig9_radial_front` adds JSON plus flat CSV with exactly 90
canonical annulus/scan slots. Methods/Figures 6–9, native pixel identities, rights,
fit-versus-rule eligibility, visibility, duplicate linkage and calibration are
recorded in [SOURCE_NOTES](../../../docs/analysis/sci_md_foster_radial_front_001/SOURCE_NOTES.md).
The historical line above describing both Figure 6/8 files as whole-bed-fit is
over-broad: Figure 6 is a whole-bed s fit; Figure 8 CSV is the mean and across-shell
SD of radial **headspace** estimates, not the ten infiltration interfaces.
The new intake preserves those old bytes and the different Figure 12–14 observer.

Primary t=3/4/5 s: center variation resolves graphically, with nominal minimax
costs 0.061/0.055/0.015 bed depths; outermost is shallower than innermost.
The 4/5 s displayed-extent cohorts admit a common position for every reading
under the frozen contract; complete 3 s is unsupported due to one hidden cap. This does not prove physical uniformity, sharpness,
binary saturation or model form. [Bounded result](../../../docs/analysis/sci_md_foster_radial_front_001/RESULT.md).
Source-derived numerical/visual assets retain Foster et al. ©2025 CC BY-NC 4.0;
UL wrapper separately states CC BY-NC-SA 4.0. Not relicensed under MIT.
G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE / TARGET_EXPOSED /
SOURCE_INTERNAL / NONSCORING. PHYSICAL_VALIDATION=NOT_ESTABLISHED.

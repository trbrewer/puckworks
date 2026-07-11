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

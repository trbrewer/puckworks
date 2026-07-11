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

## Pending your digitized figures (validation upgrade)
- `fig6_front_position.csv` — s(t) front position vs time (front-trajectory
  validation vs CT).
- `fig8_headspace.csv` — H(t) headspace level vs time.
- `fig15_flow_pressure.csv` — normalized pump flow + headspace pressure vs time
  (the flow-minimum signature; P2 null baseline for Sprint 9). The model's full
  minimum/recovery shape is validated once this lands.

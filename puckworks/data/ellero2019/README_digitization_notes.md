# Digitization notes — Figures 2–4 (inverse/direct discharge, fines migration + caffeine extraction)

Method: pixel-level extraction from the uploaded screenshots. Axis calibration fitted from
detected tick-mark pixel positions on each panel (residuals < 1 px). Curves extracted by
color classification with per-column median; legend boxes and in-plot annotations masked.
LBM noise on Re curves is preserved via bin-averaging, not smoothed away.

## Files
| File | Source panel | Grid |
|---|---|---|
| fig2_inverse_discharge_applied_forcing.csv | Fig 2 left | exact step breakpoints |
| fig2_inverse_discharge_reynolds_vs_theta.csv | Fig 2 right (6 curves) | dt = 0.25 t/tnu |
| fig2_inverse_discharge_reynolds_data_ref8.csv | Fig 2 right (open circles) | per-marker |
| fig3_direct_discharge_reynolds_vs_theta.csv | Fig 3 left | dt = 0.25 |
| fig3_direct_discharge_cumulative_output_concentration.csv | Fig 3 right | dt = 0.5 |
| fig4_direct_discharge_caffeine_content_vary_Db.csv | Fig 4 left (Dr=0.0005, theta=0.0058) | dt = 0.5 |
| fig4_direct_discharge_caffeine_content_vary_Dr.csv | Fig 4 right (Db=0.005, theta=0.0058) | dt = 0.5 |

Units: t_over_tnu dimensionless; Re absolute value; content in percent (as plotted).

## Caveats
1. **Fig 2 right — gaps in curve columns** correspond to the pump-off intervals
   (t/tnu ~ 37.6–52.6 and 75.2–90.2), where all curves sit at Re ~ 0 on the axis and
   overplot each other; values there should be read as ~0.
2. **Fig 2 right — theta=0.005 (red) curve** was separated from the same-colored Ref.[8]
   markers by continuity tracking within each pump-on window; vertical jump columns at the
   four forcing transitions are excluded.
3. **Ref.[8] markers (38 recovered):** ring centers located by component analysis after
   subtracting the theta=0.005 curve. In the first descent (t/tnu < ~6) several markers ride
   directly on the red curve; roughly 2–3 markers there (near t~1–4, Re~8–10) were
   unrecoverable, and the recovered early points carry higher uncertainty (~+/-0.3 in Re).
   The two low points near t~73 (Re 0.3–0.7) are plausibly real but sit near the
   window-end transition; treat with caution.
4. **Fig 2 left forcing** is emitted as exact breakpoints (levels snapped to -1/0/+1);
   detected transition times: t/tnu = 37.58, 52.62, 75.19, 90.24.
5. **Fig 3 right blue curve** passes within a few px of the legend's blue key line;
   a 16-px band around the key was masked and the short gap bridged by the column median
   on either side.
6. Estimated digitization accuracy: ~+/-0.05 in Re, ~+/-0.0003 in content [%]
   (Fig 3R/4L), ~+/-0.0008 (Fig 4R), plus the plotted line width itself.

# Digitized data: Foster et al., Phys. Fluids 37, 013383 (2025)

## Files
1. **fig6_front_position.csv** — Fig. 6 (right panel), wetting front s(t), fine grind, whole-bed sigmoid-fit analysis. Pixel-digitized markers and cap-to-cap error bars.
2. **fig8_headspace.csv** — Fig. 8, headspace/ponded level -H(t). H = mean of the 10 radial-shell marker positions at each t; H_err = standard deviation across the 10 shells (not the plotted per-shell error bars).
3. **fig15_flow_pressure.csv** — Fig. 15 curves reproduced by solving the paper's model exactly (Eqs. 32-38, Table I/II parameters), not pixel-traced. Q_norm = flow through the coffee bed / Qm = min(Qp, f(H,s)) per Eq. 18, matching the Fig. 15(b) caption. p_h_norm = p_h/p_m.
4. **fig12_14_fitted_curves.csv** — model fitted curves s, w = H + phi_T*s, H (mm, exact ODE solution) on a 0.02 s grid, plus pixel-digitized mean data (squares) with std bars at t = 1-8 s.

## Model validation (exact reproduction, not digitization)
- Parameters: Pm=14.8038, R=2e-4, H=0.782, G=9.3195e-4, Pc=0.0987, beta=1.226, K=0.0495 (fitted), phi_T=0.322 (fitted), t_shift=0.796 s. Time scale A*L/Qm = 5.162 s.
- Reproduced checkpoints: ponding at t=0.823 s (paper: 0.823 s), saturation at t=6.667 s (paper: 6.669 s), flow minimum Q/Qm = 0.181 at t = 2.0 s (figure: ~0.18 at ~2 s).
- Computed curves overlaid on the printed Figs. 12-14 curves align to within line width.

## Units and conventions
- Dimensionless z is scaled so bed depth = 1; mm conversion uses L = 9.975 mm throughout (Figs. 6, 8).
- Time axes: Figs. 6/8 use reconstruction time (1 s frames); Figs. 12-15 use experiment time (model starts at t_shift = 0.796 s).
- t = 0 rows in Figs. 6/8: paper sets s = H = 0 where scaled absorption < 0.2 (no fit attempted), so err = 0 there.

## Caveats
- Fig. 8's "-H" (sigmoid-fit water level, reaching ~9.8 mm ~ 1.0 bed depths) is NOT the same quantity/analysis as Fig. 14's H (5-vertical-line mean, saturating ~6.5 mm < H0 = 7.8 mm). Do not mix the two series.
- Similarly Fig. 6 s(t) (whole-bed fit) and Fig. 12 s-data (5-line mean) differ by roughly 1 s of apparent onset and in early values; both are provided as printed.
- Digitization precision: ~1 px, i.e. about +/-0.03 mm and +/-0.02 s for Figs. 12-14 data; about +/-0.03 in dimensionless z (+/-0.3 mm) for Figs. 6/8.
- Calibration anchors were the printed tick marks/labels and the z=0 axis line; all calibrations were verified by overlaying the reproduced model curves on the rasterized pages.

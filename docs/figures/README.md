# Paper-B figures

Rendered by `puckworks/figures.py` from committed harness/gate/data outputs —
**every number is pulled from a function, none hand-typed**, so the figures track
the corrected, downgraded findings (model-capacity not identification; weak peak;
instability scoped to the tested config).

## Regenerate
```
pip install -e ".[figures]"          # optional matplotlib extra
python -m puckworks.figures          # writes fig{1..5}_*.png here
```
`import puckworks.figures` works without matplotlib (imported lazily inside the
render functions, per the CLAUDE.md optional-dependency rule); rendering needs the
`[figures]` extra.

## The figures
- **fig1_result1_tds_ey** — Result 1. (a) measured TDS-EY vs dial (monotone raw
  cells) + schmieder's own RSM EY curve (weak interior vertex 1.75, adj-R² 0.64,
  **shape only** — the printed RSM coefficients are rounded, so a refit is used for the curve; the earlier "overpredicts ~1.7×" was a rounding artifact); (b) the
  channeling model's ensemble EY on its *own* (non-portable) dial axis — generates
  an interior max, but fragile (40% of the σ-closure grid) and weak.
  → *model capacity, not identification.*
- **fig2_evidence_matrix** — mechanism evidence matrix (implemented / observable
  matched / params constrained / generates interior max / evidence strength).
  Qualitative; deliberately **not** a winner scoreboard.
- **fig3_kappa_t_ladder** — Result 2, ONE window (15–95 s). (a) Foster
  machine-only flow-minimum null (post-fit); (b) 9-bar ladder RMSE — three
  DISTINCT constant nulls (best-in-window 0.573, long-run 0.641, static κ(P) 0.648)
  vs Φ(t) 0.116 (0 params, ~4.9× better) vs a 4-param flexible cubic 0.096: time
  variation is NEEDED, not a specific bed mechanism; (c) within-campaign
  conditional-transfer RMSE — regime-dependent, no single mechanism lowest
  everywhere (NOT independent out-of-sample validation).
- **fig4_composition_diagnostic** — the registered shared-porosity composition:
  extraction-only reduces to the poroelastic rung (0.116); adding the imported
  (pre-parameterized) swelling branch flattens Q (residual > the best-constant null
  over 15–95 s) — a diagnosed mis-scale, **a FAILED composite**, not a success.
- **fig5_concentration_floortest** — Result 3 (exploratory finite-time
  concentration, NOT a stability theorem; filename deliberately not "stability").
  (a) N_eff vs the homogenization parameter, flow vs pressure control, at FIXED
  grind gs=1.1 — strong concentration is the flow-control + zero-homogenization
  corner only; (b) the CLOSED-FORM conductance-ratio gain M_f/M₀ vs the numerical
  floor: poroelastic scales ∝1/floor (floor-controlled → NOT an eigenvalue),
  Kozeny-Carman floor-independent (~1.5) — annotated with the MEASURED numerical
  N_eff, which (re-run at every floor) IS floor-independent (poro→1.0, CK≈83). Use
  N_eff, not the gain magnitude. *(The earlier "A≈10¹², linearly unstable" was
  retracted; floor-independence of the concentration is now tested, not asserted.)*

**Status:** manuscript-DRAFT figures. They are the honest current state; captions
still belong in the manuscript (LaTeX), and the underlying analyses carry the
validation-strength tags in `docs/PAPER_OUTLINE.md` / `docs/ANALYSIS_P2.md`.

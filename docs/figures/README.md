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
- **fig3_kappa_t_ladder** — Result 2. (a) Foster machine-only flow-minimum null
  (post-fit); (b) 9-bar ladder RMSE (Φ(t) beats the flat floor 5.4×, sufficient
  not unique); (c) cross-pressure OOS RMSE — regime-dependent, no universal winner.
- **fig4_composition_diagnostic** — the registered shared-porosity composition:
  extraction-only reduces to the poroelastic rung (0.116); adding the
  parameter-free swelling branch flattens Q (residual 0.648 > 0.603 flat null) —
  a diagnosed mis-scale, **a FAILED composite**, not a success.
- **fig5_stability_map** — Result 3 (exploratory). (a) N_eff vs lateral coupling,
  flow vs pressure control — the single-channel latch is the flow-control +
  zero-lateral corner only; (b) the closed-form linear amplification
  A = M(φ_max)/M(φ₀): poroelastic ~10¹² (unstable) vs Kozeny-Carman 1.5 (stable).

**Status:** manuscript-DRAFT figures. They are the honest current state; captions
still belong in the manuscript (LaTeX), and the underlying analyses carry the
validation-strength tags in `docs/PAPER_OUTLINE.md` / `docs/ANALYSIS_P2.md`.

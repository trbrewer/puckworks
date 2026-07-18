# Cross-dataset transfer of a multi-solute espresso extraction model: an inventory–kinetics identifiability limit

*Analysis writeup (paper-track). Every number reproduces from
`python -m puckworks.validation.slow.angeloni_bracket` and its functions, and is a field in the
committed result bundle `docs/figures/paper_a/results.json`. Validation-strength tags follow
ROADMAP §0 and are load-bearing. The detailed current authority is the corrected manuscript
[`docs/PAPER_A_DRAFT.md`](PAPER_A_DRAFT.md); this note is a concise current summary and does not
reproduce every Paper A table.*

## Summary (matched-endpoint result)

We tested whether a multi-solute espresso extraction model (`pannusch2024`, Schmieder-calibrated)
transfers to an independent campaign (`angeloni2023`). The model has two adjustable knobs — a
per-species solid **inventory** `c_s0` (which enters the whole-cup concentration linearly, as a pure
level) and a Sherwood mass-transfer **rate** scale — fitted to whole-cup concentrations.

Two findings, kept distinct:

1. **Practical non-identifiability at the endpoint.** Fitting inventory and rate to a whole-cup
   endpoint leaves them practically non-identifiable, because the objective has a flat valley along
   `c_s0 · φ(rate) = const`. On the caffeine log-parameter objective the SSE-Hessian **condition
   number is ≈ 1,930** and the local **inverse-curvature coupling is ≈ −0.99** — this is
   objective-surface geometry, **not** a statistical parameter correlation. The 10%-near-optimal
   profiled-SSE rate set covers **≈ 76%** of the tested log-rate grid and is **right-censored** at the
   upper tested boundary; the MAPE and SSE tolerance sets overlap with **Jaccard ≈ 0.86**.
   (Trigonelline mirrors this: condition number ≈ 3,600 — a tighter but still ill-conditioned valley.)
   An "the caffeine gap is inventory, the trigonelline gap is kinetics" decomposition is an artifact of
   where a fit lands on the valley floor.

2. **Endpoint prediction is reasonably stable, but adds little skill over a null.** Across held-out
   grinds (matched to the target beverage mass) the mechanistic model's pooled held-out **MAPE is
   8.2%** versus **8.6%** for an O-trained **level-only constant** baseline, and the mechanistic model
   is **worse than the constant on 50 of 108** held-out points (skill vs const ≈ 0.04). A shared
   multi-grind joint fit is pooled ≈ 6.4% vs ≈ 4.9% per-grind (cost of sharing ≈ 1.5 pp); leave-one-
   condition-out is pooled ≈ 6.5%.

**Superseded reading.** An earlier version of this note reported a large-error, non-transferring result
across grind, based on an **unmatched fixed-25 s integration window**. That reading was an artifact and
is retired; the corrected analysis matches cups to the target beverage mass (B1), uses an exact
weighted-median MAPE level (B3), a wider log-spaced rate domain (B6), and a sampled-fraction-aggregate
positive-control endpoint (B2).

**Interpretation.** Identifiability, endpoint prediction, and incremental mechanistic skill are three
distinct things. The parameters are individually non-identifiable from endpoint data; the level+rate
pair predicts the endpoint across grind about as well as simply carrying the fitted concentration
level; so endpoint accuracy is **not** evidence that the kinetic mechanism transferred. Comparing
against the level-only null is essential — a modest held-out MAPE alone would overstate the mechanistic
claim.

## What retains the information the cup discards

- **Timed fractions.** The positive control shows that fraction-resolved objectives keep a sharper rate
  optimum than the collapsed whole cup (`identifiability_fractions_vs_cup` →
  `positive_control.per_solute.*`). Fraction agreement here is **in-sample verification** on the
  model's own calibration data, not independent validation. An exact-integral cup simulation confirms a
  true cup (not just the sampled aggregate) loses the rate information (`full_cup_sim`).
- **Independent inventory.** Supplying an independently measured soluble inventory collapses the valley
  to a conditional rate range (`table7_rate_constraint` → caffeine implied rate ≈ 0.95, band
  ≈ [0.60, 1.75] at inventory ≈ 12.5 g/L; the intersection is interior to the tested grid).

This is the constructive counterpart of the negative identifiability result, and it resolves gap **G6**
(multi-class inventory ↔ kinetics): the two are separable only with time-resolved data or an
independent inventory measurement.

## Reproduction

All numbers reproduce from `puckworks/validation/slow/angeloni_bracket.py`:

- `identifiability_panel()` → `panel_caffeine.*` / `panel_trigonelline.*` (condition number, inverse-
  curvature coupling, profiled SSE/MAPE, 10% tolerance set + right-censoring, SSE↔MAPE Jaccard, 2-D
  surface);
- `transfer_skill_vs_baselines()` → `transfer_skill.*` (held-out mechanistic vs level-only-constant
  MAPE, worse-count, skill);
- `validate_refit_granulometry()`, `joint_multigrind_fit()`, `loco_cv_refit()`,
  `refit_pannusch_angeloni()`, `table7_rate_constraint()`, `flow_map_refinement()`;
- `identifiability_fractions_vs_cup()` (positive control).

Data: `puckworks.data.angeloni_{bioactives,total_solids,inventories}` (manifest rows carry the
`p → flow` mapping caveat). Strength tags: bracket = independent (wide envelope); per-condition / refit
= post-fit reconstruction, single grind; the endpoint identifiability limit is the core result. The
committed bundle `docs/figures/paper_a/results.json` (`schema_version` 2) carries these under the keys
above; `python -m puckworks.paper_a.build verify` binds the manuscript numbers to that bundle.

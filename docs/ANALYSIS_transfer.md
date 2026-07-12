# Cross-dataset transfer of a multi-solute espresso extraction model: an inventory–kinetics identifiability limit

*Analysis writeup (paper-track). Every number reproduces from
`python -m puckworks.validation.slow.angeloni_bracket` and its functions;
validation-strength tags follow ROADMAP §0 and are load-bearing.*

## Summary

We tested whether a multi-solute espresso extraction model calibrated on one
dataset transfers to an independent one, and found a **parameter-identifiability
limit** that is easy to mistake for a successful transfer. Fitting the model's
two adjustable knobs — a per-species solid **inventory** `c_s0` and a Sherwood
mass-transfer **rate** scale — to whole-cup concentrations at a single grind
gives an excellent held-out error (~7 %). But the fit is **degenerate**: over a
6× range of the rate scale the error is essentially flat (16.2–18.8 %) while the
inventory silently compensates, so the two are not separately identifiable from
single-grind, whole-cup data. The apparent "the caffeine gap is inventory, the
trigonelline gap is kinetics" decomposition is an artifact of where one lands on
this flat valley, and the calibration **does not transfer across grind**
(held-out coarse/fine error 25–49 %). The result is a cautionary methodological
point for cross-dataset extraction-model validation.

## 1. Setup

- **Model.** `pannusch2024` — a two-grain (fine/coarse), multi-solute 1-D
  extraction PDE. Per solute it carries a solid inventory `c_s0`, a van't Hoff
  partition `K(T)`, and a Sherwood mass-transfer correlation
  `Sh = A·Re^B·Sc^(1/3)`. Calibrated (post-fit) to the Schmieder multi-solute
  fraction kinetics. Verified property used throughout: the whole-cup
  concentration is **exactly linear in `c_s0`** (the normalization constant
  `cl1` cancels), so inventory acts as a pure level.
- **Target data.** `angeloni2023` — an **independent** campaign (66 shots,
  Arabica + Robusta, a 3×3×3 T×p×granulometry grid + off-grid points), on a
  different machine, coffee, and basket. Measured beverage concentrations
  (g/L) for caffeine (CF), trigonelline (TR), 5-CQA, plus total solids; and,
  separately, the roast-and-ground solid inventory per species (their Table 7).
- **Matching.** angeloni reports pressure, the model consumes flow. We map
  `p → flow` from the study's own hydraulics: `q = (40 g / τ_gran)·k_r(p)/k_r(9)`
  using their fitted per-granulometry conductivity `k_r(p)` and shot times
  `τ_{O,C,F} = 20/13/35 s`, with a `μ(T)` temperature correction. This is an
  assumption, not fitted (see §5).

## 2. An apparent success

Three successively stricter tests, on granulometry O (≈ the model's calibrated
grind):

| test | result | reading |
|---|---|---|
| pooled-envelope bracket | model brackets all 4 species | *optimistic* — the 66-shot ranges are wide |
| per-condition, blind | overall MAPE 31 % (22–50 % by species) | ≫ the envelope and ≫ angeloni's own ~9–13 % model |
| + Darcy `q~p/μ(T)` flow refinement | 26.5 % | closes ~5 pp (residence-time part) |
| + refit `c_s0`+`rate_scale` (fit 9 on-grid O, hold out 2 off-grid O) | **mean holdout 7.2 %** | *looks closed* |

The refit appeared not only to close the gap but to **explain** it: caffeine
took `rate_scale ≈ 1` (its fitted `c_s0`, 13.0/17.4, recovered the Table 7
inventory, 12.5/18.6), while trigonelline took `rate_scale ≈ 0.4` — read at the
time as "caffeine transfers kinetically and the gap was pure inventory;
trigonelline needs a genuine rate correction." Strength was labelled post-fit
(on-grid) with a weak 2-point holdout. **That reading is wrong**, for the reason
in §3.

## 3. The degeneracy (core result)

The whole-cup concentration is, to good approximation,
`C_cup ≈ c_s0 · φ(rate, flow, T)`, where `φ` is the fractional extraction. Since
`c_s0` enters linearly and `rate` enters only through `φ`, **both knobs move the
level**, and the objective has a flat valley along `c_s0 · φ = const`. Holding a
single grind and re-optimizing `c_s0` at each `rate_scale` makes this explicit
(caffeine, Arabica, granulometry O):

| rate_scale | 0.4 | 0.7 | 1.0 | 1.5 | 2.0 | 2.5 |
|---|---|---|---|---|---|---|
| best-fit c_s0 | 17.3 | 15.2 | 14.2 | 13.3 | 12.8 | **12.5** |
| MAPE (%) | 16.2 | 16.5 | 16.9 | 17.6 | 18.3 | 18.8 |

A **6.25× change in the kinetic rate is absorbed by the inventory with a <3 pp
change in error** — the rate is not identifiable from these data. Three
corollaries:

1. The "best" rate the optimizer reports sits at a shallow boundary optimum, so
   it **flips with incidental choices**: caffeine's fitted rate is 1.0 under one
   flow anchor and 0.4 under another; across grinds it is 0.4 / 0.4 / 2.5
   (O/C/F). The earlier inventory-vs-kinetics decomposition was reading noise on
   the valley floor.
2. The inventory absorbs the ambiguity too: the fitted `c_s0` that should equal
   the grind-independent Table 7 value spreads **17.8 → 20.3 → 8.8** (2.3×)
   across O/C/F.
3. The only tie-breaker is *external*: at `rate_scale = 2.5` the best-fit `c_s0`
   coincides with the independently measured Table 7 inventory (12.5). The
   beverage data alone cannot select it; the measured inventory can.

## 4. Transfer failure across granulometry

Because the single-grind fit is non-identifiable, it is also **non-transferable**.
Fitting on granulometry O and predicting the held-out coarse (C) and fine (F)
grinds — with each grind's own measured flow — gives (independent, held-out
granulometry):

| species | O-fit | held-out C | held-out F |
|---|---|---|---|
| caffeine | 17–18 % | 23–25 % | 31–38 % |
| trigonelline | 19–20 % | 29–30 % | 43–44 % |
| 5-CQA | 17–24 % | 25–26 % | 46–49 % |

versus the ~7 % same-grind holdout. Fine grind is worst — its flow departs most
from the calibration grind, and the fixed (grind-O) grain geometry mispredicts
the flow/surface-area sensitivity. A model whose sensitivity to flow is stronger
than the data's (angeloni's measured concentrations move only ~15 % across
grinds despite a >2× flow change) cannot both fit one grind and predict another
with a level-only correction.

## 5. Discussion — what is identifiable, and the lesson

**What single-grind whole-cup data identify.** Only the *product* `c_s0 · φ`
(the level). Neither the inventory nor the kinetic rate individually.

**What breaks the degeneracy.**
- *Hold the inventory to an independent measurement* (Table 7). Then `rate_scale`
  is identifiable — but here that fit is worse for trigonelline, i.e. the
  residual is then a genuine structural/kinetic mismatch, not a free knob.
- *Fit multiple grinds jointly with a shared, grind-independent `c_s0`.* This is
  the real transfer test, and it **fails** (§4): no single (inventory, rate)
  fits O, C, and F together.
- *Use time-resolved fractions, not the whole cup.* The extraction *curve*
  constrains rate (early-time slope) separately from level (asymptote); the
  endpoint alone does not. angeloni reports whole-cup only, which is why the
  degeneracy is unbreakable here.

**Lesson for cross-dataset extraction-model validation.** A single-grind,
whole-cup MAPE — even a good held-out one (7 %) — can be a **non-identifiable
curve fit masquerading as a transferred calibration**. Reporting it as evidence
that a model "transfers" is unsafe without (i) an independent inventory
constraint, (ii) a joint multi-grind fit with shared inventory, or (iii)
time-resolved data. On the strength ladder, the pannusch→angeloni refit is
**post-fit reconstruction at a single grind; it does not reach independent
validation and does not transfer across grind.**

**Standing position.** `pannusch2024` remains a Schmieder-calibrated runtime;
`angeloni2023` is an independent transfer *target* it does not meet across grind.
The two stay model-vs-data (ONBOARDING §6), and the earlier §7.1 "gap closed /
inventory-vs-kinetic" entry is corrected by the later "negative validation"
entry.

## Reproducibility

- Transfer arc: `validation/slow/angeloni_bracket.py` —
  `gate_angeloni_multispecies_bracket`, `gate_pannusch_angeloni_per_condition`,
  `flow_map_refinement`, `refit_pannusch_angeloni`,
  `validate_refit_granulometry`.
- Data: `puckworks.data.angeloni_{bioactives,total_solids,inventories}`
  (manifest rows carry the p→flow caveat).
- Strength tags: bracket = independent (wide envelope); per-condition/refit =
  post-fit, single grind; granulometry validation = negative (held-out grind).

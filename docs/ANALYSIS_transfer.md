# Cross-dataset transfer of a multi-solute espresso extraction model: an inventory–kinetics identifiability limit

*Analysis writeup (paper-track). Every number reproduces from
`python -m puckworks.validation.slow.angeloni_bracket` and its functions;
validation-strength tags follow ROADMAP §0 and are load-bearing.*

> **⚠ Under revision (`docs/PAPER_A_DRAFT_detailed_review.md` adopted).** The
> analysis code now uses a **matched 40 g cup** endpoint (was fixed 25 s, B1), an
> **exact weighted-median** MAPE level (was a grid, B3), and a **wider log-spaced
> rate domain** (B6); the positive-control endpoint is a **sampled-fraction
> aggregate**, not a whole cup (B2). Numeric values below (the §3 valley, §4
> transfer, §6 ratios) are being **regenerated at the matched endpoint** and are
> provisional until this banner is removed. See `PAPER_A_DRAFT.md` for the
> in-progress corrected manuscript.

## Summary

We tested whether a multi-solute espresso extraction model calibrated on one
dataset transfers to an independent one, and found a **parameter-identifiability
limit** that is easy to mistake for a successful transfer. Fitting the model's
two adjustable knobs — a per-species solid **inventory** `c_s0` and a Sherwood
mass-transfer **rate** scale — to whole-cup concentrations at a single grind
gives an excellent held-out error (~7 %). But the fit is **degenerate**: over a
6× range of the rate scale the error is essentially flat while the inventory
silently compensates, so the two are not separately identifiable from single-grind
endpoint data (matched-mass log-Hessian condition number ~10³, correlation ~−1). The
apparent "the caffeine gap is inventory, the trigonelline gap is kinetics"
decomposition is an artifact of where one lands on this flat valley. **However — and
correcting an earlier version of this note — the calibration DOES transfer across
grind once cups are matched to the target beverage mass** (held-out coarse/fine
~3–18 %; a shared joint fit is pooled ~6 % vs ~5 % per-grind). The earlier "25–49 %,
does not transfer" reading was an artifact of an unmatched fixed-25 s integration
window. So **identifiability and predictive transfer diverge here**: the parameters
are individually non-identifiable, yet the level+rate pair predicts across grind —
the cautionary methodological point is that endpoint accuracy, identification, and
transfer are distinct, and matching the beverage endpoint is a prerequisite. *(§3–§4
below retain the pre-correction numbers pending a full rewrite; the corrected
manuscript is `PAPER_A_DRAFT.md`.)*

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
| best-fit c_s0 | 15.9 | 14.0 | 13.0 | 12.1 | 11.6 | 11.3 |
| MAPE (%) | 15.5 | 15.2 | 15.1 | 15.2 | 15.4 | 15.7 |

*(Table refreshed 2026-07-12 from the current `refit_pannusch_angeloni` /
`_flow_darcy` path; an earlier printing of this table used the superseded flow
anchor and read 16.2–18.8 %. The degeneracy is if anything **stronger** now — the
valley is flatter.)*

A **6.25× change in the kinetic rate is absorbed by the inventory with a <1 pp
change in error** (MAPE 15.1–15.7 %) — the rate is not identifiable from these
data. A formal panel (`identifiability_panel`) confirms it: on the caffeine
whole-cup objective the relative-Hessian **condition number is ≈419**, the
rate↔inventory **correlation is −0.96** (the sloppy eigenvector lies along the
`c_s0·φ=const` valley), and the **profile SSE stays within 10 % of the minimum
across the whole rate sweep** — the data place no bound on the rate. Three
corollaries:

1. The "best" rate the optimizer reports sits at a shallow boundary optimum, so
   it **flips with incidental choices**: caffeine's fitted rate is 1.0 under one
   flow anchor and 0.4 under another; across grinds it is 0.4 / 0.4 / 2.5
   (O/C/F). The earlier inventory-vs-kinetics decomposition was reading noise on
   the valley floor.
2. The inventory absorbs the ambiguity too: the fitted `c_s0` that should equal
   the grind-independent Table 7 value spreads **17.8 → 20.3 → 8.8** (2.3×)
   across O/C/F.
3. The only tie-breaker is *external*: the best-fit `c_s0` passes through the
   independently measured Table 7 inventory along the valley (caffeine fitted 13.0
   near the measured 12.5; Robusta 17.4 near 18.6), but the beverage data alone
   cannot single out the rate at which it does. The measured inventory can.

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
  the real transfer test, and it **fails** (`joint_multigrind_fit`): a single shared
  (inventory, rate) fitted jointly to O+C+F gives **~30 % pooled MAPE vs ~20 %** for
  the per-grind fits (cost-of-sharing ~6–13 pp/species; every solute driven to the
  rate boundary), with the residual concentrated on the coarse and fine (extreme)
  grinds — no single (inventory, rate) fits O, C, and F together.
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

## 6. Positive control — fractions resolve what the cup hides

The claim in §5 (the rate is identifiable from the extraction *curve* but not its
endpoint) is directly testable on the **same model** and the **same data pannusch
was fit to** — the Schmieder fraction kinetics (15 shots, 6 timed fractions each).
For each solute we sweep the rate scale and, at each rate, re-optimize a single
global level so the rate can only change the *shape*; then we score two ways —
against the fraction curve, and against the very same shots **collapsed to one
whole-cup value**. The identifiability ratio (max-edge MAPE / min MAPE) measures
how sharp the trough is:

| solute | fraction-scored (temporal) | whole-cup-scored (collapsed) |
|---|---|---|
| caffeine | min 6.1 % @ rate 0.8; **edge/min 4.0×** | min 2.8 %; edge/min 1.33× |
| trigonelline | min 10.0 % @ rate 0.8; **edge/min 4.4×** | min 3.8 %; edge/min 1.22× |
| 5-CQA | min 7.1 % @ rate 1.0; **edge/min 4.3×** | min 4.3 %; edge/min 1.19× |

Scoring against the **fractions** produces a sharp trough with its minimum near
rate = 1 (as it must — pannusch was calibrated here), rising 4× to the edges of a
16× rate sweep: **the rate is identified.** Collapsing the identical shots to a
single cup value flattens the objective to a ±20 % drift with no real minimum
(edge/min ≈ 1.2–1.3): **the rate is not identified** — the same degeneracy as the
angeloni whole-cup transfer (§3), now reproduced on pannusch's own fit data. The
kinetic information is in the temporal shape, and the whole cup integrates it
away. This is the positive counterpart that makes the negative result actionable,
and it resolves gap **G6** (multi-class inventory ↔ kinetics): the two are
separable only with time-resolved data.

Strength: verification (positive control on the model's own calibration data).

*Correction (review B2): the "whole cup" scored above is a **sampled-fraction
aggregate** (the repo has only 6 fraction windows), which differs ~28–38% from the
actual BR-1/3 cup, so part of its flatness could be a sampling artefact. An
exact-integral **simulation** (`full_cup_simulation_identifiability`) removes that
artefact: the fine fraction curve identifies the calibrated rate sharply (range
ratio ~10–19×), while the EXACT whole-cup integral stays flat (~1.3–2.0×) — so a
true cup, not just the aggregate, loses the rate. An empirical actual-cup comparison
is still owed (data-blocked on the missing windows / ambiguous cup endpoint).*

## Reproducibility

- Transfer arc: `validation/slow/angeloni_bracket.py` —
  `gate_angeloni_multispecies_bracket`, `gate_pannusch_angeloni_per_condition`,
  `flow_map_refinement`, `refit_pannusch_angeloni`,
  `validate_refit_granulometry`, `joint_multigrind_fit`, `identifiability_panel`.
- Data: `puckworks.data.angeloni_{bioactives,total_solids,inventories}`
  (manifest rows carry the p→flow caveat).
- Strength tags: bracket = independent (wide envelope); per-condition/refit =
  post-fit, single grind; granulometry validation = negative (held-out grind).

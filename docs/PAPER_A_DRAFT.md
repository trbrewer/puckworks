# Paper A — draft prose (rev. 2026-07-12)

*Manuscript draft, converted from `docs/ANALYSIS_transfer.md` (the analysis of
record; this file is the manuscript layer, that file stays the analysis spec).
**Verb discipline (load-bearing, same as Paper B):** "shows/predicts" only for
independent evidence; "reconstructs / is consistent with" for post-fit;
"verifies" for a positive control on a model's own fit data; never
"identifies / proves / transfers" unless the evidence tier supports it. Every
number regenerates from `puckworks.validation.slow.angeloni_bracket` and
`puckworks.validation.slow.identifiability` (see Reproducibility). Validation
strength labels (ROADMAP §0) ride along unchanged and control the verbs.*

**Title.** The cup hides the clock: an inventory–kinetics identifiability limit in
cross-dataset espresso extraction modelling.

---

## Abstract

A recurring claim in coffee-extraction modelling is that a model calibrated on one
dataset "transfers" to another when it reproduces the second dataset's whole-cup
concentrations. We test that claim directly and find a **parameter-identifiability
limit** that is easily mistaken for a successful transfer. Using a multi-solute,
two-grain extraction PDE (`pannusch2024`) calibrated on time-resolved Schmieder
fraction kinetics, we predict an independent 66-shot campaign (`angeloni2023`;
different machine, coffee, and basket). Fitting the model's two adjustable knobs —
a per-species solid **inventory** and a Sherwood mass-transfer **rate** scale — to
whole-cup concentrations at a single grind gives an excellent held-out error
(~7 %). But the fit is **degenerate**: over a 6.25× range of the rate scale the
error is essentially flat while the inventory silently compensates, so the two are
not separately identifiable from single-grind whole-cup data. The apparent
"the caffeine gap is inventory, the trigonelline gap is kinetics" decomposition is
an artefact of where the optimiser lands on this flat valley — the fitted rate
flips with incidental choices, and the fitted inventory that should equal the
independently measured value instead spreads 2.3× across grinds. Consistent with
non-identifiability, the single-grind calibration **does not transfer across
grind** (held-out coarse/fine error 25–49 % vs the ~7 % same-grind holdout).
Finally, as a positive control on the model's own calibration data, we show the
missing information is recoverable: scoring the rate sweep against the *fraction
curves* produces a sharp identifiability trough (edge/min ≈ 4×) near the calibrated
rate, whereas collapsing the identical shots to a whole-cup value flattens it
(edge/min ≈ 1.2–1.3×). The kinetic rate lives in the temporal shape, and the whole
cup integrates it away. The methodological consequence is concrete: a single-grind,
whole-cup MAPE — even a good held-out one — is not evidence that an extraction
model transfers, without an independent inventory constraint, a joint multi-grind
fit, or time-resolved data.

---

## 1. Introduction

Espresso extraction models are increasingly used to predict beverage composition
from process settings, and a natural way to build confidence in a model is to show
it reproduces a dataset it was not fitted to. In practice this cross-dataset check
is almost always performed on **whole-cup** quantities — total dissolved solids, or
a per-species beverage concentration integrated over the shot — because those are
what most campaigns report. A good held-out whole-cup error is then read as
evidence that the model has captured the underlying extraction physics and will
generalise.

This paper argues that reading is unsafe, and shows why with a concrete worked
case. Extraction models of the Moroney–Cameron lineage carry (at least) two
adjustable degrees of freedom that both act as a *level* on the beverage
concentration: the amount of extractable material initially present (the
**inventory**), and the rate at which it is released (the **kinetic rate**). When
only the endpoint of the extraction is observed, these two knobs are confounded —
a faster rate and a smaller inventory can produce the same cup as a slower rate and
a larger inventory. A single-grind whole-cup fit therefore constrains only their
product, and an optimiser that reports a specific (inventory, rate) pair is
reporting a point on a flat valley, not an identified mechanism.

We make this quantitative on a real transfer attempt (§3–§5) and then close the
loop with a positive control that recovers the lost information from time-resolved
data (§6). The contribution is methodological: a matched-observable, held-out
protocol that distinguishes a *transferred calibration* from a *non-identifiable
curve fit masquerading as one*, and a demonstration that the distinction is
decided by whether the observable preserves the extraction's temporal shape.

---

## 2. Methods

### 2.1 Model

`pannusch2024` is a two-grain (fine/coarse), multi-solute one-dimensional
extraction PDE (Pannusch et al., *J. Food Eng.* **367**, 111887, 2024), extending
the Moroney et al. (2016, 2019) double-porosity reduction with per-species
constitutive relations. For each solute it carries a solid **inventory** `c_s0`, a
van't Hoff equilibrium partition `K(T)`, and a Sherwood mass-transfer correlation
`Sh = A·Re^B·Sc^(1/3)`. It was calibrated (post-fit) to the Schmieder multi-solute
fraction kinetics. A load-bearing structural property, used throughout, is that the
whole-cup concentration is **exactly linear in `c_s0`** — the normalisation
constant `cl1` cancels in the normalised solver — so the inventory acts as a pure
level. This makes the best-fit inventory at any fixed rate available analytically
(a rescale), which is what lets us map the objective valley exactly rather than by
noisy re-optimisation.

### 2.2 Data

- **Calibration (time-resolved).** The Schmieder 2023 extraction-kinetics DoE
  (*Foods* **12**, 2871, 2023; CC BY): 15 shots × 6 timed fractions per shot, per
  solute — the dataset `pannusch2024` was fitted to. Used here only as the positive
  control (§6), on the model's own fit data.
- **Transfer target (independent, whole-cup).** Angeloni et al. 2023 (*Appl. Sci.*
  **13**, 2688): a 66-shot campaign (Arabica + Robusta) on a different machine,
  coffee, and basket, across a 3×3×3 temperature × pressure × granulometry grid
  plus off-grid points. It reports measured beverage concentrations (g/L) for
  caffeine (CF), trigonelline (TR), 5-CQA, and total solids, and — separately — the
  roast-and-ground **solid inventory per species** (their Table 7), which we use
  only as the external tie-breaker in §4. Angeloni's own coupled FeFlow solver is
  out of scope (the card marks it skip); we consume only its chemical campaign.

### 2.3 Pressure → flow map (an assumption, not a fit)

Angeloni report pressure; the model consumes flow. We map `p → flow` from the
study's *own* hydraulics, not by fitting to its concentrations. The refined map is
Darcy-consistent, `q = q_ref · (p/p_ref) · (μ(T_ref)/μ(T))`, anchored to a single
physical espresso point (40 g / ~24 s at 9 bar, 93.4 °C) with `μ(T)` from the
registered water-viscosity closure. A cruder linear-shot-time baseline is retained
for the sensitivity in §3. The per-granulometry transfer test (§5) instead uses
angeloni's own fitted per-granulometry hydraulic conductivity `k_r(p)` and shot
times `τ_{O,C,F} = 20/13/35 s`. All three are **assumptions**, labelled as such;
none is fitted to the target concentrations.

### 2.4 Fitting and evaluation protocol

The transfer refit adjusts two knobs per solute per variety: `c_s0` (inventory
level, obtained analytically) and `rate_scale` (a multiplier on the Sherwood
prefactors A1, A2; the van't Hoff and Reynolds-exponent *structure* is held). We
fit on the 9 on-grid granulometry-O points and evaluate on the 2 held-out off-grid
O points; the cross-granulometry test (§5) fits on O and predicts held-out C and F.
No post-hoc relabelling of a refit as a prediction is permitted: a held-out score
is reported only for data untouched by the fit.

### 2.5 Identifiability metric

For the positive control (§6), we sweep `rate_scale` and, at each rate,
re-optimise a *single global level* so the rate can only change the extraction
*shape*, not its magnitude. We then score two ways on the identical shots — against
the six-fraction curve (temporal shape retained) and against the same shots
collapsed to one volume-weighted whole-cup value (shape integrated away) — and
report the **identifiability ratio** = (max-edge MAPE)/(min MAPE). A sharp trough
(ratio ≫ 1) means the rate is identified; a flat valley (ratio ≈ 1) means it is
not.

### 2.6 Validation-strength vocabulary (ROADMAP §0)

*Independent* — held-out data on a genuinely different system. *Post-fit
reconstruction* — a model evaluated on data used to fit or calibrate it.
*Verification* — reproducing a known result or a positive control on a model's own
fit data. *Negative validation* — a held-out test the model fails. These labels are
attached to every result below and are not upgraded.

---

## 3. Result 1 — an apparent success, and a flow-map sensitivity

We ran three successively stricter tests on granulometry O (≈ the model's
calibrated grind):

| test | result | reading | strength |
|---|---|---|---|
| pooled-envelope bracket | model brackets all 4 species | *optimistic* — the 66-shot ranges are wide | independent (wide envelope) |
| per-condition, blind | overall MAPE **31 %** (22–50 % by species) | ≫ the envelope and ≫ angeloni's own ~9–13 % model | independent, per-condition |
| + Darcy `q~p/μ(T)` flow refinement | **26.5 %** | closes ≈5 pp (the residence-time part) | independent, per-condition |
| + refit `c_s0` + `rate_scale` (fit 9 on-grid, hold out 2 off-grid) | **mean holdout ≈7 %** | *looks closed* | post-fit (single grind); weak 2-pt holdout |

The refit appeared not only to close the gap but to **explain** it: caffeine took
`rate_scale ≈ 1` (its fitted `c_s0` recovering the Table 7 inventory), while
trigonelline took `rate_scale ≈ 0.4` — read at the time as "caffeine transfers
kinetically and its gap was pure inventory; trigonelline needs a genuine rate
correction." We labelled that reading post-fit (on-grid) with a weak 2-point
holdout. **It is wrong**, for the reason in §4.

The flow-map refinement is a genuine but partial improvement: the cruder map
over-attributed flow to high pressure, and fixing the residence-time term closes
about 5 percentage points. The residual (~26 %) is *not* a flow error — it is
cross-coffee inventory + per-species kinetic mismatch, which no flow map can close,
and which the refit then absorbs.

## 4. Result 2 — the degeneracy (core result)

The whole-cup concentration is, to good approximation, `C_cup ≈ c_s0 · φ(rate, flow,
T)` with `φ` the fractional extraction. Because `c_s0` enters linearly and the rate
enters only through `φ`, **both knobs move the level**, and the objective has a
flat valley along `c_s0 · φ = const`. Holding a single grind and re-optimising
`c_s0` at each rate makes this explicit (caffeine, Arabica, granulometry O):

| rate_scale | 0.4 | 0.7 | 1.0 | 1.5 | 2.0 | 2.5 |
|---|---|---|---|---|---|---|
| best-fit `c_s0` | 15.9 | 14.0 | 13.0 | 12.1 | 11.6 | 11.3 |
| MAPE (%) | 15.5 | 15.2 | 15.1 | 15.2 | 15.4 | **15.7** |

A **6.25× change in the kinetic rate is absorbed by the inventory with a <1-pp
change in error** (MAPE 15.1–15.7 % across the sweep) — the rate is not identifiable
from these data. Three corollaries follow:

1. **The "best" rate is a shallow boundary optimum, so it flips with incidental
   choices.** Caffeine's fitted rate is 1.0 under one flow anchor and 0.4 under
   another; across grinds it is 0.4 / 0.4 / 2.5 (O/C/F). The earlier
   inventory-vs-kinetics decomposition was reading noise on the valley floor.
2. **The inventory absorbs the ambiguity too.** The fitted `c_s0` that should equal
   the grind-independent Table 7 value instead spreads ~2.3× across O/C/F.
3. **The only tie-breaker is external.** Across the whole valley the best-fit `c_s0`
   passes through the independently measured Table 7 inventory (caffeine: fitted
   13.0 near the measured 12.5; Robusta 17.4 near 18.6), but the beverage data alone
   cannot single out the rate at which it does so. Non-identifiability is broken by
   adding information (the measured inventory), not by optimising harder.

Strength: this is a *diagnosis of the fit*, established on the transfer target and
corroborated on the model's own data in §6 — not a claim about the model's physics.

## 5. Result 3 — transfer failure across grind

Because the single-grind fit is non-identifiable, it is also **non-transferable**.
Fitting on granulometry O and predicting the held-out coarse (C) and fine (F)
grinds — each with its own measured flow — gives (independent, held-out
granulometry):

| species | O-fit | held-out C | held-out F |
|---|---|---|---|
| caffeine | 17–18 % | 23–25 % | 31–38 % |
| trigonelline | 19–20 % | 29–30 % | 43–44 % |
| 5-CQA | 17–24 % | 25–26 % | 46–49 % |

versus the ~7 % same-grind holdout. Fine grind is worst: its flow departs most from
the calibration grind, and the fixed grind-O grain geometry mispredicts the
flow/surface-area sensitivity. A model whose sensitivity to flow is stronger than
the data's — angeloni's measured concentrations move only ~15 % across grinds
despite a >2× flow change — cannot both fit one grind and predict another with a
level-only correction. Strength: **negative validation** (held-out grind).

## 6. Result 4 — positive control: fractions resolve what the cup hides

The claim in §4 (the rate is identifiable from the extraction *curve* but not its
endpoint) is directly testable on the **same model** and the **same data
`pannusch2024` was fitted to** — the Schmieder fraction kinetics. For each solute we
sweep the rate scale and, at each rate, re-optimise a single global level so the
rate can only change the *shape*; then we score against the fraction curve and
against the identical shots collapsed to a whole-cup value:

| solute | fraction-scored (temporal) | whole-cup-scored (collapsed) |
|---|---|---|
| caffeine | min 6.1 % @ rate 0.8; **edge/min 4.0×** | min 2.8 %; edge/min 1.33× |
| trigonelline | min 10.0 % @ rate 0.8; **edge/min 4.4×** | min 3.8 %; edge/min 1.22× |
| 5-CQA | min 7.1 % @ rate 1.0; **edge/min 4.3×** | min 4.3 %; edge/min 1.19× |

Scoring against the **fractions** produces a sharp trough with its minimum near
rate = 1 (as it must — `pannusch2024` was calibrated here), rising ~4× to the edges
of a 16× rate sweep: **the rate is identified.** Collapsing the identical shots to a
single cup value flattens the objective to a ±20 % drift with no real minimum
(edge/min ≈ 1.2–1.3×): **the rate is not identified** — the same degeneracy as the
angeloni whole-cup transfer (§4), now reproduced on `pannusch2024`'s own fit data.
The kinetic information is in the temporal shape, and the whole cup integrates it
away. Strength: **verification** (positive control on the model's own calibration
data). This is the positive counterpart that makes the negative result actionable,
and it resolves gap **G6** (multi-class inventory ↔ kinetics): the two are separable
only with time-resolved data.

## 7. Discussion

**What single-grind whole-cup data identify.** Only the *product* `c_s0 · φ` — the
level. Neither the inventory nor the kinetic rate individually.

**What breaks the degeneracy.** (i) Holding the inventory to an independent
measurement makes the rate identifiable — but here that fit is then *worse* for
trigonelline, i.e. the residual becomes a genuine structural/kinetic mismatch
rather than a free knob. (ii) Fitting multiple grinds jointly with a shared,
grind-independent inventory is the real transfer test, and it fails (§5): no single
(inventory, rate) fits O, C, and F together. (iii) Using time-resolved fractions
constrains rate (early-time slope) separately from level (asymptote); the endpoint
alone does not (§6). Angeloni report whole-cup only, which is why the degeneracy is
unbreakable on that dataset.

**Lesson for cross-dataset extraction-model validation.** A single-grind, whole-cup
MAPE — even a good held-out one (7 %) — can be a **non-identifiable curve fit
masquerading as a transferred calibration**. Reporting it as evidence that a model
"transfers" is unsafe without (i) an independent inventory constraint, (ii) a joint
multi-grind fit with shared inventory, or (iii) time-resolved data. On the strength
ladder, the `pannusch2024`→`angeloni2023` refit is **post-fit reconstruction at a
single grind; it does not reach independent validation and does not transfer across
grind.**

**Standing position.** `pannusch2024` remains a Schmieder-calibrated runtime;
`angeloni2023` is an independent transfer *target* it does not meet across grind.
The two stay model-vs-data. This scoping supersedes any earlier "gap closed /
inventory-vs-kinetic" reading of the same refit.

## 8. Open gaps this paper defines

- **A joint multi-grind fit with a single shared inventory**, reported with its
  residual structure rather than a forced success — the strongest single test of
  whether any (inventory, rate) pair generalises across grind. *(Owed; scoped as a
  diagnostic, not a gate.)*
- **A profile-likelihood / condition-number identifiability panel** to quantify the
  valley flatness beyond the tabulated sweep (parameter correlation, local
  curvature, bootstrap across shots).
- **Time-resolved fractions on an independent rig** — the measurement that would
  turn the §6 verification into an independent identification off `pannusch2024`'s
  own fit data.
- **A per-species inventory measurement on the calibration coffee** to close the
  external tie-breaker without borrowing angeloni's Table 7.

## 9. Related work

*Bibliographic details below are taken from the model cards on file; entries are
flagged where a detail could not be verified from the card and needs a check before
submission.*

- **Extraction-model lineage.** Moroney, Lee, O'Brien, Suijver & Marra, "Asymptotic
  analysis of the dominant mechanisms in the coffee extraction process," *SIAM J.
  Appl. Math.* **76**(6), 2196–2217 (2016), DOI 10.1137/15M1036658 — the
  double-porosity reduction (fast surface dissolution + slow kernel diffusion) that
  `pannusch2024` extends. Cameron et al., "Systematically improving espresso,"
  *Matter* **2**, 631–648 (2020), DOI 10.1016/j.matt.2019.12.019 — the espresso
  extraction/EY model used elsewhere in the registry (Paper B) and the lineage's
  best-known application.
- **The model under test.** Pannusch et al., "…representative taste components,"
  *J. Food Eng.* **367**, 111887 (2024), DOI 10.1016/j.jfoodeng.2023.111887
  (reprinted as Article 3 of the Pannusch TU Munich dissertation, 2024).
- **The transfer target.** Angeloni, Giacomini, Maponi, Perticarini, Vittori,
  Cognigni & Fioretti, "Computer Percolation Models for Espresso Coffee: State of
  the Art, Results and Future Perspectives," *Appl. Sci.* **13**, 2688 (2023), DOI
  10.3390/app13042688; and the group's numerical-scheme work, Egidi, Giacomini,
  Larsson & Perticarini, *Chaos, Solitons & Fractals* **188**, 115625 (2024), DOI
  10.1016/j.chaos.2024.115625.
- **The calibration dataset.** Schmieder, Pannusch, Vannieuwenhuyse, Briesen &
  Minceva, extraction-kinetics DoE, *Foods* **12**, 2871 (2023), DOI
  10.3390/foods12152871 (open access, CC BY).
- **To be added before submission (not on file as verified citations):** the
  broader identifiability / practical-non-identifiability methods literature
  (profile-likelihood and sloppy-model analyses) and any prior explicit treatment
  of inventory–kinetics confounding in beverage extraction. *Flagged: a systematic
  related-work search is owed; do not assert novelty of the identifiability framing
  until it is done.*

## Reproducibility

- **Transfer arc:** `puckworks/validation/slow/angeloni_bracket.py` —
  `gate_angeloni_multispecies_bracket`, `gate_pannusch_angeloni_species_bracket`,
  `gate_pannusch_angeloni_per_condition`, `flow_map_refinement`,
  `refit_pannusch_angeloni`, `validate_refit_granulometry`. Run:
  `python -m puckworks.validation.slow.angeloni_bracket`.
- **Positive control:** `puckworks/validation/slow/identifiability.py` —
  `identifiability_fractions_vs_cup`. Run:
  `python -m puckworks.validation.slow.identifiability`.
- **Data:** `puckworks.data.angeloni_{bioactives,total_solids,inventories}` and the
  Schmieder fraction loaders; manifest rows carry the p→flow caveat.
- **Strength tags:** bracket = independent (wide envelope); per-condition/refit =
  post-fit, single grind; granulometry validation = negative (held-out grind);
  positive control = verification.
- These functions are slow (PDE solves; minutes) and live in `validation/slow/`,
  **not** in CI — the analysis is a paper-track deliverable, not a quick gate.

*Change log: see ROADMAP §7.1 (2026-07-12, Paper A manuscript conversion).*

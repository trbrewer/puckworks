# Paper A — draft prose (rev. 2026-07-12)

> **⚠ MAJOR REVISION (detailed review adopted, `docs/PAPER_A_DRAFT_detailed_review.md`).**
> The review found two real observable-contract bugs and a mislabelled optimiser,
> now fixed in code and **regenerated at the matched endpoint**: a **matched 40 g
> cup** (`t_end = 40 mL / Q`) not a fixed 25 s (B1); the **exact weighted-median**
> MAPE level not a grid falsely called "analytic" (B3); a **widened, log-spaced**
> rate domain (B6); the positive-control endpoint relabelled a **sampled-fraction
> aggregate** with an audit that it differs ~28–38 % from the actual BR-1/3 cup (B2).
> **Headline outcome of the correction:** the single-grind **non-identifiability is
> confirmed and stronger** (condition number ~10³), but the earlier **"does not
> transfer across grind" claim was an endpoint artefact** — at matched mass the
> frozen calibration transfers reasonably (~3–18 %) and a shared calibration exists
> (joint pooled ~6 % vs ~5 % per-grind). The paper is rewritten around this
> (identifiability ≠ transfer). **Now also done** (post-review + handoff): the
> uncertainty/bootstrap + leave-one-condition-out CV (M4/M6), grain-geometry
> sensitivity (B5), the exact-integral full-cup simulation (B2 design #3), the six
> figures, JFE-standard terminology, the named-solute/aggregate-proxy split (M5), the
> M9 related-work section + documented-scoping-search scaffold, and an independent
> second-rig external TDS test (Waszkiewicz 2026). **Still owed / blocked (flagged,
> not fabricated):** executing the full Scopus/WoS database search (at submission,
> §9), replicate-level named-solute external data (Kuhn/Vaca Guerra requests), the
> empirical full-shot actual-cup reconstruction (repo has only 6 fraction windows),
> and the frozen reproducibility tag `paper-a-v1.0.0` (created at submission, not
> now).*

*Manuscript draft, converted from `docs/ANALYSIS_transfer.md` (the analysis of
record; this file is the manuscript layer, that file stays the analysis spec).
**[Internal — strip before submission:** the verb-discipline note, ROADMAP/G6
pointers, and change-log prose are repo-internal.] **Verb discipline (load-bearing):**
"shows/predicts" only for independent evidence; "reconstructs / is consistent with"
for post-fit; "verifies" for an in-sample positive control; never "identifies /
proves / transfers" unless the evidence tier supports it. Numbers regenerate from
`puckworks.validation.slow.angeloni_bracket` and `…identifiability` (see
Reproducibility — a single paper-build command is still owed, M10). Validation
strength labels ride along unchanged and control the verbs.*

**Title (case-study scope until the formal analysis + actual-cup comparison are
complete, review §6).** The cup can hide the clock: practical inventory–kinetics
confounding in a cross-dataset espresso extraction case study.

---

## Abstract

We examine whether a multi-solute extraction model calibrated on fraction-resolved
data (`pannusch2024`, calibrated on the Schmieder kinetics) retains a unique kinetic
interpretation when refitted to an independent endpoint dataset (`angeloni2023`; a
different machine, coffee, and basket). Profiling the model's two adjustable knobs —
a per-species solid **inventory** and a Sherwood mass-transfer **rate** scale —
against **matched-beverage-mass** cup concentrations at a single grind reveals a
strong **practical non-identifiability**: the rate is not separately estimable over
the tested domain because the inventory compensates, quantified by a log-parameter
Hessian condition number of order 10³, a rate↔inventory correlation near −1, and a
rate profile that stays within 10 % of its minimum across most of a wide rate sweep.
Crucially, we report **parameter identifiability and predictive transfer as separate
properties** — and they diverge. Although the individual parameters are not
identifiable, a calibration frozen on one grind **predicts the held-out coarse/fine
grinds reasonably** (~3–18 % error), and a single shared (inventory, rate) fitted
jointly to all grinds nearly matches the per-grind fits (cost-of-sharing ~1
percentage point): predictions are stable along the compensating manifold. This
corrects an earlier version of this analysis, which — using an **unmatched fixed-time
integration window** — reported a large cross-grind transfer failure; that failure
was mostly a measurement-window artefact. Finally, an **in-sample verification** on
the model's own calibration campaign shows fraction-resolved scoring localizes the
rate profile more sharply than an aggregated endpoint (the aggregate here is a
sampled-fraction statistic, not a full cup — it differs from the actual cup by
~30 %). The lesson is that a low endpoint error need not identify a mechanism even
when it *does* transfer: identifiability, transfer, and endpoint accuracy are
distinct properties and must be reported separately, and matching the beverage
endpoint is a prerequisite for any of them.

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
level. This makes the best-fit inventory at any fixed rate available in closed form
— for the MAPE objective it is the exact **weighted median** of the per-condition
ratios (not a plain rescale, not a grid search) — so the level axis of the objective
is solved exactly and only the **rate** is profiled over a stated (wide, log-spaced)
grid.

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

### 2.6 Evidence vocabulary (JFE-standard terms)

We keep the evidence types explicit and standard (the repo's internal labels are
kept only in a supplement): *calibration / reconstruction* — a model evaluated on
data used to fit it; *internal holdout / internal prediction* — held-out points from
the same campaign (e.g. leave-one-condition-out CV); *external prediction /
cross-dataset prediction* — a genuinely different rig/coffee; *failed external
prediction* — an external test the model does not pass; *in-sample verification /
objective localization* — reproducing a positive control on the model's own fit
data. These are attached to every result below and are not upgraded. We use
*practical identifiability* (over the tested design, domain, and objective)
throughout — never *structural* identifiability, which would need an analytic
proof — and we call the rate profiles *profiled MAPE objectives*, not *profile
likelihoods* (there is no explicit likelihood/noise model, so the tolerance bands
are stated thresholds, not confidence intervals).

---

## 3. Result 1 — an apparent success, and a flow-map sensitivity

**Observable convention (M5).** The primary headline is the macro-average over the
**three named solutes** (caffeine, trigonelline, 5-CQA). Source-specific TDS /
total-solids is treated as a separate **aggregate-solids proxy** — the Pannusch-side
TDS is a modelled caffeine-like pseudo-component, Angeloni's is a gravimetric
total-solids assay, and (§6) Waszkiewicz's is an optical-refractometer reading; these
are not an equivalent analyte, so we never pool the proxy with named molecules.

We ran three successively stricter tests on granulometry O (≈ the model's calibrated
grind), all at the **matched 40 g cup** endpoint. *[The holdout is a mean of two
off-grid O points per solute × variety — a small internal check, superseded by the
leave-one-condition-out CV of §5 (M4).]*

| test | result | reading | strength |
|---|---|---|---|
| pooled-envelope bracket | model brackets the 3 named solutes + the aggregate proxy | *optimistic* — the 66-shot ranges are wide | external (wide envelope) |
| per-condition, blind | overall MAPE **22.6 %** (incl. proxy) | > angeloni's own ~9–13 % model | external, per-condition |
| + Darcy `q~p/μ(T)` flow refinement | **22.6 %** (crude-τ 23.1) | closes only **~0.5 pp** — at matched mass the flow-map choice barely matters | external, per-condition |
| + refit `c_s0` + `rate_scale` (fit 9 on-grid, hold out 2 off-grid O) | **named-solute holdout ≈8.4 %** (aggregate-solids proxy TDS ≈11.5 %, reported separately) | a NEW angeloni calibration | reconstruction (single grind); weak 2-pt holdout |

Two things changed from our earlier draft once the endpoint was matched. First, the
blind per-condition gap dropped from ~31 % to **22.6 %** — the fixed-25 s window had
inflated it. Second, the flow-map refinement, which previously appeared to close
~5 pp, now closes only ~0.5 pp: **the residence-time "improvement" was largely an
endpoint artefact, not a flow correction.** The refit then reads a per-species rate
(caffeine ~2.2, trigonelline at the domain edge, etc.), but **that per-species
decomposition is not supported by the profile analysis** (§4): the fitted rate is a
point on a flat valley, not an identified mechanism, and it moves with the endpoint
and domain choices.

At the matched endpoint the two tested flow maps are nearly interchangeable (~0.5 pp
apart), so the residual is **not removed by the flow map**; we do *not* attribute it
uniquely to inventory + kinetics, because competing sources — grain geometry (frozen
at the centre grind), the viscosity model, the endpoint definition, and the assay —
are not separately quantified here.

## 4. Result 2 — the degeneracy (core result)

The whole-cup concentration is, to good approximation, `C_cup ≈ c_s0 · φ(rate, flow,
T)` with `φ` the fractional extraction. Because `c_s0` enters linearly and the rate
enters only through `φ`, **both knobs move the level**, and the objective has a
flat valley along `c_s0 · φ = const`. Holding a single grind and re-optimising
`c_s0` at each rate makes this explicit (caffeine, Arabica, granulometry O):

Over a wide log-spaced rate sweep the best-fit `c_s0` moves to compensate while the
error barely changes. We describe inventory and rate as **practically
non-identifiable over the tested rate domain under this single-grind endpoint
design, flow assumptions, and objective** — not as an exact theorem that all
endpoint designs identify only a product. Two robust corollaries: (i) the fitted
rate is a valley-floor value, not a converged interior estimate, so it flips with
incidental choices (flow anchor, grind, rate domain) — the earlier
inventory-vs-kinetics decomposition read the valley floor, not a mechanism; (ii) the
best-fit `c_s0` passes through the independently measured Table 7 inventory somewhere
along the valley (caffeine ~13 near the measured 12.5; Robusta ~14–17 near 18.6), but
the beverage data alone cannot single out the rate — the measured inventory is **one
available external tie-breaker**.

**A formal identifiability panel** (`identifiability_panel`) quantifies the valley on
the caffeine matched-mass objective: locate the minimum, fit a local Hessian in **log
parameters** (u = ln rate, v = ln c_s0; the standard sloppiness basis, valid on the
log-spaced grid), and profile the rate. The result is unambiguous and, at the matched
endpoint, *stronger* than before: **condition number ≈ 1930** (one stiff, one sloppy
direction; interior optimum, reliable Hessian), rate↔inventory **correlation −0.99**
(the sloppy eigenvector lies almost exactly along the `c_s0·φ = const` valley), and
the profile SSE stays within 10 % of the minimum over **~76 % of the swept rate
range** [0.4–6.5] — the data place essentially no bound on the rate. Trigonelline is
similar (condition number ≈ 3600, correlation −0.84, profile flat over ~45 % of the
range). This is practical non-identifiability over the tested domain, quantified —
robust to the matched-mass and exact-level corrections, not an artefact of a coarse
grid.

Strength: this is a *diagnosis of the fit*, established on the transfer target and
corroborated on the model's own data in §6 — not a claim about the model's physics.

## 5. Result 3 — frozen-parameter transfer across grind

*Practical non-identifiability (§4) and predictive transfer are separate questions:
a compensating manifold can leave predictions stable even when the parameters are
individually non-identifiable. **The corrected results show exactly this** — and, in
doing so, overturn a claim in our earlier draft.* We freeze the O calibration
(level+rate pair) and predict the held-out coarse (C) and fine (F) grinds at **matched
40 g cups**, each with its own measured flow:

| species | O-fit | held-out C | held-out F |
|---|---|---|---|
| caffeine | 3–5 % | 8–10 % | 5–7 % |
| trigonelline | 2–4 % | 7–8 % | 3–7 % |
| 5-CQA | 5–12 % | 10–18 % | 5–9 % |

The frozen O calibration **transfers reasonably** to the other grinds (held-out
C ~7–18 %, F ~3–9 %). This is a large improvement over our pre-correction draft,
which reported **25–49 %** held-out error and concluded the model "does not transfer
across grind." **That failure was mostly an artefact of the unmatched 25 s
endpoint** (review B1/B5): once cups are matched to the target beverage mass, the
transfer is much better. **The joint multi-grind fit confirms it:** a *single shared*
`(c_s0, rate_scale)` fitted jointly to O+C+F (`joint_multigrind_fit`) gives a mean
pooled MAPE of **~6 %, against ~5 % for the per-grind independent fits — a
cost-of-sharing of only ~1 pp**, with every rate interior to the widened domain
(none at the boundary). So, contrary to the earlier draft, **an adequate shared
cross-grind calibration does exist** at the matched endpoint.

This is the empirical payoff of separating the two questions (review M1): the
`(inventory, rate)` split is **degenerate within a grind** — the fitted rate flips
with incidental choices (§4) — **yet the level+rate *pair* predicts the other grinds
well**, because predictions are stable along the compensating manifold. Individual
non-identifiability did *not* imply predictive non-transfer. Strength: **held-out /
joint predictive transfer** (reasonable), conditioned on the tested flow maps, frozen
centre-grind geometry, and matched endpoint.

**Proper cross-validation, uncertainty, and robustness** (`loco_cv_refit`,
`geometry_sensitivity_transfer`). Replacing the weak two-off-grid-point holdout with
**leave-one-(T,p)-condition-out CV** over the nine on-grid O conditions gives a pooled
held-out MAPE of **6.5 %** (median **5.2 %**, shot-level bootstrap 95 % CI
**[5.0, 8.2] %**), reported per solute × variety (medians 2.8–8.8 %, worst individual
fold 32.7 % on Robusta 5-CQA) rather than as a single mean (review M4). The verdict is
robust to the loss function: under a log/relative-error level fit the pooled mean is
**7.0 %** (review M6). And it is robust to the frozen geometry: re-running the O→C/F
transfer under each of the three Pannusch fitted geometries (1.4/1.7/2.0, which vary
<15 %) moves the held-out MAPE by **at most 1 pp** (review B5) — so the transfer is not
a geometry artefact. A calibrated cross-grinder map remains unavailable (we sweep the
observed geometry range instead). Together these confirm the corrected §5 conclusion —
the calibration transfers across grind — with proper cross-validation, an uncertainty
interval, and loss/geometry robustness, not a two-point mean.

## 6. Result 4 — positive control: fraction scoring localizes the rate more than an aggregated endpoint

The claim in §4 (the rate constrains the extraction *curve* more than an aggregated
endpoint) is testable on the **same model** and the **same data `pannusch2024` was
fitted to** — the Schmieder fraction kinetics. For each solute we sweep the rate
scale and, at each rate, re-optimise a single global level (the exact MAPE
weighted-median) so the rate can only change the *shape*; then we score against the
fraction curve and against the identical shots collapsed to a **sampled-fraction
aggregate** — a duration-weighted mean of the six measured windows (fractions
1,2,3,5,7,10). **This aggregate is not a whole cup:** a data-only audit
(`sampled_aggregate_vs_actual_cup`) shows it differs from the actual brew-ratio-1/3
cup by **27.8 / 38.3 / 30.7 % MAPE** (caffeine / trigonelline / 5-CQA), so part of
its flatness is a sampling artefact; a full-cup comparison is owed (below).

| solute | fraction-scored (temporal) | sampled-fraction aggregate |
|---|---|---|
| caffeine | min 6.0 % @ rate 0.8; range ratio 4.1× | min 2.6 %; range ratio 1.4× |
| trigonelline | min 10.0 % @ rate 0.8; range ratio 4.4× | min 3.6 %; range ratio 1.2× |
| 5-CQA | min 7.0 % @ rate 1.0; range ratio 4.4× | min 4.1 %; range ratio 1.2× |

Scoring against the **fractions** produces a sharp trough with its minimum near
rate = 1 (consistent with calibration on these data), rising ~4× to the edges of a
16× rate sweep. Scoring the **sampled-fraction aggregate** stays flat (range ratio
≈ 1.2–1.4×, no real minimum). So **fraction-resolved scoring localizes the rate
profile more sharply than the aggregated endpoint** on this campaign. Strength:
**in-sample verification of information content** on `pannusch2024`'s own
calibration data — *not* an independent identification of the physical rate (the
model was fitted here, and its source warns the fitted parameters lack generality).
Scoped conclusion: *time-resolved data can supply the rate information missing from
an aggregated endpoint in this model and design* (other independent constraints or
multi-condition designs could also help). This speaks to gap **G6** (multi-class
inventory ↔ kinetics).

**Does a *true* whole cup also lose the rate — or was the flatness a sampling
artefact?** Because the repo has only six fraction windows (1,2,3,5,7,10; the
intermediate windows are absent), an *empirical* complete-shot reconstruction is
data-blocked and a clean actual-cup comparison is ambiguous (the BR-1/3 `mass_in_cup`
does not cleanly reconcile with the fraction shot — a data question). So we test the
claim with an **exact-integral simulation** (`full_cup_simulation_identifiability`,
review B2 design #3): for each experiment we generate synthetic truth at the
calibrated rate = 1 — a fine-grid fraction curve over the whole shot *and* the
**exact single whole-cup integral** `[0, t_end]` — add seeded relative noise, then
sweep the rate. **Result:** fraction-curve scoring recovers rate = 1 sharply — range
ratio **10–19×** across the three solutes, minimum exactly at the calibrated rate —
while scoring the **exact whole-cup integral** stays flat (range ratio **1.3–2.0×**,
minimum wandering off rate 1). The exact cup is only marginally more informative than
the crude six-window aggregate and remains essentially flat. This removes the
sampled-window artefact: a *true* whole cup, not just a sampled aggregate, loses
kinetic-rate information — so the "cup hides the clock" claim survives the review's
B2 concern. Strength: **simulation study** (exact integral, seeded 3 % noise) — not
an empirical positive control. *(Still owed: an empirical full-cup comparison, which
needs either the missing fraction windows or an unambiguous same-shot cup
observable — a data question, not a code one.)*

## 7. Discussion

**What a single-grind endpoint fit constrains here.** Over the tested domain it
constrains essentially the *product* `c_s0 · φ` (the level); neither the inventory
nor the kinetic rate is individually pinned. This is a *practical* statement about
this design and objective, not a theorem that every endpoint design identifies only
a product — sufficiently informative endpoints at different residence times, flows,
or temperatures could in principle carry rate information.

**Identifiability and transfer diverge here.** The single-grind endpoint does not
pin the rate (§4), yet the frozen level+rate pair transfers reasonably across grind
and a shared calibration exists (§5). This is the textbook distinction between
*parameter* identifiability and *predictive* transfer: predictions are stable along
the compensating manifold even though the parameters on it are not individually
estimable. What would separately *identify* the rate is different information —
holding the inventory to an independent measurement, or time-resolved fractions,
which constrain the rate via the early-time slope where an aggregated endpoint does
so weakly (§6). Angeloni report an endpoint only, which is why *this* dataset does
not, on its own, identify the two — though it transfers.

**Lesson for cross-dataset extraction-model validation.** A single-grind endpoint
MAPE — even a low held-out one, and even one that *transfers* — need not identify a
mechanism: **endpoint accuracy, parameter identification, and frozen-parameter
transfer are distinct properties and must be reported separately.** A second lesson
is procedural: **matching the beverage endpoint is a prerequisite** — an unmatched
fixed-time window manufactured a spurious cross-grind transfer failure in our earlier
draft, which the correction removed. On the strength ladder, the
`pannusch2024`→`angeloni2023` refit is **post-fit reconstruction (a new calibration
on the angeloni coffee) whose frozen predictions transfer reasonably across grind at
matched mass, but which does not, on this dataset, identify the kinetic rate.**

**Standing position.** `pannusch2024` remains a Schmieder-calibrated runtime;
`angeloni2023` is an independent target. A refit to angeloni transfers across grind
(matched mass) but is a new calibration, not evidence that the original kinetics are
identified. This scoping supersedes both the earlier "gap closed / inventory-vs-
kinetic" reading *and* the subsequent "does not transfer across grind" reading — the
first over-claimed identification, the second was an endpoint artefact.

## 8. Open gaps this paper defines

- **Held-out validation, uncertainty, and robustness** — *delivered* (§5): the joint
  multi-grind fit (`joint_multigrind_fit`, pooled ~6 % vs ~5 %); **leave-one-condition-
  out CV** (`loco_cv_refit`, pooled 6.5 %, median 5.2 %, bootstrap 95 % CI [5.0, 8.2] %)
  replacing the 2-point holdout (M4) with a bootstrap interval and a log-loss robustness
  check (M6); and a **geometry-sensitivity sweep** (`geometry_sensitivity_transfer`,
  ≤1 pp across the three fitted geometries, B5). Still owed: per-condition residual
  plots by (T, p, grind, variety, solute), and per-point measurement-uncertainty
  weighting (only total-solids carries RSD; the named-solute rows are single
  measurements).
- **A profiled-objective / condition-number identifiability panel** — *delivered*
  (§4, `identifiability_panel`): caffeine log-Hessian condition number ≈1930,
  rate↔inventory correlation −0.99, profile flat over ~76 % of a wide rate sweep.
  Still owed on top: the same panel across all solutes/varieties as a supplementary
  figure.
- **An empirical full-cup comparison** (review B2) — the exact-integral simulation
  (§6) is delivered; the empirical version is **data-blocked** (the repo has only
  fraction windows 1,2,3,5,7,10; the BR-1/3 cup mass/endpoint is ambiguous).
- **Time-resolved fractions on an independent rig** — the measurement that would
  turn the §6 verification into an independent identification off `pannusch2024`'s
  own fit data.
- **A per-species inventory measurement on the calibration coffee** to close the
  external tie-breaker without borrowing angeloni's Table 7.

## Figures

Six figures (`docs/figures/paper_a/`, rendered from the corrected matched-mass
analysis via `python -m puckworks.figures_paper_a`; every value regenerates from the
slow analysis functions, none hand-typed):

- **Fig 1** — study & evidence design: calibration → Angeloni-O fit → held-out
  leave-one-condition-out CV → frozen O→C/F transfer → Table 7 tie-breaker →
  in-sample verification, arrows colour-coded by evidence type.
- **Fig 2** — inventory–rate objective surface (caffeine, trigonelline): the flat
  valley, the profiled path, the Table 7 inventory line, and the condition number
  (§4).
- **Fig 3** — every leave-one-condition-out held-out point (observed vs predicted)
  by solute × variety — the distribution behind the pooled 6.5 % (§5, M4).
- **Fig 4** — frozen O→C/F transfer at matched 40 g cups: observed vs predicted per
  condition, grinds C and F (§5).
- **Fig 5** — joint shared-(c_s0, rate) residual by variety × solute × grind, with
  the cost-of-sharing and rate-boundary flags (§5).
- **Fig 6** — rate profiles: fraction scoring (sharp) vs the sampled aggregate and
  the exact-integral whole cup (both flat) (§6).

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
- **The model under test.** Pannusch et al., "Model-based kinetic espresso brewing
  control chart for representative taste components," *J. Food Eng.* **367**, 111887
  (2024), DOI 10.1016/j.jfoodeng.2023.111887 (reprinted as Article 3 of the Pannusch
  TU Munich dissertation, 2024).
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
  `refit_pannusch_angeloni`, `validate_refit_granulometry`, `joint_multigrind_fit`
  (the shared-inventory joint fit of §5), `identifiability_panel` (the
  Hessian/condition-number/profiled-objective quantification of §4),
  `loco_cv_refit` (leave-one-condition-out CV + bootstrap + loss sensitivity, M4/M6),
  `geometry_sensitivity_transfer` (B5). Run:
  `python -m puckworks.validation.slow.angeloni_bracket`.
- **Positive control:** `puckworks/validation/slow/identifiability.py` —
  `identifiability_fractions_vs_cup` (empirical, sampled aggregate),
  `sampled_aggregate_vs_actual_cup` (B2 audit), and
  `full_cup_simulation_identifiability` (B2 exact-integral simulation). Run:
  `python -m puckworks.validation.slow.identifiability`.
- **Data:** `puckworks.data.angeloni_{bioactives,total_solids,inventories}` and the
  Schmieder fraction loaders; manifest rows carry the p→flow caveat.
- **Strength tags:** bracket = independent (wide envelope); per-condition/refit =
  post-fit, single grind; granulometry validation = negative (held-out grind);
  positive control = verification.
- These functions are slow (PDE solves; minutes) and live in `validation/slow/`,
  **not** in CI — the analysis is a paper-track deliverable, not a quick gate.

*Change log: see ROADMAP §7.1 (2026-07-12, Paper A manuscript conversion).*

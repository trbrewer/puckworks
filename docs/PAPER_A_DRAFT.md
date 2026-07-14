# Paper A — draft prose (rev. 2026-07-12)

> **Reviewers:** please read `docs/REVIEWER_BRIEF_PAPER_A.md` first — it is a
> disclosure register of the known/scoped limitations and the maximum defensible
> claim per result, with an explicit ask (assess whether our disclosure is
> adequate; flag anything new; say if a disclosed limit undermines a claim).

*__[REPOSITORY NOTE — strip before submission.__ This is the working draft; the
manuscript body starts at the Title below. Full revision provenance (the two
observable-contract corrections adopted from `docs/PAPER_A_DETAILED_REVIEW.md` and
its predecessor, the matched-endpoint regeneration, and the P0 objective/units/
uncertainty corrections) lives in the ROADMAP §7.1 change log, not here. Verb
discipline (load-bearing, retained): "shows/predicts" only for independent evidence;
"reconstructs / is consistent with" for post-fit; "verifies" for an in-sample
positive control; "localizes" for an objective-profile result; never "identifies /
proves / transfers" unless the evidence tier supports it. Numbers regenerate from
`puckworks.figures_paper_a compute` (`angeloni_bracket`, `identifiability`,
`external_waszkiewicz`); a frozen `paper-a-v1.0.0` tag and pinned environment remain
owed at submission.]_*

**Title.** The cup can hide the clock: practical inventory–kinetics confounding in a
cross-dataset espresso extraction case study.

---

## Abstract

We examine whether a multi-solute extraction model calibrated on fraction-resolved
data (`pannusch2024`, calibrated on the Schmieder kinetics) retains a unique kinetic
interpretation when refitted to an independent endpoint dataset (`angeloni2023`; a
different machine, coffee, and basket). Profiling the model's two adjustable knobs —
a per-species solid **inventory** and a Sherwood mass-transfer **rate** scale —
against cup concentrations at a **matched beverage endpoint** (a 40 mL matched-volume
proxy for the 40 g cup) at a single grind reveals a strong **practical
non-identifiability**: the rate is not separately estimable over the tested domain
because the inventory compensates. On the SSE surface a local log-parameter Hessian is
highly ill-conditioned (condition number of order 10³, basis- and discretisation-
dependent) with an inverse-curvature coupling near −1 (a geometric diagnostic of the
SSE valley, **not** a statistical parameter correlation — no likelihood is specified);
more robustly, the profiled objective stays within 10 % of its minimum from ≈0.4 up to
the **upper tested rate boundary** (so its upper extent is **right-censored** by the
domain, not closed), and a MAPE tolerance set overlaps the SSE set.
Crucially, we report **parameter identifiability, predictive transfer, and incremental
skill over a null model as separate properties**. Although the individual parameters are
not identifiable, a calibration frozen on one grind produces held-out coarse/fine-grind
absolute errors of **~3–18 %** at the point optimum. But absolute error alone does **not**
establish mechanistic transfer skill: against an **O-trained level-only constant**
baseline (a single concentration fit to the O grind, carrying no temperature/pressure/
flow/kinetic response), the mechanistic model's pooled held-out MAPE is **8.2 %** versus
**8.6 %** for the constant — an incremental skill of only **≈4 % relative (0.36 pp absolute)**, and the
model is worse than the constant on **50 of 108 held-out points**. The kinetic/transport
structure therefore adds little beyond the transferred level; the scientifically robust
statement is that the fitted level-plus-rate pair does not catastrophically deteriorate
across grinds, not that the mechanism transfers. Propagating the **discrete 10 %-near-
optimal MAPE grid set** (rates within 10 % of the O-fit minimum on an 18-point rate grid,
a declared set — not a continuous manifold) to C/F, the worst **aggregate** held-out MAPE
rises to **~22 %**. Condition-wise ranges across this finite 18-point tolerance set **are
reported** (Fig. 4); a continuous, grid-converged profile-prediction propagation remains
future work. A single shared
(inventory, rate) fitted jointly to all grinds reconstructs the pooled data at 6.4 %
macro-MAPE vs 4.9 % for separate per-grind fits — an **in-sample** parameter-sharing
penalty (not a held-out prediction), whose adequacy must be judged against reduced-model
baselines since a per-grind constant is nearly competitive.
This corrects an earlier version of this analysis, which — using an **unmatched fixed-time
integration window** — reported a large cross-grind transfer failure; that failure
was mostly a measurement-window artefact. Finally, across an **in-sample
verification** on the model's own calibration campaign and an **independent
second-rig TDS trajectory** (Waszkiewicz et al. 2026), retaining temporal resolution
moves the rate objective more than an integrated aggregate does — though on the single
external shot the flat integrated-cup profile is **algebraic** (one scalar concentration
is matched by one profiled level at every rate), not an empirical no-information result,
and the external trajectory minimum remains shallow and high-error (~27 % MAPE). The
lesson is that a low endpoint error need not identify a mechanism, and need not even
signal mechanistic transfer skill beyond a level-only baseline: identifiability,
predictive transfer, endpoint accuracy, and incremental skill over a null model are
**distinct properties** that must be reported separately. A validation score is
interpretable only when the model output is mapped to the **same observation window and
endpoint** as the data.

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
a faster rate and a smaller inventory can produce nearly the same cup as a slower
rate and a larger inventory. Under the tested single-grind whole-cup design,
inventory and rate are therefore **practically confounded**: changes in one can be
largely compensated by changes in the other over the evaluated domain, so an
optimiser that reports a specific (inventory, rate) pair is reporting a point on a
near-flat valley rather than an identified mechanism. This is an empirical statement
about the tested model, observation map, parameterisation, operating design, and
objective — not a claim of exact product invariance; with multiple temperatures,
pressures, flows, or endpoints the compensation need not be exact.

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
  (*Foods* **12**, 2871, 2023; CC BY). The source study collected **ten** consecutive
  fractions across **15 experimental settings** (three repetitions, six at the centre
  point); the `pannusch2024` port uses a **derived six-window subset** (fractions 1, 2,
  3, 5, 7, 10) across the 15 conditions. Used here only as the positive control (§6),
  on the model's own fit data.
- **Transfer target (independent, whole-cup).** Angeloni et al. 2023 (*Appl. Sci.*
  **13**, 2688): **66 condition-level sample records** (33 per variety, each based on
  duplicate extractions in the source, which also reports analyte RSD ≈ 0.3–19.7 %; the
  repository retains reported central values, not the replicate-level uncertainty), on a
  different machine, coffee, and basket, across a 3×3×3 temperature × pressure ×
  granulometry grid
  plus off-grid points. It reports measured beverage concentrations (g/L) for
  caffeine (CF), trigonelline (TR), 5-CQA, and total solids, and — separately — the
  roast-and-ground **solid inventory per species** (their Table 7), which we use
  only as a same-campaign orthogonal-measurement constraint in §4. Angeloni's own coupled FeFlow solver is
  out of scope (the card marks it skip); we consume only its chemical campaign.

### 2.3 Pressure → flow map (an assumption, not a fit)

**Endpoint contract (review A2-09).** The Angeloni cup is a **40 ± 2 g** beverage; the
solver integrates to a *volume* endpoint `t_end = V_target / Q`. We set `V_target = 40 mL`,
i.e. we approximate 40 g as 40 mL — at a hot-beverage density ρ ≈ 0.98–1.00 g/mL this is a
≈ 0–2 % (≤ ~0.8 mL) endpoint shift, and the source's own ±2 g tolerance is a further ±5 %.
We ran the per-endpoint sensitivity sweep (38 / 40 / 42 mL) rather than assert insensitivity
(`endpoint_mass_sensitivity`). The result is a **quantified caveat, not a dismissal**: the
overall blind per-condition **named-solute** MAPE is *moderately* endpoint-sensitive — it
moves ≈ 5.0 pp (23.8 → 28.8 %) across the ±2 g window — and the finer
*trigonelline-hurts-when-inventory-matched* detail flips near the +5 % endpoint. What is
**robust** across every endpoint is the **blind discrepancy** itself (a large per-condition
residual) and the caffeine inventory-match improvement. **This sweep quantifies the blind
O-grind discrepancy only; it is not the O-refit→C/F transfer estimand** (refitting O,
transferring to C/F, and recomputing the level-only baseline at each endpoint remains
deferred — review A-18). So the qualitative conclusion (a large, structured blind residual not removed by
inventory alone) does not hinge on the 40 g ≈ 40 mL approximation, but the exact residual
magnitude and the trigonelline detail carry a ≈ 5 pp endpoint uncertainty that we state
here rather than absorb. We use "matched beverage endpoint" rather than "matched 40 g"
wherever the distinction could matter.

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
report the **profile range ratio** (edge-to-minimum objective ratio) = (max-edge
MAPE)/(min MAPE), with the edges being the tested rate-domain bounds. A sharp trough
(ratio ≫ 1) means the rate objective is **more strongly localized over the tested
domain**; a flat valley (ratio ≈ 1) means it is **weakly localized** — this is a
localization contrast over the declared domain, not an identification theorem in a
likelihood sense.

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
proof. The formal identifiability panel (§4) profiles **unweighted concentration-scale
SSE** with a least-squares nuisance level — SSE is a smooth local-curvature diagnostic,
and MAPE (the paper's predictive metric) is reported there only as a cross-check that
agrees. Because there is no explicit likelihood/noise model, the 10 % tolerance bands
are stated thresholds, not confidence intervals, and the inverse-Hessian coupling is a
geometric coupling of the SSE surface, not a statistical parameter correlation.

---

## 3. Result 1 — an apparent success, and a flow-map sensitivity

**Observable convention (M5).** The primary headline is the macro-average over the
**three named solutes** (caffeine, trigonelline, 5-CQA). Source-specific TDS /
total-solids is treated as a separate **aggregate-solids proxy** — the Pannusch-side
TDS is a modelled caffeine-like pseudo-component, Angeloni's is a gravimetric
total-solids assay, and (§6) Waszkiewicz's is an optical-refractometer reading; these
are not an equivalent analyte, so we never pool the proxy with named molecules.

We ran three successively stricter tests on granulometry O (≈ the model's calibrated
grind), all at the **matched beverage endpoint** (40 mL matched-volume proxy for the
40 g cup, ρ≈1). *[The holdout is a mean of two
off-grid O points per solute × variety — a small internal check, superseded by the
leave-one-condition-out CV of §5 (M4).]*

| test | result | reading | strength |
|---|---|---|---|
| pooled-envelope bracket | model brackets the 3 named solutes + the aggregate proxy | *optimistic* — the 66-shot ranges are wide | external (wide envelope) |
| per-condition, blind | **named-solute macro-MAPE 26.3 %** (proxy-inclusive 22.7 %, reported separately) | > angeloni's own ~9–13 % model | cross-dataset blind comparison, per-condition |
| + Darcy `q~p/μ(T)` flow refinement | **26.3 %** (crude-τ 26.8) | closes only **~0.5 pp** — at matched mass the flow-map choice barely matters | cross-dataset blind comparison, per-condition |
| + refit `c_s0` + `rate_scale` (fit 9 on-grid, hold out 2 off-grid O) | **named-solute holdout ≈8.4 %** (aggregate-solids proxy TDS ≈11.5 %, reported separately) | a NEW angeloni calibration | reconstruction (single grind); weak 2-pt holdout |

Two things changed from our earlier draft once the endpoint was matched. First, the
blind per-condition named-solute gap dropped from ~31 % to **26.3 %** — the fixed-25 s window had
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
endpoint designs identify only a product. Two robust corollaries: (i) the numerical
optimum is **interior**, but it is **weakly localized** — the near-optimal set is
right-censored at the tested upper boundary — so the fitted rate is a valley-floor
value that flips with incidental choices (flow anchor, grind, rate domain) — the earlier
inventory-vs-kinetics decomposition read the valley floor, not a mechanism; (ii) the
best-fit `c_s0` passes through the independently measured Table 7 inventory somewhere
along the valley (caffeine ~13 near the measured 12.5), but the beverage data alone
cannot single out the rate — the measured inventory is a **same-campaign
orthogonal-measurement constraint** (Table 7 measures a different quantity within the
*same* Angeloni study; it is not external to the transfer campaign). We now make this
constraint **quantitative** (`table7_rate_constraint`, review A3-13/A-16): intersecting
the profiled valley `c*(rate)` with the caffeine Table 7 value (12.54 g L⁻¹) yields a
**conditional implied rate ≈ 0.95**. An **illustrative ±10 % inventory perturbation** — an
analyst-selected sensitivity assumption, **not** a calibrated measurement-uncertainty
model — maps to rates of **≈ 0.60–1.76**. This **narrows** the beverage-only tolerance set
to a **conditional one-dimensional intersection band**, but it is **not a confidence
interval**. It is nonetheless the strongest available *same-campaign* constraint on the
rate, precisely because the endpoint beverage data cannot supply it; it is not an
independent external validation.

**A numerical identifiability panel** (`identifiability_panel`) quantifies the valley on
the caffeine matched-mass **SSE** objective (unweighted concentration-scale SSE with a
least-squares nuisance level — a smooth local-curvature diagnostic; MAPE, the paper's
predictive metric, is reported as a cross-check): locate the minimum, fit a local
Hessian in **log parameters** (u = ln rate, v = ln c_s0; the standard sloppiness basis,
valid on the log-spaced grid), and profile the rate. The result is unambiguous and, at
the matched endpoint, *stronger* than before: **condition number ≈ 1930** (one stiff,
one sloppy direction; interior optimum, reliable Hessian) and a **local inverse-curvature
coupling ≈ −0.99** — a geometric diagnostic of the SSE valley (the sloppy eigenvector
lies almost exactly along `c_s0·φ = const`), **not** a statistical parameter correlation,
since no likelihood is specified. The profiled SSE has an **interior numerical minimum**, but its 10 %-above-minimum set
extends from ≈0.4 up to the **upper tested rate boundary (6.5)** — so the set is
**right-censored** by the tested domain (its upper extent is not closed, and the reported
log-width ≈ 2.8 is a *lower bound* on the full near-optimal extent, not a domain-
independent width). It covers **~76 % of the swept log-rate grid**. The exact
weighted-median **MAPE** profile agrees quantitatively — its 10 % set overlaps the SSE set
with **Jaccard ≈ 0.86** and covers ~66 % of the grid (replacing the earlier arbitrary
binary "agreement" flag; the still-earlier "33 %" was a tuple-indexing bug, review A2-01,
now corrected and unit-tested).
Trigonelline is similar (condition number ≈ 3600,
coupling ≈ −0.84, SSE profile flat over ~45 % of the grid). This is practical
non-identifiability over the tested domain, quantified — robust to the matched-mass and
exact-level corrections and consistent across the SSE and MAPE objectives.

**Grid-density and domain convergence** (`identifiability_panel_convergence`, review
A2-06/07) confirms it is not a coarse-grid or chosen-domain artefact: across rate grids of
**18 / 36 / 72** points the caffeine condition number is **1924 / 2069 / 2067** and the
coupling **−0.99** (both stable to ≤10 %), and the flat valley persists on a **narrower
[0.3, 3]** (log-width 2.0, 89 % of grid within 10 %) and a **wider [0.1, 10]** (log-width
3.3) domain. In every configuration the 10 % threshold set **reaches the swept-domain
boundary** — the profile is therefore **right-censored**: the flat region extends beyond
the tested rate range, so the reported widths are lower bounds and the rate is, if
anything, *less* bounded than the finite-domain numbers imply.

Strength: this is a *diagnosis of the fit*, established on the transfer target and
corroborated on the model's own data in §6 — not a claim about the model's physics.

## 5. Result 3 — cross-grind endpoint prediction versus a level-only baseline

*Practical non-identifiability (§4) and predictive transfer are separate questions:
a compensating manifold can leave predictions stable even when the parameters are
individually non-identifiable. **The corrected results show exactly this** — and, in
doing so, overturn a claim in our earlier draft.* We freeze the O calibration
(level+rate pair) and predict the held-out coarse (C) and fine (F) grinds at **matched
40 mL matched-volume proxies for the nominal 40 g cups**, each with its own **study-derived, inferred (not measured) pressure–flow map** (fitted
hydraulic conductivity, nominal grind-specific shot time, and viscosity correction —
*not* a per-shot measured flow trace; transfer conclusions are conditional on this map):

| species | O-fit | held-out C | held-out F |
|---|---|---|---|
| caffeine | 3–5 % | 8–10 % | 5–7 % |
| trigonelline | 2–4 % | 7–8 % | 3–7 % |
| 5-CQA | 5–12 % | 10–18 % | 5–9 % |

The frozen O calibration produces held-out **absolute** errors of C ~7–18 %, F ~3–9 %
— a large improvement over our pre-correction draft, which reported **25–49 %** held-out
error and concluded the model "does not transfer across grind." **That failure was mostly
an artefact of the unmatched 25 s endpoint** (review B1/B5): once cups are matched to the
target beverage endpoint, the absolute error is much smaller. **This is an internal
cross-grind holdout** — C and F are held-out granulometries from the *same* Angeloni
campaign (same varieties, platform, assay), a within-campaign design extrapolation, not
an external-rig prediction (review A2-03).

**Null benchmark (review A3-01): absolute error alone does not establish transfer skill.**
Because the model profiles a free inventory level, a constant carrying only that level is
the natural null. Against an **O-trained MAPE-optimal constant** — one concentration fit
to the nine O observations and applied unchanged to C/F, with no temperature, pressure,
flow, or kinetic response — the mechanistic model's pooled held-out MAPE is **8.2 %**
versus **8.6 %** for the constant (`transfer_skill_vs_baselines`). That is an incremental
skill of only **≈4 % relative** (**0.36 pp** absolute), and the model is **worse than the constant on
50 of 108 held-out points** (better than a same-(T,p) O lookup, 10.8 %, by ~2.6 pp). The
honest reading is therefore that the fitted level-plus-rate pair *does not catastrophically
deteriorate* across grinds — **not** that the kinetic/transport mechanism transfers: its
incremental predictive skill over a level-only baseline is small, and endpoint-level MAPE
does not diagnose mechanism. This sharpens rather than weakens the paper's thesis.

A **shared-parameter compatibility analysis** complements the holdout: a *single shared*
`(c_s0, rate_scale)` fitted jointly to O+C+F (`joint_multigrind_fit`) reconstructs the
pooled data at **6.4 % macro-MAPE against 4.9 %** for the per-grind independent fits — a
modest **in-sample** cost-of-sharing of ~1.5 pp. This is an in-sample compatibility test
(it scores the same pooled observations it was fitted to), **not** a held-out prediction.
An **in-sample comparator ladder** (`reduced_model_ladder`, review A3-19) makes its
adequacy auditable. These are **non-nested models of unequal flexibility, each scored on
its own fitting data** (no complexity penalty or held-out evaluation), so the comparison
is descriptive: mean in-sample macro-MAPE runs one-constant **7.1 %** (1 param) →
per-grind-constant **5.1 %** (3 params) → shared-mechanistic **6.4 %** (2 params) →
per-grind-mechanistic **4.9 %** (6 params). The salient comparison is that the
2-parameter **shared mechanistic model has lower in-sample MAPE than the 3-parameter
per-grind constant in none of six variety–solute comparisons** — i.e. the mechanistic
response did not improve in-sample MAPE over grind-specific levels in this dataset,
consistent with the small held-out skill above (this is a descriptive in-sample
comparison, not proof that mechanism "explains nothing").

The `(inventory, rate)` split is **degenerate within a grind** — the fitted rate flips
with incidental choices (§4). Propagating the **discrete 10 %-near-optimal MAPE grid set**
(O-MAPE within 10 % of the minimum on the 18-point rate grid — a *declared set*, not a
continuous manifold), the worst **aggregate** held-out C/F error rises to **21.7 %** (vs
18.2 % at the point optimum; `validate_refit_granulometry.manifold_transfer`). We now also
propagate the set to **condition-wise prediction envelopes** (review A3-11): at each
held-out (T, p) the predicted concentration ranges across the near-optimal set span a
**median of only ~3 % of the observation** (worst ~16 %), and the worst-case held-out MAPE
grows only modestly across declared tolerances (2/5/10/20 %: ~8.5→9.7 % for caffeine).
So the *aggregate and pointwise* prediction is stable across the set even though the
parameters on it are not — the distinction between parameter identifiability and
prediction stability, *tested* (review A2-02) rather than asserted. This stability is,
however, distinct from mechanistic skill (the ladder and null benchmark above). Strength: **within-campaign cross-grind holdout with a null-model skill
comparison**, conditioned on the tested flow maps, frozen centre-grind geometry, and
matched endpoint.

**Cross-validation, uncertainty, and robustness** (`loco_cv_refit`,
`geometry_sensitivity_transfer`). Replacing the weak two-off-grid-point holdout with
**leave-one-(T,p)-condition-out CV** over the nine on-grid O conditions gives a pooled
held-out MAPE of **6.5 %** (median **5.2 %**), reported per solute × variety (medians
2.8–8.8 %, worst individual fold 32.7 % on Robusta 5-CQA) rather than as a single mean
(review M4). Because the 54 held-out errors share overlapping folds and repeated
conditions, we report **two descriptive resampling summaries**, neither of which is a
coverage-calibrated confidence interval (review MAJ-05/A2-04): a residual-resampling
interval that ignores fold dependence (**[5.0, 8.2] %**), and a condition-level
resampling of the nine (T,p) macro errors (macro mean 6.5 %, **[5.1, 8.3] %**). The two
nearly coincide, but this does **not** demonstrate that fold dependence is immaterial —
both resample already-computed fold errors *without* repeating the fit, and the LOCO
training sets overlap, so neither corrects the fold dependence; a coverage-calibrated
interval would require a resampling scheme that repeats the fit (owed). The verdict is
robust to the loss function: under a log/relative-error level fit the pooled mean is
**7.0 %** (review M6). It is also robust to the choice of a
single **global** frozen geometry: re-running the O→C/F transfer under each of the three
Pannusch fitted geometries (1.4/1.7/2.0, applied globally to all grinds) moves the
held-out MAPE by **at most ~1 pp** (review B5) — which supports limited sensitivity to
the *global* geometry choice over that range, but does **not** validate a grind-specific
geometry map (a calibrated cross-grinder map remains unavailable; geometry stays an
unresolved structural uncertainty). It is likewise robust to the **inferred flow-map
magnitude** (`flow_map_sensitivity_transfer`, review A2-10): a systematic **±20 %** flow
scale (a shot-time / hydraulic-conductivity uncertainty proxy), with the O calibration
refitted and transferred under the perturbed map, moves the held-out MAPE by **≤ 0.6 pp**
(the fitted rate shifts 0.71→0.88, as expected from the non-identifiability, while the
*prediction* barely moves) — so the transfer conclusion does not hinge on the exact
flow-map magnitude, though it remains conditional on the inferred-map *form* (a per-shot
measured flow trace is still owed). Together these support the corrected §5 conclusion —
the calibration's held-out **absolute** error is modest and does not catastrophically
deteriorate across grind (while its incremental skill over a level-only null is small,
per the benchmark above) — with cross-validation, descriptive uncertainty, and
loss/geometry/flow-map robustness, not a two-point mean.

## 6. In-sample fraction verification and an independent external TDS trajectory test

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
**exact single whole-cup integral** `[0, t_end]` — add seeded relative noise over **20
independent seeds** (the PDE predictions are seed-independent, so this is inexpensive),
then sweep the rate. **Result:** fraction-curve scoring recovers rate = 1 sharply — mean
range ratio **9.8× / 20.3× / 13.2×** (caffeine / trigonelline / 5-CQA; seed std ≤ 1.1),
with the best rate exactly at the calibrated value in **100 %** of seeds — while scoring
the **exact whole-cup integral** stays flat (range ratio **1.5 / 1.5 / 1.7×**). The exact
cup is only marginally more informative than the crude six-window aggregate and remains
essentially flat. This isolates the information-content difference from the
sampled-window artefact — within this **same-model, best-case** design (an inverse crime,
no model discrepancy): a *true* whole cup, not just a sampled aggregate, carries far less
kinetic-rate information than the resolved fractions. We removed the two obvious
best-case artefacts (review A3-15/A3-16, `full_cup_simulation_offgrid_noise`): generating
truth at **off-grid rates** (0.7 / 1.15 / 1.8, none on the candidate set) and recovering a
**continuous** rate from a dense grid, the fraction objective still recovers the true rate
to a few-percent error while the cup is far worse — and this holds under **heteroscedastic**
and **correlated per-shot** noise, not just iid. So the contrast is not an artefact of an
on-grid true rate or iid noise. It remains **not** evidence that a real experimental cup
lacks rate information, nor that the model is correctly specified — the model-discrepancy
dose-response (§6, `full_cup_simulation_discrepancy`) shows a sharp fraction minimum is
necessary-not-sufficient. Strength: **simulation study** (exact integral, seeded noise) —
not an empirical positive control.

**An independent external test** (`external_waszkiewicz`). The Pannusch fraction data
above are part of the model's own calibration lineage, so they provide *in-sample
verification* of objective localization, not independent identification. To add a
genuinely external observation class we evaluate the public five-second TDS fractions
of Waszkiewicz et al. (2026, *Phys. Fluids* **38**, 063113; already in the repo as
`waszkiewicz2025`, same Zenodo release), collected on a **second café-grade rig** with
a simultaneously measured flow trace. We freeze the Pannusch TDS *kinetics* and, at
each rate, **profile a target-specific concentration level** against the Waszkiewicz
observations (the coffee and inventory differ). This is therefore **external-data
objective localization**, *not* a blind frozen concentration prediction — the level is
fitted to the target trajectory, so only the rate shapes the profile. **Result:** the
twelve-fraction trajectory *does* constrain the kinetic rate — a profiled-MAPE trough
(fraction range ratio **~2×**, best rate **~0.4**, minimum MAPE **~27 %**) — whereas the
single integrated cup carries **no rate information**: with one integrated scalar and
one free multiplicative level, the model matches that scalar exactly at every rate, so
the flat cup profile (range ratio 1.0×) is **algebraic by construction**, not an
empirical discovery that cup-integrated designs generally lack rate information (a
multi-cup design at different flows/endpoints could still localize the rate). The localization is **weaker** than the
in-sample Schmieder result (range ratio ~2× vs ~10×) and the minimum MAPE is high
(~27 %): the frozen Pannusch TDS kinetics reconstruct this different coffee's
aggregate trajectory only moderately, and the best-fit rate (~0.4) reflects a
faster-decaying trajectory than the model at rate 1 — honest external limits, not a
tight fit. The *direction*, however, is robust across declared time-origin offsets
(0/2/4 s, since brewer activation precedes first drip) and with or without the
single-replicate first bin (no imputation of its missing standard deviation):
fraction scoring always constrains the rate (ratio 1.6–2.1×), the cup never does
(1.0×). Scoped conclusion (handoff §2.6): *on the independent TDS
trajectory, fraction-resolved observations produced a more localized profiled
objective than the corresponding cup-integrated aggregate, under the tested model,
parameter domain, time-alignment assumptions, and aggregate-solids observation
operator.* **This is an aggregate-solids proxy (optical TDS), one coffee and one
grind — an external objective-localization panel, not independent named-solute
identification.** *(Owed: a named-solute, multi-PSD external dataset — Kuhn 2017 /
Vaca Guerra 2024 requests in `docs/data_requests/`.)*

## 7. Discussion

**What a single-grind endpoint fit constrains here.** Over the tested domain it
constrains essentially the *product* `c_s0 · φ` (the level); neither the inventory
nor the kinetic rate is individually pinned. This is a *practical* statement about
this design and objective, not a theorem that every endpoint design identifies only
a product — sufficiently informative endpoints at different residence times, flows,
or temperatures could in principle carry rate information.

**Four distinct properties.** The single-grind endpoint does not pin the rate (§4); the
frozen level+rate pair's held-out **absolute** error across grind is modest (§5); but its
**incremental skill over a level-only null is small** (§5, A3-01); and a shared fit is
*in-sample* compatible (§5). These are four separate properties — **parameter
identifiability, endpoint accuracy, predictive skill over a benchmark, and cross-grind
transferability** — and they do not coincide here. Aggregate prediction is stable across
the near-optimal set even though the parameters on it are not individually estimable, but
that stability is *not* the same as adding mechanistic information beyond a transferred
level. What would separately *identify* the rate is different information — holding the
inventory to an independent measurement, or time-resolved fractions, which constrain the
rate via the early-time slope where an aggregated endpoint does so weakly (§6).

**Lesson for cross-dataset extraction-model validation.** A single-grind endpoint MAPE —
even a low held-out one — need not identify a mechanism *and need not signal mechanistic
skill beyond a null model*: **endpoint accuracy, parameter identification, cross-grind
transferability, and incremental skill are distinct properties and must be reported
separately.** A second, procedural lesson: **a validation score is interpretable only when
the model output is mapped to the same observation window and endpoint as the data** — an
unmatched fixed-time window manufactured a spurious cross-grind transfer failure in our
earlier draft, which the correction removed. On the strength ladder, the
`pannusch2024`→`angeloni2023` refit is **post-fit reconstruction (a new calibration on the
angeloni coffee) whose frozen held-out error is modest at the matched endpoint but whose
incremental skill over a level-only baseline is small, and which does not, on this
dataset, identify the kinetic rate.**

**Standing position.** `pannusch2024` remains calibrated to the Schmieder fraction
campaign, whereas `angeloni2023` is an independent target campaign. After
target-specific O-grind recalibration and matched-endpoint mapping, absolute C/F errors
were modest, but performance was **nearly matched by an O-trained level-only constant**
(pooled 8.2 % vs 8.6 %; the mechanism was worse on 50/108 held-out points). The result
therefore supports **endpoint prediction stability under the tested within-campaign
design, not transfer of an identified kinetic mechanism**. This scoping supersedes both
the earlier "gap closed / inventory-vs-kinetic" reading *and* the subsequent "does not
transfer across grind" reading — the first over-claimed identification, the second was
an endpoint artefact.

## 8. Open gaps this paper defines

- **Held-out validation, uncertainty, and robustness** — *delivered* (§5): the joint
  multi-grind fit (`joint_multigrind_fit`, pooled 6.4 % vs 4.9 %, cost 1.5 pp); **leave-one-condition-
  out CV** (`loco_cv_refit`, pooled 6.5 %, median 5.2 %; two DESCRIPTIVE resampling
  summaries — residual and condition-level — neither coverage-calibrated, MAJ-05/A2-04)
  replacing the 2-point holdout (M4) with descriptive intervals and a log-loss robustness
  check (M6); and a **geometry-sensitivity sweep** (`geometry_sensitivity_transfer`,
  ≤1 pp across the three fitted geometries, B5). Still owed: per-condition residual
  plots by (T, p, grind, variety, solute); per-point measurement-uncertainty weighting
  (only total-solids carries RSD; the named-solute rows retain the source's reported
  central values, not the replicate-level RSD); and a coverage-calibrated CV interval
  that repeats the fit under resampling.
- **A profiled-objective / condition-number identifiability panel** — *delivered*
  (§4, `identifiability_panel`): caffeine log-Hessian condition number ≈1930, local
  inverse-curvature coupling ≈ −0.99 (a geometric SSE-surface diagnostic, not a
  statistical correlation), SSE profile flat over ~76 % of a wide rate sweep (MAPE
  cross-check ~66 %). Still owed on top: the same panel across all solutes/varieties as
  a supplementary figure. Grid-density/domain convergence is **delivered**
  (`identifiability_panel_convergence`, A2-06/07): condition number 1924/2069/2067 across
  18/36/72-point grids, flat valley on [0.3,3] and [0.1,10], threshold set right-censored.
- **An empirical full-cup comparison** (review B2) — the exact-integral simulation
  (§6) is delivered; the empirical version is **data-blocked** (the repo has only
  fraction windows 1,2,3,5,7,10; the BR-1/3 cup mass/endpoint is ambiguous).
- **Time-resolved fractions on an independent rig** — the measurement that would
  turn the §6 verification into an independent identification off `pannusch2024`'s
  own fit data.
- **A per-species inventory measurement on the calibration coffee** to close the
  external tie-breaker without borrowing angeloni's Table 7.

## Figures

**Eight figures** (`docs/figures/paper_a/`, rendered from the corrected matched-mass
analysis via `python -m puckworks.figures_paper_a`; every value regenerates from the
slow analysis functions, none hand-typed): six main figures (1–6) and two
condition-structure diagnostics (7–8; A4-09). All figure titles state design and
quantities, not verdicts.

- **Fig 1** — study & evidence design with campaign-accurate categories: source
  calibration → Angeloni-O target recalibration → within-campaign leave-one-condition-out
  holdout → within-campaign O→C/F cross-grind holdout → Table 7 same-campaign orthogonal
  measurement → in-sample localization → independent Waszkiewicz external panel.
- **Fig 2** — inventory–rate objective surface (caffeine, trigonelline): the flat
  valley, the profiled path, the Table 7 inventory line, and the condition number
  (§4).
- **Fig 3** — leave-one-condition-out holdouts: (a) observed vs predicted by solute ×
  variety; (b, c) the **signed residual faceted against temperature and pressure**, which
  exposes the within-group condition structure the near-diagonal cloud and the pooled
  6.5 % hide (§5, M4; review A3-05).
- **Fig 4** — O→C/F transfer at the matched-volume endpoint proxy: observed vs predicted
  per condition (grinds C, F) **plus a third panel comparing the model against an
  O-trained level-only constant baseline** and reporting the pooled skill (§5, A3-01).
- **Fig 5** — joint shared-(c_s0, rate) residual by variety × solute × grind, with
  the cost-of-sharing and rate-boundary flags (§5).
- **Fig 6** — rate profiles in **three evidence tiers** (§6): (a–c) in-sample Schmieder
  empirical fraction + same-model exact-cup simulation with the ±1σ 20-seed band;
  (d) the **independent external Waszkiewicz** TDS trajectory as a target-profiled shape
  test — a shallow ~27 % minimum with an alignment-sensitivity band and the
  algebraically-flat single cup (one scalar + one profiled level).
- **Fig 7** *(diagnostic)* — per-group blind and inventory-matched errors, with the
  cross-condition model–data response correlation (n=9 O conditions/group; 40 mL proxy
  endpoint). Panel (b) is a cross-condition association, **not** a temporal trajectory
  (A4-31); the n=9 correlation is descriptive.
- **Fig 8** *(diagnostic)* — blind source-model residuals by operating condition,
  **before** the per-group target level is fitted. The solute/variety group offsets
  motivate the target-level recalibration; a per-group level **can** remove such offsets,
  so this figure motivates rather than proves irreducibility (A4-08). Within-group (T,p)
  structure after level-fitting is the owed follow-up (deferred; see §8 Open gaps).

## 9. Related work

*Citations are verified against the source DOIs collated in
`docs/literature_search/references.bib`; the search is a **documented scoping
search** (protocol + log in `docs/literature_search/`), not a PRISMA-complete
review — the full Scopus/Web-of-Science query is run and archived at submission, so
novelty is stated as "to our knowledge, following a documented scoping search," not
as categorical priority.*

**Structural and practical identifiability.** Parameter estimation in mechanistic
models must distinguish structural identifiability from practical identifiability.
Structural identifiability concerns uniqueness under ideal, noise-free observations
for a specified model, input, initial condition, parameterization, and observation
map, whereas practical identifiability concerns whether finite and noisy data
localize the parameters under the actual experimental design and objective.
Structural-identifiability methods have been compared and systematized by Chis et al.
(2011), Miao et al. (2011), Villaverde et al. (2016), and Villaverde (2019). Raue et
al. (2009), Wieland et al. (2021), Heinrich et al. (2025), and Simpson & Maclaren
(2023) emphasize that a parameter may be structurally identifiable yet practically
weakly constrained, and that nonlinear profiles can reveal asymmetric or effectively
unbounded uncertainty that a local covariance approximation misses.

**Profiles, sloppiness, and parameter compensation.** Profile-likelihood and
profile-wise analyses characterize how the optimum changes when one parameter is
fixed and the rest are re-optimized — useful for detecting compensation, boundaries,
and asymmetric uncertainty. Work on "sloppy" models describes broad spectra of
parameter sensitivities and a geometric model manifold with narrow and broad
directions (Gutenkunst et al., 2007; Transtrum et al., 2011, 2015). Sloppiness and
identifiability are related but not equivalent (Tönsing et al., 2014; Chis et al.,
2016), and experimental design may improve some weak directions without guaranteeing
that all parameters become well determined (Apgar et al., 2010; White et al., 2016).
We therefore use the descriptive term *inventory–rate profile valley* unless a
scaled sensitivity-spectrum analysis is explicitly reported. The formal panel profiles
**SSE** (a smooth local-curvature diagnostic) with MAPE as an agreeing cross-check, and
— because no likelihood or noise model is specified — we report a *profiled objective*,
not a profile likelihood, and an inverse-curvature **coupling** coefficient, not a
statistical parameter correlation.

**Reaction/transport confounding and design.** Similar parameter-confounding
problems occur in environmental, reaction–transport, gas–liquid mass-transfer, and
dissolution models, where kinetic coefficients, diffusivities, transfer
coefficients, inventories, and boundary conditions can induce nearly collinear
output changes (Brun et al., 2001; Navarro-Laboulais et al., 2008; Haario et al.,
2007; Browning et al., 2024). Optimal experimental-design studies seek inputs,
conditions, and sampling times that create distinct sensitivity directions (Banga &
Balsa-Canto, 2008; Bandara et al., 2009; Liepe et al., 2013; Lages et al., 2012).
For extraction models this motivates combining early, middle, and late fractions,
multiple operating conditions, and independent inventory measurements rather than
relying on a single integrated endpoint.

**Coffee lineage and the gap.** Coffee-extraction modelling includes multiscale and
asymptotic formulations (Moroney et al., 2015, 2016), well-mixed kinetics (Moroney
et al., 2017), porous-bed non-uniformity (Moroney et al., 2019), brewing-control-
chart and espresso-optimization studies (Melrose et al., 2018; Cameron et al., 2020),
mesoscopic and porous-media simulations (Ellero & Navarini, 2019; Giacomini et al.,
2020), and component-resolved or dispersive packed-bed models (Schmieder et al.,
2023; Pannusch et al., 2024; Vaca Guerra et al., 2024). Time-resolved experiments
have measured caffeine and trigonelline across particle-size distributions (Kuhn et
al., 2017), representative nonvolatile solutes and TDS across process conditions
(Schmieder et al., 2023), volatile release online (Sánchez-López et al., 2014, 2016),
and independent TDS fractions with simultaneous flow measurements (Waszkiewicz et
al., 2026). In our documented scoping search we did not find an espresso study that
explicitly profiles inventory–rate compensation and separates in-sample
localization, internal holdout, external-data objective localization, and target-data
refitting. Paper A addresses that applied gap using established identifiability
methods (an applied espresso case study, not a new identifiability method).

**Novelty (case study + model/data observation, not a new method).** To our
knowledge, based on a documented scoping search, mechanistic coffee-extraction
modelling and the mature inverse-problem toolkit (structural/practical
identifiability, profile analysis, parameter-compensation manifolds, model-based
experimental design) have not previously been combined in a systematic
practical-identifiability study of inventory–rate confounding in a multi-solute
espresso-extraction model evaluated with internal holdouts and independent coffee
datasets. Our contribution is therefore an espresso case study and a
model–data-specific result, not a new general identifiability method: under the
tested whole-cup design, inventory and kinetic rate occupy a broad compensating
profile, whereas fraction-resolved observations provide substantially stronger
localization of the rate. *These results do not establish that cup-integrated
observations are structurally incapable of identifying extraction kinetics in
general; they establish weak practical localization for the tested model,
observation map, datasets, parameter domain, and error model.*

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
- **Independent external test:** `puckworks/validation/slow/external_waszkiewicz.py`
  — `waszkiewicz_external_tds` (external-data objective localization on the Waszkiewicz
  2026 5 s TDS trajectory, target-profiled level; measured 9-bar flow trace on the same
  shifted time origin as the observed-cup bin masses; flow-weighted interval operator;
  time-offset + first-bin sensitivity). Run:
  `python -m puckworks.validation.slow.external_waszkiewicz`.
- **Data:** `puckworks.data.angeloni_{bioactives,total_solids,inventories}` and the
  Schmieder fraction loaders; manifest rows carry the p→flow caveat.
- **Strength tags:** bracket = independent (wide envelope); per-condition/refit =
  post-fit, single grind; granulometry validation = negative (held-out grind);
  positive control = verification.
- These functions are slow (PDE solves; minutes) and live in `validation/slow/`,
  **not** in CI — the analysis is a paper-track deliverable, not a quick gate.

*Change log: see ROADMAP §7.1 (2026-07-12, Paper A manuscript conversion).*

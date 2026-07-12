# Paper A — draft prose (rev. 2026-07-12)

> **⚠ MAJOR REVISION IN PROGRESS (detailed review adopted, `docs/PAPER_A_DRAFT_detailed_review.md`).**
> The review found two real observable-contract bugs and a mislabelled optimiser.
> **Fixed in code:** the cross-grind/joint/transfer/identifiability paths now
> terminate at a **matched 40 g cup** (`t_end = 40 mL / Q`), not a fixed 25 s (B1);
> the MAPE inventory level is the **exact weighted median**, no longer a coarse grid
> falsely called "analytic" (B3); the rate domain is **widened + log-spaced** so a
> boundary optimum is exposed not imposed (B6); the positive-control endpoint is
> relabelled a **sampled-fraction aggregate** (it is not a whole cup) with a
> data-only audit that it differs ~28–38 % from the actual BR-1/3 cup (B2). **The
> headline numbers below are being regenerated from the corrected code**; where a
> value is marked *[regenerating]* it is provisional. **Still blocked / owed
> (flagged, not fabricated):** the systematic identifiability/inverse-problem
> related-work review (M9), the figure set, the full reproducibility/paper-build
> package + CI (M10), an independent fraction dataset, and the full-shot actual-cup
> reconstruction (B2 preferred design).*

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

*[Abstract being finalised from the corrected (matched-mass) results; specific
error ranges are omitted until regenerated, per review. Provisional scoped
version:]*

We examine whether a multi-solute extraction model calibrated on fraction-resolved
data (`pannusch2024`, calibrated on the Schmieder kinetics) retains a unique kinetic
interpretation when refitted to an independent endpoint dataset (`angeloni2023`; a
different machine, coffee, and basket). Profiling the model's two adjustable knobs —
a per-species solid **inventory** and a Sherwood mass-transfer **rate** scale —
against matched-beverage-mass cup concentrations at a single grind reveals a **broad
compensating region**: the rate is practically non-identifiable over the tested
domain because the inventory absorbs it, quantified by a log-parameter Hessian
condition number and a near-flat rate profile. We report **practical
non-identifiability and frozen-parameter predictive transfer as separate findings**:
a calibration frozen on one grind predicts held-out coarse/fine grinds poorly, and a
single shared (inventory, rate) fitted jointly to all grinds does not reproduce them
— conditioned on the tested flow maps, frozen centre-grind geometry, and matched
endpoint. In a separate **in-sample verification** on the model's own calibration
campaign, fraction-resolved scoring localizes the rate profile more sharply than an
aggregated endpoint score (the aggregate here is a sampled-fraction statistic, not a
full cup — it differs from the actual cup by ~30 %, so a full-cup comparison is
owed). The results motivate reporting parameter profiles and collecting temporal or
independent-inventory information, rather than treating a low endpoint error as
mechanistic validation.

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
calibrated grind). *[The numeric values in this table are being regenerated at the
matched 40 g endpoint (B1); the pre-correction values are shown, marked provisional.
The ~7 % holdout is a mean of two off-grid O points per solute × variety — a small
check, not a robust validation (review M4); TDS/total-solids is a proxy and will be
separated from the named solutes (M5).]*

| test | result *(provisional, pre-B1)* | reading | strength |
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
holdout. **That mechanistic decomposition is not supported by the profile
analysis** (§4): the fitted per-species rate is a point on a flat valley, not an
identified mechanism.

The flow-map refinement is a genuine but partial improvement: the cruder map
over-attributed flow to high pressure, and fixing the residence-time term closes a
few percentage points at the matched-mass endpoint. The residual is **not removed by
the two tested flow maps**; we do *not* attribute it uniquely to inventory + kinetics,
because competing sources — grain geometry (frozen at the centre grind), the
viscosity model, the endpoint, and the assay definition — are not separately
quantified here.

## 4. Result 2 — the degeneracy (core result)

The whole-cup concentration is, to good approximation, `C_cup ≈ c_s0 · φ(rate, flow,
T)` with `φ` the fractional extraction. Because `c_s0` enters linearly and the rate
enters only through `φ`, **both knobs move the level**, and the objective has a
flat valley along `c_s0 · φ = const`. Holding a single grind and re-optimising
`c_s0` at each rate makes this explicit (caffeine, Arabica, granulometry O):

Over a wide rate sweep the best-fit `c_s0` moves to compensate while the error
barely changes — the illustrative valley table is being regenerated at the matched
endpoint *[regenerating]*, but the primary evidence is now the formal panel below,
not a hand-tabulated sweep (review B4). We therefore describe inventory and rate as
**practically non-identifiable over the tested rate domain under this single-grind
endpoint design, flow assumptions, and objective** — not as an exact theorem that
all endpoint designs identify only a product. Two robust corollaries:

1. **The fitted rate is a boundary/valley-floor value, not a converged interior
   estimate**, so it flips with incidental choices (flow anchor, grind, rate
   domain). The earlier inventory-vs-kinetics decomposition was reading the valley
   floor, not a mechanism.
2. **The inventory absorbs the ambiguity too**, and the best-fit `c_s0` passes
   through the independently measured Table 7 inventory somewhere along the valley
   (caffeine fitted ~13 near the measured 12.5; Robusta ~17 near 18.6) — but the
   beverage data alone cannot single out the rate at which it does. That measured
   inventory is **one available external tie-breaker**; adding information breaks the
   degeneracy, optimising harder does not.

**A formal identifiability panel** (`identifiability_panel`) quantifies the valley.
On the caffeine matched-mass objective we locate the minimum, fit a local Hessian in
**log parameters** (u = ln rate, v = ln c_s0; the standard sloppiness basis, valid
on the log-spaced grid), and profile the rate. The results are unambiguous:
condition number **[regenerating]** (one stiff, one sloppy direction), rate↔inventory
**correlation [regenerating]** (the sloppy eigenvector lies along the
`c_s0·φ = const` valley), and the **profile SSE stays within 10 % of the minimum
across [regenerating] of the swept rate range**, so the data place little or no bound
on the rate. Where a profile minimum sits at the (widened) sweep boundary the local
Hessian is flagged unreliable and the model-free profile is used instead. This is
practical non-identifiability over the tested domain, quantified — not an artefact of
a coarse grid.

Strength: this is a *diagnosis of the fit*, established on the transfer target and
corroborated on the model's own data in §6 — not a claim about the model's physics.

## 5. Result 3 — frozen-parameter transfer across grind

*Practical non-identifiability (§4) and predictive transfer are separate questions
(a compensating manifold can leave predictions stable, or well-estimated parameters
can transfer poorly under misspecification); we report them separately.* Here we
test predictive transfer directly: freeze the O calibration and predict the held-out
coarse (C) and fine (F) grinds at **matched 40 g cups**.
Fitting on granulometry O and predicting the held-out coarse (C) and fine (F)
grinds — each with its own measured flow, at matched 40 g cups — gives (held-out
granulometry). *[Values regenerating at the matched endpoint (B1); pre-correction
values shown, provisional. This is one point in a hierarchy owed (review B5):
fixed-geometry matched-mass, then a plausible grind-geometry mapping from the
Pannusch 1.4/1.7/2.0 table, then geometry sensitivity.]*

| species | O-fit *(prov.)* | held-out C *(prov.)* | held-out F *(prov.)* |
|---|---|---|---|
| caffeine | 17–18 % | 23–25 % | 31–38 % |
| trigonelline | 19–20 % | 29–30 % | 43–44 % |
| 5-CQA | 17–24 % | 25–26 % | 46–49 % |

versus the same-grind O holdout (which uses a different evaluation set — not a
direct comparator, review §Result 3). Fine grind is worst: its flow departs most from
the calibration grind, and the fixed grind-O grain geometry mispredicts the
flow/surface-area sensitivity. A model whose sensitivity to flow is stronger than
the data's — angeloni's measured concentrations move only ~15 % across grinds
despite a >2× flow change — cannot both fit one grind and predict another with a
level-only correction. Strength: **negative validation** (held-out grind).

**The joint multi-grind fit — the strongest form of the test.** Rather than fit one
grind and predict the others, we also fit a *single shared, grind-independent*
`(c_s0, rate_scale)` **jointly** to all three granulometries at once, each with its
own measured flow (`joint_multigrind_fit`). If any shared (inventory, rate)
generalised across grind, the joint fit would approach the per-grind fits. It does
not: the **mean pooled MAPE is ~30 %, versus ~20 % for the per-grind independent
fits** (a cost-of-sharing of ~6–13 pp per species, and well above angeloni's own
~9–13 % model). Every solute is pushed to the rate-sweep boundary (2.5), and the
pooled residual concentrates on the **coarse and fine (extreme) grinds** while the
middle O grind stays best — the structured residual signature of a single
inventory+rate that cannot serve all grinds. This confirms the failed transfer is
not an artefact of the held-out protocol: **no adequate shared calibration was found
within the tested model and the (widened, log-scaled) parameter domain** — not a
proof that none exists. Strength: **failed shared-parameter fit** (a negative
predictive result, conditioned on the tested flow maps, frozen centre-grind
geometry, and matched endpoint).

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
multi-condition designs could also help). This is the constructive counterpart of
the negative transfer result, and it speaks to gap **G6** (multi-class
inventory ↔ kinetics). *(Owed, review B2: the preferred comparison scores full-shot
model predictions against the actual BR-1/3 cup, or reconstructs the complete shot;
the range ratio is a descriptive sharpness proxy, not a decision rule.)*

## 7. Discussion

**What a single-grind endpoint fit constrains here.** Over the tested domain it
constrains essentially the *product* `c_s0 · φ` (the level); neither the inventory
nor the kinetic rate is individually pinned. This is a *practical* statement about
this design and objective, not a theorem that every endpoint design identifies only
a product — sufficiently informative endpoints at different residence times, flows,
or temperatures could in principle carry rate information.

**What can reduce the ambiguity.** (i) Holding the inventory to an independent
measurement makes the rate better-constrained — though that fit is then *worse* for
trigonelline, i.e. the residual becomes a genuine structural/kinetic mismatch rather
than a free knob. (ii) Fitting multiple grinds jointly with a shared,
grind-independent inventory is the sharper transfer test, and no adequate shared
(inventory, rate) is found within the tested domain (§5; conditioned on the tested
flow maps and frozen geometry). (iii) Time-resolved fractions constrain the rate via
the early-time slope separately from the level; an aggregated endpoint does so much
more weakly (§6). Angeloni report an endpoint only, which is why *this* dataset does
not, on its own, separate the two — multiple endpoint conditions, independent priors,
or a different model structure could still carry information.

**Lesson for cross-dataset extraction-model validation.** A single-grind endpoint
MAPE — even a low held-out one — can be a **practically non-identifiable curve fit
rather than a transferred calibration**. Endpoint accuracy, parameter
identification, and frozen-parameter transfer are distinct properties and should be
reported separately. On the strength ladder, the `pannusch2024`→`angeloni2023` refit
is **post-fit reconstruction at a single grind; it does not reach independent
validation and its frozen predictions did not reproduce the held-out grinds under
the tested assumptions.**

**Standing position.** `pannusch2024` remains a Schmieder-calibrated runtime;
`angeloni2023` is an independent transfer *target* it does not meet across grind.
The two stay model-vs-data. This scoping supersedes any earlier "gap closed /
inventory-vs-kinetic" reading of the same refit.

## 8. Open gaps this paper defines

- **A joint multi-grind fit with a single shared inventory** — *delivered* (§5,
  `joint_multigrind_fit`): ~30 % pooled vs ~20 % per-grind, residual on the extreme
  grinds. Still owed on top: propagating measurement uncertainty into the pooled
  residual and testing a grind-dependent grain geometry (not just a level+rate) to
  see whether *any* physically-motivated extension recovers transfer.
- **A profile-likelihood / condition-number identifiability panel** — *delivered*
  (§4, `identifiability_panel`): caffeine relative-Hessian condition number ≈419,
  rate↔inventory correlation −0.96, profile flat across the whole rate sweep.
  Still owed on top: propagating measurement noise into a proper confidence region
  (bootstrap across shots), and the same panel across all solutes/varieties as a
  supplementary figure.
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
  Hessian/condition-number/profile-likelihood quantification of §4). Run:
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

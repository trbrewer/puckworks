# Paper A — P0-5 uncertainty results (A + B; review MC4)

Scope + design: [`PAPER_A_P0-5_UNCERTAINTY_SCOPE.md`](PAPER_A_P0-5_UNCERTAINTY_SCOPE.md). Author decisions:
run A+B now under the **sensitivity-sweep** framing (named-solute per-cell RSD is data-blocked),
**Huber** primary robust objective, **both** bootstrap units. Sub-analysis **C** (a LOCO-style interval that repeats the fit) is **DELIVERED (bounded)** -- see section (C) below; this header previously read 'deferred' and contradicted it. Producers: `identifiability_panel.objective_family` and
`transfer_skill_vs_baselines.records` → `paired_clustered_bootstrap` in
`puckworks/validation/slow/angeloni_bracket.py` (slow, hand-run; B=8000, seed 0).

## (A) Does the inventory–rate valley persist across objectives?

10 %-near-optimal rate set as a **fraction of the tested log-rate grid** (`_RATE_DOMAIN` 0.15–6.5,
**29** points), and the rate at the objective minimum, under each objective.

> **Corrected 2026-07-27 (third review MC3).** This note previously said 18 points while the
> machine-readable record (`PAPER_A_OBJECTIVE_FAMILY_PANELS.json`, `n_rate_grid`) and the formal
> Methods both said 29. The archived fractions decide it: every one of the eighteen panel ×
> objective values is an exact 29th (0.759 = 22/29, 0.345 = 10/29, 0.897 = 26/29) and none is a
> multiple of 1/18. The **29-point grid is correct**; only this supporting note was wrong. Counts
> are now printed as `k/29` alongside the fraction so the denominator cannot be lost again.

**Status: COMPLETE — all six solute x variety panels** (second review MC2; the two Robusta panels
that were owed have been run). Archived verbatim in
[`PAPER_A_OBJECTIVE_FAMILY_PANELS.json`](PAPER_A_OBJECTIVE_FAMILY_PANELS.json). The four panels
recorded earlier were re-run from the same producer and reproduced exactly; the only change to the
first four rows is that fractions are now printed at the producer's own precision (Arabica 5-CQA
0.345, previously shown as 0.35).

Grid counts are `points within the 10 % set / 29 tested rate points`.

| Panel | SSE frac / rate* | relative-L2 frac / rate* | Huber frac / rate* | censored? |
|---|---|---|---|---|
| Arabica caffeine | 22/29 = 0.759 / 0.66 | 19/29 = 0.655 / 0.58 | 21/29 = 0.724 / 0.86 | SSE, Huber upper; rel no (hi 4.34) |
| Arabica trigonelline | 13/29 = 0.448 / 3.79 | 14/29 = 0.483 / 3.32 | 13/29 = 0.448 / 6.50 | all upper |
| Arabica 5-CQA | 10/29 = 0.345 / 6.50 | 10/29 = 0.345 / 6.50 | 10/29 = 0.345 / 6.50 | all upper (min at boundary) |
| Robusta caffeine | 9/29 = 0.310 / 0.20 | 10/29 = 0.345 / 0.23 | 9/29 = 0.310 / 0.20 | all **lower** (min near lower edge 0.15) |
| **Robusta trigonelline** | **19/29 = 0.655 / 0.44** | **24/29 = 0.828 / 0.58** | **26/29 = 0.897 / 0.50** | rel + Huber upper; SSE no (hi 2.53) |
| **Robusta 5-CQA** | **29/29 = 1.000 / 0.15** | **29/29 = 1.000 / 0.44** | **29/29 = 1.000 / 0.34** | **both ends, all three — the whole domain is within 10 %** |

**Reading.** The broad near-optimal set is **invariant to the objective**: across all eighteen
panel x objective combinations the 10 % set spans **31–100 %** of the log-rate grid and reaches a
tested-domain boundary in **16 / 18** (so those widths are lower bounds). The two newly completed
Robusta panels do not weaken the conclusion — they sharpen it. Robusta 5-CQA is fully degenerate:
under every objective the **entire** swept domain lies within 10 % of the minimum, i.e. that panel
places no bound on the rate whatsoever. Robusta trigonelline is the one panel whose SSE set is not
censored at either end (0.23–2.53), yet it still spans two thirds of the grid, and it becomes
upper-censored under the relative and Huber objectives.

The **rate at the minimum also shifts with the loss function** (Arabica caffeine 0.66 → 0.58 → 0.86;
Arabica trigonelline 3.79 → 3.32 → 6.50; Robusta trigonelline 0.44 → 0.58 → 0.50 under
SSE → relative → Huber). We do **not** read a loss-dependent minimum as proof of non-identifiability
on its own: different losses can move a point estimate under model discrepancy or outliers even when
a parameter is reasonably estimable. The defensible reading is the conjunction — a substantial
loss-dependent shift *together with* broad, boundary-reaching near-optimal sets is additional
evidence that rate localization is weak under plausible objective choices. The weak localization is
therefore a property of the **design**, not of the unweighted SSE objective; a relative or robust
(Huber, δ per panel from 1.345·1.4826·MAD at the SSE optimum) weighting does not close the valley.
(Threshold family 2/5/10/20 % is archived per panel in the JSON; the picture is monotone and the
same.)

**Data-blocked piece:** a *calibrated* per-observation weighting of the named-solute profile is not
possible (only global RSD ranges exist); this is a **sensitivity sweep**, and the calibrated
named-solute interval remains owed on the Angeloni replicate drop.

## (B) Is the model-vs-null skill distinguishable from zero?

> **Superseded in part by round 7 (P0-3, P1-1).** The corpus and the primary resampling unit both
> changed: the benchmark now scores the complete 44-record coarse/fine corpus (132 named-solute
> observations, not 108), and the primary cluster is the **(variety, T, p) condition**, carrying all
> three solutes and both held-out grinds together. The numbers below are retained as the record of
> what was run at the time; the current values are in
> `PAPER_A_ENDPOINT_PROPAGATION.json` and Supplementary Table S3.

Pooled held-out MAPE: **model 8.44 %** vs **O-trained level-only comparator 8.83 %**; paired mean
ΔMAPE (model − comparator) = **−0.394 pp**; model worse on **62 / 132** held-out points.
Dependence-aware **paired clustered resampling sensitivity analysis** of the paired loss
(B = 8000, seed 0). We call it a sensitivity analysis rather than a confidence procedure because no
full sampling model is specified, and we report it as a *clustered percentile sensitivity range*
rather than a 95 % CI:

| Resampling unit | percentile range on pooled ΔMAPE (pp) | reaches zero? | frac. resamples model-worse |
|---|---|---|---|
| (variety, T, p) condition (**primary**) | **[−0.825, +0.000]** | **yes — upper bound on zero** | see archive |
| (T,p) condition within variety × solute group (secondary) | [−0.742, −0.044] | no, by 0.044 pp | see archive |
| whole variety × solute groups (secondary) | [−0.883, −0.024] | no, by 0.024 pp | see archive |

**Reading.** Once the 132 held-out points are treated as the **dependent** observations they are —
every (variety, T, p) condition observed for all three named solutes at both held-out grinds — the
mechanistic model's ~0.4 pp advantage over a level-only comparator is **not robustly distinguishable
from zero**: the primary range's upper bound sits on zero. The two secondary units clear zero by
0.02–0.04 pp, which is a difference too small to carry an inferential claim; that the three units
disagree at the third decimal place is itself the sign the effect is marginal. Read with the small
absolute difference, **the mechanism adds no resolvable predictive skill beyond a learned level** —
which sharpens (does not weaken) the paper's thesis that endpoint accuracy ≠ mechanistic skill.
Descriptive/sensitivity; no evidence-tier change.

**Note on scope.** This clustered bootstrap resamples the *precomputed* paired losses of two fixed
predictors, so it does not require repeating the fit — appropriate for the null *comparison*. The
separate **condition-cluster out-of-bag interval that repeats the fit inside the resample loop**
(sub-analysis C) is **DELIVERED (bounded)** -- `loco_coverage_interval`, 600 draws / 599 effective, held-out MAPE 7.4 %, 95 % [4.3, 11.5] %; see section (C).

## (C) Condition-cluster out-of-bag refit bootstrap — DELIVERED (bounded)

`loco_coverage_interval` (`_oob_coverage_bootstrap` core), 600-replicate cap, seed 0. The per-unit-level
PDE matrix `F` is data-independent, so it is cached once (the only PDE cost) and each replicate
resamples the nine (T,p) **conditions** (the dependence cluster), **refits** rate+level on the in-bag
conditions, and scores the **out-of-bag** ones — an interval that genuinely repeats the fit, with no
leave-one-out-on-resample leakage.

**Naming (second review MC3).** This is *not* a coverage-calibrated interval and is no longer
described as one. Repeating the fit removes one known source of optimism; it does not establish that
the interval attains its nominal frequentist coverage, which would require a simulation study under a
specified data-generating process. With only **nine** clusters per group a percentile bootstrap is an
exploratory uncertainty summary. Its estimand also differs from single-condition LOCO: each
out-of-bag set holds out ~3–4 of the nine conditions.

| statistic | value |
|---|---|
| pooled held-out MAPE (OOB point) | **7.4 %** |
| 95 % percentile interval (out-of-bag, refit) | **[4.3, 11.5] %** |
| effective replicates | 599 / 600 (one draw discarded: its resample left no condition out of bag) |

**Reading.** Repeating the fit gives a **wider** interval than the two descriptive summaries
([5.0, 8.2] % residual-resampling, [5.1, 8.3] % condition-cluster) — precisely because those omit the
refitting variability. The OOB centre (7.4 %) runs slightly above the LOCO point estimate (6.5 %)
because out-of-bag held-out sets (~3–4 of 9 conditions) are larger than LOCO's single condition, so
this **complements** rather than replaces the LOCO estimate. The held-out error remains modest
(single-to-low-double-digit) under the refit interval — the §5 conclusion is unchanged; the
uncertainty is just stated correctly.

## Owed after this PR

- **Calibrated named-solute weighting** — blocked on the Angeloni raw-replicate drop.
- **Supplement figure** — the six completed objective-family panels still need to be drawn as a
  supplementary figure; the underlying numbers are complete and archived
  ([`PAPER_A_OBJECTIVE_FAMILY_PANELS.json`](PAPER_A_OBJECTIVE_FAMILY_PANELS.json)).

# Paper A — P0-5 uncertainty results (A + B; review MC4)

Scope + design: [`PAPER_A_P0-5_UNCERTAINTY_SCOPE.md`](PAPER_A_P0-5_UNCERTAINTY_SCOPE.md). Author decisions:
run A+B now under the **sensitivity-sweep** framing (named-solute per-cell RSD is data-blocked),
**Huber** primary robust objective, **both** bootstrap units. Sub-analysis **C** (coverage-calibrated
LOCO that repeats the fit) is **DELIVERED (bounded)** -- see section (C) below; this header previously read 'deferred' and contradicted it. Producers: `identifiability_panel.objective_family` and
`transfer_skill_vs_baselines.records` → `paired_clustered_bootstrap` in
`puckworks/validation/slow/angeloni_bracket.py` (slow, hand-run; B=8000, seed 0).

## (A) Does the inventory–rate valley persist across objectives?

10 %-near-optimal rate set as a **fraction of the tested log-rate grid** (`_RATE_DOMAIN` 0.15–6.5, 18
points), and the rate at the objective minimum, under each objective:

| Panel | SSE frac / rate* | relative-L2 frac / rate* | Huber frac / rate* | upper-censored? |
|---|---|---|---|---|
| Arabica caffeine | 0.76 / 0.66 | 0.66 / 0.58 | 0.72 / 0.86 | SSE, Huber yes; rel no (hi 4.34) |
| Arabica trigonelline | 0.45 / 3.79 | 0.48 / 3.32 | 0.45 / 6.50 | all yes |
| Arabica 5-CQA | 0.35 / 6.50 | 0.35 / 6.50 | 0.35 / 6.50 | all yes (min at boundary) |
| Robusta caffeine | 0.31 / 0.20 | 0.35 / 0.23 | 0.31 / 0.20 | none (min near lower edge 0.15) |

**Reading.** The broad near-optimal set is **invariant to the objective**: across all panels and all
three objectives the 10 % set spans **31–76 %** of the log-rate grid and reaches a domain boundary in
most panels (right-censored, so the widths are lower bounds). Crucially, the **rate at the minimum
shifts with the loss function** (e.g. Arabica caffeine 0.66 → 0.58 → 0.86 under SSE → relative → Huber;
trigonelline 3.79 → 3.32 → 6.50) — a well-identified rate would not move with the objective. The
weak localization is therefore a property of the **design**, not of the unweighted SSE objective; a
relative or robust (Huber, δ per panel from 1.345·1.4826·MAD at the SSE optimum) weighting does not
close the valley. (Threshold family 2/5/10/20 % in the run log; the picture is monotone and the same.)

**Data-blocked piece:** a *calibrated* per-observation weighting of the named-solute profile is not
possible (only global RSD ranges exist); this is a **sensitivity sweep**, and the calibrated
named-solute interval remains owed on the Angeloni replicate drop.

## (B) Is the model-vs-null skill distinguishable from zero?

Pooled held-out MAPE: **model 8.23 %** vs **O-trained level-only constant 8.59 %**; paired mean
ΔMAPE (model − const) = **−0.36 pp**; model worse on **50 / 108** held-out points. Dependence-aware
**clustered bootstrap** of the paired loss (B = 8000, seed 0):

| Resampling unit | 95 % CI on pooled ΔMAPE (pp) | excludes zero? | frac. resamples model-worse |
|---|---|---|---|
| conditions within group (primary) | **[−0.73, +0.03]** | **no (straddles 0)** | 0.035 |
| whole groups | [−0.75, −0.03] | yes (barely) | 0.011 |

**Reading.** Once the 108 held-out points are treated as the **dependent** observations they are (6
variety × solute groups × shared (T,p) conditions × two grinds), the mechanistic model's ~0.4 pp
advantage over a level-only constant is **not robustly distinguishable from zero**: the primary,
more-conservative conditions-in-group interval **includes zero** ([−0.73, +0.03]), and the coarser
group interval only *barely* excludes it ([−0.75, −0.03]). The two units disagreeing on the boundary
case is itself a sign the effect is marginal. Read with the small absolute difference, **the mechanism
adds no resolvable predictive skill beyond a learned level** — which sharpens (does not weaken) the
paper's thesis that endpoint accuracy ≠ mechanistic skill. Descriptive/sensitivity; no evidence-tier
change.

**Note on scope.** This clustered bootstrap resamples the *precomputed* paired losses of two fixed
predictors, so it does not require repeating the fit — appropriate for the null *comparison*. The
separate **LOCO coverage-calibrated interval that repeats the fit inside the resample loop**
(sub-analysis C) is **DELIVERED (bounded)** -- `loco_coverage_interval`, 600 replicates, held-out MAPE 7.4 %, 95 % [4.3, 11.5] %; see section (C).

## (C) Coverage-calibrated LOCO interval that repeats the fit — DELIVERED (bounded)

`loco_coverage_interval` (`_oob_coverage_bootstrap` core), 600-replicate cap, seed 0. The per-unit-level
PDE matrix `F` is data-independent, so it is cached once (the only PDE cost) and each replicate
resamples the nine (T,p) **conditions** (the dependence cluster), **refits** rate+level on the in-bag
conditions, and scores the **out-of-bag** ones — a coverage-calibrated interval that genuinely repeats
the fit, with no leave-one-out-on-resample leakage.

| statistic | value |
|---|---|
| pooled held-out MAPE (OOB point) | **7.4 %** |
| coverage-calibrated 95 % interval | **[4.3, 11.5] %** |
| effective replicates | 599 / 600 (1 skipped, empty OOB) |

**Reading.** Repeating the fit gives a **wider** interval than the two descriptive summaries
([5.0, 8.2] % residual-resampling, [5.1, 8.3] % condition-cluster) — precisely because those omit the
refitting variability. The OOB centre (7.4 %) runs slightly above the LOCO point estimate (6.5 %)
because out-of-bag held-out sets (~3–4 of 9 conditions) are larger than LOCO's single condition, so
this **complements** rather than replaces the LOCO estimate. The held-out error remains modest
(single-to-low-double-digit) under the honest, coverage-calibrated interval — the §5 conclusion is
unchanged; the uncertainty is just stated correctly.

## Owed after this PR

- **Calibrated named-solute weighting** — blocked on the Angeloni raw-replicate drop.
- **Supplement** — all six solute × variety objective-family panels (four run for A: Arabica ×3 +
  Robusta caffeine); Robusta trigonelline/5-CQA owed for completeness.

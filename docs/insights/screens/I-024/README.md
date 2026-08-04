# I-024 — multi-species common-state consistency

```
CHEAP_SCIENTIFIC_SCREEN
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

> **Corrected 2026-08-04 — decision unchanged (RETIRE), but the argument is rebuilt.** The first
> version claimed C3 was *scale-free* in the assumed bioactive RSD and inferred whole-band
> invariance from two endpoints. Both were wrong: changing the bioactive RSD reweights the
> bioactives against the **measured** total-solids weights and **refits the shared model** (its
> selected rate demonstrably moves). Replaced by an exact finite-grid breakpoint sweep plus
> rate-grid expansion. Several explanatory claims were also over-reaching and are corrected.

## What was run

**Question** (generated, verbatim from the candidate):

> Under one shared hydraulic and transport state, do the per-species residuals show structure
> that a single kinetic story cannot absorb?

## How to re-run

```
python -m puckworks.analysis.screen_i024_common_state
```

Writes `result.json` and `figures/primary.png`. ~5 min — **1440 PDE solves** (20 rates after
grid expansion × 18 conditions × 4 species). Amplitudes are fitted in closed form and the whole
RSD sweep is analytic, so neither costs a solve.

Focused test: `pytest tests/test_screen_i024.py -v`

## Evidence unit — the Angeloni campaign only

`angeloni2023` (bioactives + total_solids), granulometry O, on-grid, both varieties.
**18 conditions** (3 T × 3 p × 2 varieties) × **4 species** (caffeine, trigonelline, 5CQA,
total-solids proxy).

MANIFEST `validation_strength`, verbatim: `independent (different machine/coffee/basket than
pannusch fit or cameron calibration)`.

**Explicitly excluded from scoring**, as the authority requires. The generated candidate lists
these entities because the lens grouped them, not because they belong in this screen:

| excluded | why |
|---|---|
| `maille2024.phi_closure`, `maille2024.two_regime` | batch fits on a different campaign; scoring them would mix campaigns, which is the candidate's own INCONCLUSIVE confound |
| `ellero2019/fig4_caffeine_content` | digitised **simulation** output, not measurement — it cannot carry a residual |
| `khamitova2020/tamping` | different rig and design; reference strength only |
| `pannusch2024.solver` / `.closures` **as evidence** | used here as the **model**, never as evidence; its own fit target (Schmieder) is post-fit |
| `angeloni2023/lipids` | not a species the model produces; never scored |

## The two models

Both carry **one hydraulic state** per condition — one flow map, one bed, one porosity, one
grind, one observation operator (matched 40 g endpoint). They differ only in transport freedom:

| | transport rate | amplitude term |
|---|---|---|
| **SHARED** | one multiplier per **variety**, shared across all four species | one per (species, variety) |
| **INDEPENDENT** | one multiplier per **(species, variety)** | one per (species, variety) |

**The amplitude is free in both.** That is the design decision that answers the candidate's
strongest alternative — *"the apparent species difference is a measurement-lineage difference
between the assays, not chemistry"*. The amplitude is a **condition-independent multiplicative
scale** on the prediction; a solid-inventory difference, an assay calibration scale and a
multiplicative model error all enter identically and this screen **cannot distinguish them**.
Making it free in both models means the comparison is blind to all three by construction, so
anything that survives is *condition-dependent* structure.

**Why the amplitude can be fitted without re-solving.** The solver's output is *exactly* linear
in `c_s0` — verified to ~1e-6, the solver's own tolerance: scaling `c_s0` by λ scales the liquid
state by λ and leaves the normalised solid state untouched. So one unit-amplitude solve per
(rate, condition, species) suffices and the optimum is a weighted-least-squares closed form.
That, plus the analytic RSD sweep, is what keeps this inside a cheap-screen budget.

## Predeclared before any fit

- **Held-out split.** Train on **p = 6 and 12 bar**; hold out **p = 9 bar**, at every temperature
  and in both varieties. 12 training / 6 held-out conditions. The *interior* pressure is held
  out, so this is interpolation rather than extrapolation.
- **Base rate domain.** `geomspace(0.15, 6.5, 15)` — **expanded automatically** when a decisive
  optimum lands on a boundary (see below).
- **The materiality criterion** — thresholds unchanged by the correction:

  | arm | test | reads |
  |---|---|---|
  | **C1** exceeds noise | `Z_shared > 1.0` | shared state's RMS standardised held-out residual exceeds one σ |
  | **C2** species-specific | SD across species of per-species mean `z` > 1.0 | separates *a species problem* from *a shared model-form problem* |
  | **C3** reduced by per-species fits | `Z_independent ≤ 0.70 × Z_shared` | per-species freedom removes ≥30 % of the RMS held-out residual |

  **SURVIVE iff C1 ∧ C2 ∧ C3.**

## The uncertainty problem — and what actually establishes robustness

The campaign retains **per-condition replicate RSD for total solids only**. For caffeine /
trigonelline / CGA the source gives a *global* range and no per-cell value — MANIFEST
`angeloni2023/bioactives`: `%RSD 0.3-19.7 (in card, not per-cell)`.

### The withdrawn claim

The first version asserted that **C3 is scale-free** in the assumed bioactive RSD, and tested it
by uniformly rescaling already-computed `z` values. That test was **vacuous**: it is not the
perturbation the screen performs. Changing the bioactive RSD changes the weight of the three
bioactives *relative to the measured, fixed* total-solids weights, and that reweighting **refits
the shared model**. The evidence it does: the selected shared rate for Arabica moves
`0.44 → 14.93` and for Robusta `26.0 → 0.44` across the band.

Inferring invariance over an interval from its two endpoints was equally unsupported when the
model is refitted inside it.

### What replaced it — an exact finite-grid argument

Write `x = (100/RSD)²`. Then:

1. the fitted **amplitude is x-independent** (the common factor cancels in the WLS ratio);
2. each bioactive's training SSE at a fixed rate is exactly **`x · a_s`**; total solids' is a
   **constant `b`**;
3. so the shared rate is `argmin` over a family of **straight lines in x** — its selection
   changes only at finitely many **breakpoints**;
4. the **independent per-species rates are provably x-independent** (a common positive factor
   cannot move an argmin) and do not move across the band at all;
5. on a fixed-selection interval `Z² = (x·D + E)/N`, so **C1 is monotone** and **C3 is a Möbius
   function of x, hence also monotone** — extrema at the interval endpoints;
6. **C2** is the square root of a *quadratic* in `u = √x`, so its extremum can be interior — each
   interval's **vertex** is evaluated.

Evaluating both band endpoints, both sides of every breakpoint, and every C2 vertex therefore
bounds each criterion **exactly over the continuous band**.

### Rate-domain robustness

A decisive optimum on the grid boundary is a censored answer. Predeclared policy: multiply the
offending bound by **4**, add **5** log-spaced points, refit everything, and stop when the
decisive optima are interior, or the worst-case C3 moves by less than **0.01**, or after **4**
rounds.

## Result — **RETIRE**

**24 breakpoints → 25 fixed-selection intervals → 51 evaluated points. 1440 PDE solves.**

**C3 is never satisfied anywhere on the band.** Best (smallest) ratio at any evaluated point:
**1.0008**, against the 0.70 threshold — and above 1 everywhere, i.e. per-species fits are
slightly *worse* out of sample at every admissible setting. `C3_ever_satisfied: false`.

Sample of the interval table (full version in `result.json → sweep.intervals`):

| assumed bioactive RSD | shared rate (Ara / Rob) | C3 ratio range |
|---|---|---|
| 12.26 – 19.70 % | 0.44 / 26.0 | 1.0008 – 1.0020 |
| 6.42 – 7.14 % | 0.576 / 1.692 | 1.2925 – 1.3254 |
| 2.69 – 3.42 % | 1.292 / 0.576 | 1.0984 – 1.1498 |
| 0.30 – 0.664 % | 14.93 / 0.44 | 1.0096 – 1.0147 |

### Rate-grid robustness evidence

| round | rates | max rate | decisive optima at an edge | worst-case C3 | Δ vs previous |
|---|---|---|---|---|---|
| 0 | 15 | 6.5 | 4 | 1.00064 | — |
| 1 | 20 | 26.0 | 3 | 1.00085 | **0.00021** |

Stopped by the **convergence tolerance**, not by interiority — quadrupling the ceiling moved the
worst-case C3 by 2 × 10⁻⁴. Three optima remain censored at the upper bound and that is recorded
in `result.json`, not hidden. The independent per-species rates span **0.257 – 26.0**, a 100×
range, and still buy no held-out improvement.

### The amplitude term (corrected metric and corrected language)

The free per-species amplitude reduces the **RMS standardised held-out residual** by
**44 % – 87 %**, depending on the assumed bioactive RSD — reported at all 26 evaluated settings
in `result.json → amplitude_diagnostic`. The metric is
`1 − RMS(z_fitted) / RMS(z_fixed)`; the first version mislabelled it "a fraction of the raw
residual" and quoted a single value (76.1 %) as if it were RSD-independent.

**The amplitude is a condition-independent multiplicative scale.** It may represent a solid
inventory difference, an assay calibration scale, **or a multiplicative model error**, and this
screen cannot separate them. The first version's "the species differ in inventory, not in
transport" is **withdrawn**.

**Table 7 comparison, qualified:** of the **4 species-matched cells** (caffeine, trigonelline ×
2 varieties), **3** have a fitted amplitude closer to angeloni Table 7 than to pannusch Table 2.
5CQA is not species-matched (Table 7 reports **total CQA**) and there is no Table 7 inventory for
the total-solids proxy; both are excluded from the count.

## Figure

`figures/primary.png` — four panels. **A**: the exact C3 sweep across the declared band, with
all 24 breakpoints marked. **B**: the rate-grid expansion evidence. **C1/C2**: held-out
standardised residuals at both retained endpoints, shared and independent fits overlaid — the
two marker sets sit on top of each other almost everywhere, and *that coincidence is the
result*. **D**: the amplitude diagnostic at every evaluated setting.

Not registered in the viz layer, for the same reason as I-040 and I-010: a screen artifact, not
a mechanism render bound to a VizSpec fidelity ceiling, and the IF-5 decision forbids extending
a governed registry before Wave 1 reports.

## Corpus warnings

**None of the 32 build warnings is load-bearing for this screen**, and none was repaired.
`docs/cards/angeloni2023.md` resolves with no `TEMPLATE_DEVIATION`, as does
`docs/cards/pannusch2024.md`. All 32 deferred — see
[`../../IF5_HUMAN_TRIAGE_DECISION.md`](../../IF5_HUMAN_TRIAGE_DECISION.md) §7.

## Scope — what this screen did NOT do

- It did **not** score any campaign other than angeloni2023.
- It did **not** upgrade any evidence label. `pannusch2024.solver` remains
  `post_fit_reconstruction`; angeloni2023 remains a data-only intake.
- It did **not** claim the model predicts angeloni. It does not; the blind gap is `ANALYSIS_
  transfer`'s standing result. This screen compares two *fits* on the same held-out points.
- It did **not** attempt to resolve the inventory↔rate non-identifiability. That is gap G6 and
  needs time-resolved data or an independent inventory measurement.
- It did **not** identify what the free amplitude term physically is. Inventory, assay scale and
  multiplicative model error are indistinguishable to this screen.
- It did **not** run any candidate outside Wave 1, and did no novelty research.

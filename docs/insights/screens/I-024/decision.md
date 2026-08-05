# I-024 Cheap Screen Decision

```
CHEAP_SCIENTIFIC_SCREEN
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

> **Corrected 2026-08-04.** The first version claimed C3 was *scale-free* in the assumed
> bioactive RSD, and inferred whole-band invariance from **two** endpoints. Neither was
> supported. Changing the bioactive RSD reweights the three bioactives against the **measured**
> per-condition total-solids weights, which **refits the shared model** — observably, the
> selected shared rate moves. Both claims are replaced by an exact finite-grid breakpoint
> argument plus rate-grid expansion. Several explanatory statements were also over-reaching and
> are corrected below. **The decision remains RETIRE, but it is now earned rather than
> asserted.**

## Question

Can one shared hydraulic/transport state explain the Angeloni species observations under one
model and one observation operator — or do the per-species held-out residuals carry structure a
single kinetic story cannot absorb?

## Evidence unit

The **angeloni2023 campaign only**: bioactives + total_solids, granulometry O, on-grid, both
varieties. 18 conditions × 4 species; **12 training conditions** (6 and 12 bar), **6 held out**
(9 bar, the interior pressure — predeclared). Maille, Ellero, Khamitova, Pannusch/Schmieder
post-fit evidence and angeloni lipids are excluded from scoring; reasons in
`result.json → evidence_unit.excluded_evidence`.

## Method

Two models, one hydraulic state each, differing only in transport freedom: one shared rate per
variety vs one rate per species. **A per-species amplitude is free in both.** Levels are fitted
in closed form because the solver is exactly linear in `c_s0`. Predeclared: the split, the base
rate grid, and the C1/C2/C3 thresholds. Full method in [`README.md`](README.md).

### What replaced the withdrawn scale-free claim

Writing `x = (100/RSD)²`, the problem decomposes exactly:

- the fitted **amplitude is x-independent** — the common factor cancels in the weighted
  least-squares ratio;
- each bioactive's training SSE at a fixed rate is therefore **exactly `x · a_s`**, and total
  solids' is a **constant `b`** (its weights come from the measured per-condition RSD and carry
  no `x`);
- so the shared rate is `argmin` over the grid of a family of **straight lines in x**, and its
  selection changes only at finitely many **breakpoints**;
- the **independent per-species rates do not depend on x at all** — a common positive factor
  cannot move an argmin — so they are constant across the entire band;
- on any fixed-selection interval `Z² = (x·D + E)/N`, so **C1 is monotone in x** and **C3, a
  ratio of two such, is a Möbius function of x and therefore also monotone** — their extrema sit
  at the interval endpoints. **C2** is the square root of a *quadratic* in `u = √x`, so its
  extremum can be interior; each interval's **vertex** is evaluated too.

Evaluating both band endpoints, both sides of every breakpoint, and every interval's C2 vertex
therefore bounds each criterion **exactly over the continuous band** — this is the preferred
exact method, not a sample.

## Result — the band sweep

**24 shared-rate breakpoints → 25 fixed-selection intervals → 51 evaluated points.**

The selected shared rate **changes at discrete breakpoints** across the band — it is an argmin
over a finite grid, so it is piecewise constant, not a continuously varying optimum. That it
changes at all is precisely why two endpoints were never sufficient. Examples:

| assumed bioactive RSD | shared rate (Arabica / Robusta) | C3 ratio range |
|---|---|---|
| 12.26 – 19.70 % | 0.44 / 26.0 | 1.0008 – 1.0020 |
| 6.42 – 7.14 % | 0.576 / 1.692 | 1.2925 – 1.3254 |
| 4.58 – 4.68 % | 0.754 / 0.754 | 1.2401 – 1.2475 |
| 2.69 – 3.42 % | 1.292 / 0.576 | 1.0984 – 1.1498 |
| 0.30 – 0.664 % | 14.933 / 0.44 | 1.0096 – 1.0147 |

Full table in `result.json → sweep.intervals`.

**C3 is never satisfied anywhere on the band.** The smallest (best) ratio achieved at any
evaluated point is **1.0008**, against a **0.70** threshold — and it is above 1 everywhere,
meaning independent per-species fits are *worse* out of sample at every admissible uncertainty
setting, not merely no better. `C3_ever_satisfied: false`; `any_point_survives: false`.

## Rate-grid robustness

A decisive optimum on a grid boundary is a censored answer. The predeclared policy expands the
offending bound by ×4 with 5 new log-spaced points, refits everything, and stops when the
decisive optima are interior, or when the worst-case C3 moves by less than 0.01, or after 4
rounds.

| round | rates | max rate | decisive optima at an edge | worst-case C3 | Δ vs previous |
|---|---|---|---|---|---|
| 0 | 15 | 6.5 | 4 (shared ×2, independent ×2) | 1.00064 | — |
| 1 | 20 | 26.0 | 3 | 1.00085 | **0.00021** |

**Stopped by the convergence tolerance**, not by interiority: quadrupling the rate ceiling moved
the worst-case C3 by 2 × 10⁻⁴, two orders of magnitude below the 0.01 tolerance. Three optima
remain censored at the upper bound (`Arabica 5CQA`, `Robusta tds`, and the Robusta shared rate at
the low-x end) and that is recorded rather than hidden. **The remaining censoring was not
decision-changing under the predeclared 0.01 convergence policy**: one ×4 expansion moved the
worst-case C3 by ≈ 0.000210, the final minimum C3 is ≈ 1.0008, and the survival threshold is
0.70. Whether a still larger ceiling would eventually change the verdict was not tested — the
policy stopped first, by design, and that is a bound on this screen's evidence rather than a
proof about the unbounded rate domain.

## Primary figure

[`figures/primary.png`](figures/primary.png) — **A**: the exact C3 sweep across the band with
all 24 breakpoints marked. **B**: the grid-expansion evidence. **C1/C2**: held-out standardised
residuals at both retained endpoints, shared and independent fits overlaid. **D**: the amplitude
diagnostic at every evaluated setting.

## Adversarial check

The strongest attempt to overturn this RETIRE is that **the screen never gave per-species freedom
a fair chance**. Four probes:

1. **"The rate grid was censored."** It was, at round 0 — and that is exactly why the grid was
   expanded. After expanding to 26.0 the worst-case C3 moved by 0.0002. The independent
   per-species rates span 0.257 – 26.0, a **100× range**, and still produce no held-out
   improvement.
2. **"The band was only sampled."** It is not sampled; it is covered exactly. C1 and C3 are
   provably monotone between breakpoints and C2's only interior extremum is its vertex, all of
   which are evaluated. There is no point in the continuous 0.3–19.7 % band at which C3 could be
   satisfied without contradicting monotonicity.
3. **"The shared model was flattered by the reweighting."** The opposite: the shared rate is
   refitted at every setting, so the shared model gets the *best* rate available at each point
   of the band, and the independent model still fails to beat it.
4. **"The held-out split was easy."** The interior pressure is the easiest fair split, which
   depresses `Z_shared` and therefore makes C3 *easier* to satisfy, not harder. C1 nonetheless
   passes at both endpoints — the shared state does not fit within uncertainty either.

## Strongest alternative explanation

*"The apparent species difference is a measurement-lineage difference between the assays, not
chemistry."*

**Addressed, and the corrected statement is weaker than the first version's.** The free amplitude
is a **condition-independent multiplicative scale**. It reduces the RMS standardised held-out
residual by **44 % – 87 %** depending on the assumed bioactive RSD (`result.json →
amplitude_diagnostic`, evaluated at all 26 settings). But an amplitude term may represent a solid
inventory difference, an assay calibration scale, **or a multiplicative model error**, and this
screen cannot separate them. The first version's "inventory, not transport" is not supportable
and has been withdrawn.

**Table 7 comparison, properly qualified — and setting-dependent.** There are **4
species-matched cells** (caffeine and trigonelline × two varieties). 5CQA is **not**
species-matched — Table 7 reports **total CQA** — and there is **no** Table 7 inventory for the
aggregate total-solids proxy; both are excluded from the count rather than folded into a claim of
universal recovery.

The fitted amplitude depends on which shared rate is selected, which depends on the assumed
bioactive RSD, so the count is **not** a fixed property. Across all **25** distinct shared-rate
selections on the band it ranges **3 to 4** of 4 — it is **not constant**. At the recorded
evaluation setting (RSD 0.300 %, shared rates Arabica 14.933 / Robusta 0.440) it is **3 of 4**.
That provenance is stored in `result.json → amplitude_vs_table7.evaluated_at_rsd_pct` and
`.evaluated_at_shared_rates`, with the full cross-setting range under `.setting_dependence`. Do
not quote a single figure as setting-independent.

## Decision

**RETIRE.**

The candidate's original rule, applied to the corrected analysis: *"RETIRE if residuals are
unstructured, or the structure is common to all species (a shared model-form problem, not a
species one)."* The decisive finding is that **per-species transport freedom does not improve
held-out prediction anywhere in the retained uncertainty band** — C3 fails at all 51 evaluated
points across 25 intervals, by a margin (ratio ≥ 1.0008 vs a 0.70 threshold) that no admissible
RSD, and no rate-grid expansion, comes close to closing.

`NEEDS_NEW_DATA` was live and is **not** triggered: it would require the *verdict* to change
inside the band, and it does not. `SURVIVE` would require C3 to hold somewhere; it holds nowhere.

This is **not** preserved from the first version's endpoint result — the endpoints happened to
agree with the sweep, but the sweep is what establishes it.

## Why

1. **The whole-cup endpoint does not identify a benefit from species-specific rate freedom.** A
   100× spread in fitted per-species rate produces no held-out improvement. That is a statement
   about what this observable can resolve, not about whether species-specific transport exists.
2. **A condition-independent amplitude explains a large and RSD-dependent share of the
   residual** (44–87 %). Whatever that amplitude is — inventory, assay scale, or multiplicative
   model error — it is not condition-dependent transport structure.
3. **At the lenient end of the band the residual is not even species-specific**: the
   between-species spread falls to 0.65, below the 1 σ C2 threshold.

## Claim ceiling

**The strongest thing this result licenses anyone to say:**

> On the angeloni2023 campaign, scored at held-out 9-bar conditions under one model
> (`pannusch2024.solver`) and one observation operator (matched 40 g endpoint), giving each
> measured species its own transport rate does not improve held-out prediction over a single
> shared rate at any bioactive replicate RSD in the campaign's declared 0.3–19.7 % range, after
> expanding the rate grid until that conclusion stopped moving. A free per-species amplitude
> reduces the RMS standardised held-out residual by 44–87 % depending on that assumed RSD.

It licenses **nothing** beyond that. In particular it does **not** say:

- that species-specific extraction kinetics do not exist. This campaign, at a cup-integrated
  endpoint, does not identify a benefit from modelling them;
- **that inventory rather than transport is what separates the species.** The first version said
  so; that statement is **withdrawn**. The amplitude term is not identified as inventory — it is
  equally consistent with an assay calibration scale or a multiplicative model error;
- that the shared transport state is correct. `Z_shared > 1` throughout: the shared state does
  not fit within measurement uncertainty either. The two models are compared to each other, and
  neither is validated;
- that the fitted rates mean anything. Three decisive optima remain censored at the grid
  boundary and the shared rate moves 0.44 → 14.9 across the band;
- that any evidence label has changed. `pannusch2024.solver` remains `post_fit_reconstruction`,
  angeloni2023 remains a data-only intake, and gap **G6** remains open.

The ceiling may not exceed the weakest evidence consumed. The weakest input is the **absent**
solute-specific bioactive replicate RSD, so the ceiling is a **comparative statement between two
fits, bounded over an uncertainty range**, not a statement about coffee chemistry.

## Next action

Record the retirement in [`../../RETIRED_CANDIDATES.md`](../../RETIRED_CANDIDATES.md) with its
reopen condition.

Note the reopen condition is **not** solute-specific RSD. The corrected analysis shows C3 fails
across the whole declared band, so better bioactive uncertainty would sharpen C1 and C2 but could
not change the decisive arm. What would change it is a **fraction-resolved** observable —
`ANALYSIS_transfer` already shows fraction-resolved objectives retain rate information the cup
discards — and that is a different candidate needing data this campaign does not have.

No deep screen. No novelty research. Triage rule 1.

## Reproduction

```
python -m puckworks.analysis.screen_i024_common_state
pytest tests/test_screen_i024.py -v
```

## Source commit

- Corpus snapshot the candidate was generated at: `c1b7d79e8f6800df16ad4fc195d45bf156e4ec8b`
- Foundation merge / branch base: `56060e5b589132c496c432fa09e61efea305d5cf`
- Branch: `insights/if5-wave1-cheap-screens`

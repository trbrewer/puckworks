# I-010 Cheap Screen Decision

```
CHEAP_SCIENTIFIC_SCREEN
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

## Question

Does substituting one declared closure at a time materially change held-out predictions from
`pannusch2024.solver`?

## Evidence unit

`angeloni2023` — bioactives + total_solids, granulometry O, on-grid, both varieties.
**18 conditions × 4 species = 72 held-out points.** MANIFEST-labelled *independent* ("different
machine/coffee/basket than pannusch fit or cameron calibration"), never used to fit the
closures. The closures' own fit target (Schmieder kinetics) is excluded as circular.

## Method

Path established from source; everything frozen; one closure swapped at a time from a declared
in-repo alternative; no-refit comparison first; uncertainty propagated; materiality predeclared.
Full method and the frozen configuration in [`README.md`](README.md).

## Result

**The path is real.** `solver.py:30` imports `closures as pc` and calls `sherwood_h` and
`vant_hoff_K` directly; the other three closures reach the consumer only through `sherwood_h`.
The artifact enters each solve as exactly **three scalars — `h1`, `h2`, `K`**.

**No admissible swap is material.**

| substitution | median abs. rel. change over 72 points | vs U = 4.700 % |
|---|---|---|
| `vant_hoff_K` → romancorrochano Arrhenius T-law | **2.968 %** | 63 % of U — below |
| `diffusion_coeff` → Stokes-Einstein T-law | **0.831 %** | 18 % of U — below |
| `water_density` → telisromero2001 at `X_w = 1` | **0.012 %** | 0.3 % of U — below |
| `water_viscosity` → TR2001 at `X_w = 100 %` | 8.885 % | above U, but **excluded** |
| `sherwood_h` | not run | **unsubstitutable** |

**The artifact is not consumed outside its declared range.** T 88–98 °C against a declared
80–98; Q 1.045–2.344 mL/s against a declared 1–3. The candidate's second SURVIVE arm does not
fire either.

**Recalibration branch not triggered** — the brief conditions it on a material no-refit effect,
and there is none among the admissible swaps.

## Primary figure

[`figures/primary.png`](figures/primary.png) — held-out concentration per species and condition
under each closure, over the common validity range, with the measured points and their replicate
band. No-refit only; nothing is fitted to these points, so there is no recalibrated curve to
distinguish.

## Adversarial check

The strongest attempt to make the RETIRE go away is to ask **whether the screen was rigged to
find nothing** — by choosing swaps too weak to move anything. Three independent answers:

1. **The swaps are not weak; the consumer is insensitive.** The K(T) substitution changes the
   partition constant's temperature law from one that *decreases* with T (pannusch, γ<0 for
   caffeine/trigonelline/5CQA) to one that *increases* with it (romancorrochano). Those two
   closures are already on record as disagreeing on the **sign** of dK/dT
   (`gate_g4_temperature_sensitivity`). Over 88→98 °C that is roughly an 8 % swing in K. It
   moves the held-out cup by 2.97 % — real, visible in the figure, and still below the
   campaign's own replicate noise.
2. **A deliberately excessive swap was run, and it is reported.** Driving the viscosity closure
   to TR2001's `X_w = 100 %` extrapolation — a −44 % change in μ — moves the held-out
   prediction by 8.9 %, i.e. **above U**. So the consumer is *not* insensitive to everything;
   it is insensitive to every change an admissible alternative source actually produces. That
   distinction is what the decision turns on, and it is the honest reading.
3. **The uncertainty floor is not inflated.** The numerical component is 0.0001 %, so U is
   essentially the campaign's own measured replicate spread. Had U been set from the lipid RSD
   (12.55 %) instead, the conclusion would be unchanged and weaker; had it been set from the
   *low* end of the source's global bioactive band (0.3 %), the K(T) swap would have been
   "material" — but 0.3 % is the best cell in a 0.3–19.7 % range and using it as a campaign
   floor would be indefensible. The choice was predeclared and its sensitivity is stated here
   rather than after the fact.

## Strongest alternative explanation

The generated alternative — *"nothing consumes this artifact at all, or the named same-stage
component is insensitive to it, so portability is moot"* — splits in two, and the screen
resolves both halves in opposite directions.

- *"Nothing consumes it"* — **refuted.** The path is a direct import, established in step 1.
- *"The consumer is insensitive"* — **confirmed, and this is the finding.** The reason is
  structural rather than accidental: the whole artifact is funnelled into three scalars, and the
  scored observable is a cup-integrated endpoint over a near-exhausted bed, which absorbs
  changes in transfer rate. The `h ~ D^(2/3)` exponent damps the diffusion swap further.

A third alternative worth naming, because it would invalidate the result if true: *the two
closures being swapped might not be the same quantity, so the null is a category error rather
than an insensitivity.* Addressed by construction — the swaps are **anchored** at pannusch's own
`Tref`, so each substitution changes only the declared temperature law and preserves the
convention and the reference value. What is being compared is like for like.

## Decision

**RETIRE.**

The candidate's rule, applied without revision: *"RETIRE if a consuming path exists and the
consuming result is insensitive to the swap across the used range."* A path exists. The result
is insensitive to every admissible one-closure swap, by a factor of 1.6× to 400× under the
predeclared criterion. The artifact is driven strictly inside its declared range, so the second
SURVIVE arm does not fire either.

`NEEDS_NEW_DATA` was available — *"the consumer path exists but no non-circular scoring unit is
available"* — and was **not** triggered: angeloni is manifest-labelled independent and was never
used to fit the closures.

## Why

1. **The interface is three numbers wide.** Five declared closures, and every one of them
   reaches the consumer only as `h1`, `h2`, `K`. Portability of a calibration artifact is
   bounded by how much of it the consumer can actually see, and here that is very little.
2. **The scored observable integrates the difference away.** The observation operator is a
   cup-integrated endpoint at a matched 40 g. Rate-scale changes shift *when* solute leaves the
   grain, not how much is available to leave; by the endpoint the bed is near-exhausted and the
   difference has largely closed.
3. **The measured campaign is noisier than the closure disagreement.** A median 4.70 % replicate
   RSD sits above the 2.97 % that the sign-disagreeing K(T) closures produce. Even a real,
   documented, sign-level disagreement between two partition closures is not resolvable against
   this campaign at this observable.

### Two limitations recorded, neither changing the decision

- **The one closure that would matter is the one that could not be tested.** μ(T) is the most
  influential closure on the path (it enters Re, Sc and Wilke-Chang D), and the corpus holds no
  second **pure-water** viscosity correlation declared over 88–98 °C. The bound run here says a
  μ error of TR2001-extrapolation size would move the held-out cup by ~8.9 %, above U. So the
  RETIRE is properly read as: *portable with respect to every alternative the corpus can supply*
  — not *portable with respect to all sources*.
- **`sherwood_h` is unsubstitutable.** The card states its fitted parameters "lack physical
  meaning and generality", which is precisely a portability concern, and the corpus offers
  nothing to swap it against. Recorded as a gap, not silently omitted.

Both are **data/corpus gaps**, not analysis gaps, which is why they do not convert this into
`NEEDS_NEW_DATA`: the candidate's rule routes there only when no non-circular scoring unit
exists, and one does.

## Claim ceiling

**The strongest thing this result licenses anyone to say:**

> Under one frozen configuration of `pannusch2024.solver` (centre grind, Darcy p→flow map,
> pannusch Table 2 inventory, matched-40 g endpoint), scored on 72 held-out `angeloni2023`
> points, substituting any one of `pannusch2024.closures`'s temperature-dependent closures for
> the alternative source the repository declares moves the predicted cup concentration by less
> than the campaign's own median replicate RSD.

It licenses **nothing** beyond that. In particular it does **not** say:

- that `pannusch2024.solver` *predicts* angeloni. It does not — the blind gap against the
  measured points is large and clearly visible in the figure, and `ANALYSIS_transfer` is the
  standing authority on that. This screen measures **sensitivity to a closure swap**, not
  accuracy;
- that the closures are portable in general. They are portable *with respect to the alternatives
  this corpus contains*, over this configuration, at this observable;
- anything about μ(T) portability, which was not testable;
- anything about `sherwood_h`, which was not substitutable;
- that any evidence label has changed. `pannusch2024.closures` remains `code_verification`;
  `pannusch2024.solver` remains `post_fit_reconstruction`. A screen cannot promote a rung and
  this one did not.

The ceiling may not exceed the weakest evidence consumed. The weakest input here is the p→flow
map — an assumption with a single physical anchor and granulometry O only — so the ceiling is a
**configuration-conditional sensitivity statement**, not a property of the closures.

## Next action

Record the retirement in [`../../RETIRED_CANDIDATES.md`](../../RETIRED_CANDIDATES.md) with its
reopen condition.

Two things route onward and are **not** part of this screen's output:

- The missing pure-water μ(T) alternative is a **corpus gap**. It belongs with the G10 liquor-
  rheology thread, which already tracks inter-source viscosity spread, not with this candidate.
- The three-scalar interface finding is exactly the kind of edge the **candidate-readiness**
  lane (I-013/I-014/I-015) needs recorded on a card. Worth carrying there.

No deep screen. No novelty research. Triage rule 1.

## Reproduction

```
python -m puckworks.analysis.screen_i010_closure_portability
pytest tests/test_screen_i010.py -v
```

## Source commit

- Corpus snapshot the candidate was generated at: `c1b7d79e8f6800df16ad4fc195d45bf156e4ec8b`
- Foundation merge / branch base: `56060e5b589132c496c432fa09e61efea305d5cf`
- Branch: `insights/if5-wave1-cheap-screens`

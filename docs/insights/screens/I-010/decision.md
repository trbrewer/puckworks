# I-010 Cheap Screen Decision

```
CHEAP_SCIENTIFIC_SCREEN
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

> **Corrected 2026-08-04.** The first version of this screen used the median total-solids
> replicate RSD (4.70 %) as the decision authority for **all four** scored outputs — including
> the three named bioactives, whose replicate uncertainty the campaign does **not** retain — and
> returned RETIRE. That was an invented uncertainty for three of the four outputs. Each output is
> now judged against its own retained uncertainty, and the disposition changes to
> **NEEDS_NEW_DATA**. The producer→consumer path, the frozen configuration, the admissible
> substitutions and the no-refit predictions are unchanged and are reproduced by a fresh run.

## Question

Does substituting one declared closure at a time materially change held-out predictions from
`pannusch2024.solver`?

## Evidence unit

`angeloni2023` — bioactives + total_solids, granulometry O, on-grid, both varieties.
**18 conditions × 4 outputs = 72 held-out points.** MANIFEST-labelled *independent*, never used
to fit the closures. The closures' own fit target (Schmieder kinetics) is excluded as circular.

## Method

Path established from source; everything frozen; one closure swapped at a time from a declared
in-repo alternative; no-refit comparison only; **each output evaluated against its own retained
uncertainty**. Full method and the frozen configuration in [`README.md`](README.md).

## Result

### The path is real, and it is narrow

`solver.py:30` imports `closures as pc` and calls `sherwood_h` and `vant_hoff_K` directly; the
other three closures reach the consumer only through `sherwood_h`. The artifact enters each solve
as exactly **three scalars — `h1`, `h2`, `K`**. Unchanged from the first version and not in
dispute.

### Uncertainty authority, per output

| output | retained uncertainty | authority |
|---|---|---|
| `tds` (total solids) | **measured per-condition RSD**, median **5.30 %** over these 18 conditions | a real threshold |
| `caffeine` | **none per cell** — declared range 0.3–19.7 % only | evaluated at both ends |
| `trigonelline` | **none per cell** — declared range 0.3–19.7 % only | evaluated at both ends |
| `5CQA` | **none per cell** — declared range 0.3–19.7 % only | evaluated at both ends |

Source, verbatim: `angeloni2023/bioactives` uncertainty cell reads `%RSD 0.3-19.7 (in card, not
per-cell)`; `angeloni2023/total_solids_lipids_rsd` records `caffeine/trigonelline/CGA
solute-specific RSD NOT recovered … raw replicates still owed`.

### The decisive table

Median (and max) absolute relative change in the held-out prediction, per output, per
substitution. **Outputs are not pooled** — they do not share an uncertainty authority.

| substitution | caffeine | trigonelline | 5CQA | **tds** |
|---|---|---|---|---|
| **K(T) → Arrhenius T-law** | 3.171 % (5.539) | 3.061 % (5.416) | 3.138 % (5.581) | 1.709 % (3.006) |
| | `CHANGES` | `CHANGES` | `CHANGES` | **`IMMATERIAL`** |
| **D(T) → Stokes-Einstein T-law** | 0.946 % (1.674) | 0.663 % (1.247) | 0.899 % (1.665) | 0.770 % (1.411) |
| | `CHANGES` | `CHANGES` | `CHANGES` | **`IMMATERIAL`** |
| **ρ(T) → telisromero2001** | 0.018 % (0.055) | 0.006 % (0.020) | 0.009 % (0.030) | 0.009 % (0.030) |
| | `IMMATERIAL` | `IMMATERIAL` | `IMMATERIAL` | **`IMMATERIAL`** |
| *μ(T) → TR2001 @ X_w=100 % — **excluded**, out of its own range* | *13.661 %* | *6.136 %* | *9.691 %* | *7.948 %* |
| | *`CHANGES`* | *`CHANGES`* | *`CHANGES`* | *`MATERIAL`* |
| *`sherwood_h` — **unsubstitutable**, no alternative in the corpus* | — | — | — | — |

`CHANGES` = `CHANGES_WITHIN_RANGE`: material at 0.3 %, immaterial at 19.7 %.

**Fraction of conditions exceeding the threshold** is in `result.json` per cell
(`frac_conditions_exceeding_low_end` / `_high_end` for the bioactives,
`n_conditions_effect_exceeds_own_rsd` for tds — **0 of 18** for every admissible swap).

### Validity range

The artifact is driven at **T 88–98 °C** (declared 80–98) and **Q 1.045–2.344 mL/s** (declared
1–3): strictly **inside** its declared range. The second SURVIVE arm does not fire.

### Recalibration branch

Not triggered — no admissible swap is material throughout, which is the condition the brief sets.

## Primary figure

[`figures/primary.png`](figures/primary.png) — two panels. Top: held-out concentration per output
and condition under each closure, with each output's measured points carrying the uncertainty it
actually has (a measured bar for total solids; the full declared 0.3–19.7 % range drawn as a band
for the three bioactives, because no per-cell value exists). Bottom: the decisive panel — each
swap's median and maximum held-out effect against that output's own authority.

## Adversarial check

The corrected question is no longer "is the consumer insensitive" but "**can this campaign tell**".
Four attempts to break the NEEDS_NEW_DATA:

1. **"Total solids settles it — that output has a real uncertainty and every swap is
   immaterial."** True, and it is reported as a definite sub-result: 0 of 18 conditions exceed
   their own measured RSD for any admissible swap. But total solids is an *aggregate* proxy, and
   the closures are per-solute (`vant_hoff_K` takes a solute-specific `K_ref`, `gamma`;
   `diffusion_coeff` a solute-specific molar volume). Generalising an aggregate result to the
   named solutes is exactly the inference the swap effects contradict: K(T) moves tds by 1.71 %
   but the bioactives by ~3.1 %, nearly twice as much.
2. **"Pick a defensible single bioactive RSD."** Explicitly forbidden and rightly so — every
   available choice (midpoint 10 %, the total-solids 5.30 %, the best cell 0.3 %) is a number
   selected after seeing that the effects land at ~1–3 %, and each one decides the screen on its
   own. The band is the retained evidence; collapsing it *is* the defect being corrected.
3. **"The effects are small in absolute terms, so it hardly matters."** A 3 % shift in a
   predicted cup concentration is *not* obviously below a bioactive HPLC assay's replicate
   spread — the source's own range reaches 19.7 %, and its low end reaches 0.3 %. Whether 3 %
   is signal or noise is precisely the unknown.
4. **"The excluded μ(T) bound is material even for total solids, so the answer is really
   SURVIVE."** No — it is inadmissible by construction, because TR2001 at `X_w = 100 %` is being
   driven far outside *its own* declared 76–90 % range, so the 7.9 % it produces measures
   TR2001's extrapolation error. It is reported because it bounds what a genuine μ error would
   do, not because it counts.

## Strongest alternative explanation

*"Nothing consumes this artifact at all, or the consumer is insensitive to it."*

- **"Nothing consumes it" — refuted.** Direct import, established in step 1.
- **"The consumer is insensitive" — no longer supportable as stated.** It is supportable for
  **total solids only**, and only against that output's measured replicate RSD. For the three
  named bioactives the screen cannot distinguish insensitivity from an effect the campaign
  simply cannot resolve.

The alternative that now matters most is a third one: *the three-scalar interface makes any
closure difference structurally small*. The evidence is consistent with it — ρ(T) is immaterial
everywhere by three orders of magnitude — but it is not established for K(T) and D(T), whose
effects sit inside the unresolvable band.

## Decision

**NEEDS_NEW_DATA.**

By the fixed classification:

- **SURVIVE** requires an admissible swap material *throughout* the applicable range, or
  consumption outside the declared range. Neither holds — no admissible cell is
  `MATERIAL_THROUGHOUT`, and the artifact stays inside its range.
- **RETIRE** requires *every* admissible swap immaterial *throughout* for *every* output. It does
  not hold: 6 (substitution, output) cells are `CHANGES_WITHIN_RANGE` — K(T) and D(T) on each of
  the three bioactives.
- **NEEDS_NEW_DATA** is what remains, and it is the honest answer.

**The missing evidence, named:** solute-specific replicate RSD for caffeine, trigonelline and
CGA in the `angeloni2023` campaign. `angeloni2023/MANIFEST_UNCERTAINTY.md` already records these
as owed ("raw replicates still owed"), so this is a request for data the campaign has and has not
released, not a new experiment.

**What would resolve it:** any solute-specific RSD **above ~3.2 %** retires the candidate (every
admissible effect falls below it); any value **below ~0.7 %** makes K(T) and D(T) material on all
three bioactives and the candidate survives; a value between them splits by substitution.

## Why

1. **Three of the four scored outputs have no retained replicate uncertainty at all.** The
   campaign published a global range, not per-cell values, and the range spans a factor of 65.
2. **The measured effects land inside that range.** K(T) at ~3.1 % and D(T) at ~0.9 % are above
   0.3 % and below 19.7 %. There is no reading of the retained evidence that settles them.
3. **The one output that *is* resolved gives a clean negative** — 0 of 18 conditions exceed their
   own measured RSD under any admissible swap — but it is an aggregate proxy and the closures are
   per-solute, so it does not transfer.

## Claim ceiling

**The strongest thing this result licenses anyone to say:**

> Under one frozen configuration of `pannusch2024.solver`, scored on 72 held-out `angeloni2023`
> points: substituting any single declared temperature-dependent closure for the alternative this
> repository declares changes the predicted **total-solids** concentration by less than its
> measured per-condition replicate RSD at every one of the 18 conditions; and for caffeine,
> trigonelline and 5CQA the corresponding effects (≈0.7–3.2 % median) fall inside the campaign's
> declared 0.3–19.7 % replicate range, so the campaign's retained uncertainty does not determine
> whether they are material.

It licenses **nothing** beyond that. In particular it does **not** say:

- that the closures are portable, or that the consumer is insensitive, as a general statement.
  That claim holds for total solids only;
- that `pannusch2024.solver` predicts angeloni — it does not, and the blind gap is visible in
  the figure. `ANALYSIS_transfer` is the standing authority;
- anything about μ(T) portability (untestable — no in-range alternative) or `sherwood_h`
  (unsubstitutable);
- that any evidence label has changed. `pannusch2024.closures` remains `code_verification`;
  `pannusch2024.solver` remains `post_fit_reconstruction`.

The ceiling may not exceed the weakest evidence consumed. The weakest inputs are the p→flow map
(single anchor, granulometry O) and — decisively — the *absent* bioactive replicate uncertainty.

## Next action

**No retirement is recorded.** I-010 is not entered in `RETIRED_CANDIDATES.md`; the screen has
run and returned `NEEDS_NEW_DATA`, and the bundle is the record.

The named data request — solute-specific replicate RSD for caffeine / trigonelline / CGA — is
the unblocking step. It is the *same* missing measurement I-024 identifies, which makes it a
single request serving two candidates.

No deep screen, no novelty research: triage rule 1 gates those on `SURVIVE`, and this is not one.

## Reproduction

```
python -m puckworks.analysis.screen_i010_closure_portability
pytest tests/test_screen_i010.py -v
```

## Source commit

- Corpus snapshot the candidate was generated at: `c1b7d79e8f6800df16ad4fc195d45bf156e4ec8b`
- Foundation merge / branch base: `56060e5b589132c496c432fa09e61efea305d5cf`
- Branch: `insights/if5-wave1-cheap-screens`

# I-010 — Does anything consume pannusch2024.closures, and does it survive outside its declared range?

> Generated from the insight portfolio at commit `56060e5b58`. A card is created when a person decides to work a candidate; everything below the Question is a STARTING POINT, not a result.

## Question

Which registered component, if any, actually consumes pannusch2024.closures's output — and does that consuming result change materially when the artifact is swapped for another source's or driven outside its declared validity?

## Insight type

calibration_artifact_portability

## Target audiences

technical_note, methods_paper

## Why it may matter

Calibration artifacts travel between sources far more readily than the conditions they were fitted under — but only along paths that actually exist, and the registry does not record those paths.

## Why it may be surprising

_not yet written — this is a seed._

## Models, datasets, and other entities

- `model:pannusch2024.closures`
- `model:cameron2020.extraction_bdf`
- `model:grudeva2025.reduced`
- `model:mo2023_2.coupled_bed`
- `model:pannusch2024.solver`
- `model:romancorrochano2017.extraction`

## Tension rows

T-0010

## Existing evidence

- registry execution_role + valid_range + evidence_strength, verbatim. Same-stage co-location only; no output-to-input path was checked.

## Strongest alternative explanation

Nothing consumes this artifact at all, or the named same-stage component is insensitive to it, so portability is moot for it.

## Cheap scientific screen

Step 1 — establish the path: trace the artifact's produced output to a named component's consumed input, via the cards' Interface mapping sections and the registry module. If no path exists, STOP and record that. Step 2, only if a path exists — source-swap sensitivity: hold the consuming configuration fixed, swap the artifact, record the change in the consuming observable, then sweep to the edge of the declared range.

## Minimum viable figure

Consuming observable versus the artifact's driving variable, one curve per source, with the declared range shaded — or, where step 1 fails, the producer/consumer path diagram showing the missing edge.

## Decision rule

- **SURVIVE if** A consuming path exists AND the consuming result moves by more than its own stated uncertainty under the swap, or the artifact is already consumed outside its declared range.
- **RETIRE if** A consuming path exists and the consuming result is insensitive to the swap across the used range.
- **INCONCLUSIVE if** No consuming path can be established from the cards and registry — in which case the finding is the missing path, not a portability result.

## Stop condition

Either no consuming path is found, or the swap changes the consuming result by less than its uncertainty.

## Possible outputs

- technical_note
- methods_paper

## External novelty search terms

- closure transferability porous media
- correlation extrapolation validity range
- permeability correlation portability

_Run only after the candidate survives its cheap screen (blueprint §13.4)._

## Status

SEED

Transitions require a one-line reason appended here.

---

## Human triage (IF-5)

*Hand-written on 2026-08-04, after the generated body above. Everything above this line is generator
output at the `c1b7d79e…` corpus snapshot and is preserved byte-identical — question, stable ID,
entity relations, tension rows and provenance included. The decision record is
[`../IF5_HUMAN_TRIAGE_DECISION.md`](../IF5_HUMAN_TRIAGE_DECISION.md).*

**Provenance of this card.** Content derives from corpus snapshot
`c1b7d79e8f6800df16ad4fc195d45bf156e4ec8b`; the card file was materialised by
`python -m puckworks.insights card I-010` at the foundation merge
`56060e5b589132c496c432fa09e61efea305d5cf`, which is what the generated header line stamps.
`python -m puckworks.insights verify` returns `OK` at both, so the snapshot did not drift.

**Shortlist status: `SHORTLISTED`** — recorded here only. The generated portfolio entry for I-010
is still `SEED` and still unscored; this selection is a human decision, not a generator score.

### Human lane

**Wave 1 — executing now.** The one calibration-portability candidate whose producer→consumer path
can be settled by reading a single import, so the screen cannot stall at step 1 the way
I-013/I-014/I-015 do — and the only one with a genuinely non-circular held-out unit already
ingested and already labelled independent.

### Strongest alternative explanation (human)

The generated alternative — *nothing consumes this artifact at all, or the consumer is insensitive
to it* — survives only in its second half: the consuming path is explicit in source
(`solver.py` imports `closures as pc`), so "nothing consumes it" is already refuted. The live
alternatives are therefore:

1. **Insensitivity.** The artifact reaches the consumer through a very narrow interface — two
   scalar mass-transfer coefficients (`h1`, `h2`) and one partition constant `K` per solve. A
   closure swap that moves `h` by tens of percent may still move the held-out cup endpoint by less
   than the campaign's own replicate spread, because the endpoint is an integral over a
   near-exhausted bed.
2. **Convention mismatch, not portability.** The substituted `K(T)` comes from a different
   partition convention (the two closures are already on record as disagreeing on the *sign* of
   `dK/dT`, `gate_g4_temperature_sensitivity`). A raw numeric swap would measure the convention
   difference, not the closure's portability. The screen must swap the **T-law** with the reference
   anchor held, and say so.
3. **Double consumption.** The analysis' own p→flow map (`_flow_darcy`) *also* calls
   `pc.water_viscosity`. Unfrozen, a viscosity swap would move the boundary condition and the model
   closure at once. Freezing the flow map is a predeclared choice, not a detail.

### Precise cheap screen

1. **Establish the path** from source, not from co-location: which declared closure reaches which
   consumed input, and by what route.
2. **Held-out unit**: `angeloni2023` — a different machine, coffee and basket than the pannusch
   fit, manifest-labelled *independent*, and never used to fit the closures. Non-circular by
   construction.
3. **Freeze**: grid `NZ=200`, `rtol=atol=1e-6`; Dirichlet `c_l(z=0)=0` inlet; the p→flow map at the
   **baseline** viscosity; inventory basis = pannusch Table 2 `c_s0` (blind, no refit); observation
   operator = matched-beverage-mass endpoint at 40 g.
4. **Substitute exactly one declared closure at a time.**
5. **No-refit comparison first.**
6. **Propagate** observational (campaign replicate RSD) and numerical (grid/tolerance) uncertainty.
7. **Recalibration branch** run and labelled separately, and only if the no-refit effect is
   material.

**The materiality criterion is predeclared before any result is viewed** and derived from retained
uncertainty, not from a round percentage — see `docs/insights/screens/I-010/README.md` §
"Predeclared materiality criterion".

### Primary figure

Held-out species concentration under each closure over the common validity range, no-refit
distinguished from recalibrated. `docs/insights/screens/I-010/figures/primary.png`.

### Decision criteria

- **SURVIVE** — a confirmed closure swap changes the held-out output beyond the predeclared
  uncertainty band, over the common validity range of producer and consumer.
- **RETIRE** — no path exists, the declared domains do not overlap, or the held-out output is
  insensitive to every admissible swap.
- **NEEDS_NEW_DATA** — the consumer path exists but no non-circular scoring unit is available.

### Likely output class

`methods_paper` or `technical_note` — a methods note on calibration-artifact portability and on
recording producer→consumer edges in a component registry. Conditional on SURVIVE.

### Screen outcome (appended after the Wave-1 screen ran)

**NEEDS_NEW_DATA** — `docs/insights/screens/I-010/`. The consuming path is real and the
validity-range arm did not fire, but materiality changes inside the campaign's declared
0.3–19.7 % bioactive replicate-RSD range for K(T) and D(T) on all three named solutes. For
**total solids**, the one scored output whose replicate uncertainty the campaign retains, every
admissible swap is immaterial **by the predeclared median-effect vs median-RSD criterion**
(median measured RSD 5.30 %) — though not at every individual condition, where K(T) exceeds its
own condition's RSD at 2 of 18 and D(T) at 1 of 18. Missing evidence, named: solute-specific
replicate RSD for caffeine, trigonelline and CGA.

Not a retirement, so **not** recorded in `RETIRED_CANDIDATES.md`.

*(A first version of this screen returned RETIRE by judging all four outputs against the median
total-solids RSD. That was an invented uncertainty for three of them and is corrected;
see the bundle's correction note.)*

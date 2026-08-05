# I-014 — Does anything consume wadsworth2026.grindmap, and does it survive outside its declared range?

> Generated from the insight portfolio at commit `56060e5b58`. A card is created when a person decides to work a candidate; everything below the Question is a STARTING POINT, not a result.

## Question

Which registered component, if any, actually consumes wadsworth2026.grindmap's output — and does that consuming result change materially when the artifact is swapped for another source's or driven outside its declared validity?

## Insight type

calibration_artifact_portability

## Target audiences

technical_note, methods_paper

## Why it may matter

Calibration artifacts travel between sources far more readily than the conditions they were fitted under — but only along paths that actually exist, and the registry does not record those paths.

## Why it may be surprising

_not yet written — this is a seed._

## Models, datasets, and other entities

- `model:wadsworth2026.grindmap`

## Tension rows

T-0014

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
`python -m puckworks.insights card I-014` at the foundation merge
`56060e5b589132c496c432fa09e61efea305d5cf`, which is what the generated header line stamps.
`python -m puckworks.insights verify` returns `OK` at both, so the snapshot did not drift.

**Shortlist status: `SHORTLISTED`** — recorded here only. The generated portfolio entry for I-014
is still `SEED` and still unscored; this selection is a human decision, not a generator score.

### Human lane

**Candidate-readiness — blocked on a card prerequisite, not on science.** Same lens and same reason
as I-010; step 1 cannot be answered from the current card.

### Strongest alternative explanation (human)

As generated. Sharpened: `wadsworth2026.grindmap` is a grind-dial → mean-radius map, and dial spaces
are **grinder-specific and non-portable** (ledger A9/G5, CLAUDE.md rule 9). A "source swap" for a
dial map is therefore not a portability test unless an explicit refit adapter exists — without one,
any difference measured is the known non-portability of dial spaces, not a finding. This is the
alternative most likely to be true, and it constrains what step 2 is even allowed to do.

### Readiness prerequisite

`docs/cards/wadsworth2026.md` carries a `TEMPLATE_DEVIATION` for *Scope and mechanism*, *Governing
equations*, *Parameters*, *Calibration and validation offered by the source*, *Assumptions and
validity range*, *Interface mapping*, *Overlaps and conflicts* and *Implementation estimate*.
Without *Interface mapping*, the consumed-input edge cannot be traced from the card.

**Prerequisite: the Interface mapping section of `docs/cards/wadsworth2026.md`.** Note the existing
recorded discrepancy that the repair must preserve rather than resolve: `gate_grindmap_refit`
records that "the card's printed β/R0 do NOT reproduce here — recorded, not asserted".

### Precise cheap screen (once ready)

Step 1 — trace the produced output to a named consumed input via the repaired Interface mapping. If
no path exists, STOP and record it. Step 2, only if a path exists **and** an explicit refit adapter
exists — hold the consuming configuration fixed, swap, record the change, sweep to the declared
range edge. Without a refit adapter, step 2 is **not run**: mapping one grinder's dial onto
another's is forbidden.

### Primary figure

Producer/consumer path diagram with the missing edge, or (if a path exists) consuming observable vs
grind dial with the declared range shaded and the adapter named.

### Decision criteria

- **SURVIVE** — a consuming path exists and the consuming result moves beyond its stated
  uncertainty under an **adapter-mediated** swap, or the map is already consumed outside G 1–11.
- **RETIRE** — a path exists and the result is insensitive, or no admissible adapter exists so the
  portability question is not askable.
- **NEEDS_NEW_DATA** — no consuming path can be established from the repaired card.

### Likely output class

`technical_note` on registry hygiene. Most likely deliverable is the card repair.

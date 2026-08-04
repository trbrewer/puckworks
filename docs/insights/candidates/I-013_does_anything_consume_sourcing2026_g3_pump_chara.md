# I-013 — Does anything consume sourcing2026.g3_pump_characteristic, and does it survive outside its declared range?

> Generated from the insight portfolio at commit `56060e5b58`. A card is created when a person decides to work a candidate; everything below the Question is a STARTING POINT, not a result.

## Question

Which registered component, if any, actually consumes sourcing2026.g3_pump_characteristic's output — and does that consuming result change materially when the artifact is swapped for another source's or driven outside its declared validity?

## Insight type

calibration_artifact_portability

## Target audiences

technical_note, methods_paper

## Why it may matter

Calibration artifacts travel between sources far more readily than the conditions they were fitted under — but only along paths that actually exist, and the registry does not record those paths.

## Why it may be surprising

_not yet written — this is a seed._

## Models, datasets, and other entities

- `model:sourcing2026.g3_pump_characteristic`
- `model:foster2025.machine_mode`

## Tension rows

T-0013

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
`python -m puckworks.insights card I-013` at the foundation merge
`56060e5b589132c496c432fa09e61efea305d5cf`, which is what the generated header line stamps.
`python -m puckworks.insights verify` returns `OK` at both, so the snapshot did not drift.

**Shortlist status: `SHORTLISTED`** — recorded here only. The generated portfolio entry for I-013
is still `SEED` and still unscored; this selection is a human decision, not a generator score.

### Human lane

**Candidate-readiness — blocked on a card prerequisite, not on science.** Shortlisted for the same
reason as I-010, but step 1 cannot be answered from the current cards. The lane records that the
**missing edge is the finding**, and that the fix is a card repair rather than an experiment.

### Strongest alternative explanation (human)

As generated — *nothing consumes this artifact at all* — which here is the **leading** hypothesis,
not a fallback. The generated row pairs `sourcing2026.g3_pump_characteristic` with
`foster2025.machine_mode` on **same-stage co-location only**; the manifest row for
`g3_pump_characteristic/ulka_envelope` states outright that it "Does NOT replace
waszkiewicz2025/brewer_quadratic (operative measured quad)". The operative machine-stage adapter is
the waszkiewicz quadratic; this artifact may be an envelope bound with no consumer at all.
Co-location is not a relationship.

### Readiness prerequisite (this is the blocker, not a screen step)

1. `sourcing2026.g3_pump_characteristic` carries `UNRESOLVED_CARD` — there is no
   `docs/cards/sourcing2026.md` or `sourcing2026_g3_pump_characteristic.md`. The stem
   `docs/cards/g3_pump_characteristic.md` exists but is not what the registry name resolves to.
2. `docs/cards/g3_pump_characteristic.md` is missing *Governing equations*.
3. `docs/cards/foster2025.md` — the named same-stage neighbour — is missing every template section,
   including *Interface mapping*.

**Prerequisite: a resolvable card with an Interface mapping on at least one side of the candidate
edge.** Until then the screen has no source of truth for what output this artifact produces or what
input `machine_mode` consumes, and inferring it from module code alone would be exactly the
"co-location is not a relationship" error the Foundry design forbids.

### Precise cheap screen (once ready)

Step 1 — establish the path from the repaired Interface mapping sections; if no path exists, STOP
and record the missing edge as the result. Step 2, only if a path exists — hold the consuming
configuration fixed, swap the artifact, record the change in the consuming observable, then sweep
to the edge of the declared range (catalogue endpoints only, ±15 %; the interior curve is a concave
droop, not a quadratic, per the manifest caveat).

### Primary figure

Where step 1 fails — the producer/consumer path diagram showing the **missing** edge. Only if step 1
succeeds — consuming observable vs the artifact's driving variable, one curve per source, declared
range shaded.

### Decision criteria

- **SURVIVE** — a consuming path exists **and** the consuming result moves by more than its stated
  uncertainty under the swap, or the artifact is already consumed outside its declared range.
- **RETIRE** — a path exists and the consuming result is insensitive across the used range.
- **NEEDS_NEW_DATA** — no consuming path can be established from the repaired cards, in which case
  the finding is the missing path and the readiness prerequisite becomes the deliverable. (The true
  DE1 `Q(P)` curve is closed ESP32 firmware; an independent curve needs a TB bench pull or a Decent
  request — a data request, not an analysis.)

### Likely output class

`technical_note` on registry hygiene — recording producer→consumer edges — rather than a physical
result. Most likely deliverable is the card repair itself.

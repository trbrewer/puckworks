# I-045 — Which strength is load-bearing where the manifest says 'independent + verification'?

> Generated from the insight portfolio at commit `56060e5b58`. A card is created when a person decides to work a candidate; everything below the Question is a STARTING POINT, not a result.

## Question

For the 1 datasets whose validation_strength names both independent + verification, which of those strengths does each consuming gate actually rely on?

## Insight type

data_lineage

## Target audiences

data_note, technical_note

## Why it may matter

A promotion here propagates into every downstream claim citing the dataset.

## Why it may be surprising

_not yet written — this is a seed._

## Models, datasets, and other entities

- `dataset:foster2025_2/fig12_14_curves`

## Tension rows

T-0063

## Existing evidence

- manifest cell, verbatim

## Strongest alternative explanation

The cell is mixed only in wording; both halves support the same gate assertion equally.

## Cheap scientific screen

For each cell, read the consuming gate and record which half of the strength statement its assertion depends on. Source audit, no execution.

## Minimum viable figure

A table of dataset, verbatim strength cell, consuming gate, and the half of the cell the gate leans on.

## Decision rule

- **SURVIVE if** At least one gate leans on the stronger half of a cell whose relevant half is the weaker one.
- **RETIRE if** Every consuming gate already reads the correct half.
- **INCONCLUSIVE if** The consuming gate's assertion is too coarse to attribute to either half.

## Stop condition

Every mixed cell is attributed to a gate and a half.

## Possible outputs

- data_note
- technical_note

## External novelty search terms

- validation data provenance
- circular validation model calibration

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
`python -m puckworks.insights card I-045` at the foundation merge
`56060e5b589132c496c432fa09e61efea305d5cf`, which is what the generated header line stamps.
`python -m puckworks.insights verify` returns `OK` at both, so the snapshot did not drift.

**Shortlist status: `SHORTLISTED`** — recorded here only. The generated portfolio entry for I-045
is still `SEED` and still unscored; this selection is a human decision, not a generator score.

### Human lane

**Wave 2 — after Wave 1 reports.** Method-identical to I-040 on a second dataset
(`foster2025_2/fig12_14_curves`, cell `independent + verification`). Sequenced second on purpose:
it reuses I-040's audit template rather than inventing a parallel one, and if I-040 retires the
same logic is applied here rather than rediscovered.

**Promoted into the slot freed by moving I-079 to reserve** — see
[`../IF5_HUMAN_TRIAGE_DECISION.md`](../IF5_HUMAN_TRIAGE_DECISION.md) §4.

### Strongest alternative explanation (human)

As generated — *the cell is mixed only in wording* — with one sharpening specific to this pairing:
`independent` and `verification` are not two strengths of the same kind. `verification` is a
statement about **code reproducing a source curve**; `independent` is a statement about **data
provenance**. A consumer can legitimately depend on both at once (independent data, verified
implementation) without any promotion having occurred. The audit must not score a consumer as
promoting merely because it names both.

### Precise cheap screen

Identical method to I-040, applied to `foster2025_2/fig12_14_curves`: enumerate consumers, record
the exact source columns and assertion, classify against the half actually load-bearing, compare to
the stated label, preserve manifest wording verbatim. No model execution.

**Prerequisite (not blocking, but recorded):** `docs/cards/foster2025.md` carries a
`TEMPLATE_DEVIATION` for every template section. `foster2025_2` is a distinct card and must be
confirmed to resolve before the audit treats its Interface mapping as authoritative.

### Primary figure

Same shape as I-040: dataset → evidence half → consumer → assertion → load-bearing half.

### Decision criteria

- **SURVIVE** — a consumer states `independent` for an assertion carried only by the
  `verification` half (i.e. by the implementation reproducing a curve, not by the data).
- **RETIRE** — every consumer reads the correct half, or legitimately depends on both.
- **NEEDS_NEW_DATA** — source metadata cannot resolve which half a consumer's assertion rests on.

### Likely output class

`data_note`, merged with I-040 into a single lineage note if both produce findings of the same kind.

### Screen outcome (appended after the Wave-2 screen ran)

**RETIRE** — `docs/insights/screens/I-045/`, recorded in `RETIRED_CANDIDATES.md` with its reopen
condition.

The two halves turned out to be **different columns** of one file, so attribution was observed by
column-level access tracing rather than inferred: `s_fit/w_fit/H_fit` (461 rows, the paper's own
ODE) against `s_data/H_data` + errors (8 pixel-digitized CT points). Seven consumers, coverage
complete. `gate_foster_ct_trajectory` legitimately requires **both** halves — the case this
card's own alternative explanation anticipated — three consumers record verification only, three
make no evidentiary claim, and **none** relies on the independent half alone.

The prerequisite this card flagged is confirmed, not assumed: `docs/cards/foster2025_2.md`
resolves and carries no `TEMPLATE_DEVIATION`; the deviation belongs to `docs/cards/foster2025.md`,
a different card, and is not inherited.

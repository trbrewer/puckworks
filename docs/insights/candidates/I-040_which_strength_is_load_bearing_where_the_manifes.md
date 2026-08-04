# I-040 — Which strength is load-bearing where the manifest says 'independent + post_fit + same_campaign'?

> Generated from the insight portfolio at commit `56060e5b58`. A card is created when a person decides to work a candidate; everything below the Question is a STARTING POINT, not a result.

## Question

For the 1 datasets whose validation_strength names both independent + post_fit + same_campaign, which of those strengths does each consuming gate actually rely on?

## Insight type

data_lineage

## Target audiences

data_note, technical_note

## Why it may matter

A promotion here propagates into every downstream claim citing the dataset.

## Why it may be surprising

_not yet written — this is a seed._

## Models, datasets, and other entities

- `dataset:waszkiewicz2025/traces_time_dependent`

## Tension rows

T-0119

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
`python -m puckworks.insights card I-040` at the foundation merge
`56060e5b589132c496c432fa09e61efea305d5cf`, which is what the generated header line stamps.
`python -m puckworks.insights verify` returns `OK` at both, so the snapshot did not drift.

**Shortlist status: `SHORTLISTED`** — recorded here only. The generated portfolio entry for I-040
is still `SEED` and still unscored; this selection is a human decision, not a generator score.

### Human lane

**Wave 1 — executing now.** The cheapest decisive screen in the portfolio (source audit, no model
execution) over the most re-used time-resolved dataset in the repository. Highest blast radius per
unit cost: two published public claims cite this dataset.

### Strongest alternative explanation (human)

The generated alternative stands and is the one to beat: *the cell is mixed only in wording; both
halves support the same gate assertion equally.* Sharpened for this dataset — the two halves are
not independent artifacts but two **readings of one file**: the equilibrium half is the last
time-point of each of the 11 traces, and the post-fit half is the full 9-bar `Q(t)` trajectory from
the same file. A consumer could therefore touch the file and still depend on only the equilibrium
endpoint. Attribution must be made **per consumer, by what its assertion depends on**, never by
whether it opens `traces_time_dependent.csv`.

A second alternative, specific to this dataset and not in the generated text: the manifest's own
caveat already declares "soft circularity: `m_d(t)` from TDS × Q on same rig". A consumer that
inherits that caveat verbatim is not promoting even if its own docstring is terse.

### Precise cheap screen

Source audit. No model execution except where a source-column path cannot otherwise be resolved.

1. Enumerate **every** consumer of `waszkiewicz2025/traces_time_dependent` — registry gates, the
   `puckworks.harness` producers, the `puckworks.public.claims` PV records (PV-02 and PV-05 are
   named in the authority), the viz producers, and the paper builds.
2. For each, record the exact source columns read and the pressure-node definition in play
   (`basket_pressure__bar` = P_basket vs `pressure__bar` = line/pump-side, per §5.9 / ledger A1).
3. Classify the assertion each consumer makes as depending on the **equilibrium** half
   (independent within-rig) or the **9-bar Q(t)** half (post-fit reconstruction), or both.
4. Compare that against the evidence label the consumer *states*.
5. Preserve the manifest wording verbatim throughout; copy, never paraphrase.

### Primary figure

A table/graph of dataset → evidence half → consumer → assertion → the half actually load-bearing,
with any mismatch marked. `docs/insights/screens/I-040/figures/primary.png`.

### Decision criteria

- **SURVIVE** — at least one consumer states, or lets a reader infer, the independent-equilibrium
  label for an assertion that is actually carried by the post-fit 9-bar reconstruction.
- **RETIRE** — every active consumer preserves the split: post-fit assertions carry post-fit (or
  weaker) labels, and independent labels appear only on equilibrium-carried assertions.
- **NEEDS_NEW_DATA** — the source metadata (columns, node convention, campaign identity) is
  insufficient to determine which half a consumer's assertion rests on. *Only* on that ground; a
  merely coarse assertion is a RETIRE with the coarseness recorded, not a data block.

### Likely output class

`data_note` — a provenance/lineage note about mixed-strength manifest cells and how consumers
should read them. Not a domain paper: nothing here is a physical result.

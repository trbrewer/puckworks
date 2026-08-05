# I-079 — Does the negative result in ANALYSIS_transfer generalise beyond its configuration?

> Generated from the insight portfolio at commit `56060e5b58`. A card is created when a person decides to work a candidate; everything below the Question is a STARTING POINT, not a result.

## Question

Is the negative verdict recorded in ANALYSIS_transfer a property of the mechanism, or of the one configuration it was tested in?

## Insight type

negative_result

## Target audiences

technical_note, domain_paper

## Why it may matter

A recorded negative result is publishable material and stops the same ground being retrodden.

## Why it may be surprising

_not yet written — this is a seed._

## Models, datasets, and other entities

- `result:ANALYSIS_transfer`

## Tension rows

T-0160

## Existing evidence

- allowlisted standing analysis, line pointers only

## Strongest alternative explanation

The negative result is already correctly scoped in the document and no generalisation was ever claimed.

## Cheap scientific screen

Re-run the recorded analysis under a second configuration drawn from the same declared validity range, changing one factor.

## Minimum viable figure

The verdict statistic under both configurations, with the decision threshold drawn.

## Decision rule

- **SURVIVE if** The verdict reverses or weakens materially under the second configuration — the result was configuration-specific.
- **RETIRE if** The verdict holds, which strengthens the existing negative record rather than producing a new one.
- **INCONCLUSIVE if** No second configuration is available inside the declared range.

## Stop condition

The second configuration is run and the verdict compared.

## Possible outputs

- technical_note
- domain_paper

## External novelty search terms

- negative results modelling
- reproducibility negative findings

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
`python -m puckworks.insights card I-079` at the foundation merge
`56060e5b589132c496c432fa09e61efea305d5cf`, which is what the generated header line stamps.
`python -m puckworks.insights verify` returns `OK` at both, so the snapshot did not drift.

**Shortlist status: `SHORTLISTED`** — recorded here only. The generated portfolio entry for I-079
is still `SEED` and still unscored; this selection is a human decision, not a generator score.

### Human lane

**RESERVE.** Moved from active to reserve during IF-5 triage. Full reasoning:
[`../IF5_HUMAN_TRIAGE_DECISION.md`](../IF5_HUMAN_TRIAGE_DECISION.md) §4.

Two reasons, both about scope rather than merit:

1. **It is not a cheap screen.** Its cheap test is "re-run the recorded analysis under a second
   configuration". For `ANALYSIS_transfer` that work is largely already done and archived —
   `angeloni_bracket.geometry_sensitivity_transfer`, `flow_map_sensitivity_transfer`,
   `endpoint_mass_sensitivity`, `loco_cv_refit` and `numerical_convergence` are exactly
   second-configuration runs, and they are slow-lane, not CI. A cheap screen here would mostly
   re-read an existing result.
2. **It lands on a governed claim surface.** `ANALYSIS_transfer` is the source of
   `docs/PAPER_A_DRAFT.md`, and the Paper 1 assurance layer is FROZEN (CLAUDE.md). A candidate
   whose SURVIVE condition is "the verdict reverses or weakens materially" cannot be run as a
   one-day screen without touching reader-facing claim text. It needs the deep-screen lane (IF-7)
   and a human prepared to open the claim ledger.

**Reserve is not retirement.** This candidate is *not* recorded in `RETIRED_CANDIDATES.md`, keeps
its stable ID, and needs no reopen condition. `I-045` was promoted into the freed active slot.

### Strongest alternative explanation (human)

As generated, and it is strong: *the negative result is already correctly scoped in the document and
no generalisation was ever claimed.* `ANALYSIS_transfer` is unusually explicit about its own scope —
it names the superseded reading, the matched-endpoint correction, and the exact strength tags. The
prior should be that the scoping is already right.

### Precise prerequisite before this leaves reserve

Not a card repair — a **governance** step. Before any re-run: identify which second configuration is
genuinely *new* (i.e. not already archived in `docs/figures/paper_a/results.json`), and confirm with
a human that a verdict-bearing re-run is in scope for the frozen assurance layer.

### Primary figure

The verdict statistic under both configurations with the decision threshold drawn.

### Decision criteria (unchanged, for when it is worked)

- **SURVIVE** — the verdict reverses or weakens materially under a second configuration drawn from
  the same declared validity range.
- **RETIRE** — the verdict holds, which strengthens the existing negative record rather than
  producing a new one.
- **NEEDS_NEW_DATA** — no genuinely new second configuration is available inside the declared range
  (i.e. every admissible one is already archived).

### Likely output class

`domain_paper` contribution to Paper A, or a strengthening entry in the existing negative record —
**not** a standalone output. That is itself part of why it is a deep screen and not a cheap one.

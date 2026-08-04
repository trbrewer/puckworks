# Cheap screens

Screens run only on candidates a human has shortlisted
([`../IF5_HUMAN_TRIAGE_DECISION.md`](../IF5_HUMAN_TRIAGE_DECISION.md), IF-5).

## Wave 1 — reported 2026-08-04

| screen | question | decision |
|---|---|---|
| [`I-040`](I-040/) | which half of a mixed-strength manifest cell each consumer leans on | **RETIRE** — 27 consumers attributed, 0 promotions |
| [`I-010`](I-010/) | does anything consume `pannusch2024.closures`, and does a swap move a held-out result | **RETIRE** — path is real; held-out output insensitive to every admissible swap |
| [`I-024`](I-024/) | can one shared transport state explain every Angeloni species at once | **RETIRE** — per-species fits buy nothing held out; the difference is inventory |

Each carries a claim ceiling, an adversarial check, and a reopen condition in
[`../RETIRED_CANDIDATES.md`](../RETIRED_CANDIDATES.md). Wave 2 is **I-045** and **I-076**.

Two habits from Wave 1 worth repeating, both of which changed a result:

- **Enumerate the consumers two independent ways and require the hand-written table to cover the
  union.** In I-040 a static pass over-approximated to 12 gates, dynamic tracing confirmed 7, and
  one real consumer was in neither the obvious reading nor the static-only list. A single
  enumeration would have produced a confident, wrong table.
- **Predeclare the materiality threshold from retained uncertainty, and prefer an arm that is
  scale-free in whatever uncertainty you had to assume.** I-024 could not recover
  solute-specific replicate RSD; because its decisive arm was a *ratio*, the verdict held across
  a band spanning a factor of 65 instead of becoming an artifact of the assumption.

## Budget — per candidate, per blueprint §12 Stage C

```
one focused working day
one executable script
one primary figure
one adversarial check
one decision
```

If a screen wants more than that, it is not a cheap screen; either narrow the question or promote
it to a deep screen (IF-7) with eyes open.

## Bundle

```
docs/insights/screens/I-xxx/
  README.md          what was run and how to re-run it
  result.json        the numbers, machine-readable, producer-bound
  decision.md        SURVIVE | RETIRE | NEEDS_NEW_DATA, and why
  figures/primary.*  the one figure that makes the result legible
```

## Required content of every screen

Per blueprint §18.2, all six:

1. the primary result;
2. an adversarial check — the strongest attempt to make the result go away;
3. raw or source-level visualisation where applicable, not only summary statistics;
4. the effect stated **relative to uncertainty or replicate variation**;
5. the strongest alternative explanation, addressed;
6. the candidate's decision rule applied **without revision** — the rule was written before the
   screen for exactly this reason.

## `decision.md` shape

Blueprint Appendix C:

```markdown
# I-xxx Cheap Screen Decision

## Question
## Evidence unit
## Method
## Result
## Primary figure
## Adversarial check
## Strongest alternative explanation
## Decision            SURVIVE | RETIRE | NEEDS_NEW_DATA
## Why
## Claim ceiling       the strongest thing this result licenses anyone to say
## Next action
## Reproduction        the exact command
## Source commit
```

## Standing constraints

- **Claim ceiling is mandatory.** It is the field that stops a screen result being read as more
  than it is, and it may never exceed the weakest evidence the screen consumed.
- No evidence label is upgraded by a screen result. A screen can tell you a model reproduces a
  curve; it cannot make that reproduction independent validation.
- A `RETIRE` is recorded in [`../RETIRED_CANDIDATES.md`](../RETIRED_CANDIDATES.md) with a reopen
  condition.
- **No publication assurance here.** Protocol freezes, claim ledgers and manuscript work begin
  only after a candidate survives (blueprint §18.3) — that sequencing is the Paper 1 lesson.

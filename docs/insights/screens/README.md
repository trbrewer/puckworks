# Cheap screens

**No screen has been run yet.** This directory defines the bundle shape so the first one
(SPRINTS IF-6) has somewhere to land. Screens run only on candidates a human has shortlisted
(IF-5).

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

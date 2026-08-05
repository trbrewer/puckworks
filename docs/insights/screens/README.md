# Cheap screens

Screens run only on candidates a human has shortlisted
([`../IF5_HUMAN_TRIAGE_DECISION.md`](../IF5_HUMAN_TRIAGE_DECISION.md), IF-5).

## Wave 1 — reported 2026-08-04

| screen | question | decision |
|---|---|---|
| [`I-040`](I-040/) | which half of a mixed-strength manifest cell each consumer leans on | **RETIRE** — 27 consumers attributed, 0 promotions |
| [`I-010`](I-010/) | does anything consume `pannusch2024.closures`, and does a swap move a held-out result | **NEEDS_NEW_DATA** — path is real and total solids is settled (immaterial), but the three named bioactives have no retained per-cell RSD and the effects land inside the declared 0.3–19.7 % range |
| [`I-024`](I-024/) | can one shared transport state explain every Angeloni species at once | **RETIRE** — per-species rate freedom buys nothing held out anywhere in the declared RSD band |

Each carries a claim ceiling and an adversarial check. **Retirements** carry reopen conditions
in [`../RETIRED_CANDIDATES.md`](../RETIRED_CANDIDATES.md); **a `NEEDS_NEW_DATA` screen is not a
retirement and is not recorded there** — its bundle is the record, and it names the missing
measurement.

## Wave 2 — reported 2026-08-05, **corrected 2026-08-05 after exact-head review**

| screen | question | decision |
|---|---|---|
| [`I-045`](I-045/) | which evidentiary function each consumer of a mixed `independent + verification` cell leans on | **SURVIVE** — under ROADMAP §0 (*independent* = data **not used in fitting** the thing being tested) **neither** arm is independent: `k` and `φ_T` were fitted to the very s/H curves the CT columns hold. `gate_foster_ct_trajectory` calls that arm `independent`; it is post-fit reconstruction, same campaign, not held out |
| [`I-076`](I-076/) | do `pannusch2024.solver` and `cameron2020.extraction_bdf` actually disagree, or only claim to | **NEEDS_NEW_DATA** — no admissible matched scenario. **One decisive blocker**: two grinder dial spaces with no declared adapter. Temperature is a non-blocking caveat, not a second blocker |

I-076 carries a [`PROTOCOL.md`](I-076/PROTOCOL.md) frozen and committed **before** any execution.
No model was run: the determination is reached at scenario construction.

**Both Wave-2 screens were corrected on review.** I-045's verdict changed (RETIRE → SURVIVE)
because the screen had used a local reading of *independent* instead of the repository's governing
definition. I-076's disposition is unchanged, but its blocker set was reduced from two to one: the
absence of a temperature *argument* in Cameron's signature is not evidence of a different
intervention, because Cameron carries a fixed ~90 °C water-property basis that sits inside
Pannusch's declared 80–98 °C window. I-076's `PROTOCOL.md` records this in a dated erratum rather
than by rewriting the frozen text.

**I-045 is the first survivor.** It enters the IF-7 deep-screen queue. It is **not** in
[`../RETIRED_CANDIDATES.md`](../RETIRED_CANDIDATES.md).

## Two habits from Wave 2, each of which changed a result

- **A defined term belongs to the repository, not to the screen.** I-045 read the manifest's
  `independent` as an independent measurement *modality*. ROADMAP §0 defines it as **data not used
  in fitting the thing being tested** — a different question with a different answer. The screen
  now extracts the glossary block from `docs/ROADMAP.md` at run time, so the definition it applies
  cannot drift from the definition it cites.
- **A missing argument is not a different intervention.** I-076 inferred from
  `simulate_shot`'s lack of a temperature parameter that Cameron is isothermal in a way
  incompatible with Pannusch. What the signature actually shows is that temperature is not
  *exposed*; the source documents a fixed ~90 °C water-property basis. A fixed or implicit basis
  is a narrow validity range, not an incompatible one. Read what the implementation fixes before
  concluding that it omits.

## Three habits from Wave 1, each of which changed a result

- **Enumerate the consumers two independent ways and require the hand-written table to cover the
  union.** In I-040 a static pass over-approximated to 12 gates, dynamic tracing confirmed 7, and
  one real consumer was in neither the obvious reading nor the static-only list. A single
  enumeration would have produced a confident, wrong table.
- **Judge each output against ITS OWN retained uncertainty, and never borrow another output's.**
  This is the defect that changed I-010's disposition on review. The screen had used the median
  total-solids replicate RSD as the authority for all four scored outputs — but the campaign
  retains no per-cell replicate uncertainty for the three named bioactives at all, only a
  declared 0.3–19.7 % range. Borrowing a fourth output's measurement precision manufactured a
  decision the evidence could not support. Where an output's uncertainty is a *range*, evaluate
  the range; do not collapse it to a midpoint, a median, or the best cell.
- **A robustness claim over an interval needs the interval, not its endpoints — especially when
  the model is refitted inside it.** I-024 originally claimed its decisive arm was *scale-free*
  in the assumed RSD and checked it by rescaling already-computed residuals. That test was
  vacuous: changing the bioactive RSD reweights the bioactives against the *measured*
  total-solids weights and refits the shared model, whose selected rate demonstrably moves. The
  fix was to find the structure that makes an exact argument possible — here, linearity in
  `1/RSD²` giving finitely many breakpoints with monotone criteria between them — and to expand
  the rate grid until a boundary optimum stopped being load-bearing.

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

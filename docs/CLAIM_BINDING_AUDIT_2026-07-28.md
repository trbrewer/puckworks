# How much of the three manuscripts is actually bound to a producer?

**Generated 2026-07-28** from the three existing numeral audits
(`puckworks.paper_a.claim_coverage`, `puckworks.paper_b2.claim_coverage`,
`puckworks.paper3.claim_coverage`) at commit `fc61c46`.

This exists to answer one question: *how much work is left, and where?* Six review rounds have
found defects at a roughly constant rate, and the reason is measurable rather than mysterious.

## The headline

All three papers report **0 unaccounted numerals**. That is not the same as bound.

| | numerals | of which structural | **claims** | producer-bound | **unbound** |
|---|---:|---:|---:|---:|---:|
| Paper 1 | 604 | 168 | 436 | 65 (14.9 %) | **371 (85.1 %)** |
| Paper B2 | 476 | 73 | 403 | 190 (47.1 %) | **213 (52.9 %)** |
| Paper 3 | 375 | 173 | 202 | 135 (66.8 %) | **67 (33.2 %)** |
| **Total** | **1455** | **414** | **1041** | **390 (37.5 %)** | **651 (62.5 %)** |

*Structural* = section, table, figure and equation numbers, years, citation markers. Not claims;
correctly excluded.

**Roughly five out of eight claim-bearing numbers in these manuscripts are not verified against
anything that computes them.** They are accounted for by a hand-written explanation in a Python
dictionary. That dictionary is what "0 unaccounted" measures.

## What the 651 unbound numbers actually are

They are not all equal, and the distinction decides how much matters.

### (a) Declared design settings — the large majority

Thresholds, windows, condition counts, grid sizes, decimation resolutions:

| Paper 1 | Paper B2 |
|---|---|
| 29 × declared tolerance (%) | 37 × scored pressure condition (9 bar) |
| 24 × near-optimal set threshold (%) | 25 × diagnostic decimation resolution (s) |
| 23 × varieties (Arabica, Robusta) | 22 × moving-block duration (s) |
| 22 × brew-ratio / sampling window | 22 × campaign pressure condition (bar) |
| 21 × solutes (3) | 9 × scoring window start (s) |

These are *choices*, not results. Recomputing them is meaningless. But they are **retyped**, often
dozens of times — "9 bar" appears as a bare numeral 37 times in Paper B2. The risk is not that any
one is wrong; it is that changing a design choice requires finding every occurrence by hand. This
is a single-sourcing problem, not a correctness problem.

### (b) Results exempted because they are expensive — the real risk

These are genuine computed outputs whose explanation is a string rather than a producer call:

| paper | distinct result-like unbound values |
|---|---:|
| Paper 1 | **~68** |
| Paper B2 | ~14 |
| Paper 3 | ~4 (and on inspection none is a real result — a SHA width, an interval coverage) |

Paper 1's are almost all prefixed `SLOW LANE:` — endpoint propagation differences, PDE convergence
deviations, objective-family minima, paired bootstrap bounds. Examples:

```
0.421   SLOW LANE: endpoint propagation: paired model-minus-null difference at 38 mL (pp)
0.0204% SLOW LANE: PDE convergence: worst-case relative deviation of the profile range ratio
0.44    SLOW LANE: objective-family: Robusta trigonelline SSE rate_at_min
0.03    SLOW LANE: paired bootstrap 95 % bound (pp)
```

**These are the numbers that can silently go stale.** Each is a real result, exempted from
verification because recomputing it costs minutes to hours. Every one is a place where the
manuscript can drift from the analysis and no gate will notice — which is exactly the failure mode
five of the six review rounds have been finding by hand.

### (c) Values from sources

Published calibrations (`P_c = 12.39 bar`), dataset facts, cited literature values. These need
*provenance*, not recomputation: a citation to the record they came from.

## Why Paper 3 is three times better than Paper 1

Paper 3 is 66.8 % bound; Paper 1 is 14.9 %. The difference is not diligence — it is architecture.
Paper 3 **splices generated blocks** from producers between explicit markers. Those blocks have
never drifted, in any round. Where Paper 3 drifted (round four's Appendix A), it was in a
hand-maintained *copy* of a spliced block — and the fix was to delete the copy.

That is the whole lesson of six review rounds, visible as a number.

## A caveat on the "0 unaccounted" figure itself

Dispositions are keyed by the numeral's **value**, not its context, so the first matching entry
supplies the explanation for every occurrence of that token. A component count of 25 in Paper 3 was
reported as accounted with the explanation *"draft date (25 July 2026)"* — the right disposition
class attached to an unrelated fact.

So the 390 producer-bound figure is trustworthy: those resolve through a producer path. The 651
"explained" figure is softer than it looks — some of those explanations do not describe the number
they are attached to.

## Progress (updated 2026-07-28, after the first binding pass on Paper 1)

`puckworks/paper_a/slow_lane_bindings.py` now resolves each bound number against a committed
archive, the figure bundle, or a module constant, and `verify()` fails on drift.

| Paper 1 slow-lane results | before | after |
|---|---:|---:|
| **Actually checked** | **0 of 75** | **45 of 75** |
| Declared unbindable, with the missing artefact named | 0 | 9 |
| Still unbound | 75 | 21 |

52 bindings cover those 45 tokens, in three kinds:

* **fixed path** into an archive or the committed figure bundle;
* **derived** — for claims of the form *"smallest/largest X across the swept cases"*, which must be
  recomputed; pinning today's argmax would silently stop checking the claim the moment the extremum
  moved to a different case;
* **code constant** — molecular weights, bed porosity. Stronger than an archive: the manuscript is
  checked against the thing that actually runs.

All four failure modes are mutation-tested: a drifted archive value, a vanished archived field, a
missing archive file, a drifted code constant, and a moved derived extremum are each caught.

### What it found on the first pass

Two committed records disagree about the same estimand, and the manuscript quotes both:
`PAPER_A_P0-5_RESULTS.md` gives **−0.73** for the conditions-within-group clustered lower bound,
while `PAPER_A_ENDPOINT_PROPAGATION.json` row 1 gives **−0.725**. They are two runs of one
procedure, so the gap is resampling noise — but a reader comparing the Results with the supplement
sees two numbers for one interval. Recorded in `DISCREPANCIES` rather than reconciled: choosing
which run the paper reports is an authorial decision.

### A note on method

Candidate paths were found by scanning the archives for values matching each unbound token, then
**reviewed for semantic match**. Most candidates were coincidences — `7.0` matched a call-site
count, `100` matched an axial node count, `0.17` (bed porosity) matched an unrelated log-width.
Accepting them would have produced a binding table that passes while checking nothing, which is the
same value-versus-context error the numeral audit itself makes.

## What this implies for the work remaining

The remaining work is **finite and now counted**, which it was not before:

1. **~86 result-like unbound values** (68 + 14 + 4) need binding to their producers. This is the
   correctness-critical set and it is small. For the `SLOW LANE:` entries the binding does not have
   to trigger a rerun — it can compare the manuscript against the *archived record* the slow run
   already wrote, which is cheap and would have caught every stale-number defect found by review.
2. **~565 declared settings** need single-sourcing, not verification. Mechanical, low-risk, and
   convertible to a splice.
3. **Paper 1 is the priority by a wide margin** — it holds 371 of the 651 unbound claims and 68 of
   the ~86 exempted results, while being the paper closest to submission.

The number that says whether the reviews are converging is (1). It is 86. It was never
enumerated before, which is why no round could tell whether it was near the end.

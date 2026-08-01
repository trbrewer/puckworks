# Paper 1 — response to the domain referee

**Review:** `paper1_domain_referee_review_20260731.md` (major revision)
**Reviewed commit:** `4ab18ad3e6fa8b7185a20b6a10d6de86507be805`
**Response prepared:** 1 August 2026

This records what was changed, what was found, and what remains. Two of the referee's findings
changed the paper's reported result; one of them changed it against our interest, and that is
reported first.

---

## 1. Disposition

| ID | Finding | Status |
|---|---|---|
| Major 1 | Level-only constant is not a sufficient headline benchmark | **Actioned** — equal-information panel added; grind asymmetry reported |
| Major 2 | Resampling does not quantify uncertainty in the comparison procedure | **Actioned** — leave-one-condition-out refit of all three arms |
| Major 3 | "Cross-grind" is conditional outcome transfer, not grind physics | **Actioned (Path A)** — Table 2 corrected, dependency table added, interpretation narrowed |
| Major 4 | Convergence evidence is one panel, not paper-wide | **Partially actioned** — see §5; cost measured, not hidden |
| Major 5 | Four-way dissociation and protocol claim are too strong | **Actioned** — recast into the referee's four tiers |
| Minor 1–6 | eligibility rule, ṁ/Q_v notation, physical omissions, Table 2, effect size, Note S1 | **All actioned** |
| Editorial 1–7 | three text defects, Figure S2 readability | **All actioned** |

The referee's headline instruction — *"The next revision should add science, not gates"* — is the
one we followed. This revision adds two new analyses and one source-verification tool; it adds no
new claim-policing machinery.

---

## 2. The two findings that changed the result

### 2.1 The pooled figure was averaging two opposite results

The archived corpus contract has carried this since round 7, and **no reader-facing surface had
ever shown it**:

| grind | mechanistic | level-only constant | difference |
|---|---:|---:|---:|
| coarse | 10.17 % | 11.19 % | **−1.02 pp** (favours the model) |
| fine | 6.71 % | 6.48 % | **+0.23 pp** (favours the **constant**) |
| pooled | 8.44 % | 8.83 % | −0.394 pp |

The whole of the pooled advantage comes from the coarse grind. On the fine grind the mechanistic
model is the worse predictor. This is now stated in the principal Results block and in the
Conclusions, generated from the archive so it cannot drift out again.

We record that this required no new computation. It was a reporting omission, not a missing
analysis, and the referee found it by asking a question none of the twelve preceding rounds asked.

### 2.2 Refitting both arms destabilises the sign

Following the referee's suggested companion analysis, we drop one optimal-grind condition at a
time and **refit all three arms** — mechanistic rate and level, the level-only constant, and the
equal-information empirical response with its family re-selected — then score each on the unchanged
132-observation corpus.

| comparison | median | range | folds favouring the model |
|---|---:|---|---:|
| model − constant | **−0.058 pp** | [−0.328, **+0.416**] | **6 of 9** |
| model − empirical response | −0.187 pp | [−2.249, +0.389] | 8 of 9 |

The fixed-predictor headline of −0.394 pp sits well outside the middle of this distribution, and
the **sign is not stable** to which conditions were used for calibration. Nine dependent folds, so
this is exploratory and descriptive and is labelled as such; it is not a calibrated interval.

This is the referee's Major finding 2 confirmed with a number, and it qualifies the headline more
than any wording change in the previous three rounds did.

---

## 3. Major finding 1 — the equal-information benchmark

New `puckworks/paper_a/empirical_benchmarks.py`. Low-degree responses (constant, linear
temperature, linear pressure, additive, interaction) fitted under MAPE by linear programming,
selected by leave-one-optimal-condition-out cross-validation, refitted on all nine and **frozen
before any held-out record is scored**.

| arm | macro pooled MAPE | model minus arm |
|---|---:|---:|
| level-only constant | 8.832 % | −0.392 pp |
| **empirical response** | **8.691 %** | **−0.251 pp** |
| mechanistic model | 8.440 % | — |

**It reproduces the referee's Appendix A calculation exactly** — every macro figure, all six family
selections and all six per-group scores, to the last reported digit. Two implementations written
without sight of each other agreeing that closely is the strongest validation available for a new
comparator, and we thank the referee for supplying the intermediate values that made it checkable.

The holdout contract is tested rather than asserted: perturbing every held-out concentration by
2–5× leaves family selection and coefficients identical while the scores move.

**The remaining asymmetry is recorded, not hidden.** These baselines receive temperature and
pressure; the mechanistic arm additionally receives a target-grind hydraulic map. The −0.251 pp is
therefore an **upper bound** on the value of the mechanistic structure, and the archive says so in
a `hydraulic_note` field.

We have **not** implemented the "source-rate fixed, target level fitted" and "common hydraulic map"
mechanistic ablations the referee suggested. They are the natural next step and are listed in §6.

---

## 4. Major findings 3 and 5 — what transfers, and what the case shows

**Table 2 contradicted the analysis.** It described `d_s2` and `ψ` as "per grind, from the source's
fitted table"; the canonical calculation freezes centre-grind geometry and applies each source
geometry *globally* as a sensitivity. Corrected — and this mattered, because that row is what tells
a reader what "cross-grind" means.

**A dependency table now states what varies with grind** (hydraulic conductivity and nominal shot
time, the collected-mass endpoint through flow, the records scored) **and what is frozen** (coarse
size, fines fraction and d₃₂; porosity and permeability evolution; the fitted inventory and rate;
the inherited species parameterisation). We adopt the referee's Path A: this is conditional
outcome transfer, and the paper says so.

**The contribution hierarchy is recast** into the referee's four tiers. The paper now distinguishes
what it *demonstrates* (weak localization coexisting with stable prediction; the observation-window
artefact), what it *observes without adjudicating* (a small, heterogeneous, benchmark-sensitive
advantage), what it *does not establish* (transfer of a physical grind mechanism), and what it
*motivates* (the reporting discipline). The four properties are still named as separate, but the
paper now says explicitly that they are not four *independently established* ones — transferability
is assessed through the same held-out errors that describe endpoint accuracy.

---

## 5. Major finding 4 — the numerical envelope, honestly

**Not completed, and nothing is claimed from it.** We attempted the referee's envelope suite and
report the cost and one measured timing rather than a partial pass.

The existing convergence machinery is already parameterised by variety, solute and grind, so the
suite is a matter of compute rather than new code. We launched six cells — Arabica 5-CQA at O, C
and F, Robusta 5-CQA at O, and Arabica caffeine at C and F. **One cell completed: Arabica 5-CQA at
the optimal grind, in 2,482 s (41 minutes)**, against roughly 2 minutes for the published
Arabica-caffeine panel — a factor of about twenty. The remaining five were still running when the
job was stopped.

We deliberately claim **no envelope result** from that single completed cell. It emitted a pass
verdict, but the run wrote no archived artefact and the ad-hoc driver script was not retained, so
the verdict is not reproducible from anything in the repository and is not evidence. Recording it
as a result would be exactly the kind of unbound number the rest of this chain exists to prevent.

The timing is informative, and it is why the referee asked. 5-CQA is the stiffest solute; at 400
nodes and 10⁻⁷ tolerance it is roughly twenty times more expensive per cell than the panel the paper
currently certifies, so the full suite is a multi-hour commitment. The run also reproduced the
numerical-Jacobian overflow and invalid-value warnings the referee asked us to demonstrate harmless
— **they are not absent in the 5-CQA cell**, so that request cannot be answered by assertion.

What we can say now:

- the suite is tractable but is a multi-hour commitment, not an afternoon's work — measured, not
  estimated: ~41 minutes for the single stiffest cell;
- it needs a committed producer that writes an archived artefact, not a driver script, so that the
  result is bound the way every other number in the paper is;
- the highest-value cell is Arabica 5-CQA, because it supplies the largest part of the model's
  apparent advantage; and
- the check that matters is the one the referee specified — whether discretisation and tolerance
  changes move the **paired difference** by much less than the ~0.394 pp (now ~0.058 pp
  refit-aware) effect, not whether concentrations agree to sub-percent in one panel.

Given the refit-aware result in §2.2, this check has become *more* important, not less: the effect
being defended is now smaller than it was.

---

## 6. What we have not done

Stated plainly rather than folded into the above.

1. **The numerical envelope suite** (§5). Attempted and costed; one of six cells finished and is
   deliberately not reported, because it produced no archived artefact.
2. **Mechanistic ablations** — "source-rate fixed, target level fitted" and "common hydraulic map
   across grinds". The referee is right that these would separate the value of target-rate
   recalibration and target-grind hydraulics from the rest of the structure.
3. **A hydraulically equal baseline.** Our empirical panel uses temperature and pressure only. A
   baseline receiving the derived flow/shot-time variable would close the last of the information
   asymmetry, and would probably narrow the margin further.
4. **Flow-map form family** (Major 3). We test magnitude (±20 %) but not form: a nonlinear pressure
   exponent, a shot-time-only map, or a time-varying profile remain untested.
5. **Supplementary Table S7 at journal width.** Still unproofed.
6. **A practical margin.** Not manufactured. The source publishes no per-condition replicate
   uncertainty for the named solutes, so the paper discusses engineering relevance without
   converting it into a formal margin — as the referee directed.

Items 1–4 are the substance of a second revision. None of them is blocked by data availability;
all are compute and analysis.

---

## 7. One correction to our own tooling

The refit-aware tool's first draft never applied the rate multiplier when building the
unit-inventory prediction. `f` was identical for every candidate rate, the level absorbed
everything, and the mechanistic arm was silently a **rate-free** model — scoring 8.281 % against
the published 8.44 %, close enough to look plausible in a table of fold results.

It was caught by validating the no-fold-dropped case against the published arms, and that
validation is now a test asserting the tool recovers 10.17/6.71/8.44, 11.19/6.48/8.83 and 8.691
before any fold is trusted.

The buggy run had reported a stable sign in 9 of 9 folds. The corrected run reports 6 of 9. We would
have published a materially wrong conclusion, and we record it because the referee's own Appendix A
is what made the check possible.

---

## 8. Verification

- protected values unchanged: 38/40/42 g endpoints, ranges, worse-on counts, corpus hashes
- full chain green; 0 unaccounted numerals in both manuscripts
- new numerals all bound to archived producers
- the source transcription was independently verified against the article PDF before this revision
  (726 analyte cells, 66 condition rows, 0 mismatches)

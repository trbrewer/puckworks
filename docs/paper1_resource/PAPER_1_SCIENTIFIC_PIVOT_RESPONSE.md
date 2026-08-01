# Paper 1 — response to the recommended scientific pivot

**Plan reviewed:** `paper1_recommended_scientific_pivot_and_revision_plan_20260801.md`
**Frozen state:** merge commit `eaa3ee7e4930c053e16254ea254fe6073e0032b2`
**Response prepared:** 1 August 2026

The plan's own instruction governs what this round does: *"Do not rewrite the manuscript in earnest
before the first three analytical gates are complete. Otherwise the text will continue to chase
moving results."* So this round runs the gates. It does not touch the manuscript.

The recommendation to pivot is **accepted**. Three of the four analyses run this round changed what
the paper can claim, and two of them removed a plank the plan had assumed was sound.

---

## 1. Disposition

| Stage | Item | Status |
|---|---|---|
| 0 | Freeze evidentiary state, claim ledger | **Done** — `PAPER_A_CLAIM_LEDGER.md` |
| 1 | Measured fractions vs measured complete cups | **Blocked — premise falsified.** See §2 |
| 2 | Observation-design separability (RSI) | **Done** — §4; admitted as a *screen*, not a criterion |
| 3 | Hydraulically equal benchmark + M0/M1/M2 | **Done** — §3; both findings adverse to the model |
| 4 | Numerical reference + envelope | **Not done** — §6 |
| 5 | Structured novelty search | **Cannot be done here** — §6 |
| 6 | Rewrite from a blank outline | **Correctly deferred** by the plan's own gate rule |
| 7 | Adversarial re-review | Deferred with Stage 6 |

---

## 2. Stage 1 is blocked: the "measured cups" are not measurements

The plan makes the measured-fraction-versus-measured-cup contrast its highest-priority analysis, on
this premise:

> "The existing exact-cup simulation is a useful positive control, but it is an inverse crime. The
> sampled-window aggregate is not a complete cup... **The available measured cup data remove both
> limitations.**"

The plan also, correctly, requires that premise be tested before fitting (§6.2). It does not
survive.

Every one of Schmieder's 432 published cup masses was compared with the closed-form integral of that
same replicate's published exponential fit, `M(BR) = c0·λ·(1 − exp(−M_BR/λ))`:

| quantity | value |
|---|---|
| cup masses compared | 432 |
| agreeing to better than 0.01 % | **427 (98.8 %)** |
| median relative difference | **0.000032 %** |
| campaign's own reported cup RSD | **2.5 %** |
| exceptions | 5, **all** in runs containing bit-identical duplicated source cells |

Five orders of magnitude separate the observed agreement from the campaign's own reproducibility.
Nothing separately weighed and assayed lands that far inside its own measurement scatter. Fractions
4, 6, 8 and 9 were never analysed, so the cup could not have been recovered by summing fractions
even in principle — integrating a fitted curve is what the analysed subsample permits.

**Consequence.** A measured-cup versus measured-fraction profile contrast would score the fraction
data against a smooth two-parameter summary *of that same fraction data*. The cup cannot carry rate
information the fractions lack; it is a deterministic function of parameters estimated from them.
The comparison could not come out any way except "fractions are sharper", so it would restate the
data-reduction step rather than test observation design. That is a different inverse crime from the
one the plan set out to escape, not an escape from it.

Outcomes A–D in the plan's §6.7 are therefore not equally reachable, and the predeclared outcome
matrix cannot be applied to this dataset. No other campaign in `puckworks/data/` pairs an
independent cup assay with fractions on the same shots.

**What survives.** The three brew ratios are three collected-mass endpoints of one shot, and under
the separability result those really do carry different rate sensitivities. They are usable as a
*model-based design* input — the plan's own §5.4 category, which requires such designs be "labeled
as model-based design analysis rather than experimental validation". §4 uses them that way.

The audit includes a test that perturbs the cup column by the campaign's reported RSD and confirms
the verdict flips to INDEPENDENT, so the finding is falsifiable rather than a constant.

---

## 3. Stage 3: information parity, and where the skill actually comes from

### 3.1 Parity does not narrow the margin — it reverses it, and the reason is extrapolation

The mechanistic solver's target-grind channel is its matched endpoint, `t_end = 40 g / flow(p, T,
grind)`, so the scalar the empirical arm lacked is the derived residence time. Adding it:

| arm | macro MAPE | vs model |
|---|---:|---:|
| mechanistic (M2) | 8.438 % | — |
| T/p-only empirical panel | 8.691 % | +0.251 pp |
| level-only constant | 8.832 % | +0.392 pp |
| **hydraulically equal, frozen selection** | **9.670 %** | **+1.232 pp** |

Giving the baseline *more* information made it *worse*. The cause is measured, not inferred:

| grind | residence range | outside calibration | largest gap |
|---|---|---:|---:|
| calibration (O) | 11.99 – 27.80 s | — | — |
| coarse | 7.57 – 20.18 s | 36 % | 0.3 spans |
| **fine** | 20.71 – 52.32 s | **73 %** | **1.6 spans** |

A linear empirical response asked to extrapolate 1.6 calibration-spans beyond its support fails
where a solver transports structurally.

### 3.2 But the family contains a predictor that beats the model

A two-parameter, mechanism-free response in **flow alone** scores **8.408 %** against the model's
8.438 %.

**That figure is an oracle upper bound, not a result.** The form was chosen by its held-out score,
which is selection on the test set. It is archived under `oracle_upper_bound` with that status
string, tested to stay separated from the frozen score, and must never be quoted as the empirical
arm's performance.

The gap between 9.670 % and 8.408 % is the actual finding: **nine calibration conditions cannot
identify which hydraulic form to trust when the target domain is extrapolative.** The mechanistic
model's advantage over a fair baseline is not that no simple response can match it — one can — but
that the calibration design cannot *find* that response.

### 3.3 The cross-grind skill is hydraulic, and fitting the rate hurts

| arm | coarse | fine | pooled |
|---|---:|---:|---:|
| **M0** inherited rate, level only, target map | 9.640 | 6.922 | **8.281** |
| **M1** fitted rate and level, **common** map | 11.158 | 6.612 | 8.885 |
| **M2** fitted rate and level, target map *(canonical)* | 10.167 | 6.709 | 8.438 |

| contrast | value | reading |
|---|---:|---|
| M1 → M2 | **+0.447 pp** | value of the **target-grind hydraulic map alone** |
| M0 → M2 | **−0.157 pp** | rate recalibration makes held-out prediction **worse** |
| M0 → M1 | −0.604 pp | fitting the rate under a common map is actively harmful |

The target-grind hydraulic map alone is worth more (0.447 pp) than the entire published
model-minus-constant advantage (0.394 pp). And the best mechanistic arm is the one that **does not
fit the rate at all**.

This lands squarely on two rows of the plan's own outcome matrix — *"Target map drives most of the
gain → reframe the cross-grind result as hydraulic covariate transfer"* and *"if M0 and M2 are
similar, state that rate recalibration adds little held-out value"* — except that M0 is not merely
similar, it is better.

**A confirmation worth recording.** M0's 8.281 % is exactly the value the refit tool produced last
round when its rate multiplier was accidentally omitted. That bug made the arm rate-free, which is
what M0 is by construction. Two independent routes to the same number is a real check on this arm,
and it is now a test.

---

## 4. Stage 2: the separability result, and what it says about espresso designs

The manuscript's sensitivity-collinearity paragraph becomes an exact statement. For `yhat_i = I
f_i(k)` with `s_i = dlog f_i/dlog k`,

    det(G) = (Σ w) · Σ w (s_i − s̄)² = (Σ w)² Var_w(s),

so after profiling the level, **all** local rate information is the weighted spread of the log-rate
sensitivities. The identity is tested against a direct determinant; the module reports the variance
form because on a degenerate design the direct determinant cancels to noise (~1e-9 at n=1000) while
the identity holds ~1e-26.

Applied to the designs actually available:

| design | median RSI | reading |
|---|---:|---|
| single condition | 0.0000 | two unknowns, one observation |
| vary temperature only (isobaric) | 0.0005 | ~nothing |
| vary pressure only (isothermal) | 0.0113 | **21× the temperature axis** |
| full 3×3 grid, 9 conditions | 0.0113 | no better than pressure alone |
| **two extreme corners, 2 conditions** | **0.0131** | **beats all nine** |
| **vary collected-mass endpoint (20/40/60 g)** | **0.0252** | **2.2× the whole process grid** |

Four things follow, and none of them needed a new experiment:

1. RSI is ~10⁻² **everywhere**, never order unity. The paper's central claim is now a number.
2. The 3×3 grid spends a third of its conditions on the axis that buys almost nothing.
3. Two well-chosen conditions carry more separation than all nine — diversity, not count.
4. The **endpoint** is the strongest available lever, which is exactly what Schmieder's brew ratios
   would have supplied had they been independent (§2).

**The admission test, reported at its stricter reading.** Over designs whose RSI is resolved above
its own finite-difference step change, the expected negative association with nonlinear profile
width holds in **5 of 6 groups** (median Spearman −0.61). Including noise-limited designs gives
−0.71 in 6 of 6 — reported only as secondary, because ranking designs whose RSI sits in solver noise
lets noise choose the order. Arabica trigonelline shows no relationship at all.

Per the plan's §5.6, that admits RSI as a **screening tool, not a complete design criterion**, and
the test asserts that reading rather than the flattering one.

---

## 5. What this does to the paper's argument

The pivot is better supported than when it was proposed, and it has moved:

- The **constructive** half is stronger than expected. The separability result is exact, it produces
  concrete and counter-intuitive design guidance (pressure over temperature, endpoints over
  conditions, two over nine), and it needed no new data.
- The **empirical** half of Stage 1 is gone, and cannot be recovered from the available corpora.
- The **cross-grind case** is now best described as *hydraulic covariate transfer*: the target-grind
  map supplies more than the whole published advantage, and rate recalibration subtracts from it.
- The honest summary of the benchmark question is **not** "the model wins" and **not** "the model
  loses". It is: a simple flow response can match the model, the calibration design cannot identify
  that response, and the model's structure substitutes for the support the design lacks.

That last sentence is a real engineering claim, it is outcome-neutral in the plan's sense, and it
survives every result in this round.

---

## 6. Not done, and why

1. **Stage 4, numerical reference and envelope.** Not attempted this round. Unchanged from the
   previous response: one cell measured at 2,482 s, numerical-Jacobian warnings present and
   uncharacterised in 5-CQA. The plan's §9 proposal to exploit the linear structure (analytical
   sparse Jacobian, or a matrix-exponential reference) is the right next move and is not started.
   Note that §3.3 raises the stakes: the contrast now being defended is ~0.15–0.45 pp.
2. **Stage 5, structured novelty search.** **Cannot be completed in this environment.** Scopus, Web
   of Science and Engineering Village require subscriptions unavailable here, and MDPI and Royal
   Society hosts are Cloudflare-blocked from this network. No "to our knowledge" or "first" phrasing
   may be added on the strength of anything done in this session. This is recorded in the claim
   ledger as an environment limit rather than an open task, because no amount of local work closes
   it.
3. **Stages 6–7, rewrite and adversarial re-review.** Correctly deferred by the plan's own gate
   rule. Gate 1 did not close — it was falsified — so the rewrite's Section 5 needs re-planning
   around a design analysis rather than a measured-cup result.
4. **Mechanistic ablations beyond M0/M1/M2**, and the flow-map form family. The plan's §10 says to
   run M1 vs M2 first and only broaden if they differ materially. They differ by 0.447 pp, the
   largest single effect in the comparison, so the flow-map form family is now **indicated** rather
   than optional.
5. **A practical margin.** Still not manufactured. The source publishes no per-condition replicate
   uncertainty for the named solutes.

---

## 7. Verification

- new: `tools/audit_schmieder_cup_provenance.py`, `tools/paper_a_information_parity.py`,
  `tools/paper_a_design_separability.py`, `puckworks/paper_a/separability.py`
- 61 new tests across four files; the referee-pinned `FAMILIES` panel still reproduces 8.691 %
- every archived number has a producer; the oracle bound is tested to stay quarantined from the
  frozen score
- no manuscript file was modified this round

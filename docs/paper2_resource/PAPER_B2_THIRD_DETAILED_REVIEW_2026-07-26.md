# Third Detailed Review of PAPER B2

## Manuscript reviewed

**File:** `docs/PAPER_B2_TEMPORAL_DRAFT.md`  
**Current title:** *One flow curve, many explanations: null-first inference for machine and porous-bed dynamics in espresso*  
**Repository:** [trbrewer/puckworks](https://github.com/trbrewer/puckworks)  
**Repository snapshot reviewed:** [`a0db098e0e5e99a1275a11f05676d46036a6c438`](https://github.com/trbrewer/puckworks/tree/a0db098e0e5e99a1275a11f05676d46036a6c438)  
**Last substantive Paper B2 revision identified:** [`7ec68b4bd354dda2b1e288579bee368fa39d9834`](https://github.com/trbrewer/puckworks/commit/7ec68b4bd354dda2b1e288579bee368fa39d9834)  
**Review date:** 26 July 2026  
**Recommendation:** **Major revision before external journal submission**

Line references in this review refer to the raw Markdown file at the pinned snapshot unless otherwise stated.

---

## 1. Editorial decision and bottom-line assessment

Paper B2 is now **substantially stronger than the two versions previously reviewed**. The authors have acquired and analyzed the individual-brew traces, made the shot rather than the time sample the principal experimental unit, corrected the description of the observation operator, distinguished standard errors from standard deviations, documented the target-access path of each branch, added an exact paired randomization analysis, renamed the pressure analysis as an equilibrium-calibration sensitivity, and exposed the strong pressure dependence hidden by the aggregate mean. Those are major improvements.

The core scientific message is valuable and remains supportable:

> On the declared, preprocessed 9-bar trajectory, the tested time-invariant branches reconstruct the data much less well than time-varying branches; however, the integrated flow curve does not identify a unique bed mechanism.

I independently reproduced the principal 9-bar RMSE values, the five-shot paired effects, the reported pressure-level errors, and the residual diagnostics. I found no evidence that the central numerical ladder is incorrectly calculated.

The manuscript is nevertheless **not yet ready for submission**, chiefly because several newly added validation claims are stronger than the analyses support. The most important problems are:

1. the quantity called a **“shot-to-shot noise floor”** is calculated with each shot included in the mean to which it is compared, so it is optimistic by construction and is not a lower bound or resolution threshold;
2. the leave-one-shot-out spline is fully held out, but the empirical `Φ(t)` branch remains partly target-informed, making the comparison asymmetric despite “like-for-like” wording;
3. the leave-segment-out conclusion is comparator- and gap-definition-dependent, and simple held-out interpolation or a held-out cubic reverses the reported ranking;
4. the “shot-weighted” pressure summary weights pressure-level mean-curve RMSEs and therefore does **not** estimate the expected error for a randomly selected shot;
5. the residual-spectrum interpretation converts the first two Fourier bins of an 80-point, heavily preprocessed series into physical “periods” and overstates what the diagnostic establishes;
6. the evidence manifest remains dirty and commit-mismatched, so the manuscript still lacks a submission-grade frozen release; and
7. manuscript, code, figures, manifest labels, and captions have not completed the same semantic correction pass—terms such as “bound,” “noise floor,” “held-out LOPO,” and “drift, not oscillation” remain in load-bearing locations.

These are serious but tractable issues. I would **not reject the paper’s premise or core result**. A targeted revision that corrects the validation language, replaces the interval-holdout headline, reports the proper shot-level pressure estimands, and freezes a clean release could produce a strong and unusually careful paper about non-identifiability in espresso flow interpretation.

---

## 2. Review scope and materials examined

This review covered more than the prose draft. I examined the following at the pinned repository snapshot:

- [`docs/PAPER_B2_TEMPORAL_DRAFT.md`](https://raw.githubusercontent.com/trbrewer/puckworks/a0db098e0e5e99a1275a11f05676d46036a6c438/docs/PAPER_B2_TEMPORAL_DRAFT.md)
- [`puckworks/analysis/waszkiewicz_shot_level.py`](https://raw.githubusercontent.com/trbrewer/puckworks/a0db098e0e5e99a1275a11f05676d46036a6c438/puckworks/analysis/waszkiewicz_shot_level.py)
- [`puckworks/analysis/waszkiewicz_cross_pressure.py`](https://raw.githubusercontent.com/trbrewer/puckworks/a0db098e0e5e99a1275a11f05676d46036a6c438/puckworks/analysis/waszkiewicz_cross_pressure.py)
- [`puckworks/figures_paper_b2.py`](https://raw.githubusercontent.com/trbrewer/puckworks/a0db098e0e5e99a1275a11f05676d46036a6c438/puckworks/figures_paper_b2.py)
- [`docs/reproducibility/paper_b_manifest.json`](https://raw.githubusercontent.com/trbrewer/puckworks/a0db098e0e5e99a1275a11f05676d46036a6c438/docs/reproducibility/paper_b_manifest.json)
- the committed per-brew Waszkiewicz traces and equilibrium-window data;
- the poroelastic and dissolved-mass implementations and parameter files;
- the generated Paper B result bundle and claim registrations;
- the current figure specifications and figure-generation labels; and
- the two previous detailed reviews, to distinguish genuinely resolved issues from remaining or newly introduced issues.

I also carried out an independent numerical audit. The machine-readable audit accompanies this review as `PAPER_B2_THIRD_REVIEW_NUMERICAL_AUDIT_2026-07-26.json`.

---

## 3. What has been materially improved since the previous review

The revision should receive explicit credit for the following changes.

| Earlier concern | Current status | Assessment |
|---|---|---|
| The averaged 9-bar curve was treated too much like a raw experimental trace | The observation operator now identifies differentiation, ~3 s Savitzky–Golay smoothing, alignment, interpolation, and averaging of five shots | **Substantially resolved** |
| `*_std` fields were actually SEM | The manuscript now says they are pointwise standard errors, not standard deviations | **Resolved** |
| The shot was not used as the experimental unit | Individual-shot scoring and paired effects are now included | **Major improvement**, with one remaining scale error |
| Block resampling was given too much inferential weight | It is now described as a secondary, conditional, fixed-loss sensitivity | **Resolved in principle** |
| `Φ(t)` target reuse was insufficiently disclosed | The prose and dependency graph now acknowledge indirect target access | **Substantially resolved**, but held-out comparisons remain asymmetric |
| Cubic was framed as predictive or as a hard floor | Main prose often calls it a same-trace descriptive benchmark | **Partly resolved**; “bound” and “floor” remain elsewhere |
| Equilibrium observable was incorrectly described as 110–120 s | The repository endpoint-at-100-s observable and 90–100-s sensitivity are now documented | **Resolved**, although the main text is overlong |
| LOPO was presented as fully held-out temporal validation | The Methods now use “LOPO-EC” and state that only equilibrium calibration is withheld | **Resolved in Methods**, but captions, code labels, and conclusion still drift |
| Cross-pressure averaging hid branch reversals | Per-pressure winners and shot counts are now tabulated | **Strong improvement** |
| Pressure-node ambiguity was not explicit | Nominal, recorded basket, and fitted characteristic pressures are separated | **Strong improvement**, with one nominal/recorded inconsistency |
| Solids-sigmoid documentation had the wrong sign | The implementation metadata has been corrected | **Resolved** |
| Reproducibility claims covered too few printed values | The manifest now registers many more claims | **Improved**, but not release-ready |

The strongest addition is the **parameter-access dependency graph** in §5.3c. The distinction between “zero coefficients fitted to the scored trace” and “no target access” is exactly the distinction this paper needs. It should become the organizing principle for all validation language, not merely one late subsection.

---

## 4. Priority revision matrix

### 4.1 P0 — submission blockers

| ID | Required revision | Why it is blocking | Minimum acceptance criterion |
|---|---|---|---|
| **P0.1** | Remove or redefine “shot-to-shot noise floor” | The 0.149 g s⁻¹ quantity is leave-in and is not a lower bound or a resolution threshold | No manuscript, figure, manifest, or code-generated claim uses 0.149 as a “noise floor,” “lower bound,” or criterion for resolvability |
| **P0.2** | Correct the leave-one-shot-out comparison | The spline is fully held out; `Φ(t)` retains the dissolved-mass channel derived partly from the target observable | Abstract, Methods, Results, Discussion, figure captions, manifest, and result labels all state the asymmetry consistently |
| **P0.3** | Remove or redesign the leave-segment-out headline | Simple held-out comparators outperform `Φ(t)` and the result changes with segment count | Delete the claim from Abstract/Conclusions, or rerun a prespecified, sensitivity-tested, target-withheld protocol with multiple generic comparators |
| **P0.4** | Calculate genuine per-shot cross-pressure performance | Weighting mean-curve RMSEs by shot count is not the expected RMSE of a random shot | Report individual-shot RMSEs for all included shots and all branches, with the estimand named precisely |
| **P0.5** | Reframe the spectral result as descriptive low-frequency structure | 80 s and 40 s are the first two nonzero Fourier periods of the short analysis window, not established physical periods | Remove “drift, not oscillation,” “dominant period” mechanistic language, or add proper taper/detrend/raw-shot/null sensitivity |
| **P0.6** | Produce a clean Paper B2 release | Current manifest is dirty, stale, and commit-mismatched | `git_dirty=false`, source/bundle commit match, `release_fresh=true`, timestamp and hashes present, and all figures regenerated from that bundle |
| **P0.7** | Complete a repository-wide semantic audit | The prose has outpaced code, figures, and manifest labels | No contradictory use of “bound,” “floor,” “held-out,” “prespecified,” or LOPO terminology remains |

### 4.2 P1 — important scientific revisions

| ID | Revision | Expected outcome |
|---|---|---|
| **P1.1** | Replace “prespecified spline” with “fixed-architecture spline” unless a dated protocol predates result inspection | Avoids implying preregistration that the repository does not demonstrate |
| **P1.2** | Report spline knot/penalty sensitivity and effective degrees of freedom | Shows that the LOSO conclusion is robust and clarifies that the spline is nearly an empirical other-shot template |
| **P1.3** | Remove post hoc “7–11 bar band” and “upper-pressure regime” language | Report the observed fact: `Φ(t)` is lowest at 7, 8, 9, and 11 bar among the tested settings |
| **P1.4** | Reconcile nominal and recorded pressure in the `P_c` domain count | A pressure-domain claim should use the pressure variable that enters the model, or be explicitly labelled nominal |
| **P1.5** | State exactly which parameters are re-fitted per shot | Constant and cubic are re-fitted; static and `Φ(t)` generally retain upstream calibration |
| **P1.6** | Add methodological references | Cite exact paired randomization/sign-flip inference, smoothing/GCV, grouped validation, inverse problems, identifiability, and model discrimination |
| **P1.7** | Move the long 110–120-s autopsy to a supplement | Preserve provenance without overwhelming the main Data section |
| **P1.8** | Expand the Supplement plan around the new shot-level analyses | Include per-shot tables, LOSO paired differences, knot sensitivity, gap sensitivity, target-reuse audit, and true per-shot pressure summaries |

### 4.3 P2 — editorial and presentation improvements

- Shorten the abstract substantially.
- Correct the malformed LaTeX `Q_{\text{cub}}` expression.
- Renumber §§4.2a/4.2b and §§5.3a–c conventionally.
- Update the stale draft date and complete author, contribution, funding, competing-interest, and acknowledgement fields.
- Replace “Figure near here” specifications with actual rendered figures in the submission manuscript.
- Decide whether Figure 5 and Table 4 duplicate one another; one may belong in the supplement.
- Reduce repeated cautions. The paper’s carefulness is a strength, but some caveats are stated three or four times while the core inferential hierarchy becomes harder to see.

---

## 5. Independent numerical audit

### 5.1 Primary 9-bar mean-trajectory ladder

Using the committed per-brew data and the repository equations on the declared 15.015–94.995 s window, I obtained:

| Branch | Manuscript RMSE | Independent RMSE (g s⁻¹) | Result |
|---|---:|---:|---|
| Best constant | 0.573 | 0.5728555115 | Reproduced |
| Static poroelastic | 0.648 | 0.6476960418 | Reproduced |
| Empirical `Φ(t)` | 0.116 | 0.1157694277 | Reproduced |
| Same-trace cubic | 0.096 | 0.0963965122 | Reproduced |

The primary numerical statement is therefore sound for the committed, preprocessed mean trajectory.

### 5.2 Five individual 9-bar shots

| Shot | Constant | Static | `Φ(t)` | Same-shot cubic |
|---|---:|---:|---:|---:|
| 9-1 | 0.5533 | 0.5657 | 0.2269 | 0.1049 |
| 9-2 | 0.5322 | 0.5980 | 0.1154 | 0.0813 |
| 9-3 | 0.6659 | 0.7726 | 0.2414 | 0.1241 |
| 9-4 | 0.5485 | 0.6037 | 0.1297 | 0.1066 |
| 9-5 | 0.5990 | 0.7654 | 0.2334 | 0.1170 |
| **Mean** | **0.5798** | **0.6611** | **0.1894** | **0.1068** |

Mean paired differences, defined as `Φ(t)` minus comparator:

| Comparison | Mean difference (g s⁻¹) | Direction by shot | Exact two-sided sign-flip/randomization p |
|---|---:|---:|---:|
| `Φ − constant` | −0.3904 | `Φ` better on 5/5 | 0.0625 |
| `Φ − static` | −0.4717 | `Φ` better on 5/5 | 0.0625 |
| `Φ − cubic` | +0.0826 | cubic better on 5/5 | 0.0625 |

These calculations support a large, consistent separation from the tested constant/static branches. They do not establish conventional significance with only five paired units, and the cubic remains an in-sample comparator.

### 5.3 Leave-in dispersion versus honest other-shot prediction

The repository’s 0.149 value is calculated as the mean RMSE between each shot and the **full five-shot mean**, which includes that shot.

For `n` shots,

\[
Q_i-\bar Q_{-i}=\frac{n}{n-1}(Q_i-\bar Q).
\]

With `n=5`, every leave-one-shot-out distance is exactly `5/4 = 1.25` times the leave-in distance. The audit confirms this identity shot by shot.

| Scale | Mean RMSE (g s⁻¹) | Interpretation |
|---|---:|---|
| Shot versus full five-shot mean | 0.149151 | Leave-in descriptive dispersion; optimistic by construction |
| Shot versus mean of the other four | 0.186439 | Honest empirical-template prediction of an omitted shot |
| Mean pointwise between-shot SD | 0.153950 | Descriptive pointwise spread; not a prediction error threshold |

Consequently, the manuscript’s “2.6 times” and “3.2 times the noise floor” statements are not defensible. Even if the other-four benchmark were used merely as a descriptive denominator, the ratios would be approximately 2.09 and 2.53. More importantly, neither value is a formal lower bound or significance threshold.

### 5.4 Leave-one-shot-out spline versus `Φ(t)`

The repository’s fixed 12-knot spline result is reproducible:

| Quantity | RMSE or difference (g s⁻¹) |
|---|---:|
| Fully held-out spline mean RMSE | 0.186072 |
| Raw mean of the other four shots | 0.186439 |
| Spline improvement over raw other-four mean | 0.000367 |
| `Φ(t)` mean per-shot RMSE | 0.189358 |
| Mean `Φ − spline` | +0.003286 |
| SD of five paired differences | 0.025590 |
| Exact two-sided sign-flip p | 0.8125 |

Per-shot differences are mixed: `Φ(t)` is better on two shots and the spline on three. The spline’s result is almost identical to simply using the aligned mean of the other four shots. This is useful evidence, but it should be described as a **same-condition empirical template learned from the other shots**, not as proof that an abstract property called “generic smoothness” explains the trajectory.

Knot sensitivity is reassuring:

| Interior knots | Mean LOSO RMSE | Mean effective df |
|---:|---:|---:|
| 3 | 0.18747 | 7.00 |
| 4 | 0.18719 | 7.99 |
| 6 | 0.18588 | 10.00 |
| 8 | 0.18603 | 11.97 |
| 12 | 0.18607 | 15.66 |
| 16 | 0.18607 | 19.55 |
| 24 | 0.18628 | 27.75 |
| 32 | 0.18629 | 35.74 |

The prediction error is stable, but the effective complexity is high and the result is driven mainly by repeatability of the aligned mean shape across shots.

### 5.5 Leave-segment-out sensitivity

I repeated the repository’s interior-gap protocol and added two simple comparators trained only on non-held-out points:

- linear interpolation across the omitted interval; and
- a cubic polynomial fitted to the non-held-out points and scored only on the omitted interval.

For the manuscript’s five-segment setup:

| Branch | Interior held-out RMSE (g s⁻¹) |
|---|---:|
| Linear interpolation | **0.0705** |
| Held-out cubic | **0.1355** |
| `Φ(t)` | 0.1579 |
| Repository penalized spline | 0.2330 |
| Constant | 0.4193 |

Thus, the statement that `Φ(t)` has a special interval-filling advantage is not robust to the choice of generic comparator.

It is also sensitive to the number and duration of segments:

| Number of segments | Approx. gap (s) | `Φ(t)` | Repository spline | Linear interpolation | Held-out cubic |
|---:|---:|---:|---:|---:|---:|
| 4 | 20.0 | 0.1575 | 0.3926 | 0.0992 | 0.1858 |
| 5 | 16.0 | 0.1579 | 0.2330 | 0.0705 | 0.1355 |
| 6 | 13.3 | 0.1565 | 0.0831 | 0.0534 | 0.1265 |
| 8 | 10.0 | 0.1540 | 0.0496 | 0.0384 | 0.1264 |
| 10 | 8.0 | 0.1537 | 0.0445 | 0.0300 | 0.1177 |
| 16 | 5.0 | 0.1489 | 0.0340 | 0.0254 | 0.1018 |

At six or more segments, even the same spline outperforms `Φ(t)`. The present headline is therefore an artifact of one gap definition and one comparator, not a stable scientific conclusion.

### 5.6 Cross-pressure estimands

The current manuscript reports equal-pressure and shot-count-weighted averages of **pressure-level mean-curve RMSEs**. I calculated individual-shot errors for the static and `Φ(t)` branches across all 57 included shots:

| Estimand | Static RMSE | `Φ(t)` RMSE |
|---|---:|---:|
| Equal-pressure macro mean of mean-curve RMSE | 0.5239 | 0.3345 |
| Shot-count-weighted macro mean of mean-curve RMSE | 0.5095 | 0.3431 |
| Actual mean of 57 individual-shot RMSEs | 0.5271 | 0.3632 |
| Pooled RMSE over all shot × time observations | 0.5567 | 0.3927 |

The ordering of these two branches does not change in this audit, but the values and estimands do. Because RMSE is nonlinear, weighting pressure-level RMSEs by the number of shots cannot be described as the expected RMSE for a randomly drawn shot.

The source campaign is described as 60 brews, while the committed processed deposit contains 57 included shots after source-side exclusions. The manuscript should state both numbers and the exclusion provenance.

### 5.7 Residual-spectrum audit

The reported residual metrics are reproducible:

| Branch | Lag-1 ACF | Durbin–Watson | Lowest-quarter power | Reported dominant period |
|---|---:|---:|---:|---:|
| Constant | 0.9579 | 0.0049 | 0.9571 | 80 s |
| Static | 0.9579 | 0.0038 | 0.9571 | 80 s |
| `Φ(t)` | 0.9687 | 0.0468 | 0.9897 | 40 s |
| Cubic | 0.9041 | 0.0667 | 0.9540 | 40 s |

However, the diagnostic uses an 80-point, 1-s-decimated series. Its first two nonzero Fourier periods are necessarily 80 s and 40 s. The code applies a centered, untapered FFT and defines “slowest quarter” simply as the lowest quarter of available frequency bins. The calculation supports **low-frequency residual structure on this preprocessed window**. It does not establish a physical 40-s oscillation, prove “drift rather than oscillation,” or show that no additional trend term could absorb the residual.

---

## 6. Detailed major comments

### 6.1 Major comment 1 — the 0.149 g s⁻¹ “noise floor” must be withdrawn

#### Current claim

The abstract, §4.2a, §5.2a, Limitations, manifest, and code describe the mean shot-to-full-mean RMSE of 0.149 g s⁻¹ as a “shot-to-shot noise floor.” The manuscript then uses it to state that effects inside the floor are “not resolvable” and to scale the constant/static effects.

#### Why this is incorrect

Each shot contributes 20% of the mean against which it is assessed. That shrinks its residual deterministically. It is not an independent prediction error, an irreducible-noise estimate, a lower bound on model error, or an inferential threshold.

The exact leave-one-out identity above makes the optimism transparent. The honest other-four empirical-template RMSE is 0.1864 g s⁻¹, not 0.1492 g s⁻¹. Even 0.1864 should not be called a noise floor: it combines biological/material repeatability, preparation variation, alignment, smoothing, and measurement effects, and it is based on five shots from one condition.

A model with genuine shot-specific covariates could in principle predict individual shots better than the other-four mean; a misspecified model could perform worse. There is no floor in the mathematical sense.

#### Required revision

1. Replace “shot-to-shot noise floor” everywhere with one of the following precise labels:
   - “leave-in shot-to-full-mean dispersion,” for 0.1492; or
   - “leave-one-shot-out other-four empirical-template RMSE,” for 0.1864.
2. Do not use either quantity to declare a point estimate “resolvable” or “unresolvable.”
3. Present the five paired differences directly and use the exact paired randomization result as the inferential statement.
4. If a standardized descriptive effect is desired, report it explicitly as a ratio to the other-four empirical-template error and state that it is not a significance criterion.
5. Update code names, manifest claim names, figure annotations, and narrative text—not just the manuscript paragraph.

#### Suggested replacement wording

> Across-shot variability was summarized descriptively in two ways: the mean pointwise between-shot standard deviation and the RMSE between each shot and an empirical template formed from the other four shots. The latter was 0.186 g s⁻¹. Neither quantity is treated as an irreducible noise floor or as a formal threshold for resolving model differences; inference is based on the five paired shot-level differences.

#### Acceptance test

A repository-wide search for `noise floor`, `lower bound`, and `not resolvable` should return no load-bearing Paper B2 claim tied to the 0.149 value.

---

### 6.2 Major comment 2 — the LOSO spline/`Φ(t)` comparison is not like-for-like

#### What the code correctly says

The shot-level module explicitly records:

- the equilibrium-calibration channel is cross-fitted;
- the dissolved-mass sigmoid remains target-reusing because TDS replicates are not shot-matched to flow shots;
- `is_full_cross_fit=False`; and
- “Do NOT describe this as a leave-one-shot-out validation of `Φ(t)`.”

This is good internal scientific governance.

#### Where the manuscript overreaches

The Methods call the comparison “like-for-like,” the abstract places the fully held-out spline beside the temporal trajectory without immediately foregrounding the asymmetry, and the Results say the generic smoother “predicts a held-out brew as well as the dissolution-linked trajectory.” The latter can be retained only if the access difference is explicit in the same sentence.

The strongest defensible interpretation is actually useful:

> A fully held-out empirical template performs as well as a partly target-informed mechanistic trajectory; therefore `Φ(t)` shows no predictive advantage and the evidence does not identify the dissolution–poroelastic closure.

That is more conservative—and arguably more compelling—than the current symmetric comparison.

#### Additional point to investigate

The lack of shot-matched TDS prevents pairing one TDS replicate with one particular flow shot. It may not necessarily prevent removal of the held-out shot’s **flow contribution** from the dissolved-mass construction. The authors should inspect the original experimental linkage carefully. If scientifically defensible, they could recompute the flow-dependent component using the mean of the other four flow shots while retaining the aggregate TDS curve, then refit the dissolved-mass sigmoid. This would not create shot-matched TDS, but it would test sensitivity to the target-flow reuse that is currently removable in principle. If the source design does not support that operation, explain why explicitly.

#### Required revision

- Delete “like-for-like” from §4.2b.
- Describe the spline as fully held out and `Φ(t)` as partially cross-fitted/partly target-informed every time they are compared.
- Report the five paired spline-versus-`Φ(t)` differences; the mean difference alone conceals a 2-versus-3 split and an exact p of 0.8125.
- Replace “prespecified” with “fixed across folds” or “fixed-architecture” unless a dated protocol predating analysis is available.
- Explain that the spline is almost identical to the raw other-four mean template.

#### Acceptance criterion

No sentence may use “held-out `Φ(t)`,” “LOSO validation of `Φ(t)`,” or “like-for-like” unless it immediately specifies which access channels remain unwithheld.

---

### 6.3 Major comment 3 — the interval-holdout claim does not survive comparator or gap sensitivity

#### Current claim

The abstract and §5.2a state that `Φ(t)` retains an advantage over the penalized spline when predicting an unobserved interval and that this proves its “shape information is real.” The Discussion repeats that the trajectory carries information a local smoother lacks.

#### Why the conclusion is not supported

The result is conditional on one spline implementation and one five-segment partition. A linear interpolation and a cubic fitted only on non-held-out points both beat `Φ(t)` at the manuscript’s chosen gap duration. When the number of segments is changed from five to six or more, the repository spline also beats `Φ(t)`.

Moreover, `Φ(t)` is not reconstructed without access to the held-out observable: its campaign-derived dissolved-mass trajectory remains fixed and partly derives from the same flow campaign. Thus, the protocol is asymmetric both in model access and in comparator architecture.

The result can support an engineering statement about the behavior of one spline under one large-gap interpolation task. It cannot support the general claim that mechanistic “shape information” exists and generic smoothness lacks it.

#### Required revision

The preferred action is to **remove the interval-holdout claim from the Abstract, main Results, Discussion, and Conclusion** and, if useful, retain the analysis as exploratory supplementary material.

To keep it as a main result, all of the following are needed:

1. prespecify scientifically meaningful gap durations rather than segment counts;
2. show sensitivity across gap location and duration;
3. include linear interpolation, Gaussian-process or smoothing-spline, held-out polynomial, and other reasonable generic comparators;
4. ensure hyperparameter selection uses only available training points;
5. reconstruct `Φ(t)` without the scored segment’s contribution where possible;
6. report paired segment-level or shot-level summaries without treating overlapping time intervals as independent replicates; and
7. state that the exercise tests interpolation architecture, not mechanism identification.

#### Suggested replacement

> An exploratory interval-holdout analysis was highly sensitive to gap definition and comparator choice and is therefore reported only in the supplement; it does not contribute to the mechanistic conclusion.

---

### 6.4 Major comment 4 — the spline is an empirical same-condition template, not merely “generic smoothness”

The LOSO spline is trained on the aligned mean of four other brews made on the same rig, coffee, grind, dose, nominal pressure, preprocessing pipeline, and campaign. Its mean RMSE differs from the raw other-four mean by only 0.00037 g s⁻¹. This means the predictive power is chiefly the repeatable common trajectory, not a generic mathematical ability to smooth arbitrary data.

That is not a weakness. It is exactly the appropriate comparator for the question “does the mechanistic closure add predictive value beyond repeatability of the average shot shape?” But the manuscript should name the estimand correctly.

Recommended phrasing:

> A fixed-architecture empirical template learned from the other four aligned 9-bar shots predicts the omitted shot with mean RMSE 0.186 g s⁻¹, essentially identical to using the unsmoothed other-four mean. The partly target-informed `Φ(t)` trajectory reaches 0.189 g s⁻¹. The closure therefore adds no detectable new-shot predictive value beyond the repeatable same-condition trajectory in this five-shot dataset.

Report knot sensitivity and effective degrees of freedom in the supplement. The numerical stability across knot counts is reassuring, but the near-saturated effective degrees of freedom at 12 knots should be visible to readers.

---

### 6.5 Major comment 5 — exact paired inference needs more careful language

The exact sign-flip/randomization calculation is a good choice for five paired shots, and the reported value 0.0625 is correct when all five differences have the same sign. Several wording changes are still needed.

1. “The p-value reflects the design, not the strength of the effect” is too absolute. The **minimum attainable p-value** is design-limited, but the realized randomization statistic still depends on the observed paired differences and the assumed sign-symmetry null.
2. State the null and assumption: under the null, the signs of paired differences are exchangeable/sign-symmetric.
3. Report the five paired differences in the main text or a compact table.
4. Do not infer that a comparison inside a descriptive dispersion scale is automatically unresolvable.
5. The five-shot percentile bootstrap should remain secondary and clearly labelled unstable/indicative.

Suggested wording:

> All five paired differences favored `Φ(t)` over the constant and static branches. Under an exact two-sided sign-flip test, p = 0.0625, which is also the smallest attainable value with five nonzero paired differences. We therefore emphasize the observed paired effect sizes and their consistency rather than a thresholded significance claim.

---

### 6.6 Major comment 6 — the cross-pressure “random shot” interpretation is mathematically wrong

The code forms a shot-count-weighted average of **pressure-level mean-curve RMSEs**. Because

\[
\operatorname{RMSE}\left(\text{mean curve}\right)
\neq
\operatorname{mean}\left[\operatorname{RMSE}(\text{individual shots})\right],
\]

this is not the expected RMSE of a randomly drawn shot. The manuscript’s statement at lines 345–349 should be corrected.

#### Required outputs

For each branch, report at least:

1. equal-pressure macro mean of pressure-level mean-curve scores;
2. shot-count-weighted macro mean of those pressure-level scores, labelled exactly as such;
3. mean individual-shot RMSE across the 57 included shots;
4. pooled shot×time RMSE, if useful; and
5. pressure-stratified uncertainty or a hierarchical/grouped analysis if inferential claims are intended.

Calculate these for RC-3b as well as static and `Φ(t)`. The current ordering statement should not be finalized until all three are evaluated at the shot level.

The revised prose should also distinguish the 60 reported brews from the 57 traces included in the processed deposit and document the three exclusions.

---

### 6.7 Major comment 7 — pressure “regimes” are post hoc

The manuscript commendably says in Methods that categorical regimes are avoided because bins were not prespecified. It then describes a “7–11 bar band,” an “upper-pressure regime,” and a boundary “below about 7 bar.” That is an internal contradiction.

The observed result is straightforward and should be reported without threshold inference:

> Among the eleven tested nominal settings, `Φ(t)` had the lowest mean-curve RMSE at 7, 8, 9, and 11 bar; RC-3b was lowest at 1, 2, and 13 bar; and the static branch was lowest at 3.5, 4, 5, and 6 bar.

Do not imply that an untested pressure just above or below 7 bar belongs to an inferred regime. Any threshold or regime boundary would require a prespecified model, uncertainty, and denser pressure sampling.

The aggregate `Φ(t)` advantage is also conditional on importing a fixed 9-bar dissolved-mass trajectory across pressures. It is a within-campaign reconstruction exercise, not evidence of a universal pressure-transfer law.

---

### 6.8 Major comment 8 — nominal versus recorded pressure remains inconsistent in the model-domain statement

The pressure-domain producer counts nominal reference settings at or above `P_c`, while the paper emphasizes that recorded basket pressure is the actual delivered boundary variable and is below nominal at every setting. The sentence that “only 1 of 11 reference pressures reach or exceed `P_c`” is true as a nominal-setting count, but may not be true in the same sense for recorded basket pressure.

Required correction:

- state explicitly whether the `P/P_c` model argument uses nominal or recorded basket pressure in each analysis;
- calculate the number of recorded pressure means at or above `P_c` if that is the physically relevant comparison;
- label the current count “nominal settings at or above `P_c`” if retained; and
- discuss the dynamic implementation’s clipping or boundary behavior near/above the characteristic pressure.

The recorded-pressure substitution at 9 bar is a useful robustness result, but it does not resolve model-domain coverage across all eleven settings.

---

### 6.9 Major comment 9 — the residual spectrum is overinterpreted

The residual-versus-time plots, ACF, and Durbin–Watson statistics are valuable. They clearly show coherent residual structure and make the important point that low RMSE is not equivalent to white residuals.

The Fourier interpretation should be narrowed. On an 80-s window sampled at 1 s, 80 s and 40 s are simply the first and second nonzero Fourier periods. The source curve has already been differentiated, smoothed over about 3 s, aligned, interpolated, and averaged, which suppresses high-frequency variation. An untapered FFT of a nonstationary residual is especially sensitive to endpoints and trend leakage.

Replace:

- “Residual structure is slow drift”;
- “drift, not oscillation”;
- “dominant period 40 s”; and
- “not a monotone trend that a further level or slope term would absorb.”

with something such as:

> Residual power is concentrated at low frequencies on the 80-s preprocessed analysis window. This descriptive result confirms coherent long-timescale lack of fit but does not establish a physical periodicity or distinguish drift from oscillation.

If spectral analysis remains a main result, add:

- detrended and tapered estimates;
- multiple windows and sampling resolutions;
- raw individual-shot spectra;
- confidence bands or surrogate/null simulations; and
- a clear scientific cutoff rather than “the lowest quarter of bins.”

---

### 6.10 Major comment 10 — “temporal dynamics are required” should remain explicitly model-relative

The manuscript usually handles this well, but the phrase can still be read as a physical identification statement. The tested static branches are time-invariant levels at fixed pressure. They do not exhaust static spatial heterogeneity, changing boundary conditions at unmeasured nodes, preprocessing artifacts, or latent machine states.

Preferred wording:

> Time-varying predictions are required to reconstruct this preprocessed mean trajectory relative to the tested time-invariant branches.

This preserves the important falsification of the tested static nulls without implying that a particular internal material state has been observed.

Similarly, the Foster reconstruction is a **capacity counterexample from a different apparatus**, not a statistical null calibrated to the Waszkiewicz data. The manuscript largely says this correctly; maintain that distinction in title, tables, and conclusions.

---

### 6.11 Major comment 11 — the equilibrium-observable correction is sound but belongs mainly in the supplement

The endpoint-at-100-s correction is now carefully documented and the sensitivity results are convincing. The current §2.3 paragraph, however, devotes a large amount of main-text space to the 110–120-s forensic autopsy, including one shot identifier, a −106-bar derived value, and an approximately 82-bar pathological fit.

Recommended main-text version:

> The released aggregate traces end at 100 s, so the repository uses the final preprocessed value at each pressure as its equilibrium observable. A 90–100-s mean gives nearly identical calibration. The source-described 110–120-s raw-trace window is unsuitable without an unreported exclusion because one trace has ended within that interval; details are provided in Supplement S1.

Place the full shot-level evidence, exclusion logic, and alternate fits in the supplement and reproducibility bundle.

---

### 6.12 Major comment 12 — the clean-release requirement remains unmet

The current manifest reports:

- `source_commit = 7ec68b4...`;
- `git_dirty = true`;
- `timestamp_utc = null`;
- `bundle_source_commit = 604a581...`;
- `bundle_matches_head = false`; and
- `release_fresh = false`.

The reviewed repository snapshot is `a0db098...`. Thus, `verified=true` means the registered values agree with the current result object under the verifier’s tolerances; it does **not** establish that the manuscript, figures, source code, environment, and bundle constitute one frozen clean release.

The manuscript sentence that a figure “cannot disagree with a verified number” is also too absolute. A figure may reproduce a numeric field while mislabelling its estimand or overinterpreting it. This review found exactly that type of semantic disagreement: “held-out LOPO,” “noise floor,” “bound,” and “drift, not oscillation” labels can be numerically faithful and scientifically misleading.

#### Release acceptance checklist

Before submission, create a Paper B2-specific release for which:

- [ ] the source commit is the exact manuscript commit;
- [ ] the working tree is clean;
- [ ] the result bundle is generated from that commit;
- [ ] `bundle_matches_head=true`;
- [ ] `release_fresh=true`;
- [ ] generation timestamp is populated;
- [ ] data, code, environment/lockfile, bundle, figures, and source-data hashes are recorded;
- [ ] every printed numerical claim is checked;
- [ ] semantic tests reject prohibited labels such as “LOPO held-out temporal validation”;
- [ ] the figure module’s claimed number of verified claims matches the manifest;
- [ ] all figure source CSVs and alt text are archived;
- [ ] a tagged release and archival DOI are cited in the manuscript; and
- [ ] an independent clean-environment reproduction succeeds.

---

### 6.13 Major comment 13 — manuscript, code, figures, and manifest need one synchronized terminology pass

Examples of current drift include:

- Main prose says the cubic is not a lower bound, while Table 1, Figure 2 text, and figure code call it a “flexibility bound.”
- The manuscript calls the pressure analysis LOPO-EC, while Figure 3 and manifest labels still say “held-out.”
- The code correctly says `Φ(t)` is not fully cross-fitted, while Methods call the comparison “like-for-like.”
- The manuscript and manifest call 0.149 a “noise floor.”
- Figure 4 says “drift, not oscillation” and assigns 40-s/80-s dominant periods beyond what the method supports.
- The figure module says its bundle is checked against 122 claims while the manifest now contains 124 registered claims.
- The main Results first say lag-1 ACF is approximately 0.99 in every branch and mean Durbin–Watson approximately 0.01, while the later detailed values include cubic ACF 0.904 and mean DW around 0.031.
- The Methods correctly avoid bare “held out” for LOPO-EC, while Figure 3’s caption says “leave-one-pressure-out held-out means.”

Run a semantic audit across Markdown, Python docstrings, JSON field names, figure labels, captions, alt text, generated CSV metadata, and tests. Numerical verification is not enough for a paper whose central contribution is careful inference terminology.

Suggested repository search before release:

```bash
rg -n "noise floor|flexibility bound|lower bound|LOPO held-out|held-out means|like-for-like|prespecified|drift, not oscillation|dominant period|shape information is real" \
  docs puckworks tests
```

Every match should be either removed, precisely qualified, or explicitly justified.

---

## 7. Section-by-section comments

### 7.1 Title

The current title is strong and includes “espresso.” It is accessible, descriptive, and consistent with the paper’s inverse-problem framing. I would keep it or make only a minor tightening:

> **One Espresso Flow Curve, Many Explanations: Null-First Tests of Machine and Porous-Bed Dynamics**

An alternative that foregrounds the result is:

> **Temporal Flexibility Without Mechanism Identification in Espresso Flow Curves**

The current title is preferable if the Foster machine-capacity case remains a major component.

### 7.2 Abstract

The abstract is too long and carries too many secondary analyses. It currently contains the two most serious overclaims: the 0.149 “noise floor” and the leave-segment-out “shape information” result.

Required changes:

- remove the interval-holdout result;
- remove all “times the noise floor” and “forty times smaller” language;
- state the asymmetric access status of spline and `Φ(t)`;
- report the five-shot effect and exact p without threshold rhetoric;
- replace pressure “band/regime” with the four tested settings;
- reduce residual details to one sentence; and
- retain the intervention-oriented conclusion.

A replacement abstract is provided in §9.

### 7.3 Introduction

The introduction is conceptually strong. It clearly separates:

- machine-side shape capacity;
- failure of tested static branches;
- temporal flexibility;
- empirical versus mechanistic temporal fits; and
- mechanism identification.

Recommended additions:

- cite literature on inverse problems/identifiability and model discrimination, not only espresso models;
- define “null-first” as the authors’ workflow rather than implying an established named method unless cited;
- soften “can establish the need for temporal dynamics” to “can reject the tested time-invariant branches”; and
- ensure “four scoped contributions” matches the actual revised result set after the interval-holdout claim is removed.

### 7.4 Data and observable definitions

This section is much improved. Remaining edits:

- state that the source reports 60 brews but the committed processed deposit includes 57;
- identify the three exclusions or point to a transparent exclusion table;
- move most of the 110–120-s forensic detail to Supplement S1;
- update the final sentence of the observation-operator paragraph, which still says shot-level analysis is the “natural next analysis” and refers to “Limitations, §7,” even though shot-level analysis is now present and Limitations is §8;
- state whether the five 9-bar flow shots and three TDS replicates are experimentally paired, unpaired, or of uncertain linkage; and
- distinguish preprocessing inherited from the upstream source from preprocessing introduced by Puckworks.

### 7.5 Model-comparison ladder

Corrections:

- fix `Q_{\text{cub}}`; the current source contains a tab/malformed `\text` sequence;
- remove “bound” and “floor” from the cubic description;
- call it a “same-trace four-parameter descriptive comparator”;
- in Table 1, add a column for **target access** or merge Table 1 with the dependency graph so readers see parameter count and data access together;
- state which parameters are fitted per shot in the shot-level analysis; and
- identify RC-3b clearly as a Puckworks synthesis rather than a source-paper validated model.

### 7.6 Statistical and diagnostic analysis

#### Residuals

Keep residual curves, ACF, and Durbin–Watson. Demote or reframe the FFT.

#### Block resampling

The caveats are now adequate. Consider moving the method to the supplement because shot-level inference is primary and the main paper is already dense.

#### Shot-level inference

Replace the “noise floor” paragraph. Add the exact sign-symmetry assumption and full paired differences.

#### Flexible comparator

Use “fixed architecture” rather than “prespecified.” Explain why 12 knots were chosen, show sensitivity, and state effective degrees of freedom. Delete “like-for-like.”

#### LOPO-EC

The Methods description is good. Propagate it everywhere else.

### 7.7 Results

#### Primary ladder

The principal table is correct. Change the `Φ(t)` cross-reference from §4.3 to the actual target-access subsection. Remove the stale sentence that all lag-1 ACFs are approximately 0.99 and mean DW approximately 0.01, or replace it with the exact range.

#### Composite branch

The explanation that the composite collapses to the static limit is useful but may be too detailed for this paper unless the composite is shown in the main ladder or figure. Otherwise move it to the supplement or Paper 3.

#### Shot-level section

Retain the all-five directional effects. Remove noise-floor multiples and interval-holdout headline. Present LOSO spline/`Φ(t)` paired differences with asymmetric access labels.

#### Cross-pressure section

Retain the per-pressure table. Replace “7–11 bar band” with the list of tested settings. Replace the random-shot interpretation with actual per-shot calculations.

#### Sign constraints

This section is careful and useful. Keep the conditional language. The viscosity paragraph introduces a second candidate but reserves its analysis for another paper; either cite and explain it briefly or remove it to avoid opening an undeveloped branch.

### 7.8 Discussion

The Discussion’s central inference is strong. Revise §7.2 as follows:

- remove the claim that the interval result proves shape information;
- state that the fully held-out other-shot template matches the partly target-informed `Φ(t)` branch;
- emphasize that this denies a predictive advantage to the named closure;
- state that the outcome may reflect repeatability of a campaign-specific shape rather than abstract generic smoothness; and
- distinguish “time-varying reconstruction required relative to tested branches” from “physical temporal state identified.”

In §7.3, replace generic “LOPO assessment” with “LOPO-EC” and avoid “held-out pressure” unless only the equilibrium point is meant.

### 7.9 Limitations

The section should have at least eight limitations after revision:

1. Foster and Waszkiewicz systems differ.
2. Only five 9-bar shots support the paired analysis.
3. The 0.149 leave-in dispersion was not an inferential floor; use proper descriptive metrics.
4. `Φ(t)` remains partly target-informed and is not fully LOSO.
5. Segment-holdout results are comparator/gap sensitive.
6. Cross-pressure summaries remain within one campaign and should be evaluated per shot.
7. Preprocessing—differentiation, smoothing, alignment, interpolation, averaging—changes residual structure.
8. Many plausible physical processes and direct state measurements remain absent.

The block-bootstrap caveat can remain as an additional limitation or move to the supplement.

### 7.10 Conclusion

The first conclusion paragraph is close to publishable. Replace “temporal dynamics are required” with the explicitly model-relative version.

The second paragraph must say “LOPO-EC” and avoid claiming held-out temporal transfer. A suitable revision is:

> Withholding each equilibrium pressure point in turn produces only modest calibration drift and preserves the aggregate within-campaign ordering, but the calculation retains the common temporal inputs and is not external temporal validation. Branch rankings vary across the tested nominal pressures. The decisive next step is therefore intervention rather than additional curve fitting.

### 7.11 Data/code availability and figures

Do not submit until the clean release exists. Remove the assertion that figures cannot disagree with verified numbers; say instead that plotted numerical fields are generated from the verified bundle and that labels undergo separate semantic tests.

Figure-specific recommendations:

- **Figure 1:** retain; it communicates the capacity-counterexample logic well.
- **Figure 2:** replace “flexibility bound” with “same-trace descriptive comparator”; label the variability band precisely; consider adding per-shot points.
- **Figure 3:** replace “held-out means” with “LOPO-EC mean trace errors”; remove the shaded 7–11 “band” unless explicitly labelled as a post hoc visual grouping.
- **Figure 4:** retitle “Low-frequency residual structure on the 80-s analysis window”; remove “drift, not oscillation” and physical-period rhetoric.
- **Figure 5:** useful, but Table 4 may make it redundant. Keep whichever communicates the perturbation logic better and move the other to the supplement.

### 7.12 Supplement and references

Expand the supplement plan to include:

- full per-shot RMSEs and paired differences;
- exact sign-flip enumeration;
- leave-in versus leave-one-out dispersion derivation;
- spline knot, penalty, and effective-df sensitivity;
- raw other-four template comparison;
- interval-gap and comparator sensitivity, if retained;
- target-access/cross-fit audit for each input channel;
- true individual-shot cross-pressure metrics for all branches;
- preprocessing sensitivity and raw-shot residual diagnostics;
- equilibrium-window forensic analysis;
- all figure source data; and
- a semantic-claim audit report.

The seven references are too few for a methodological paper. Add authoritative references on:

- inverse problems and identifiability;
- practical versus structural identifiability;
- model discrimination and experimental design;
- grouped/clustered cross-validation;
- smoothing splines and GCV;
- exact paired randomization or permutation tests;
- residual diagnostics for smoothed time series; and
- interpolation/forecast validation under temporal dependence.

---

## 8. Recommended revised analysis hierarchy

The paper will be clearer if all results are organized in the following evidentiary order.

### Tier 1 — verified descriptive reconstruction

- Mean 9-bar curve: constant, static, `Φ(t)`, same-trace cubic.
- Exact observation operator and data access.
- Result: time-varying branches reconstruct much better than tested time-invariant branches.

### Tier 2 — experimental-unit replication

- Five individual 9-bar shots.
- Full paired differences and exact sign-flip analysis.
- Result: the separation from constant/static branches is directionally consistent in all five shots.

### Tier 3 — predictive comparator

- Fully held-out other-shot empirical template/spline.
- Partly target-informed `Φ(t)` shown separately.
- Result: no new-shot predictive advantage for the named closure.

### Tier 4 — within-campaign pressure sensitivity

- Equal-pressure mean-curve summaries.
- True individual-shot summaries.
- LOPO-EC, explicitly limited to equilibrium calibration.
- Result: aggregate ordering survives equilibrium recalibration, but branch ranking varies across tested pressures.

### Tier 5 — diagnostics and constraints

- Residual curves and dependence metrics.
- Conditional sign constraints for isolated swelling/fines branches.
- Result: all branches omit structure; some isolated mechanisms have the wrong fixed-pressure sign to explain the rise alone.

### Tier 6 — proposed discriminating experiments

- Pressure steps, reversal, rebrew, and spatial end states.
- Result: interventions are required for mechanism identification.

The current interval-holdout analysis does not belong in the main hierarchy unless fully redesigned.

---

## 9. Suggested replacement abstract

> **Abstract.** Time-resolved espresso outlet flow integrates machine response, pressure boundary conditions, wetting, evolving bed resistance, extraction, and measurement processing, so similar curve shapes need not imply the same mechanism. We use a null-first comparison to ask whether a measured trace requires time-varying predictions relative to specified time-invariant branches and whether that requirement identifies a bed process. A published pump–headspace–infiltration model first demonstrates that a mid-shot flow minimum can arise without an evolving bed. We then analyze the differentiated, approximately 3-s-smoothed, aligned, interpolated mean of five nominal 9-bar brews over 15–95 s. The best constant and a static pressure-dependent poroelastic branch have RMSEs of 0.573 and 0.648 g s⁻¹, respectively. A dissolution-linked empirical `Φ(t)` trajectory, whose temporal input is partly derived from the same campaign flow, has RMSE 0.116 g s⁻¹; a four-parameter cubic fitted and scored on the same mean trace has RMSE 0.096 g s⁻¹. At the shot level, `Φ(t)` improves on the constant and static branches in all five brews by mean paired differences of 0.390 and 0.472 g s⁻¹. The exact two-sided sign-flip p-value is 0.0625, the minimum attainable with five nonzero paired differences, so we emphasize effect size and directional consistency. A fixed-architecture empirical template trained on the other four shots predicts the omitted shot with mean RMSE 0.186 g s⁻¹, compared with 0.189 g s⁻¹ for the partly target-informed `Φ(t)` trajectory; the named closure therefore shows no new-shot predictive advantage. Across eleven tested nominal pressure settings, the best-reconstructing branch varies, with `Φ(t)` lowest at 7, 8, 9, and 11 bar only. Residuals remain strongly structured. We conclude that time-varying predictions are required relative to the tested time-invariant branches, but the integrated flow curve does not identify the responsible mechanism. Pressure steps, flow reversal, spent-puck rebrewing, and spatial state measurements provide more discriminating tests than further unconstrained fits to the same trajectory.

This version deliberately omits the interval-holdout claim and the invalid “noise floor” comparisons while preserving the paper’s strongest results.

---

## 10. Suggested revised conclusion

> A flow curve can reject specified time-invariant descriptions without identifying a physical mechanism. In the cases examined here, a pump–headspace–infiltration model can generate a dip-and-recovery shape without bed evolution, while the preprocessed nominal 9-bar rising-flow trajectory is reconstructed much better by time-varying branches than by the tested constant and static pressure-dependent branches. The same trajectory is reconstructed at least as well by a same-trace cubic, and a fully held-out empirical template learned from other shots predicts a new shot as well as the partly target-informed dissolution-linked trajectory. Fit quality therefore supports time variation relative to the tested nulls but not the named closure.
>
> Withholding each equilibrium pressure point in turn produces modest calibration drift and preserves the aggregate within-campaign ordering, but the temporal inputs remain shared and branch rankings vary across the tested pressure settings. Conditional sign tests constrain isolated resistance-increasing swelling and fines-deposition branches without excluding them from a coupled bed. Mechanism identification now requires interventions—especially pressure steps, flow reversal, spent-puck rebrewing, and spatial end-state measurements—that force the surviving explanations to make different predictions.

---

## 11. Proposed acceptance checklist for the next review round

### Scientific claims

- [ ] The central claim is explicitly relative to tested time-invariant branches.
- [ ] The 0.149 quantity is not called a noise floor or used as a resolution threshold.
- [ ] Full paired shot differences are reported.
- [ ] The sign-flip null and five-shot p-value limitation are stated correctly.
- [ ] The spline is described as fully held out and `Φ(t)` as partly target-informed.
- [ ] “Prespecified” is supported by a dated protocol or replaced.
- [ ] The leave-segment-out headline is removed or fully redesigned.
- [ ] True per-shot cross-pressure metrics are reported for all branches.
- [ ] Pressure groupings are described as observed settings, not inferred regimes.
- [ ] Spectral language is descriptive and does not assign physical periods.

### Internal consistency

- [ ] Abstract, Methods, Results, Discussion, Limitations, and Conclusion use the same estimands.
- [ ] Figure labels and captions use LOPO-EC rather than generic held-out language.
- [ ] Cubic is never called a lower bound or predictive floor.
- [ ] Target-access terminology matches the dependency graph.
- [ ] ACF and Durbin–Watson summaries match the detailed values.
- [ ] Cross-references and section numbers are correct.
- [ ] The malformed cubic equation is fixed.

### Reproducibility

- [ ] Exact manuscript commit is frozen.
- [ ] Clean-tree manifest is generated.
- [ ] Bundle and source commit match.
- [ ] All figures and CSVs regenerate from the frozen bundle.
- [ ] Claim count is consistent across verifier and figure module.
- [ ] Semantic tests accompany numerical tests.
- [ ] Environment and dependency lock are archived.
- [ ] Release tag and DOI are cited.

### Submission presentation

- [ ] Draft placeholders are completed.
- [ ] Actual figures are embedded.
- [ ] Supplement includes all new shot-level and sensitivity analyses.
- [ ] Methodological bibliography is expanded.
- [ ] Abstract is shortened to the target journal’s limit.

---

## 12. Final recommendation

**Major revision.**

The manuscript has crossed an important threshold since the previous review: its core numerical result is reproducible, its observation operator is now honestly described, the experimental unit is finally represented, and the authors have adopted an unusually strong data-access provenance framework. The paper’s central thesis—temporal flexibility can be required without mechanism being identified—is both scientifically useful and well suited to the Puckworks project.

The remaining problems arise mainly from overinterpreting the newest validation layers rather than from failure of the primary analysis. Correcting the leave-in “noise floor,” removing the interval-holdout headline, accurately presenting the asymmetric LOSO comparison, calculating genuine per-shot pressure performance, narrowing the spectrum claims, and producing a clean frozen release would make the manuscript much more defensible. After those revisions, I would expect the paper to be suitable for external peer review.

---

## 13. Principal repository sources

1. Current manuscript at reviewed snapshot:  
   <https://raw.githubusercontent.com/trbrewer/puckworks/a0db098e0e5e99a1275a11f05676d46036a6c438/docs/PAPER_B2_TEMPORAL_DRAFT.md>
2. Shot-level analysis:  
   <https://raw.githubusercontent.com/trbrewer/puckworks/a0db098e0e5e99a1275a11f05676d46036a6c438/puckworks/analysis/waszkiewicz_shot_level.py>
3. Cross-pressure analysis:  
   <https://raw.githubusercontent.com/trbrewer/puckworks/a0db098e0e5e99a1275a11f05676d46036a6c438/puckworks/analysis/waszkiewicz_cross_pressure.py>
4. Paper B2 figure generator:  
   <https://raw.githubusercontent.com/trbrewer/puckworks/a0db098e0e5e99a1275a11f05676d46036a6c438/puckworks/figures_paper_b2.py>
5. Current Paper B evidence manifest:  
   <https://raw.githubusercontent.com/trbrewer/puckworks/a0db098e0e5e99a1275a11f05676d46036a6c438/docs/reproducibility/paper_b_manifest.json>
6. Reviewed repository tree:  
   <https://github.com/trbrewer/puckworks/tree/a0db098e0e5e99a1275a11f05676d46036a6c438>

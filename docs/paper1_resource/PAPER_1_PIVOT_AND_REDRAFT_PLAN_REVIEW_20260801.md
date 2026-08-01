# Review of `PAPER_1_PIVOT_AND_REDRAFT_PLAN.md`

**Review date:** 1 August 2026  
**Document reviewed:** [`PAPER_1_PIVOT_AND_REDRAFT_PLAN.md`](https://github.com/trbrewer/puckworks/blob/main/docs/paper1_resource/PAPER_1_PIVOT_AND_REDRAFT_PLAN.md)  
**Review purpose:** Assess whether the proposed pivot provides a scientifically defensible, genuinely interesting, and executable basis for redrafting Paper 1; identify factual, mathematical, inferential, physical, and novelty risks; and prescribe the actions required before manuscript drafting.  
**Overall disposition:** **Approve the pivot in principle, but require major revision of the plan before it becomes operative.**

---

## 1. Executive assessment

The pivot is directionally correct and materially better than continuing to defend the original −0.394 percentage-point benchmark headline. The plan correctly recognizes that the paper’s most interesting result is not a small average predictive advantage. It is the mismatch between:

1. apparently useful whole-cup prediction;
2. weak or one-sided localization of the fitted transfer-rate multiplier; and
3. a much stronger dependence of cross-grind prediction on target-side hydraulic information.

That is a credible basis for a compelling paper. It is also more intellectually valuable than another narrowly benchmarked mechanistic-versus-empirical comparison.

However, the current plan replaces the old overclaim with several new ones. In particular, it repeatedly treats a high-rate asymptote that has been verified **within the declared numerical model** as a physically verified property of real espresso. It also makes a universal recommendation to freeze an unseparated parameter, despite evidence that the benefit reverses by grind. The most important pooled ablation result is driven entirely by the coarse-grind target and is small or opposite in the fine-grind target. This is not a minor qualification: it changes H3, H4, the title, the proposed evidential hierarchy, and the manuscript structure.

The paper available after correction is stronger and more precise:

> **A whole-cup espresso model can remain predictively useful while failing to localize a fitted extraction-rate multiplier. In this campaign, target-side hydraulic metadata explains a robust coarse-grind transfer benefit, whereas fine-grind effects are small and often opposite. An exact local sensitivity geometry identifies when the scale and rate directions become difficult to separate and suggests model-based, prospective design changes.**

That thesis is interesting, testable, and appropriately scoped. It does not require claiming that real espresso kinetics have been physically verified to saturate, that all whole-cup designs are uninformative, or that freezing is universally preferable to fitting.

### Recommended decision on H1–H4

| Hypothesis | Disposition | Required change |
|---|---|---|
| **H1 — saturation** | **Retain, but reclassify and narrow** | State first as an analytical/model-structural high-transfer limit. Treat campaign placement on the plateau as an empirical observation. Do not call the matrix-exponential check physical validation. |
| **H2 — exact sensitivity geometry** | **Retain; potentially the cleanest methodological contribution** | Distinguish the Gram determinant from the profiled local curvature, specify the loss/noise assumptions, and label RSI as a local model-based screen rather than “all information.” |
| **H3 — hydraulic attribution** | **Retain, but disaggregate by grind** | The pooled 9/9 result is coarse-driven. Recast as a robust coarse-grind benefit and a heterogeneous or near-null fine-grind result. Call the input target-side hydraulic metadata, not a mechanism proved to transfer. |
| **H4 — freeze rather than fit** | **Replace** | The evidence supports “do not interpret an unlocalized fitted value as learned.” It does not establish a universal freeze-at-one rule. Compare fixing, regularization, independent constraint, and profile/ensemble propagation. |

### Blocking conclusion

**Do not begin the substantive redraft under the current H1–H4 wording.** The following must be corrected first:

- the physical-versus-model-structural conflation;
- the incorrect identification of the 8-of-9 fold exception;
- the pooled coarse/fine concealment;
- the mismatched full-fit and refit-aware estimands;
- the overstatement of “unbounded,” “unidentified,” and “two conditions beat nine”; and
- the novelty framing in light of directly adjacent espresso inverse-modeling work and the established variable-projection literature.

Once those points are resolved, the pivot should proceed.

---

## 2. What is strong and should be retained

### 2.1 Abandoning the old benchmark hierarchy

The decision to stop leading with the −0.394 pp model-versus-constant result is correct. Its refit-aware median is much smaller, and its sign changes across leave-one-condition-out refits. It should remain a secondary historical result, not the thesis.

The plan’s general rule is right: a headline should reflect the strongest stable scientific finding, not the largest convenient fixed-fit number.

### 2.2 Separating prediction from parameter learning

The pivot recognizes an important distinction that many modeling papers blur: a model may predict an output adequately without identifying every fitted parameter. This is a useful scientific and practical message for espresso modeling. It also creates a bridge between the domain problem and broader inverse-problem practice.

### 2.3 The exact-in-time temporal reference

Recognizing the semi-discrete linear structure and evaluating it by matrix exponential is an excellent numerical contribution to the assurance layer. It strongly supports the conclusion that the observed high-rate plateau is not caused by the BDF time integrator, adaptive tolerances, or a time-stepping floor.

This result should be retained, but described as:

> an exact-in-time reference for the same semi-discrete model and spatial operator.

It is not an independent physical model, an independent discretization, or experimental validation.

### 2.4 The refit-aware M0/M1/M2 comparison

Refitting inside each calibration-condition fold is substantially more informative than comparing arms using a single full-support fit. The archive also correctly labels the folds exploratory and dependent rather than converting them into a confidence interval.

The M1–M2 construction is particularly useful because it isolates the effect of replacing the common optimal-grind hydraulic map with the target-grind map, conditional on the same fitted level and rate.

### 2.5 The explicit “not claiming” section

The plan already contains several valuable boundaries: it does not treat the multiplier as an intrinsic kinetic constant, does not claim general non-identifiability, and does not call the nine folds a calibrated interval. These should be retained and expanded.

### 2.6 Premise-first review

The proposed R0 premise audit is a major improvement over repeatedly hardening the assurance taxonomy while leaving scientific premises untested. The plan correctly learns from the Schmieder and rate-domain discoveries.

The implementation should be adjusted, however: not every physical premise can be converted into an executable repository test. Premises need to be classified as algebraic, numerical, data/provenance, inferential, or physical/empirical, with an appropriate form of evidence for each.

---

## 3. Critical findings requiring correction before drafting

## 3.1 The plan confuses numerical verification with physical verification

### Finding

Sections 1, 2, 3.6, 4, 6, 9, and 10 repeatedly describe the high-rate plateau as “physical,” state that “H1’s mechanism is verified,” refer to the matrix-exponential result as “truth,” and retire the risk that saturation may not be physical.

The matrix-exponential path establishes something narrower and still valuable:

- the production right-hand side is linear in the state for the tested formulation;
- the matrix operator reproduces that right-hand side;
- the high-rate plateau is reproduced without BDF time stepping; and
- the finite-dimensional semi-discrete model approaches a finite high-rate response.

It does **not** establish that real espresso grounds reach local equilibrium before displacement, that the fitted rate multiplier corresponds to a physical rate, or that the omitted processes in the model would preserve the same plateau and shoulder.

Both temporal paths share the same governing equations, parameterization, initial state, spatial discretization, hydraulic inputs, two-grain representation, and omitted physics. The path is independent only with respect to temporal integration.

### Why this matters

The proposed primary hypothesis is presently described as “a claim about espresso, not about statistics.” That is too strong. The high-rate limit is first a property of the declared model. Whether real whole-cup measurements occupy that regime is an empirical question. Parameter identifiability is also inherently an inverse-problem concept, even when its cause has a physical interpretation.

This distinction is especially important because the present model does not resolve all processes that can create or destroy apparent rate sensitivity, including wetting and unsaturated infiltration, evolving permeability and porosity, puck compression/swelling, axial dispersion, radial nonuniformity, channeling, time-varying flow, and model-form discrepancy. Recent experimental and modeling work emphasizes nonlinear, time-dependent hydraulic behavior and dissolution–poromechanical coupling in espresso; that literature strengthens the need for careful scope rather than invalidating the paper.

### Required wording changes

Replace:

- “The saturation is physical, not a solver floor”
- “H1’s mechanism is verified”
- “measure BDF’s time-integration error against truth”
- “flatness … is a measurement”
- “DONE: saturation is physical”
- “no numerical objection to the redraft remains open”

with language such as:

- “The plateau is a structural property of the declared semi-discrete model, not a BDF time-stepping artifact.”
- “The matrix-exponential reference verifies the high-rate asymptote within the declared model.”
- “BDF error is measured against the exact-in-time solution of the same semi-discrete system.”
- “The computed response is strongly rate-sensitive at low multipliers and nearly flat at high multipliers.”
- “The numerical-artifact hypothesis is retired; external physical validity remains open.”

Rename G3:

> **G3 — Is the high-rate plateau a BDF artifact or a structural property of the declared semi-discrete model?**

Recommended status:

> **PASSED for the tested model and numerical envelope. Physical generalization remains untested.**

### Required action

Add a model-scope table that distinguishes:

| Proposition | Status |
|---|---|
| High-rate limit exists in the declared semi-discrete model | Established numerically; ideally derive analytically |
| Plateau is not caused by BDF integration | Strongly established |
| Existing campaign profiles are broad/right-censored under the declared objective and model | Established descriptively |
| Real espresso reaches the same local-equilibrium regime | Not established |
| The fitted multiplier is a physical kinetic constant | Explicitly not claimed |
| The shoulder location is transferable to other machines, recipes, roasts, or model structures | Not established |

---

## 3.2 The plan contains a factual attribution error: the 8-of-9 exception is not Arabica caffeine

### Finding

H1 states that the heterogeneity explains why freezing wins in 8 of 9 folds and that “the single exception is Arabica caffeine.” This conflates two different units of analysis:

- The **9-fold** result is indexed by the omitted optimal-grind calibration condition.
- The **6-group** result is indexed by variety × solute.

In `PAPER_A_ABLATION_REFIT_STABILITY.json`, the single positive pooled M0−M2 fold is the fold that omits **93.4 °C and 6 bar**, with M0−M2 = +0.010 pp. A fold is not a solute/variety group.

Arabica caffeine may be the exception in a separate six-group full-fit or group-level comparison, but it cannot be used to identify or causally explain the one positive calibration-condition fold without an additional decomposition.

### Why this matters

This is not merely a label error. The plan uses the misattribution to provide a physical explanation for the fold result. That explanation is currently unsupported.

### Required correction

Use two separate statements:

> “Across the six solute × variety groups in the full-support analysis, M0 is better in five groups, with Arabica caffeine as the exception.”

and

> “Across the nine leave-one-condition-out refits, the pooled M0−M2 contrast is negative in eight folds; the positive fold occurs when the 93.4 °C, 6 bar condition is omitted.”

Do not claim that one explains the other until a fold × group contribution analysis has been run.

### Required action

Generate a 9-fold × 6-group contribution matrix for M0−M2 and M1−M2, separately for coarse and fine targets. This will show which groups and target observations produce each pooled fold direction.

---

## 3.3 The pooled hydraulic result conceals opposite coarse- and fine-grind directions

### Finding

The plan makes M1−M2 = +0.524 pp, positive in 9/9 folds, the central hydraulic result. Yet its own drafting rule states that no pooled number may be presented without disaggregation. Applying that rule to the archived fold rows changes the interpretation substantially.

The following values are recomputed from the rounded fold-level coarse and fine scores in `PAPER_A_ABLATION_REFIT_STABILITY.json`. The contrast is arm minus M2; therefore positive M1−M2 favors the target-grind map in M2, while negative M0−M2 favors freezing in M0.

| Contrast | Coarse-grind fold distribution | Fine-grind fold distribution | Pooled interpretation |
|---|---|---|---|
| **M1−M2** | median **+1.234 pp**; range **+0.613 to +2.190**; **9/9 positive** | median **−0.037 pp**; range **−0.671 to +0.086**; **7/9 negative** | Pooled +0.524 pp is entirely coarse-driven; target-map hydraulics usually perform slightly worse on fine targets |
| **M0−M2** | median **−0.483 pp**; range **−1.012 to −0.155**; **9/9 negative** | median **+0.155 pp**; range **−0.587 to +0.400**; **6/9 positive** | Freezing consistently helps coarse predictions but usually hurts fine predictions |

The same asymmetry is visible in the full-fit table:

- M1−M2: coarse +0.991 pp, fine −0.097 pp, pooled +0.447 pp.
- M0−M2: coarse −0.527 pp, fine +0.213 pp, pooled −0.157 pp.

### Consequences

This changes the paper in four ways.

1. **H3 cannot say simply that target-grind hydraulics transfer.** The result is a robust coarse-grind benefit and a small, usually opposite fine-grind effect.
2. **H4 cannot say simply that freezing transfers better.** Freezing consistently improves coarse predictions but generally worsens fine predictions.
3. **The pooled 9/9 result is not evidence of uniform target-side benefit.** It is evidence that a large, stable coarse effect dominates a small fine effect.
4. **The underlying asymmetry may be more scientifically interesting than the pooled result.** It raises a real question: why is the optimal-grind hydraulic map especially inadequate for coarse prediction, while the target-grind map does not improve—and may slightly degrade—fine prediction?

### Required reframing

Replace H3 with a grind-specific statement. For example:

> “In this campaign, target-side hydraulic metadata provides a large and refit-stable improvement for coarse-grind prediction. Fine-grind effects are small and usually opposite. The pooled transfer gain is therefore a coarse-driven result, not a uniform hydraulic benefit across target grinds.”

Replace “freezing beats fitting” with:

> “Fixing the rate at its inherited normalization is competitive in pooled prediction and consistently improves coarse-grind transfer in this campaign, but it is not uniformly superior and generally worsens fine-grind prediction.”

### Required action

Before drafting, produce all headline ablations at the following levels:

- pooled;
- coarse versus fine;
- variety × solute;
- calibration-condition fold; and
- fold × group contribution.

The first main ablation figure should show the coarse/fine split, not the pooled mean alone.

---

## 3.4 H4 is too categorical and is not supported by the evidence

### Finding

H4 states:

> “When a design cannot separate a parameter, the parameter should be frozen at an inherited value rather than fitted.”

The evidence supports a weaker and more defensible rule:

> **When a design does not localize a parameter, the fitted value should not be interpreted as learned, and its uncertainty/non-uniqueness should be propagated or constrained.**

It does not establish that fixing the multiplier at 1.0 is the generally optimal response. The inherited value is a normalization from the source model, not an externally validated physical constant. The fine-grind result often favors the fitted-rate arm. Other defensible treatments of a weakly localized parameter include:

- regularization toward the inherited value;
- a hierarchical or shrinkage prior;
- independent experimental constraint;
- reporting a profile set rather than a point estimate;
- propagating predictions over the near-optimal profile;
- model averaging over the flat direction; or
- removing/reparameterizing the weak direction if the intended task does not require it.

### Why this matters

A paper that recommends “freeze rather than fit” risks turning a campaign-specific ablation into a universal estimation principle. Reviewers in inverse problems or statistics will challenge this immediately.

### Recommended H4

> **When whole-cup data do not localize the rate multiplier, its fitted value should not be interpreted as a learned kinetic quantity. The parameter should instead be independently constrained, regularized, fixed with sensitivity analysis, or propagated over its acceptable profile. In this campaign, fixing it at the inherited normalization improves coarse-grind transfer and is competitive in pooled error, but is not uniformly superior.**

### Required analyses

At minimum, compare:

1. **Fixed anchors:** k = 0.5, 1, 2 and any source-justified nominal values.
2. **Penalized fitting:** several predeclared regularization strengths toward k = 1.
3. **Profile-propagated prediction:** prediction envelopes or profile-weighted summaries over acceptable k.
4. **Free fitting:** current M2.

The purpose is not to optimize another benchmark after seeing the targets. It is to test whether the conclusion is specifically “k = 1 wins” or more generally “aggressive unconstrained fitting is unnecessary for this transfer task.”

---

## 3.5 H2’s algebra is useful, but “all local information” needs qualification

### Finding

For log-parameters under a multiplicative factorization, let

- `u_i = ∂ log ŷ_i / ∂ log I = 1`,
- `s_i = ∂ log ŷ_i / ∂ log k`, and
- `W = Σ w_i`, `S = Σ w_i s_i`, `Q = Σ w_i s_i²`.

The two-column weighted sensitivity Gram matrix is

```text
G = [[W, S],
     [S, Q]].
```

Therefore,

```text
det(G) = WQ − S² = W² Var_w(s).
```

That identity is exact. However, after profiling the level direction, the Schur complement—the local curvature in the log-rate direction under the corresponding weighted least-squares geometry—is

```text
Q − S²/W = W Var_w(s),
```

not the determinant itself. The determinant equals the scale-direction norm `W` multiplied by that profiled curvature.

### Required distinction

The paper should separate three statements:

1. **Exact algebraic geometry:** `det(G) = W² Var_w(s)`.
2. **Profiled local curvature under specified assumptions:** `W Var_w(s)`.
3. **RSI normalization:** `sqrt(Var_w(s))`, a per-observation sensitivity-spread measure.

“All local information” is only justified after specifying the observation scale, objective/loss, weights, variance assumptions, and local linearization. The production calibration appears to use MAPE/absolute relative loss rather than a conventional smooth Gaussian log-likelihood, so Fisher-information language should remain absent unless a separate likelihood is defined.

### Recommended H2

> “For `ŷ_i = I f_i(k)`, the weighted two-column log-sensitivity Gram determinant is exactly `(Σw)² Var_w(s)`. Under the corresponding local weighted least-squares geometry, profiling the level leaves curvature `Σw · Var_w(s)` in the log-rate direction. This provides a local, model-based design screen conditional on the nominal rate, observation weights, and declared model.”

### Required action

Add a concise proposition and proof, followed by explicit assumptions and failure modes. Validate the formula by automatic differentiation or finite differences, but do not present a numerical test as the proof.

---

## 3.6 The RSI design conclusions are overstated and compare unequal observation budgets

### Finding

The plan states:

> “Two well-chosen conditions beat all nine; the endpoint is the strongest lever available.”

The archived RSI is a per-observation sensitivity-spread measure. Under equal weights,

```text
RSI_total = sqrt(n) × RSI.
```

A two-condition design therefore requires more than `sqrt(9/2) ≈ 2.12` times the per-observation RSI to exceed a nine-condition design in total local separation. The reported median ratio is only `0.0131/0.0113 ≈ 1.16`. Thus the current table supports, at most, the statement that the two corners are more efficient **per observation**, not that they contain more total local separation information than all nine conditions.

The 20/40/60 g endpoint design also changes the number and type of observations. If it contains three endpoints at each condition, it must be compared on an equal-cost or equal-observation basis. Furthermore, it is a prospective simulation result under the present model, not an empirical result.

### Additional scope issue

RSI is evaluated at a nominal reference rate, apparently k = 1. Yet the widened-domain optima span approximately 0.79 to 143.5. Local sensitivity geometry can change materially with k, especially across the very shoulder that drives H1. A design ranking at k = 1 is not automatically robust over the profile domain.

### Required corrections

Replace:

> “Two well-chosen conditions beat all nine.”

with:

> “The two extreme corners provide greater local rate-sensitivity spread per observation than the full grid at the nominal rate, but the current calculation does not establish greater total information at equal budget.”

Replace:

> “the endpoint is the strongest lever available”

with:

> “within the tested prospective perturbations and the declared model, varying the collected-mass endpoint gives the largest per-observation local sensitivity spread at the nominal rate.”

### Required analyses

1. Report both **RSI** and **RSI_total**.
2. Compare designs at equal observation count and, if practical, equal experimental cost.
3. Recompute rankings at:
   - k = 1;
   - each group optimum;
   - representative points spanning each acceptable profile; and
   - the high-rate asymptote.
4. Add a synthetic-recovery experiment with plausible measurement noise and model mismatch. A useful design metric should predict actual recovery behavior, not merely local sensitivity geometry.
5. Label all unobserved endpoint designs **prospective, model-based, and local**.

---

## 3.7 Full-fit, fold-median, and widened-domain estimands are being mixed

### Finding

Several numerical results answer different questions but are presented as if one “moves” directly into another:

- Full-support, published-domain M0−M2: approximately **−0.157 pp**.
- Full-support, widened-domain M0−M2: approximately **−0.183 pp**.
- Nine-fold, published-domain median M0−M2: **−0.205 pp**.
- Numerical-envelope full-support M0−M2: approximately **−0.1572 pp**.
- Numerical-envelope full-support M1−M2: approximately **+0.4471 pp**.
- Nine-fold median M1−M2: **+0.524 pp**.

The plan says that widening the domain “moves” the refit-aware −0.205 pp result to −0.183 pp. That is not a like-for-like comparison unless the widened-domain fit is rerun inside all nine folds. The −0.183 pp value is a full-support contrast.

Likewise, G4’s +0.4471 and −0.1572 are full-support numerical-envelope estimands, not numerical verification of the 9-fold medians +0.524 and −0.205.

### Required correction

Every headline number should carry an estimand tag, for example:

- **FULL-PUB:** full calibration support, published rate domain;
- **FULL-WIDE:** full calibration support, widened rate domain;
- **LOCO-PUB:** leave-one-condition-out refit, published rate domain;
- **LOCO-WIDE:** leave-one-condition-out refit, widened rate domain;
- **NUM-FULL:** full-support numerical envelope.

### Required actions

1. Run **LOCO-WIDE** if the argument requires claiming that the fold result is not a cap artifact.
2. Otherwise weaken the statement to:
   > “In the full-support fit, widening the rate domain changes M0−M2 from −0.157 to −0.183 pp; the refit-aware result has only been computed on the published domain.”
3. Either run a numerical envelope for selected LOCO folds or state clearly that G4 establishes numerical robustness of the full-support contrasts only.

---

## 3.8 “Unbounded,” “unidentified,” and “6 of 6” are stronger than the archived result

### Finding

The widened search shows:

- a finite high-rate asymptote in the declared model;
- very small prediction change over the upper decade;
- five of six 10%-near-optimal sets right-censored at k = 500; and
- one group with a finite upper near-optimal boundary.

That supports broad or one-sided practical localization under the declared profile criterion. It does not by itself prove that the near-optimal set is mathematically unbounded above. Right-censoring at 500 means the upper endpoint was not located inside the searched domain. To claim true unboundedness, the asymptotic objective must be evaluated and shown to remain inside the near-optimal threshold as k → ∞.

Similarly, “6 of 6 groups saturate” refers to the model response approaching a high-rate limit. It is not identical to “the rate is unidentified in 6 of 6 groups.” Five of six profiles are right-censored under the selected 10% criterion; the sixth is finite.

The numerical inequality also needs correction. The plan says the top-decade movement is `<0.05%`, but the verification table reports a maximum of approximately **0.053%**. Use `≤0.053%`, “about 0.05%,” or the exact archived value.

### Required terminology

Use the following distinctions consistently:

- **structural factorization**: scale and rate enter in separable form;
- **local sensitivity collinearity**: log-rate sensitivities have low spread;
- **high-rate model asymptote**: predictions approach a finite limit as transfer becomes fast;
- **practical profile localization**: objective-based acceptable rate set is finite, broad, or right-censored;
- **structural non-identifiability**: reserve for a proof of exact non-uniqueness under the observation operator.

### Required action

Evaluate the asymptotic profiled objective for every group, preferably analytically or by a controlled high-k limit, and classify each profile as:

- finite two-sided;
- finite but broad;
- one-sided/right-censored within the tested range; or
- asymptotically admissible under the declared threshold.

Also show sensitivity to the profile threshold, not only the current 10% near-optimal rule.

---

## 3.9 H3 overstates causal attribution and excludes an untested mechanism

### Finding

H3 says that what transfers is exogenous hydraulic information, “not fitted kinetics and not particle geometry.”

The M1−M2 contrast does isolate the effect of substituting the target-grind hydraulic map for the optimal-grind map, conditional on the same fitted parameters. It does not prove that hydraulics are the only transferable mechanism. Particle geometry was frozen, not varied; therefore the analysis cannot empirically exclude a particle-geometry mechanism. It can only state that geometry is not part of the tested contrast.

The word “transfers” also needs precision. The target-grind flow map is target-side covariate information supplied at prediction time. It is not a learned source-domain quantity transferred unchanged to the target. The clean attribution is:

> “Providing target-side hydraulic metadata changes cross-grind prediction.”

### Required H3 scope

> “Conditional on the fitted level/rate and the declared model, replacing the optimal-grind hydraulic map with target-side flow information produces a large, refit-stable coarse-grind improvement. Particle geometry and other grind-dependent physics were held fixed and therefore were not tested as alternative explanations.”

### Required action

Add an information-flow diagram for M0, M1, and M2 showing exactly which source and target variables each arm receives. This will prevent “held out,” “transferred,” and “exogenous” from being used ambiguously.

---

## 3.10 Novelty must be narrowed before the title and introduction are locked

### Preliminary literature finding

A preliminary search already identifies directly adjacent work:

- Barletta et al., **“Inverse modeling of porous flow through deep neural networks: the case of coffee percolation”** (2025), explicitly frames espresso as an inverse problem and discusses local invertibility through Jacobian-rank conditions.
- Golub and Pereyra’s variable-projection/separable nonlinear least-squares work dates to 1973, with extensive subsequent literature.
- Recent espresso work by Waszkiewicz et al. (published in *Physics of Fluids* in 2026 after a 2025 preprint) emphasizes nonlinear, time-dependent pressure–flow behavior, swelling/porosity changes, and dissolution dynamics.

This does not eliminate novelty. It does eliminate any broad claim to be the first espresso inverse-problem study or to introduce profiling of a separable linear scale parameter.

### Viable novelty intersection

The strongest defensible novelty is likely the conjunction of:

1. an exact special-case sensitivity-spread identity for the whole-cup scale/rate factorization;
2. global profile behavior and a high-transfer limit in a declared espresso extraction model;
3. an empirical cross-grind ablation separating target-side hydraulics from rate fitting on named-solute whole-cup data; and
4. a prospective design screen showing how pressure/endpoint variation may increase local separation.

The novelty is therefore not “saturation exists” or “parameters can be unidentifiable.” It is the specific connection between observation-operator geometry, campaign placement, and transfer consequences in this espresso dataset/model.

### Required action

Complete G5 before drafting the introduction, title, abstract, or contribution list. At minimum search:

- espresso/coffee extraction + identifiability;
- inverse problem + coffee percolation;
- kinetic parameter estimation + whole-cup coffee;
- sensitivity/Fisher/profile likelihood + coffee extraction;
- separable nonlinear least squares + multiplicative scale parameter;
- experimental design + practical identifiability + extraction/porous media.

Use backward and forward citation searching from the directly adjacent papers. Record databases, dates, queries, inclusion criteria, and claim implications. “No first claim” is necessary but not sufficient; the paper still needs an affirmative statement of what is new.

---

## 4. Major findings and recommendations

## 4.1 The high-rate limit should be derived, not only plotted

Because the semi-discrete system is linear in state and the rate multiplier scales transfer terms, the high-rate limit should be amenable to analytical or asymptotic treatment. A derivation would elevate H1 from an empirical response-curve observation to a transparent property of the model.

Recommended work:

1. express the operator as `A(k) = A₀ + k A₁` if valid;
2. identify the fast exchange subspace and equilibrium manifold;
3. derive or characterize the `k → ∞` reduced system;
4. prove or numerically verify convergence of the outlet/whole-cup functional; and
5. identify a dimensionless transfer-to-residence ratio, rather than using the model-specific multiplier values 2, 50, and 500 as universal thresholds.

A Damköhler-like group based on transfer time versus residence/displacement time would make the shoulder physically interpretable and more transferable across conditions. With two grain classes, the relevant quantity may require more than one timescale or an effective slow mode.

## 4.2 “All Robusta groups run past the shoulder” is not established by the listed optima

The plan describes the response as nearly flat above approximately k ≈ 50, but the widened optimum for Robusta caffeine is approximately 6.34. It may still have a broad profile extending into the plateau, but the point optimum is not “past” a shoulder at 50.

Define the shoulder objectively, for example by:

- `|∂ log ŷ/∂ log k| < ε`;
- reaching 95% or 99% of the asymptotic response;
- a specified change per decade; or
- the smallest k for which the profiled objective is within a declared tolerance of its asymptote.

Then map each group’s optimum and acceptable profile relative to that definition.

## 4.3 The causal statement that the shoulder “explains” the fold result is untested

Even after correcting the fold/group error, the paper should not claim that profile placement causes the M0−M2 transfer behavior without testing the relationship.

Suggested analysis:

- for each group, calculate profile width/right-censoring, RSI, shoulder distance, and M0−M2 contribution by grind;
- examine whether weak localization predicts the difference between free-fit and fixed-rate transfer;
- report the result descriptively, with only six groups and no inferential overreach.

A negative result would be informative: freezing may help coarse transfer because of model discrepancy or hydraulic extrapolation rather than because of parameter variance alone.

## 4.4 The prior bug is not independent scientific confirmation of M0

The exact match between M0’s 8.281% and a previous bug that omitted the rate multiplier is an implementation cross-check: both computations instantiate a rate-free arm. It is not independent scientific confirmation, particularly if they share the same model, data, scoring, and prediction code.

Reword as:

> “The corrected M0 arm reproduces the score produced by the earlier omitted-rate implementation, as expected from their equivalent rate-free construction. This is a regression cross-check, not an independent validation.”

A genuinely independent confirmation would use an alternate implementation or a direct reduced expression with independently assembled inputs.

## 4.5 The oracle empirical model should remain supplementary and should not be said to “match” without a criterion

The 8.408% oracle was selected using the target score and is correctly quarantined. The statement that it “matches” 8.438% needs either:

- a predeclared practical-equivalence margin; or
- neutral wording such as “has a numerically similar target score under oracle form selection.”

The 9.670 versus 8.408 gap shows that form selection matters under target-domain extrapolation. It does not prove that nine calibration conditions cannot identify the form in a structural sense. Better:

> “Among the tested empirical forms, selection on the optimal-grind calibration support does not reproduce the target-selected form or target score under substantial fine-grind extrapolation.”

Keep this result secondary unless the paper develops a clear model-selection argument.

## 4.6 The hydraulic map itself requires uncertainty and model-form sensitivity

The target-grind “hydraulic map” is treated as known exogenous information, but the paper should document:

- how flow is measured or inferred;
- whether it is condition-level, averaged, or interpolated;
- uncertainty and repeatability;
- map functional form;
- extrapolation; and
- whether the target chemistry observations influence the map.

Since the fine-grind effect is opposite, map error or model-form mismatch is a plausible explanation. Run at least one map-form sensitivity and, if data permit, perturb flows within measurement uncertainty.

## 4.7 The design screen should include model mismatch

A design that separates parameters inside the same model can still fail when real data contain omitted physics. The proposed endpoint variation may alter wetting, flow evolution, or other processes not represented by the current operator.

The decisive experiment section should therefore distinguish:

- **model-internal separation:** simulated sensitivity/profile recovery;
- **measurement feasibility:** repeatable endpoint-resolved chemistry and flow;
- **model discrimination:** whether candidate models predict distinguishable endpoint trajectories; and
- **external validation:** whether the identified rate transfers to a new condition or measurement operator.

## 4.8 The current title is too categorical

**“What a Whole Espresso Cup Cannot See: Equilibrium-Limited Composition, Unidentifiable Kinetics, and Hydraulic Transfer”** overstates all three central nouns:

- the cup is not universally blind; the model is sensitive below the shoulder;
- “equilibrium-limited composition” sounds physically established;
- “unidentifiable kinetics” implies a physical kinetic parameter and a more general result than shown; and
- “hydraulic transfer” hides the coarse/fine asymmetry.

Recommended title:

> **When Whole-Cup Espresso Measurements Cannot Localize Extraction Rate: Saturation, Sensitivity Geometry, and Hydraulic Attribution**

Other viable options:

- **Prediction Without Kinetic Identification in Whole-Cup Espresso Models**
- **What Whole-Cup Espresso Measurements Identify—and What They Do Not**
- **Whole-Cup Espresso Prediction Without Rate Identification: Sensitivity Geometry and Cross-Grind Hydraulic Ablations**
- **A Whole-Cup Espresso Model Can Predict Without Learning Its Rate Multiplier**

The first option is the best balance of specificity, accessibility, and restraint.

---

## 5. Recommended replacement hypothesis set

## H1 — model limit and campaign placement

> **Within the declared saturated two-grain extraction model, the matched whole-cup response approaches a finite high-transfer limit. When a calibration profile extends into that plateau, the rate multiplier becomes weakly or one-sidedly localized after profiling the extractable-inventory level. In the present campaign, five of six 10%-near-optimal rate sets remain right-censored at k = 500, while one is finite.**

Interpretive boundary:

> The high-rate limit is established for the declared model; whether real espresso occupies the same regime requires external experimental validation.

## H2 — exact local geometry

> **For predictions `ŷ_i = I f_i(k)`, the weighted two-column log-sensitivity Gram determinant is exactly `(Σw)² Var_w(s)`. Under the corresponding local weighted least-squares geometry, profiling the level leaves log-rate curvature `Σw Var_w(s)`. The sensitivity spread therefore provides a local, model-based rate-separability screen conditional on the nominal rate, weights, and observation operator.**

## H3 — grind-specific hydraulic attribution

> **In this campaign, supplying target-side hydraulic metadata gives a large, refit-stable improvement for coarse-grind prediction. Fine-grind effects are small and usually opposite. The pooled hydraulic benefit is therefore coarse-driven rather than uniform across target grinds. Particle geometry and other grind-dependent physics were held fixed and were not tested as competing explanations.**

## H4 — estimation consequence

> **When whole-cup data do not localize the rate multiplier, its fitted value should not be interpreted as a learned kinetic quantity. It should be independently constrained, regularized, fixed with sensitivity analysis, or propagated over its acceptable profile. Here, fixing it at the inherited normalization improves coarse-grind transfer and is competitive in pooled error, but is not uniformly superior.**

### Optional unifying thesis

> **Whole-cup prediction and kinetic identification are different achievements. This campaign illustrates how a model can transfer useful composition predictions through target-side hydraulic information while its fitted rate multiplier remains weakly localized by the whole-cup observation operator.**

This should become the paper’s central message.

---

## 6. Required gates before substantive drafting

The present sequence says drafting can begin after R0 because G3 and G4 are closed. I recommend a revised gate sequence. The following P0 gates block the results narrative, title, abstract, and contribution claims.

| Gate | Question | Required deliverable | Pass criterion |
|---|---|---|---|
| **P0-G1 Factual reconciliation** | Are all units of analysis and numerical claims correct? | Corrected plan and generated claim table | Fold/group exception fixed; `<0.05%` corrected; full/fold estimands labeled; no unsupported “unbounded” wording |
| **P0-G2 Grind disaggregation** | Does each pooled claim survive coarse/fine decomposition? | Full-fit and 9-fold coarse/fine/group tables and figure | H3/H4 rewritten to match direction and magnitude in each grind |
| **P0-G3 Model-versus-physical scope** | Is every saturation claim correctly scoped? | Revised G3, scope table, model limitations | No statement equates exact-in-time model integration with physical validation |
| **P0-G4 Widened-domain refits** | Is the refit-aware freeze result robust to the rate cap? | LOCO-WIDE archive or explicitly weakened claim | Like-for-like comparison available, or cap-robustness claim removed |
| **P0-G5 Rate-treatment sensitivity** | Is the conclusion specific to fixing k = 1? | Fixed-anchor, regularized, free-fit, and profile-propagated comparison | H4 reflects the tested policy set; no universal freeze rule |
| **P0-G6 H2 mathematical scope** | Is the exact identity connected correctly to local curvature and RSI? | Proposition/proof, assumptions, numerical check | Determinant, Schur complement, and RSI distinguished; no unjustified Fisher/global claim |
| **P0-G7 Design robustness** | Do design rankings survive nominal-rate and equal-budget analysis? | RSI/RSI_total across k and synthetic recovery | “Corners beat grid” and “endpoint strongest” claims match equal-budget results |
| **P0-G8 Shoulder characterization** | Where is the shoulder for each group and condition? | Analytical/asymptotic limit plus response/sensitivity map | Objective criterion defined; groups located relative to shoulder without categorical misclassification |
| **P0-G9 Hydraulic information audit** | What exactly enters M0/M1/M2 and how uncertain is it? | Information-flow diagram and map sensitivity | H3 attribution is conditional and auditable; fine-grind reversal investigated |
| **P0-G10 Novelty search** | What is genuinely new relative to coffee inverse modeling and general inverse-problem methods? | Indexed search log and claim-positioning memo | Specific affirmative novelty statement; no broad first claim |

### Work that may proceed in parallel

The model description, data provenance, exact-factorization derivation, and numerical-method appendix can be prepared as controlled source material while these gates run. The results narrative, title, abstract, and discussion should wait.

---

## 7. Detailed action register

## P0 — required before the plan becomes operative

### P0-1 Correct factual and numerical statements

**Actions**

- Correct the 8/9 exception to the omitted 93.4 °C, 6 bar calibration condition.
- Separate any six-group Arabica-caffeine exception from the nine-fold result.
- Replace `<0.05%` with `≤0.053%` or “about 0.05%.”
- Replace “unbounded above” with “right-censored at k = 500” until the asymptotic objective is evaluated.
- Replace “6 of 6 rates unidentified” with the exact profile classification.
- Correct the widened-domain statement so it does not compare a full-fit contrast to a fold median.
- Label G2 as **failed sign stability / retained at a lower evidential tier**, not “passed with a caveat.”
- Replace “truth” with “exact-in-time semi-discrete reference.”
- Correct any archive metadata that describes M0−M2 as including a hydraulic-map change; M0 and M2 use the same target map in the stated construction.

**Check**

Create a machine-readable claim-to-artifact table containing estimand, unit of analysis, conditioning set, rate domain, numerical path, and rounding.

### P0-2 Produce the disaggregated refit analysis

**Actions**

- Generate coarse and fine contrasts for every fold.
- Generate variety × solute contrasts for every fold and grind.
- Visualize fold contributions and identify which groups drive the 93.4 °C, 6 bar exception.
- Put disaggregated effects on the same figure/page as pooled effects.

**Check**

A reviewer should be able to reconstruct every pooled value from the displayed components.

### P0-3 Run widened-domain LOCO refits

**Objective**

Determine whether the refit-aware M0−M2 behavior remains similar when the rate search is widened, rather than inferring this from the full-support fit.

**Pitfalls**

- computational cost;
- grid resolution at low/intermediate k;
- flat minima producing grid-dependent point optima; and
- confusing point-optimum movement with prediction movement.

**Checks**

- compare objective minima and predictions, not only fitted k;
- refine the grid around finite optima;
- record right-censoring explicitly; and
- report FULL-PUB, FULL-WIDE, LOCO-PUB, and LOCO-WIDE separately.

### P0-4 Test rate-treatment policies

**Objective**

Determine what practical recommendation follows from weak localization.

**Actions**

- fixed anchors;
- regularized rate fitting;
- free fitting;
- profile propagation; and
- optionally model averaging.

**Checks**

Predeclare anchors and penalty grid from source/scale considerations, not target performance. Report coarse/fine and group results.

### P0-5 Derive and map the high-rate limit

**Objective**

Turn the numerical response curve into a transparent model result and avoid arbitrary rate-multiplier thresholds.

**Actions**

- derive the high-k reduced system or equilibrium manifold;
- define a dimensionless transfer/residence metric;
- calculate local log-sensitivity versus that metric; and
- locate each group/condition/profile relative to an objective shoulder definition.

**Checks**

Compare analytical/reduced-limit predictions with the matrix exponential at increasingly large k and across more than the single representative center condition.

### P0-6 Repair and stress-test RSI

**Actions**

- distinguish determinant, profiled curvature, RSI, and RSI_total;
- calculate at multiple k values;
- compare equal observation budgets;
- add plausible noise;
- add at least one model-mismatch scenario; and
- test actual parameter recovery or profile contraction.

**Checks**

The ranking should not be presented as a design recommendation unless it predicts recovery/profile improvement over a declared range.

### P0-7 Audit target-side hydraulics

**Actions**

- document data provenance and uncertainty;
- identify whether each target flow is measured, inferred, or interpolated;
- perturb the map within uncertainty;
- compare at least one alternative map form; and
- examine coarse/fine reversal by condition.

**Checks**

No target chemistry may enter map selection for a held-out claim. Any oracle selection remains clearly quarantined.

### P0-8 Complete novelty positioning

**Actions**

- indexed search;
- direct comparison table against adjacent espresso inverse-modeling papers;
- direct comparison against variable projection/profile-likelihood/design literature; and
- a one-paragraph novelty statement approved before drafting.

**Check**

The contribution list should remain true if “first” and “to our knowledge” are deleted.

---

## P1 — required before submission, but may follow the initial corrected results package

### P1-1 Add an alternate implementation check for the reduced/factorized model

Use an independently assembled direct expression or small reference implementation to reproduce selected predictions and profiles. Do not count a prior bug as independent confirmation.

### P1-2 Define the observation and error model

Explain why MAPE is used, how zero/near-zero observations are handled, what weights mean, and whether the local log-sensitivity geometry corresponds to the calibration objective. Consider a robustness check with another predeclared loss.

### P1-3 Separate interpolation, extrapolation, and transfer

Quantify the target hydraulic and chemistry domain relative to calibration support. Fine-grind residence-time extrapolation should be shown graphically. Avoid calling all target evaluation “transfer” without describing its extrapolative character.

### P1-4 State a decisive external experiment

A useful proposal would collect time- or endpoint-resolved chemistry at multiple collected masses while measuring the flow/pressure trajectory and preserving independent target conditions for validation. The experiment should be designed to discriminate rate profiles, not only improve cup-level prediction.

### P1-5 Add sensitivity to the near-optimal threshold

Show profile classifications for several declared thresholds, or define an absolute practical prediction-equivalence criterion. A 10% relative increase in objective is conventional but not physically self-interpreting.

---

## 8. Recommended manuscript structure

The current structure is close, but it should not lead with a physical saturation claim or place “freezing beats fitting” before the grind-specific evidence.

### Recommended structure

1. **Introduction: prediction is not parameter identification**  
   Frame the practical problem: whole-cup accuracy is often interpreted as kinetic support, but those are distinct claims. State the espresso-specific question and narrow novelty after G5.

2. **Data, model, observation operator, and scope**  
   Define the rate multiplier as a scale on inherited transfer coefficients, not a kinetic constant. Show the target/source information flow and all omitted physics relevant to interpretation.

3. **Exact scale–rate sensitivity geometry**  
   Present the factorization, Gram determinant, profiled curvature, and assumptions. Introduce RSI and RSI_total as local design diagnostics.

4. **High-transfer limit and practical rate localization**  
   Derive the model limit, define the shoulder, show response/sensitivity curves across groups/conditions, and then present profile classifications. Keep model-structural and empirical statements separate.

5. **Cross-grind ablations: what changes prediction**  
   Present M0/M1/M2 information parity. Lead with the coarse/fine decomposition. Show refit-aware distributions and distinguish full from fold estimands.

6. **What follows—and what does not—from weak localization**  
   Compare fixed, regularized, free, and profile-propagated treatments. State that fitted k is not learned; avoid a universal freeze rule.

7. **Prospective experiments that may improve separation**  
   Present equal-budget, multi-k RSI and synthetic recovery. Clearly label endpoint designs as model-based hypotheses for future testing.

8. **Discussion**  
   Address target hydraulic uncertainty, omitted dynamic physics, one-machine scope, adjacent literature, and the difference between predictive utility and mechanistic validation.

9. **Conclusions**  
   State the narrow result: the current whole-cup operator weakly localizes rate in this model/campaign; target hydraulics mainly improve coarse transfer; better observation design is needed for kinetic inference.

### Placement of the original −0.394 pp result

Keep it in a secondary results table or historical comparison. It should not appear in the title, abstract conclusion, or first contribution bullet.

---

## 9. Recommended evidence hierarchy

The present A–E tiers are useful but several entries need reclassification.

| Proposed tier | Defensible claim | Basis and caveat |
|---|---|---|
| **A — algebraic** | Exact Gram determinant identity | Proof under declared sensitivity coordinates and weights |
| **A — numerical/model-structural** | High-rate plateau is not a BDF artifact and exists in the tested semi-discrete model | Exact-in-time temporal reference; same model/discretization; not physical validation |
| **B — refit-stable descriptive** | Target-side hydraulic map strongly improves coarse-grind prediction | Coarse M1−M2 positive in 9/9 folds; dependent folds |
| **C — heterogeneous descriptive** | Fine-grind target-map effect is small and usually opposite | Fine M1−M2 negative in 7/9 folds |
| **B/C — practical profile result** | Five of six profiles remain right-censored at k = 500 under the declared 10% criterion | Model-, objective-, threshold-, and dataset-specific |
| **C — treatment comparison** | Fixing k = 1 improves coarse transfer and is competitive pooled, but worsens fine transfer in most folds | Must be supplemented by anchor/regularization sensitivity |
| **D — local design screen** | Pressure and endpoint variation increase nominal local sensitivity spread in the tested model | Prospective; k-dependent; unequal-budget issue unresolved |
| **D — quarantined oracle** | A target-selected empirical flow form has a numerically similar score | Selection on target; not held out; supplementary only |
| **E — historical secondary** | Original model-versus-constant advantage | Weak refit stability; not a thesis |

Remove the phrase “near-deterministic” for empirical profile conclusions. The model response curve may be deterministic; the practical localization conclusion depends on data, objective, threshold, and model form.

---

## 10. Review-plan recommendations

## 10.1 Replace “executable test for every premise” with evidence-type matching

Use the following categories:

| Premise type | Appropriate assurance |
|---|---|
| Algebraic | proof plus symbolic/numerical sanity check |
| Numerical | convergence, alternate numerical path, patch-effect controls |
| Data/provenance | source reconciliation, transcription checks, lineage |
| Inferential | resampling unit, sensitivity, estimand clarity, negative controls |
| Physical | independent measurements, external literature, or explicit unvalidated assumption |
| Novelty | documented literature search and comparison |

A physical premise that cannot be tested with the current data should be marked open or scoped, not forced into a repository test that merely restates the model.

## 10.2 Revise acceptance criteria

“no defect found” is not a workable acceptance criterion. Use:

> “No unresolved critical or major finding; all other findings documented with an accepted disposition and corresponding manuscript change or scoped limitation.”

R3 cannot establish that recommendations are “not artefacts of one machine” from one-machine evidence. Replace with:

> “Recommendations are explicitly prospective and model-based; claims are scoped to the present machine/campaign; no cross-machine generalization is made without data.”

## 10.3 Do not forbid scientific correction during the editorial round

R5 may be editorial in scope, but any reviewer must remain able to flag a factual or scientific error. The rule should prevent reopening settled preferences, not suppress load-bearing corrections.

## 10.4 Expand the termination rule

A review should not close merely because no finding contradicts the tier assignment. A claim can be placed at a low tier and still be irrelevant, logically disconnected from the thesis, or non-novel.

A round closes when:

1. no unresolved critical/major issue remains within scope;
2. every finding has a documented disposition;
3. the claim–premise–evidence chain is internally consistent;
4. the contribution remains nontrivial and relevant; and
5. required changes have been verified in the manuscript/artifacts.

## 10.5 Add a claim–premise–test matrix

For every headline claim, record:

- exact wording;
- claim type and tier;
- data and observation unit;
- calibration and target information supplied;
- estimand;
- resampling unit;
- model and numerical configuration;
- supporting artifact;
- alternative explanation;
- external-validity boundary; and
- falsifying result.

This will do more for scientific reliability than another claim-scanning rule alone.

---

## 11. Specific edits to the current plan

The following substitutions should be made immediately.

### Section 1

Current concept:

> “verified on an independent integrator … lead with a physical claim”

Recommended:

> “reproduced by an exact-in-time integration of the same semi-discrete model … lead with a claim about the observation operator and model regime, with physical interpretation clearly separated from validation.”

### H1

Delete:

> “This is a claim about espresso, not about statistics.”

Replace with:

> “The high-transfer limit is a structural property of the declared model. The practical localization result is conditional on the campaign, whole-cup observation operator, calibration objective, and profile criterion. Whether real espresso occupies the same regime is an empirical question.”

Delete the explanation linking the 8/9 fold result to Arabica caffeine unless supported by a new contribution analysis.

### H2

Replace “all local information” with “all local scale–rate non-collinearity in the declared weighted log-sensitivity geometry,” then give the profiled-curvature formula separately.

### H3

Replace the pooled statement with the grind-specific version and remove “not particle geometry.” State that particle geometry was held fixed and untested.

### H4

Replace the universal freeze rule with the revised estimation-consequence hypothesis in §5.

### Section 3.1

- Replace `<0.05%` with `≤0.053%` or “about 0.05%.”
- Replace “The rate is unbounded above” with “The acceptable profile remains right-censored at k = 500” unless the asymptotic objective proves otherwise.
- Separate response saturation from profile localization.

### Section 3.2

Add the coarse/fine fold table. The pooled row cannot remain the sole headline.

### Section 3.3

- Correct the full-fit versus fold-median rate-domain comparison.
- Recast the bug match as a regression cross-check.
- State the fine-grind reversal.

### Section 3.4

Replace “matches” with “has a numerically similar target-selected score” and replace “cannot identify” with a narrower form-selection instability statement.

### Section 3.5

- Report RSI_total.
- Remove “two conditions beat all nine.”
- Label endpoint variation prospective and model-based.
- State nominal k and repeat across the profile range.

### Section 3.6

Rename to:

> **The high-rate plateau is a property of the declared semi-discrete model, not a BDF floor**

Replace “physical,” “measurement,” “truth,” and “independent path” where they imply independent physics. “Independent temporal-integration path” is accurate.

### Section 4

Rebuild the evidence hierarchy using §9 of this review.

### Section 6

- G2: **FAILED sign stability; result retained at lower tier.**
- G3: revised model-structural question.
- G5: still open as a systematic indexed search, but preliminary adjacent literature must already inform the plan.

### Section 7

Change the title and structure. Put the coarse/fine ablation before the practical recommendation about fixing or fitting.

### Section 8

Revise acceptance and termination criteria as in §10.

### Section 9

Un-retire the physical-validity risk. Retire only the BDF-artifact risk.

### Section 10

Do not state that “no numerical objection remains open” unless the claim is limited to the tested temporal and mesh envelope. More importantly, the unresolved scientific and estimand issues block drafting even if the numerical checks are complete.

---

## 12. Suggested contribution statement after the required work

A defensible contribution paragraph could read:

> “This study separates predictive transfer from kinetic parameter identification in a whole-cup espresso extraction model. First, it derives an exact sensitivity-spread identity for the multiplicative inventory–rate factorization and relates it to profiled local curvature. Second, it shows that the declared model approaches a finite high-transfer limit and that five of six campaign profiles remain right-censored under the stated practical criterion. Third, refit-aware cross-grind ablations show that target-side hydraulic metadata provides a large, stable benefit for coarse-grind prediction, while fine-grind effects are small and often opposite. Finally, model-based design analyses identify endpoint and pressure variation as candidates for experiments intended to localize the rate multiplier. These results are scoped to the present model, observation operator, machine, and campaign and do not constitute physical validation of a universal espresso kinetic constant.”

This is much stronger than the present “physical saturation + freeze the parameter” framing because every clause maps to a distinct, auditable result.

---

## 13. Final recommendation

### Decision

**Proceed with the pivot, but do not adopt the current plan verbatim and do not begin the manuscript results narrative until the P0 corrections and analyses are complete.**

### Most important strategic change

The paper should not be organized around the proposition that espresso kinetics have been physically shown to saturate and therefore should be frozen. It should be organized around the more defensible and more broadly useful proposition that:

> **whole-cup predictive performance does not demonstrate kinetic identification, and the information channel responsible for transfer can be isolated and may differ sharply by target grind.**

### Expected outcome

With the recommended corrections, Paper 1 can become a genuinely interesting paper about:

- observation-operator limitations;
- prediction without parameter identification;
- exact local sensitivity geometry;
- global profile behavior;
- grind-specific hydraulic attribution; and
- the design of measurements that could actually test the kinetic parameter.

Without those corrections, the redraft is likely to be challenged for physical overclaiming, pooled-effect concealment, categorical estimation advice, and novelty overstatement.

---

## 14. Sources reviewed and preliminary adjacent literature

### Repository sources

- [Paper 1 pivot and redraft plan](https://github.com/trbrewer/puckworks/blob/main/docs/paper1_resource/PAPER_1_PIVOT_AND_REDRAFT_PLAN.md)
- [Rate-domain check artifact](https://github.com/trbrewer/puckworks/blob/main/docs/paper1_resource/PAPER_A_RATE_DOMAIN_CHECK.json)
- [Ablation refit-stability artifact](https://github.com/trbrewer/puckworks/blob/main/docs/paper1_resource/PAPER_A_ABLATION_REFIT_STABILITY.json)
- [Design-separability artifact](https://github.com/trbrewer/puckworks/blob/main/docs/paper1_resource/PAPER_A_DESIGN_SEPARABILITY.json)
- [Saturation-verification artifact](https://github.com/trbrewer/puckworks/blob/main/docs/paper1_resource/PAPER_A_SATURATION_VERIFICATION.json)
- [Numerical-envelope artifact](https://github.com/trbrewer/puckworks/blob/main/docs/paper1_resource/PAPER_A_NUMERICAL_ENVELOPE.json)
- [Rate-domain check producer](https://github.com/trbrewer/puckworks/blob/main/tools/paper_a_rate_domain_check.py)
- [Ablation refit-stability producer](https://github.com/trbrewer/puckworks/blob/main/tools/paper_a_ablation_refit_stability.py)
- [Information-parity producer](https://github.com/trbrewer/puckworks/blob/main/tools/paper_a_information_parity.py)
- [Design-separability producer](https://github.com/trbrewer/puckworks/blob/main/tools/paper_a_design_separability.py)
- [Saturation-verification producer](https://github.com/trbrewer/puckworks/blob/main/tools/paper_a_saturation_verification.py)
- [Numerical-envelope producer](https://github.com/trbrewer/puckworks/blob/main/tools/paper_a_numerical_envelope.py)

### Preliminary literature relevant to novelty and scope

- Barletta, A., Cuomo, S., Egidi, N., Giacomini, J., & Maponi, P. (2025). [Inverse modeling of porous flow through deep neural networks: the case of coffee percolation](https://arxiv.org/abs/2511.11194). arXiv:2511.11194.
- Golub, G. H., & Pereyra, V. (1973). [The Differentiation of Pseudo-Inverses and Nonlinear Least Squares Problems Whose Variables Separate](https://doi.org/10.1137/0710036). *SIAM Journal on Numerical Analysis*, 10, 413–432.
- O’Leary, D. P., & Rust, B. W. (2012). [Variable Projection for Nonlinear Least Squares Problems](https://www.nist.gov/publications/variable-projection-nonlinear-least-squares-problems).
- Waszkiewicz, R., Myck, F., Białas, Ł., Puciata-Mroczynska, M., Dzikowski, M., Szymczak, P., & Lisicki, M. (2026). [Under pressure: poroelastic regulation of flow in espresso brewing](https://doi.org/10.1063/5.0319611). *Physics of Fluids*, 38, 063113. Preprint: [arXiv:2512.21528](https://arxiv.org/abs/2512.21528).

**Literature note:** This was a targeted preliminary screen for review purposes, not a substitute for the systematic indexed novelty search required by P0-G10.

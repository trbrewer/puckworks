# Paper 1 — recommended scientific pivot and detailed revision execution plan

**Prepared:** 1 August 2026  
**Primary response reviewed:** `docs/paper1_resource/PAPER_1_DOMAIN_REFEREE_RESPONSE.md`  
**Current manuscript reviewed:** `docs/submission/PAPER_A_JFE_MANUSCRIPT.md`  
**Repository state reviewed:** merge commit `eaa3ee7e4930c053e16254ea254fe6073e0032b2`  
**Prior domain review:** `paper1_domain_referee_review_20260731.md`

---

## 1. Executive decision

I would **pivot the paper deliberately and unambiguously**. I would not spend the next revision trying to rescue a positive claim that the mechanistic model has demonstrated superior cross-grind predictive skill. The new analyses in the response show that this is not the most defensible or interesting scientific story:

- the pooled advantage combines opposite coarse- and fine-grind outcomes;
- the margin falls from approximately 0.39 percentage points against the level-only constant to approximately 0.25 percentage points against a more capable empirical response;
- even that 0.25-point margin is an upper bound because the empirical arm does not yet receive the target-grind hydraulic information available to the mechanistic arm; and
- after all arms are refitted, the sign of the model-versus-constant difference changes with the omitted calibration condition.

Those findings do not damage the paper if they are made central. They reveal a more important result:

> **Acceptable held-out whole-cup prediction does not, by itself, identify espresso extraction kinetics or establish incremental mechanistic value. What can be learned depends on the observation operator and on whether the measurements create distinct sensitivity directions for extractable inventory and extraction rate.**

The paper should therefore become a study of **what different espresso measurements can and cannot identify**, using the cross-grind exercise as a real, adversarial example of the distinction between:

1. absolute endpoint accuracy;
2. parameter localization;
3. incremental skill over an equal-information non-mechanistic predictor; and
4. validation of a physical mechanism.

The constructive contribution should be stronger than “whole cups are weak and fractions are better.” The exact multiplicative structure already present in the manuscript supports a more general and more novel result:

> **Rate separability is controlled by variation in the rate-sensitivity direction across observations. Time-resolved fractions are one way to create that variation, but deliberately varied endpoints, flows, temperatures, pressures, or an independent inventory measurement can do the same.**

That should be the paper’s main engineering insight.

### Recommended central title

**What Can a Whole Espresso Cup Identify? Observation Operators, Parameter Compensation, and Experimental Design in Extraction Models**

More conventional alternatives are:

- **Whole-Cup Accuracy Can Conceal Kinetic Non-Identifiability in Espresso Extraction Models**
- **Observation-Operator Control of Inventory–Rate Identifiability in Espresso Extraction Models**
- **Why Whole-Cup Prediction Does Not Validate Espresso Extraction Kinetics**

The first title is my preference because it is memorable without sounding like a slogan, contains “espresso,” poses the correct scientific question, and leaves room for a nuanced answer rather than presupposing that every cup-integrated design is uninformative.

---

## 2. Assessment of the domain-referee response

The response is scientifically strong. It does four things that materially improve confidence in the work:

1. **It reports adverse results first.** The coarse/fine asymmetry and refit-aware sign instability are not hidden behind pooled statistics.
2. **It corrects the interpretation rather than merely softening wording.** “Cross-grind transfer” is now described as conditional outcome transfer with frozen particle geometry and target-grind hydraulics.
3. **It distinguishes completed from incomplete work.** The numerical-envelope attempt is not converted into evidence after the run failed to produce an archived artifact.
4. **It records a consequential implementation defect.** The initial refit-aware implementation omitted the rate multiplier and would have yielded a false 9-of-9 sign-stability result. The no-fold-dropped recovery check caught it.

This is an excellent response posture. It also means the scientific decision is now clearer than it was at the time of the original review.

### 2.1 What the response has established

The following statements are now well supported within the declared model and data:

- Whole-cup calibration leaves a broad inventory–rate compensation profile.
- A matched collection endpoint materially changes the apparent blind residual.
- Absolute coarse/fine endpoint errors can remain moderate despite weak localization of the inventory–rate split.
- The observed pooled mechanistic advantage is small, heterogeneous by grind, and sensitive to the benchmark.
- The fixed-fit pooled advantage is not stable to refitting on different subsets of the nine calibration conditions.
- The present test does not validate a physical grind mechanism because target grind enters mainly through hydraulics and the endpoint while particle geometry is frozen.
- Fraction-resolved observations carry more rate-shape information than the currently used sampled-window aggregate and the same-model exact-cup control.

### 2.2 What remains scientifically unresolved

The following questions still prevent the current draft from reaching its strongest form:

1. **Direct empirical fraction-versus-complete-cup contrast:** measured complete cups exist for the Schmieder campaign, but the model has not yet been profiled against those measured cups over the same rate sweep used for the measured fractions.
2. **Truly equal information:** the strongest empirical benchmark still lacks the hydraulic variable available to the mechanistic model.
3. **Attribution:** the paper has not separated the contribution of target-grind hydraulics, target-specific rate recalibration, and the remaining mechanistic structure.
4. **Observation-design mechanism:** the manuscript explains sensitivity collinearity qualitatively but does not yet convert it into a quantitative design diagnostic and prospective experiment-selection result.
5. **Load-bearing numerical coverage:** the stiffest and most important panels have not been certified, and numerical-Jacobian warnings remain active in the 5-CQA case.
6. **Novelty positioning:** the indexed, reproducible novelty search acknowledged in the manuscript has not yet been completed.

### 2.3 Consequence for the manuscript

The response should not lead to another round of adding caveats around the existing Section 4. It should trigger a change in hierarchy:

- **Promote:** observation-operator information, inventory–rate separability, and experimental design.
- **Retain but compress:** the matched-endpoint and held-out cross-grind case as an empirical demonstration that prediction and mechanism validation are different questions.
- **Demote:** the numerical size of the 0.25–0.39 percentage-point pooled advantage.
- **Remove as a central objective:** proving that the mechanistic model “wins” the cross-grind comparison.

The paper will be more compelling if the fair conclusion is that the current endpoint experiment **cannot adjudicate mechanistic superiority**, rather than if it expends substantial space defending a marginal and unstable advantage.

---

## 3. Recommended scientific thesis and contribution hierarchy

### 3.1 Central thesis

The paper should argue and demonstrate the following:

> In an espresso extraction model whose output factorizes into an extractable-inventory level and a rate-dependent response, whole-cup observations can support accurate endpoint prediction while weakly separating inventory from rate. The local ability of an experimental design to separate those quantities is governed by the diversity of its rate sensitivities. A real held-out coarse/fine case shows that acceptable aggregate prediction can coexist with no stable incremental advantage over fair non-mechanistic alternatives. Time-resolved fractions, deliberately varied process histories, or independent inventory constraints can create the missing sensitivity contrast.

This thesis has four linked parts:

1. **Analytical mechanism:** exact multiplicative factorization and sensitivity geometry.
2. **Real-data manifestation:** broad profiles under whole-cup calibration.
3. **Validation paradox:** acceptable held-out endpoint error but fragile incremental mechanistic advantage.
4. **Constructive resolution:** measurement designs that increase rate-sensitivity diversity.

### 3.2 Claim hierarchy

The manuscript should use a strict hierarchy.

### Demonstrated

- The inventory parameter is an exact multiplicative level in the declared model.
- Whole-cup calibration under the tested conditions produces broad, often boundary-reaching inventory–rate profiles.
- Observation-window mismatch can manufacture a large apparent prediction error.
- Absolute held-out endpoint accuracy can coexist with weak parameter localization.
- The pooled model advantage is grind-dependent and unstable under calibration refitting.

### To be demonstrated in the next analysis

- The precise empirical difference between measured fraction profiles and measured complete-cup profiles on the same Schmieder experiments.
- The quantitative link between rate-sensitivity diversity and profile localization.
- The minimum or near-minimum observation subsets that recover most of the rate-separation information.
- The model’s incremental endpoint value, if any, against a hydraulically equal empirical baseline.

### Not to be claimed

- Structural non-identifiability of espresso extraction kinetics in general.
- Universal inability of whole-cup experiments to identify rate parameters.
- Validation of a physical grind-change mechanism.
- A statistically calibrated confidence interval or equivalence conclusion from nine dependent calibration folds.
- Superiority of time resolution as the only useful experimental strategy.
- General validity of the fitted rate multiplier as an intrinsic material or kinetic constant.

### Motivated

- A general reporting discipline for food-process inverse problems.
- Model-based design of espresso experiments using sensitivity diversity.
- Fraction selection, endpoint variation, flow perturbation, and independent inventory assays as alternative routes to stronger parameter separation.

---

## 4. Revised research questions

I would replace the current three research questions with the following four.

1. **What combination of extractable inventory and extraction rate is constrained by whole-cup espresso measurements under the tested design?**
2. **Why does the observation design leave those quantities weakly separated, and can that weakness be predicted from the model’s local sensitivity geometry?**
3. **Does acceptable held-out whole-cup prediction provide evidence of incremental mechanistic skill when compared with equal-information empirical alternatives and after refitting uncertainty is propagated?**
4. **Which feasible measurement designs—complete cups across varied conditions, timed fractions, multiple endpoints, or independent inventory constraints—most effectively create the rate-sensitivity contrast needed to localize the rate?**

These questions are outcome-neutral. They remain publishable whether the mechanistic model wins, ties, or loses the fair benchmark and whether measured complete cups are flat, moderately informative, or strongly informative.

---

## 5. The core analytical result to add: observation-design separability

This is the highest-value conceptual addition because it turns a careful case report into an engineering result with prospective value.

### 5.1 Exact local relation

The manuscript already writes the prediction as

\[
\widehat y_i(I,k)=I f_i(k),
\]

where \(I\) is the extractable-inventory level and \(k\) is the rate multiplier. Define log-parameters

\[
a=\log I, \qquad b=\log k,
\]

and the local log-rate sensitivity

\[
s_i=\frac{\partial\log f_i(k)}{\partial\log k}.
\]

On a relative or log-response scale, the local sensitivity row for observation \(i\) is

\[
\mathbf{s}_i=[1,\ s_i].
\]

For nonnegative observation weights \(w_i\), the local Gram matrix is

\[
G=S^{\mathsf T}WS
=
\begin{bmatrix}
\sum w_i & \sum w_i s_i\\
\sum w_i s_i & \sum w_i s_i^2
\end{bmatrix}.
\]

Its determinant is

\[
\det(G)
=
\left(\sum_i w_i\right)
\left[\sum_i w_i(s_i-\bar s_w)^2\right]
=
\left(\sum_i w_i\right)^2\operatorname{Var}_w(s),
\]

where \(\bar s_w=\sum w_i s_i/\sum w_i\). Equivalently, after profiling the level direction, the local information or curvature remaining for \(b=\log k\) is proportional to

\[
\mathcal S_k
=
\sum_i w_i(s_i-\bar s_w)^2.
\]

This gives an exact local criterion for this parameterization:

- if all observations have the same rate sensitivity, the two sensitivity columns are collinear and the rate cannot be separated locally from the inventory level;
- separation improves as the rate sensitivities spread apart;
- adding many observations with nearly identical \(s_i\) increases sample count but adds little directional information;
- two carefully chosen observations with widely separated sensitivities can be more useful than many redundant observations.

For an original-scale sum-of-squares objective, the same result holds after incorporating the appropriate prediction-scale factors into the weights. The manuscript should state that this is a **local, model-based separability diagnostic**, not a universal Fisher-information result unless a noise model is explicitly assumed.

### 5.2 Proposed terminology

Use one clear term throughout. I recommend:

**Rate-separability index**

\[
\mathrm{RSI}=\sqrt{\frac{\sum_i w_i(s_i-\bar s_w)^2}{\sum_i w_i}}.
\]

This normalized form describes sensitivity diversity independently of the number of observations. Also report the unnormalized quantity

\[
\mathrm{RSI}_{\mathrm{total}}=\sqrt{\sum_i w_i(s_i-\bar s_w)^2},
\]

which incorporates the amount of data under the chosen weights. The normalized and total measures answer different questions:

- **RSI:** how non-redundant is the design?
- **Total RSI:** how much local rate-separation information does the complete design provide under the adopted weighting?

Do not describe either as a confidence measure. Profile-based results remain the nonlinear empirical check.

### 5.3 Numerical implementation

For every candidate observation and fitted panel:

1. evaluate \(f_i(k)\) at the reference or profiled optimum;
2. estimate \(s_i\) with a centred finite difference in \(\log k\);
3. repeat with half and double the log step;
4. record the maximum change in \(s_i\);
5. compute the weighted mean, variance, RSI, total RSI, column cosine, smallest singular value, and condition number;
6. compare those local quantities with the actual nonlinear profile width and edge-to-minimum ratio.

The finite-difference step should be selected before examining which design “wins.” A sensible default is one quarter to one half of the current geometric rate-grid spacing, with a step-convergence check.

### 5.4 Candidate designs to compare

Compute the diagnostic and full nonlinear profile for the following designs.

### Existing empirical designs

- Angeloni optimal-grind complete cups across the nine calibration conditions.
- Schmieder measured complete cups across the matched experiments.
- Schmieder measured fractions across the same experiments.
- Waszkiewicz time-resolved TDS fractions.

### Retrospective reduced fraction sets

- early fraction only;
- middle fraction only;
- late fraction only;
- early + late;
- early + middle + late;
- every other measured fraction;
- all fractions;
- equal-count random fraction subsets for comparison.

### Prospective model-based designs

- two or more collected-mass endpoints from the same shot class;
- complete cups at deliberately varied flow rates or residence times;
- complete cups at varied temperature and pressure combinations;
- a complete cup plus an independent inventory measurement;
- fractions plus an inventory measurement;
- selected flow-profile perturbations.

The prospective designs may use synthetic observations, but they must be labeled as model-based design analysis rather than experimental validation.

### 5.5 Robust design selection

A design chosen at one fitted rate may be fragile. Therefore optimize designs over a declared uncertainty set rather than at a single point only.

For each solute and plausible rate \(k\) in the current near-optimal set:

1. compute the candidate observation sensitivities;
2. calculate RSI for each feasible subset;
3. rank subsets by the minimum RSI across the uncertainty set, or by the mean log determinant with the minimum reported separately;
4. require the selected design to perform reasonably for all three solutes rather than being optimal only for caffeine;
5. repeat under the source geometry alternatives and plausible flow perturbations already used in the paper.

This yields a practical result such as:

> “An early and a late fraction retained X% of the full design’s model-based rate-separation information across all three solutes, whereas three adjacent middle fractions retained only Y%.”

The exact result must come from the analysis; the paper should not assume in advance that early and late are optimal.

### 5.6 Validation of the design diagnostic

The RSI analysis should earn its place in the main paper only if it passes the following checks:

- designs with larger RSI generally have narrower nonlinear profiles;
- the ranking is stable to finite-difference step, objective weighting, and reasonable parameter perturbations;
- discrepancies between the local diagnostic and nonlinear profiles are identified and explained rather than averaged away;
- the metric does not merely reproduce observation count;
- reduced fraction subsets are compared with equal-count controls;
- the result is reported per solute before any pooled summary.

If the local metric fails to predict nonlinear profile behavior in important panels, that is itself a useful result: local sensitivity geometry is insufficient in the strongly nonlinear or boundary-censored regime. The paper should then present RSI as a screening tool, not as a complete design criterion.

---

## 6. Highest-priority empirical analysis: measured fractions versus measured complete cups

This is the most important unfinished analysis. It should replace the sampled-window aggregate as the principal empirical evidence in Section 5.

### 6.1 Objective

Determine, on the **same Schmieder experiments**, how strongly measured complete-cup concentrations and measured time-resolved fractions localize the rate after profiling a common inventory level.

The existing exact-cup simulation is a useful positive control, but it is an inverse crime. The sampled-window aggregate is not a complete cup and differs materially from the measured cup. The available measured cup data remove both limitations.

### 6.2 Data audit and pairing manifest

Create a machine-readable manifest with one row per experiment and fields for:

- experiment identifier;
- coffee and roast identifier;
- temperature;
- pressure or flow condition;
- particle-size or grind condition;
- dose;
- complete-cup endpoint or brew ratio;
- fraction time or mass windows;
- complete-cup replicate count;
- fraction replicate count;
- solute;
- units;
- source table, file, row, and column;
- missingness and exclusion reason;
- whether the cup and fractions are from the same physical extraction, paired replicate set, or merely the same nominal condition.

The last distinction is essential. “Same campaign” is not automatically “same shot.” The paper must state the actual pairing level.

Before model fitting, verify:

- unit consistency;
- whether the measured complete cup is a direct assay or reconstructed from fractions;
- whether fraction volumes or durations cover the full shot;
- whether replicate-level measurements are available or only summaries;
- whether cup and fraction endpoints are exactly matched;
- whether any fraction lies below quantification limits;
- whether TDS and named-solute measurements share the same sampling basis.

### 6.3 Common model sweep

For each solute:

1. define the same geometric rate grid for cup and fraction analyses;
2. solve the model under each experiment’s actual condition;
3. compute the predicted concentration over each measured fraction window;
4. compute the exact model-predicted complete-cup concentration over the measured endpoint;
5. at each rate, profile **one common inventory level** across the complete set of experiments for that scoring target;
6. score the measured fractions and measured cups separately;
7. retain identical parameter bounds and solver settings.

The point is not to force the cup and fraction objectives to have the same minimum error. The point is to compare the width, boundary behavior, and stability of the rate profile after each design has been allowed the same inventory-level freedom.

### 6.4 Primary and robustness objectives

Use a smooth primary objective for profile geometry and retain MAPE as a reader-familiar prediction metric.

Recommended hierarchy:

- **Primary profile objective:** relative-L2 or replicate-weighted SSE where source uncertainty permits.
- **Robustness:** MAPE and Huber.
- **Descriptive fit metric:** macro-MAPE at the optimum.

If complete-cup replicate variance is available, perform both:

- replicate-level fitting, with experiments retained as clusters; and
- mean-level fitting, with uncertainty-weighted residuals.

Do not give the many fraction observations an unacknowledged numerical advantage. Report both average loss and profile curvature/width, and include equal-count fraction subsets.

### 6.5 Required outputs

For each solute and design, archive:

- optimum rate and inventory;
- minimum objective and MAPE;
- 2%, 5%, 10%, and 20% near-optimal rate intervals;
- whether each interval reaches a tested boundary;
- profile range ratio;
- log-rate width of the 10% set;
- RSI and total RSI;
- objective-family sensitivity;
- leave-one-experiment-out optimum and width;
- replicate/cluster bootstrap summaries if the source replication supports them;
- exact observations and predictions used in each panel.

The main paper should show normalized profiles \(J(k)/J_{\min}\) so cup and fraction shapes can be compared even when their absolute residual scales differ.

### 6.6 Controls needed to isolate time resolution from observation count

At minimum, include:

1. **All measured fractions versus all measured cups.** This compares the actual experimental designs.
2. **Equal-count fraction control.** Select one fraction per experiment or an equal number of fraction observations to the cup design.
3. **Minimal informative subset.** Use the RSI analysis to select two or three fractions without using measured concentrations.
4. **Random equal-count subsets.** Show where the selected subset lies relative to random subsets.
5. **Synthetic exact-cup control.** Retain the current same-model analysis in the supplement as a mechanistic explanation, not the main empirical proof.
6. **Sampled-window aggregate.** Retain only as a warning that an incomplete temporal aggregate is not an adequate proxy for a complete cup.

### 6.7 Outcome-dependent interpretation

The paper should precommit to the following interpretation branches.

### Outcome A: measured cups are nearly flat; measured fractions are sharp

This directly supports the proposed thesis. State that, in this campaign and model, temporal fractions create rate-sensitivity diversity that complete cups do not.

### Outcome B: measured cups contain some information but fractions are substantially sharper

This is arguably the best result. It supports the more general thesis that information depends on design diversity, not simply on the label “cup” or “fraction.” Report which process-condition contrasts make the cup design informative.

### Outcome C: measured cups are as informative as fractions

Reverse the current temporal-superiority claim. The central result becomes:

> multi-condition complete-cup experiments can separate rate from inventory when their rate sensitivities differ sufficiently; temporal fractionation is one efficient route but is not intrinsically required.

This would still be novel and useful.

### Outcome D: both designs are weak

Conclude that the current model/data combination does not identify the rate, even with the available fractions. Investigate model discrepancy, fraction timing, loss weighting, and whether the rate parameterization is too coarse. Do not retain a positive identification claim.

---

## 7. Complete the equal-information comparison

The current temperature/pressure empirical benchmark is a major improvement, but the response correctly states that it remains information-disadvantaged. The next comparison must close that gap.

### 7.1 Principle

Every held-out comparator must receive all non-response information available to the mechanistic model at prediction time, including the scalar hydraulic quantity actually used by the solver.

If the mechanistic calculation uses a constant flow derived from a target-grind pressure–flow map, the empirical comparator should receive that same derived flow, shot time, hydraulic conductance, or residence-time summary. It does not need access to latent model states, but it must not be denied the target-domain covariate that drives the mechanistic prediction.

### 7.2 Recommended empirical family

With only nine optimal-grind calibration conditions per variety–solute group, keep the family small and predeclared. Standardize variables using calibration data only.

Candidate predictors should include:

1. constant;
2. temperature;
3. pressure;
4. log flow or log residence time;
5. temperature + pressure;
6. temperature + log residence time;
7. pressure + log residence time;
8. temperature + pressure + log residence time;
9. one predeclared low-order interaction, only if leave-one-condition-out selection supports it.

Because pressure and derived flow may be strongly dependent, inspect condition numbers and extrapolation. A simpler family using temperature and residence time may be preferable if it represents the actual information channel more directly.

Select the family by leave-one-optimal-condition-out validation **within the calibration corpus only**, refit it to all nine calibration conditions, and freeze it before coarse/fine responses are read.

### 7.3 Leakage and support checks

Retain and extend the current perturbation test:

- multiply or permute held-out concentrations and verify that family selection and coefficients do not change;
- verify that predictor standardization uses calibration values only;
- report whether coarse/fine hydraulic inputs lie outside the optimal-grind calibration range;
- flag extrapolative predictions;
- archive the design matrix and selected family for every group;
- recover the no-fold-dropped published scores before any resampling result is accepted.

### 7.4 Mechanistic ablation panel

Add the following mechanistic arms.

### M0 — source-rate, level-only recalibration

- Keep the source rate multiplier fixed at its inherited value.
- Fit only the inventory level on optimal-grind observations.
- Predict coarse/fine using target hydraulics.

This tests whether target-specific rate recalibration contributes meaningful held-out value.

### M1 — fitted rate and level, common hydraulic map

- Fit rate and level on optimal grind.
- Apply the same optimal-grind hydraulic map or a declared common map to coarse and fine.

This removes the principal target-grind information channel.

### M2 — fitted rate and level, target hydraulic map

- This is the current canonical mechanistic arm.

The contrasts have direct interpretations:

- **M0 to M2:** combined value of rate recalibration and any interaction with hydraulics.
- **M1 to M2:** value supplied by target-grind hydraulics.
- **M0 to M1:** value of fitting the rate under a common hydraulic assumption.
- **M2 versus hydraulically equal empirical model:** incremental value of the mechanistic response shape after information parity.

Do not fit any parameter to coarse or fine concentrations in these held-out arms.

### 7.5 Reporting

The primary display should be an attribution plot or compact table, not another single pooled score. Report:

- coarse;
- fine;
- pooled;
- each variety–solute group;
- number of observations on which each arm is best;
- fold-level refit-aware paired differences;
- concentration-scale error as well as MAPE.

The paper should make the following outcome-neutral commitment:

- if the hydraulically equal empirical model matches or beats M2, conclude that no incremental mechanistic endpoint skill has been demonstrated;
- if M2 retains a stable advantage, describe it as incremental endpoint prediction skill, not identification or validation of the rate mechanism;
- if M1 and M2 differ materially, emphasize that the apparent cross-grind skill is largely hydraulic transfer;
- if M0 and M2 are similar, state that rate recalibration adds little held-out value.

### 7.6 Do not manufacture a practical margin

The source lacks condition-specific uncertainty for the named solutes. Do not introduce an arbitrary equivalence margin merely to produce a categorical conclusion. Instead:

- report the effect in percentage points of MAPE;
- report the corresponding concentration-error distribution;
- compare the result with any independently documented analytical repeatability only if the source supports that comparison;
- state whether the observed difference would change any plausible recipe, equipment, or process decision;
- avoid “statistically significant,” “equivalent,” or “non-inferior” language.

---

## 8. Refit-aware stability: retain, simplify, and make diagnostic

The corrected leave-one-calibration-condition-out analysis is more informative than the fixed-predictor percentile ranges for the central scientific question. It should move into the main results; much of the four-scheme fixed-predictor resampling can move to the supplement.

### 8.1 Main analysis

For each of the nine omitted optimal-grind conditions:

1. refit the mechanistic rate and level;
2. reselect and refit every empirical benchmark family;
3. refit the level-only constant;
4. score the unchanged complete coarse/fine corpus;
5. record pooled, grind-specific, and group-specific paired differences;
6. record fitted rate, inventory, and empirical-family selection.

Plot all nine fold results. Do not summarize them only by median and range. Label the omitted temperature/pressure condition so the reader can see which parts of the calibration design drive the sign reversal.

### 8.2 Calibration leverage analysis

Calculate for each omitted condition:

- change in fitted rate;
- change in fitted inventory;
- change in model-minus-benchmark error;
- leverage in the empirical design matrix;
- whether the omitted condition is a temperature or pressure corner;
- whether it controls extrapolation toward coarse or fine hydraulic states.

This can convert “the sign is unstable” into an engineering explanation of which calibration conditions are missing.

### 8.3 Optional subset-stability analysis

Because the expensive PDE responses can be cached at unit inventory over the rate grid, a descriptive calibration-size analysis may be computationally inexpensive after the forward library exists.

For 6-, 7-, and 8-of-9 calibration-condition subsets:

- refit all arms;
- score the fixed coarse/fine corpus;
- plot the distribution of paired differences versus calibration size;
- identify whether stability improves monotonically;
- keep this analysis in the supplement unless it reveals a clear design result.

Do not present these dependent subset results as calibrated frequentist uncertainty.

### 8.4 Disposition of current uncertainty material

Retain the primary fixed-predictor clustered range as a sensitivity result, but compress the main-text treatment to one paragraph. Move the four cluster schemes, seed checks, endpoint sweep, and most loss variants to the supplement. Their purpose is to show that the fixed-fit comparison is not a numerical artifact; they do not answer the more important refit-aware question.

---

## 9. Numerical strategy: fix the solver path before buying more compute

The response measured a roughly twenty-fold cost increase for the stiff 5-CQA cell and reproduced numerical-Jacobian overflow/invalid-value warnings. Before running a large envelope with the same implementation, I would examine whether the semi-discrete problem permits a substantially better reference solution.

### 9.1 Exploit the linear structure

For fixed temperature, flow, geometry, and rate multiplier, the declared governing equations are linear in the concentration state. After spatial discretization, the system has the form

\[
\dot{\mathbf y}=A\mathbf y+\mathbf b,
\]

with a sparse, largely banded matrix. This creates two high-value options.

### Option 1 — exact sparse Jacobian for BDF

Construct the analytical sparse Jacobian directly from the discretized advection and interphase-transfer operators. The Jacobian is fixed during a constant-condition solve. This should:

- remove finite-difference Jacobian overflow warnings;
- reduce repeated RHS evaluations;
- improve stiffness handling;
- make failure modes easier to diagnose;
- reduce the cost of 5-CQA sweeps.

### Option 2 — independent matrix-exponential reference

For constant-coefficient cases, solve the affine linear system with a sparse matrix exponential, for example by augmenting the state with a constant component or shifting by the steady state. `expm_multiply` or an equivalent Krylov action can return the state at fraction boundaries and the cup endpoint without stepping through every intermediate time.

This would provide an independent numerical path against which the BDF result can be checked. It is particularly attractive for the Angeloni and constant-flow Schmieder cases. Time-varying external-flow cases can remain on BDF or be treated piecewise if justified.

### 9.2 Required implementation checks

Whichever path is adopted:

- construct small-grid matrices explicitly and compare the matrix RHS with the existing function RHS state by state;
- compare analytical and finite-difference Jacobian-vector products;
- verify the inlet boundary treatment;
- verify that the unit-inventory response scales exactly with inventory;
- check global solute balance;
- check positivity or characterize any small discretization undershoot;
- verify monotone accumulated volume and mass;
- compare BDF and matrix-exponential outputs for representative conditions;
- retain warning counts and solver-status fields in every archive.

### 9.3 Load-bearing numerical envelope after the pivot

The envelope should follow the revised claim hierarchy. Priority cases are:

1. Arabica 5-CQA optimal grind, because it is stiff and contributes strongly to the apparent coarse-grind advantage;
2. one Arabica 5-CQA coarse and one fine prediction;
3. Robusta 5-CQA optimal grind, because its residual structure is conspicuous;
4. one representative caffeine panel for continuity with the existing sweep;
5. the measured Schmieder fraction-versus-cup profile case;
6. the external time-varying-flow TDS case;
7. one boundary-censored rate-profile case.

For each case, cross:

- 100, 200, and 400 axial nodes;
- tolerances 10⁻⁵, 10⁻⁶, and 10⁻⁷;
- existing BDF and the independent reference path where applicable.

Archive:

- endpoint concentration;
- selected fraction concentrations;
- global mass balance;
- optimum rate;
- 10% profile width;
- profile range ratio;
- RSI;
- model-minus-benchmark MAPE where relevant;
- runtime and solver diagnostics.

### 9.4 Numerical acceptance rule

The criterion should be tied to the scientific conclusion, not an arbitrary concentration tolerance.

A numerical result is adequate only if discretization, tolerance, and solver-path changes:

- do not change the qualitative classification of a profile as broad, sharp, or boundary-censored;
- do not change which measurement design is more informative;
- do not change the sign of any mechanistic-versus-baseline conclusion presented as meaningful;
- move paired benchmark differences by much less than the effect being discussed; and
- preserve mass balance and physical state checks.

If numerical variation is comparable to the approximately 0.06–0.25 percentage-point benchmark contrasts, remove those contrasts as quantitative evidence of mechanistic advantage. The paper does not need them to support the stronger observation-design thesis.

---

## 10. Flow-map sensitivity: reduce its role unless the ablation makes it important

The response proposes a broad flow-map form family. I would not make this the next major workstream automatically. First run M1 versus M2.

### If M1 and M2 are nearly identical

The target hydraulic map is not a load-bearing source of the held-out result. State the limited sensitivity and keep the broader flow-map family as future work.

### If M1 and M2 differ materially

Then the hydraulic representation is central and requires a compact structural sensitivity panel:

1. current Darcy-style map;
2. direct nominal-shot-time flow;
3. common map across grinds;
4. one nonlinear pressure–flow family with predeclared exponent or compliance parameter;
5. one representative time-varying flow profile if data support it.

Report how each form changes:

- endpoint prediction;
- fitted rate and inventory;
- model-minus-baseline difference;
- coarse/fine asymmetry;
- profile width.

Do not claim that a ±20% magnitude perturbation validates the form of the map. Magnitude and structural form are different questions.

---

## 11. Structured novelty search and positioning

The current manuscript correctly refuses to claim a systematic novelty search that has not been performed. Complete that search before finalizing the contribution statement.

### 11.1 Databases

At minimum:

- Scopus;
- Web of Science Core Collection;
- Engineering Village/Compendex;
- Crossref or Dimensions for DOI-level recall;
- Google Scholar for citation chasing and preprints;
- arXiv and relevant institutional repositories for recent work.

### 11.2 Query families

Run and archive searches such as:

- `espresso AND (identifiability OR "practical identifiability" OR "profile likelihood" OR "parameter compensation")`
- `espresso AND ("inverse problem" OR "inverse modelling" OR "inverse modeling")`
- `("coffee extraction" OR espresso) AND ("parameter estimation" OR kinetic*) AND (model OR simulation)`
- `espresso AND ("experimental design" OR "optimal design" OR "time-resolved" OR "fraction-resolved")`
- `("coffee percolation" OR "coffee brewing") AND (Jacobian OR sensitivity OR identifiability)`
- `(food extraction OR food process) AND (identifiability OR "profile likelihood" OR "parameter compensation")`

Record database, exact query, date, result count, screening decisions, and included papers.

### 11.3 Adjacent work that must be distinguished

The revision should explicitly position itself relative to:

- established espresso forward models and extraction-optimization studies;
- time-resolved named-solute experiments;
- recent time-resolved infiltration and poroelastic-flow measurements;
- the 2025 preprint on inverse reconstruction of brewing conditions from cup composition;
- the mature practical-identifiability and optimal-experimental-design literature;
- parameter-estimation guidance in food engineering.

The likely defensible novelty statement is not that the paper invents identifiability analysis. It is:

> This is an applied espresso study that combines an exact inventory–rate factorization, nonlinear profile analysis, matched observation operators, equal-information held-out benchmarking, and model-based measurement-design analysis to show why endpoint accuracy does not by itself validate extraction kinetics.

Use “to our knowledge” only after the search record supports it. Avoid “first” unless the screening is decisive.

---

## 12. Proposed manuscript architecture

The current manuscript is approximately 18,000 words before references and gives disproportionate space to the weak cross-grind advantage and its many caveats. I would target a substantially tighter main text, with most audit detail in the supplement.

### 12.1 Proposed title and abstract logic

### Title

**What Can a Whole Espresso Cup Identify? Observation Operators, Parameter Compensation, and Experimental Design in Extraction Models**

### Abstract sequence

1. Whole-cup predictions are commonly interpreted as validation of extraction physics.
2. The tested model factorizes exactly into inventory level and rate-dependent response.
3. Derive the rate-separability criterion from variation in local rate sensitivities.
4. Show broad profiles under whole-cup calibration.
5. Show that matched endpoints repair a large observation mismatch but do not identify the rate.
6. Report that held-out endpoint accuracy is acceptable while incremental advantage is small, grind-dependent, benchmark-sensitive, and refit-unstable.
7. Report the direct measured fraction-versus-cup result and design analysis.
8. Conclude with practical measurement recommendations.

The abstract should not lead with “8.4% versus 8.8%.” That number is now supporting evidence for the validation paradox, not the headline contribution.

### 12.2 Section outline

### 1. Introduction — the validation paradox

- Why whole-cup outcomes are attractive.
- Why good aggregate prediction can be mistaken for mechanism validation.
- Inventory–rate compensation in extraction models.
- Gap in espresso modeling: observation design and practical parameter separation.
- Four research questions.
- Contribution stated in outcome-neutral terms.

### 2. Model, data, and observation-design theory

#### 2.1 Reduced two-grain extraction model

Keep the governing equations and physical scope concise. Move extended source-model audit details to the supplement.

#### 2.2 Data and analytical roles

One table should identify calibration, held-out endpoint, measured fraction, measured cup, and external TDS datasets.

#### 2.3 Observation operators

Define exact complete-cup, fraction-window, sampled-window, and external TDS operators.

#### 2.4 Exact inventory factorization and rate-separability criterion

Present the proposition, derivation, RSI, and relationship to profiled objectives.

#### 2.5 Profile and benchmark methods

Describe profiling, equal-information comparators, refit-aware stability, and losses without reproducing every resampling detail.

#### 2.6 Numerical methods and verification

Report the improved Jacobian/reference path and the load-bearing envelope.

### 3. Whole-cup calibration constrains an inventory–rate combination

- Matched endpoint versus mismatched operator.
- Profile surfaces and boundary-reaching sets.
- Sensitivity geometry and RSI for the Angeloni cup design.
- Prediction stability along the profile valley.

### 4. Endpoint accuracy does not establish incremental mechanism

- Complete held-out coarse/fine errors.
- Coarse/fine asymmetry.
- Equal-information empirical baseline.
- M0/M1/M2 ablation attribution.
- Fold-level refit stability.
- One concise conclusion: the endpoint experiment does or does not demonstrate incremental mechanistic skill, stated according to the final result.

This section should be much shorter than the current Section 4.

### 5. Which measurements recover rate information?

- Direct measured Schmieder fractions versus measured complete cups.
- Equal-count and minimal-fraction controls.
- RSI versus nonlinear profile width.
- Independent external TDS stress test, read at the weaker loss.
- Prospective design map: fractions, multiple endpoints, varied flows, inventory anchor.

### 6. Discussion

- Prediction, localization, and mechanism validation are different.
- Observation design—not measurement label alone—controls separability.
- Implications for espresso model calibration and equipment/recipe studies.
- Limits imposed by reduced physics and existing data.
- What a future decisive experiment should measure.

### 7. Conclusions

A short, direct conclusion with no repeated numerical caveats.

### 12.3 Internal word targets

These are editorial targets, not venue requirements:

- Abstract: 220–260 words.
- Introduction: 1,000–1,300 words.
- Methods: 2,500–3,000 words.
- Results: 3,500–4,500 words.
- Discussion and limitations: 1,500–2,000 words.
- Conclusion: 200–300 words.

Target main-text length: approximately 9,000–11,000 words before references.

---

## 13. Figure and table plan

### 13.1 Main figures

### Figure 1 — What the observation operator preserves

Panels:

A. Schematic of puck model, outlet trajectory, timed fractions, and complete-cup integration.  
B. Exact factorization \(\widehat y=If(k)\).  
C. Sensitivity vectors for two nearly redundant cup observations and two separated fraction observations.  
D. Geometric interpretation of the inventory–rate valley.

Purpose: establish the paper’s central mechanism before presenting any score.

### Figure 2 — Whole-cup compensation and matched-observable correction

Panels:

A. Two-dimensional objective surface for the representative panel.  
B. Profiled objective with near-optimal sets.  
C. Predictions along the valley showing stable cup output despite moving parameters.  
D. Mismatched versus matched collection endpoint residual.

Purpose: show why an optimizer can return a precise point without the experiment strongly localizing it.

### Figure 3 — The endpoint-validation paradox

Panels:

A. Held-out observed versus predicted concentrations.  
B. Model-minus-comparator error by coarse and fine grind.  
C. Hydraulically equal empirical and mechanistic-ablation comparison.  
D. Nine fold-level refit-aware differences, labeled by omitted calibration condition.

Purpose: show that acceptable absolute prediction and incremental mechanism evidence are different.

### Figure 4 — Measured fractions versus measured cups

Panels:

A–C. Normalized rate profiles for caffeine, trigonelline, and 5-CQA, with measured fractions and measured complete cups on the same axes.  
D. Profile width or RSI summary across solutes and objectives.  
E. Equal-count and minimal-fraction subset comparison.

Purpose: provide the direct empirical observation-design result currently missing.

### Figure 5 — Prospective espresso measurement design

Panels:

A. Rate sensitivity as a function of fraction time or collected mass.  
B. RSI for candidate measurement designs.  
C. Fraction-subset efficiency relative to the full design.  
D. Effect of an independent inventory constraint on the rate profile.

Purpose: convert the diagnostic result into an actionable experiment-design recommendation.

If journal space is tight, combine Figures 4 and 5 and move the external TDS plot to the supplement.

### 13.2 Main tables

### Table 1 — Datasets, observation operators, and inferential roles

One row per dataset/analysis with columns for source, measured quantity, time resolution, calibration/validation role, parameter refitting, and claim ceiling.

### Table 2 — Parameter localization and design separability

Per solute/design: optimum rate, 10% profile width, boundary status, RSI, and total RSI.

### Table 3 — Held-out benchmark and ablation results

Per grind and pooled: mechanistic arms, equal-information empirical arm, MAPE, paired difference, worse-on count, and refit sign stability.

All large group-level tables, cluster schemes, endpoint sweeps, rate-grid checks, solver diagnostics, and source audits should move to the supplement.

---

## 14. Detailed disposition of current manuscript material

### 14.1 Retain in the main text

- The exact multiplicative inventory factorization.
- The observation-operator definitions.
- The matched endpoint correction.
- The broad profile and boundary-reaching tolerance sets.
- The coarse/fine asymmetry.
- The equal-information and refit-aware findings.
- The conditional nature of the cross-grind test.
- The direct measured fraction-versus-cup result once completed.
- One concise external TDS stress test.
- The major physical limitations.

### 14.2 Expand or replace

- Expand the sensitivity-collinearity paragraph into the formal separability result.
- Replace the sampled-fraction aggregate as main evidence with measured complete cups.
- Replace the temperature/pressure-only “equal-information” label with a hydraulically equal benchmark.
- Replace the current long cross-grind narrative with an attribution panel.
- Replace generic future-experiment recommendations with the quantified design map.
- Replace the abstract with one centered on the validation paradox and observation design.

### 14.3 Move to the supplement

- Four fixed-predictor cluster schemes and full seed diagnostics.
- Full endpoint-tolerance sweep.
- Full loss-family tables.
- In-sample per-grind comparator ladder.
- Geometry alternatives and most ±20% flow-scale details.
- Full numerical warning inventory.
- Source-transcription and numeral-binding audits.
- Same-model exact-cup robustness family.
- Complete external TDS alignment and first-bin variants.
- Detailed parameter tables and source-model provenance.

### 14.4 Remove or sharply reduce

- Repeated paragraphs explaining that an uncalibrated range crossing zero proves neither presence nor absence. State this once clearly.
- Repeated “standing position” passages.
- Any implication that −0.394 percentage points is the paper’s principal scientific result.
- Any residual language suggesting transfer of grind physics.
- Claims that time resolution is uniquely necessary.
- Repository-governance detail that does not affect the scientific argument.

---

## 15. Implementation architecture and reproducible artifacts

The scientific work should be implemented through a small number of producer modules with explicit result contracts, not through manual notebook calculations.

Suggested components, adapted to the repository’s existing naming conventions:

1. **Measured-cup profile producer**
   - reads the paired Schmieder manifest;
   - generates exact cup and fraction predictions;
   - profiles inventory at every rate;
   - emits per-solute profiles and replicate-aware summaries.

2. **Observation-design separability module**
   - computes log-rate sensitivities;
   - evaluates RSI and matrix diagnostics;
   - searches feasible observation subsets;
   - validates finite-difference convergence.

3. **Hydraulically equal benchmark module**
   - creates calibration-only predictor matrices;
   - performs leave-one-condition-out family selection;
   - freezes and scores held-out data;
   - implements leakage perturbation checks.

4. **Mechanistic ablation producer**
   - runs M0, M1, and M2 from a common response library;
   - reports attribution by grind and group.

5. **Refit stability producer**
   - refits all arms under each omitted calibration condition;
   - verifies no-fold-dropped recovery;
   - emits fold-level parameter and score changes.

6. **Numerical reference and envelope producer**
   - supports analytical Jacobian and/or matrix-exponential reference;
   - writes complete diagnostic artifacts;
   - fails closed if warnings or conservation criteria are not characterized.

7. **Figure-data producer**
   - reads only archived result contracts;
   - exports one tidy table per figure panel;
   - does not recompute scientific results inside plotting code.

Each result archive should contain:

- repository commit;
- environment;
- source file hashes;
- exact data-manifest hash;
- model configuration;
- rate grid and parameter domain;
- objective definition;
- solver configuration;
- result values;
- warning and failure counts;
- command used to reproduce the artifact.

The tooling should continue using the no-fold-dropped recovery test that caught the omitted-rate bug. Add similarly simple invariants wherever possible:

- unit-inventory scaling is exactly linear;
- measured-cup and fraction operators integrate the same outlet trajectory over their declared windows;
- complete-cup prediction equals the full-window integral on synthetic constant-flow tests;
- held-out response perturbation cannot alter benchmark selection;
- M1 equals M2 when the target and common hydraulic maps are deliberately made identical;
- analytical Jacobian matches finite-difference directional derivatives on small cases.

---

## 16. Staged execution plan and decision gates

Do not rewrite the manuscript in earnest before the first three analytical gates are complete. Otherwise the text will continue to chase moving results.

### Stage 0 — Freeze the current evidentiary state

Actions:

- tag or record the current merge commit;
- preserve the current manuscript, supplement, response, and result archives;
- create a scientific-revision branch;
- write a one-page claim ledger containing only the current supported claims and unresolved questions.

Gate 0:

- current published numbers reproduce;
- response findings reproduce;
- no planned analysis requires target-response leakage.

### Stage 1 — Direct measured fraction-versus-cup analysis

Actions:

- build and verify the pairing manifest;
- implement the common rate sweep and exact observation operators;
- run all three named solutes;
- run equal-count and minimal-fraction controls;
- archive complete profiles.

Gate 1:

- measured cup and fraction results are based on the same declared experiments and model settings;
- every exclusion is traceable;
- profile conclusions survive at least two sensible objectives;
- result is interpretable under one of Outcomes A–D in §6.7.

This gate determines whether the temporal argument remains, is narrowed, or is reversed.

### Stage 2 — Observation-design separability

Actions:

- derive and unit-test the exact local relation;
- calculate sensitivities and RSI;
- compare RSI with nonlinear profiles;
- identify minimal fraction subsets;
- evaluate prospective endpoint, flow, and inventory-anchor designs.

Gate 2:

- finite-difference sensitivities converge;
- RSI is not merely a proxy for observation count;
- local rankings broadly agree with nonlinear profile behavior or discrepancies are understood;
- design recommendations are robust across solutes and plausible parameter values.

This gate determines whether the paper has a genuinely constructive experimental-design result.

### Stage 3 — Equal-information benchmark and mechanistic attribution

Actions:

- add the hydraulic variable to the empirical family;
- run M0/M1/M2;
- rerun all nine refit folds;
- report per-grind and per-group outcomes;
- assess extrapolation and leverage.

Gate 3:

- all arms recover their full-calibration reference scores;
- held-out perturbation leaves fitting unchanged;
- no baseline receives less exogenous information than the mechanistic arm;
- the manuscript can state, without qualification games, whether incremental endpoint skill is demonstrated, unresolved, or absent under the tested comparison.

### Stage 4 — Numerical reference and envelope

Actions:

- implement analytical Jacobian and/or independent linear-system reference;
- resolve or characterize 5-CQA warnings;
- run the load-bearing envelope;
- compare paired scientific quantities, not only state variables.

Gate 4:

- numerical choices do not alter the qualitative scientific conclusions;
- all load-bearing results have archived diagnostics;
- any precise small benchmark contrast retained in the paper is substantially larger than numerical variation.

### Stage 5 — Structured novelty search

Actions:

- run the declared database queries;
- screen and archive results;
- update related work and the novelty statement;
- distinguish recent inverse coffee-percolation work.

Gate 5:

- every novelty phrase is supported by the search record;
- no “first” claim rests on an informal search.

### Stage 6 — Rewrite from a blank outline

Actions:

- do not edit the existing manuscript paragraph by paragraph;
- create the new section skeleton in §12;
- write the analytical contribution and measured-cup result first;
- insert the cross-grind case as supporting evidence;
- move diagnostics to the supplement;
- regenerate abstract, highlights, figures, and conclusions last.

Gate 6:

- each main-text section answers one research question;
- every main figure advances the central argument;
- the paper can be summarized without mentioning the 0.394-point result first;
- the conclusion remains correct under every fair benchmark outcome.

### Stage 7 — Adversarial scientific rereview

Review the revised manuscript as four different referees:

1. food-process modeler;
2. inverse-problem/parameter-estimation specialist;
3. espresso experimentalist;
4. skeptical statistical reviewer.

Required questions:

- Is the measurement-design result genuinely supported by measured data?
- Is equal information truly equal?
- Is any refitted quantity mislabeled as held out?
- Does a local sensitivity result get overextended into a global theorem?
- Are model-based design recommendations clearly separated from empirical validation?
- Does the numerical evidence cover every load-bearing panel?
- Are the physical omissions compatible with the narrowed claims?

---

## 17. Predeclared outcome matrix

The paper should be designed so that every plausible result produces an honest, interesting conclusion.

| Result | Scientific conclusion | Manuscript action |
|---|---|---|
| Fractions much sharper than measured cups | Temporal resolution creates substantial rate-sensitivity diversity in this campaign | Keep temporal contrast central |
| Cups moderately informative, fractions sharper | Multi-condition cups retain some rate information; fractions improve it | Emphasize sensitivity diversity, not a cup/fraction binary |
| Cups as sharp as fractions | Integrated observations can identify rate when conditions are sufficiently diverse | Reverse the “fractions are required” claim; retain design theory |
| Both cups and fractions broad | Rate parameterization/model discrepancy prevents localization | Recast as a negative identifiability case and identify needed independent constraints |
| Hydraulically equal empirical model matches/beats mechanism | No incremental mechanistic endpoint value demonstrated | State this directly; use as evidence for the validation paradox |
| Mechanistic model wins stably after information parity | Modest incremental endpoint skill demonstrated | Report as secondary; do not call it kinetic validation |
| Common and target hydraulic maps give similar results | Hydraulic transfer is not load bearing | Drop broad flow-form campaign from main paper |
| Target map drives most of the gain | Apparent transfer is principally hydraulic | Reframe the cross-grind result as hydraulic covariate transfer |
| Numerical variation changes benchmark sign | Small benchmark contrast is not scientifically resolved | Remove it as positive evidence |
| RSI predicts profile width | Exact local geometry provides a useful design screen | Make design analysis a principal contribution |
| RSI fails in nonlinear/boundary cases | Local design metrics require profile confirmation | Present the failure and a two-stage design workflow |

This matrix should be retained internally during analysis so that no result is subconsciously steered toward a preferred narrative.

---

## 18. Provisional rewritten claim set

The final numbers will determine the wording, but the paper should aim for claims of this form.

### Claim 1

In the declared model, extractable inventory is an exact multiplicative level. After profiling that level, local rate information is governed by the weighted variation of the observations’ log-rate sensitivities.

### Claim 2

The tested optimal-grind whole-cup design produces insufficient rate-sensitivity diversity to tightly localize the inventory–rate split, even though it admits a numerical optimum and predicts held-out endpoints with moderate absolute error.

### Claim 3

Matching the measured collection endpoint corrects a large observation-operator error but does not validate the fitted kinetics.

### Claim 4

The held-out mechanistic advantage is small, heterogeneous by grind, benchmark-sensitive, and unstable to calibration refitting; therefore the present endpoint test does not establish incremental mechanistic value unless the hydraulically equal analysis changes that result.

### Claim 5

The measured fraction-versus-cup analysis shows exactly how much rate information temporal resolution adds in the source campaign; the wording will follow Outcomes A–D rather than presupposing superiority.

### Claim 6

A small set of deliberately selected measurements can recover much of the model-based rate-separation information, providing concrete guidance for future espresso experiments.

---

## 19. Provisional highlights

Pending the direct measured-cup result, suitable highlights would be:

- Whole-cup accuracy did not imply localized espresso extraction kinetics.
- Inventory–rate separation depended on variation in rate sensitivity.
- Fair benchmarks made the apparent cross-grind advantage small and unstable.
- Timed or deliberately varied measurements supplied the missing direction.
- A model-based design metric identified efficient measurement combinations.

These should be updated to comply with the current journal character limit at submission.

---

## 20. What not to do

1. **Do not try to “win” the benchmark by adding increasingly favorable mechanistic comparisons.** The paper is stronger if the fair result is neutral or negative.
2. **Do not retain the level-only constant as the sole headline comparator.** It remains a useful minimal ablation.
3. **Do not call the current temperature/pressure response fully equal-information.** It is not, while the model receives target hydraulics.
4. **Do not use the sampled-window aggregate as the main empirical proxy for a whole cup.** Measured cups exist.
5. **Do not present the same-model exact-cup simulation as empirical confirmation.** It is a mechanism check and positive control.
6. **Do not infer absence of value from a range crossing zero or claim value from a small negative point estimate.**
7. **Do not defend a 0.06-point refit-aware effect with an enormous numerical campaign if the paper no longer needs that effect.** Verify load-bearing conclusions instead.
8. **Do not say whole cups contain no rate information in general.** Multiple conditions or endpoints can create sensitivity diversity.
9. **Do not say time resolution is the only solution.** Independent inventory assays, varied endpoints, and flow perturbations may also separate the parameters.
10. **Do not call the fitted multiplier a physical rate constant.** It scales inherited Sherwood prefactors and absorbs model conventions and discrepancy.
11. **Do not claim physical grind-mechanism transfer.** Geometry is frozen in the canonical calculation.
12. **Do not add more governance machinery as a substitute for science.** Add only checks that can falsify a load-bearing result.
13. **Do not rewrite incrementally around the current Section 4.** Rebuild the narrative from the new research questions.
14. **Do not claim novelty from author awareness alone at submission.** Complete the structured search.

---

## 21. Venue recommendation

The revised paper remains well suited to the **Journal of Food Engineering** if it foregrounds:

- an engineering model of a food process;
- rigorous parameter-estimation and validation logic;
- direct implications for measurement design;
- practical consequences for espresso experiments, recipe studies, and model-based optimization.

The observation-design pivot improves venue fit because it provides a clear engineering application rather than a purely methodological warning. If the final manuscript becomes dominated by general inverse-problem theory and contains little direct food-process design guidance, *Computers & Chemical Engineering* would become a plausible alternative. I would, however, continue targeting JFE unless the empirical measured-cup analysis fails to support any useful espresso-specific conclusion.

---

## 22. Final acceptance criteria for the revised paper

I would regard the manuscript as ready for external submission only when all of the following are true.

### Scientific coherence

- One central thesis governs the title, abstract, results, and conclusion.
- Cross-grind prediction is supporting evidence, not a competing paper inside the paper.
- The direct measured-cup result is complete.
- The conclusion is outcome-neutral and follows the actual fair benchmark.

### Information fairness

- The strongest empirical comparator receives the same exogenous hydraulic information as the mechanistic model.
- All family selection occurs on calibration data only.
- Target-response perturbation cannot change a fitted predictor.
- Every refit is labeled as a refit.

### Identification logic

- The exact separability relation is derived correctly.
- Local sensitivity diagnostics are not confused with global identifiability.
- Nonlinear profiles validate or qualify the local design ranking.
- Whole-cup, fraction, and inventory-anchor claims are scoped to their actual designs.

### Numerical credibility

- 5-CQA and temporal-profile cases have archived numerical checks.
- Jacobian warnings are resolved or shown not to alter the relevant outputs through an independent path.
- Numerical variation is smaller than any quantitative contrast retained as meaningful.
- Conservation and physical-state checks pass.

### Presentation

- Main text is materially shorter and more focused than the current draft.
- Every main figure answers one research question.
- The abstract does not lead with the marginal pooled benchmark difference.
- Repetitive caveats and audit prose are moved to the supplement.
- The title contains “espresso” and states the scientific issue rather than a promotional tagline.

### Novelty and reproducibility

- The indexed novelty search is archived.
- Recent adjacent inverse-coffee work is discussed accurately.
- Every reported number has a reproducible producer and data contract.
- The final manuscript, supplement, figure data, and code resolve to one release commit and DOI.

---

## 23. Bottom-line recommendation

The response confirms that the paper should **not** be abandoned and should **not** be forced back toward its former positive transfer narrative. It has uncovered a more interesting result than the one it originally tried to establish.

The most compelling paper is now:

> a real-data demonstration that aggregate predictive accuracy, parameter identification, and mechanistic validation are not interchangeable; an exact explanation of the observation geometry that causes the distinction; and a constructive design analysis showing which espresso measurements recover the missing information.

The next revision should therefore proceed in this order:

1. run the direct measured fraction-versus-complete-cup profile comparison;
2. turn the exact inventory factorization into a quantitative observation-design separability result;
3. close the hydraulic information gap and complete the mechanistic ablations;
4. certify the load-bearing numerical cases with an improved or independent solver path;
5. complete the structured novelty search; and
6. rewrite the manuscript from a new outline, with the cross-grind result compressed into a validation-paradox case study.

This route does not depend on obtaining a favorable mechanistic benchmark result. It produces a scientifically useful paper under every plausible outcome and is the most direct path to a genuinely novel, compelling contribution.

---

## Sources reviewed and relevant adjacent literature

- [Paper 1 domain-referee response](https://github.com/trbrewer/puckworks/blob/eaa3ee7e4930c053e16254ea254fe6073e0032b2/docs/paper1_resource/PAPER_1_DOMAIN_REFEREE_RESPONSE.md)
- [Current Paper 1 manuscript](https://github.com/trbrewer/puckworks/blob/eaa3ee7e4930c053e16254ea254fe6073e0032b2/docs/submission/PAPER_A_JFE_MANUSCRIPT.md)
- [Current Paper 1 supplement](https://github.com/trbrewer/puckworks/blob/eaa3ee7e4930c053e16254ea254fe6073e0032b2/docs/submission/PAPER_A_JFE_SUPPLEMENT.md)
- Schmieder et al. (2023), *Influence of Flow Rate, Particle Size, and Temperature on Espresso Extraction Kinetics*.
- Waszkiewicz et al. (2026), *Under pressure: Poroelastic regulation of flow in espresso brewing*, DOI `10.1063/5.0319611`.
- Foster et al. (2025), *Dynamics of liquid infiltration into an espresso bed using time-resolved X-ray imaging*.
- Barletta et al. (2025), *Inverse modeling of porous flow through deep neural networks: the case of coffee percolation*, arXiv `2511.11194`.
- Dolan (2013), *Parameter Estimation in Food Science*, DOI `10.1146/annurev-food-022811-101247`.
- Bernaerts et al. (2000), *On the design of optimal dynamic experiments for parameter estimation in predictive microbiology*.
- Brun et al. (2001), *Practical identifiability analysis of large environmental simulation models*.
- Raue et al. (2009), profile-likelihood methods for practical identifiability.
- Wieland et al. (2021), practical-identifiability assessment in dynamical models.


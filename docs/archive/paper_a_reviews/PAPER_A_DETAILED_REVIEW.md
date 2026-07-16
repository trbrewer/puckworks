# Detailed technical review of `PAPER_A_DRAFT.md`

**Repository:** [`trbrewer/puckworks`](https://github.com/trbrewer/puckworks)  
**Manuscript reviewed:** [`docs/PAPER_A_DRAFT.md`](https://github.com/trbrewer/puckworks/blob/main/docs/PAPER_A_DRAFT.md)  
**Review date:** 2026-07-12  
**Recommendation:** **Major revision before journal submission**

---

## 1. Scope, review basis, and limitations

This review covers the current `main`-branch manuscript, all six Paper A figures, the principal analysis and plotting modules, the repository’s data representations, its reproducibility scaffolding, and the primary literature needed to audit the manuscript’s data descriptions and statistical claims. In particular, I examined:

- `docs/PAPER_A_DRAFT.md`
- `puckworks/validation/slow/angeloni_bracket.py`
- `puckworks/validation/slow/identifiability.py`
- `puckworks/validation/slow/external_waszkiewicz.py`
- `puckworks/figures_paper_a.py`
- `puckworks/models/pannusch2024/solver.py`
- the derived Schmieder kinetics table used by the repository
- `pyproject.toml`
- `docs/literature_search/`
- `docs/figures/paper_a/fig1_design.png` through `fig6_fraction_vs_endpoint.png`

The review is directed at the corrected matched-beverage-mass manuscript version. The repository history shows a substantial revision sequence on 2026-07-12, including the matched-mass correction and regeneration of the six figures. That correction materially changed the cross-grind conclusion, so comments below apply to the corrected version rather than to the superseded fixed-time interpretation.

I performed a static audit of the manuscript, code paths, cached outputs, figures, source data representation, and primary references. I did **not** independently rerun every multi-minute PDE sweep in a clean, locked environment. The repository currently lacks a frozen Paper A release, fully pinned environment, and one complete end-to-end paper-build command, so numerical values are assessed for internal consistency and implementation provenance rather than claimed as independently reproduced here. The review therefore separates:

1. **implementation defects or manuscript/code contradictions**, which can be established statically;
2. **statistical or interpretive limitations**, which require revised analysis or wording; and
3. **numerical robustness questions**, which require reruns at additional grids, domains, seeds, or uncertainty models.

Line numbers cited below refer to the retrieved manuscript and Python files on the review date. They may move as the repository changes; freeze a commit or release before responding to this review.

---

## 2. Executive assessment

The paper has a potentially valuable central message: **good whole-cup prediction, parameter identifiability, and transfer are different properties**, and a mechanism can remain weakly localized even when predictions are stable. The matched-endpoint correction is scientifically important and is disclosed unusually transparently. The distinction between named solutes and source-specific aggregate-solids proxies is also strong. The repository has the beginnings of an excellent reproducibility package.

However, the manuscript is not yet ready for submission because several quantitative claims are generated or presented under inconsistent contracts:

- Section 2.6 says the profiles are **profiled MAPE objectives**, but the formal identifiability panel and Figure 2 actually use **unweighted concentration-scale SSE**, an SSE-optimal inventory, and an SSE Hessian.
- The reported inverse-Hessian “parameter correlation” is presented like a statistical correlation even though no likelihood or error model is specified.
- The leave-one-condition-out “95% CI” is created by independently resampling 54 dependent out-of-fold errors. It is not a conventional confidence interval for generalization error, and “shot-level bootstrap” is not an accurate description of the analyzed experimental units.
- Figure 3 and Figure 4 label concentration as `mg/g`, while the Angeloni source data and the corresponding code path use `g/L` (numerically equivalent to `mg/mL`, not to `mg/g` without a density conversion).
- The manuscript says all Result 1 tests use matched 40 g cups, but the pooled species-envelope bracket still defaults to a fixed 25 s integration interval.
- “Measured flow” is claimed for the cross-grind transfer although the implementation uses a constructed flow map based on assumed grind-specific shot times, fitted hydraulic-conductivity polynomials, and viscosity correction.
- The geometry sensitivity applies each geometry globally to all grinds; it does not test a grind-specific geometry map. The current conclusion overstates what this sensitivity establishes.
- The external Waszkiewicz analysis is an external-data objective-profile exercise with a target-profiled level and rate sweep, not a fully frozen external prediction. Its integrated-cup profile is exactly flat by algebraic construction from one observation and one free level.
- The paper-build function claims to run every slow analysis, but omits several results used in the manuscript, including the blind bracket, flow refinement, refit summary, geometry sensitivity, sampled-aggregate audit, and external Waszkiewicz analysis.

These are fixable. The qualitative conclusion that inventory and kinetic rate are **practically compensating under the tested endpoint design** appears plausible and is worth pursuing. The quantitative identifiability metrics, uncertainty language, data provenance, evidence labels, and figure contracts must be corrected before the result can be considered reliable enough for publication.

### Recommended editorial disposition

| Dimension | Assessment |
|---|---|
| Scientific significance | Potentially high for mechanistic espresso-model evaluation and experimental design |
| Conceptual contribution | Strong: separates endpoint accuracy, parameter localization, and transfer |
| Current quantitative validity | Not yet adequate because objectives, uncertainty, and units are inconsistent |
| Current reproducibility | Promising repository structure, but incomplete and not frozen |
| Recommendation | **Major revision** |

---

## 3. Principal strengths to preserve

1. **The matched-endpoint correction is exemplary scientific practice.** The manuscript openly states that an earlier fixed-time comparison produced a misleading cross-grind failure and that the conclusion reversed after matching beverage endpoint. This is exactly the kind of provenance and self-correction that should be retained, though moved to an appropriate methods/history note rather than an internal banner in the submission manuscript.

2. **The paper’s conceptual separation is valuable.** The distinction among practical identifiability, predictive transfer, and endpoint error is clear and important. The observation that predictions may be stable along a compensating parameter manifold is a useful counterweight to the common assumption that parameter uncertainty necessarily implies poor prediction.

3. **The exact MAPE level solution is a thoughtful implementation choice.** Where MAPE is genuinely the objective, using the weighted median of condition-specific level ratios is preferable to an arbitrary grid search and should remain part of the methods.

4. **Named solutes are kept separate from TDS/total-solids proxies.** The manuscript correctly recognizes that the Pannusch TDS pseudo-component, Angeloni gravimetric total solids, and Waszkiewicz optical TDS are not an interchangeable fourth molecule. That semantic discipline should be retained and applied equally strictly to evidence labels.

5. **Limitations are often stated candidly.** The draft acknowledges the in-sample nature of the Schmieder positive control, the sampled-window aggregate problem, the single-coffee/single-grind scope of the Waszkiewicz analysis, and the lack of a calibrated cross-grinder map.

6. **The repository contains unusually good review provenance.** Commit messages document observable-contract corrections, the matched-mass regeneration, the external TDS addition, and the figure build. With a frozen release and complete build, this could become a strong reproducibility asset.

---

## 4. Required-action matrix

Priority definitions:

- **P0 — validity-critical:** must be resolved before submission because it changes the interpretation or numerical support for a central claim.
- **P1 — major reporting/reproducibility:** required for a defensible submission, but unlikely by itself to reverse the core qualitative conclusion.
- **P2 — clarity/editorial:** should be corrected in the submission manuscript and figures.

| ID | Priority | Required action | Acceptance criterion |
|---|---:|---|---|
| AR-01 | P0 | Make the identifiability objective internally consistent. | The manuscript, code, cached results, and Figure 2 all state exactly which objective is profiled. MAPE, SSE, and any likelihood-based analysis are not conflated. |
| AR-02 | P0 | Reframe or replace the inverse-Hessian “correlation.” | Either specify a defensible residual/noise model and derive a covariance approximation, or rename the statistic as a local inverse-curvature coupling diagnostic with no confidence interpretation. |
| AR-03 | P0 | Demonstrate rate-domain and grid-resolution robustness. | Repeat the profile on multiple domains and resolutions or use continuous one-dimensional optimization; report boundary behavior, convergence, and a domain-independent width measure where possible. |
| AR-04 | P0 | Correct the LOCO uncertainty analysis and language. | Remove the conventional “95% CI” claim unless a dependence-aware resampling/inference procedure is implemented. Describe the experimental unit correctly and report fold-level/cluster-aware uncertainty. |
| AR-05 | P0 | Correct data units and experimental-unit descriptions. | Figures 3–4 and text use `g/L` or `mg/mL`; Angeloni duplicate extractions and Schmieder repetitions/ten-fraction design are accurately described; the repository’s six-window derivation is documented. |
| AR-06 | P0 | Make the pooled bracket use the matched endpoint or narrow the manuscript claim. | `gate_pannusch_angeloni_species_bracket` uses a mass-consistent endpoint, or Result 1 no longer states that this bracket was run at matched 40 g. |
| AR-07 | P0 | Correct the external Waszkiewicz evidence label and time/mass alignment. | The analysis is called external-data objective localization/shape fitting rather than frozen prediction; shifted flow and bin-mass weights share the same time origin; assumptions and sensitivities are reported. |
| AR-08 | P0 | Recalculate joint-fit summaries from full precision. | Rounding occurs only at presentation; text, table, cached JSON, and Figure 5 agree on pooled errors and cost of sharing. |
| AR-09 | P0 | Correct flow and geometry claims. | “Measured flow” is replaced by “inferred/assumed flow map”; geometry sensitivity is described as a global-geometry sweep unless a grind-specific assignment test is added. |
| AR-10 | P0 | Rescope the positive-control simulation. | It is presented as a same-model best-case structural design illustration; multiple seeds/noise levels and at least one model-discrepancy sensitivity are reported. |
| AR-11 | P0 | Enforce a single mass/volume endpoint contract. | The conversion between 40 g beverage and solver volume is explicit and consistent with density; sensitivity to density is reported or the solver is terminated by mass. |
| AR-12 | P1 | Add residual diagnostics that do not hide within-series performance. | Provide normalized/faceted plots by solute, variety, temperature, pressure, and grind, with per-group metrics and uncertainty where available. |
| AR-13 | P1 | Complete the end-to-end paper build. | One command regenerates every manuscript number and all figures, including external analysis and sensitivity results, from a frozen source commit. |
| AR-14 | P1 | Freeze the software environment and release. | Pin dependencies, record seeds and data hashes, create a Paper A tag/release, archive outputs, and include a machine-readable provenance manifest. |
| AR-15 | P1 | Complete the literature-search record and bibliography. | The evidence matrix contains actual screened sources and decisions; database search details are archived; every author–year citation resolves in the rendered bibliography. |
| AR-16 | P1 | Rebuild Figure 1 evidence taxonomy. | Within-campaign cross-grind holdout is not called “external prediction”; Table 7 is an orthogonal measurement from the same study, not an independent dataset; Waszkiewicz is shown. |
| AR-17 | P2 | Remove internal review/change-log prose from the paper. | Submission manuscript begins with title/author material, not repository review notes, roadmap pointers, or owed-item tracking. |
| AR-18 | P2 | Standardize symbols, precision, and terminology. | Units are attached to `c_s0`; rate scale is explicitly dimensionless; “localizes” replaces unsupported “identifies”; percentage-point differences use unrounded values. |

---

## 5. Major review comments

### MAJ-01 — The central contribution is credible only after narrowing the strongest wording

The paper’s strongest defensible conclusion is not that a whole cup generally “hides the clock,” nor that a single-grind whole-cup fit mathematically constrains only an inventory–rate product. It is that, **for this model, observation map, parameterization, operating design, objective, and tested domain**, inventory and rate exhibit strong practical compensation, while fraction-resolved observations produce a more localized rate objective.

The manuscript eventually states this scope correctly in the related-work conclusion and Discussion, but the Introduction still says:

> “A single-grind whole-cup fit therefore constrains only their product.”

That is too strong. With multiple temperatures, pressures, flows, or endpoint durations, the function `φ(rate, flow, T)` can change differently across conditions, so a set of endpoint observations may contain shape information across the design even if each individual endpoint is scalar. The empirical result is a near-flat profile under the tested design, not an exact product invariance theorem.

**Required action:** Rewrite the Introduction and any figure title or abstract sentence that implies structural impossibility. A suitable formulation is:

> “Under the tested single-grind whole-cup design, inventory and rate are practically confounded: changes in one can be largely compensated by changes in the other over the evaluated domain.”

Retain the carefully scoped statement already present near the end of the related-work section: the result concerns the tested model, observation map, datasets, domain, and error model.

---

### MAJ-02 — The formal identifiability panel profiles SSE, not MAPE

This is the most important implementation/manuscript inconsistency.

The manuscript states in §2.6 that the rate profiles are “profiled MAPE objectives,” and the related-work section repeats that the paper minimizes MAPE rather than a likelihood. However, `identifiability_panel` does the following:

- defines `sse(pred) = sum((pred - m)**2)`;
- chooses `c_star` by the least-squares formula `(Fᵀm)/(FᵀF)`;
- computes the full two-dimensional SSE surface;
- constructs an SSE Hessian in log parameters; and
- defines the 10% profile set using `sse_prof <= 1.10 * sse_min`.

The function’s docstring alternates between “SSE objective” and “profiled MAPE objective,” and an inline comment says “profiled MAPE” while the next words say “min SSE.” Figure 2 is explicitly an SSE contour plot. Manuscript §4 correctly says “profile SSE,” but §2.6 and §9 say the opposite.

This is not merely nomenclature. MAPE and SSE produce different nuisance-level optima, different weighting of conditions, different profile shapes, and potentially different minima. The exact MAPE weighted-median method highlighted in §2.1 is **not** what generates the formal condition numbers and profile-width claims.

**Required action:** Choose and defend one of these approaches:

1. **Preferred for inferential interpretation:** define an explicit residual model, such as log-normal or heteroscedastic Gaussian errors, and use the corresponding negative log-likelihood or weighted residual objective for the profile and local curvature. Predictive scores such as MAPE can remain secondary reporting metrics.
2. **Descriptive dual-objective approach:** retain SSE solely as a smooth local-curvature diagnostic, but profile MAPE separately using the exact weighted-median level. Clearly label Figure 2 and the condition number as SSE-based, and report whether the qualitative conclusion is unchanged under MAPE.
3. **MAPE-only descriptive approach:** profile MAPE throughout, but do not compute a conventional Hessian at its nondifferentiable weighted-median kinks. Use profile width, boundary behavior, and finite objective contrast instead.

Whichever is selected, regenerate all quoted profile widths, optima, condition numbers, captions, and cached results. Do not describe an SSE profile as MAPE.

---

### MAJ-03 — The inverse-Hessian “correlation” is not yet a statistical parameter correlation

The code inverts the raw SSE Hessian and normalizes its off-diagonal term to produce `rate_cs0_correlation`. The manuscript then reports “rate↔inventory correlation −0.99” in the abstract and Result 2.

An inverse objective Hessian can support a local covariance approximation only under explicit assumptions about the observation-error model, weighting, parameter scale, and behavior near an interior optimum. None is currently specified. Here, the objective is unweighted concentration-scale SSE, while the manuscript’s primary predictive metric is MAPE. The code also clips out-of-range numerical values to `[-1,1]`, which can hide instability rather than resolve it.

The statistic does convey a useful geometric fact: the local inverse-curvature ellipse is strongly tilted along the compensation direction. It should not be presented as though it were an empirical or posterior correlation between estimated parameters.

**Required action:** Either:

- define a likelihood, justify weighting and residual assumptions, estimate the noise scale, and report a clearly qualified local asymptotic correlation; or
- rename it, for example:

> “local inverse-curvature coupling coefficient in log-parameter space”

and state explicitly that it is **not** a confidence correlation.

Suggested wording:

> “The local inverse-curvature diagnostic from the SSE surface indicates near-collinearity (coefficient −0.99); because no likelihood is specified, this is not a statistical parameter correlation.”

Also report the Hessian eigenvalues, finite-difference steps, optimum distance from all boundaries, and numerical sensitivity of this coefficient.

---

### MAJ-04 — The profile width and condition number need domain, resolution, and threshold robustness

The central profile metrics are sensitive to analyst choices that are not yet tested:

- The rate grid in the production fits is only 18 points over `0.15–6.5`.
- The formal panel uses 29 rate points and 41 inventory points.
- The Hessian is a central finite difference at the closest grid cell, not at a continuously optimized stationary point.
- The “fraction of the swept rate range” is calculated as the mean of a Boolean mask on a **log-spaced grid**. It is therefore the fraction of sampled log-rate points, not the fraction of the linear numeric interval.
- The 10% threshold is a user-defined tolerance with no calibration to noise, repeatability, or a likelihood ratio.
- The “identifiability ratio” or max/min profile contrast depends directly on the chosen sweep limits and can be unstable when the minimum is small.

The manuscript says the result is “not an artefact of a coarse grid,” but no convergence study is supplied.

**Required action:** Add a robustness appendix that includes at minimum:

1. rate grids of substantially increasing density, such as 18, 36, 72, and 144 points;
2. at least two wider/narrower domains, with explicit reporting of whether the minimum or tolerance interval touches a boundary;
3. continuous one-dimensional optimization of rate after analytic nuisance-level profiling, where computationally feasible;
4. a profile-width measure on `log(rate)`, such as the log-width of the set satisfying a stated relative objective tolerance;
5. several tolerances, or a tolerance linked to an explicit error model;
6. finite-difference or local-polynomial sensitivity for the Hessian and eigenvectors.

Rename “identifiability ratio” to a more neutral term such as **profile contrast over the predefined rate domain**. Always report the domain alongside it. Avoid any universal threshold such as “ratio ≫ 1 means identified.”

---

### MAJ-05 — The LOCO bootstrap interval treats dependent errors as independent

The LOCO procedure generates 54 residuals: 9 held-out conditions × 3 solutes × 2 varieties. The code then samples those 54 errors independently with replacement and reports the 2.5th and 97.5th percentiles of the resampled mean as a “bootstrap 95% CI.”

Those errors are not independent:

- all nine folds for a given solute/variety use highly overlapping training sets;
- the same `(T,p)` design conditions recur across solutes and varieties;
- multiple analytes arise from the same condition-level extraction campaign;
- source observations are condition summaries rather than 54 independent new shots; and
- the underlying Angeloni campaign used duplicate extractions, while the repository appears to analyze reported means rather than replicate-level observations.

Cross-validation error estimates have well-known dependence problems because training sets overlap. Bengio and Grandvalet showed that no universal unbiased estimator of the variance of k-fold cross-validation exists, and naive independence can underestimate variance. Nadeau and Bengio likewise emphasized that ignoring training-set variability can substantially understate uncertainty.

Calling this a “shot-level bootstrap” is especially misleading: the bootstrap unit is an out-of-fold percentage error, not a source-level shot or independent experimental replicate.

**Required action:** At minimum, relabel the current interval as a **descriptive residual-resampling interval** and state that it ignores fold dependence; do not call it a conventional 95% confidence interval. A stronger revision would:

- summarize one macro error per held-out `(T,p)` fold, preserving the condition cluster across solutes and varieties;
- recover replicate-level Angeloni measurements if available and perform a hierarchical or cluster bootstrap at the independent extraction/condition level;
- rerun the entire fitting and CV procedure within each bootstrap sample rather than resampling final residuals only;
- present fold-by-fold values and sensitivity intervals without claiming exact frequentist coverage; and
- distinguish uncertainty in the finite nine-condition design from uncertainty about future machines, coffees, or grinds.

Suggested manuscript wording if the current computation is retained temporarily:

> “Pooled LOCO MAPE was 6.5%; a simple residual-resampling interval was [5.0, 8.2]%, reported descriptively because overlapping folds and shared conditions induce dependence.”

This wording should not be used as a substitute for a stronger resampling analysis in the final paper.

---

### MAJ-06 — The data descriptions conflate conditions, shots, replicates, and derived fractions

#### Angeloni campaign

The draft calls Angeloni a “66-shot campaign.” The source describes 33 espresso samples for Arabica and 33 for Robusta, with all extractions duplicated and analytical repeatability/RSD information reported. The repository appears to store condition-level reported values, not the full duplicate-extraction records.

A more accurate description is:

> “The analysis uses 66 condition-level sample records (33 per variety), each based on duplicate extractions in the source study; the repository retains reported central values rather than the full replicate-level uncertainty.”

The current open-gap statement that “the named-solute rows are single measurements” should be removed. The source reports named-solute concentrations in `g/L` and RSD values, with reported RSD spanning approximately 0.3–19.7% in the relevant table. Even if the repository does not retain those uncertainties, the source observations are not accurately described as unreplicated single measurements.

#### Schmieder campaign

The draft describes “15 shots × 6 timed fractions per shot.” The source study used 15 experimental settings, each with three repetitions and six repetitions at the center point, and collected ten consecutive fractions. It then analyzed/modelled a six-fraction subset, specifically fractions 1, 2, 3, 5, 7, and 10. The repository CSV contains 15 condition-level series × those six selected fractions, apparently as derived/averaged values.

**Required action:** Document the derivation explicitly:

- original experimental design and repetitions;
- ten collected fractions;
- why only six fractions are present in the repository/model port;
- whether values are replicate means, fitted values, or selected raw values;
- how timing bounds were derived; and
- what uncertainty was lost through aggregation.

Suggested wording:

> “The Pannusch port uses a derived six-window subset (fractions 1, 2, 3, 5, 7, and 10) across 15 experimental conditions from a study that collected ten consecutive fractions with repeated extractions.”

Do not call the 15 rows “shots” unless each row truly corresponds to one individual extraction.

---

### MAJ-07 — Figure 3 and Figure 4 use the wrong concentration unit

Both figures label observed and predicted values as `mg/g`. The Angeloni manuscript and the corresponding repository code use named-solute beverage concentrations in `g/L`; the Pannusch side uses `mg/mL`, which is numerically equivalent to `g/L`. `mg/g` is a mass-fraction unit and is not identical without an explicit beverage-density conversion.

This is a concrete figure error and can lead readers to infer a different observable contract.

**Required action:** Change both axes to either:

- `concentration (g L⁻¹)`, or
- `concentration (mg mL⁻¹)`.

State the numerical conversion and any density assumption in Methods. Audit all captions, tables, JSON field names, and figure legends for the same error.

---

### MAJ-08 — The pooled-envelope bracket still uses a fixed 25 s interval

Result 1 says all three tests were run at the matched 40 g endpoint. However, `gate_pannusch_angeloni_species_bracket` defaults to `t_shot_s=25.0` and calls the solver over `[0, 25 s]`. It does not call the matched-endpoint helper.

The bracket is admittedly only a wide-envelope regime check, but the manuscript’s explicit statement that all tests use matched cups is false for this code path. This matters because the paper’s central correction is precisely that a fixed time and matched beverage endpoint are not interchangeable.

**Required action:** Convert the bracket to the same explicit mass/volume endpoint contract as the other analyses, regenerate its prediction ranges, and update cached results. Alternatively, remove it from the “all at matched 40 g” table and label it as an unmatched, representative-condition screening calculation. The first option is preferable.

Also add an automated test that prevents any Paper A whole-cup path from silently using a fixed time when the manuscript claims a fixed beverage mass.

---

### MAJ-09 — “Matched 40 g” is implemented as 40 mL, not strictly 40 g

The matched-endpoint helper defines `_V_TARGET_ML = 40.0` and stops at `t_end = 40 mL / Q`, while the source campaign specifies `40 ± 2 g` beverage. The solver also contains a beverage/water density on the order of 980 kg/m³, implying that 40 g is not exactly 40 mL.

The approximation is likely modest, but this paper is specifically about observable-contract precision. A hidden 1:1 mass–volume substitution weakens that message.

**Required action:** Choose one explicit contract:

- terminate at 40 g by integrating mass flow;
- convert 40 g to volume with the same density model used elsewhere; or
- state that 40 g is approximated as 40 mL, quantify the resulting endpoint difference, and show that conclusions are insensitive to a plausible density range.

Use “matched beverage endpoint” until the implementation exactly supports “matched 40 g.”

---

### MAJ-10 — The manuscript calls constructed flow values “measured flow”

Section 5 says each grind is evaluated with “its own measured flow.” The implementation actually computes flow from:

- assumed grind-specific shot times (`20/13/35 s`);
- polynomial hydraulic-conductivity functions by grind;
- normalization at 9 bar; and
- a viscosity correction.

These inputs may be based on the Angeloni card or study, but the condition-level flow used in the simulation is an inferred map, not a directly measured flow trajectory for each observation.

**Required action:** Replace “measured flow” with a precise description such as:

> “each grind uses a study-derived, assumed grind-specific pressure–flow map based on fitted hydraulic conductivity, nominal shot time, and viscosity correction.”

Report the source and uncertainty for each component. Add sensitivity to the nominal times and hydraulic-conductivity coefficients, or state that transfer conclusions are conditional on this map.

Do not treat the small difference between the two O-grind flow maps as evidence that flow uncertainty is generally negligible across C/F transfer.

---

### MAJ-11 — The geometry sensitivity does not test a cross-grind geometry map

`geometry_sensitivity_transfer` applies each of the three Pannusch geometry parameter sets globally to all O, C, and F simulations, refits on O, and evaluates C/F. This asks whether the conclusion is sensitive to selecting one global frozen geometry from the observed range. It does **not** ask whether plausible grind-specific geometry assignments alter transfer.

The manuscript says the transfer is “not a geometry artefact,” which is broader than the implemented test.

**Required action:** Use more exact language:

> “Transfer errors changed by at most approximately one percentage point when each of the three Pannusch geometry settings was applied globally, indicating limited sensitivity to the global geometry choice over that range.”

A stronger test would assign geometry separately by grind using a justified mapping, then perturb that mapping within measurement uncertainty. Until then, retain geometry as an unresolved structural uncertainty rather than declaring it excluded.

---

### MAJ-12 — Early rounding contaminates the joint-fit aggregate and causes Figure 5 disagreement

In `joint_multigrind_fit`, per-grind joint MAPEs and independent best MAPEs are rounded to whole percentages before pooled means and cost-of-sharing are calculated. The aggregate therefore depends on presentation rounding. This likely explains why the manuscript says a cost of approximately 1 percentage point while Figure 5 says approximately 2 percentage points.

Rounding before aggregation is a preventable numerical reporting defect.

**Required action:** Preserve full-precision errors in all internal structures. Compute pooled metrics and differences from unrounded values, then round only for display. Regenerate `results.json`, manuscript tables, figure titles, and captions. Report the exact definition of “pooled”:

- macro-average across six variety–solute fits;
- average across all 162 condition-level predictions; or
- another weighting.

The figure should also show the independent comparator, not only the joint-fit heatmap, if its title emphasizes the cost of sharing.

---

### MAJ-13 — The positive-control simulation is a same-model best-case test, not a general demonstration

The exact-cup simulation generates synthetic observations from the same model later used to refit them, at a known rate of 1, with one seed and 3% independent multiplicative Gaussian noise. Under this inverse-crime setup, fraction-resolved observations are expected to recover the generating rate more sharply than one integrated scalar per shot.

The test is useful as a **structural design illustration**: given a correct model, preserving temporal resolution supplies more rate-shape information than aggregation. It is not strong evidence that a true experimental whole cup generally lacks rate information, nor that the proposed model is correctly specified.

The current statement that the simulation “removes the sampled-window artefact” is fair only within the same-model synthetic setting. The figure title “fraction scoring identifies the rate” overstates the evidence.

**Required action:**

- rename it a “same-model structural design simulation” or “best-case information-content simulation”;
- run many random seeds and report distributions of best rate, profile width, and contrast;
- vary noise level and correlation structure;
- include at least one model-discrepancy scenario, such as altered geometry, flow trajectory, initial condition, or transfer law between data generation and fitting;
- show the simulated fraction profile as well as the simulated exact-cup profile in Figure 6; and
- use “localizes the rate objective” rather than “identifies the rate.”

The empirical result already acknowledges that six-window aggregation is not a true cup. Keep that distinction prominent.

---

### MAJ-14 — The Waszkiewicz analysis is not a fully frozen external prediction

The manuscript and code call the analysis a “frozen external prediction,” but two target-data operations are performed:

1. at every rate, the level is fitted to the Waszkiewicz observations; and
2. the rate producing the minimum target-data MAPE is reported.

The Pannusch model structure and base solute parameters are carried across, but the displayed result is an **external-data profile/shape fit with a target-specific nuisance level**, not a blind external prediction. A blind frozen prediction would report performance at the source-calibrated rate and independently specified inventory/level without using the target trajectory to choose either.

This does not invalidate the objective-localization question. It changes the evidence category.

**Required action:** Split the analysis into clearly named quantities:

- **frozen reference-rate trajectory**, evaluated at rate scale 1 with any independently defensible level;
- **target-profiled nuisance-level curve** at each rate;
- **external-data objective localization**, describing the profile minimum and width.

If an independent level is unavailable, state that a true blind concentration prediction cannot be made. Do not call the profile minimum an external prediction.

The scope sentence could read:

> “On an independent TDS trajectory, after profiling a target-specific concentration level, the fraction-resolved objective is more localized in rate than the corresponding single integrated observation.”

---

### MAJ-15 — The flat Waszkiewicz cup profile is an algebraic consequence, not empirical evidence about cups generally

For the Waszkiewicz case, the “cup” dataset contains one integrated scalar. At each rate the analysis fits one free multiplicative level. Therefore the model can match that one scalar exactly at every rate, and the objective is flat by construction. This is correctly acknowledged in parts of the code and draft, but the abstract’s phrasing can be read as an empirical discovery that this external cup “carries no rate information.”

The analysis demonstrates the elementary degrees-of-freedom fact that one scalar plus one free level cannot constrain a second parameter. It does **not** test whether multiple integrated cups at different flows, temperatures, pressures, or endpoints could localize rate.

**Required action:** State this explicitly wherever the result appears:

> “For the single integrated observation, fitting one free level makes the objective flat at every rate by construction; this panel illustrates the algebra of one-point endpoint fitting rather than evidence that cup-integrated designs generally lack rate information.”

The external value lies in the non-flat **fraction** profile, not in the trivially flat cup profile.

---

### MAJ-16 — The Waszkiewicz implementation needs a stricter observable/time contract

The external module appropriately declares several assumptions, but additional corrections are needed:

1. **Time-shift inconsistency.** The simulated flow function is shifted by the assumed time offset, but `binmass` is computed once from the unshifted cumulative-mass trace. For nonzero offsets, the weights used to construct the observed integrated cup should be derived from the same shifted flow/time convention.
2. **Temperature assumption.** A fixed 93 °C is used because the trace lacks brew temperature. This needs a temperature sensitivity, especially because the model contains explicit temperature dependence.
3. **Flow floor.** The early-time flow is floored at 0.05 mL/s for numerical stability. The result should be tested against several floors and, preferably, a solver treatment that handles pre-flow intervals without artificial advection.
4. **Public-bin mismatch.** The code uses 12 public 5 s bins while noting 14 in the paper’s figure. Resolve which bins are missing and whether the public table spans the same endpoint.
5. **Uncertainty.** The source includes replicate information/standard deviations for most bins, but the fit is unweighted MAPE. Use uncertainty weighting or explain why it is unavailable/inappropriate. Dropping the first bin does not substitute for using uncertainty in the remaining bins.
6. **Model mismatch.** A minimum MAPE near 27% is substantial. The conclusion should be “the profile is localized despite moderate/poor trajectory agreement,” not that the frozen model accurately reconstructs the external trajectory.

**Required action:** Implement and report sensitivity to temperature, flow floor, time origin, bin selection, and uncertainty weighting. Ensure the observed cup and model bins use identical time/mass windows.

---

### MAJ-17 — Pooled observed-versus-predicted plots can exaggerate apparent agreement

Figures 3 and 4 pool analytes with different concentration levels. A plot can appear close to the identity line primarily because caffeine, trigonelline, and 5-CQA occupy distinct level bands, even if within-solute responses to temperature or pressure are weak or biased. In Figure 4, the Arabica/Robusta level separation further dominates the visual pattern.

These plots are not wrong, but they are insufficient evidence of condition-level predictive shape.

**Required action:** Add at least one of the following, preferably in the main paper or supplement:

- observed and predicted values normalized within each variety–solute series;
- residuals versus temperature and pressure, faceted by solute, variety, and grind;
- within-series centered predictions versus observations;
- fold-level and condition-level relative errors;
- calibration slope/intercept within each group; and
- uncertainty bars from source replicate/RSD information.

Report metrics by group rather than only pooled averages. Include the worst-fold Robusta 5-CQA behavior in a diagnostic plot and discuss whether it reflects a systematic condition or assay issue.

---

### MAJ-18 — Evidence labels need stricter campaign-level semantics

The manuscript’s evidence vocabulary is a good idea, but Figure 1 and some prose do not follow it:

- O→C/F uses held-out grinds from the **same Angeloni campaign** after fitting O. This is an internal cross-grind holdout, not an “external prediction.”
- Table 7 inventory comes from the same Angeloni study. It is an orthogonal or independently measured observable within the same study, not an independent external dataset.
- The Waszkiewicz external trajectory is absent from Figure 1 even though it is central to §6.
- The Schmieder fraction test is in-sample relative to the Pannusch calibration lineage, while the exact-cup result is synthetic. These should be separate boxes.

**Required action:** Rebuild Figure 1 with evidence categories tied to campaigns and data use:

1. Schmieder fractions → Pannusch source calibration;
2. Schmieder source-data profile → in-sample objective-localization check;
3. same-model exact-cup simulation → synthetic design illustration;
4. Angeloni O → target-data recalibration;
5. Angeloni O LOCO → internal condition holdout;
6. Angeloni C/F → within-campaign cross-grind holdout;
7. Angeloni Table 7 → orthogonal inventory measurement from the same study;
8. Waszkiewicz fractions → independent external-data objective localization.

Use “external” only for a genuinely different campaign/rig/coffee not used for target fitting.

---

### MAJ-19 — The paper-build claim is broader than the implementation

The figure module states that `compute` runs “every slow analysis function once” and that every manuscript value regenerates from those functions. In fact, `compute_all` currently includes:

- two identifiability panels;
- transfer;
- joint fit;
- LOCO;
- empirical positive control; and
- exact-cup simulation.

It omits at least:

- the blind pooled species bracket;
- per-condition blind result;
- flow-map refinement;
- target refit summaries;
- geometry sensitivity;
- sampled-aggregate-versus-cup audit; and
- external Waszkiewicz analysis.

Several manuscript numbers therefore do not arise from the advertised paper build.

**Required action:** Create a true end-to-end build, for example:

```bash
python -m puckworks.paper_a build --config configs/paper_a.toml
```

It should:

- run every analysis used in text, tables, and figures;
- write one immutable results bundle with full precision;
- record source commit, environment, dependency versions, data hashes, command-line arguments, seeds, and timestamps;
- generate figures and a machine-readable claim-to-result map;
- fail if manuscript-facing values are stale; and
- include lightweight integrity tests in CI, even if full PDE sweeps run only on a scheduled or release workflow.

Until this exists, narrow the claim to “the six figures render from cached results generated by a subset of slow analysis functions.”

---

### MAJ-20 — Reproducibility is promising but not submission-grade

The repository’s Python dependencies are not pinned to exact versions, slow analyses are outside CI, and the manuscript itself says a frozen tag remains owed. Reproducibility is especially important because the conclusions depend on numerical PDE solves, rate grids, endpoint operators, and several manually chosen assumptions.

**Required action:** Before submission:

- create a lockfile or fully specified environment (`uv.lock`, `poetry.lock`, conda lock, or equivalent);
- record Python, NumPy, SciPy, and Matplotlib versions;
- freeze all random seeds and expose them in configuration;
- archive all input datasets with checksums and license/provenance metadata;
- create a release tag such as `paper-a-v1.0.0` only after the final manuscript build;
- deposit the release and generated outputs in an archival repository with DOI;
- include a resource estimate and expected run time;
- add tests for exact-level fitting, matched endpoints, unit conversions, profile-objective consistency, and shifted interval operators; and
- include a `REPRODUCE_PAPER_A.md` with one clean-environment walkthrough.

Cached numerical JSON should not be the only record of a slow analysis. Include a full command log and validation that cached values correspond to the cited source commit.

---

### MAJ-21 — The novelty statement remains provisional because the documented search is not complete

The related-work section is thoughtful and appropriately says the search is scoping rather than PRISMA-complete. However, the repository evidence matrix is still scaffold-like and the full Scopus/Web of Science search is deferred to submission. A novelty claim cannot be finalized before that search is run and documented.

**Required action:** Complete and archive the search before submission, including:

- databases and exact query strings;
- search dates;
- inclusion/exclusion criteria;
- deduplication and screening process;
- a populated evidence matrix;
- records specifically addressing practical identifiability, parameter compensation, and experimental design in coffee/extraction models; and
- a transparent statement of what was and was not searched.

Keep the contribution modest: this is an applied espresso case study using established identifiability tools, not a new identifiability method.

---

### MAJ-22 — Measurement uncertainty should be recovered or the analysis explicitly treated as unweighted

The manuscript currently mixes condition means, source RSD information, and unweighted objectives. Angeloni reports repeatability/RSD for named solutes, and Schmieder includes replicate structure. Ignoring those uncertainties gives equal influence to observations with potentially very different precision and makes the use of raw SSE especially difficult to justify.

**Required action:** Recover source-level uncertainty where licenses/data permit, then compare:

- unweighted MAPE;
- log-relative residual loss;
- uncertainty-weighted least squares or likelihood; and
- robust alternatives for outlying conditions.

At minimum, report that the primary results are unweighted and show sensitivity to plausible uncertainty ranges. Do not imply that a local Hessian or profile tolerance has confidence meaning without this model.

---

## 6. Figure-by-figure review

### Figure 1 — Study and evidence design

**What works:** The flowchart makes the distinction among calibration, holdout, transfer, and verification visible.

**Problems:**

- O→C/F is labeled “external prediction” even though C/F belong to the same Angeloni campaign used for O fitting.
- Table 7 is labeled an “independent tie-breaker” and linked as an external constraint, but it is an orthogonal measurement from the same source study.
- The independent Waszkiewicz dataset is absent.
- The exact-cup simulation is merged conceptually with empirical fraction verification.
- The arrow from Schmieder/Pannusch to Angeloni O is called “calibration,” which can obscure that this is a new target-data calibration distinct from the original Pannusch calibration.

**Required redesign:** Use the eight-stage evidence map listed in MAJ-18. Add a small legend that defines “source calibration,” “target recalibration,” “within-campaign holdout,” “external dataset,” and “simulation.”

---

### Figure 2 — Inventory–rate objective surface

**What works:** The compensation valley is visually clear, and showing the independently measured inventory line is useful.

**Problems:**

- The plotted objective is SSE while the manuscript elsewhere calls it profiled MAPE.
- There is no color bar, so contour magnitude cannot be interpreted.
- The two panels have different absolute SSE scales but are visually compared without normalization.
- The inventory axis has no physical unit.
- The title reports condition number as “cond. no.” without stating the parameter basis, objective, or local nature.
- The black optimum marker and black 10%-above-minimum contour are not explained in the legend.
- The figure does not actually show a separate one-dimensional profile, making the “76% flat” statement hard to verify visually.
- The heatmap is clipped to 1–3× the minimum, which can overemphasize or underemphasize contrast depending on the minimum.

**Required redesign:**

- choose one objective contract and name it in the title/caption;
- plot normalized objective increase, for example `(J-Jmin)/Jmin`, with a color bar;
- label `c_s0` with units and define the rate scale as dimensionless;
- explain the marker, tolerance contour, domain, data subset, and Table 7 line;
- add a lower or adjacent profile panel showing `J_profile(rate)` and the threshold interval;
- report grid resolution and whether the optimum is interior; and
- show grid/domain sensitivity in supplementary figures.

---

### Figure 3 — Leave-one-condition-out holdouts

**What works:** Displaying all held-out predictions is better than reporting only a pooled number.

**Problems:**

- axes incorrectly say `mg/g` rather than `g/L` or `mg/mL`;
- the title presents a conventional “95% CI” from a dependence-ignoring residual bootstrap;
- concentration-level clustering across analytes dominates the visual agreement;
- no fold condition `(T,p)` is identifiable;
- no uncertainty bars are shown despite source repeatability information;
- the worst residual is not highlighted; and
- the identity-line plot does not reveal systematic within-series condition response.

**Required redesign:** Correct units; remove or relabel the CI; add normalized residual/faceted panels; encode or annotate held-out conditions; show per-solute/variety summary metrics; and include uncertainty where recoverable.

---

### Figure 4 — Frozen O→C/F transfer

**What works:** Separate coarse and fine panels make the transfer question concrete.

**Problems:**

- same unit error as Figure 3;
- “frozen transfer” is conditional on an inferred pressure–flow map and globally frozen geometry;
- pooled level bands can visually dominate within-group performance;
- the title claims ≤1 percentage-point geometry sensitivity, but the figure provides no geometry comparison;
- the legend is crowded; and
- no error bars or condition labels appear.

**Required redesign:** Correct units; change “measured flow” language in caption; either add a geometry-sensitivity inset/panel or remove the claim from the title; provide normalized residual diagnostics; and separate or simplify legends.

---

### Figure 5 — Joint shared-fit residuals

**What works:** A heatmap is a useful compact view of where a shared calibration incurs error.

**Problems:**

- the title’s approximately 2 percentage-point cost conflicts with the manuscript’s approximately 1 percentage point;
- this discrepancy is linked to early rounding in the analysis;
- labels display literal code notation rather than publication-quality symbols;
- the heatmap shows only joint-fit errors, not the per-grind independent baseline;
- the asterisk legend says boundary rates, while the manuscript says none are at the boundary; and
- whole-integer cell values hide potentially meaningful differences.

**Required redesign:** Recompute from full precision; place joint and independent errors side by side or plot their difference; use publication symbols (`c_{s,0}`); show exact boundary status; and align title, text, and table.

---

### Figure 6 — Fraction versus endpoint profiles

**What works:** The figure communicates the broad difference between fraction-resolved and aggregated scoring.

**Problems:**

- “identifies the rate” overclaims in-sample and same-model simulation evidence;
- the figure shows empirical fractions, empirical sampled aggregate, and simulated exact cup, but omits the **simulated fraction curve** needed for the direct synthetic comparison;
- one seed is shown without uncertainty bands;
- the external Waszkiewicz profile is omitted despite being central to the corresponding section;
- the exact-cup curve can be visually flatter partly because the y-axis and baseline differ across solutes;
- the profile-contrast ratio and predefined domain are not shown; and
- the trivially flat one-observation Waszkiewicz cup result should not be visually conflated with multi-condition exact-cup simulations.

**Required redesign:** Retitle:

> “Fraction-resolved scoring localizes the rate objective more strongly than aggregated scoring in the tested designs.”

Add simulated fraction curves and multi-seed bands; place the Waszkiewicz external-data profile in a separate panel or figure; annotate domain, best rate, and profile contrast; and explicitly label any flat one-point cup profile as “flat by construction after fitting one level.”

---

## 7. Additional methods and code comments

### 7.1 Discrete rate optimization

Most fits select the best rate from `_RATE_DOMAIN = geomspace(0.15, 6.5, 18)`. This is coarse for reporting fitted rates such as 2.2 or deciding whether rates are interior. A grid is acceptable for visualization and global screening, but final point estimates and cost-of-sharing comparisons should use a continuous bounded one-dimensional optimizer after exact nuisance-level profiling. Verify the optimizer against increasingly fine grids and report boundary cases honestly.

### 7.2 MAPE properties

MAPE is intuitive but places high weight on smaller observations and can become unstable near zero. The current named-solute values are positive and not near zero, but the manuscript should still state why MAPE is selected. Report at least one complementary metric, such as median absolute percentage error, mean absolute log error, or uncertainty-weighted normalized error.

### 7.3 The “level is exactly linear” statement

If `c_s0` is exactly linear in the normalized solver for all relevant operators, add a unit test demonstrating linearity over representative temperatures, flows, rates, and interval operators. Clarify whether the property survives all transformations used for TDS, volume weighting, and time-varying flow. The exact weighted-median result depends on this contract.

### 7.4 Interval concentration operator

The solver helper’s documentation indicates a weighted mean while a plain arithmetic mean is used over selected subinterval outputs. For the current adjacent union of measured windows, this may not alter the result, but it is a latent bug for unequal-duration or nonadjacent intervals. Implement an explicit duration- or flow-weighted interval integral and test it against analytic/simple cases.

### 7.5 Objective precision and JSON

Store full-precision values in `results.json`; add a separate formatted-value layer for figures and manuscript tables. Include schema/version metadata so stale caches fail loudly after changes to objective, units, or endpoint definitions.

### 7.6 Boundary reporting

Every optimized rate should carry:

- search domain;
- optimizer/grid resolution;
- boundary flag;
- local profile width; and
- whether the fitted nuisance level also approached its allowed domain.

Do not interpret boundary-selected values mechanistically.

### 7.7 Table 7 inventory as tie-breaker

The independent inventory measurement is useful, but it is not independent of the Angeloni study context. Discuss measurement uncertainty, unit conversion, roast/variety matching, and whether the model’s `c_s0` has exactly the same biochemical definition as the assay’s measured solid inventory. Agreement of a curve with a horizontal line “somewhere along the valley” is weak unless uncertainty and mapping are quantified.

### 7.8 Multiple comparisons and selective examples

The formal panel emphasizes caffeine and trigonelline for Arabica. The manuscript should show all solutes and both varieties in supplementary material, including cases with boundary optima or less dramatic compensation. State whether examples were selected before or after results were known.

---

## 8. Manuscript organization and editorial comments

1. **Remove the internal major-revision banner and roadmap prose.** Lines 1–36 and the final change-log note are repository process notes, not manuscript content. Put version history in a public changelog or supplement.

2. **Add a conventional reference list.** The draft contains author–year citations but no rendered bibliography. Cross-check every citation against `references.bib`, including publication year and title for Waszkiewicz.

3. **Clarify title status.** Remove the internal parenthetical “case-study scope until…” from the title block. A suitable journal title could retain “case study” explicitly.

4. **Define every symbol with units.** In particular, `c_s0`, `A1`, `A2`, `rate_scale`, `K(T)`, `φ`, and flow units need a compact notation table.

5. **Use publication notation, not source-code identifiers.** Write `c_{s,0}` and “rate scale,” while supplying code names in a reproducibility table.

6. **Avoid “formal identifiability panel” unless formal means merely quantitative.** The analysis is numerical and objective-dependent, not a formal structural-identifiability proof.

7. **Replace “proper cross-validation” with a neutral description.** LOCO is a valid internal holdout design, but the current uncertainty treatment is not “proper” in the inferential sense.

8. **Report exact sample accounting.** For every table and figure, specify number of conditions, source replicates, analyzed values, held-out folds, and weighting.

9. **Avoid causal attribution.** Phrases such as “the residual is inventory + kinetic mismatch” should remain removed unless competing sources are quantitatively separated.

10. **Standardize percentage precision.** Do not mix integer heatmaps, one-decimal pooled values, and approximate percentage-point differences derived from rounded inputs.

11. **Distinguish “reconstruction,” “prediction,” and “profile fit” consistently.** Any target-data level/rate fitting is reconstruction or objective localization, not blind prediction.

12. **Use “rate information” carefully.** A flatter objective means weaker localization under that objective; it is not a direct Shannon-information measure unless an information framework is defined.

13. **Explain the chosen 10% threshold.** Call it a descriptive tolerance and show sensitivity. Do not let readers infer a 95% profile interval.

14. **State the target population.** The current data support conclusions about specific rigs, coffees, solutes, grinds, and designs. They do not establish population-level generalization across espresso systems.

15. **Move implementation detail to supplement.** Keep the main paper focused on study design, observable contracts, and central results; place full rate sweeps, all varieties/solutes, and numerical diagnostics in supplementary material.

---

## 9. Suggested replacement language for high-risk passages

### 9.1 Introduction: practical compensation

**Replace:**

> “A single-grind whole-cup fit therefore constrains only their product.”

**With:**

> “Under the tested single-grind whole-cup design, inventory and rate are practically confounded: changes in one can be largely compensated by changes in the other over the evaluated domain. The numerical profile therefore localizes a compensating manifold more strongly than a unique mechanistic parameter pair.”

### 9.2 Local curvature statistic

> “The local inverse-curvature diagnostic from the specified SSE surface indicates near-collinearity in log-parameter space (coefficient −0.99). Because no likelihood and measurement-error model are specified, this coefficient is a geometric coupling diagnostic rather than a statistical parameter correlation.”

### 9.3 Cross-validation interval

> “Pooled leave-one-condition-out MAPE was 6.5%, with a median of 5.2%. A simple residual-resampling interval was [5.0, 8.2]%; because folds share overlapping training data and conditions are repeated across analytes and varieties, this interval is descriptive and is not interpreted as a coverage-calibrated confidence interval.”

### 9.4 Flow statement

> “Each grind was evaluated with a study-derived pressure–flow map based on fitted hydraulic conductivity, nominal grind-specific shot time, and viscosity correction; these flows were inferred rather than measured condition by condition.”

### 9.5 Geometry sensitivity

> “Transfer errors changed by no more than approximately one percentage point when each of the three Pannusch geometry settings was applied globally. This supports limited sensitivity to the selected global geometry over the tested range, but it does not validate a grind-specific geometry map.”

### 9.6 Waszkiewicz external profile

> “On the independent Waszkiewicz TDS trajectory, after profiling a target-specific concentration level, the fraction-resolved objective showed a finite rate minimum despite moderate trajectory error. The corresponding single integrated observation was fit exactly at every rate because one free level was fitted to one scalar; its flat profile is therefore algebraic by construction.”

### 9.7 Positive-control simulation

> “In a same-model synthetic design study, fraction-resolved observations localized the generating rate more sharply than exact cup integrals. This is a best-case information-content result and does not include model discrepancy.”

### 9.8 Data descriptions

> “The Angeloni analysis uses 66 condition-level sample records, 33 per variety. The source reports duplicate extractions and analyte-specific repeatability, while the repository port retains central reported values rather than the full replicate-level data.”

> “The Schmieder source study collected ten consecutive fractions under 15 experimental settings with repeated extractions. The Pannusch/repository analysis uses a derived six-window subset comprising fractions 1, 2, 3, 5, 7, and 10.”

### 9.9 Figure 6 title

> “Fraction-resolved scoring localizes the rate objective more strongly than aggregated scoring in the tested designs.”

---

## 10. Minimum analysis package needed for a revised submission

A convincing revision should include the following outputs in the main paper or supplement:

1. **Objective-consistency table** listing every analysis, target observable, nuisance-level method, loss/objective, rate domain, optimizer, and uncertainty treatment.
2. **All-solute/all-variety profiles** under the primary objective, with domain and grid sensitivity.
3. **Secondary-objective sensitivity** comparing MAPE, log error, and an uncertainty-weighted objective.
4. **Full-precision joint versus per-grind results**, including paired differences by group.
5. **Dependence-aware LOCO summaries**, or transparent descriptive fold distributions without a conventional CI claim.
6. **Replicate/RSD-aware sensitivity** using source uncertainty where recoverable.
7. **Flow-map sensitivity** for nominal times, viscosity, density, and hydraulic-conductivity assumptions.
8. **Geometry assignment sensitivity**, not only a global geometry sweep.
9. **Positive-control simulation ensemble** over seeds, noise levels, and at least one model-discrepancy scenario.
10. **Waszkiewicz sensitivity matrix** over time offset, temperature, flow floor, bin set, and weighting, with consistent shifted mass integration.
11. **Residual diagnostic figures** by condition and normalized within analyte/variety series.
12. **One frozen reproducibility bundle** that generates all numbers and figures.

---

## 11. Submission-readiness checklist

### Scientific/statistical

- [ ] Primary objective is specified and consistent across manuscript, code, and figures.
- [ ] MAPE and SSE nuisance-level optima are not conflated.
- [ ] Any likelihood/covariance interpretation has an explicit residual model.
- [ ] Local curvature statistics are numerically converged and correctly labeled.
- [ ] Rate-domain, resolution, and threshold sensitivity is reported.
- [ ] Boundary optima are clearly flagged.
- [ ] Profile contrast is described as domain-dependent.
- [ ] LOCO uncertainty respects clustering/dependence or is labeled descriptive.
- [ ] Experimental units and source replicate structures are correct.
- [ ] Source measurement uncertainty is incorporated or explicitly omitted.
- [ ] Joint-fit metrics are calculated from full precision.
- [ ] External-data profiling is not called blind frozen prediction.
- [ ] One-point cup flatness is labeled “by construction.”
- [ ] Synthetic results are identified as same-model/best-case.

### Observable contracts and units

- [ ] Every whole-cup path uses a documented matched mass/volume endpoint.
- [ ] The pooled bracket no longer silently uses fixed 25 s.
- [ ] The 40 g–40 mL conversion is consistent and sensitivity-tested.
- [ ] Figures 3–4 use `g/L` or `mg/mL`, not `mg/g`.
- [ ] Interval averaging uses correct duration/flow weighting.
- [ ] Shifted flow, bins, and mass weights share one time origin.
- [ ] TDS proxies remain separate from named-solute metrics.

### Figures and manuscript

- [ ] Figure 1 evidence categories are campaign-accurate.
- [ ] Figure 2 has a consistent objective, color bar, units, and profile panel.
- [ ] Figure 3 removes the unsupported conventional CI and adds normalized diagnostics.
- [ ] Figure 4 either shows geometry sensitivity or removes it from the title.
- [ ] Figure 5 agrees with full-precision text/table values.
- [ ] Figure 6 says “localizes,” includes simulated fraction curves, and shows uncertainty.
- [ ] Internal revision notes and roadmap language are removed.
- [ ] Complete bibliography is rendered.
- [ ] Novelty language matches the completed search record.

### Reproducibility

- [ ] One end-to-end Paper A build regenerates every manuscript value.
- [ ] Dependencies are pinned.
- [ ] Data and output hashes are recorded.
- [ ] Random seeds are configured and logged.
- [ ] A frozen release/tag is created.
- [ ] Slow-run provenance and resource estimates are documented.
- [ ] Tests cover endpoint, units, level linearity, profile objective, and interval operators.

---

## 12. Supporting literature and source checks

The following sources are particularly important for the revision.

### Primary espresso/model sources

1. **Angeloni, S., et al. (2023).** “Computer Percolation Models for Espresso Coffee: State of the Art, Results and Future Perspectives.” *Applied Sciences*, 13, 2688. DOI: [10.3390/app13042688](https://doi.org/10.3390/app13042688).  
   Relevant to: 40 ± 2 g beverage endpoint, duplicate extractions, named-solute units in g/L, reported RSD, campaign structure, Table 7 inventory.

2. **Schmieder, B. K. L., et al. (2023).** “Influence of Flow Rate, Particle Size, and Temperature on Espresso Extraction Kinetics.” *Foods*, 12, 2871. DOI: [10.3390/foods12152871](https://doi.org/10.3390/foods12152871).  
   Relevant to: ten consecutive fractions, 15 experimental settings, three repetitions and six at center, six analyzed fractions 1/2/3/5/7/10, cup calculations.

3. **Pannusch, V. B., et al. (2024).** “Model-based kinetic espresso brewing control chart for representative taste components.” *Journal of Food Engineering*, 367, 111887. DOI: [10.1016/j.jfoodeng.2023.111887](https://doi.org/10.1016/j.jfoodeng.2023.111887).  
   Relevant to: two-grain model, temperature/flow correlations, source calibration lineage, use of six analyzed fraction windows, model scope.

4. **Waszkiewicz, R., et al. (2026).** “Under pressure: Poroelastic regulation of flow in espresso brewing.” *Physics of Fluids*, 38, 063113. DOI: [10.1063/5.0319611](https://doi.org/10.1063/5.0319611).  
   Relevant to: independent rig, time-dependent flow, external TDS trajectory, publication year and experimental scope.

5. **Schmieder/Pannusch data release.** Mendeley Data DOI: [10.17632/y2tz67f6ry.1](https://doi.org/10.17632/y2tz67f6ry.1).  
   Relevant to: raw/derived fraction provenance and replicate recovery.

### Identifiability and uncertainty sources

6. **Raue, A., et al. (2009).** “Structural and practical identifiability analysis of partially observed dynamical models by exploiting the profile likelihood.” *Bioinformatics*, 25(15), 1923–1929. DOI: [10.1093/bioinformatics/btp358](https://doi.org/10.1093/bioinformatics/btp358).  
   Relevant to: profile-based practical-identifiability analysis and limits of local approximations.

7. **Wieland, F.-G., et al. (2021).** “On structural and practical identifiability.” *Current Opinion in Systems Biology*, 25, 60–69. [ScienceDirect record](https://www.sciencedirect.com/science/article/pii/S245231002100007X).  
   Relevant to: distinction between structural and practical identifiability and shortcomings of Fisher-information/local covariance diagnostics.

8. **Bengio, Y., & Grandvalet, Y. (2004).** “No Unbiased Estimator of the Variance of K-Fold Cross-Validation.” *Journal of Machine Learning Research*, 5, 1089–1105. [JMLR article](https://www.jmlr.org/papers/v5/grandvalet04a.html).  
   Relevant to: dependence among cross-validation estimates and limits of naive variance/CI calculations.

9. **Nadeau, C., & Bengio, Y. (2003).** “Inference for the Generalization Error.” *Machine Learning*, 52, 239–281. DOI: [10.1023/A:1024068626366](https://doi.org/10.1023/A:1024068626366).  
   Relevant to: underestimation of uncertainty when variability from overlapping training sets is ignored.

---

## 13. Code-to-comment traceability

| Review point | Repository location |
|---|---|
| SSE/MAPE contradiction | `angeloni_bracket.py`, `identifiability_panel`, especially the docstring and SSE/profile calculations |
| Least-squares inventory in formal panel | `angeloni_bracket.py`, `c_star = dot(F,m)/dot(F,F)` |
| Inverse-Hessian coupling | `angeloni_bracket.py`, inversion of `H` and `rate_cs0_correlation` |
| Profile fraction on log grid | `angeloni_bracket.py`, `within` and `mean(within)` |
| Coarse production rate grid | `angeloni_bracket.py`, `_RATE_DOMAIN = geomspace(0.15, 6.5, 18)` |
| Fixed-time pooled species bracket | `angeloni_bracket.py`, `gate_pannusch_angeloni_species_bracket(..., t_shot_s=25.0)` |
| 40 g represented as 40 mL | `angeloni_bracket.py`, `_V_TARGET_ML = 40.0` and `_matched_bounds` |
| Inferred cross-grind flow | `angeloni_bracket.py`, `_TAU_GRAN`, `_KR`, and `_flow_gran` |
| Early rounding in joint fit | `angeloni_bracket.py`, `joint_multigrind_fit`, rounded per-grind values before pooled aggregation |
| Dependent residual bootstrap | `angeloni_bracket.py`, `loco_cv_refit`, independent resampling of `all_mape` |
| Global geometry sweep | `angeloni_bracket.py`, `geometry_sensitivity_transfer`, same `geom` passed to all grinds |
| Six-window aggregate | `identifiability.py`, fractions 1/2/3/5/7/10 and duration-weighted sampled aggregate |
| Same-model simulation | `identifiability.py`, `full_cup_simulation_identifiability`, generating and fitting with the same solver |
| External target-level profiling | `external_waszkiewicz.py`, `_level_mape` applied at every rate |
| Shifted flow but unshifted bin mass | `external_waszkiewicz.py`, `binmass` computed before `qf` offset loop |
| Uncertainty omitted in external profile | `external_waszkiewicz.py`, unweighted MAPE despite bin uncertainty metadata |
| Incomplete paper build | `figures_paper_a.py`, `compute_all` result list |
| Wrong Figure 3/4 units | `figures_paper_a.py`, axes labeled `observed/predicted (mg/g)` |
| Figure 5 text disagreement | `figures_paper_a.py`, title generated from rounded joint summary |
| Figure 6 overclaim | `figures_paper_a.py`, title “identifies the rate” |

---

## 14. Final recommendation

**Major revision.** The manuscript has a worthwhile and potentially publishable core: a carefully scoped case study showing that endpoint prediction, cross-condition/grind transfer, and parameter localization need not agree. The matched-endpoint correction strengthens the scientific story and should remain a central methodological lesson.

The current numerical evidence is nevertheless undermined by objective inconsistency, an overinterpreted Hessian statistic, dependence-ignoring uncertainty, incorrect plotted units, a residual fixed-time bracket, imprecise flow/geometry labels, early rounding, and incomplete reproducibility. These are not cosmetic issues. They affect the quantitative support for the headline condition numbers, profile widths, confidence language, transfer summary, and external-evidence taxonomy.

After the P0 actions are completed and all outputs are regenerated from a frozen, fully specified build, the paper should be reevaluated on the corrected profiles and uncertainty analysis. The most likely durable conclusion is narrower but still valuable:

> **In the tested espresso model and datasets, a single-grind matched-endpoint design leaves inventory and kinetic rate strongly practically compensating, while predictions can remain stable across held-out conditions and grinds; fraction-resolved observations provide stronger rate-objective localization than aggregated observations.**

That conclusion is scientifically useful without requiring claims of general structural non-identifiability or universal failure of cup-integrated measurements.

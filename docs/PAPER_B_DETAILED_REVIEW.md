# Detailed technical review of `PAPER_B_DRAFT.md`

**Repository:** [`trbrewer/puckworks`](https://github.com/trbrewer/puckworks)  
**Review snapshot:** commit [`8ca073fdda68a2032d321abe5401eb5d531d6e88`](https://github.com/trbrewer/puckworks/commit/8ca073fdda68a2032d321abe5401eb5d531d6e88)  
**Manuscript reviewed:** [`docs/PAPER_B_DRAFT.md`](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/docs/PAPER_B_DRAFT.md)  
**Figures reviewed:** Paper B Figures 1–5 and their plotting code  
**Review date:** 2026-07-13  
**Recommendation:** **Major revision before journal submission**

---

## 1. Scope, review basis, and limitations

This review covers the Paper B manuscript, all five rendered figures, the analysis functions that generate the reported quantities, the principal model implementations, the committed Schmieder-derived table, the data manifest, and primary supporting literature. I examined, in particular:

- [`docs/PAPER_B_DRAFT.md`](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/docs/PAPER_B_DRAFT.md)
- [`puckworks/harness.py`](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/puckworks/harness.py)
- [`puckworks/figures.py`](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/puckworks/figures.py)
- [`puckworks/models/brewer2026/streamtube.py`](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/puckworks/models/brewer2026/streamtube.py)
- [`puckworks/models/brewer2026/coupled_kappa_t.py`](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/puckworks/models/brewer2026/coupled_kappa_t.py)
- the Waszkiewicz poroelastic implementation and the committed Schmieder cup-mass representation
- `docs/figures/fig1_result1_tds_ey.png` through `fig5_concentration_floortest.png`
- the repository manifest and figure-generation documentation

The manuscript has already incorporated several thoughtful corrections, especially the matched-observable rule, the downgrade from mechanism identification to model capacity in Result 1, the use of explicit constant nulls in Result 2, and the removal of a formal “stability” claim from Result 3. Those corrections should be preserved.

I performed a static traceability audit and a targeted independent recomputation of the Schmieder TDS/BR 1/2 response-surface fit from the committed CSV. I did **not** claim a clean-room reproduction of every slow model sweep or the complete package test suite. The repository does not yet expose one frozen, environment-locked command that generates a machine-readable Paper B results bundle and then all manuscript figures from that bundle. Accordingly, comments below distinguish:

1. **definite implementation or reporting defects**, established directly from manuscript/code inspection;
2. **statistical and inferential limitations**, which require revised analysis or wording; and
3. **numerical or physical robustness questions**, which require additional runs rather than editorial changes alone.

Line-number links in this review point to the reviewed commit so that the evidence remains stable if `main` changes.

---

## 2. Executive assessment

Paper B has the basis of a useful methodological paper. Its strongest scientific contribution is not that any one mechanism has been identified, but that **integrated espresso observables often support mechanism capacity while providing weak mechanism discrimination**. The manuscript also makes a valuable distinction among a machine-only null, static bed models, time-varying bed models, and a flexible phenomenological time function. This null-first framing is worth publishing.

The current draft is nevertheless not submission-ready. The central blockers are:

1. **The manuscript is still a project-management draft rather than a conventional paper.** It openly says that Methods, novelty searching, equations, uncertainty methods, references, data/code availability, and a pinned release remain “owed,” and it retains internal instructions such as “review-endorsed,” “gated,” function names, and a status/to-do section.

2. **The statistical unit and source design are described inaccurately.** The source study reports 15 settings, each with three extraction repetitions and six at the center point. Calling each dial cell “a single DoE experiment” with “no between-experiment replication” obscures that the source’s unit was an extraction run. The Welch interval is still campaign-conditional and confounded by achieved operating conditions, but the hierarchy must be stated correctly before deciding what inference is defensible.

3. **The Schmieder RSM refit does not reproduce the source’s stated predictor contract.** The source used set grind and experimentally achieved flow and temperature; the repository refit uses target flow and target temperature. It also assumes a retained term set without documenting exact equality to the source’s backward-eliminated OriginPro model.

4. **The RSM uncertainty and conditioning language is stronger than the calculation supports.** The design is fixed, but the code uses a row/case bootstrap. It reports `cond(XᵀX)` as a “design condition number,” and accepts every finite bootstrap vertex without requiring a concave, in-domain maximum. The present interval is numerically similar under several bootstrap variants, but the method and labels need correction.

5. **Figure 2 is not generated from the analysis it appears to summarize.** Its qualitative cells are hard-coded; the computed discrimination result is loaded and then unused. This directly conflicts with the figure-directory claim that manuscript numbers are not hand-entered.

6. **The Result 2 complexity labels and validation comparison are misleading.** “0p” means zero additional coefficients fitted to the particular flow trace, not zero parameters. The imported poroelastic trajectory contains campaign- and donor-estimated quantities. The four-parameter cubic is fitted and scored on the same trace, so its in-sample RMSE is not a fair predictive benchmark.

7. **Serial residual structure is a central lack-of-fit result but is not visualized.** A mean Durbin–Watson statistic near 0.01 after one-second decimation implies that the residuals are strongly structured. RMSE rankings without residual panels or dependence-aware validation do not establish an adequate dynamic model.

8. **The cross-pressure code contains a definite precision bug and the LOPO interpretation is overextended.** The field called “full precision” averages values that were already rounded. Leave-one-pressure-out refitting shows that the two-parameter equilibrium calibration is not dominated by one pressure; it does not prove that residual “regimes” are properties of the physics.

9. **The swelling/fines “refuted by sign” claim is too broad.** Under a fixed-pressure, isolated resistance-increasing branch, such a branch cannot by itself produce a positive flow contribution. That is a useful conditional sign constraint. It does not establish that swelling or fines are absent from a coupled puck–machine system.

10. **Result 3 is a constructed finite-time positive-feedback example, not yet a robust physical result.** The model reuses a whole-bed empirical extraction trajectory as a local streamtube clock, builds conductance–flow–age feedback into the update, compares boundary conditions with different normalizations, and sweeps only one numerical floor. The current evidence supports a numerical counterexample in one configuration, not the statement that the concentration itself is generally robust.

These issues are remediable. The recommended revision is to make the paper explicitly about **limits of mechanism discrimination under matched integrated observables**, move or substantially expand the exploratory network result, and make every quantitative evidence label correspond to a documented calibration/evaluation contract.

### Recommended editorial disposition

| Dimension | Assessment |
|---|---|
| Scientific question | Important and timely for mechanistic model evaluation in espresso brewing |
| Conceptual contribution | Strong null-first and observability framing |
| Current statistical support | Mixed; several headline quantities are conditional on an incompletely specified hierarchy or model-selection procedure |
| Current mechanistic support | Capacity and incompatibility tests are useful; identification/refutation language remains too strong in places |
| Current reproducibility | Promising provenance structure, but figure/result generation is not yet fully data-driven or frozen |
| Recommendation | **Major revision** |

---

## 3. Strengths to preserve

1. **The matched-observable rule is excellent.** The draft correctly rejects aggregation across components, units, brew ratios, temperatures, and experimental roles before those contracts are made explicit. This should be elevated from repository terminology into a conventional Methods subsection on observation operators and comparability.

2. **The model-capacity versus mechanism-identification distinction is scientifically mature.** Result 1 now says that a static heterogeneous streamtube model can generate a small interior maximum without claiming that channeling has been identified. That is the correct direction.

3. **The null-first ladder is a valuable contribution.** Showing that a machine-only model can generate a dip-and-recovery shape, and that a flexible temporal null performs similarly to a physical trajectory on one trace, prevents overinterpretation of visual shape matching.

4. **The draft often discloses circularity and transfer limitations.** It explicitly notes that the empirical dissolution trajectory is derived from the same rig and that cross-pressure transfer is within campaign. These caveats should be made structurally visible in tables and figures rather than left only in prose.

5. **The composition failure is worth reporting.** A physically motivated composition that worsens the trace can be more informative than another fitted success. The calculation should be presented neutrally as a test of one composition rule and transferred parameterization.

6. **The revised treatment of Result 3 is more honest than a stability claim.** The draft now acknowledges the absence of a Jacobian/eigenmode analysis and the singularity of the closed-form gain at a zero-conductance base state. That restraint should be extended to the remaining “robust” language.

7. **The repository’s provenance intent is unusually strong.** Model cards, manifests, explicit gates, and typed contracts can support a high-quality reproducibility package once the manuscript-facing workflow is fully automated and frozen.

---

## 4. Required-action matrix

Priority definitions:

- **P0 — validity-critical:** must be resolved before submission because it affects a central result, statistical interpretation, or reproducibility claim.
- **P1 — major reporting/reproducibility:** required for a defensible paper, but less likely to reverse the main qualitative conclusion.
- **P2 — clarity/editorial:** needed for publication quality and reader comprehension.

| ID | Priority | Required action | Acceptance criterion |
|---|---:|---|---|
| AR-01 | P0 | Replace project-management prose with a complete journal manuscript. | No “owed,” “review-endorsed,” “gated,” ROADMAP instructions, code-function narration, or status/to-do section remains in the manuscript body; full Methods, References, Data/Code Availability, and figure captions are present. |
| AR-02 | P0 | Define the experimental unit and hierarchy for the Schmieder analysis accurately. | The paper distinguishes condition setting, extraction run, fraction measurement, derived cup mass, and campaign/generalization level; source replication is described as three extraction repetitions per setting and six at the center, with any independence assumption stated and justified. |
| AR-03 | P0 | Refit the Schmieder RSM using the source’s stated predictors and verified retained terms. | Set grind plus experimentally achieved flow and temperature are used; the retained model is verified against the full-precision Origin object or transparently treated as an independent reanalysis. |
| AR-04 | P0 | Correct RSM bootstrap and numerical-conditioning reporting. | A fixed-design-appropriate residual, wild, or parametric bootstrap is used or justified; valid concave/in-domain vertex fraction is reported; `κ₂(X)` is distinguished from `κ₂(XᵀX)`; predictors are centered/scaled for computation. |
| AR-05 | P0 | Make Figure 2 data-driven. | Every matrix cell is generated from a committed structured evidence table with documented criteria; no manuscript-facing qualitative result is hand-coded in plotting logic. |
| AR-06 | P0 | Correct model-complexity labels and add out-of-sample or penalized comparison for Result 2. | “0p” is replaced by a complete accounting of flow-fitted and donor-fitted quantities; the cubic and physical models are compared using blocked/rolling/whole-trace validation or a justified information criterion. |
| AR-07 | P0 | Surface residual dependence and uncertainty. | Main or supplementary figures show residuals and autocorrelation; uncertainty in RMSE differences is dependence-aware; the manuscript does not treat densely sampled time points as independent replicates. |
| AR-08 | P0 | Fix cross-pressure precision and overclaiming. | Unrounded values are retained until display; the so-called full-precision mean is genuinely full precision; LOPO is described only as calibration-stability/within-campaign held-out evidence. |
| AR-09 | P0 | Narrow the sign-test conclusion. | The claim is explicitly limited to isolated, resistance-increasing branches under the imposed fixed-pressure boundary condition; “refuted,” “excluded,” and “coffee-independent” are removed unless a broader theorem is supplied. |
| AR-10 | P0 | Reframe or expand Result 3. | Either move it to an exploratory/supplementary numerical example, or provide a physical lateral operator, consistent boundary conditions, convergence analysis, and a broad parameter/start-state sensitivity study. |
| AR-11 | P1 | Document the static-channeling calibration/evaluation chain. | A table gives source observable, grinder axis, inferred σ values, closure fit, uncertainty, and evaluation target; non-portability is explicit and “observable matched” is not marked unqualified “yes.” |
| AR-12 | P1 | Add a complete calibration/evaluation map for every result. | Each parameter is labeled as fixed from literature, fitted to the target trace, fitted to another observable in the same campaign, or independently transferred. |
| AR-13 | P1 | Make Figure 1 statistically and visually honest. | Raw extraction-run points are shown; error-bar definition is explicit; the phrase “raw: monotone” is replaced; achieved-condition RSM and uncertainty band are plotted. |
| AR-14 | P1 | Redesign Figures 3–5 for diagnostics rather than rhetoric. | Evaluation windows are shaded, residuals/uncertainty are shown, loaded words such as “FAILED,” “OVER-closes,” and “refuted” are removed, and complexity/provenance labels are explicit. |
| AR-15 | P1 | Create one reproducible Paper B build. | One command writes a versioned results bundle and all vector figures; outputs contain commit SHA, environment, data hashes, seeds, parameter sets, and timestamps; figures consume the bundle only. |
| AR-16 | P1 | Complete a systematic related-work and novelty section. | Search databases, dates, queries, screening rules, and included studies are documented; novelty claims are bounded to the completed search. |
| AR-17 | P1 | Correct source-year and dataset terminology. | The published Waszkiewicz article is cited as 2026; any `waszkiewicz2025` internal key is identified as a repository/dataset key rather than the article year. |
| AR-18 | P2 | Supply journal-quality captions and accessible graphics. | Captions define data, model status, fitted quantities, evaluation window, error bars, and inference limits; color is not the sole carrier of meaning; vector files and source data are released. |
| AR-19 | P2 | Consolidate the paper around one thesis. | Introduction, Results, and Discussion consistently frame the work as limits of discrimination from integrated observables rather than three only loosely related mechanism stories. |

---

## 5. Detailed major comments

### MAJ-01 — The document is not yet a submission manuscript

The manuscript begins with internal review instructions and a “review-endorsed” title, tells the author which verbs to use, embeds source-code paths in the prose, states that a conventional Methods section is still owed, and ends with a “Status & to-do (NOT for the manuscript body)” section. See, for example, [`PAPER_B_DRAFT.md` lines 1–17](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/docs/PAPER_B_DRAFT.md#L1-L17), [`lines 91–116`](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/docs/PAPER_B_DRAFT.md#L91-L116), and [`lines 377–434`](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/docs/PAPER_B_DRAFT.md#L377-L434).

This is not merely a stylistic issue. The missing material includes the equations, calibration/evaluation splits, numerical tolerances, statistical model, uncertainty methods, related-work search, data/code statement, and pinned release needed to evaluate the claims. A reviewer cannot reconstruct those contracts reliably from function names.

**Required action:** Create a clean submission branch of the manuscript with conventional sections:

1. Introduction and pre-specified research questions;
2. Data and observation operators;
3. Models and parameter provenance;
4. Statistical and numerical methods;
5. Results;
6. Discussion and limitations;
7. Data/code availability;
8. References;
9. complete figure captions.

Move review history, verb rules, implementation status, and future-work tracking to `ROADMAP.md` or a response-to-review document. Function names may appear in a reproducibility appendix, not as substitutes for method descriptions.

---

### MAJ-02 — The paper needs one explicit inferential thesis

The three results currently concern:

- a dial-response/RSM and a static heterogeneous ensemble;
- time variation in a pressure-trace ladder; and
- an exploratory finite-time streamtube network.

They are connected by observability, but the connection is stated most clearly only in the Discussion. The title promises “mechanism discrimination,” while large portions of the draft establish model capacity, within-campaign incompatibility, or numerical behavior rather than discrimination in a common statistical experiment.

**Recommended thesis:**

> “Integrated espresso measurements can reject some model–boundary-condition combinations and establish model capacity, but they generally provide weak mechanism identification without pathway-resolved or independently measured bed-state observables.”

A title aligned with the actual evidence would be:

> **Limits of mechanism discrimination from integrated espresso measurements: matched observables, null models, and exploratory streamtube dynamics**

This formulation preserves the novelty of the framework without implying that all candidate mechanisms were symmetrically adjudicated.

**Required action:** Recast each result under the same four questions:

1. What is the observation operator?
2. What is calibrated, and on which data?
3. What is genuinely held out?
4. What conclusion is licensed: capacity, incompatibility, transfer, or identification?

---

### MAJ-03 — The Schmieder experimental unit and replication hierarchy are misstated

The draft says that “each dial cell is a single DoE experiment” and that there is “no between-experiment replication” ([`lines 120–140`](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/docs/PAPER_B_DRAFT.md#L120-L140)). The source paper instead describes a face-centered central composite design with 15 settings, **three extraction repetitions per setting and six repetitions at the center point**. It also states that extraction kinetics were fit for each experimental run and that cup masses were calculated by integrating each replicate individually.

The hierarchy should therefore be described as:

- **condition setting:** one point in the face-centered design;
- **experimental unit:** independently prepared espresso extraction/run at that setting, assuming the source preparation procedure made runs independent at the intended campaign level;
- **within-run observations:** fractions and instrument time samples;
- **derived response:** cup mass or TDS-derived EY from each run;
- **external-generalization unit:** not provided—there is one machine, one main coffee/campaign, and no independent replication across rigs or campaigns.

The present Welch contrast can describe the difference among repeated extraction runs at the three selected settings, conditional on that campaign and assuming those runs are independent. It does **not** isolate a causal dial effect because achieved flow, pressure, and temperature differ with dial, nor does it generalize to machines/coffees/days. The ambiguity resembles the general problem emphasized in the literature on pseudoreplication: the inferential unit must match the level at which treatment and independence operate. Do not invoke a stronger population than the design supports.

The manuscript also says that the raw ordering “rules out a middle-dial maximum.” A safer statement is that the **observed central-condition cell means do not contain a middle-dial maximum**. Inferential exclusion of an underlying conditional response maximum requires a specified model for achieved covariates and run-level variation.

**Required action:**

- Correct the source description to “three independently prepared extraction runs per setting; six at the center,” unless source metadata show a different hierarchy.
- State whether run order was randomized or blocked and whether the two roast batches contributed to the analyzed design.
- Use the extraction run, not fractions or dense sensor points, as the unit for the selected-cell comparison.
- Show all run-level points in Figure 1.
- Report the Welch interval as a within-campaign, setting-level contrast; do not use it as evidence that dial alone caused the difference.
- Fit a whole-design model using achieved flow and temperature and an explicit treatment of pressure/confounding. Report dial-response uncertainty conditional on that model.

**Supporting reference:** Hurlbert’s classic discussion is useful for the principle that replication and independence must be defined at the level of the treatment/inference, but the paper should not label the source repetitions “pseudoreplicates” without establishing that they were dependent.

---

### MAJ-04 — The RSM refit uses target rather than achieved flow and temperature

The repository refit extracts `target_flow_ml_s` and `target_temp_C` in [`harness.py` lines 938–968](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/puckworks/harness.py#L938-L968). Figure 1 independently duplicates the same target-predictor refit in [`figures.py` lines 67–93](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/puckworks/figures.py#L67-L93).

The source Methods state that the RSM used **set grinding levels and experimental values for flow rate and temperature**, followed by ANOVA-based backward elimination. The committed CSV includes achieved-flow (`scale_flow_ml_s`) and achieved-temperature (`decent_temp_C`) fields. Therefore, the current refit is not a strict reproduction of the published model contract.

A targeted audit of the 48 committed TDS/BR 1/2 observations found:

| Refit | R² | Adjusted R² | Residual σ [g] | Grind vertex at flow 2.0 |
|---|---:|---:|---:|---:|
| Current target-flow/target-temperature specification | 0.6941 | 0.6494 | 0.1128 | 1.7332 |
| Achieved-flow/achieved-temperature specification | 0.6889 | 0.6434 | 0.1137 | 1.7501 |
| Achieved specification at the mean achieved flow of the central cell (1.9011 mL s⁻¹) | — | — | — | 1.7432 |

The headline vertex is therefore not radically changed in this dataset, but that numerical similarity does not repair the method mismatch. Moreover, the code assumes a retained term set of intercept, F, G, T, G², T², and F×G. That set appears consistent with the printed TDS/BR 1/2 row, but the paper must verify it against the full-precision OriginPro model or label the calculation as an independent refit rather than a reconstruction.

**Required action:**

1. Refit with achieved flow and achieved temperature, set grind, and the exact source-selected terms.
2. If the full-precision Origin object is unavailable, label the result “our refit of the source design” rather than “the study’s own fitted response surface.”
3. Report sensitivity to target versus achieved predictors.
4. Remove the duplicated fitting code from `figures.py`; the figure should consume a single analysis result.
5. Regenerate the vertex, interval, prediction curve, diagnostics, and text from that corrected result.

---

### MAJ-05 — The RSM bootstrap and “real maximum” language need correction

The code performs 2,000 **case resamples** of rows, refits the fixed-design regression, and accepts every finite vertex ([`harness.py` lines 979–996](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/puckworks/harness.py#L979-L996)). The manuscript then says the interval confirms that the interior maximum is “a real but modest feature” ([`lines 142–153`](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/docs/PAPER_B_DRAFT.md#L142-L153)).

There are four problems:

1. **Fixed design:** the design points were selected, not sampled from a random covariate distribution. A residual, wild, or model-based bootstrap is usually the more natural conditional bootstrap for a fixed-design regression, subject to its error assumptions.
2. **Model selection:** the source used backward elimination. The repository conditions on the selected term set and does not repeat model selection. The interval is therefore conditional on the chosen model form.
3. **Vertex validity:** a finite algebraic vertex is not necessarily a concave maximum or within the experimental dial domain.
4. **Interpretation:** a narrow interval conditional on a selected quadratic model does not establish that the physical response truly has an interior maximum.

My independent audit of the present target-predictor fit found:

| Bootstrap, 2,000 draws | 95% vertex interval | Concave fits | In-domain vertices [1.4, 2.0] | Both concave and in-domain |
|---|---:|---:|---:|---:|
| Current case bootstrap | [1.6815, 1.8125] | 1,995 | 1,994 | 1,992 |
| Fixed-X residual bootstrap | [1.6911, 1.7989] | 2,000 | 1,998 | — |
| Fixed-X Rademacher wild bootstrap | [1.6899, 1.8102] | 2,000 | 1,997 | — |

The central interval is numerically stable across these three implementations, which is reassuring. Yet the case bootstrap produced extreme finite vertices from −0.21 to 3.59, illustrating why validity classification should be explicit rather than silently including all finite values.

**Required action:**

- Use a residual, wild, or parametric bootstrap appropriate to the stated residual model and fixed design, or explicitly justify case resampling.
- State that the interval is conditional on the retained quadratic model and design.
- Report the percentage of fits that are concave and whose vertex lies inside the experimental domain.
- Consider repeating the source’s model-selection step in each bootstrap if the intended target includes selection uncertainty.
- Replace “confirming the interior maximum is real” with:

> “Under the specified quadratic refit, the estimated grind-direction vertex is interior, and its conditional bootstrap interval remains within the tested dial range.”

This is strong enough and accurately scoped.

**Supporting reference:** Freedman (1981) distinguishes bootstrap behavior under different regression formulations and is an appropriate starting point for justifying the bootstrap target.

---

### MAJ-06 — The condition number is mislabeled, and raw-scale fitting should be stabilized

The code computes `XtX = X.T @ X` and then `np.linalg.cond(XtX)`, storing the result as `design_condition_number` ([`harness.py` lines 997–1018](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/puckworks/harness.py#L997-L1018)). The manuscript reports a raw-scale design condition number of approximately `3×10¹²`.

For the committed target-predictor design, my audit gives:

- `κ₂(X) = 1.66×10⁶`
- `κ₂(XᵀX) = 2.74×10¹²`

The second is approximately the square of the first and is the condition number of the normal-equation/Gram matrix, not the design matrix. This distinction matters because readers use “design condition number” to assess the numerical geometry of `X`.

The fit itself uses `np.linalg.lstsq`, which is preferable to explicitly solving normal equations, but the reporting and covariance calculation use the poorly conditioned raw-scale Gram matrix. Temperature and temperature squared make this particularly severe.

**Required action:**

- Center and scale continuous predictors before fitting and computing covariance.
- Use QR or SVD-based covariance diagnostics where possible.
- Report `κ₂(X)` and, only if useful, `κ₂(XᵀX)` under their correct names.
- Report coefficient estimates in interpretable centered units, then transform only predictions/vertices back to original units.
- Remove any implication that a large raw-scale condition number by itself invalidates the offset-invariant vertex; instead show numerical sensitivity directly.

---

### MAJ-07 — Figure 1 overstates the raw-cell result and hides the run-level data

Figure 1(a) plots means with error bars from `np.std(..., ddof=0)` and labels the result “raw: monotone (no bump).” The plotting path is in [`figures.py` lines 56–126](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/puckworks/figures.py#L56-L126); the standard deviation is calculated with `ddof=0` in [`harness.py` lines 437–475](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/puckworks/harness.py#L437-L475).

Problems:

- “Monotone” sounds inferential; there are only three nominal settings and the fine-to-middle contrast includes zero under the manuscript’s own Welch calculation.
- Error bars are not identified in the graphic as population-form descriptive SD, sample SD, SE, or CI.
- The source reports repeated extraction runs; displaying only means hides sample size and distribution.
- The RSM curve uses target operating variables rather than the source’s achieved-variable contract.
- The panel juxtaposes a Schmieder E65S dial and a separate Cameron/model grind coordinate. The text says “own dial axis,” but the visual proximity can still suggest transferability.
- No uncertainty band is shown for the fitted response curve except the vertex span.

**Required action:**

- Plot every extraction-run value with jitter, then overlay mean and a clearly defined interval.
- Use sample SD (`ddof=1`) if the intention is to summarize the observed sample, or retain `ddof=0` only with an explicit descriptive definition and rationale.
- Replace “raw: monotone” with “observed cell means increase; no observed middle-cell maximum.”
- Plot the corrected achieved-predictor curve and a conditional confidence or prediction band.
- Make the non-portability of the two x axes visually unmistakable—preferably separate them into Figure 1 and a supplementary model-capacity figure rather than one side-by-side causal-looking comparison.

---

### MAJ-08 — Static channeling is a cross-dataset capacity demonstration, not a matched validation

The static streamtube calculation uses unit-mean lognormal permeability multipliers and a fitted closure from a Cameron-derived calibration, then evaluates the ability to generate a response shape associated with the Schmieder dial axis. The manuscript correctly calls this asymmetric, but Figure 2 marks the static-channeling observable as matched “yes.”

The calibration and evaluation differ in several dimensions:

- source dataset and machine;
- grinder and grinder coordinate;
- the calibration target is a residual/deviation relative to a homogeneous model;
- the evaluation target is TDS-derived EY versus a different dial;
- the closure is grind-calibrated, but no calibrated map exists between grinder coordinates;
- the evaluation response is confounded with achieved pressure and flow.

This can establish that a particular heterogeneity model class has **capacity** to create a small interior response under its own closure. It cannot be called a quantitatively matched external validation.

The Jensen argument is plausible but should be written with the exact numerical observation operator. `ey_of_k` clips log-permeability queries to the simulated support, and the deficit is compared with `EY(1)`. Because the quadrature nodes are theoretically unit mean before clipping/interpolation, the numerical audit should also report the actual weighted mean after support handling and convergence with quadrature order/support.

**Required action:**

Create a calibration/evaluation table with columns:

| Model | Calibration data | Calibration observable | Fitted quantities | Evaluation data | Evaluation observable | Transfer distance | Status |
|---|---|---|---|---|---|---|---|

For static channeling, status should read something like **cross-dataset qualitative capacity, non-portable grind coordinate**, not “matched validation.” Include the source points used to infer σ, closure-fit uncertainty, quadrature convergence, actual numerical mean multiplier, clipped mass, and sensitivity to the response interpolation domain.

---

### MAJ-09 — Figure 2 is hard-coded and its evidence categories are not operationally defined

This is a definite reproducibility defect. `fig2_evidence_matrix` calls `h.schmieder_peak_discrimination()` and builds `by`, but never uses the result. Every displayed cell is typed manually in the `rows` list ([`figures.py` lines 130–163](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/puckworks/figures.py#L130-L163)). Thus a code or data change can alter the analysis without changing the figure.

The matrix also lacks reproducible definitions:

- What exactly qualifies as “observable matched”?
- Does “params constrained” distinguish fitted to the target, fitted to another observable in the same campaign, literature-fixed, or independently measured?
- Why is every implemented mechanism assigned “partial” evidence strength?
- Is “generates interior max” evaluated at a registered nominal parameterization, anywhere in a sensitivity range, or after tuning?
- How is an unimplemented mechanism compared to implemented candidates without conflating software availability and scientific evidence?

The red/green/orange palette also relies heavily on color semantics. Scientific visualization guidance recommends avoiding color mappings that are inaccessible or imply unsupported ordinal meaning.

**Required action:**

- Commit a structured evidence file such as `paper_b_evidence_matrix.yaml` or CSV.
- For every cell, include: value, criterion, evidence source, analysis function, commit, and reviewer note.
- Generate the plot from that file and validate it against analysis outputs in tests.
- Replace ambiguous “yes/partial/no” with more specific statuses such as `implemented`, `target-fitted`, `same-campaign transfer`, `independent transfer`, `observable mismatch`, `parameter-blocked`, and `not implemented`.
- Use text/symbols as well as a colorblind-safe palette.
- Put the “decisive missing measurement” in the visual or a companion table; this is more informative than a generic evidence-strength column.

**Supporting reference:** Crameri, Shephard, and Heron (2020) provide relevant guidance on scientifically faithful and accessible color use.

---

### MAJ-10 — “Zero parameters” in the Result 2 ladder is not an adequate complexity description

Figure 3 labels the static and Φ(t) branches “0p,” and the prose calls the empirical porosity trajectory “zero-free-parameter” or “zero-parameter” ([`PAPER_B_DRAFT.md` lines 212–230](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/docs/PAPER_B_DRAFT.md#L212-L230); [`figures.py` lines 190–207](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/puckworks/figures.py#L190-L207)).

The intended distinction is legitimate: no additional coefficient is optimized directly against the 9-bar flow trace for those branches. But the models are not parameter-free:

- the flow relation contains the campaign-calibrated equilibrium pair `(P_c, Q_c)`;
- Φ(t) contains a solids sigmoid fitted to a 9-bar TDS trajectory from the same rig/campaign;
- RC-3b imports parameters from Cameron and recomputes a dissolution path;
- the machine/bed formulations contain fixed literature or repository parameters.

A single integer parameter count cannot communicate this provenance. More importantly, the four-parameter cubic is fit and scored on the **same 15–95 s trace**, while the physical branch imports parameters from related data. The resulting RMSE comparison is useful as an in-sample capacity bound but is not a fair predictive model selection.

**Required action:** Replace `0p/1p/4p` with a two-level complexity table:

| Model | Parameters fitted to this Q(t) trace | Parameters fitted elsewhere in same campaign | External/literature-fixed quantities |
|---|---:|---:|---|
| Best constant | 1 | 0 | 0 |
| Long-run constant | 1 interval-derived level | 0 | 0 |
| Static κ(P) | 0 | 2 equilibrium parameters | constitutive form |
| Empirical Φ(t) | 0 | 2 equilibrium + 3 TDS-sigmoid parameters | constitutive form |
| RC-3b | 0 | 2 equilibrium parameters | Cameron donor calibration/model |
| Cubic | 4 | 0 | polynomial form |

Then either:

1. evaluate all candidates on held-out contiguous time blocks/whole traces/pressures; or
2. explicitly call the cubic an **in-sample flexibility bound**, not a predictive competitor.

---

### MAJ-11 — The temporal comparison needs dependence-aware validation

Time samples in an espresso trace are strongly dependent. The manuscript itself reports a mean Durbin–Watson statistic near 0.01 after decimating to one-second resolution ([`lines 285–295`](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/docs/PAPER_B_DRAFT.md#L285-L295)). This is not a minor diagnostic; it shows that model residuals contain persistent structure.

Consequences:

- the apparent number of data points is much larger than the effective information content;
- standard pointwise residual assumptions are untenable;
- in-sample RMSE differences may be stable numerically but do not quantify predictive uncertainty;
- a cubic fit can exploit smooth temporal structure when trained and evaluated on the same interval;
- confidence intervals based on independent time points would be severely overconfident.

Blocked cross-validation is a standard remedy when data have temporal structure. The exact scheme should reflect the deployment question. Options include:

- leave out one or more contiguous time blocks;
- rolling-origin prediction, fitting on early time and predicting later time;
- fit at one pressure and evaluate whole traces at other pressures;
- hierarchical validation at the shot/pressure level, not at the individual time-sample level.

**Required action:**

- Add residual-versus-time and ACF plots for every ladder rung.
- Report bias, MAE, RMSE, and maximum structured deviation, not RMSE alone.
- Use blocked or rolling validation for the cubic and any data-fitted dynamic model.
- Quantify uncertainty by resampling entire blocks/traces/pressures, not individual samples.
- State that the current RMSE ladder demonstrates reconstruction capacity on one interval unless and until held-out temporal prediction is provided.

**Supporting reference:** Roberts et al. (2017) review cross-validation strategies for temporally, spatially, and hierarchically structured data and explain why random splits can underestimate predictive error.

---

### MAJ-12 — The cross-pressure aggregation contains a definite “full precision” bug

In `cross_pressure_discrimination`, each pressure-specific RMSE is rounded to three decimals when inserted into `per` ([`harness.py` lines 1147–1162](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/puckworks/harness.py#L1147-L1162)). The object named `full_prec` then averages those already-rounded values ([`lines 1164–1172`](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/puckworks/harness.py#L1164-L1172)). Therefore, `conditional_transfer_mean_full_precision` is not full precision.

This is unlikely to change a qualitative ranking, but it is a direct contradiction between field name and computation. It also illustrates why rounding should occur only in the reporting layer.

**Required action:**

- Store raw floating-point per-pressure RMSEs.
- Calculate all summaries from raw values.
- Round only while formatting tables/figures.
- Add a unit test asserting that the “full precision” field equals the mean of raw, unrounded values and differs appropriately from the display-rounded field when expected.
- Regenerate the manuscript values in [`lines 275–287`](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/docs/PAPER_B_DRAFT.md#L275-L287).

---

### MAJ-13 — The pressure-regime narrative is internally inconsistent and risks post-hoc categorization

The `cross_pressure_discrimination` docstring says that low- and mid-pressure bins were fixed a priori on physical grounds ([`harness.py` lines 1129–1135](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/puckworks/harness.py#L1129-L1135)). The manuscript says the bins are descriptive and not predeclared ([`PAPER_B_DRAFT.md` lines 259–268](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/docs/PAPER_B_DRAFT.md#L259-L268)). Both cannot be true.

If the categories were created after seeing residual curves, they may be useful descriptive summaries but should not support a mechanistic regime claim. If they were genuinely specified before analysis, the protocol/date and physical thresholds should be documented.

**Required action:**

- Resolve the code/manuscript contradiction.
- Prefer continuous pressure-residual plots and smooth effect summaries over winner bins.
- If categorical regimes are retained, provide a time-stamped protocol or commit showing pre-specification, the physical rationale for thresholds, and uncertainty around crossing pressures.
- Do not describe mechanism-specific “regimes” from visually selected intervals without independent replication.

---

### MAJ-14 — Leave-one-pressure-out refitting shows calibration stability, not that regimes are physical

`cross_pressure_loco` refits only the two-parameter equilibrium pair `(P_c, Q_c)` while holding the 9-bar TDS sigmoid and all other donor assumptions fixed ([`harness.py` lines 1202–1284](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/puckworks/harness.py#L1202-L1284)). Small calibration drift and similar held-out/shared RMSEs support a useful but narrow conclusion:

> The equilibrium calibration is not dominated by any single pressure point.

They do **not** show that the residual regimes are “a property of the physics,” as the code and manuscript state. The pattern could also arise from:

- a pressure-independent 9-bar sigmoid transferred outside its calibration pressure;
- omitted machine dynamics or control effects;
- viscosity or sensor calibration;
- an imperfect equilibrium constitutive form;
- time alignment or windowing;
- shared preprocessing;
- other omitted bed mechanisms.

There is also a presentation problem: the manuscript juxtaposes means over different pressure sets—11-pressure LOPO means, 11-pressure shared-calibration means, and 10 off-9-bar conditional-transfer means—making numbers such as 0.534/0.347/0.516 and 0.512/0.356/0.522 difficult to reconcile.

**Required action:**

- Replace the strong sentence with:

> “LOPO shows that the two-parameter equilibrium calibration is not dominated by any one pressure. It does not establish that the residual pressure pattern is physical, because the 9-bar solids trajectory and other donor assumptions remain fixed.”

- Put all means in a table with explicit pressure set, calibration procedure, and weighting.
- Add a sensitivity test that refits or perturbs the solids trajectory, time alignment, and window.
- Reserve “held-out prediction” for quantities truly estimated without the held-out trace and describe the remaining same-campaign dependencies.

---

### MAJ-15 — The swelling and fines result is a conditional sign constraint, not a general refutation

The manuscript says that swelling and fines are “excluded” or “refuted by sign,” that the sign is grind- and coffee-independent, and that dissolution opening is the only surviving branch ([`lines 232–257`](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/docs/PAPER_B_DRAFT.md#L232-L257)). Figure 3 repeats “swelling refuted by sign” and “refuted” in the panel annotation ([`figures.py` lines 218–240](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/puckworks/figures.py#L218-L240)).

A sound narrower statement is available:

- under a prescribed constant-pressure boundary condition;
- with machine response omitted or held fixed;
- for an isolated mechanism represented solely as increasing hydraulic resistance;
- and with all other state variables fixed,

that branch cannot by itself generate a positive contribution to flow. This is a useful sign incompatibility test.

But real or coupled behavior can include simultaneous dissolution opening, compaction relaxation, changing saturation, viscosity, gas release, machine/headspace response, erosion/rearrangement, pressure deviations, and state-dependent constitutive coupling. Swelling or fines may be present while another process dominates the net sign. A representative powder parameterization from another rig cannot support “coffee-independent” magnitude or absence.

The analytic fines statement also needs a precise theorem-to-experiment mapping. A lemma under a mathematical model’s assumptions does not automatically apply to the experimental boundary conditions unless those assumptions are enumerated.

**Required action:**

Replace the headline with:

> “Within the imposed fixed-pressure model, the tested resistance-only swelling and fines branches cannot by themselves generate the observed rising contribution. This constrains isolated branches; it does not show that swelling or fines are absent from a coupled bed.”

In the Methods, list every assumption needed for the sign conclusion. In Figure 3, change “wrong sign/refuted” to “isolated resistance-only branch: opposite net trend under fixed pressure.” Treat the Mo magnitude and RMSE as a cross-rig sensitivity example, not a quantitative validation.

**Supporting references:** Mo et al. (2022) model swelling through coupled transport and geometric expansion; Mo et al. (2021) treat flow-induced mechanical erosion. Their mechanisms and boundary conditions should be represented with the same precision used for the repository models.

---

### MAJ-16 — The Foster panel is a reproduction of a source model curve, not independent data validation

Figure 3(a) retrieves `d.foster_fig15_flow()` and plots a reproduced source/model curve with no observed data, residuals, or uncertainty. The annotation says that pump plus headspace “reproduce” a dip-and-recover shape with no bed mechanism ([`figures.py` lines 180–188](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/puckworks/figures.py#L180-L188)). The manifest reportedly identifies this as a model-curve verification rather than a pixel trace of measured data.

The legitimate conclusion is:

> A published machine/infiltration model contains a dip-and-recovery solution in its source configuration without invoking evolving bed resistance.

That establishes availability of a null mechanism for shape interpretation. It is not an independent fit to the Waszkiewicz trace and should not be visually presented as though panel (a) validates the same target used in panels (b–d).

**Required action:**

- Label the line “numerical reproduction of Foster et al. model curve.”
- State the source figure, parameter set, and whether any parameters were refit.
- If digitized experimental data exist, show them and a residual; otherwise avoid “reconstructs the digitized source trace.”
- Visually separate source-model verification from the Waszkiewicz data ladder.

---

### MAJ-17 — The coupled composition’s exact reduction is an implementation identity, not validation

The coupled model is explicitly a project synthesis. Its extraction-only branch is designed so that the composite porosity is converted back into an effective dissolved-mass equivalent and passed through the same Waszkiewicz poroelastic closure; the module docstring says extraction-only must reduce to rung 4 exactly ([`coupled_kappa_t.py` lines 1–31](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/puckworks/models/brewer2026/coupled_kappa_t.py#L1-L31), [`lines 62–93`](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/puckworks/models/brewer2026/coupled_kappa_t.py#L62-L93)).

Therefore, “reduces exactly to the poroelastic rung” is a software consistency check, not evidence for physical degeneracy. The shared-porosity addition rule and mapping to `m_d_eff` are modeling choices. Compaction and fines are zero stubs. The swelling branch notes that it may over-close an already swollen/pre-wet rig, raising a potential initial-state mismatch or double counting.

The statement that a 14× flow rise “requires” a near-choke poroelastic closure is likewise conditional on the adopted porosity trajectory, mapping, and set of candidate closures. It does not prove that coffee beds physically operate only through that closure.

**Required action:**

- Present Figure 4 as a test of **one shared-porosity composition and one transferred swelling parameterization**.
- Derive or justify the additive porosity rule and `m_d_eff` mapping; otherwise label them as hypotheses.
- Define the initial swelling/saturation state and test whether the donor swelling law double counts pre-existing wetting.
- Include alternative composition rules and initial conditions.
- Treat the exact extraction-only reduction as a unit test, not a scientific result.
- Replace “requires near-choke closure” with “within this mapping, the near-choke closure is the only tested relation that reproduces the magnitude.”

---

### MAJ-18 — Figure 4 should be a neutral diagnostic, with the scoring window and residuals visible

Figure 4 plots the full trace while calculating RMSE only on 15–95 s, but does not shade that interval. Its title and annotation use “FAILED,” “OVER-closes,” and “worse than a flat line” ([`figures.py` lines 246–284](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/puckworks/figures.py#L246-L284)). This rhetoric is not needed and obscures the specific scientific conclusion.

The extraction+swelling curve being flatter and having higher RMSE than the best constant over the selected window is a valid diagnostic. Readers need to see where the error occurs, whether time alignment or early transients dominate, and how parameter/initial-state uncertainty changes it.

**Required action:**

- Title: **“Tested shared-porosity composition worsens the 9-bar reconstruction.”**
- Shade the 15–95 s evaluation window.
- Add a residual panel with the same axis.
- Show uncertainty/sensitivity bands for transferred swelling parameters and initial state.
- Use neutral wording: “underpredicts the rise” or “produces a flatter trajectory.”
- State explicitly that the result does not distinguish parameter-transfer error, initial-state error, control-regime mismatch, and composition-form error.

---

### MAJ-19 — The N-tube model builds in positive feedback and changes more than one physical condition between controls

`ntube_kappa_t_union` creates deterministic lognormal conductance nodes, assigns each tube a local extraction age based on relative flow, updates porosity/conductance, and feeds that change back into the relative flow. The resulting loop is structurally positive:

> higher conductance → higher flow share → faster local extraction clock → altered porosity/conductance → changed flow share.

That is a legitimate constructed mechanism, but concentration should not be surprising without a neutral comparison showing which feedback term causes it. The model also reuses a whole-bed empirical Φ(t) trajectory as a local per-tube clock. This is not independently validated as a local constitutive law.

The flow-control and pressure-control implementations use different normalizations. Flow control normalizes current conductances to impose a shared fixed total flow; pressure control references the initial mean, allowing total flow to vary. Thus Figure 5 changes both the boundary condition and the normalization/total-flow behavior. The “lateral” parameter is an algebraic homogenization proxy rather than a dimensional transverse-flow operator.

A stale docstring also reportedly calls static channeling the “unique physical reproducer,” contradicting the manuscript’s capacity-not-identification discipline.

**Required action:**

- Write the network equations explicitly, including dimensions and conservation laws.
- Identify the feedback loop and include ablations: fixed local age, fixed porosity, no flow redistribution, and alternative local extraction laws.
- Compare flow and pressure control within a consistent machine/bed model and report total flow/pressure trajectories.
- Replace the algebraic homogenization proxy with a physical lateral exchange law, or keep it explicitly as a numerical regularizer.
- Remove stale identification language from code and docs.
- Demonstrate mass conservation and non-negativity at every step.

---

### MAJ-20 — Result 3 has only a floor sweep, not a robustness analysis

The manuscript says that “what is robust is the numerical concentration,” because the final effective channel count is unchanged when the conductance floor is swept from `1e-9` to `1e-15` ([`PAPER_B_DRAFT.md` lines 322–346](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/docs/PAPER_B_DRAFT.md#L322-L346)). Figure 5 similarly calls the concentration result robust ([`figures.py` lines 288–342](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/puckworks/figures.py#L288-L342)).

A floor sweep tests only one regularization. The code and manuscript acknowledge dependence on start state and other choices but do not show the required sweeps. At minimum, the result could depend on:

- number of tubes `N`;
- integration substeps/time step and scheme;
- simulation horizon;
- initial permeability distribution and seed/quadrature construction;
- initial local extraction age/porosity;
- pressure, grind, closure steepness, and closure calibration;
- total-flow path;
- local extraction law;
- lateral exchange form and coefficient;
- definition of “collapse” (`N_eff`, maximum share, top-decile threshold);
- conductance floor and porosity clamps.

The deterministic lognormal nodes also mean there is no ensemble uncertainty over finite networks. A final `N_eff≈1` hides whether concentration is monotone, transient, step-size-driven, or caused by one extreme initial node.

**Required action:** Either downgrade Result 3 to a supplementary counterexample or complete a factorial robustness study. Acceptance criteria should include:

1. convergence in `N`, timestep/substeps, and solver method;
2. multiple random finite-network realizations plus deterministic quadrature comparison;
3. trajectories of `N_eff(t)`, maximum flow share, total flow, and mass balance;
4. sensitivity to initial state and horizon;
5. pressure and grind sweeps;
6. closure-parameter uncertainty;
7. a dimensional physical lateral exchange operator;
8. comparison under consistent pressure/flow machine boundary models.

Until then, use:

> “The constructed uncoupled network exhibits finite-time concentration in one near-choke, fixed-total-flow configuration, and the endpoint is insensitive to the tested conductance-floor range.”

Do not call the broader concentration result robust.

---

### MAJ-21 — Figure 5 does not show the evidence needed for its central claim

Figure 5(a) plots only final `N_eff` against an abstract homogenization parameter at fixed `gs=1.1` and `N=150`. Figure 5(b) plots a known floor-sensitive closed-form gain and annotates final `N_eff`. It does not show:

- the time evolution of concentration;
- maximum channel share;
- total outlet flow under pressure control;
- numerical convergence;
- variability across network realizations;
- sensitivity to grind/pressure/start state;
- conservation error;
- the physical scale of lateral exchange.

The closed-form gain is singular by construction near the floor and is already acknowledged not to be a stability eigenvalue. Giving it half the main figure may overemphasize a quantity the paper says is not meaningful.

**Required action:** Redesign Figure 5 around the actual numerical evidence:

- panel (a): `N_eff(t)` and maximum share over time for key controls/closures;
- panel (b): convergence with `N` and timestep;
- panel (c): pressure × grind or closure-slope sensitivity;
- panel (d): effect of a physical lateral exchange coefficient, with units;
- supplementary panel: conductance-floor audit and closed-form gain.

If those analyses are not completed, move Figure 5 and Result 3 to an explicitly exploratory appendix.

---

### MAJ-22 — Source provenance and article-year terminology need tightening

The source description should distinguish what is measured, derived, fitted, and reconstructed:

- Schmieder et al. collected ten fractions but analyzed six selected fractions for the concentration fits; the source reports repeated extraction runs and derives cup masses by integrating each run’s fitted extraction kinetic.
- The RSM used set grind and achieved flow/temperature, with backward elimination.
- The published Waszkiewicz article is a **2026** Physics of Fluids paper, although an internal repository or dataset key may retain `waszkiewicz2025` from preprint/data provenance.
- The Foster panel is a reproduced model curve, not necessarily digitized experimental data.
- The Mo swelling calculation uses a transferred representative powder parameterization.

**Required action:** Add a data-provenance table with fields:

| Dataset key | Published source/year | Raw measured quantities | Derived quantities used here | Repository transformations | License | Role |
|---|---|---|---|---|---|---|

Use the published article year in the reference list and explain internal keys once in the reproducibility appendix.

---

### MAJ-23 — The figure workflow is not yet single-source or fully auditable

The repository’s figure documentation says that manuscript values are pulled from functions rather than hand-entered. The implementation does not fully meet that standard:

- Figure 2 is hard-coded.
- Figure 1 reimplements the RSM fit inside plotting code rather than consuming `schmieder_rsm_refit` outputs.
- Figure annotations include narrative verdicts hard-coded in the plotting layer.
- `render_all` directly recomputes analyses and writes raster PNGs, with no versioned results bundle or provenance stamp ([`figures.py` lines 349–355](https://github.com/trbrewer/puckworks/blob/8ca073fdda68a2032d321abe5401eb5d531d6e88/puckworks/figures.py#L349-L355)).
- Slow figure functions are reportedly outside the main CI path.

A robust paper build should separate:

1. data ingestion and validation;
2. analysis and machine-readable results;
3. figure/table rendering;
4. manuscript assembly.

**Required action:**

- Create `python -m puckworks.paper_b.build --release <tag>` or equivalent.
- Write a `results.json`/Parquet bundle containing raw and display-rounded values, parameter provenance, seeds, data hashes, commit SHA, package versions, and environment.
- Make all plots consume that bundle only.
- Add tests that manuscript headline values equal bundle fields.
- Add a fast CI smoke build and a scheduled/release full build.
- Export SVG/PDF plus figure source data.
- Archive a tagged release with a DOI and environment lock file.

---

### MAJ-24 — Discussion should distinguish rejection of a model instance from rejection of a mechanism class

Throughout the draft, conclusions move among four levels:

1. an implementation fails to produce a target;
2. a registered parameterization fails;
3. a mechanism under one boundary condition has the wrong sign;
4. a broad physical mechanism is absent or excluded.

Only levels 1–3 are supported here, and often only levels 1–2. The Discussion should use a formal evidence vocabulary:

| Evidence label | Meaning |
|---|---|
| Numerical verification | Code reproduces a known equation/curve or internal identity |
| Model capacity | At least one registered parameterization can generate the qualitative feature |
| Target-conditioned fit | Parameters were estimated using the same target being scored |
| Same-campaign transfer | Parameters came from another observable/condition in the same campaign |
| Held-out condition prediction | The scored condition was excluded from the relevant fit, but campaign dependencies remain |
| Independent transfer | Machine/coffee/campaign and target data were not used in calibration |
| Conditional incompatibility | A model instance or mechanism under stated assumptions cannot match a feature |
| Mechanism identification | Competing plausible mechanisms are discriminated under a justified uncertainty model |

Most Paper B results fall between model capacity and same-campaign/held-out-condition evidence. None establishes unique mechanism identification. Making this table part of Methods would transform the manuscript’s strongest conceptual idea into a reproducible framework.

---

## 6. Figure-by-figure review

### Figure 1 — TDS-EY target and static-channeling capacity

**What works**

- The title correctly says “model capacity, not identification.”
- The panel acknowledges that the channeling x axis is non-portable.
- The RSM vertex interval and adjusted R² are visible.

**Required revisions**

1. Show all 3/6/3 extraction-run values, not means alone.
2. Define error bars in the caption and use a standard sample summary.
3. Replace “raw: monotone” with “observed cell means increase; no observed middle-cell maximum.”
4. Refit using achieved flow and temperature.
5. Show curve uncertainty conditional on the model.
6. Do not duplicate the fit in the plotting function.
7. Consider separating the two grinder coordinate systems into distinct figures.
8. Add the achieved mean flow, temperature, and pressure for each dial beneath the x axis or in a companion panel.
9. Make clear that the RSM curve is a whole-design model, while the points are three selected settings.
10. State that the vertex interval is conditional on the quadratic model and source term selection.

**Suggested caption core**

> “Run-level TDS-derived extraction yield at three nominal central settings in Schmieder et al.; points are separate extraction runs reported by the source, and bars show [specified summary]. The inferential independence assumption is stated in Methods. The curve is our achieved-flow/achieved-temperature quadratic refit of the full design, with a model-conditional uncertainty band. The right panel is a separate Cameron-coordinate model-capacity calculation and is not a calibrated cross-grinder prediction.”

---

### Figure 2 — Mechanism evidence matrix

**What works**

- The intended goal—preventing a winner scoreboard—is appropriate.
- Including unimplemented incomplete wetting is scientifically honest.

**Required revisions**

1. Replace hand-coded cells with a committed evidence table.
2. Define every evidence dimension before displaying it.
3. Distinguish implementation status from scientific evidence.
4. Distinguish target-fitted, same-campaign, held-out, and independent parameter constraints.
5. Change static channeling “observable matched” from unqualified yes to a qualified cross-dataset/proxy status.
6. Replace generic evidence-strength “partial” cells with specific reasons.
7. Add the decisive missing measurement for each mechanism.
8. Use accessible symbols/text and a colorblind-safe palette.
9. Provide source references in the caption or supplemental table.
10. Add an automated consistency test between the evidence table and registry/analysis outputs.

A conventional table may be more informative than a heatmap if the evidence categories cannot be made truly ordinal.

---

### Figure 3 — Machine null, 9-bar ladder, transfer, and sign constraint

**What works**

- It places a machine-only null before bed-mechanism interpretation.
- It shows that a flexible temporal curve can match the trace as well as the physical trajectory.
- It visualizes pressure-dependent model error rather than only an aggregate mean.

**Required revisions**

1. Split this overloaded four-panel figure into at least two figures: (i) 9-bar ladder/residuals; (ii) cross-pressure transfer/sign constraint.
2. Label the Foster curve as a reproduced source model curve.
3. Replace `0p` with full parameter provenance.
4. Mark the cubic as in-sample unless blocked validation is added.
5. Add residual and ACF panels.
6. Add uncertainty on RMSE differences using whole-block/trace resampling.
7. Remove “swelling refuted by sign”; use conditional sign language.
8. State that the Mo magnitude is a cross-rig representative parameterization.
9. Visually identify the 15–95 s evaluation window.
10. Distinguish 10-pressure off-9-bar summaries from 11-pressure LOPO summaries.
11. Do not shade or label post-hoc pressure regimes as though they were confirmed physical regimes.
12. Show calibration provenance in the legend or a companion table.

---

### Figure 4 — Shared-porosity composition diagnostic

**What works**

- It exposes a failed composition rather than tuning it away.
- It compares against the same-window best constant.

**Required revisions**

1. Use a neutral title.
2. Shade 15–95 s.
3. Add residuals.
4. Show initial-condition and swelling-parameter sensitivity.
5. Explain that extraction-only equivalence is built into the implementation.
6. Separate the auxiliary Kozeny–Carman comparison from the operative closure.
7. Remove “OVER-closes,” “FAILED,” and “worse than a flat line” from the artwork.
8. State which uncertainty sources are omitted.

---

### Figure 5 — Exploratory finite-time concentration

**What works**

- It no longer calls the calculation a stability theorem.
- It discloses floor sensitivity of the closed-form gain.
- It compares flow and pressure control and the effect of homogenization.

**Required revisions**

1. Show time trajectories, not only endpoints.
2. Plot maximum share alongside `N_eff`.
3. Show total flow/pressure and conservation diagnostics.
4. Add convergence in `N`, timestep/substeps, and solver.
5. Add start-state, pressure, grind, closure, and horizon sensitivity.
6. Use multiple finite-network realizations.
7. Replace the dimensionless homogenization proxy with a physical lateral exchange or keep it explicitly numerical.
8. Move the singular closed-form gain audit to the supplement.
9. Remove the word “robust” except for the narrow tested floor invariance.
10. Keep the entire result clearly labeled exploratory unless a physical stability/validation program is completed.

---

## 7. Claim-by-claim wording revisions

| Current or implied claim | Problem | Recommended replacement |
|---|---|---|
| “the raw cells rule out a middle-dial maximum” | Stronger than a three-setting, achieved-condition-confounded comparison supports | “The observed central-setting cell means contain no middle-dial maximum; the middle mean is lower than the 2.0 mean in this campaign.” |
| “bootstrap CI confirms the interior maximum is real” | Conditional on quadratic form, term selection, and bootstrap assumptions | “Under the specified quadratic refit, the estimated vertex is interior and remains inside the tested dial range in the conditional bootstrap.” |
| “raw: monotone” | Implies an established monotone response | “Observed means increase across the three selected nominal settings.” |
| “static channeling is observable-matched” | Calibration and evaluation use different datasets, machines, grinders, and target constructions | “Static channeling is evaluated as cross-dataset qualitative capacity using an EY-related target; the grind coordinate is non-portable.” |
| “zero-parameter poroelastic Φ(t)” | Contains campaign/donor-estimated quantities | “No additional coefficient is fitted directly to the scored Q(t) trace; equilibrium and TDS-trajectory parameters are imported from the same campaign.” |
| “time variation is required” | True only within the tested window and candidate set | “Within the 15–95 s window and tested model set, all constant baselines have substantially larger reconstruction error than time-varying alternatives.” |
| “swelling/fines refuted by sign” | Overgeneralizes an isolated fixed-pressure resistance branch | “The tested resistance-only branches cannot by themselves generate the observed rising contribution under the imposed fixed-pressure model.” |
| “dissolution opening is the only surviving mechanism” | Candidate set is incomplete and mechanisms may coexist | “Among the implemented isolated branches, dissolution-linked opening has the required net sign; other coupled or unimplemented mechanisms remain unresolved.” |
| “regime structure is a property of the physics” | LOPO only stabilizes a two-parameter equilibrium fit | “The residual pressure pattern is not caused by any single equilibrium calibration point, but its physical origin remains unresolved.” |
| “within-rig held-out prediction” | Sigmoid and campaign assumptions remain shared | “Within-campaign leave-one-pressure-out evaluation of the equilibrium calibration, with the 9-bar solids trajectory held fixed.” |
| “extraction-only degeneracy” | Exact equality is designed into code | “Extraction-only implementation identity/unit test.” |
| “14× rise requires near-choke closure” | Conditional on adopted mapping and tested closures | “Within the adopted Φ(t)-to-flow mapping, the near-choke closure is the only tested relation that reproduces the rise magnitude.” |
| “numerical concentration is robust” | Only a conductance-floor sweep is shown | “The final concentration endpoint is insensitive to the tested conductance-floor range in this fixed configuration.” |
| “Foster trace reconstructed” | Panel appears to be a reproduced source model curve | “Numerical reproduction of the published machine-model curve demonstrates that dip-and-recovery is available without evolving bed resistance in that model.” |

---

## 8. Required analyses and suggested acceptance criteria

### 8.1 Schmieder selected-cell and RSM analysis

**Minimum analysis package**

1. Plot all run-level TDS/BR 1/2 central-setting outcomes.
2. Provide a data dictionary linking each row to condition setting, run, roast batch if available, achieved flow, achieved temperature, pressure, and derived mass/EY.
3. Fit the source-specified achieved-covariate RSM with centered/scaled predictors.
4. Verify the retained term set against the full-precision Origin object, or explicitly classify the result as a new refit.
5. Provide model residuals, leverage, influence, lack-of-fit if estimable, and prediction bands.
6. Use a fixed-design-appropriate bootstrap and report valid-vertex frequency.
7. Compare target- and achieved-predictor specifications as sensitivity, not as interchangeable models.
8. Evaluate whether pressure should enter the inferential model or be treated as a mediator/confound under flow control; explain the causal target before adjustment.

**Acceptance criteria**

- Every source replication statement matches the source Methods.
- No result is described as causal dial-only evidence without a causal/experimental justification.
- The vertex estimate and interval are generated once, stored in the results bundle, and reused by text and figure.
- `κ₂(X)` and `κ₂(XᵀX)` are correctly labeled.
- The conclusion remains model-conditional even if the interval is narrow.

### 8.2 Static heterogeneity/channeling analysis

**Minimum analysis package**

1. Publish calibration points and how each σ value was inferred.
2. Fit closure uncertainty, not only a point closure.
3. Report quadrature-order and response-grid convergence.
4. Report weighted mean permeability multiplier after all numerical clipping/interpolation.
5. Propagate closure uncertainty to peak prominence and location.
6. Compare against at least one alternative heterogeneity distribution or closure family.
7. Keep the Cameron and Schmieder grinder coordinates separate.
8. Add incomplete wetting as a conceptual comparator even if parameter-blocked, with the measurement that would distinguish it.

**Acceptance criteria**

- The result is called model capacity, not external validation.
- Peak prevalence is reported over a predefined sensitivity domain with no probability interpretation.
- Small prominence is compared with run-level variability and measurement resolution without an unsupported “noise floor.”

### 8.3 Result 2 temporal ladder

**Minimum analysis package**

1. Freeze the evaluation window before model comparison or show window sensitivity.
2. Add residual and ACF plots.
3. Treat the cubic as an in-sample flexibility bound or evaluate it under blocked validation.
4. Use whole-block/whole-trace uncertainty.
5. Report parameter provenance rather than one-dimensional parameter counts.
6. Include time-alignment, smoothing, and decimation sensitivity.
7. Compare errors with scale-normalized metrics where pressure changes the flow magnitude.
8. Make the machine-only null’s evidence type explicit.

**Acceptance criteria**

- No claim of unique mechanism identification remains.
- “Time variation” is scoped to the specified interval, model set, and error metric.
- RMSE ranking is accompanied by structured-residual diagnostics.

### 8.4 Cross-pressure analysis

**Minimum analysis package**

1. Fix the rounding bug.
2. Tabulate all pressures, raw RMSEs, calibration status, and trace lengths/weights.
3. State whether aggregation weights pressures equally or weights time samples.
4. Report both absolute and normalized error.
5. Separate 9-bar calibration pressure from off-9-bar evaluation.
6. Keep 10-pressure and 11-pressure summaries distinct.
7. Perturb/refit the 9-bar TDS sigmoid and quantify impact.
8. Avoid post-hoc regime claims or provide genuine pre-specification.

**Acceptance criteria**

- LOPO conclusion is limited to equilibrium-calibration stability.
- No statement attributes residual patterns uniquely to physics.
- All summary numbers are computed from unrounded values.

### 8.5 Sign-constraint analysis

**Minimum analysis package**

1. State governing equations and boundary conditions for each branch.
2. Prove or numerically verify monotonicity under those exact assumptions.
3. Enumerate coupling terms that can reverse the net sign.
4. Distinguish mechanism presence from mechanism dominance.
5. Treat transferred magnitudes as sensitivity examples.

**Acceptance criteria**

- The paper says “cannot by itself under the imposed model,” not “mechanism refuted.”
- The theorem/lemma assumptions are mapped explicitly to the experiment.

### 8.6 N-tube exploratory model

**Minimum analysis package for main-text retention**

1. Dimensionally defined equations and boundary conditions.
2. Physical lateral exchange.
3. `N`, timestep, solver, and horizon convergence.
4. Multiple initial realizations and start states.
5. Pressure, grind, closure, and flow-path sensitivity.
6. Ablation of each positive-feedback link.
7. `N_eff(t)`, maximum share, total flow/pressure, and conservation plots.
8. A formal stability/finite-time amplification analysis if “instability” is discussed.
9. Comparison with at least one independent spatial observation or clearly stated absence thereof.

**Acceptance criteria**

- Without spatial data, the result remains a model-generated hypothesis.
- No general robustness claim is based on one floor sweep.
- Flow-control and pressure-control comparisons use a consistent coupled machine/bed formulation.

---

## 9. Suggested revised manuscript architecture

### Proposed title

**Limits of mechanism discrimination from integrated espresso measurements: matched observables, null models, and exploratory streamtube dynamics**

### Proposed section flow

1. **Introduction**
   - Why integrated observations are mechanistically ambiguous.
   - Difference among capacity, fit, transfer, incompatibility, and identification.
   - Three pre-specified questions.

2. **Data and observation contracts**
   - Schmieder repeated extraction design and derived cup responses.
   - Waszkiewicz pressure traces, solids trajectory, and equilibrium curve.
   - Cameron and Foster source roles.
   - Units, normalization, and experimental units.

3. **Models and evidence provenance**
   - Static heterogeneous streamtubes.
   - Machine-only null and κ(t) branches.
   - Shared-porosity synthesis.
   - Exploratory N-tube network.
   - Calibration/evaluation matrix.

4. **Statistical and numerical methods**
   - RSM specification and fixed-design bootstrap.
   - RMSE/MAE/residual diagnostics.
   - Blocked validation for time traces.
   - Cross-pressure LOPO.
   - Sensitivity and convergence.

5. **Results**
   - 5.1 Observed dial response and conditional RSM curvature.
   - 5.2 Static heterogeneity: capacity but weak cross-dataset discrimination.
   - 5.3 Temporal ladder: time variation beats constants; mechanism remains unresolved.
   - 5.4 Cross-pressure calibration stability and structured residuals.
   - 5.5 Conditional sign constraints and composition failure.
   - 5.6 Exploratory network counterexample (or Supplement).

6. **Discussion**
   - What was rejected, what remains viable, and at what evidence level.
   - Why integrated measurements are insufficient.
   - Concrete discriminating experiments.

7. **Limitations**
   - campaign specificity;
   - transferred parameters;
   - incomplete candidate set;
   - source-data derivatives;
   - no spatial validation.

8. **Data and code availability**

9. **References**

### Abstract structure

The abstract should avoid detailed CI and parameter-count rhetoric until the statistical contracts are repaired. A safer structure is:

1. problem: integrated observables can be mechanistically non-unique;
2. method: matched observation contracts and null-first comparison;
3. Result 1: selected cell means have no observed middle maximum; a quadratic refit has conditional interior curvature; static heterogeneity has qualitative capacity;
4. Result 2: time-varying alternatives beat constants on one trace, but a flexible null and structured residuals prevent mechanism identification; LOPO stabilizes equilibrium calibration only;
5. Result 3: an exploratory uncoupled network can concentrate flow in one constructed configuration;
6. conclusion: spatial/bed-state measurements are needed.

---

## 10. Reproducibility and release checklist

Before submission, the Paper B release should satisfy all items below.

### Data and provenance

- [ ] Every data file has source citation, license, retrieval date, checksum, units, and transformation script.
- [ ] Raw, digitized, derived, fitted, and simulated quantities are labeled distinctly.
- [ ] The Schmieder table documents how each source replicate and derived cup mass was represented.
- [ ] The Waszkiewicz dataset key is distinguished from the 2026 publication year.
- [ ] Every parameter has a provenance category: target-fit, same-campaign other-observable fit, held-out fit, external literature, or assumed.

### Analysis

- [ ] RSM uses achieved predictors and verified terms.
- [ ] Fixed-design bootstrap method and model-selection treatment are documented.
- [ ] Cross-pressure summaries use raw, unrounded values.
- [ ] Time-series validation respects dependence.
- [ ] Residual diagnostics are archived.
- [ ] Sensitivity/convergence results are machine-readable.
- [ ] Random seeds and deterministic solver settings are recorded.

### Figures and tables

- [ ] Figures are generated from a single results bundle.
- [ ] No evidence cell or headline number is manually entered in plotting code.
- [ ] Every plotted series has source data exported.
- [ ] Evaluation windows are shown.
- [ ] Error bars and uncertainty bands are defined.
- [ ] Color is not the only semantic channel.
- [ ] SVG/PDF versions are generated.
- [ ] Captions state fit/evaluation status and claim limits.

### Software release

- [ ] One command builds the result bundle, figures, tables, and manuscript.
- [ ] Commit SHA and dirty-tree status are embedded.
- [ ] Python and dependency versions are locked.
- [ ] Fast smoke tests run in CI; full slow analyses run for release.
- [ ] Headline values are tested against the results bundle.
- [ ] A tagged release and archival DOI are created.
- [ ] The release contains a computational README with expected runtime/hardware and deterministic outputs.

---

## 11. Minor and editorial comments

1. Define `κ(t)`, `Φ(t)`, `RC-3b`, `N_eff`, and every grind symbol at first use; repository shorthand should not be assumed knowledge.
2. Use one notation for pressure and one for mass flow throughout. Distinguish volumetric flow from mass flow explicitly.
3. The phrase “static pressure-dependence is observationally identical to a constant” is true only at a single fixed pressure and specified observation window; retain that qualifier each time.
4. Replace “weak” RSM with quantitative fit diagnostics and prediction uncertainty rather than an adjective alone.
5. Avoid “noise floor” unless measurement-error variance and minimum detectable effect are formally estimated.
6. Distinguish a confidence interval for a conditional mean/contrast from a prediction interval for a new extraction run.
7. Do not use “external” for Schmieder evaluation if the closure calibration and target lack a portable grinder map; use “different dataset” and specify transfer distance.
8. Use “TDS-derived extraction yield” consistently and state the dose/normalization equation.
9. Explain whether density is assumed when converting volumetric to mass flow anywhere in the pipeline.
10. Put all evaluation-window choices in Methods and show sensitivity to plausible alternatives.
11. Report units in every table header, not only surrounding prose.
12. The term “long-run constant” should state the exact calibration interval and whether that interval overlaps the evaluation window.
13. “Best constant” should be identified as the least-squares in-window mean and therefore an optimistically fitted null.
14. The flexible cubic should be checked for physical pathologies outside the fit window; avoid extrapolating it.
15. If Durbin–Watson is used, explain its assumptions and supplement it with ACF/residual plots rather than using one scalar as the full diagnosis.
16. In pressure aggregation, state whether all pressures receive equal weight regardless of trace length or variance.
17. Use “same-campaign” consistently rather than alternating among conditional transfer, held-out, and out-of-sample without hierarchy.
18. Replace “only tested mechanism with the correct sign” with “only implemented isolated branch in this comparison with the required net sign.”
19. Avoid capitalized rhetorical labels inside figures.
20. State explicitly that the N-tube paths are simulated latent states and not measured channels.
21. Separate the companion Paper A result from the Paper B argument unless a formal joint framework is presented.
22. A glossary of evidence labels and repository terms would improve accessibility.
23. Confirm all DOIs and article years in the final bibliography, especially preprint-to-publication transitions.
24. Add author contributions and conflicts/funding statements appropriate to the target journal.

---

## 12. Supporting references

The following references support the methodological and source-specific comments in this review. Primary sources should be preferred in the manuscript.

1. **Schmieder, B. K. L., Pannusch, V. B., Vannieuwenhuyse, L., Briesen, H., & Minceva, M. (2023).** Influence of Flow Rate, Particle Size, and Temperature on Espresso Extraction Kinetics. *Foods, 12*(15), 2871. [https://doi.org/10.3390/foods12152871](https://doi.org/10.3390/foods12152871)  
   Relevant to the 15-setting face-centered design, three repetitions per setting/six at the center, fraction collection, individually fitted extraction runs, achieved flow/temperature in the RSM, backward elimination, and the source’s warning that quantitative RSM interpretation should be cautious.

2. **Waszkiewicz, R., Myck, F., Białas, Ł., Puciata-Mroczynska, M., Dzikowski, M., Szymczak, P., & Lisicki, M. (2026).** Under pressure: Poroelastic regulation of flow in espresso brewing. *Physics of Fluids, 38*, 063113. [https://doi.org/10.1063/5.0319611](https://doi.org/10.1063/5.0319611)  
   Primary source for the pressure–flow relation, time-dependent behavior, and dissolution-linked poroelastic interpretation.

3. **Cameron, M. I., Morisco, D., Hofstetter, D., Uman, E., Wilkinson, J. P. T., Kennedy, Z. C., Fontenot, S. A., Lee, W. T., Hendon, C. H., & Foster, J. M. (2020).** Systematically Improving Espresso: Insights from Mathematical Modeling and Experiment. *Matter, 2*, 631–648. [https://doi.org/10.1016/j.matt.2019.12.019](https://doi.org/10.1016/j.matt.2019.12.019)  
   Source for the homogeneous extraction lineage and the observed fine-grind deviation used in the static-heterogeneity calibration chain.

4. **Foster, J. M., Lee, W. T., Moroney, K., Prjamkov, D., Salamon, M., Smith, A., Petrassem-de-Sousa, J., & Vynnycky, M. (2025).** Dynamics of liquid infiltration into an espresso bed using time-resolved micro-computed tomography: Insights from experiment and modeling. *Physics of Fluids, 37*, 013383. [https://doi.org/10.1063/5.0245167](https://doi.org/10.1063/5.0245167)  
   Source for the machine/infiltration model curve used as a null-shape demonstration.

5. **Lee, W. T., Smith, A., & Arshad, A. (2023).** Uneven extraction in coffee brewing. *Physics of Fluids, 35*, 054110. [https://doi.org/10.1063/5.0138998](https://doi.org/10.1063/5.0138998)  
   Relevant competing mechanism for flow–extraction feedback and fine-grind response.

6. **Mo, C., Johnston, R., Navarini, L., & Ellero, M. (2022).** Modeling swelling effects during coffee extraction with smoothed particle hydrodynamics. *Physics of Fluids, 34*, 043104. [https://doi.org/10.1063/5.0086897](https://doi.org/10.1063/5.0086897)  
   Primary swelling-model source; important for preserving donor boundary conditions and parameter scope.

7. **Mo, C., Johnston, R., Navarini, L., & Ellero, M. (2021).** Modeling the effect of flow-induced mechanical erosion during coffee filtration. *Physics of Fluids, 33*, 093101. [https://doi.org/10.1063/5.0059707](https://doi.org/10.1063/5.0059707)  
   Relevant to fines/erosion mechanisms and the need not to reduce all particle migration to a single resistance-only branch without qualification.

8. **Moroney, K. M., O’Connell, K., Meikle-Janney, P., O’Brien, S. B. G., Walker, G. M., & Lee, W. T. (2019).** Analysing extraction uniformity from porous coffee beds using mathematical modelling and computational fluid dynamics approaches. *PLOS ONE, 14*, e0219906. [https://doi.org/10.1371/journal.pone.0219906](https://doi.org/10.1371/journal.pone.0219906)  
   Relevant background on extraction nonuniformity and spatial observability.

9. **Freedman, D. A. (1981).** Bootstrapping Regression Models. *The Annals of Statistics, 9*, 1218–1228. [https://doi.org/10.1214/aos/1176345638](https://doi.org/10.1214/aos/1176345638)  
   Supports the need to define whether a regression bootstrap targets fixed-design or random-design uncertainty.

10. **Hurlbert, S. H. (1984).** Pseudoreplication and the Design of Ecological Field Experiments. *Ecological Monographs, 54*, 187–211. [https://doi.org/10.2307/1942661](https://doi.org/10.2307/1942661)  
    General reference for aligning treatment, replication, independence, and inferential unit. It should be applied carefully rather than used to relabel independent extraction repetitions without evidence.

11. **Roberts, D. R., Bahn, V., Ciuti, S., et al. (2017).** Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography, 40*, 913–929. [https://doi.org/10.1111/ecog.02881](https://doi.org/10.1111/ecog.02881)  
    Supports blocked/structured validation when observations are temporally or hierarchically dependent.

12. **Crameri, F., Shephard, G. E., & Heron, P. J. (2020).** The misuse of colour in science communication. *Nature Communications, 11*, 5444. [https://doi.org/10.1038/s41467-020-19160-7](https://doi.org/10.1038/s41467-020-19160-7)  
    Supports accessible, perceptually faithful figure design and avoiding color-only evidence encoding.

---

## 13. Bottom-line recommendation

The manuscript should be revised around a narrower and stronger conclusion:

> **Matched integrated observables can establish model capacity, expose conditional incompatibilities, and test limited same-campaign transfer, but the present datasets do not uniquely identify espresso bed mechanisms.**

That conclusion is supported by the best parts of the current work. To make it publishable, the revision must correct the source-design description and RSM predictor contract, make uncertainty and complexity accounting explicit, replace hard-coded evidence graphics, surface structured residuals, narrow the sign-test and LOPO claims, and either substantially validate or clearly demote the N-tube result. A complete, frozen, single-source paper build is also required.

With those changes, Paper B could become a useful example of rigorous mechanism-discrimination practice: it would show not merely which models can fit espresso data, but exactly what each dataset and observation operator can—and cannot—tell us.

# Detailed review of the updated `PAPER_B_DRAFT.md`

## Review basis and scope

This review evaluates the updated manuscript against a pinned repository revision so that every comment remains reproducible even if `main` changes later.

- **Draft reviewed:** [`docs/PAPER_B_DRAFT.md`](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/docs/PAPER_B_DRAFT.md)
- **Pinned repository revision:** [`135f5d277ea004f8e05532f16bf8a1ba67889d78`](https://github.com/trbrewer/puckworks/commit/135f5d277ea004f8e05532f16bf8a1ba67889d78)
- **Major-revision rewrite:** [`36e1690f265d5c9fe71e4a53c8a71db41a349a2a`](https://github.com/trbrewer/puckworks/commit/36e1690f265d5c9fe71e4a53c8a71db41a349a2a)
- **Principal implementation files inspected:**
  - [`puckworks/harness.py`](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/puckworks/harness.py)
  - [`puckworks/figures.py`](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/puckworks/figures.py)
  - [`puckworks/models/brewer2026/streamtube.py`](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/puckworks/models/brewer2026/streamtube.py)
  - [`puckworks/models/waszkiewicz2025/poroelastic.py`](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/puckworks/models/waszkiewicz2025/poroelastic.py)
  - [`puckworks/models/brewer2026/coupled_kappa_t.py`](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/puckworks/models/brewer2026/coupled_kappa_t.py)
- **Principal committed data inspected:**
  - [`schmieder2023/cup_masses.csv`](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/puckworks/data/schmieder2023/cup_masses.csv)
  - [`schmieder2023/rsm_coefficients.csv`](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/puckworks/data/schmieder2023/rsm_coefficients.csv)
  - [`waszkiewicz2025/traces_time_dependent.csv`](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/puckworks/data/waszkiewicz2025/traces_time_dependent.csv)
  - [`waszkiewicz2025/static_calibration.csv`](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/puckworks/data/waszkiewicz2025/static_calibration.csv)
  - [`waszkiewicz2025/solids_calibration.csv`](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/puckworks/data/waszkiewicz2025/solids_calibration.csv)

I independently recalculated the central Schmieder TDS-derived extraction-yield contrasts, refitted the retained-term TDS response surface under several reasonable conventions, and reconstructed the 9-bar Waszkiewicz baseline and dynamic RMSE values from the committed CSVs. I also reviewed the code paths used to generate all five figures. I did not treat the repository's passing regression tests as scientific validation, and I did not rerun the complete test suite because the execution environment did not contain a complete clone of every dependency. The conclusions below are based on pinned source inspection and independent calculations from the committed data.

---

## Recommendation

**Major revision, but substantially improved relative to the previous draft.**

The rewrite responds seriously to the earlier review. It removes the erroneous claim that the Schmieder response surface overpredicts cup mass by about 1.7×, abandons the undefined “noise floor” language, distinguishes raw cells from fitted response-surface curvature, narrows the cross-pressure claim, and downgrades the N-tube result from a purported stability theorem to an exploratory concentration calculation. Those are material scientific improvements rather than cosmetic edits.

The manuscript's strongest prospective contribution is now clear: **a matched-observable, null-first framework for deciding what integrated espresso measurements can and cannot discriminate**. That contribution is plausible and useful. The paper is not yet submission-ready, however, because several remaining statements are stronger than the code and statistics support, one key Result-2 number is evaluated over a different time window from the manuscript's stated window, and the new claim that the N-tube concentration is “floor-independent” has not actually been tested in the numerical N-tube calculation.

### Status of the previous review's main findings

| Previous issue | Status in the updated draft | Current assessment |
|---|---|---|
| Rounded RSM coefficients were mistaken for full-precision parameters | **Conceptually corrected** | The 1.7× criticism is gone, but the repository refit still lacks a documented statistical specification, covariance, diagnostics, and internally consistent figure annotations. |
| Averaged within-cell SD was called a “noise floor” | **Mostly corrected** | A Welch contrast is now reported, but one contrast does not establish that the whole three-level response is “statistically monotone,” and the experimental unit/run structure remains unaddressed. |
| “40% of the grid” was presented as robustness | **Improved** | The draft now says 10 of 25 over a chosen rectangle and denies a probabilistic interpretation. “Pre-specified” is unsupported, and the reported median prominence is conditional on cases that already peak. |
| Jensen/concavity premise was not demonstrated | **Partially addressed** | A numerical curvature and clipping audit was added. The audit is useful but should be replaced or supplemented by a direct, converged Jensen-gap calculation. |
| Cross-pressure analysis was called independent out-of-sample validation | **Corrected in prose** | The manuscript now calls it within-campaign conditional generalization. The harness and Figure 3 still use “OOS,” “wins,” and “winner” language. |
| N-tube result was called a linear instability/stability theorem | **Corrected in prose** | The theorem language is removed. A new unsupported statement—numerical concentration is floor-independent—now occupies the critical logical step. |
| Manuscript lacked conventional Methods, references, and reproducibility details | **Unresolved and explicitly acknowledged** | These remain submission-blocking, not optional future work. |

---

## Principal strengths of the revision

### 1. The three-object distinction greatly improves Result 1

The table separating the Cameron fine-grind deviation, the Schmieder raw TDS response, and the Schmieder fitted RSM curvature is one of the rewrite's best changes ([Draft lines 60–74](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/docs/PAPER_B_DRAFT.md#L60-L74)). It prevents the paper from treating a grinder-dial response, a particle-size response, and a fitted surface as interchangeable. The explicit warning that dial 1.7 is the finest by Sauter diameter, despite lying between 1.4 and 2.0 numerically, is essential.

### 2. The evidence-tier and verb discipline is scientifically healthy

The draft now distinguishes “reconstructs,” “can generate,” and “exhibits in the tested configuration” from “shows,” “identifies,” or “proves.” That is a strong editorial discipline, and the statement that a regression gate demonstrates software reproducibility rather than scientific validation should remain in the eventual Methods or reproducibility section ([Draft lines 83–102](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/docs/PAPER_B_DRAFT.md#L83-L102)).

### 3. Negative and conditional results are now treated as results

The revision is much more credible because it allows the raw Schmieder cells to disagree with the fitted RSM feature, allows the shared-porosity composition to fail, and states that no tested temporal branch dominates at every pressure. This supports a methodological paper about discrimination limits rather than forcing every analysis into a channeling-identification narrative.

### 4. The observability thesis now unifies the paper

The Discussion's central idea—that whole-cup and whole-bed observables can erase the structure needed to distinguish mechanisms—is coherent across the three analyses. It can support a strong paper if scoped to **the tested datasets and model classes**, rather than generalized to all integrated observables in espresso.

---

# Submission-blocking findings

## 1. Result 1 rules out a middle-dial maximum, but does not establish a fully “statistically monotone” three-level response

### What the committed cells show

At the nominal central target condition (TDS, brew ratio 1/2, target flow 2 mL/s, target temperature 89 °C), the committed data give:

| Dial | n | Mean EY (%) | Sample SD (EY-points) | Mean achieved flow (mL/s) | Mean achieved temperature (°C) | Mean maximum pressure (bar) |
|---:|---:|---:|---:|---:|---:|---:|
| 1.4 | 3 | 18.267 | 0.552 | 1.921 | 88.495 | 3.907 |
| 1.7 | 6 | 19.381 | 0.159 | 1.901 | 88.258 | 3.408 |
| 2.0 | 3 | 19.622 | 0.071 | 1.996 | 88.618 | 3.333 |

The means are numerically ordered 18.3 < 19.4 < 19.6. The updated manuscript correctly reports the middle-minus-2.0 contrast:

| Contrast | Difference (EY-points) | Welch 95% CI | Two-sided p |
|---|---:|---:|---:|
| 1.4 − 1.7 | −1.114 | [−2.414, +0.187] | 0.068 |
| 1.7 − 2.0 | −0.241 | [−0.422, −0.060] | 0.016 |
| 1.4 − 2.0 | −1.355 | [−2.696, −0.014] | 0.049 |

Because dial 1.7 is significantly below dial 2.0 under that Welch comparison, these raw cells do not support an interior maximum at 1.7. That is a defensible and useful negative result.

The stronger sentence—“the raw response is statistically monotone” ([Draft lines 112–116](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/docs/PAPER_B_DRAFT.md#L112-L116))—is not established by the reported test. The 1.4-versus-1.7 interval includes zero. A curvature contrast,

\[
\bar y_{1.7}-\tfrac12(\bar y_{1.4}+\bar y_{2.0}),
\]

is +0.436 EY-points with an approximate 95% interval [−0.143, +1.016]. This is compatible with a saturating, concave rise, but it is not evidence that every adjacent increase is statistically resolved.

### The nominal “fixed central condition” is not an achieved-condition match

The three dial cells share target flow and temperature, but the achieved flow, temperature, and pressure differ. Dial 1.7 and dial 2.0 differ by about 0.095 mL/s in mean achieved flow; dial 1.4 operates at appreciably higher maximum pressure. The source design also stores the three dial settings as different experiment conditions: dial 1.4 is an axis-point experiment, dial 1.7 is the repeated center-point experiment, and dial 2.0 is another axis-point experiment. Treating all 12 replicate rows as exchangeable observations in a Welch test therefore needs a stated experimental-unit argument. At minimum, run/condition effects and achieved covariates should be discussed.

This does not reverse the descriptive ordering. It does limit a causal interpretation such as “dial alone causes a monotone response.” The paper already recognizes pressure confounding in the Introduction; the empirical analysis should carry that recognition into the statistical language.

### Required change

Replace “statistically monotone” with a statement that matches the actual evidence, for example:

> At the nominal central settings, the cell means increase across dial (18.27, 19.38, and 19.62% EY). Dial 1.7 is 0.24 EY-points below dial 2.0 (Welch 95% CI [−0.42, −0.06]), so the raw cells do not support an interior maximum at dial 1.7. Achieved flow and pressure differ among these experiment conditions, so this is a conditional response comparison rather than a dial-only causal effect.

For the final manuscript, either justify the replicate as the inferential unit or use a design-aware model based on experiment-level means/blocks and achieved conditions. Plot the individual observations, not only means and population SD bars.

---

## 2. Result 2 contains a reproducibility mismatch between the stated 15–95 s window and the implemented 15–100 s calculation

### What the code actually evaluates

The manuscript reports RMSE 0.603 g/s for the flat/static baselines and 0.113 g/s for the empirical time-varying porosity branch “within the 15–95 s evaluation window” ([Draft lines 175–183](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/docs/PAPER_B_DRAFT.md#L175-L183)). The supporting function instead selects 15–115 s ([`harness.py` lines 106–130](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/puckworks/harness.py#L106-L130)). The committed 9-bar trace ends at 100 s, so the effective evaluation window is 15–100 s.

The baseline is also described in code as a “long-run” mean, but it is calculated as `mean(q[t >= 100])`. Because the trace has one sample at exactly 100 s and no later samples, this is a **single endpoint observation**, not a long-run mean.

Independent reconstruction gives:

| Evaluation window | Samples | Endpoint-calibrated constant RMSE | Best in-window constant RMSE | Published static q(P) RMSE | Dynamic porosity RMSE | Endpoint/dynamic factor |
|---|---:|---:|---:|---:|---:|---:|
| 15–95 s | 800 | 0.6214 | 0.5729 | 0.6477 | 0.1158 | 5.37× |
| 15–100 s | 850 | 0.6029 | 0.5594 | 0.6284 | 0.1126 | 5.36× |
| Code label 15–115 s | 850, ending at 100 s | 0.6029 | 0.5594 | 0.6284 | 0.1126 | 5.36× |

The headline factor is numerically similar, so this is not a reversal of the qualitative result. It is nevertheless a direct manuscript–code mismatch and obscures what “flat baseline” means.

### “Static pressure-dependence is identical to a constant” is true in shape, not in fitted level

At one fixed pressure, a static q(P) model is time-constant. It is therefore observationally identical to **some constant curve in shape**. But the published static calibration predicts approximately 1.886 g/s at 9 bar, whereas the endpoint-calibrated constant is approximately 1.825 g/s and the best in-window constant is the observed window mean. Their RMSE values are not identical. The harness currently assigns the endpoint constant's RMSE to both rung 1 and rung 3 rather than evaluating the published static q(P) level ([`harness.py` lines 124–142](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/puckworks/harness.py#L124-L142)).

The final paper should define and report three distinct nulls if all are scientifically relevant:

1. a best-fitting constant over the evaluation window;
2. an endpoint- or long-run-calibrated constant, with the calibration window specified and containing more than one sample;
3. the published static q(P) prediction with no target-trace level adjustment.

### The time samples are not independent evidence

For the empirical dynamic branch over 15–95 s, the residual lag-1 correlation is approximately 0.9992 and the Durbin–Watson statistic is approximately 0.0015. The pointwise residual RMS normalized by the reported flow standard deviations is approximately 1.81. These values indicate a highly structured residual trajectory; 800 time samples should not be treated as 800 independent observations.

The paper presently reports RMSE descriptively, which is acceptable, but it cannot attach conventional sample-size-based certainty to the RMSE without a temporal covariance model or trajectory-level replication. A residual plot is needed. Uncertainty should be estimated from independent shots, a block/bootstrap procedure justified for the trace, or a functional-data model.

### Flat nulls are too weak to support “a time-varying bed term is needed”

The empirical porosity branch clearly improves on the specified constants. That establishes a need for **time variation within the selected model set**, not specifically a bed mechanism. A flexible phenomenological temporal null is missing. As an exploratory diagnostic, a cubic polynomial fitted directly to the same 15–95 s mean trace gives an in-sample RMSE of about 0.096 g/s, below the 0.116 g/s dynamic-porosity result. This is not a fair predictive comparison—the polynomial is fitted to the target trace—but it demonstrates why constants alone cannot establish mechanistic necessity. A monotone/smooth spline, sigmoid, or low-order state-space null should be calibrated and evaluated under the same information budget as the physical branch.

### Required change

- Make the code and manuscript use one explicit window.
- Evaluate each baseline at its actual predicted level; do not copy one RMSE into two rungs.
- Replace the one-sample “long-run mean” with a justified calibration interval or remove it.
- Add a flexible nonmechanistic temporal null and report parameter counts/calibration inputs.
- Add residual curves, autocorrelation, and uncertainty based on independent trajectories or justified blocks.
- Narrow the claim to: “a time-varying trajectory improves reconstruction relative to the specified baselines; the present comparison does not identify the source of that time variation.”

This is the most immediate numerical correction needed in the revision.

---

## 3. The new assertion that the N-tube concentration is “floor-independent” is not tested by the current implementation

The revised manuscript correctly states that the algebraic conductance-ratio gain is floor-dependent and is not a stability eigenvalue ([Draft lines 222–229](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/docs/PAPER_B_DRAFT.md#L222-L229)). It then states:

> “What is robust and floor-independent is the numerical concentration: poroelastic drives N_eff→1, Kozeny–Carman does not.”

That conclusion is not supported by the code as written.

### The algebraic floor sweep and the N-tube integration are separate calculations

In `ntube_kappa_t_union`, the per-tube conductance multiplier is clipped at a hard-coded floor of `1e-12` ([`harness.py` lines 964–979](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/puckworks/harness.py#L964-L979)). The function exposes no `conductance_floor` argument.

`ntube_finite_time_gain` varies floors only in the separate algebraic calculation `M_f / max(M_0, floor)`. It then calls `ntube_kappa_t_union(...)` once per closure without passing any floor, so every numerical N-tube trajectory still uses `1e-12` ([`harness.py` lines 1042–1085](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/puckworks/harness.py#L1042-L1085)). Figure 5 panel (b) therefore establishes floor sensitivity of the algebraic ratio only. It does not establish floor insensitivity of final N_eff, maximum tube share, concentration time, or the classification threshold.

The claim may eventually prove true over a reasonable regularization range. It is currently **untested**, not demonstrated.

### The homogenization and control operators are not physically comparable

Under flow control, `w = g / mean(g)` has mean one, and blending `w <- (1−λ)w + λ` preserves the mean. Under pressure control, `w = g / mean(g0)` need not have mean one as conductance evolves; the same blend moves both heterogeneity and total throughput toward one. Thus the “lateral” parameter does not merely represent exchange under pressure control—it also alters the aggregate age/throughput clock. This complicates the claim that the control-mode contrast isolates flow stealing.

The manuscript appropriately calls the term a proxy rather than transverse Darcy exchange. The conclusion should be equally limited. “Structurally unsafe” ([Draft lines 233–240](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/docs/PAPER_B_DRAFT.md#L233-L240)) is still too broad for one regularized ODE configuration with a nonphysical homogenizer.

### The binary “concentrates” classification is operational

The code labels a run as concentrating when the final top-decile share exceeds 0.90 and the trajectory is not classified as self-limiting ([`harness.py` lines 1009–1027](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/puckworks/harness.py#L1009-L1027)). That threshold is useful operationally, but it is not a stability criterion and does not require the single-tube share itself to approach one. The paper should emphasize continuous metrics—N_eff(t), maximum share, top-decile share, and concentration time—rather than a thresholded label.

### Required change

Expose the regularization and numerical choices as explicit arguments and run the actual N-tube integration over:

- conductance floor or, preferably, a physically interpretable nonzero start state;
- start time/initial extraction age;
- N;
- timestep and substeps;
- quadrature/initial heterogeneity resolution;
- grind, pressure, closure parameters, and control mode;
- lateral-operator strength and form.

For each sweep, report N_eff(t), maximum share, top-decile share, concentration time, aggregate throughput, and convergence. Until this is done, replace the floor-independence sentence with:

> At the currently implemented conductance floor (`10⁻¹²`), the near-choke flow-controlled, zero-homogenization calculation concentrates strongly, whereas the auxiliary Kozeny–Carman calculation remains distributed. Dependence of the numerical concentration on conductance regularization and start state has not yet been established.

A physical lateral-exchange model and Jacobian/finite-time-Lyapunov analysis remain appropriate future work. They are not required if Result 3 is explicitly retained as an exploratory numerical failure mode, but the regularization and convergence sweep is required even for that narrower claim.

---

## 4. The document is still a research memo rather than a submission manuscript

The revision openly acknowledges this, but the missing elements are core manuscript requirements rather than optional polish:

- The opening block refers to the prior review, adopts “verb discipline,” calls the title “review-endorsed,” and points to internal roadmap items ([Draft lines 1–19](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/docs/PAPER_B_DRAFT.md#L1-L19)). None of this belongs in the submitted manuscript.
- The Methods section describes the registry concept but does not give the equations, preprocessing, experimental units, calibration/evaluation splits, numerical solvers, tolerances, uncertainty procedures, or parameter tables needed to reproduce the results ([Draft lines 83–108](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/docs/PAPER_B_DRAFT.md#L83-L108)).
- There is no related-work section, bibliography, or reference list. Claims such as “a prerequisite the field has not stated,” “the mechanisms have not been run head-to-head,” and “homogeneous-flow models predict” cannot stand without a literature review and citations.
- There is no data/code availability statement, archived release/DOI, software environment, or exact command sequence for regenerating tables and figures.
- The “Status & to-do” block explicitly lists analyses still owed before submission ([Draft lines 275–289](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/docs/PAPER_B_DRAFT.md#L275-L289)). That block should be converted into an internal checklist and removed from the paper.

A passing software gate and a committed draft are useful project-management milestones. They are not substitutes for a conventional scientific Methods section or an archived reproducibility package.


---

# Major scientific and implementation comments

## 5. The RSM correction is scientifically right, but the repository refit must become a documented analysis rather than a plotting convenience

The rewrite correctly explains why literal evaluation of the rounded Table-3 coefficients produces a spurious absolute prediction ([Draft lines 118–126](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/docs/PAPER_B_DRAFT.md#L118-L126)). The current `schmieder_rsm_refit` is a useful audit, but it returns only the number of observations and three central predictions; it does not return coefficient covariance, adjusted R², residual diagnostics, or uncertainty in the vertex/prominence ([`harness.py` lines 720–763](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/puckworks/harness.py#L720-L763)).

### Independent audit of the current retained-term refit

Using the 48 complete TDS, brew-ratio 1/2 replicate rows, target flow/temperature, and the retained terms

\[
1,\;F,\;G,\;T,\;G^2,\;T^2,\;F G,
\]

the ordinary least-squares audit gives:

| Quantity | Audit result |
|---|---:|
| R² | 0.694 |
| Adjusted R² | 0.649 |
| Prediction at F=2, G=1.7, T=89 | 3.918 g |
| 95% CI for mean prediction | [3.859, 3.977] g |
| Raw central-cell mean | 3.876 g |
| Literal rounded-coefficient prediction | 6.723 g |
| Grind vertex at F=2 | 1.733 |
| Delta-method 95% CI for vertex | [1.683, 1.783] |
| Peak above G=2 endpoint | 0.106 g |
| Delta-method 95% CI for that prominence | [0.022, 0.191] g |

The adjusted R² is close to the printed 0.64, supporting the conclusion that the source's absolute fitted level was near the data and that 6.7 g is a rounding artifact. It does not prove that this is exactly the source software's fit.

The raw-unit design matrix is also severely ill-conditioned: its condition number is approximately 1.66×10⁶. Centering/scaling F, G, and T reduces the condition number to approximately 3.88. This is precisely why rounded coefficients in an uncentered polynomial basis are unsafe for absolute reconstruction. The final Methods should report a centered/scaled model or provide a stable prediction function, even if the paper prints raw-variable coefficients for comparability.

### The unit of analysis changes the uncertainty

If the 15 experiment-condition means are fitted instead of all replicate rows, the central prediction remains similar (3.929 g), but the vertex interval widens to approximately [1.653, 1.811] and the prominence interval becomes approximately [−0.030, 0.254] g. The latter includes zero. The difference arises because the replicate-level fit gives extra weight to conditions with more replicates and treats within-condition rows as independent contributions.

This sensitivity is not a reason to discard the RSM. It is a reason to state:

- whether the source model was fit to individual replicate rows or condition means;
- whether target or achieved flow/temperature were used;
- how repeated center points were weighted;
- which terms were selected or eliminated and by what rule;
- what covariance estimator and resampling unit were used.

A bootstrap should resample at the experiment/condition level unless individual shots are demonstrably independent experimental units.

### Figure 1 currently mixes two different surfaces

Figure 1 plots the repository's raw-data refit but draws and labels the vertex from the printed rounded coefficients ([`figures.py` lines 67–100](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/puckworks/figures.py#L67-L100)). The difference is small—about 1.733 versus 1.747—but the logic is inconsistent. A refitted curve must use its own vertex and uncertainty band. If the printed-source vertex is shown, the plotted curve must be identified as an approximate printed-coefficient curve and not used for absolute level.

### Recommended path

Choose one of two clean options:

1. **Source-RSM option:** obtain full-precision coefficients or the original model object, reproduce the source surface, and report its uncertainty if available.
2. **Repository-refit option:** call it a documented reanalysis, use centered/scaled predictors, specify the analysis unit and retained terms, report coefficients/covariance/adjusted R²/residuals, and bootstrap the vertex and prominence.

Do not describe the refit as “shape only” while simultaneously using it quantitatively in Figure 1 without a statistical specification.

---

## 6. The concavity audit is a useful step, but “96–97% concave over the support” is not yet the cleanest test of the Jensen claim

The new `channeling_concavity_audit` directly responds to the prior review and is a meaningful improvement ([`harness.py` lines 594–631](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/puckworks/harness.py#L594-L631)). It checks numerical curvature on the finite response domain and estimates the Gauss–Hermite weight of nodes outside that domain. The draft appropriately says global concavity is not claimed.

Several technical qualifications remain:

1. The lognormal distribution has infinite support. `[k_min, k_max]` is the interpolation/clipping domain, not the distribution's or quadrature's mathematical “support.”
2. The second derivative is approximated by two calls to `numpy.gradient` on a linear-in-k grid, whereas the PCHIP is constructed in log k. Boundary formulas, grid density, and the arbitrary `1e-9` tolerance can materially affect a result reported as a percentage of grid points.
3. PCHIP is piecewise cubic and shape-preserving in the interpolated variable, but it does not guarantee global curvature preservation after the transformation from log k to k.
4. The clipping diagnostic sums the weights of a 15-node Gauss–Hermite rule outside the response domain. That is not the same as the exact lognormal tail probability and should be checked against the analytic CDF.

Most importantly, the paper's substantive claim is the **sign and size of the ensemble Jensen gap**, not the fraction of a grid with negative estimated curvature. The direct audit is:

\[
J(\sigma,g,p)=E[f_{g,p}(K)]-f_{g,p}(E[K]),\qquad E[K]=1.
\]

For a claimed deficit, report `J < 0` and its magnitude across the actual calibrated and sensitivity parameter values. Repeat it over response-grid density, Gauss–Hermite order, and interpolation domain. This directly verifies the modeled effect even if the response has small local convex regions.

If pointwise curvature is retained, use the spline's derivatives in its native log coordinate. With x=log k and f=f(x),

\[
\frac{d^2 f}{d k^2}=\frac{f_{xx}-f_x}{k^2}.
\]

Report curvature after excluding boundary stencil points and show convergence over several k grids and tolerances. Also report the exact lognormal probability outside `[k_min,k_max]`, not only discrete quadrature-node weight.

The current wording “Jensen-type yield deficit” is appropriately cautious. Keep that wording until the direct gap and numerical convergence are documented.

---

## 7. The 10-of-25 closure result is better framed, but its summary still overstates typical magnitude

The revised draft explicitly says the 10/25 fraction is descriptive over a chosen rectangle rather than a robustness probability ([Draft lines 154–164](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/docs/PAPER_B_DRAFT.md#L154-L164)). That is an important correction.

Three issues remain in `channeling_interior_max_sensitivity` ([`harness.py` lines 634–717](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/puckworks/harness.py#L634-L717)):

### 7.1 “Pre-specified” is not documented

The manuscript calls the 25 combinations “pre-specified,” but it identifies no protocol, preregistration, or earlier commit that fixes the rectangle before the result was inspected. Use “fixed 5×5 analysis grid” unless a dated protocol can be cited.

### 7.2 The median prominence is conditional on successful peak cases

The code constructs `proms` only from combinations classified as interior and reports the median of that subset. Thus “median prominence ~0.14 EY-points” is the median **among the 10 successful cases**, not among all 25 combinations. Conditioning on the outcome makes the typical effect across the rectangle appear larger.

Report a signed interior contrast for every grid point, such as

\[
\max_{g\ \mathrm{interior}} EY(g)-\max(EY(g_{min}),EY(g_{max})),
\]

and summarize all 25 values. Show a contour/heatmap rather than reducing the result to a fraction and a success-conditional median.

### 7.3 “Grid-converged” currently means only stable discrete peak location

The convergence flag checks whether the argmax falls at the same one of seven grind points for response-grid sizes 7, 13, and 21. It does not test convergence of prominence, curve shape, Gauss–Hermite order, or the seven-point grind-axis discretization itself. A peak can remain at the same grid point while its prominence changes materially.

The final sensitivity analysis should vary:

- response-solver grid/tolerance;
- Gauss–Hermite order;
- grind-axis density;
- interpolation domain;
- closure parameters with uncertainty from the Cameron calibration;
- pressure and any donor-model parameters that materially affect EY(k).

The most informative result would be the probability or fraction of bootstrap-calibrated closure draws that produce a positive, practically detectable prominence—not a uniform count over an arbitrary rectangle.

---

## 8. Cross-pressure wording improved in the manuscript, but the code, figures, and calibration logic remain out of sync

The manuscript now describes the analysis as “within-rig generalization conditional on campaign-wide constants” and explicitly denies fully independent out-of-sample validation ([Draft lines 185–196](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/docs/PAPER_B_DRAFT.md#L185-L196)). This is the correct direction.

The implementation still says:

- “out-of-sample RMSE,”
- “the mechanism that best explains all pressures wins,”
- “Phi(t) wins on the OOS mean,”
- and “the other 10 are out of sample”

([`harness.py` lines 838–905](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/puckworks/harness.py#L838-L905)). Figure 3 repeats “Cross-pressure OOS” and “out-of-sample RMSE” ([`figures.py` lines 190–199](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/puckworks/figures.py#L190-L199)). These stale labels will undermine the manuscript's improved claim discipline if the figures are read independently.

The scientific issue is larger than terminology. The published static calibration pair was estimated from the same eleven-pressure campaign, so the non-9-bar traces are not held out from that calibration. The empirical dissolved-mass sigmoid and other constants are also campaign-derived. The current analysis is a **conditional transfer across pressures under shared campaign calibration**.

A stronger validation would perform leave-one-pressure-out refitting of every campaign-level quantity that used the held-out pressure, then predict the excluded trace. Better still, repeat the analysis on a second coffee, rig, grind, or day. Until then:

- rename `oos_mean` to `conditional_transfer_mean` or similar;
- remove “wins/winner” from docstrings and figure labels;
- show continuous residual-versus-pressure curves with uncertainty;
- state how the low/mid pressure ranges were chosen and avoid inferential language for post hoc bins;
- report parameter counts and exactly which data informed each branch.

---

## 9. The shared-porosity failure is useful, but the comparison currently mixes windows and reintroduces “parameter-free” language

The manuscript's scoped interpretation of the failed extraction-plus-swelling composition is much better than the prior causal diagnosis ([Draft lines 198–208](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/docs/PAPER_B_DRAFT.md#L198-L208)). Two inconsistencies remain.

### 9.1 “Parameter-free” contradicts the manuscript's own caution

At line 182, the draft says “parameter-free” is avoided because donor parameters were estimated elsewhere and the trajectory contains target-rig information. At line 200, it calls the swelling branch “parameter-free.” The model and figure code do the same ([`coupled_kappa_t.py` lines 107–118](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/puckworks/models/brewer2026/coupled_kappa_t.py#L107-L118); [`figures.py` lines 231–236](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/puckworks/figures.py#L231-L236)).

Use “pre-parameterized imported branch, with no parameters refit to this trace.” That captures the intended distinction without implying the branch has no empirical parameters.

### 9.2 Figure 4 compares residuals from different windows

`coupled_kappa_t.degeneracy_rmse` and `composition_residual` default to 15–95 s. Figure 4 labels the flat null as 0.603, hard-coded from the ladder's effective 15–100 s calculation ([`figures.py` lines 212–236](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/puckworks/figures.py#L212-L236)). The stated comparison “0.648 > 0.603” therefore uses different windows.

On 15–95 s, the endpoint-calibrated constant is approximately 0.621 g/s, the best constant is approximately 0.573 g/s, and the published static q(P) curve is approximately 0.648 g/s. The swelling composition may still be worse than the endpoint/best constants, but the figure and text must compare like with like.

The phrase “a diagnosed mis-scale” in Figure 4 remains too strong. The calculation demonstrates incompatibility of the imported branch under this composition, control regime, initial condition, and transfer convention. It does not uniquely diagnose parameter scale.

---

## 10. Several high-level claims need narrower attribution and literature support

### 10.1 Clarify whose mixed-observable error is being corrected

The Abstract says “we correct a mixed-observable aggregation” but can be read as accusing the source study or the field of combining mg solute masses with g TDS values. The source data report distinct observables; the problematic aggregation was in the prior repository comparison. State this explicitly:

> We correct an earlier aggregation in our comparison pipeline that combined distinct solute-mass and TDS observables across brew ratios.

This protects the source authors from an unintended criticism and makes the software/data-contract contribution clearer.

### 10.2 Remove unsupported novelty claims until the related-work review exists

“Enforcing a single matched observable is a prerequisite the field has not stated” ([Draft lines 25–33](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/docs/PAPER_B_DRAFT.md#L25-L33)) is a broad novelty claim without a review. Replace it with “an often-implicit prerequisite” unless a systematic search supports the stronger statement.

Similarly, “the mechanisms have not been run head-to-head” and any “first” claim must wait for a documented related-work search. The parenthetical caveat in the Introduction is honest, but the unsupported sentence should not remain in the manuscript body.

### 10.3 Scope the homogeneous-model and integrated-observable claims

“Homogeneous-flow models predict a monotone rise” should be tied to the specific model lineage and conditions examined. “Integrated observables are insufficient for unique mechanism identification” should become:

> Across the datasets, observables, and implemented model classes tested here, the integrated measurements do not uniquely identify a mechanism.

Integrated observables are not intrinsically non-identifying in every experiment; identifiability depends on excitation, noise, model class, and the number and type of measurements.

### 10.4 Avoid sliding back from a dial response to a universal fine-grind anomaly

The manuscript carefully distinguishes the Schmieder dial response from the Cameron fine-grind deviation. The practitioner statement “static flow heterogeneity remains a plausible generator of the fine-grind response” risks merging them again. Prefer:

> Static flow heterogeneity remains a plausible capacity mechanism for Cameron-type fine-grind deviations, but the present integrated datasets do not identify it uniquely.

---

## 11. The strongest paper may be narrower than the current three-result package

The current paper joins:

1. a matched-observable audit and static model-capacity test;
2. a null-first temporal reconstruction ladder;
3. an exploratory N-tube composition failure.

They are connected by observability and model-composition discipline, but they do not form an experimentally established causal chain. The manuscript should not imply that the static heterogeneity inferred in Result 1 becomes the evolving channel in Result 3 or that the 9-bar whole-bed porosity trajectory is the local per-tube clock. Those links are modeling hypotheses.

Two viable architectures are available:

- **Integrated methods paper:** keep all three results, explicitly label Result 3 as a numerical cautionary example, and make the thesis “matched observables, nulls, and composition audits prevent over-identification.”
- **Narrower empirical/model-discrimination paper:** center Results 1 and 2, move Result 3 to an appendix or companion methods paper until its regularization and physical lateral-exchange analysis are mature.

The second route would likely produce a tighter submission sooner. The first can work, but only if Result 3 is prevented from becoming the rhetorical climax of a paper that otherwise emphasizes evidential restraint.


---

# Section-by-section review

## Front matter and title

The current title—“Mechanism discrimination in espresso flow and extraction: matched observables, null models, and transient streamtube concentration”—is accurate enough for the revised scope. “Transient streamtube concentration” may still give Result 3 more weight than its present evidence warrants. A tighter alternative is:

> **Matched-observable and null-first tests for mechanism discrimination in espresso extraction and flow**

Remove the revision note, prior-review summary, verb-discipline instructions, “review-endorsed” label, figure-path notes, and comments about a hypothetical stability-focused title. Preserve those in an internal editorial file or pull-request description.

## Abstract

The Abstract is substantially improved, especially in calling static channeling a capacity result and Result 3 exploratory. It still needs five changes:

1. Identify the mixed-observable aggregation as an error in the authors' earlier comparison pipeline, not in the source study or the whole field.
2. Replace “a prerequisite the field has not stated” with a literature-supported or narrower phrase.
3. Replace “the response is monotone” with “the cell means are ordered and the middle cell lies below dial 2.0,” unless a full order-restricted/design-aware analysis is added.
4. Avoid implying the empirical porosity branch establishes a bed mechanism; say it improves reconstruction relative to specified temporal nulls.
5. Replace the broad final conclusion with “in the tested datasets and model classes.”

Do not include Result-2 RMSE numbers in the Abstract until the window and baseline definitions are corrected. Do not call the N-tube concentration floor-independent until an actual numerical floor sweep is completed.

## Introduction

The three-object table and two confounds are strong. Add citations for:

- the Cameron fine-grind deviation and homogeneous-model prediction;
- the Schmieder dial/particle-size mapping and pressure confound;
- each proposed competing mechanism;
- prior work on channeling, incomplete wetting, dissolution feedback, swelling, compaction, and fines migration;
- model discrimination/identifiability concepts outside espresso if those concepts motivate the framework.

The sentence “the mechanisms have not been run head-to-head” should be removed or made explicitly provisional until the related-work search is complete. Define what counts as “head-to-head”: same dataset, same observable, same calibration budget, and the same evaluation split.

The research questions are clear. Question 4 should say “What numerical failure can occur in the implemented composition?” rather than implying a general physical failure.

## Methods

The registry description is not yet a Methods section. A conventional structure could be:

### 2.1 Data sources and experimental designs

For every dataset, report source, license, original sampling design, number of conditions and replicates, measured variables, pointwise uncertainty, digitization, exclusions, and any transformation performed in this repository.

### 2.2 Observable contracts and preprocessing

Define TDS mass, TDS-derived EY, solute-specific mass, brew ratio, dose, flow, pressure, and temperature. State exactly which rows form each analysis. Explain that the no-silent-merge check corrects an earlier repository aggregation.

### 2.3 Result-1 empirical statistics

State the experimental unit, target versus achieved covariates, contrast definitions, variance assumptions, multiplicity policy, and confidence-interval method. If the three-level ordering is claimed, use an order-restricted or trend analysis and still report pairwise effects.

### 2.4 RSM audit

Give the retained polynomial, predictor coding/centering, analysis unit, weighting, selection rule, covariance estimate, residual diagnostics, and bootstrap procedure for the vertex and prominence.

### 2.5 Static streamtube model

Write the permeability distribution, quadrature, EY response interpolation, sigma closure, calibration dataset/objective, parameter uncertainty, clipping, and numerical convergence checks. Separate donor-source parameters from repository choices.

### 2.6 Temporal ladder

Define every null and mechanistic branch as an equation, identify every calibration datum, specify the evaluation window, and report parameter/information budgets. Explain the relationship between the Foster trace and the Waszkiewicz trace rather than placing them in one ladder without context.

### 2.7 Cross-pressure analysis

State which quantities are campaign-wide, which are fitted at 9 bar, which use all pressures, and what is held out. If leave-one-pressure-out is used, describe the complete refit loop.

### 2.8 Shared-porosity and N-tube exploratory models

Give governing equations, initial conditions, clipping/floors, normalization under each control mode, time integration, step-size checks, concentration metrics, and operational thresholds. Clearly label the homogenizer as a numerical operator.

### 2.9 Reproducibility and uncertainty

Pin a release, environment, random/deterministic nodes, commands, test scope, figure-generation commands, and archived data/code DOI. Distinguish software regression tests from scientific validation gates.

## Result 1

The target/capacity/identification separation is good. Revise “statistically monotone,” document the achieved-condition mismatch, and make the RSM refit a formal analysis. The concavity and closure-sensitivity claims should be accompanied by a supplementary table/figure showing direct Jensen gaps and the full signed 5×5 response surface.

“Among the response generators currently implemented” is an appropriately limited universe. The phrase “without altering a source parameter” should be supplemented with a calibration-budget column because the static channeling closure is empirically calibrated to another response. A parameter need not be altered in the current run to make a comparison partly circular.

## Result 2

Correct the evaluation window and baseline definitions before any further interpretation. The manuscript's current caveats about soft circularity, conditional transfer, and omitted mechanisms are good and should remain. Add a flexible temporal null and residual diagnostics. Avoid “needed” unless it is explicitly followed by “within this model set and comparison design.”

The Foster machine-only example is valuable but belongs either in a separate null-demonstration subsection or in the Introduction/Discussion. It is not fitted to the same Waszkiewicz trajectory and therefore does not occupy the same empirical ladder rung as the 9-bar baselines.

## Result 3

This section is much better than the prior version. It should now be titled something like:

> **Exploratory Result 3 — finite-time concentration in an uncoupled N-tube composition**

Remove “floor-independent” until tested. Replace “structurally unsafe” with “can concentrate strongly under the implemented configuration.” Define the initial heterogeneity, floor, start state, and concentration threshold in the text. Make clear that the local extraction-age law is an imposed composition of donor models, not an observed per-pathway mechanism.

Consider moving the algebraic conductance-ratio calculation to an appendix. Its main value is to expose the singular near-choke initialization and motivate the regularization audit, not to quantify amplification.

## Discussion

The observability theme is persuasive. Scope it to the tested examples. The sentence saying integrated observables “erase” discriminating structure is rhetorically absolute; “can erase” is more accurate.

The simulated pathway outputs are correctly labeled simulated. Expand the experimental-design implications into a concrete table:

| Ambiguity | Measurement most likely to discriminate it | Predicted difference |
|---|---|---|
| Static heterogeneity vs incomplete wetting | first-drip timing by grind; spatial saturation | wetting mechanism changes onset/saturation pattern |
| Machine dynamics vs bed evolution | simultaneous pump/headspace/basket pressure and flow | machine null predicts coupled machine-state signatures |
| Empirical porosity vs alternative temporal curves | independent dissolved-mass/bed-height trajectory | porosity branch predicts a specific measured state trajectory |
| Uncoupled concentration vs lateral exchange | spatial flow/pathway imaging | exchange limits pathway-share divergence |

This turns the paper's negative identifiability conclusion into a constructive experimental agenda.

## Open gaps and status block

Some items in “Open gaps” are legitimate future studies, such as a new spatial dataset or physical lateral-exchange experiment. Others—RSM covariance, residual diagnostics, and numerical regularization sweeps—are analyses required to support current claims and should be completed before submission rather than advertised as future work.

Delete the “Status & to-do” section from the manuscript. Keep it in `ROADMAP.md` or an issue tracker.

---

# Figure-by-figure review

## Figure 1 — target and model capacity

**Strengths:** The two panels correctly separate the empirical target from the model's own dial axis, and the caption-level title says capacity rather than identification.

**Required corrections:**

- The error bars are population SD (`ddof=0`) but are unlabeled. Show individual replicates plus mean and a clearly defined interval; with n=3/6, raw points are more informative than symmetric bars.
- The refit curve and vertex come from different coefficient sets. Use the repository-refit vertex and uncertainty band if plotting the refit.
- The text “fragile: 40% of closures” reintroduces the exact shorthand the manuscript corrected. Use “10/25 on the fixed analysis grid; descriptive” or omit the fraction from the panel.
- Add the Sauter-diameter mapping to the empirical dial axis so the nonmonotonic dial-to-particle-size relation is visible.
- State that the model dial axis is not quantitatively aligned with the Schmieder grinder dial.

Relevant code: [`figures.py` lines 56–119](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/puckworks/figures.py#L56-L119).

## Figure 2 — evidence matrix

The manuscript says the matrix will include implementation status, calibration data, evaluation data, observable, free parameters, fitted-versus-predicted status, evidence strength, and decisive missing experiment. The actual figure has five columns and hard-codes every cell; the imported `board` output is not used ([`figures.py` lines 123–156](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/puckworks/figures.py#L123-L156)). This contradicts the module's claim that every number is pulled from the harness.

Rebuild the matrix from structured metadata. Include all dimensions promised in the manuscript or reduce the prose to match the actual figure. Avoid red/green “yes/no” scoring for evidence strength, which can look like a winner scoreboard despite the title. A table with textual evidence tiers and calibration/evaluation datasets may be clearer.

Remove “doctored” from code, comments, and labels. “Sensitivity value set to 2× the measured ceiling” is neutral and precise.

## Figure 3 — temporal ladder and cross-pressure transfer

The figure still says “Cross-pressure OOS,” labels the y-axis “out-of-sample RMSE,” and concludes “a time-dependent bed is required” ([`figures.py` lines 160–200](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/puckworks/figures.py#L160-L200)). These statements contradict the revised manuscript.

More importantly, a bar chart of three RMSE values hides the systematic residual structure. Replace or supplement it with:

- observed 9-bar mean trace and uncertainty band;
- all baseline/dynamic predictions over the exact evaluation window;
- residual-versus-time curves;
- a small table of RMSE, parameter count, calibration inputs, and window;
- conditional cross-pressure residual curves labeled as within-campaign transfer.

The Foster panel comes from a distinct source configuration. Mark it explicitly as an external counterexample to shape-based diagnosis, not as a fitted rung on the Waszkiewicz trace.

## Figure 4 — failed composition

The 0.603 flat-null value is hard-coded and comes from a different window than the two model residuals. Compute all values from one result object and one window. Replace “parameter-free,” “OVER-closes,” and “diagnosed mis-scale” with neutral language consistent with the manuscript. Consider adding a porosity-state panel showing why the imported swelling term changes the trajectory and whether any clamp/floor is active.

Relevant code: [`figures.py` lines 204–237](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/puckworks/figures.py#L204-L237).

## Figure 5 — finite-time concentration

The current figure is a substantial improvement over the prior “stability map,” but its function and output filename still use “stability.” Rename both.

Panel (a) shows six final N_eff values at one grind, one pressure, one floor, one N, and one closure. It is not a phase map. Show time trajectories and numerical convergence, not only final values. Panel (b) varies the algebraic floor but not the numerical N-tube floor, so it cannot support the manuscript's floor-independence statement.

A defensible revised Figure 5 would include:

- N_eff(t) and maximum share for several actual conductance floors/start states;
- convergence with N and substeps;
- poroelastic versus Kozeny–Carman under the same settings;
- flow versus pressure control, with aggregate throughput shown;
- the homogenizer clearly labeled as a numerical proxy.

Relevant code: [`figures.py` lines 241–285](https://github.com/trbrewer/puckworks/blob/135f5d277ea004f8e05532f16bf8a1ba67889d78/puckworks/figures.py#L241-L285).

## Figure production

The renderer writes only PNG files. For journal submission, also export vector PDF or SVG with embedded text, verify font sizes at final column width, add panel-specific captions, and provide a machine-readable table behind every plotted summary. The module-level claim that nothing is hand-typed should be removed until Figure 2 and the hard-coded Figure-4 baseline are fixed.

---

# Suggested replacement language

## Suggested revised Abstract

> Espresso measurements integrate extraction, flow, and bed evolution, allowing distinct mechanisms to produce similar whole-cup or whole-bed signals. We use a provenance-tracked model registry and matched-observable, null-first comparisons to determine what two published datasets can discriminate within a specified model set. First, we correct an earlier aggregation in our comparison pipeline that combined distinct solute-mass and total-dissolved-solids observables across brew ratios. At the nominal central settings, TDS-derived extraction-yield means are 18.27, 19.38, and 19.62% at grinder dials 1.4, 1.7, and 2.0; dial 1.7 is 0.24 percentage points below dial 2.0 (Welch 95% CI [−0.42, −0.06]), so the raw cells do not support an interior maximum at the middle dial. A calibrated lognormal streamtube ensemble can generate a small interior maximum for some closure choices, establishing model capacity rather than identifying channeling. Second, on a 9-bar rising-flow trace, an empirical time-varying porosity trajectory improves reconstruction relative to explicitly defined constant baselines, but it uses campaign-derived information and is not uniquely identified; conditional transfer across pressures is regime-dependent. Finally, an exploratory uncoupled N-tube composition can concentrate flow strongly in the implemented near-choke, fixed-total-flow, zero-homogenization configuration, but the result is regularization-dependent until numerical floor and start-state sweeps are completed and does not constitute a stability theorem. Across the datasets and model classes tested here, integrated measurements do not uniquely identify a mechanism; spatial, pathway-resolved, first-drip, or independently measured bed-state observables would be more discriminating.

Update the Result-2 wording and numbers after correcting the window and null definitions. If the N-tube floor sweep shows practical invariance, the regularization sentence can be strengthened with the tested range.

## Suggested revised Result-1 opening

> At the nominal central settings, the TDS-derived extraction-yield cell means increase across grinder dial: 18.27, 19.38, and 19.62% at dials 1.4, 1.7, and 2.0. The middle cell is 0.24 EY-points below dial 2.0 (Welch 95% CI [−0.42, −0.06]), ruling out an interior maximum at dial 1.7 under this comparison. The 1.4-versus-1.7 interval includes zero, so we describe the means as numerically ordered rather than claiming that every adjacent increase is statistically resolved. These are nominal-condition comparisons: achieved flow and pressure vary among the experiment conditions.

## Suggested revised Result-2 core claim

> Over the prespecified [corrected window] interval, the empirical time-varying porosity trajectory has lower RMSE than each explicitly defined constant baseline. This demonstrates that time variation improves reconstruction within the tested model set. It does not by itself identify a bed mechanism, because the trajectory uses information from the same experimental campaign, residuals are strongly autocorrelated, and flexible nonmechanistic temporal nulls have not yet been excluded.

## Suggested revised Result-3 core claim

> With the currently implemented conductance floor, start state, and numerical resolution, the near-choke poroelastic composition concentrates flow strongly under fixed-total-flow control and zero homogenization, while the auxiliary Kozeny–Carman composition remains distributed. This is a finite-time property of the implemented ODE, not a linear-stability result. The dependence of N_eff and maximum pathway share on conductance regularization, initial age, and numerical resolution must be established before claiming robustness.

---

# Prioritized revision plan

## Priority 1 — repair Result 2's numerical contract

1. Choose and encode one evaluation window.
2. Define every baseline and calculate its own predicted level/RMSE.
3. Remove the one-sample “long-run mean.”
4. Regenerate Figures 3 and 4 from the same window and result object.
5. Add residual plots/autocorrelation and a flexible temporal null.

This is the most direct current manuscript–code inconsistency.

## Priority 2 — make Result 1's inference design-aware

1. Replace “statistically monotone” with “ordered means; middle below dial 2.0.”
2. Report achieved flow, temperature, and pressure by dial.
3. State the experimental unit and account for experiment/condition structure.
4. Plot raw observations and defined intervals.
5. Keep the negative conclusion: no raw interior maximum at dial 1.7.

## Priority 3 — formalize the RSM reanalysis

1. Decide source-model versus repository-refit route.
2. Center/scale predictors and document the retained terms.
3. Report covariance, adjusted R², residuals, influence diagnostics, and prediction uncertainty.
4. Bootstrap experiment-level vertex and prominence.
5. Use one consistent curve/vertex in Figure 1.

## Priority 4 — test the actual N-tube regularization sensitivity

1. Parameterize the conductance floor/start state.
2. Sweep floor, start time, N, substeps, timestep, pressure, grind, and control.
3. Report continuous concentration metrics and aggregate throughput.
4. Remove “floor-independent” unless the actual ODE sweep supports it.
5. Retain the physical lateral operator and formal stability analysis as future work or a companion paper.

## Priority 5 — complete the static-channeling numerical audit

1. Report direct Jensen gaps.
2. Use exact tail probabilities and quadrature-order convergence.
3. Report all 25 signed prominence values, not a success-conditional median.
4. Refine the grind axis and propagate closure-calibration uncertainty.
5. Replace “pre-specified” with “fixed” unless a protocol is cited.

## Priority 6 — synchronize manuscript, code, and figures

Remove stale “OOS,” “winner,” “doctored,” “parameter-free,” “required,” and “runaway” language where it contradicts the revised evidence tiers. Derive Figure 2 and every numeric figure annotation from structured outputs. Add automated manuscript-figure consistency checks for windows, labels, and reported RMSE values.

## Priority 7 — convert the draft into a conventional manuscript

1. Remove all review/roadmap/status prose from the manuscript body.
2. Add full Methods, related work, citations, and references.
3. Add data/code availability, archived release/DOI, environment, and commands.
4. Add limitations and experimental-design implications.
5. Export publication-quality vector figures with complete captions.

---

# Final verdict

The updated draft is a meaningful scientific improvement and demonstrates unusually good willingness to retract or narrow claims when the implementation does not support them. The earlier three central problems have been addressed at the conceptual level. The paper's methodological core—matched observables, explicit evidence tiers, null-first comparison, and honest model-composition failures—is worth developing.

The revision should nevertheless remain at **major revision**. The decisive remaining blockers are:

1. the 15–95 versus effective 15–100 s Result-2 mismatch and ambiguous flat/static baselines;
2. the overstatement of a three-level “statistically monotone” response from one adjacent contrast without a design-aware experimental-unit analysis;
3. the unsupported statement that numerical N-tube concentration is floor-independent when the ODE floor is hard-coded and never swept;
4. stale stronger claims in the harness and figure code that contradict the revised manuscript;
5. the absence of conventional Methods, related work, references, residual diagnostics, and an archived reproducibility package.

After those corrections, the paper could make a strong contribution as a **methods and model-discrimination study**, provided it resists returning to mechanism-identification or stability language. Its most defensible conclusion is not that channeling has been identified, but that careful observable matching and null construction reveal how little the currently integrated data uniquely determine—and specify the measurements needed to do better.

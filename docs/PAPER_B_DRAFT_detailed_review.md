# Detailed review of `PAPER_B_DRAFT.md`

## Review basis

This review evaluates the manuscript against the repository state that produced it, rather than against an unspecified moving `main` branch.

- **Draft reviewed:** [`docs/PAPER_B_DRAFT.md`](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/docs/PAPER_B_DRAFT.md)
- **Pinned repository revision:** [`803260f65d60d99f39b9cffb86e01a252d0e3d20`](https://github.com/trbrewer/puckworks/commit/803260f65d60d99f39b9cffb86e01a252d0e3d20)
- **Principal repository files inspected:**
  - [`puckworks/harness.py`](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/puckworks/harness.py)
  - [`puckworks/models/brewer2026/streamtube.py`](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/puckworks/models/brewer2026/streamtube.py)
  - [`puckworks/models/brewer2026/coupled_kappa_t.py`](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/puckworks/models/brewer2026/coupled_kappa_t.py)
  - [`puckworks/figures.py`](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/puckworks/figures.py)
  - [`docs/ANALYSIS_P2.md`](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/docs/ANALYSIS_P2.md)
  - [`docs/P3_hypotheses.md`](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/docs/P3_hypotheses.md)
  - [`docs/ROADMAP.md`](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/docs/ROADMAP.md)
  - [`puckworks/data/schmieder2023/cup_masses.csv`](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/puckworks/data/schmieder2023/cup_masses.csv)
  - [`puckworks/data/schmieder2023/rsm_coefficients.csv`](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/puckworks/data/schmieder2023/rsm_coefficients.csv)
- **Primary experimental source checked:** Schmieder et al., “Influence of Flow Rate, Particle Size, and Temperature on Espresso Extraction Kinetics,” *Foods* 12, 2871 (2023), [DOI 10.3390/foods12152871](https://doi.org/10.3390/foods12152871), including its [Figure 4](https://mdpi-res.com/foods/foods-12-02871/article_deploy/html/images/foods-12-02871-g004-550.jpg) and printed response-surface coefficients.

I independently recalculated the principal Schmieder quantities from the committed CSVs and inspected the exact implementation used to generate the manuscript claims. I did **not** treat a passing QUICK gate as scientific validation. A clean remote clone could not be completed in the execution environment because of network name-resolution failure, so this review does not claim to have rerun the repository’s full `pytest` suite. It is based on the pinned source files, direct code review, primary-source comparison, and independent calculations from the committed data.

---

## Overall assessment

**Recommendation: major revision; not submission-ready.**

The draft has a strong methodological instinct and several publishable ingredients. Its best contribution is not the claimed proof of a channeling mechanism or a closed-form instability result. It is the insistence that mechanism comparisons must use matched observables, explicit evidence tiers, and null-first tests. The correction of the earlier mixed-unit Schmieder aggregation is important, and the paper’s recurring theme—integrated observables can erase the structure needed to distinguish mechanisms—is coherent and potentially valuable.

The present manuscript nevertheless contains three submission-blocking problems:

1. The statement that the Schmieder response surface overpredicts central TDS cup mass by about 1.7× is an artifact of evaluating **rounded printed coefficients** as if they were full-precision model parameters. The source’s own plotted fit and a direct refit to the committed observations both remain near 3.9–4.0 g. This invalidates a central Abstract and Result 1 claim.
2. The “replicate noise floor” and “40% of the parameter grid” claims are descriptive heuristics presented with stronger statistical meaning than they possess.
3. Result 3 is not yet a valid linear-stability result. Its reported amplification is dominated by a numerical conductance floor at a singular near-zero-conductance initialization, the stability threshold is imposed rather than derived, and the lateral term is a homogenizing numerical regularizer rather than a physical transverse-flow model.

The paper also connects three distinct phenomena that have not yet been established as a causal chain:

- a cross-grind extraction response,
- a whole-bed flow history at fixed pressure,
- and a synthetic multi-streamtube feedback calculation.

A combined paper can still work, but the thesis should shift from “channeling plus a streamtube instability explains the anomaly” to **model-capacity tests, observability limits, and failure modes of composing plausible closures**. Otherwise, Result 3 would be cleaner as a separate applied-mathematics or methods paper after a genuine stability analysis is completed.

### Readiness summary

| Element | Current assessment | Required action |
|---|---|---|
| Matched-observable correction | **Strong** | Retain and formalize as a written data contract |
| Validation-strength vocabulary | **Strong** | Apply it consistently to Abstract and conclusions |
| Result 1 raw TDS target | **Useful negative result** | Remove the rounded-coefficient overprediction argument; add valid uncertainty analysis |
| Static-heterogeneity result | **Model-capacity result** | Demonstrate concavity, quantify calibration circularity, and conduct defensible sensitivity analysis |
| Result 2 null-first ladder | **Promising but conditional** | Separate source reconstruction, within-rig generalization, and independent validation |
| Cross-pressure comparison | **Useful within-rig test** | Remove “out-of-sample” overstatement or use leave-one-pressure-out/external validation |
| Shared-porosity composition | **Useful negative result** | Reframe as transfer incompatibility, not a diagnosis of why swelling “does not apply” |
| Result 3 N-tube concentration | **Exploratory** | Replace “linear instability” with finite-time concentration unless a full stability derivation is supplied |
| Figure plan | **Partly inconsistent with text** | Correct Figure 5 scope and regenerate after analyses are fixed |
| Methods | **Incomplete for a paper** | Add equations, preprocessing, calibration splits, uncertainty, software revision, and data/code availability |
| Overall manuscript | **Major revision** | Reframe and recompute before journal formatting |

---

## Principal strengths

### 1. The “no silent observable merge” rule is a genuine contribution

The manuscript correctly recognizes that the earlier aggregate called “cup mass” mixed different compounds, different units, and different brew ratios. The revised adapter requires a component, brew ratio, temperature, and flow condition and checks the resulting unit set ([`harness.py` lines 357–400](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/puckworks/harness.py#L357-L400)). This is exactly the kind of data-contract failure that can survive otherwise careful modeling.

The principle should be retained and generalized:

> No model comparison may average or align measurements until the observable, unit, normalization basis, experimental role, and conditioning variables are explicit and compatible.

That is more broadly useful than any single espresso result.

### 2. The manuscript distinguishes evidence classes better than most modeling papers

The separation of independent evidence, post-fit reconstruction, numerical verification, and qualitative mechanism capacity is conceptually sound. It is especially valuable that the draft states a regression gate is not scientific validation ([Draft lines 83–94](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/docs/PAPER_B_DRAFT.md#L83-L94)). This should remain visible in every result table and figure caption.

### 3. Negative results are treated as informative

The raw central TDS-EY axis points are monotone, the shared-porosity extraction-plus-swelling composition worsens the fit, and no one mechanism wins at every pressure. Those are scientifically useful outcomes. They can support a strong paper if the manuscript makes them the evidence, rather than treating them as side notes on the way to a stronger mechanistic conclusion.

### 4. The unifying observability theme is persuasive

The Discussion’s strongest sentence is that integrated observables erase discriminating structure. That connects:

- whole-cup endpoints and inventory–kinetics non-identifiability,
- whole-bed flow traces and degeneracy among temporal mechanisms,
- and the need for spatial or pathway-resolved measurements.

That is a defensible organizing thesis even if channeling is not identified and the N-tube model remains exploratory.

---

# Submission-blocking findings

## 1. The “~1.7× RSM overprediction” is a coefficient-rounding artifact

### Where the problem appears

The Abstract states that the Schmieder response surface “over-predicts the measured absolute cup mass ~1.7×” ([Draft lines 29–32](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/docs/PAPER_B_DRAFT.md#L29-L32)). Result 1 repeats that the temperature-squared term alone exceeds the cup mass ([Draft lines 116–122](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/docs/PAPER_B_DRAFT.md#L116-L122)). The supporting harness evaluates the printed coefficient row literally ([`harness.py` lines 678–738](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/puckworks/harness.py#L678-L738)).

For TDS at brew ratio 1/2, the committed coefficient table gives:

\[
y = 4.19 - 0.50F + 4.75G - 0.10T - 1.48G^2 + 0.001T^2 + 0.21FG.
\]

At \(F=2\), \(G=1.7\), and \(T=89\), literal substitution gives:

\[
y=6.7228\ \text{g},
\]

versus the committed central-cell mean of 3.8762 g, producing the reported ratio of about 1.73.

### Why that conclusion is not valid

The primary source’s own Figure 4 plots the TDS fitted response at roughly 3.8–4.0 g, near the observations—not at 6.7 g. The source also prints the \(T^2\) coefficient only to three decimal places. With \(T^2\approx 7921\), a seemingly small rounding change in that coefficient has a multi-gram effect.

A direct audit refit to the committed TDS 1/2 observations, using the same retained terms, produces central predictions around **3.92–3.93 g**, depending on whether replicate-level observations or experiment-level means and achieved versus target conditions are used. For example, a replicate-level fit on complete observations gives approximately:

| Term | Audit refit coefficient |
|---|---:|
| intercept | 4.3126 |
| \(F\) | −0.4920 |
| \(G\) | 4.7449 |
| \(T\) | −0.1041 |
| \(G^2\) | −1.4745 |
| \(T^2\) | 0.000675 |
| \(FG\) | 0.2081 |

That model predicts about **3.925 g** at the nominal central point. It is not asserted here that this is the exact OriginPro model used by Schmieder et al.; the audit convention may differ from the authors’ fitting convention. It does demonstrate that the apparent 6.7 g prediction is caused by insufficient printed precision, not by the fitted curve shown in the source.

The source article itself warns that quantitative interpretation of these response surfaces is limited by weak adjusted \(R^2\), but that caveat is different from claiming the model’s fitted absolute level is wrong by 70%. The manuscript currently converts a reporting-precision limitation into a scientific criticism of the source model.

### Required correction

Remove all of the following claims unless full-precision source coefficients are obtained:

- “over-predicts … ~1.7×,”
- “the temperature-squared term alone exceeds the whole cup mass,”
- “usable for shape only” **because of** that supposed overprediction.

Replace them with one of these approaches:

1. Obtain the authors’ full-precision OriginPro coefficients or model object and reproduce Figure 4.
2. Refit the response surface from raw experiment-level data under a fully documented convention, report coefficient uncertainty and residual diagnostics, and label it as the repository’s refit rather than the source’s exact fit.
3. Avoid absolute evaluation of rounded Table 3 coefficients and use the primary source’s plotted curve only for qualitative shape, explicitly because the published rounded coefficients are numerically insufficient for reconstruction.

This is the highest-priority correction because it affects the Abstract, Result 1, the interpretation of Figure 1, and the paper’s claim that matched-observable repair revealed an additional failure in the source response surface.

---

## 2. “Replicate noise floor” is not a statistically defined uncertainty measure

### What the code does

The adapter computes within-cell standard deviations with `numpy.std` at its default `ddof=0` ([`harness.py` lines 393–399](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/puckworks/harness.py#L393-L399)). The TDS-EY function then averages the three cell standard deviations and calls the result “noise” ([`harness.py` lines 437–458](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/puckworks/harness.py#L437-L458)). Result 1 turns that average into a “replicate noise floor” of about 0.22 EY points ([Draft lines 141–146](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/docs/PAPER_B_DRAFT.md#L141-L146)).

For the fixed TDS 1/2 central condition, the committed data yield:

| Grind level | n | Mean EY (%) | Population SD (points) | Sample SD (points) |
|---:|---:|---:|---:|---:|
| 1.4 | 3 | 18.267 | 0.451 | 0.552 |
| 1.7 | 6 | 19.381 | 0.145 | 0.159 |
| 2.0 | 3 | 19.622 | 0.058 | 0.071 |

The unweighted mean of the population SDs is about 0.218 points, which explains the manuscript’s number. But it is not a noise floor, confidence interval, standard error of a contrast, pooled variance estimate, measurement error model, or minimum detectable effect.

### Why this matters

The cells have unequal sample sizes and strongly unequal variances. Averaging SDs treats all cells equally despite different \(n\), and using population SD underestimates uncertainty for such small samples. More importantly, the scientific question is not whether a model prominence is less than the mean SD. It is whether the relevant contrast or curve feature is supported after accounting for replication, design structure, and uncertainty.

The raw middle-minus-higher-endpoint contrast is:

\[
19.381 - 19.622 = -0.241\ \text{EY points},
\]

so the observed central target is monotone without requiring a “below-noise-floor” argument. The uncertainty should support a confidence statement about the contrast or the fitted peak prominence, not a threshold comparison against an averaged SD.

### Required correction

Use one of the following:

- a replicate-level bootstrap of the middle-versus-endpoint contrast;
- a heteroskedastic regression or mixed model that respects the design and repeated center point;
- a bootstrap of the fitted RSM vertex and peak prominence;
- or, at minimum, sample SDs, standard errors, and confidence intervals for each contrast.

Until that is done, replace “below the replicate noise floor” with a descriptive statement such as:

> “The modeled prominence is small relative to the observed within-cell replicate variation, but no formal minimum-detectable-effect analysis has been performed.”

The Abstract should not include a noise-floor claim based on the current calculation.

---

## 3. Result 3 is not yet a defensible linear-stability analysis

### What is genuinely interesting

The N-tube construction asks a valuable question: if each heterogeneous path receives its own extraction-dependent conductance clock, does heterogeneity decay, remain bounded, or amplify? The tested near-choke poroelastic implementation shows severe transient flow concentration, whereas the auxiliary Kozeny–Carman implementation remains much more distributed. That is a useful exploratory model failure and a plausible motivation for physical lateral coupling.

### Why the present “linear instability” claim is unsupported

#### 3.1 The linearization is around a different state from the numerical experiment

The analytical function states that it linearizes around identical uniform tubes ([`harness.py` lines 945–966](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/puckworks/harness.py#L945-L966)). The actual N-tube experiment begins from a fixed lognormal permeability distribution. No Jacobian or tangent evolution is calculated along that heterogeneous trajectory.

A uniform-state analysis can be useful, but the manuscript must then distinguish:

- stability of the uniform solution,
- transient amplification around the heterogeneous base state,
- and nonlinear concentration in the finite-amplitude simulation.

They are currently blended into one claim.

#### 3.2 The reported \(A\approx 10^{12}\) is controlled by an imposed floor

The stability routine sorts conductance and clips it to a minimum of \(10^{-12}\) before computing \(A=M_f/M_0\) ([`harness.py` lines 967–980](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/puckworks/harness.py#L967-L980)). The near-choke initial conductance is effectively zero, so the enormous amplification is the ratio of a finite endpoint to an arbitrary numerical floor.

If \(M_0=0\) exactly, \(\log M\) and the proposed logarithmic linearization are singular. One cannot simultaneously invoke a zero-conductance base state and a conventional small-perturbation linearization without defining a regularized start time or a physically nonzero base conductance.

The correct object might be a **finite-time gain from a specified nonzero start time**, but then the gain must be reported as a function of:

- conductance floor or start time,
- initial porosity offset,
- pressure,
- closure slope,
- and extraction-clock convention.

#### 3.3 The “stable” threshold is imposed, not derived

The code defines `unstable = A > 1e2` ([`harness.py` line 979](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/puckworks/harness.py#L979)). Kozeny–Carman gives \(A\approx 1.5\), which is still amplification, but is called stable because it is below the arbitrary 100× threshold. A stability theorem requires a criterion based on eigenvalues, Lyapunov exponents, boundedness, or asymptotic behavior—not a chosen magnitude cutoff.

If the intended result is practical rather than asymptotic, call it a **finite-horizon amplification classification** and state the operational threshold and its rationale.

#### 3.4 The lateral term is a numerical homogenizer, not pressure equalization

The implementation applies:

```python
w = (1.0 - lateral) * w + lateral
```

([`harness.py` lines 893–895](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/puckworks/harness.py#L893-L895)). This blends tube weights toward unity. It is not derived from a transverse pressure equation, neighboring-tube conductance, a shared pressure field, or Darcy exchange.

The simulation therefore shows that **imposed homogenization suppresses the positive feedback**. It does not establish that physical lateral pressure equalization has a threshold near \(\lambda=0.3\), nor that such coupling is necessary and sufficient in a real puck.

#### 3.5 The Figure 5 description does not match the code

The draft says Figure 5 is a phase map over “grind × lateral coupling × control mode” ([Draft lines 216–220](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/docs/PAPER_B_DRAFT.md#L216-L220)). The figure-generation code fixes:

- grind setting at 1.1,
- closure at poroelastic,
- \(N=120\),

and sweeps only lateral parameter and control mode ([`figures.py` lines 227–267](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/puckworks/figures.py#L227-L267)). There is no grind dimension in panel (a). The stability cross-check uses \(N=150\), while the default harness uses \(N=400\), creating an additional configuration mismatch.

### Required correction

Choose one of two paths.

#### Path A: exploratory numerical result

Use language such as:

> “The uncoupled flow-controlled model exhibits strong transient flow concentration from a near-zero-conductance initialization in the tested configuration. A finite-horizon conductance-ratio calculation explains the closure sensitivity and motivates a physically derived lateral-coupling model.”

Then:

- remove “linearly unstable,” “diverges,” and “closed-form stability criterion” from the Abstract and title;
- report maximum tube share, effective channel number, entropy/Gini, and mass conservation;
- show floor/start-time sensitivity;
- show \(N\), timestep, pressure, grind, and heterogeneity sensitivity;
- label the lateral parameter as a homogenizing proxy.

#### Path B: genuine stability analysis

Derive the full normalized-flow dynamical system and its Jacobian. Specify the base state, conservation constraint, mean-zero perturbation modes, control mode, and physical lateral-coupling operator. Analyze eigenvalues or finite-time Lyapunov exponents. Then confirm against nonlinear simulations over parameter sweeps. A physical lateral network should be based on adjacent pressure exchange or a transverse Darcy conductance, not direct mixing of weights.

Until one of these is completed, Result 3 should be classified as **red/amber exploratory**, not a theorem-like result.

---

# Major scientific comments

## 4. The paper shifts among three different meanings of “the anomaly”

The manuscript refers to:

1. Cameron et al.’s fine-grind deviations from a homogeneous model, which are used to calibrate the streamtube closure;
2. Schmieder’s raw TDS-EY axis cells at fixed target conditions, which are monotone in the committed data;
3. Schmieder’s fitted response-surface curvature, which is weak and confounded by grinder dial, particle size, pressure, and achieved conditions.

These are not interchangeable observations.

The Introduction currently opens with the Cameron phenomenon, then Result 1 tests the model against the Schmieder target while the channeling closure was calibrated to Cameron. This creates a subtle circularity: the channeling model’s ability to generate a fine-grind departure is partly built from the Cameron departures, while its “external” target is a weak Schmieder smooth whose absolute reconstruction is currently mishandled.

The paper should define the three objects explicitly, perhaps in a table:

| Object | Observable | Dataset | Role |
|---|---|---|---|
| Cameron deviation | EY residual from homogeneous model vs EK43 dial | Cameron et al. | Calibration source for \(\sigma(g)\) |
| Schmieder raw axis cells | TDS-derived EY at specified central condition | Schmieder et al. | Matched-observable empirical check |
| Schmieder RSM shape | Fitted cup-mass surface vs flow, grind dial, temperature | Schmieder et al. | Qualitative smooth/shape, subject to fit uncertainty |

Then use “Cameron fine-grind deviation,” “Schmieder raw TDS response,” and “Schmieder RSM curvature,” rather than a single “observed response” or “anomaly.”

The paper should also emphasize that the Schmieder middle dial is finest by the reported Sauter diameter, but the dial-to-size mapping is non-monotonic and pressure changes with grind. The source paper itself discusses the difficulty of separating particle-size and pressure effects. A dial-axis interior maximum cannot be interpreted as a universal particle-size instability without a portable physical grind variable.

---

## 5. The mechanism comparison is asymmetric

The evidence matrix is preferable to the original winner scoreboard, but the prose still says static heterogeneity is “the only viable” implemented generator ([Draft lines 147–150](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/docs/PAPER_B_DRAFT.md#L147-L150)). The competitors are not being tested on equal terms:

- The static channeling closure is empirically calibrated to Cameron’s grind deviations.
- The Lee branch is evaluated at a measured ceiling and a deliberately doubled ceiling, with the latter called “doctored” in code ([`harness.py` lines 536–557](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/puckworks/harness.py#L536-L557)).
- The size-exclusion model supplies a different observable—extractable inventory rather than TDS-EY shape.
- The diffusion branch is a null, not a comparably calibrated alternative.
- Incomplete wetting, a central competing hypothesis, is not implemented.

This is a useful **model-availability and model-capacity audit**, not a symmetric head-to-head mechanism experiment.

Recommended wording:

> “Among the response generators currently implemented in the registry, the calibrated static-heterogeneity branch generates an interior maximum under the tested settings without altering a source parameter. The comparison does not identify channeling, because competitor maturity, calibration, and observables differ, and incomplete wetting is not yet represented.”

Remove “doctored” from manuscript-facing language. Use “deliberately doubled for a sensitivity test” or “outside the measured value.” Loaded labels weaken the appearance of neutral discrimination.

A stronger evidence matrix should include:

- implementation status,
- calibration data,
- evaluation data,
- observable produced,
- free parameters,
- whether the tested feature is fitted or predicted,
- validation strength,
- and the unresolved experiment that would discriminate it.

---

## 6. “Present in 40% of the parameter grid” is not a robustness probability

The sensitivity routine uses five hand-selected values of `s_ref` and five of exponent `m`, giving 25 equally weighted combinations ([`harness.py` lines 592–675](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/puckworks/harness.py#L592-L675)). The resulting fraction of grid points with an interior argmax is descriptive. It is not:

- a probability that the mechanism is correct,
- a posterior probability of a peak,
- a robustness confidence level,
- or a measure invariant to range, spacing, or parameterization.

A rectangular grid in \((s_{ref},m)\) gives a different fraction from a grid in log-parameters or in physically induced quantities. The “median prominence” is also computed only among cases that already have an interior maximum, which conditions on the outcome and can make the effect appear larger.

Required changes:

- Report the literal result: “10 of 25 pre-specified combinations,” if that is the exact count.
- Justify the parameter bounds from calibration uncertainty or external data.
- Plot a phase boundary or full heat map rather than reducing it to a percentage.
- Include all cases when summarizing prominence, with zero or negative prominence for non-interior cases.
- Test alternative closure forms, uncertainty in fines fraction, pressure, quadrature nodes, spline grid, and the mapping between grinder dial and physical grind.
- If a probability statement is desired, define priors or a bootstrap distribution and propagate calibration uncertainty.

“Fragile over the selected sensitivity rectangle” is defensible. “Present in ~40% of its parameter grid” should not appear in the Abstract without this qualification.

---

## 7. The Jensen/concavity mechanism is asserted, not demonstrated for the numerical response

The streamtube model constructs an empirical numerical map by:

1. solving the homogeneous model over \(k\in[0.02,8]\),
2. using pressure \(p\,k\),
3. scaling target output mass as \(m_{out}k\),
4. interpolating EY against \(\log k\) with PCHIP,
5. clipping outside the support,
6. and averaging over a unit-mean lognormal distribution

([`streamtube.py` lines 77–119](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/puckworks/models/brewer2026/streamtube.py#L77-L119)).

The manuscript then states that EY is concave in permeability and invokes Jensen’s inequality ([Draft lines 124–128](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/docs/PAPER_B_DRAFT.md#L124-L128)). No analytical concavity proof or numerical second-derivative audit is included at the pinned revision.

This matters because PCHIP is shape-preserving but does not guarantee global concavity, clipping can alter ensemble behavior, and the model varies pressure and delivered mass together rather than changing permeability inside one fixed-control problem.

Required additions:

- Plot \(EY(k)\), \(dEY/d\log k\), and the numerical second derivative over the quadrature support for every grind and pressure used.
- Report the fraction of lognormal quadrature mass that reaches the clipped boundaries.
- Demonstrate convergence with `k_min`, `k_max`, number of grid points, and Gauss–Hermite nodes.
- Explain physically why `p_bar*k` and `m_out*k` represent a permeability streamtube under the chosen control mode.
- If concavity is local rather than global, state the tested range explicitly.

Until then, say:

> “The sampled numerical response is concave over the tested support, so the lognormal averaging produces a Jensen-type yield deficit.”

Do not present global concavity as an established property without showing it.

---

## 8. Result 2 supports discrimination within a specified model set, not a universal causal requirement

### 8.1 The Foster null is useful but comes from a different setting

The machine-only reconstruction shows that a dip-and-recovery shape can arise without bed dynamics. That is an excellent null. But “carries no evidential weight for any bed-side story on its own” is too absolute ([Draft lines 154–160](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/docs/PAPER_B_DRAFT.md#L154-L160)). The null demonstrates non-uniqueness of the qualitative shape under one machine model and source trace. It does not show that the shape contains zero information in every experimental design.

Suggested wording:

> “The dip-and-recovery shape is not, by itself, diagnostic of a bed mechanism because the tested machine-only model can reconstruct it in the source configuration.”

### 8.2 “Time-varying bed mechanism required” must be scoped to the tested baselines and window

At 9 bar, the time-varying empirical trajectory beats constant and static-pressure baselines. The correct claim is:

> “Within the 15–95 s evaluation window and the specified null set, a time-varying bed term is needed to improve the reconstruction.”

This does not establish that no other machine model, viscosity model, sensor model, or untested temporal mechanism can explain the residual. Report parameter count, calibration status, residual autocorrelation, and uncertainty—not only RMSE.

### 8.3 The empirical \(\Phi(t)\) branch has soft circularity

The porosity trajectory is linked to dissolved mass derived from the same experimental campaign’s TDS and flow. Its fit is therefore a within-rig reconstruction, not independent mechanism validation. The manuscript acknowledges this, but “parameter-free” language can still mislead because donor parameters were estimated elsewhere and the empirical trajectory carries information from the target rig.

### 8.4 “Out of sample” overstates the cross-pressure design

The cross-pressure harness uses the published static calibration from the same eleven-pressure campaign and treats all pressures other than 9 bar as out of sample ([`harness.py` lines 741–808](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/puckworks/harness.py#L741-L808)). This is better described as:

> “held-out pressure traces conditional on campaign-wide calibrated constants.”

It is not fully independent out-of-sample validation. A stronger test would use:

- leave-one-pressure-out refitting of every estimated constant;
- a predeclared train/validation split;
- a second rig or coffee;
- or a hierarchical model that estimates transfer uncertainty.

The current code also rounds each per-pressure RMSE to three decimals before calculating aggregate means. Aggregation should use full-precision residuals and round only at presentation.

### 8.5 Regime definitions should be predeclared

The low-pressure and mid-pressure groups are coded after the per-pressure results. If these bins were selected after seeing the curves, they are descriptive, not confirmatory. State the physical basis for the thresholds or present the full pressure-residual curves without categorical winner language.

### 8.6 The comparison covers three implemented branches, not all plausible mechanisms

“No universal winner” is valid only among the static, empirical dissolution-linked, and Cameron-coupled variants that were run. Migration, compaction, swelling under matched control conditions, viscosity changes, and sensor/machine uncertainty remain outside the comparison.

---

## 9. The failed swelling composition is useful, but the causal diagnosis is too strong

The draft states that the parameter-free swelling branch “does not apply to the saturated pre-wet rig” ([Draft lines 181–186](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/docs/PAPER_B_DRAFT.md#L181-L186)). The simulation establishes that this particular transferred branch, under this shared-porosity composition, worsens the 9-bar fit. It does not isolate why.

Plausible alternatives include:

- control-regime mismatch,
- initial-condition mismatch,
- different coffee or grind structure,
- donor parameter non-transferability,
- timescale mismatch,
- incorrect additivity in shared porosity,
- or an omitted interaction between swelling and extraction.

Recommended wording:

> “The imported swelling parameterization is incompatible with the observed 9-bar trajectory under the tested shared-porosity composition; the calculation does not distinguish control-regime, parameter-transfer, initial-condition, or composition-form errors.”

That negative result is scientifically stronger when it does not overdiagnose the cause.

---

## 10. Methods are not yet sufficient for a manuscript

The registry architecture is a useful organizing device, but “code is the specification” is not an acceptable substitute for conventional Methods. The manuscript needs enough written detail for a reader to understand and independently reproduce each comparison without reverse-engineering Python.

At minimum add:

### Data and preprocessing

- exact source versions and licenses;
- inclusion/exclusion criteria;
- target versus achieved flow and temperature;
- pressure definitions and sensor node;
- how repeated center points are handled;
- missing-data treatment;
- unit conversions and dose normalization;
- observable schemas and validation checks.

### Model equations and controls

- homogeneous extraction equations;
- streamtube distribution and normalization;
- exact definition of \(k\), \(\sigma\), and the grind closure;
- conductance/porosity equations for Result 2;
- N-tube update equations for both flow and pressure control;
- definitions of \(M\), \(\Phi\), \(\lambda\), flow shares, and effective channel count.

### Calibration and evaluation

- every fitted parameter and its calibration data;
- whether each reported feature is fitted, reconstructed, interpolated, or predicted;
- train/evaluation separation;
- parameter uncertainty;
- the status of donor parameters transferred across rigs.

### Numerical methods

- solver tolerances and grids;
- interpolation and clipping;
- timestep and tube-count convergence;
- random-seed or deterministic quadrature details;
- exact figure-generation functions and settings.

### Statistical methods

- replicate model;
- uncertainty intervals;
- peak/vertex inference;
- residual correlation and heteroskedasticity;
- multiple comparisons or model-selection method if winner language is retained.

### Reproducibility

- pinned commit or DOI archive;
- Python and dependency versions;
- commands to regenerate every figure/table;
- data/code availability statement;
- distinction between QUICK regression gates and slow scientific analyses.

There is also an internal contradiction: the Abstract says each candidate is “independently gated” ([Draft lines 19–23](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/docs/PAPER_B_DRAFT.md#L19-L23)), while the Methods correctly state that the static streamtube carries no gate ([Draft lines 90–94](https://github.com/trbrewer/puckworks/blob/803260f65d60d99f39b9cffb86e01a252d0e3d20/docs/PAPER_B_DRAFT.md#L90-L94)). The Abstract must be corrected.

A defensible formulation is:

> “Components carry explicit provenance, assumptions, and validity ranges; where available, named gates record evidence ranging from numerical verification to independent experimental comparison.”

---

# Section-by-section comments

## Title

Current title:

> *Mechanism discrimination for the fine-grind espresso extraction anomaly, and a stability test of uncoupled streamtube models.*

The first clause is defensible after correcting Result 1. The second is premature because the present calculation is not yet a valid stability test. Also, the paper’s three results do not all analyze the same “fine-grind anomaly.”

Recommended options:

1. **What integrated espresso measurements can—and cannot—identify: model-capacity tests for grind and flow dynamics**
2. **Model-capacity tests for grind-dependent espresso extraction and time-evolving flow**
3. **Mechanism discrimination in espresso flow and extraction: matched observables, null models, and transient streamtube concentration**

If a formal Jacobian/eigenmode analysis is completed, a stability-focused title can be reconsidered.

## Abstract

The Abstract is conceptually dense and currently stacks distinct evidence levels as if they were coequal. It contains too many methodological caveats and too many numerical conclusions for a journal abstract. The following statements must change:

- “each candidate mechanism is … independently gated” — contradicted by Methods;
- “RSM over-predicts … ~1.7×” — invalid rounded-coefficient interpretation;
- “present in ~40%” — arbitrary sensitivity rectangle, not robustness probability;
- “below the measurement noise floor” — no inferential definition;
- “linearly unstable” and “closed-form analysis” — not established under the current singular/floored formulation;
- “instability disappears … with lateral coupling” — only a numerical homogenizer has been tested.

Reduce the Abstract to the valid hierarchy:

1. matched-observable correction;
2. raw TDS response is monotone at the central condition;
3. calibrated static heterogeneity can generate an interior maximum but does not identify channeling;
4. temporal models outperform specified flat baselines with pressure-dependent performance;
5. an exploratory uncoupled near-choke composition exhibits transient concentration and motivates spatial measurements/physical coupling.

## Introduction

The Introduction is strongest when it identifies the grinder-dial and pressure confounds. Add a concise account of what Cameron measured versus what Schmieder measured. Do not claim no prior head-to-head comparison until a conventional related-work search supports that novelty statement.

The Introduction should also state the paper’s research questions explicitly:

1. What does the corrected empirical target actually show?
2. Which implemented model classes can produce that response under their registered parameterizations?
3. What temporal structure is needed to beat specified nulls on flow traces?
4. What failure appears when static heterogeneity and evolving conductance are composed?

These questions are clearer and more defensible than a single causal narrative.

## Methods

The conceptual Methods section is good but too brief. Add equations, data contracts, calibration splits, and statistical methods as described above. The “corrected adapter refuses to aggregate” wording should be made precise: the function requires explicit component/brew-ratio/temperature/flow arguments and checks that selected units are unique; it does not implement a universal schema validator across every field. Add automated assertions for:

- one component,
- one unit,
- one brew ratio,
- one target temperature,
- one target flow,
- expected grind support,
- nonmissing dose and unit basis,
- duplicate experimental IDs,
- and target-versus-achieved condition fields.

## Result 1

The raw TDS-EY result is a clean negative finding and should lead the section. Remove the coefficient-overprediction discussion or replace it with a precision warning. Then separate:

- empirical target,
- model-capacity comparison,
- and calibration/sensitivity limitations.

Do not call the static branch “the only viable” mechanism. It is the only currently implemented branch that generates an interior maximum under the selected comparison without altering a source parameter. That is narrower but still useful.

Add formal uncertainty on the raw contrasts and the fitted vertex. Show model magnitude as well as shape. The sensitivity figure should display the full response surface over parameters rather than a single 40% statistic.

## Result 2

Retain the null-first structure. It is one of the draft’s best ideas. Tighten every verb to the evidence:

- machine-only **reconstructs** a source flow minimum;
- empirical \(\Phi(t)\) **reconstructs** the 9-bar rise better than specified flat baselines;
- cross-pressure performance is **within-rig generalization** conditional on campaign calibration;
- no branch **dominates the tested set** across all pressures.

Add uncertainty, residual plots, and parameter-complexity comparisons. Report full-precision aggregate RMSE. Explain the pressure regimes physically or remove winner-by-bin claims.

## Result 3

Reframe as an exploratory model-composition failure unless the formal analysis is rebuilt. The direct diagnostics—maximum tube share and effective number of channels—are improvements over the earlier top-decile metric. Keep them. But remove theorem-like claims until the singular initial state, arbitrary floor, physical lateral operator, and base-state mismatch are resolved.

A publishable exploratory section would ask:

> “Does an uncoupled streamtube extension preserve bounded heterogeneity when conductance evolves?”

The answer can be:

> “Not in the tested flow-controlled near-choke configuration; the model concentrates flow strongly, revealing that the independent-tube composition is structurally unsafe without additional physics.”

That is an interesting negative result and does not require claiming physical instability.

## Discussion

The observability theme should become the center of the Discussion and perhaps the paper. Distinguish what is measured from what is simulated. The N-tube result motivates spatial observables; it does not provide experimental evidence that real pucks evolve into one channel.

The practitioner-facing statement should remain cautious:

> “Static flow heterogeneity remains a plausible generator of the fine-grind response, but the available integrated measurements do not identify it uniquely.”

Do not claim a physical flow-control/pressure-control distinction until both modes are analyzed under a physically consistent machine/bed system and tested experimentally.

## Open gaps

The listed gaps are appropriate. Add:

- full-precision response-surface reconstruction or raw-data refit protocol;
- direct spatial flow/saturation data;
- a second-rig/coffee transfer dataset;
- a physically derived lateral network;
- and parameter-identifiability analysis for the temporal branches.

## Internal status block

Remove lines 261–268 from the manuscript. “All gated/committed” is repository project management, not evidence of scientific readiness. In particular, the current review finds that Results 1 and 3 need substantive recomputation, not only related work and LaTeX.

---

# Figure review

## Figure 1 — corrected target and static model capacity

Recommended structure:

- **Panel A:** raw replicate-level TDS-EY points at a clearly specified fixed condition, with sample means and confidence intervals;
- **Panel B:** source or repository-refit RSM curve with a bootstrap band and explicit note that printed coefficients are rounded;
- **Panel C:** homogeneous versus static-heterogeneity model response, normalized if dial spaces differ;
- **Panel D:** model prominence versus empirical contrast with uncertainty.

Do not overlay mixed-unit component masses or imply the source fit is 6.7 g.

## Figure 2 — mechanism evidence matrix

This should replace binary “winner” logic. Include:

- observable,
- implementation status,
- calibration source,
- free parameters,
- predicted shape,
- evidence strength,
- and decisive missing experiment.

Use neutral language. “Outside measured parameter value” is preferable to “doctored.”

## Figure 3 — null ladder and pressure transfer

Separate three concepts visually:

1. Foster machine-only source reconstruction;
2. Waszkiewicz 9-bar within-rig ladder;
3. pressure-by-mechanism residual curves or heat map.

Show error bands or residual uncertainty. Avoid one bar chart that makes post-fit reconstruction and held-out pressure comparison look like the same validation class.

## Figure 4 — failed composition diagnostic

This is valuable. Show:

- observed trace,
- flat baseline,
- extraction-only shared-porosity branch,
- extraction-plus-swelling branch,
- porosity trajectories,
- and residuals.

Change “A diagnosed mis-scale” to “an incompatibility under the tested transfer and composition.” The current result does not uniquely diagnose the source of failure.

## Figure 5 — transient concentration, not a phase diagram

The current code does not generate a grind × lateral × control phase map. Either:

- rename panel (a) to “effective channel count versus homogenization parameter at fixed grind,” or
- actually sweep grind and closure slope to produce a phase diagram.

A publication-grade stability/concentration figure should include:

- floor/start-time sensitivity;
- flow and pressure control;
- physical or proxy coupling clearly labeled;
- maximum tube share and effective channel number;
- \(N\) convergence;
- timestep convergence;
- pressure and grind sweeps;
- and, if a stability claim is retained, eigenvalue or finite-time Lyapunov results.

Do not draw an “instability threshold” at \(A=100\) unless it is explicitly defined as an operational plotting threshold rather than a mathematical criterion.

---

# Required additional analyses

## Priority 1 — repair the Schmieder response-surface analysis

1. Request or recover full-precision source coefficients/model files.
2. Reproduce source Figure 4 numerically.
3. If unavailable, define a repository refit using experiment-level means and achieved conditions.
4. Report coefficients with sufficient precision, covariance, adjusted \(R^2\), residuals, and bootstrap vertex/peak prominence.
5. Compare raw-cell and fitted-curve conclusions without evaluating rounded coefficients as exact.

## Priority 2 — replace the noise-floor heuristic

1. Preserve replicate-level data.
2. Estimate contrast uncertainty with a heteroskedastic model or bootstrap.
3. Report confidence intervals for the raw middle-versus-endpoint contrast.
4. Propagate calibration uncertainty into model prominence.
5. Estimate a minimum detectable effect only if the experimental-error model justifies one.

## Priority 3 — make the static-channeling capacity test auditable

1. Demonstrate numerical concavity over the actual quadrature support.
2. Report clipping probability and quadrature convergence.
3. Quantify closure calibration uncertainty.
4. Test alternative closure families.
5. Show phase boundaries rather than an arbitrary grid fraction.
6. Distinguish interpolation within Cameron’s three deviation points from external prediction.

## Priority 4 — strengthen Result 2 validation

1. Use full-precision residual aggregation.
2. Report residual time series and autocorrelation.
3. Include parameter counts and calibration provenance.
4. Perform leave-one-pressure-out calibration or use a second campaign.
5. Predeclare pressure regimes or show continuous performance curves.
6. Add sensitivity to the 15–95 s window.

## Priority 5 — rebuild or downgrade Result 3

For an exploratory result:

- specify a nonzero start time;
- sweep floor/start state;
- report finite-time gain rather than “linear instability”;
- run \(N\), timestep, pressure, grind, \(\sigma\), and closure-slope sweeps;
- label the lateral term as a proxy.

For a formal result:

- derive the normalized dynamical system;
- construct a physical lateral exchange operator;
- calculate the Jacobian/eigenmodes or finite-time Lyapunov spectrum;
- prove or numerically map stability boundaries;
- verify against nonlinear simulations.

## Priority 6 — complete manuscript standards

- related work;
- full references;
- conventional Methods;
- uncertainty/statistics;
- limitations;
- Data and Code Availability;
- exact software release and environment;
- figure/table regeneration commands.

---

# Recommended revision sequence

1. **Delete or suspend the 1.7× RSM claim.** Reconstruct the RSM correctly before revising any title or Abstract language.
2. **Replace “noise floor” with formal replicate-level inference.**
3. **Rewrite Result 1 as a matched-observable negative result plus a calibrated model-capacity test.**
4. **Make the mechanism matrix symmetric in what it reports, not falsely symmetric in evidence maturity.**
5. **Reframe Result 2 around specified nulls, within-rig reconstruction, and conditional pressure transfer.**
6. **Downgrade Result 3 to transient numerical concentration or perform a genuine stability analysis.**
7. **Correct Figure 5’s scope and regenerate all figures only after the analyses are fixed.**
8. **Rewrite title, Abstract, Introduction, and Discussion around observability and model-hierarchy limits.**
9. **Complete Methods, related work, uncertainty, references, and reproducibility package.**

The internal statement that Results 1–3 are ready and need only writing/polish should be removed. Result 1 requires a corrected response-surface analysis; Result 2 needs a more rigorous validation protocol; Result 3 requires either substantial new analysis or explicit downgrading.

---

# Recommended revised thesis

> We use a registry-based, null-first hierarchy to test what current espresso measurements can distinguish. Enforcing a matched TDS-yield observable removes an earlier mixed-unit target and shows that the raw central grind response is monotone. A calibrated static-heterogeneity model can generate an interior maximum, but the available data and calibration structure do not identify channeling. Across pressure traces, time-varying bed models outperform specified flat baselines with regime-dependent within-rig transfer, rather than yielding a universal mechanism winner. An exploratory uncoupled streamtube composition exhibits strong transient flow concentration near a conductance shutoff, exposing a model-composition failure and motivating spatial measurements and physically derived lateral coupling.

This preserves the repository’s genuine contributions:

- transparent model comparison,
- observable discipline,
- null-first reasoning,
- informative negative results,
- and discovery of unsafe model compositions,

without claiming more causal identification or mathematical stability than the evidence supports.

---

# Suggested revised abstract

Espresso measurements integrate flow, extraction, and bed evolution in ways that can make distinct mechanisms observationally similar. We use a provenance-tracked model registry and a null-first comparison hierarchy to test what current data can distinguish. First, we correct a mixed-observable aggregation in which milligram solute masses and gram total-dissolved-solids values had been combined across brew ratios. At a fixed central condition, the resulting TDS-derived extraction-yield response is monotone across the three grind settings. A calibrated static-heterogeneity streamtube model can generate an interior maximum over part of its parameter range, but this is a model-capacity result rather than causal identification because the closure is grind-calibrated and incomplete wetting remains unmodeled. Second, on rising-flow traces, a machine-only model shows that a dip-and-recovery shape is not diagnostic of bed dynamics, while an empirical time-varying porosity branch reconstructs the 9-bar trace better than specified flat baselines. Performance across pressure is regime-dependent within the same experimental campaign. Finally, an exploratory uncoupled streamtube extension with extraction-dependent conductance exhibits strong transient flow concentration in a tested near-choke, flow-controlled configuration; the result motivates a physical lateral-exchange model but does not yet establish a universal instability criterion. The common conclusion is that integrated observables are insufficient for unique mechanism identification and that spatial, pathway-resolved, or first-drip measurements are needed.

---

# Bottom line

`PAPER_B_DRAFT.md` is a promising **major-revision manuscript**, not a paper awaiting only related work and LaTeX. Its most defensible and novel story is methodological: matched observables, explicit validation tiers, null-first mechanism tests, and the discovery that plausible model branches can fail when composed. The strongest immediate action is to repair the Schmieder response-surface analysis. Until that is done, the Abstract’s absolute-overprediction claim and much of Result 1 are not reliable. The next action is to either rebuild Result 3 as a real stability analysis or present it honestly as an exploratory transient-concentration failure.

With those corrections, a coherent paper is possible. Without them, the manuscript’s headline claims exceed what the repository and primary data currently support.

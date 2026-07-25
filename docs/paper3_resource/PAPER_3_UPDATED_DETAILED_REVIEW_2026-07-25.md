# Updated Detailed Review of PAPER 3

## Change audit and full-manuscript status after PR #175

### Manuscript reviewed

**Title:** *Puckworks: an executable, provenance-aware evidence registry for espresso process models*  
**Repository:** [`trbrewer/puckworks`](https://github.com/trbrewer/puckworks)  
**Review date:** 25 July 2026  
**Previous review boundary:** [`93358f8e4d7d5c214470d82195d852f455651ff9`](https://github.com/trbrewer/puckworks/commit/93358f8e4d7d5c214470d82195d852f455651ff9)  
**Change commit:** [`0c414bc57bb1995585e7cc0a2176fe8e76c09b42`](https://github.com/trbrewer/puckworks/commit/0c414bc57bb1995585e7cc0a2176fe8e76c09b42)  
**Merge/audit boundary:** [`b8c84be3170dc644ef5d15036e9698214896842f`](https://github.com/trbrewer/puckworks/commit/b8c84be3170dc644ef5d15036e9698214896842f)  
**Pull request:** [#175 — gate-4 two-regime does-not-port](https://github.com/trbrewer/puckworks/pull/175)  
**Manuscript file:** [`docs/PAPER_3_PUCKWORKS_DRAFT.md`](https://github.com/trbrewer/puckworks/blob/b8c84be3170dc644ef5d15036e9698214896842f/docs/PAPER_3_PUCKWORKS_DRAFT.md)  
**Recommendation on the change:** **Request substantive revision before retaining the new paragraph as a manuscript result**  
**Recommendation on Paper 3 overall:** **Major revision before preprint circulation or journal submission**

This document supersedes the review dated 25 July 2026. It is written as a standalone review: it evaluates the newly merged change in detail, records which earlier comments have or have not been addressed, and restates the remaining full-manuscript blockers.

---

## 1. Executive assessment

The revision adds a valuable idea to Paper 3: a shared *fast-then-slow* curve shape does not establish that fitted fast and slow constants represent the same physical quantities in different models. That argument is highly relevant to the manuscript's central thesis. It advances the discussion from a relatively straightforward naming problem—two models using different definitions of a “fast fraction”—to a deeper identifiability and composition problem: even the same empirical functional form can summarize different mechanisms and therefore produce coefficients that are not physically portable.

The scientific idea should be retained. The present wording, however, is not yet sufficiently accurate or traceable for publication. The new paragraph makes four material overstatements:

1. **It says the Roman-Corrochano fast and slow constants are grind-independent.** Only the fitted *shape quantities*—the weight and the slow/fast ratio—are invariant under the fixed dimensionless protocol. The absolute fitted constants vary with effective diffusivity and change by almost a factor of two across the seven grinds.
2. **It presents the Roman-Corrochano timescale mismatch as a general property of that model at “its own particle size.”** The computation uses only a selected 20 μm-radius fine class. The registered model also contains a coarse class, whose size is not available in the repository. Because diffusion time scales as radius squared, plausible larger radii move the fitted constants into the Maille ranges. The absolute-range result is therefore fine-class- and configuration-specific, not a universal non-portability result for the Roman-Corrochano model.
3. **It says the Cameron flowing-bed response is effectively one-regime without qualification.** Three of the four simulated curves are single-exponential-like and have degenerate bi-exponential fits. The coarsest setting returns approximately 23.6 s and 40.0 s, and an independent reviewer model-selection check strongly favors the two-constant fit for that setting. The robust repository-supported statement is that no fitted Cameron “fast” constant lies in Maille's pooled fast range—not that all Cameron cases collapse to one scale.
4. **It does not state in the manuscript that these are model-generated, protocol-dependent, qualitative comparisons.** Those caveats appear in the analysis code and model card but not in the new paragraph. The paragraph also omits the model names, references, fitting conditions, uncertainty/identifiability information, and a manuscript claim record.

There is an additional terminology problem: the Roman-Corrochano result is described as the signature of a “single diffusion mode.” A spherical diffusion solution is generally represented by multiple mathematical eigenmodes. What is single is the **physical diffusion mechanism and selected particle/species configuration**, not necessarily the mathematical mode. “One diffusion process” or “one physical particle population under one diffusional mechanism” would be safer and more accurate.

The change was explicitly merged as a docs-only narrative propagation with no evidence-graph change. That is understandable as repository workflow, but it conflicts with Paper 3's own proposed standard: manuscript-facing numerical conclusions should have named producers, result records, input/configuration metadata, caveats, source commits, and generated tables or figures. A central Paper 3 claim should not be exempt from the architecture that Paper 3 advocates.

None of the major submission blockers identified in the previous review has been resolved by this change. The manuscript still reports stale component and manifest counts, describes an outdated registry schema, overstates the named-shot infiltration evidence, contains an obsolete readiness table, lacks completed figures and a rigorous related-work section, and does not evaluate the framework itself. The added paragraph increases the draft from 9,923 to 10,178 whitespace-delimited words, slightly worsening the unresolved venue/length problem.

My recommendation remains positive in principle and firm in execution: **keep the conceptual contribution, rewrite and properly evidence the new result, and continue with major revision of the full paper.**

---

## 2. Exact scope of the update

The Paper 3 manuscript changed narrowly between the previous review snapshot and the merge snapshot:

| Metric | Previous audit snapshot | Updated snapshot | Change |
|---|---:|---:|---:|
| Bytes | 72,141 | 73,789 | +1,648 |
| Physical lines | 617 | 619 | +2 |
| Whitespace-delimited words | 9,923 | 10,178 | +255 |
| SHA-256 | `7191b743e98fa571347e24c4c13b1868da6f8bd9f16c66523893429e4883a430` | `fe453e2a9ec4b6379a41c48123b65e3b4a6908c5f54834f4351565ea88b497b3` | changed |

The only substantive Paper 3 insertion is a single paragraph in §4.5, immediately after the comparison of alternative “fast fraction” definitions. It argues that:

- Maille, Cameron, and Roman-Corrochano can all be described using fast/slow language;
- Maille's empirical bi-exponential form collapses to one timescale when fitted to the Cameron curve;
- the same form fits the Roman-Corrochano curve with a fixed ratio and grind-independent constants, but at timescales far from Maille's range; and
- a visually good common functional form does not make the fitted coefficients physically commensurate.

PR #175 also propagated the same idea into a public-value narrative and planning documents. The PR states that the change is docs-only, makes no model or evidence promotion, and does not modify the evidence graph.

### Reviewer interpretation of the change

| Dimension | Assessment |
|---|---|
| Conceptual relevance | **Strong.** Directly advances Paper 3's core observable-semantics argument. |
| Placement | **Reasonable but over-dense.** A concise semantic conclusion belongs in §4.5; the methods and quantitative result need a dedicated subsection, table, figure, or supplement. |
| Scientific status | **Qualitative, model-to-model, protocol-dependent.** Not validation and not an empirical cross-rig test. |
| Current wording accuracy | **Requires correction.** Roman grind independence and Cameron single-regime language are overstated. |
| Traceability | **Insufficient for Paper 3's own standard.** No Paper 3 evidence-matrix/claim-record propagation and no generated result table in the manuscript. |
| Effect on prior review | **No previous major comment fully resolved.** The update adds a useful example but introduces new quantitative-reporting obligations. |

---

## 3. Strengths of the new material

### 3.1 It is a better example than a mere unit mismatch

The manuscript already explains why common labels such as pressure, saturation, concentration, inventory, and fast fraction can conceal different meanings. The new example goes further. It shows that **the same mathematical fitting form can conceal different physical meanings**, even where units and curve appearance agree. That is a sophisticated and publication-worthy point.

### 3.2 It supports the argument against premature mega-model composition

A modeler can easily be tempted to take a fitted `lambda_fast` from one model and feed it into another because the receiving model also has a fast exponential. The new analysis correctly warns that this can be a category error. Parameter names and functional forms are not interfaces unless the observables, conditioning variables, mechanisms, and estimation procedures are commensurate.

### 3.3 It illustrates why high goodness-of-fit is insufficient

The Roman-Corrochano simulated curve is fitted extremely well by the imposed two-exponential form. Yet a high coefficient of determination alone does not establish that the two fitted constants correspond to Maille's two physical pools. This is exactly the kind of inferential restraint Paper 3 should demonstrate.

### 3.4 It links model semantics to identifiability

The Cameron result exposes an important additional issue: when the two constants coincide, the bi-exponential parameterization becomes non-identifiable because the mixture weight can cease to matter. This could become one of Paper 3's strongest concrete demonstrations if it is analyzed explicitly rather than summarized only through a fit and a heuristic flag.

### 3.5 The repository source material is more cautious than the manuscript paragraph

The analysis code and Maille model card disclose important limitations: the curves are model-generated; Cameron is extended to 400 s beyond its approximately 30 s validated recipe; Cameron has no well-mixed configuration; Roman uses one lumped medium-molecular-weight species and only the fine class; and the result is qualitative rather than validation. Those caveats provide a sound basis for a corrected manuscript version.

---

## 4. Change-specific major comments

## Major comment U1 — Name and cite the three models

The new paragraph refers to “one batch model,” “a second model,” and “a third model.” This obscures the evidence chain and conflicts with the manuscript's central commitment to provenance and typed model identity. A reader cannot determine from the paragraph which parameters, equations, datasets, or physical configurations are being compared.

The paragraph should explicitly identify:

- the Maille 2024 batch-extraction model and the exact equation being fitted;
- Cameron et al. 2020 and the `cameron2020.extraction_bdf` configuration; and
- Roman-Corrochano 2017 and the `romancorrochano2017.extraction` stirred-vessel configuration.

Cameron is already reference [6]. Maille and Roman-Corrochano are not currently present in the manuscript reference list and must be added. Internal model-card citations are not a substitute for primary-source references in the submitted paper.

### Required action

Add the model names and source citations at first mention. Provide either a compact comparison table in the main text or a supplementary method table containing the producer, configuration, fit equation, fit interval, normalization, species/particle class, parameter bounds, and evidence status.

---

## Major comment U2 — Correct the Roman-Corrochano “grind-independent constants” statement

The paragraph says that the Roman-Corrochano fit produces two constants that “are grind-independent and hold a fixed ratio.” This conflates absolute and dimensionless quantities.

The exact repository producer returns the following absolute fitted values for the selected 20 μm-radius, medium-molecular-weight configuration:

| Grind | Effective diffusivity (m² s⁻¹) | Fitted fast constant (s) | Fitted slow constant (s) | Slow/fast ratio | Fitted weight |
|---|---:|---:|---:|---:|---:|
| PsiA | 1.06×10⁻¹⁰ | 0.0288 | 0.3552 | 12.32 | 0.323 |
| PsiB | 8.50×10⁻¹¹ | 0.0359 | 0.4430 | 12.32 | 0.323 |
| PsiC | 8.20×10⁻¹¹ | 0.0373 | 0.4592 | 12.32 | 0.323 |
| PsiD | 7.10×10⁻¹¹ | 0.0430 | 0.5303 | 12.32 | 0.323 |
| PsiE | 7.30×10⁻¹¹ | 0.0419 | 0.5158 | 12.32 | 0.323 |
| PsiF | 6.30×10⁻¹¹ | 0.0485 | 0.5977 | 12.32 | 0.323 |
| PsiH | 5.50×10⁻¹¹ | 0.0556 | 0.6846 | 12.32 | 0.323 |

The absolute constants therefore vary by approximately 1.93× across the grind series. What is invariant under the fixed fitting protocol is the **dimensionless curve shape**: the fitted mixture weight and the ratio of the two fitted constants. This invariance is expected from nondimensional similarity when particle radius, bath ratio, species class, normalization, sampling, and fit window are fixed while the effective diffusivity only rescales time.

### Required replacement

Replace the claim with language such as:

> Under the fixed dimensionless fitting protocol, the fitted weight and slow/fast ratio are invariant across the seven diffusivity values, while both absolute constants scale with the diffusion time and therefore vary across grinds.

This distinction is central to the manuscript's own semantics argument. A paper about typed quantities should not describe a dimensionless shape invariance as absolute parameter invariance.

---

## Major comment U3 — Restrict the Roman-Corrochano absolute-timescale conclusion to the tested fine-class configuration

The paragraph says that the Roman-Corrochano constants fall two orders of magnitude away from the batch model's range “at that model's own particle size.” This wording implies that the calculation represents the model's particle-size domain generally. It does not.

The producer deliberately uses only:

- radius `R = 20 μm`, representing the approximately 40 μm-diameter fine class stated in the model card;
- one medium-molecular-weight species;
- 80 °C;
- a pore-to-bath ratio of 0.01;
- a time interval of 0–20 diffusion times; and
- normalization by the final value on that finite interval.

The Roman-Corrochano model also includes a coarse particle class at a reported `d[4,3]`, but that size is not available in the repository and was correctly not fabricated. Because the characteristic diffusion time scales as `R²/D_eff`, the missing coarse radius is not a minor nuisance. It controls the absolute timescale comparison.

A reviewer sensitivity calculation using the exact registered solver shows this directly. Holding the other protocol choices fixed:

| Radius | PsiA fast / slow (s) | PsiH fast / slow (s) | Relationship to Maille pooled bands |
|---:|---:|---:|---|
| 20 μm | 0.0288 / 0.355 | 0.0556 / 0.685 | both below |
| 100 μm | 0.721 / 8.88 | 1.389 / 17.11 | slow enters for PsiH |
| 125 μm | 1.126 / 13.88 | 2.170 / 26.74 | slow overlaps; PsiH fast is near the lower fast boundary |
| 150 μm | 1.622 / 19.98 | 3.125 / 38.51 | both overlap for PsiH |
| 175 μm | 2.207 / 27.20 | 4.254 / 52.41 | both overlap for both endpoint grinds |
| 200 μm | 2.883 / 35.52 | 5.556 / 68.46 | both overlap |
| 400 μm | 11.531 / 142.09 | 22.223 / 273.84 | PsiA both overlap; PsiH exceeds the fast/slow upper bands |

This sensitivity does **not** show that Roman-Corrochano and Maille are semantically commensurate. Their mechanisms and parameter meanings may still differ. It does show that the absolute-band miss at 20 μm cannot establish universal numerical non-portability for the full Roman-Corrochano model.

### Required action

State precisely:

> For the selected 20 μm-radius fine-class configuration, both fitted constants are sub-second and below Maille's pooled ranges. The coarse-class comparison remains unresolved because the corresponding particle size is not available in the repository.

The stronger and more defensible conclusion is semantic: a two-exponential approximation of a single diffusional mechanism does not inherit Maille's two-pool interpretation. The absolute-range mismatch is supporting evidence for one declared configuration, not the foundation of the general conclusion.

---

## Major comment U4 — Do not call the Roman-Corrochano response a “single diffusion mode”

The phrase “the intrinsic short- and long-time signature of a *single* diffusion mode” is potentially misleading. Spherical diffusion solutions are typically represented by a series of mathematical eigenmodes. The fitted two-exponential approximation can summarize early and late portions of one **physical diffusion process**, but it should not be described as proof of one mathematical mode.

The distinction matters because the paper is explicitly about semantic precision. Suggested alternatives are:

- “one physical diffusion mechanism in one selected particle/species class”; or
- “the early- and late-time behavior of a single-population diffusional release process.”

The paper may still contrast this with Maille's explicit geometric two-pool interpretation. That contrast is strong without the mathematically questionable “single mode” phrase.

---

## Major comment U5 — Qualify the Cameron “single-regime” conclusion

The exact producer returns:

| Cameron grinder setting | Fitted weight | Fast constant (s) | Slow constant (s) | R² | Repository `single_timescale` flag |
|---:|---:|---:|---:|---:|---|
| 1.0 | 0.562 | 31.52 | 31.52 | 0.9873 | true |
| 1.5 | 0.533 | 32.30 | 32.30 | 0.9952 | true |
| 2.0 | 0.626 | 28.13 | 28.13 | 0.9976 | true |
| 2.5 | 0.500 | 23.58 | 40.00 | 0.9996 | true |

The first three cases plainly collapse. The fourth does not: the constants differ by approximately 70% when measured relative to the smaller value, or 41% relative to the larger value. It is labelled `single_timescale=True` only because the implementation uses a permissive heuristic:

```python
abs(lambda_fast - lambda_slow) / lambda_slow < 0.5
```

That threshold is not a model-selection test and is not scientifically justified in the manuscript or card.

An independent reviewer fit comparison using the same 299 nonzero time points found:

| Grinder setting | One-exponential constant (s) | Best two-exponential constants (s) | ΔAICc, two minus one | ΔBIC, two minus one | Interpretation |
|---:|---:|---:|---:|---:|---|
| 1.0 | 31.523 | degenerate at approximately 31.523 | +4.07 | +11.40 | one exponential favored; bi-exponential parameters non-identifiable |
| 1.5 | 32.297 | degenerate at approximately 32.297 | +4.07 | +11.40 | one exponential favored; bi-exponential parameters non-identifiable |
| 2.0 | 28.125 | degenerate at approximately 28.125 | +4.07 | +11.40 | one exponential favored; bi-exponential parameters non-identifiable |
| 2.5 | 31.254 | approximately 23.582 and 40.006 | −235.94 | −228.60 | two-exponential fit strongly favored under this deterministic curve/noise treatment |

These information-criterion values are reviewer diagnostics, not committed Puckworks outputs, and should be reproduced in the project's locked environment before publication. They nevertheless demonstrate why the categorical manuscript statement is unsafe.

### Robust conclusion supported now

The following is supported by the registered producer:

- no Cameron fit places its nominal fast constant inside Maille's pooled 2.2–19.1 s fast range;
- the three finer settings collapse to a single-exponential-like response under the declared protocol; and
- the coarsest setting returns two separated constants and requires formal model selection/identifiability analysis before it can be called one-regime.

### Required action

Replace the universal “that model's flowing bed is effectively one-regime” statement with a setting-specific result. Replace the heuristic `single_timescale` gate with a declared model-comparison and parameter-identifiability criterion.

---

## Major comment U6 — Analyze parameter identifiability, not only goodness-of-fit

The paragraph correctly warns that a good fit can be misleading, but the current analysis does not yet perform the inferential work needed to support its strongest claims.

For the first three Cameron curves, the bi-exponential model is structurally degenerate when the constants coincide. The mixture weight becomes arbitrary, and a second nearly unused component can move across a broad range without materially changing the fitted curve. In multistart reviewer fits, near-optimal solutions spanned almost the full 0–1 weight range and very wide unused-timescale ranges. A high R² does not resolve this.

For Roman-Corrochano, the deterministic two-exponential approximation has a high R² and outperforms a one-exponential approximation under the selected grid and weighting. This demonstrates descriptive shape capacity, not that the two coefficients are unique physical quantities. Their values depend on the fitting window, normalization, weighting, finite-bath setup, and selected species/particle class.

### Required analysis

At minimum, the result bundle should report:

1. one- versus two-exponential model comparison using a declared criterion;
2. ordered constants to remove label switching;
3. multistart stability;
4. profile likelihoods or bootstrap intervals for the two constants and mixture weight;
5. parameter correlation or covariance-condition diagnostics;
6. sensitivity to time sampling and residual weighting;
7. residual plots rather than R² alone; and
8. a predeclared rule for “single-timescale-like,” “two-timescale-shaped,” and “non-identifiable.”

For deterministic model-to-model curves, conventional AIC/BIC should be interpreted carefully because the residuals are approximation error rather than observational noise. The paper can still use them as comparative diagnostics, provided that limitation is stated. Cross-validated approximation error, profile likelihood, or a tolerance-based parsimonious-model rule may be more transparent.

---

## Major comment U7 — State all protocol choices and extrapolations in the manuscript

The new paragraph reads as a general model comparison but depends on specific, consequential protocol choices.

### Cameron protocol

- The Cameron curve is simulated to 400 s to approach exhaustion and expose a putative slow constant up to 158 s.
- This is far beyond the approximately 30 s recipe range for which the registered Cameron implementation is described as validated.
- Cameron has no well-mixed configuration; the curve is a flowing percolation-bed aggregate.
- The fit fixes the Maille delay parameter `tau` to zero.
- Cameron uses one lumped solute while Maille resolves five analytes.
- The curve is normalized by its simulated endpoint.

### Roman-Corrochano protocol

- The curve is model-generated because the raw experimental time curves are not available.
- The solver represents a finite, well-mixed bath.
- Only one medium-molecular-weight species is used.
- Radius is fixed to the 20 μm fine class.
- Temperature is 80 °C.
- Pore-to-bath ratio is 0.01.
- The fitting window is 0–20 diffusion times with 500 uniformly spaced samples.
- The response is normalized by the final value on the finite fitting interval.
- The Maille delay is fixed to zero.

These are not implementation trivia. They define the observable being fitted and the meaning of the result.

### Required action

Provide a method table and repeat the most important caveats in the result paragraph. At minimum, the main text must say “model-generated,” “qualitative,” “400 s extrapolation” for Cameron, and “20 μm fine-class configuration” for Roman-Corrochano.

---

## Major comment U8 — Add fitting-protocol sensitivity for the Roman-Corrochano result

The reported “universal” fitted weight of approximately 0.323 and ratio of approximately 12.32 are conditional on the chosen fitting protocol. A reviewer sensitivity calculation for PsiA, holding radius at 20 μm, illustrates the issue.

### Sensitivity to the fitted time window

| Fitting endpoint | Weight | Fast constant (s) | Slow constant (s) | Slow/fast ratio |
|---:|---:|---:|---:|---:|
| 3 diffusion times | 0.271 | 0.0186 | 0.2929 | 15.75 |
| 5 diffusion times | 0.311 | 0.0259 | 0.3429 | 13.26 |
| 10 diffusion times | 0.321 | 0.0280 | 0.3543 | 12.65 |
| 20 diffusion times | 0.323 | 0.0288 | 0.3552 | 12.32 |
| 40 diffusion times | 0.330 | 0.0319 | 0.3581 | 11.23 |
| 100 diffusion times | 0.352 | 0.0428 | 0.3669 | 8.56 |

### Sensitivity to pore-to-bath ratio at 20 diffusion times

| Pore-to-bath ratio | Weight | Fast constant (s) | Slow constant (s) | Slow/fast ratio |
|---:|---:|---:|---:|---:|
| 0.0001 | 0.320 | 0.0291 | 0.3592 | 12.36 |
| 0.001 | 0.320 | 0.0290 | 0.3588 | 12.36 |
| 0.01 | 0.323 | 0.0288 | 0.3552 | 12.32 |
| 0.1 | 0.354 | 0.0269 | 0.3238 | 12.04 |
| 1 | 0.552 | 0.0163 | 0.1964 | 12.05 |
| 3 | 0.734 | 0.00965 | 0.1369 | 14.19 |

The shape invariance across grinds at fixed dimensionless settings remains real. The exact numerical pair is not an intrinsic universal constant independent of protocol.

### Required action

Either:

- add a compact sensitivity analysis and describe the pair as protocol-specific; or
- remove the exact “fixed”/“intrinsic” language and limit the conclusion to the demonstrated nondimensional similarity under the declared setup.

---

## Major comment U9 — Define what “ports” means before declaring non-portability

The current producer treats absence from Maille's pooled numerical bands as the decisive non-portability signal. That is one useful test, but it is not a complete portability criterion.

A fitted parameter can fail to port for several independent reasons:

- the underlying observable differs;
- the physical mechanism differs;
- the species/inventory basis differs;
- the delay convention differs;
- the fit interval, normalization, or weighting differs;
- the parameter is not identifiable;
- the value lies outside a declared uncertainty interval; or
- the receiving model does not improve prediction when the parameter is transferred.

Conversely, numerical range overlap would not prove semantic portability. The Roman radius sensitivity shows that both fitted constants can enter Maille's pooled ranges without acquiring Maille's two-pool physical meaning.

### Required action

Define a portability decision as a vector rather than a Boolean. A useful record could include:

| Portability dimension | Question |
|---|---|
| Observable identity | Are the fitted curves the same physical observable and normalization? |
| Mechanism identity | Do the coefficients parameterize the same physical decomposition? |
| Population/species identity | Are particle classes, analytes, and inventories aligned? |
| Estimation identity | Are fit equation, delay, interval, weighting, and bounds aligned? |
| Numerical compatibility | Do uncertainty-aware parameter ranges overlap? |
| Predictive transfer | Does using the donor parameter improve or preserve out-of-sample performance? |

For the current result, the strongest conclusion is **semantic non-equivalence under the tested mappings**, not a universal numerical theorem that the parameter can never be reused.

---

## Major comment U10 — Add the new claim to Paper 3's evidence and claim architecture

PR #175 explicitly states that there was no evidence-graph change. That leaves the new manuscript result in an awkward position. Paper 3 says manuscript-facing values should map to named producers, result paths, units, datasets, components, caveats, reproduction commands, and source commits. The new paragraph contains several such values and conclusions, but it is not represented in the Paper 3 priority evidence matrix or generated claim bundle.

This should be treated as a test of the architecture, not an exception.

### Required claim records

At least two records are needed:

```yaml
claim_id: paper3.timescale_semantics.cameron
statement: >
  Under the declared 400 s, tau=0 fitting protocol, no Cameron grinder
  setting reproduces Maille's pooled fast-timescale band; three of four
  curves are single-exponential-like, while the fourth requires formal
  two-vs-one model adjudication.
producer: puckworks.analysis.maille2024.cross_model_timescale_cameron
components:
  - maille2024.two_regime
  - cameron2020.extraction_bdf
evidence_relation: model_to_model_qualitative
outcome_polarity: non_portability_under_declared_mapping
configuration:
  horizon_s: 400
  normalization: simulated_endpoint
  delay_s: 0
limitations:
  - model-generated curve
  - Cameron extrapolated beyond approximately 30 s validation window
  - one lumped Cameron solute versus five Maille analytes
  - parameter-identifiability analysis required
not_supported:
  - external validation
  - proof that Cameron has only one physical extraction mechanism
  - universal non-portability under every fit protocol
source_commit: filled at export
```

```yaml
claim_id: paper3.timescale_semantics.roman_corrochano
statement: >
  Under the declared fine-class stirred-vessel protocol, the fitted
  dimensionless bi-exponential shape is invariant across diffusivities,
  while absolute constants vary with diffusion time and remain below
  Maille's pooled bands at R=20 micrometres.
producer: puckworks.analysis.maille2024.cross_model_timescale_roman
components:
  - maille2024.two_regime
  - romancorrochano2017.extraction
evidence_relation: model_to_model_qualitative
outcome_polarity: semantic_non_equivalence_under_declared_mapping
configuration:
  radius_m: 2.0e-5
  temperature_degC: 80
  molecular_weight_class: medium
  pore_to_bath: 0.01
  fit_window_diffusion_times: 20
  normalization: finite_window_endpoint
limitations:
  - model-generated curve
  - fine class only
  - coarse-class radius unavailable
  - protocol-sensitive empirical approximation
not_supported:
  - validation against Roman-Corrochano experimental time curves
  - absolute-timescale conclusion for the untested coarse class
  - claim that the physical diffusion solution contains one mathematical mode
source_commit: filled at export
```

The exact schema can differ, but the result must be generated and included in the same frozen manuscript build.

---

## Major comment U11 — Derive verdict fields rather than hard-coding them

In `cross_model_timescale_roman()`, the return value includes:

```python
two_regime_ports_to_roman=False
```

This is hard-coded rather than computed from a fully declared portability rule. The function's `passed` field is calculated from shape invariance, two-exponential-versus-one R² separation, and fine-class numerical-band misses, but `two_regime_ports_to_roman` is not explicitly derived from that result. This is fragile and makes the scientific verdict harder to audit.

Similarly, the Cameron `single_timescale` field is derived from an arbitrary 50% relative-distance threshold rather than a model-selection criterion.

### Required action

- Define the portability dimensions and compute each one separately.
- Derive any aggregate verdict from named sub-results.
- Avoid a single `passed` field for a qualitative scientific comparison unless “pass” means a predeclared, narrow gate.
- Rename `passed` to something like `gate_condition_met` and report the exact condition.
- Replace hard-coded verdicts with computed, tested fields.

---

## Major comment U12 — Separate descriptive shape reuse from physical parameter transfer

The paragraph risks implying that using the same bi-exponential form across models is itself invalid. It is not. A common empirical form can be useful as a descriptive basis for curve comparison, compression, or feature extraction. The error occurs when its coefficients are treated as the same physical quantities or transferred without a semantic adapter and validation.

### Suggested distinction

> The shared bi-exponential form is useful as a descriptive comparison basis. It does not, by itself, define a shared physical interface. The fitted coefficients remain model-qualified unless mechanism, observable, estimation protocol, and transfer performance are shown to be commensurate.

This formulation is more precise and avoids making the paper appear hostile to empirical curve fitting in general.

---

## Major comment U13 — Move the quantitative detail out of the architecture paragraph or support it visibly

Section 4.5 is primarily an architectural/semantic section. The new 255-word paragraph contains a methods summary, three-model comparison, fitted-result interpretation, mechanism inference, and composition rule—all without a table, figure, references, or result identifier. It is too dense for its location.

### Preferred structure

- Keep two or three conceptual sentences in §4.5.
- Add a short dedicated subsection to a demonstration section, for example “Shared curve form, non-shared parameters.”
- Include one generated figure and one compact generated table.
- Put detailed fit protocol, sensitivity, and diagnostics in the supplement.

A suitable figure would show:

1. normalized curves and one-/two-exponential fits for the four Cameron settings;
2. profile or multistart evidence for degeneracy at the first three settings;
3. dimensionless Roman-Corrochano curves collapsing across grinds;
4. absolute Roman constants versus `R²/D_eff`, with the tested 20 μm point and the unknown coarse-class region clearly distinguished; and
5. Maille ranges shown as contextual bands, not as proof of semantic identity.

---

## Major comment U14 — Correct code comments, tests, and stale documentation before citing the computation

The supporting implementation contains several documentation/test inconsistencies:

1. The Cameron function docstring still says the Roman-Corrochano half is rights-deferred, while the returned record says it has landed as a research computation and only the public product lane remains deferred.
2. The Cameron test comments that “a single-timescale form fits Cameron well,” but the test actually checks R² from the **bi-exponential** fit and does not fit or compare a one-exponential model.
3. The Roman test confirms that the two-exponential R² exceeds the one-exponential R², but does not test uncertainty, parsimony, or sensitivity.
4. The Roman verdict is hard-coded as described above.
5. “Grind-independent” appears in code-generated findings without distinguishing shape from absolute constants.
6. The code and card use “one Crank diffusion mode,” which should be replaced by “one physical diffusion process” or equivalent.

These are not cosmetic. The manuscript is presenting this computation as evidence that its registry prevents semantic slippage. The supporting computation and documentation must meet the same standard.

---

## Major comment U15 — Avoid unsupported mechanistic attribution to “flow limitation”

The new paragraph says the Cameron result represents “a flow-limited single scale.” The fitted aggregate extraction curve alone does not identify which process is limiting. Cameron's registered model includes flowing-bed advection, intraparticle diffusion, nonlinear dissolution, and fine/coarse populations. A near-single-exponential cumulative response under one protocol does not prove that flow is the limiting mechanism.

Use a descriptive phrase such as:

> an aggregate flowing-bed response that is single-exponential-like for three tested settings under the declared fit.

A mechanistic “flow-limited” claim would require a sensitivity or timescale analysis showing that changing flow controls the dominant constant while other mechanisms do not.

---

## Major comment U16 — The manuscript must disclose that the curves are model-generated

The model card and code say this clearly; the paper paragraph does not. “A third model's genuinely well-mixed diffusion curve” can easily be read as an observed curve from a well-mixed experiment. Roman-Corrochano's raw time-resolved curves are not available in the repository. The analysis fits a registered model output.

### Required language

Use “model-generated stirred-vessel diffusion curve” and “model-generated Cameron flowing-bed curve.” Conclude with an explicit evidence label:

> These are qualitative model-to-model probes and do not validate any of the three models against independent measurements.

---

## 5. Suggested replacement for the new paragraph

The following replacement preserves the important conceptual contribution while correcting the main scientific overstatements. Numerical wording should be regenerated from a committed result bundle, and the Cameron model-selection sentence should be updated after the project reproduces the reviewer diagnostic in its locked environment.

> The same caution applies to a shared fast–slow curve shape. We fitted the empirical bi-exponential used by Maille [new reference] to model-generated cumulative extraction curves from Cameron et al. [6] and Roman-Corrochano [new reference]. Under the current Cameron protocol—zero delay and a 400 s run-to-exhaustion extrapolation—the fitted constants coincide for three of four grinder settings; the fourth returns distinct values of approximately 23.6 and 40.0 s and requires formal one- versus two-timescale adjudication. In all four settings, no nominal fast constant falls within Maille's pooled 2.2–19.1 s fast range. Under the current Roman-Corrochano protocol—one medium-molecular-weight species, a 20 μm-radius fine class, 80 °C, and a dilute finite bath—the fitted weight and slow/fast ratio are invariant across diffusivities, while the absolute constants scale with diffusion time and vary across grinds; for this fine-class configuration they remain sub-second and below Maille's pooled ranges. The unreported coarse-class particle size was not tested. These model-generated comparisons are qualitative rather than validation. They show that a common bi-exponential approximation does not create a common physical interface: Maille's constants parameterize a geometric two-pool construction, the Roman-Corrochano constants summarize one physical diffusional-release process under a selected configuration, and the Cameron constants summarize an aggregate flowing-bed response. Puckworks therefore retains model-qualified parameter identities unless semantic equivalence and predictive transfer are separately demonstrated.

A shorter §4.5 version could be:

> A shared empirical curve form is not a shared physical contract. Model-generated comparisons show that a bi-exponential approximation can describe Maille's geometric two-pool model, Roman-Corrochano's selected diffusional-release configuration, and Cameron's aggregate flowing-bed response while producing non-equivalent and sometimes non-identifiable coefficients. Puckworks therefore treats each fitted timescale as model-qualified unless observable identity, estimation protocol, mechanism, and predictive transfer have all been established.

The detailed numerical result can then move to a demonstration subsection or supplement.

---

## 6. Recommended generated table for the manuscript

**Proposed table: Same fast–slow form, different evidentiary meanings.**

| Source/configuration | Curve status | Declared fit protocol | Result under current protocol | Defensible interpretation | Not supported |
|---|---|---|---|---|---|
| Maille 2024 batch extraction | Measured/source-fitted analyte curves | Source bi-exponential with analyte/material-specific parameters | Fast 2.2–19.1 s; slow 13–158 s pooled ranges used in the registry | Empirical parameters associated with Maille's stated geometric two-pool construction | Universal espresso constants |
| Cameron 2020 flowing bed | Model-generated cumulative extraction | 400 s extrapolation; zero delay; endpoint normalization | Three settings collapse; coarsest returns approximately 23.6/40.0 s; no nominal fast constant in Maille fast band | Under this mapping, Maille's fast coefficient is not reproduced; first three fits are non-identifiable as two-scale decompositions | All Cameron physics is one-regime; external validation; mechanism identified as flow-limited |
| Roman-Corrochano fine class | Model-generated finite-bath diffusion | `R=20 μm`; medium-MW; 80 °C; pore:bath 0.01; 0–20 diffusion times; zero delay | Shape weight ≈0.323 and ratio ≈12.32 at fixed protocol; absolute constants 0.029–0.056 s and 0.355–0.685 s | Same dimensionless curve shape across diffusivities; coefficients summarize one selected physical diffusion process | Full coarse/fine model conclusion; universal constants; experimental validation |

Every cell should be generated from the frozen evidence bundle or be explicit interpretive prose tied to a claim record.

---

## 7. Status of the 18 major comments from the previous review

No previous major comment is fully resolved by PR #175. The table below records the current status and the effect of the new change.

| Previous major comment | Current status | Effect of PR #175 / required next step |
|---|---|---|
| 1. Decide publication genre | **Unresolved** | Draft grows from 9,923 to 10,178 words. Select software/resource/full-methods route before further expansion. |
| 2. Repair manuscript-generation pipeline | **Unresolved; newly tested again** | New numerical claim was added without a Paper 3 evidence-graph/claim-record update. Stale inline counts remain. |
| 3. Rewrite architecture around schema v2 | **Unresolved** | `kind` remains foregrounded and adapter/diagnostic role wording remains outdated. |
| 4. Separate evidence relation, outcome, artifact role, and public badge | **Unresolved** | New result is described as “the registry finds” but lacks a normalized evidence-relation/outcome record. |
| 5. Resolve evidence-vector/weakest-link contradiction | **Unresolved** | No relevant change. |
| 6. Correct infiltration overclaim | **Unresolved** | Named-shot table still says “independently gated” despite same-shot fitted permeability and pressure. |
| 7. Define executable at each layer | **Unresolved** | No relevant manuscript correction. |
| 8. Distinguish implemented capability from intent | **Unresolved** | No relevant manuscript correction. |
| 9. Add rigorous related work and novelty | **Unresolved** | New paragraph adds domain claims but still lacks Maille/Roman references and broader research-software literature. |
| 10. Evaluate the framework | **Unresolved** | New example is useful, but it is another case study rather than a predeclared framework evaluation. It could become a strong mutation/semantic-lint test. |
| 11. Reduce duplication with companion papers | **Partly aided conceptually; unresolved structurally** | The new example strengthens Paper 3 ownership of semantics, but quantitative detail should be allocated carefully across Paper 3, the Maille analysis/card, and public-value article. |
| 12. Complete and consolidate figures | **Unresolved** | No figure added for the new result; all seven manuscript figures remain specifications rather than reviewable figures. |
| 13. Strengthen quantitative/statistical reporting | **More urgent** | New paragraph adds fitted constants, model comparison, mechanism inference, and cross-model claims without uncertainty, residuals, model selection, or sensitivity. |
| 14. Reconsider external community-corpus section | **Unresolved** | No relevant change. |
| 15. Make curated-corpus method reproducible | **Unresolved** | No relevant change. |
| 16. Clarify typed-contract scope | **Unresolved** | The new example actually helps motivate typed fitted-parameter identities, but that contract is not implemented or shown. |
| 17. Generate and rename named-shot scorecard | **Unresolved** | No relevant change. |
| 18. Temper cross-domain generalization | **Unresolved** | No relevant change. |

---

## 8. Full-manuscript consistency audit at the updated boundary

The following earlier factual inconsistencies remain present at merge commit `b8c84be`.

| Item | Updated manuscript statement | Repository evidence at audit boundary | Required action |
|---|---|---|---|
| Component total | 25 | Generated count is 25 | Consistent; generate at build time. |
| Manifest total | 70 records in abstract/§2/§6/Table 7 | `MANIFEST.csv` contains **104 logical rows** | Replace every manual count with generated metadata. |
| Execution roles | 11 runtime, 13 calibration, 1 synthesis | Generated artifacts report **12 runtime, 13 calibration, 0 adapters, 0 diagnostics** | Regenerate Table 1. Synthesis is provenance, not an execution role. |
| Synthesis classification | One component assigned role `synthesis` | `brewer2026.coupled_kappa_t`: runtime execution role, project-synthesis provenance class | Correct the metadata axis. |
| Registry schema | §3.2 foregrounds `kind` | Schema v2 deprecates `kind`; authoritative fields are execution role, provenance class, evidence strength | Rewrite §3.2. |
| Adapter/diagnostic roles | Not first-class enum values | Both are schema-supported execution roles, currently with no registered instances | Say “supported but uninstantiated.” |
| Evidence taxonomy | “Independent external” and “Negative validation” presented on one category axis | Code uses `controlled_independent`; negative outcome is not an evidence-strength enum | Separate relation from outcome polarity and align names. |
| Generated-table claim | Inline tables cannot silently diverge | Inline Table 1/Appendix A diverge from generated artifacts | Repair build/test or remove the claim. |
| Infiltration evidence | “Independently gated” | Same shot supplies pressure, fitted permeability, and evaluation; evidence matrix calls it same-campaign/not-held-out compatibility | Replace with “same-shot compatibility check over a predeclared porosity bracket.” |
| Release/readiness | Editable install only; release/public API/tutorial/governance work still required | `v0.3.0`, wheels/sdist, public Colabs, API docs, support matrix, contribution/governance files now exist | Rebuild Table 7 from the frozen release and development state. |
| Executability | Title/abstract may imply corpus-wide open execution | Rights, data, release, hosting, and scientific admissibility differ by component | Define separate availability dimensions. |
| Figures | Seven specified figures | No embedded final figures | Submission blocker. |
| Manuscript date | “Draft dated 15 July 2026” | New material merged 25 July 2026 | Update date and freeze to release/archive. |
| New timescale claim | Presented as a registry finding | No Paper 3 priority-evidence entry or generated manuscript result record for the new prose | Add claim records and generated artifact. |
| New references | Three-model comparison | Maille and Roman-Corrochano absent from references | Add primary-source references. |

### Manifest-count reproduction

At the audit boundary:

```python
import csv

with open("puckworks/data/MANIFEST.csv", newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))

assert len(rows) == 104
```

The file has 105 physical lines including the header and 104 logical data rows.

---

## 9. Updated prioritized revision plan

## P0 — Correct before the next internal Paper 3 review

1. **Rewrite the new timescale paragraph** using the corrected language in §5 of this review.
2. **Name and cite Maille, Cameron, and Roman-Corrochano.** Add the missing primary references.
3. **Correct Roman wording:** shape invariance is grind-independent under a fixed protocol; absolute constants vary with diffusivity.
4. **Limit the Roman numerical conclusion to the selected 20 μm fine-class configuration.** State that the coarse-class comparison is unresolved.
5. **Correct Cameron wording:** three settings collapse; the coarsest setting does not support an unqualified single-timescale claim.
6. **Replace “single diffusion mode” with “one physical diffusion process” or equivalent.**
7. **State model-generated/qualitative status and all material protocol caveats in the manuscript.**
8. **Add two Paper 3 claim records and a committed generated result table/bundle.**
9. **Replace the Cameron 50% heuristic with a declared one- versus two-timescale/model-identifiability rule.**
10. **Derive the Roman portability verdict rather than hard-coding it.**
11. **Fix stale support documentation and test comments.**
12. **Repair the already-identified stale counts and schema statements:** 104 manifest records; 12/13 execution-role split; schema-v2 axes; adapter/diagnostic wording.
13. **Correct “independently gated” infiltration language.**
14. **Update manuscript date and frozen provenance.**

## P1 — Complete before public preprint

1. Add one-/two-exponential comparison, multistart stability, residuals, and identifiability diagnostics.
2. Add Roman sensitivity to fit window, normalization, bath ratio, particle radius, and species class; distinguish declared sensitivity from missing-source uncertainty.
3. Add a generated figure and table for the three-model comparison.
4. Define portability as a vector with semantic, estimation, numerical, and predictive dimensions.
5. Repair the manuscript-generation pipeline and add tests that parse the rendered manuscript values.
6. Update the readiness table from the frozen release/development snapshot.
7. Complete the four consolidated figures recommended in the previous review.
8. Add rigorous related work and define Paper 3's novelty relative to FAIR4RS, provenance standards, research compendia, model cards/datasheets, workflow systems, software citation, and verification/validation practice.
9. Add a reproducible curated-corpus method and frozen archive.
10. Select the publication route and reduce manuscript length accordingly.

## P2 — Complete before journal submission

1. Evaluate the framework using a predeclared semantic-defect set and mutation tests.
2. Conduct clean-room reproduction from the archived release.
3. Obtain independent adjudication of evidence labels/claim language if feasible.
4. Add predictive transfer experiments where the paper uses “portable” or “non-portable” language.
5. Resolve external-corpus governance/privacy and submission-supplement scope.
6. Archive code, data, generated figures, claim graph, and manuscript build with a DOI.

---

## 10. Suggested tests for the revised computation

The following tests would make the new result substantially more defensible.

### Cameron

```python
def test_cameron_timescale_model_selection_is_explicit():
    result = cross_model_timescale_cameron()
    assert result["comparison_method"] in {
        "cross_validated_error",
        "aicc_with_stated_residual_model",
        "profile_likelihood_parsimony_rule",
    }
    for row in result["per_grind"]:
        assert "one_timescale_fit" in row
        assert "two_timescale_fit" in row
        assert "identifiability_status" in row
        assert "model_selection_status" in row


def test_cameron_coarsest_is_not_classified_by_distance_heuristic_alone():
    row = next(r for r in cross_model_timescale_cameron()["per_grind"] if r["gs"] == 2.5)
    assert row["lambda_fast_s"] != row["lambda_slow_s"]
    assert row["single_timescale_status"] != "true_by_50_percent_distance_rule"
```

### Roman-Corrochano

```python
def test_roman_shape_invariance_is_not_absolute_timescale_invariance():
    result = cross_model_timescale_roman()
    fast = [r["lambda_fast_s"] for r in result["per_grind"]]
    slow = [r["lambda_slow_s"] for r in result["per_grind"]]
    assert max(fast) > min(fast)
    assert max(slow) > min(slow)
    assert result["shape_is_scale_invariant"]
    assert not result["absolute_timescales_are_grind_independent"]


def test_roman_verdict_is_fine_class_only():
    result = cross_model_timescale_roman()
    assert result["particle_class"] == "fine"
    assert result["radius_m"] == 20e-6
    assert result["coarse_class_status"] == "not_evaluated_missing_radius"


def test_roman_portability_verdict_is_derived():
    result = cross_model_timescale_roman()
    assert result["two_regime_ports_to_roman"] == derive_portability(result["portability_vector"])
```

### Manuscript/claim propagation

```python
def test_paper3_timescale_claims_have_generated_records():
    ids = {claim.claim_id for claim in load_paper3_claims()}
    assert "paper3.timescale_semantics.cameron" in ids
    assert "paper3.timescale_semantics.roman_corrochano" in ids


def test_paper3_generated_values_match_result_bundle():
    manuscript = render_paper3_from_frozen_bundle()
    assert manuscript.roman_fast_range_s == result_bundle.roman_fast_range_s
    assert manuscript.roman_slow_range_s == result_bundle.roman_slow_range_s
    assert manuscript.cameron_no_fast_band_match is True
```

The exact implementation can differ, but the tests should enforce scientific meaning rather than only string presence.

---

## 11. Broader full-paper comments that remain decisive

### 11.1 Publication genre remains unresolved

The manuscript is now 10,178 words before final figures, captions, expanded references, methods detail, and supplements. It remains far too long for a conventional short software paper and under-evaluated for a full methods/resource article. The authors should select one of two realistic routes:

- **Concise software/resource paper:** reduce the main text substantially, place most espresso demonstrations in supplements/companion papers, and focus on software purpose, architecture, availability, and a compact evidence of use.
- **Full methods/resource paper:** retain the scientific examples, but add formal research questions, related work, systematic framework evaluation, methods, uncertainty/identifiability analysis, figures, and a frozen archive.

The current hybrid will be difficult to review and place.

### 11.2 The manuscript-generation contradiction remains a critical credibility issue

Paper 3 argues that generated tables and claim producers prevent silent drift, yet its own inline counts are stale. This is the most important process defect because it directly falsifies a claimed property of the proposed architecture. The fix is not merely to edit the numbers. The build must make a recurrence impossible.

### 11.3 Evidence language remains inconsistent

The named-shot infiltration result is still described as independent even though it reuses the same shot's pressure trace and fitted permeability. The new timescale result is now another example where the code/card caveats are more cautious than the manuscript. Paper 3 needs a single enforced path from evidence relation to permissible prose.

### 11.4 The framework itself still lacks evaluation

The paper offers persuasive examples, but it does not measure whether the registry architecture reliably detects semantic defects, prevents manuscript drift, improves reproduction, or changes model-composition decisions. The new fast/slow example is ideal for a formal semantic-lint benchmark:

- mutation: strip model namespaces from the three timescale parameters;
- mutation: declare them commensurate based only on units/form;
- expected registry behavior: reject direct composition and require an adapter/claim with declared mapping;
- evaluation: precision/recall across a predeclared set of real and synthetic defects.

### 11.5 Related work is still insufficient

The central contribution is not only an espresso review. It concerns scientific-software provenance, semantic model interfaces, evidence-qualified claims, and reproducible computational resources. The paper must position itself against established work in FAIR/FAIR4RS, W3C PROV, RO-Crate/research compendia, software citation, model cards/datasheets, scientific workflows, verification/validation, and uncertainty/identifiability practice.

### 11.6 Figures remain a submission blocker

Seven figure specifications are present, but no final figures are embedded. The new result makes a generated comparison figure even more important. Core claims cannot be reviewed adequately from captions alone.

---

## 12. Independent reviewer computational audit

### 12.1 Scope

For this update, I went beyond the static audit performed in the previous review. I downloaded the exact analysis/model/data files associated with the merge snapshot and reconstructed the minimum import structure needed to execute:

- `puckworks.analysis.maille2024.cross_model_timescale_cameron()`; and
- `puckworks.analysis.maille2024.cross_model_timescale_roman()`.

I then performed targeted alternative fits and sensitivity calculations using the same deterministic curves. I did **not** run the entire repository test suite, reproduce every upstream digitization, or independently verify all primary-source transcription. The additional AICc/BIC and sensitivity tables in this review are reviewer diagnostics and are not yet authoritative Puckworks result artifacts.

### 12.2 Files inspected

- [`puckworks/analysis/maille2024.py`](https://github.com/trbrewer/puckworks/blob/b8c84be3170dc644ef5d15036e9698214896842f/puckworks/analysis/maille2024.py)
- [`tests/test_maille2024.py`](https://github.com/trbrewer/puckworks/blob/b8c84be3170dc644ef5d15036e9698214896842f/tests/test_maille2024.py)
- [`docs/cards/maille2024.md`](https://github.com/trbrewer/puckworks/blob/b8c84be3170dc644ef5d15036e9698214896842f/docs/cards/maille2024.md)
- [`puckworks/models/cameron2020/extraction_bdf.py`](https://github.com/trbrewer/puckworks/blob/b8c84be3170dc644ef5d15036e9698214896842f/puckworks/models/cameron2020/extraction_bdf.py)
- [`puckworks/models/romancorrochano2017/extraction.py`](https://github.com/trbrewer/puckworks/blob/b8c84be3170dc644ef5d15036e9698214896842f/puckworks/models/romancorrochano2017/extraction.py)
- Roman-Corrochano effective-diffusivity and partition tables at the same commit
- Paper 3 priority evidence matrix and generated registry artifacts at the same commit

### 12.3 Reproduced producer results

The exact registered producers reproduced the values shown in major comments U2 and U5. In particular:

- Cameron: nominal fast constants 23.58–32.30 s, none inside Maille's 2.2–19.1 s fast range; three equal-constant fits and one 23.58/40.00 s fit.
- Roman-Corrochano at 20 μm: nominal fast constants 0.0288–0.0556 s, nominal slow constants 0.3552–0.6846 s, fitted weight 0.323, ratio 12.32, two-exponential R² 0.99943, and one-exponential R² 0.95021.

### 12.4 Limits of the review diagnostics

- The curves are deterministic model outputs, so information criteria based on an implicit iid residual model should not be treated as conventional experimental inference.
- The reviewer radius sweep is a sensitivity demonstration, not a claim about the unknown Roman-Corrochano coarse size.
- The Maille ranges are pooled across source analytes/materials. A rigorous transfer test may need analyte-specific comparisons rather than pooled minimum/maximum bands.
- The primary scientific conclusion should therefore remain qualitative and configuration-specific until uncertainty-aware predictive transfer is tested.

---

## 13. Line-level comments on the inserted paragraph

The comments below follow the order of the sentences in the new §4.5 paragraph.

1. **“Three extraction models all resolve a quick phase and a slow phase.”**  
   Revise. Maille explicitly parameterizes two regimes; Roman and Cameron generate curves to which the Maille form is fitted after the fact. Say that the three models “produce or parameterize curves that can be described using fast/slow language,” not that all three natively resolve two phases.

2. **“The registry finds they are not.”**  
   Add a claim identifier, producer, evidence level, and explicit scope: “under the declared model-generated fitting protocols.”

3. **“Fitting one batch model's empirical bi-exponential form…”**  
   Name Maille and cite it. State whether the delay parameter is fitted or fixed; here it is fixed to zero.

4. **“…to a second model's simulated extraction curve…”**  
   Name Cameron, specify the 400 s extrapolation, and state endpoint normalization.

5. **“…the fast and slow constants collapse onto a single timescale…”**  
   Restrict to three of four settings. The coarsest setting returns 23.58 and 40.00 s.

6. **“…that model's flowing bed is effectively one-regime…”**  
   Overgeneralized and mechanistically ambiguous. Use “three tested aggregate curves are single-exponential-like under this fit.”

7. **“…the batch model's fast timescale has no counterpart in it.”**  
   Too absolute. The defensible statement is that no fitted Cameron nominal fast constant enters Maille's pooled fast band under the declared mapping. “No counterpart” also requires semantic/mechanistic analysis, which should be stated separately.

8. **“a third model's genuinely well-mixed diffusion curve…”**  
   Name Roman-Corrochano and say “model-generated finite-bath stirred-vessel curve.” “Genuinely” is unnecessary and may imply experimental evidence.

9. **“…does produce two constants—the fit is good…”**  
   Report the comparison method and residual diagnostics. R² alone is insufficient.

10. **“…but they are grind-independent…”**  
    Incorrect for absolute constants. Only weight and ratio are invariant at fixed protocol.

11. **“…and hold a fixed ratio…”**  
    Qualify as approximately fixed under the declared time window, normalization, species, radius, and bath ratio.

12. **“…intrinsic short- and long-time signature of a single diffusion mode…”**  
    Replace “single diffusion mode” with “one physical diffusion process in the selected particle/species configuration.”

13. **“…at that model's own particle size…”**  
    Replace with “at the selected 20 μm-radius fine class.” The model also has an untested coarse class.

14. **“…two orders of magnitude away…”**  
    Prefer the actual range: “0.029–0.056 s and 0.355–0.685 s, below Maille's pooled 2.2–19.1 s and 13–158 s ranges.” “Two orders” varies depending on which boundaries are compared.

15. **“…parameters mean three different things…”**  
    Strong and worth retaining, but cite or define each meaning precisely.

16. **“…a flow-limited single scale in the third.”**  
    “Flow-limited” is not established by the fit. Use “aggregate flowing-bed response.”

17. **“a good fit is not evidence of a shared quantity…”**  
    Excellent central sentence. Retain.

18. **“…the same category error as equating the fast fractions…”**  
    Add the qualification “when interpreted or transferred as the same physical constants.” Using the same form descriptively is not itself an error.

19. **“…keep the constructs labelled by their model of origin…”**  
    Strong architectural conclusion. Consider showing the exact proposed typed identifiers, e.g. `maille.lambda_fast_s`, `cameron.effective_curve_timescale_s`, and `roman.fitted_diffusion_shape_timescale_s`, rather than leaving this only as prose.

---

## 14. Final recommendation

### Decision on PR #175's Paper 3 text

**Revise before treating the paragraph as publication-ready.** The conceptual contribution is strong and belongs in Paper 3. The present language overstates both the Roman-Corrochano and Cameron results and omits the evidence metadata that the paper itself requires.

### Decision on Paper 3 as a whole

**Major revision remains appropriate.** The paper has a distinctive and valuable contribution: executable preservation of model semantics, provenance, evidence relation, and negative composition outcomes in a fragmented espresso-model literature. The revised fast/slow example could become one of its best demonstrations. To do so, it must model the discipline it advocates:

- distinguish absolute quantities from dimensionless shape;
- distinguish one physical mechanism from one mathematical mode;
- distinguish a selected fine-class configuration from a whole model;
- distinguish good descriptive fit from parameter identification;
- distinguish model-generated qualitative evidence from validation; and
- bind every manuscript claim to a frozen producer and result record.

The paper should not be weakened or abandoned. It should be corrected, evaluated, and frozen so that its implementation and manuscript jointly demonstrate the evidence discipline they propose.

---

## 15. Frozen repository sources used in this updated review

1. [Previous review snapshot `93358f8e`](https://github.com/trbrewer/puckworks/commit/93358f8e4d7d5c214470d82195d852f455651ff9)
2. [Change commit `0c414bc`](https://github.com/trbrewer/puckworks/commit/0c414bc57bb1995585e7cc0a2176fe8e76c09b42)
3. [Merge/audit snapshot `b8c84be`](https://github.com/trbrewer/puckworks/commit/b8c84be3170dc644ef5d15036e9698214896842f)
4. [PR #175](https://github.com/trbrewer/puckworks/pull/175)
5. [Paper 3 manuscript at the audit snapshot](https://github.com/trbrewer/puckworks/blob/b8c84be3170dc644ef5d15036e9698214896842f/docs/PAPER_3_PUCKWORKS_DRAFT.md)
6. [Maille analysis producer](https://github.com/trbrewer/puckworks/blob/b8c84be3170dc644ef5d15036e9698214896842f/puckworks/analysis/maille2024.py)
7. [Maille analysis tests](https://github.com/trbrewer/puckworks/blob/b8c84be3170dc644ef5d15036e9698214896842f/tests/test_maille2024.py)
8. [Maille model card](https://github.com/trbrewer/puckworks/blob/b8c84be3170dc644ef5d15036e9698214896842f/docs/cards/maille2024.md)
9. [Cameron extraction implementation](https://github.com/trbrewer/puckworks/blob/b8c84be3170dc644ef5d15036e9698214896842f/puckworks/models/cameron2020/extraction_bdf.py)
10. [Roman-Corrochano extraction implementation](https://github.com/trbrewer/puckworks/blob/b8c84be3170dc644ef5d15036e9698214896842f/puckworks/models/romancorrochano2017/extraction.py)
11. [Dataset manifest](https://github.com/trbrewer/puckworks/blob/b8c84be3170dc644ef5d15036e9698214896842f/puckworks/data/MANIFEST.csv)
12. [Registry implementation](https://github.com/trbrewer/puckworks/blob/b8c84be3170dc644ef5d15036e9698214896842f/puckworks/registry.py)
13. [Paper 3 priority evidence matrix](https://github.com/trbrewer/puckworks/blob/b8c84be3170dc644ef5d15036e9698214896842f/docs/paper3_resource/generated/paper3_priority_evidence_matrix.md)
14. [Generated registry counts](https://github.com/trbrewer/puckworks/blob/b8c84be3170dc644ef5d15036e9698214896842f/docs/paper3_resource/generated/registry_counts.json)
15. [Generated registry overview](https://github.com/trbrewer/puckworks/blob/b8c84be3170dc644ef5d15036e9698214896842f/docs/paper3_resource/generated/table1_registry_overview.md)


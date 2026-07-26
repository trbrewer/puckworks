# Second-round detailed review of Paper B2

## Manuscript reviewed

**Current title:** *One flow curve, many explanations: null-first inference for machine and porous-bed dynamics in espresso*  
**Repository:** [trbrewer/puckworks](https://github.com/trbrewer/puckworks)  
**Repository state reviewed:** [`d9ee264f85b15633f56d540b44066e681979a5fc`](https://github.com/trbrewer/puckworks/commit/d9ee264f85b15633f56d540b44066e681979a5fc)  
**Last Paper B2-specific content commit:** [`f7e2d4b33eff85b696c8ebe283129d17fab5ab86`](https://github.com/trbrewer/puckworks/commit/f7e2d4b33eff85b696c8ebe283129d17fab5ab86)  
**Manuscript file:** [`docs/PAPER_B2_TEMPORAL_DRAFT.md`](https://raw.githubusercontent.com/trbrewer/puckworks/d9ee264f85b15633f56d540b44066e681979a5fc/docs/PAPER_B2_TEMPORAL_DRAFT.md)  
**Review date:** 25 July 2026  
**Review type:** second-round scientific, statistical, numerical, editorial, and reproducibility review

---

## Editorial recommendation

# Major revision before journal submission

The revised manuscript is materially better than the version assessed in the first review. It now states that the principal 9-bar object is a differentiated, smoothed, aligned, interpolated, five-shot mean rather than a raw shot; identifies the emitted dispersion columns as pointwise standard errors rather than standard deviations; acknowledges that the empirical \(\Phi(t)\) input is partly derived from the same flow subsequently reconstructed; describes the cubic as a same-trace descriptive comparator; limits the block-resampling result to a conditional dependence-sensitivity exercise; and presents the recorded-pressure substitution as a robustness check rather than a mechanism result. The retitled manuscript also expresses its inverse-problem thesis more accurately.

The central numerical result is reproducible: on the committed 15–95 s mean trajectory, temporal descriptions reconstruct the curve much more closely than the tested time-invariant descriptions. That result is useful and publishable in principle.

The manuscript is not yet ready for journal submission because the decisive analyses remain undone. The independent experimental unit is the shot, but the primary inferential object remains one preprocessed mean trajectory. The \(\Phi(t)\) trajectory still reuses target information from the same campaign and has not been cross-fitted. The flexible comparator is still fitted and scored on the same trace. The pressure-level “LOPO” analysis withholds only one equilibrium calibration point while retaining the common temporal template and donor assumptions. Accordingly, the paper currently supports a strong **mean-trajectory reconstruction** claim, not a held-out-shot prediction claim and not mechanism identification.

There are also several correctable but important discrepancies between manuscript, code, metadata, and generated evidence: the residual paragraph combines statistics evaluated at different time resolutions; the equilibrium-calibration description says 110–120 s although the committed analysis uses the final point of a 0–100 s common grid; the block-resampling equations do not precisely describe the implemented algorithm; aggregate cross-pressure means hide a real pressure-dependent rank reversal; supporting code still calls \(\Phi(t)\) “parameter-free” and the cubic a “floor”; and the committed Paper B manifest is dirty, stale, bundle-mismatched, and incomplete for Paper B2.

The proper next step is not another prose-only down-scoping pass. It is the shot-level, cross-fitted analysis already identified in the repository’s own action plan, followed by a clean Paper B2-specific release.

---

## 1. Overall assessment

### 1.1 Principal strengths

1. **The scientific question is important and well chosen.** The manuscript addresses a recurring error in espresso modeling: treating an integrated outlet trace as though it directly measured a unique internal mechanism.
2. **The null-first logic is valuable.** Separating a machine-side capacity example, static material descriptions, a mechanism-motivated temporal construction, and a flexible descriptive comparator is conceptually strong.
3. **The revised manuscript is unusually transparent about evidence provenance.** The observation-operator paragraph is a major improvement and should remain prominent.
4. **The headline numerical ladder is reproducible.** My independent reimplementation reproduces all five primary 9-bar RMSE values to substantially greater precision than reported in the manuscript.
5. **The manuscript generally resists mechanism overclaiming.** The discussion correctly recognizes that similar outlet curves can arise from multiple latent state histories.
6. **The proposed intervention program points in the right direction.** Pressure steps, reversal, rebrewing, and spatial end-state measurements are much more discriminating than fitting another smooth curve to the same trace.
7. **The repository already acknowledges the essential missing work.** Its action plan explicitly defers per-shot analysis, leave-one-shot-out cross-fitting, shot-level uncertainty with refitting, a held-out flexible comparator, first-class residual diagnostics, and a clean Paper B2 release. That candor is commendable.

### 1.2 Central limitation

The paper currently has approximately 800 scored time points but only **one primary mean trajectory**, constructed from **five independent 9-bar shots**. The 800 points are temporally dependent and have passed through differentiation, smoothing, alignment, interpolation, and averaging. Treating the time coordinates as though they provided experimental replication would be pseudoreplication. The fixed-loss moving-block exercise accounts partially for serial dependence within this one derived curve, but it cannot estimate between-shot variability, test held-out-shot prediction, or propagate refitting uncertainty.

The central conclusion should therefore remain at this level until the shot-level analysis is complete:

> A same-campaign, target-informed temporal construction follows the committed preprocessed mean 9-bar trajectory much better than the tested constant and static descriptions. The current analysis does not yet establish held-out-shot performance, an independently measured state trajectory, or a unique poroelastic–dissolution mechanism.

---

## 2. What has changed since the first review

| First-review issue | Current status | Second-round assessment |
|---|---|---|
| The 9-bar curve was described too much like a single raw measurement | **Substantially resolved in prose** | The observation operator now states that the curve is a differentiated, approximately 3 s-smoothed, aligned, interpolated, five-shot mean. This must be propagated to all table titles and figure captions. |
| `*_std` columns were treated ambiguously | **Resolved in prose** | The draft now correctly states that the upstream formatter uses `DataFrame.sem()`. |
| \(\Phi(t)\) was presented as parameter-free or external | **Partially resolved** | The manuscript now acknowledges same-campaign target reuse, but code and generated labels still use “parameter-free,” “zero free parameters,” and similar language. Cross-fitting is still absent. |
| Cubic described as a floor/bound | **Partially resolved** | Main prose calls it a same-trace descriptive benchmark, but the same paragraph, Table 1, Figure 2 caption, and code still use “floor” or “bound.” |
| Block intervals presented too much like uncertainty on the full analysis | **Substantially resolved in prose** | The draft now calls them conditional fixed-loss sensitivity intervals, but the mathematical description does not match the implementation exactly and they remain secondary evidence only. |
| No recorded-pressure robustness check | **Resolved for 9 bar** | The substitution changes static and \(\Phi(t)\) RMSE by less than 0.001 g s⁻¹. Cross-pressure pressure-node sensitivity remains to be shown. |
| Viscosity/Gagné material was underdeveloped | **Mostly resolved** | The detailed material was removed and reserved for a follow-up. A brief viscosity paragraph and a companion-paper composition claim remain; these should be shortened further or explicitly sourced. |
| Shot-level experimental-unit analysis | **Open and essential** | Explicitly deferred in the repository action plan. |
| Cross-fitted \(\Phi(t)\) | **Open and essential** | Explicitly deferred. |
| Shot-level uncertainty with refitting | **Open and essential** | Explicitly deferred. |
| Held-out flexible comparator | **Open and essential** | Explicitly deferred. |
| Paper B2-specific clean release | **Open and essential** | Current manifest is not release-fresh and does not certify all manuscript numbers. |
| Residual diagnostics | **Partially resolved** | Mentioned more prominently, but the headline ACF/DW sentence mixes time resolutions and figures remain specifications rather than results. |
| LOPO terminology and fold reporting | **Partially resolved** | The caveat is present, but “LOPO held out” still overstates what is withheld. Fold-level behavior is not shown. |

The revision has therefore succeeded as an **accuracy and scope correction**, but not yet as the substantive statistical revision required for submission.

---

## 3. Priority revision matrix

### P0 — required before submission

| Priority | Required revision | Why it is essential | Minimum acceptance criterion |
|---:|---|---|---|
| P0.1 | Run the complete model ladder on each individual 9-bar shot | The shot is the independent experimental unit | Report per-shot scores, distributions of paired score differences, and the number of shots on which each branch performs better; show all five traces and residuals |
| P0.2 | Leave-one-shot-out cross-fit \(\Phi(t)\) | The present temporal state partly reuses the target flow | For each held-out shot, construct every mean, TDS/dissolved-mass trajectory, sigmoid parameter, and preprocessing choice without that shot; score only the held-out shot |
| P0.3 | Replace fixed-loss intervals as primary uncertainty | Current intervals condition on one derived mean and fixed fits | Use shot-level paired uncertainty with all eligible fitting/preprocessing repeated inside each resample or fold; retain block resampling only as a secondary within-curve sensitivity |
| P0.4 | Add a genuinely held-out flexible temporal comparator | The same-trace cubic says only that a smooth curve can fit | Use a penalized spline, Gaussian-process mean, or another prespecified smooth comparator evaluated by held-out shot and/or leave-segment-out prediction |
| P0.5 | Correct equilibrium-data provenance | Manuscript says 110–120 s; committed code uses the last point on a 0–100 s grid | Recompute from the stated 110–120 s source statistic or rewrite Methods to state exactly what the repository uses; quantify any resulting change in \(P_c\), \(Q_c\), \(Q^2\), and trace scores |
| P0.6 | Recast the pressure “LOPO” result | Only the equilibrium point is excluded; the temporal trajectory is reused | Rename it “leave-one-pressure-out equilibrium-calibration sensitivity” or equivalent; publish every fold and avoid “held-out trace validation” unless the temporal construction is also withheld |
| P0.7 | Make residual diagnostics internally consistent | Current ACF and DW summary combines different sampling scales | Report ACF and DW at the same declared resolution, provide residual-vs-time and ACF panels for every branch, and compare residual magnitude with shot-to-shot variability |
| P0.8 | Produce a clean B2-specific reproducibility release | Current manifest is dirty, stale, bundle-mismatched, and incomplete | Clean tree; immutable source commit; bundle commit equals source; `release_fresh=true`; exact environment; hashes; claim map covering every reported number; generated figures and source tables |
| P0.9 | Remove code/manuscript semantic drift | Regeneration can restore claims the manuscript has disavowed | Replace “parameter-free,” “zero-param,” “floor,” and “genuinely held-out trace” throughout code, JSON keys, verdicts, tests, and documentation; add CI assertions for evidence-tier labels |
| P0.10 | Correct the `solids_calibration.csv` model-string sign | Metadata disagrees with implementation | Change the documentation string from \(1-\tanh\) to \(1+\tanh\), rebuild pinned hashes and snapshots, and verify numerical identity |

### P1 — strongly recommended

| Priority | Revision | Minimum acceptance criterion |
|---:|---|---|
| P1.1 | Show cross-pressure heterogeneity rather than only macro means | Per-pressure table/plot, fold-level scores, rank changes, and sensitivity to equal-pressure versus shot-weighted averaging |
| P1.2 | Define model domains and boundary nodes | Declare nominal pressure, recorded basket pressure, fitted equilibrium pressure, and model-valid pressure range for every analysis |
| P1.3 | Expand parameter provenance into a dependency graph | For every branch, identify direct target use, indirect target use, same-shot use, same-campaign use, literature inputs, fitted stages, and held-out status |
| P1.4 | Correct the block-resampling Methods | Describe sampling paired squared-loss sequences through common block indices, not sampling only the difference sequence; state resample count, circular/non-circular convention, block construction, and random seed |
| P1.5 | Add complementary metrics | At least RMSE, MAE, mean bias, standardized residual scale, and shape diagnostics; avoid treating one scalar as complete evidence |
| P1.6 | Operationalize the intervention program | Prespecified perturbation magnitude, timing, measured nodes, controls, expected directional contrast, decision threshold, replicate plan, and artifact checks for each experiment |
| P1.7 | Complete figures and supplementary files | Replace “Figure near here” specifications with generated figures and machine-readable source data |
| P1.8 | Broaden the methodological literature | Add model discrimination, structural identifiability/observability, inverse problems with smoothed integrated observables, dependent-data validation, and optimal experimental design literature |

### P2 — editorial and production

Correct cross-references, LaTeX, stale date, placeholder author/funding declarations, inconsistent terminology, table captions, and minor grammar before submission.

---

## 4. Major scientific and statistical comments

### 4.1 The experimental unit must be the shot

#### Finding

The manuscript now correctly states that the primary 9-bar curve is an across-shot mean of five shots. Nevertheless, every headline score, residual sequence, window analysis, and block-resampling interval is still calculated on that one derived mean curve.

#### Why it matters

A mean trajectory can answer a descriptive question—how closely several functions reconstruct the average processed curve—but it cannot show whether the ranking is stable across shots. Averaging can suppress amplitude variation, timing variation, local oscillations, and between-shot structural differences. It can also make a smooth temporal template appear stronger because idiosyncratic shot behavior has been averaged away.

The approximately 800 time samples are not 800 independent experimental replicates. They are serially dependent points from a filtered and interpolated signal. The effective number of independent units for the primary 9-bar experiment is five.

#### Required analysis

For each of the five individual 9-bar files:

1. apply an explicitly frozen observation operator;
2. evaluate the static equilibrium branch without using that shot’s outcome beyond allowed boundary inputs;
3. evaluate a properly cross-fitted \(\Phi(t)\) branch;
4. fit and evaluate the constant and flexible branches under clearly separated same-shot and held-out modes;
5. report RMSE, MAE, bias, residual structure, and key temporal shape errors;
6. report paired differences shot by shot rather than inferential statistics over time points.

The manuscript should show a “shots won” summary only as a transparent descriptive count, not as a high-powered hypothesis test with \(n=5\). Exact paired plots are more informative than asymptotic p-values here.

#### Acceptance criterion

A reader should be able to see whether the mean-trajectory ranking holds on all, most, or only some individual shots, and whether the apparent advantage comes from amplitude, phase, endpoint, or overall shape.

---

### 4.2 Target reuse in \(\Phi(t)\) must be removed from the held-out analysis

#### Finding

The revision now acknowledges “soft circularity”: cumulative dissolved mass is constructed from total dissolved solids and flow from the same campaign, and the resulting sigmoid is then used to reconstruct flow. The manuscript’s statement that no coefficient is fitted *directly* to the scored \(Q(t)\) trace is narrowly true but does not imply target independence.

#### Why it matters

A feature or latent trajectory that contains the outcome can reconstruct that outcome well even when the constitutive interpretation is wrong. This is not necessarily invalid for a same-campaign reconstruction study, but it must not be presented as predictive evidence.

The relevant question is not merely whether the final flow equation has a coefficient fitted against \(Q\). It is whether any branch input, parameter, alignment choice, temporal template, or preprocessing statistic was learned using the held-out outcome.

#### Required analysis

Use an outer leave-one-shot-out loop. For each held-out shot:

- remove it before forming pressure-level means;
- remove it before forming any TDS or dissolved-mass trajectory;
- refit the sigmoid and any equilibrium quantities that depend on the training shots;
- freeze the resulting trajectory;
- predict the held-out shot on its native or prespecified processed grid;
- record all failed or unavailable folds rather than silently changing the input lineage.

Where flow is mathematically required to form cumulative dissolved mass for the same held-out shot, the branch cannot be called independently predictive unless that flow is supplied by an independent measurement stream or a separately predicted quantity. The manuscript should distinguish:

- **reconstruction using measured contemporaneous state inputs**;
- **cross-fitted prediction using training-shot state trajectories**; and
- **mechanistic prediction from independently measured latent states**.

These are different evidence tiers.

---

### 4.3 Separate the four evidence tiers throughout the paper

The current paper still blends materially different validation levels. I recommend explicit labels in every table and figure:

| Evidence tier | Example in current paper | Defensible interpretation |
|---|---|---|
| Same-trace fit | Best constant and cubic fitted and scored on the mean 9-bar curve | Descriptive reconstruction capacity only |
| Same-campaign target-informed reconstruction | Empirical \(\Phi(t)\) at 9 bar | Reconstruction using an imported but partly target-derived temporal input |
| Equilibrium-calibration holdout | Pressure LOPO refits \(P_c,Q_c\) without one equilibrium point | Sensitivity of equilibrium calibration and conditional trace reconstruction |
| Genuine held-out prediction | Not yet present | Model and all learned inputs frozen without the held-out shot/condition |

A fifth tier—external transportability to a different rig, coffee, grinder, preparation protocol, or operator—is also absent and should be described as future validation.

The phrase “held-out trace” should not be used for the current pressure LOPO because most of the temporal model is not held out. The manuscript itself acknowledges this caveat, but the table label, figure caption, code docstrings, JSON keys, and verdict text still imply a stronger test.

---

### 4.4 The residual summary mixes two time resolutions

#### Finding

The manuscript states that lag-1 residual autocorrelation is approximately 0.99 in every branch and that the mean **decimated** Durbin–Watson statistic is approximately 0.01. The independent audit indicates that the approximately 0.99 ACF values are the native approximately 10 Hz values, whereas the reported DW statistic is described at a 1 s decimation. Those should not be paired as though they characterize the same process at the same lag.

#### Independent results

| Branch | ACF(1), native ~10 Hz | DW, native ~10 Hz | ACF(1), 1 s decimated | DW, 1 s decimated |
|---|---:|---:|---:|---:|
| Best constant | 0.9958 | 0.00009 | 0.9579 | 0.00489 |
| Late constant | 0.9958 | 0.00007 | 0.9579 | 0.00389 |
| Static poroelastic | 0.9958 | 0.00007 | 0.9579 | 0.00380 |
| Empirical \(\Phi(t)\) | 0.9985 | 0.00150 | 0.9687 | 0.04676 |
| Same-trace cubic | 0.9911 | 0.00222 | 0.8931 | 0.06841 |

The conclusion—strong residual structure—survives. The numerical summary does not.

#### Required revision

- Choose and declare one sampling interval for headline residual statistics.
- Report the physical lag represented by ACF(1).
- Plot the ACF across multiple physical lags rather than reporting one lag only.
- Show residual-vs-time panels for every branch.
- Add a periodogram or another low-frequency lack-of-fit diagnostic if scientifically interpretable.
- Overlay individual-shot variability or an empirical shot envelope. A pointwise SEM band alone does not encode temporal covariance.

As a supplementary diagnostic, the independent audit finds RMS residuals of approximately 10.26, 9.67, 9.74, 1.81, and 1.43 pointwise SEM units for the best constant, late constant, static, \(\Phi(t)\), and cubic branches respectively. This reinforces lack of fit, but it is not a formal standardized likelihood because the SEM sequence is correlated and inherits preprocessing.

---

### 4.5 Rename and fully expose the pressure-level LOPO analysis

#### Finding

The current LOPO procedure excludes one long-run pressure–flow point when fitting \(P_c,Q_c\), then reconstructs the full trace at that pressure while retaining the common 9-bar dissolved-mass trajectory and donor assumptions.

#### Correct interpretation

This is a useful **leave-one-pressure-out equilibrium-calibration sensitivity analysis**. It tests whether one equilibrium point dominates the two-parameter calibration. It does not independently validate the temporal trajectory or show that the full trace was held out from every stage.

#### Independent audit

- Equilibrium-curve \(Q^2\): **0.8057**
- Equilibrium-point LOPO RMSE: **0.2755 g s⁻¹**
- Mean trace RMSE under equilibrium-calibration LOPO: static **0.5340**, \(\Phi(t)\) **0.3470** g s⁻¹

The fold errors are not uniform. The equilibrium prediction residuals are particularly notable at the low- and high-pressure edges and around 5 bar. Edge folds are partly extrapolative and should be identified as such.

#### Required reporting

Publish a fold table containing:

- nominal pressure;
- recorded basket pressure used in equilibrium fitting;
- observed equilibrium statistic and its derivation;
- fitted \(P_c,Q_c\) without that pressure;
- equilibrium prediction and residual;
- static, \(\Phi(t)\), and RC-3b trace metrics;
- whether the fold is interpolation or edge extrapolation;
- number of shots contributing to the pressure mean.

Rename Table 3’s first row from “LOPO held out, all 11 pressures” to “Equilibrium-calibration LOPO, all 11 pressure means.”

---

### 4.6 Aggregate cross-pressure means hide a scientifically important rank reversal

The manuscript says that no branch is best at every pressure, but the principal table reports only macro means. The omitted fold detail is not incidental; it changes the scientific interpretation.

#### Independent shared-calibration RMSEs

| Nominal pressure (bar) | Static RMSE | Empirical \(\Phi(t)\) RMSE | Lower RMSE |
|---:|---:|---:|---|
| 1.0 | 0.431 | 0.374 | \(\Phi(t)\) |
| 2.0 | 0.649 | 0.573 | \(\Phi(t)\) |
| 3.5 | 0.306 | 0.418 | Static |
| 4.0 | 0.246 | 0.374 | Static |
| 5.0 | 0.402 | 0.456 | Static |
| 6.0 | 0.453 | 0.502 | Static |
| 7.0 | 0.551 | 0.222 | \(\Phi(t)\) |
| 8.0 | 0.575 | 0.118 | \(\Phi(t)\) |
| 9.0 | 0.648 | 0.116 | \(\Phi(t)\) |
| 11.0 | 0.693 | 0.173 | \(\Phi(t)\) |
| 13.0 | 0.809 | 0.354 | \(\Phi(t)\) |

The temporal branch’s mean advantage is driven primarily by the 7–13 bar conditions; the static branch is better throughout the 3.5–6 bar middle group. This pattern may reflect pressure-dependent omitted physics, pressure-node mismatch, reuse of the 9-bar temporal shape, model-domain limitations, or changes in the observation operator. It is more scientifically interesting than the macro mean alone.

#### Required revision

- Promote the per-pressure plot to the main text.
- Report exact fold scores, not only qualitative prose.
- State that the reported mean is an unweighted macro-average across pressure means.
- Add sensitivity to weighting by number of shots and, cautiously, uncertainty.
- Avoid post hoc regime labels unless thresholds are prespecified or independently motivated.
- Test whether using recorded pressure histories across all pressures alters the rank pattern.

---

### 4.7 The equilibrium statistic described in Methods does not match the committed analysis

#### Finding

The manuscript states that long-run flow for the equilibrium relation was summarized over **110–120 s**. The committed Puckworks loader/fit used by `steady_state_curve()` instead takes the final value of the preprocessed common-grid trace, and the source formatter used for the committed data truncates/interpolates to **0–100 s**. My independent audit therefore reproduces the calibration from the 100 s endpoint, not a 110–120 s average.

#### Why it matters

This is a provenance mismatch in a parameter set used throughout the static and temporal ladders. It may or may not materially alter the conclusions, but the Methods cannot describe one statistic while the code evaluates another.

#### Required revision

Choose one of two defensible routes:

1. **Source-faithful route:** obtain or reconstruct the 110–120 s values used by the source study, refit \(P_c,Q_c\), and regenerate every dependent number; or
2. **Repository-observable route:** state explicitly that Puckworks uses the final 100 s value of each preprocessed pressure mean as its equilibrium proxy, explain why, and avoid attributing that proxy to the source paper’s 110–120 s method.

In either route, provide a sensitivity table comparing endpoint, 90–100 s mean, and source 110–120 s statistic where available.

The manuscript should also reconcile the statement “60 brews” with the exact files actually included, excluded, and aggregated at each pressure. A compact shot-accounting table is needed.

---

### 4.8 The block-resampling equations do not exactly describe the implementation

#### Finding

Section 4.2 defines one difference sequence,

\[
d_i=e_{A,i}^2-e_{B,i}^2,
\]

and says contiguous blocks of \(d_i\) are resampled before recomputing RMSE differences. The current implementation instead samples common block indices and computes

\[
\sqrt{\operatorname{mean}(e_A^2\text{ at sampled indices})}
-
\sqrt{\operatorname{mean}(e_B^2\text{ at sampled indices})}.
\]

Because of the square root, that result cannot in general be reconstructed by resampling the difference sequence \(d_i\) alone.

#### Required Methods wording

State that contiguous blocks of **paired squared-loss sequences** \((e_{A,i}^2,e_{B,i}^2)\) are selected through the same sampled indices, and that the RMSE for each branch is recomputed before differencing. Document:

- overlapping versus non-overlapping blocks;
- circular versus non-circular endpoints;
- sampling with replacement;
- block size in seconds and samples;
- number of blocks per replicate;
- truncation to the original length;
- resample count;
- random seed;
- percentile interval definition.

The independent 10,000-resample audit reproduces the qualitative result:

| Block duration | \(\Phi-\)constant median [95% interval], g s⁻¹ | \(\Phi-\)cubic median [95% interval], g s⁻¹ |
|---:|---:|---:|
| 4 s | −0.419 [−0.580, −0.256] | +0.0247 [−0.0084, +0.0570] |
| 8 s | −0.386 [−0.591, −0.221] | +0.0217 [−0.0100, +0.0530] |
| 16 s | −0.308 [−0.544, −0.219] | +0.0235 [−0.0005, +0.0393] |
| 24 s | −0.306 [−0.511, −0.230] | +0.0215 [+0.0010, +0.0403] |

This is a useful dependence sensitivity on the fixed mean-curve losses. It must remain subordinate to shot-level uncertainty.

---

### 4.9 Define pressure nodes and model domains more rigorously

The recorded-pressure substitution at 9 bar is a welcome addition. It does not close the boundary-condition question across the full pressure campaign.

The manuscript should provide a table distinguishing:

- nominal machine setting;
- recorded pump pressure, group/headspace pressure, and basket pressure where available;
- pressure used in the equilibrium calibration;
- pressure used pointwise in the temporal reconstruction;
- whether a pressure is a gauge or absolute quantity;
- whether the model is evaluated inside its declared calibration/domain range.

The repository model documentation itself states that the closed-form approximation is quantitatively poor below approximately 5 bar and is bounded by the fitted characteristic pressure at the top end. Those pressures are currently included in aggregate transfer scores. Low-pressure and top-boundary results should therefore be labeled stress tests rather than equivalent validation conditions, or the model should be evaluated using the source’s full relation if available.

The recorded-pressure robustness should be extended to all pressure traces. The 9-bar result shows that small drift does not explain the 9-bar rise; it does not show that nominal-pressure use is harmless for the cross-pressure rank pattern.

---

### 4.10 Parameter count must be replaced by parameter and information provenance

Table 1 is an improvement, but “coefficients fitted to this trace” is too narrow to communicate effective flexibility. A branch can use zero coefficients in the final flow equation while importing a temporal trajectory learned from the target outcome.

Add these columns:

| Field | Purpose |
|---|---|
| Direct access to scored \(Q(t)\) | Whether the branch was fitted against the target flow values |
| Indirect access to scored \(Q(t)\) | Whether any input such as dissolved mass contains the same flow |
| Same-shot information used | Critical for held-out-shot claims |
| Same-pressure information used | Critical for pressure transfer |
| Same-campaign information used | Distinguishes internal transfer from external validation |
| Learned numerical parameters | Values and fitting targets |
| Fixed functional form/source | Literature or project-synthesis provenance |
| Alignment/preprocessing learned from target | Timing can itself leak target information |
| Evaluation mode | Same-trace fit, cross-fit, holdout, or external |
| Validity domain | Pressure, saturation interval, apparatus, coffee, grind, control mode |

A compact directed acyclic graph should show the lineage

\[
Q(t),\;\mathrm{TDS}(t)\rightarrow m_d(t)\rightarrow \text{sigmoid parameters}
\rightarrow \Phi(t)\rightarrow \widehat Q(t).
\]

That graph will make the soft circularity immediately intelligible.

---

### 4.11 Reproducibility is not release-ready

The current [`paper_b_manifest.json`](https://raw.githubusercontent.com/trbrewer/puckworks/d9ee264f85b15633f56d540b44066e681979a5fc/docs/reproducibility/paper_b_manifest.json) reports:

- `source_commit = 52cbc060...`, which predates the latest B2-specific content commit;
- `git_dirty = true`;
- `bundle_source_commit = ed504769...`;
- `bundle_matches_head = false`;
- `release_fresh = false`;
- 18 verified claims, many belonging to broader Paper B work rather than Paper B2.

The claim map verifies the best constant, \(\Phi(t)\), cubic, one cross-pressure mean, one LOPO mean, maximum drift, and one block median. It does not certify all of the following manuscript claims:

- late-window constant RMSE;
- static 9-bar RMSE;
- full Table 3 values including RC-3b;
- equilibrium \(Q^2\) and fold-level values;
- recorded-pressure shifts;
- alternate-window scores;
- all block endpoints and block-length sensitivity;
- residual ACF and DW values;
- swelling magnitude, RMSE, and correlation;
- figure data;
- exact observation-operator metadata.

A Paper B2 release should be separate from a broad Paper B manifest. Every printed number should map to a machine-readable path, tolerance or exact representation, source commit, dependency hashes, and a generated figure/table artifact. A manuscript assertion that figures “should be regenerated” is not enough at submission.

---

### 4.12 Code and manuscript terminology are out of sync

The manuscript now avoids several overclaims, but supporting code retains them. Examples in the reviewed files include:

- the poroelastic module describes \(Q(t)\) as a “parameter-free predictor”;
- validation prose calls the dynamic equation “parameter-free”;
- the ladder records `free_params` for \(\Phi(t)\) as zero without representing upstream target-derived parameters;
- the cubic is called a “flexible floor” and results include `rung4_beats_floor`;
- verdict text says a “ZERO-param” construction nearly reaches the floor;
- cross-pressure code calls the procedure “genuinely held-out” trace prediction;
- result keys use `heldout_mean` even though the temporal template is retained.

This is not merely stylistic. A regeneration pathway can reintroduce obsolete evidentiary language into tables, JSON, notebooks, or subsequent papers. The code should use an evidence ontology such as:

- `same_trace_fitted`;
- `same_campaign_target_informed`;
- `equilibrium_calibration_lopo`;
- `shot_cross_fitted`;
- `external_validation`.

Add tests that fail when a branch with indirect target access is labeled parameter-free or independently held out.

---

### 4.13 The intervention program needs testable protocols, not only directional narratives

Table 4 is a useful hypothesis matrix, but several statements are stronger than the present protocol supports. For example, reversal asymmetry or an outlet deposit would **support** a fines-migration contribution, not automatically establish it; valves, screens, plumbing asymmetry, puck fracture, and imaging artifacts can produce similar observations.

For each intervention, specify:

1. treatment and control conditions;
2. pressure/flow waveform, amplitude, onset, and duration;
3. every pressure node and flow observable;
4. primary outcome and analysis window;
5. directional prediction for each mechanism;
6. minimum effect considered informative;
7. replicate count rationale;
8. randomization and preparation blocking;
9. null/inert-load control;
10. sensor response and machine-transient subtraction;
11. artifact/failure criteria;
12. preregistered decision rule.

Examples:

- **Pressure step:** use an inert porous load to estimate machine-only transient; compare post-step residual after subtracting the static hydraulic jump.
- **Flow reversal:** independently characterize plumbing/screen directional asymmetry before using a coffee bed.
- **Spent-puck rebrew:** control rest time, unloading, resaturation, temperature, and retained liquid.
- **Depth-resolved end state:** preregister quantitative spatial features rather than relying on qualitative images.

The intervention section could become a major strength if converted into an executable experimental-design supplement.

---

### 4.14 The “machine-only null” is a capacity counterexample, not a calibrated statistical null

The manuscript is careful to say that the Foster model is not fitted to the Waszkiewicz apparatus. Nevertheless, repeatedly calling it a “null” risks suggesting that it was quantitatively tested against the same data.

A more precise label is **machine-side capacity counterexample** or **boundary-system capacity model**. Its role is logical: the existence of a plausible machine/filling system that generates dip-and-recovery shows that the shape alone is non-identifying. It does not estimate the probability that the Waszkiewicz trace was machine-generated.

Keep the two evidence objects visually separated in Figure 1 and avoid overlaying normalized curves in a way that encourages quantitative comparison.

---

## 5. Independent numerical audit

I independently reconstructed the committed 9-bar ladder, window sensitivity, recorded-pressure substitution, residual diagnostics, fixed-loss block sensitivity, equilibrium LOPO, and shared/LOPO cross-pressure summaries from the repository’s committed tables and equations. The audit is not a substitute for the missing shot-level analysis, but it provides a check on numerical transcription.

### 5.1 Primary 9-bar ladder

Scored points: **800** on 15.015–94.995 s.

| Branch | Manuscript RMSE | Independently reproduced RMSE (g s⁻¹) | Status |
|---|---:|---:|---|
| Best constant | 0.573 | 0.572855540 | Reproduced |
| Late-window constant | 0.641 | 0.640589012 | Reproduced |
| Static poroelastic | 0.648 | 0.647696048 | Reproduced |
| Empirical \(\Phi(t)\) | 0.116 | 0.115769387 | Reproduced |
| Same-trace cubic | 0.096 | 0.096396396 | Reproduced |

This confirms the paper’s descriptive mean-trajectory ranking.

### 5.2 Recorded-pressure substitution at 9 bar

| Branch | Nominal-pressure RMSE | Recorded-pressure RMSE | Change |
|---|---:|---:|---:|
| Static poroelastic | 0.647696048 | 0.646846387 | −0.000849661 |
| Empirical \(\Phi(t)\) | 0.115769387 | 0.116442521 | +0.000673134 |

The conclusion that small recorded pressure drift does not explain the 9-bar rise is numerically supported.

### 5.3 Window sensitivity

| Scoring window | Best constant | Static | Empirical \(\Phi(t)\) | Cubic |
|---|---:|---:|---:|---:|
| 10–90 s | 0.6754 | 0.7930 | 0.1170 | 0.1283 |
| 15–95 s | 0.5729 | 0.6477 | 0.1158 | 0.0964 |
| 20–90 s | 0.4833 | 0.5337 | 0.1097 | 0.0616 |

The temporal-versus-static conclusion is stable. The ordering between \(\Phi(t)\) and the cubic is not: \(\Phi(t)\) is better on 10–90 s, while the cubic is better on the other two windows. This strongly supports treating the cubic comparison as unresolved and window-dependent.

### 5.4 Equilibrium LOPO

- \(Q^2 = 0.805678815\)
- equilibrium-point LOPO RMSE = **0.275530495 g s⁻¹**

The largest absolute equilibrium residuals occur at 5 bar and at low/high edge conditions. The full fold table should be published.

### 5.5 Cross-pressure means

| Assessment | Static | Empirical \(\Phi(t)\) |
|---|---:|---:|
| Shared calibration, all 11 pressures | 0.523934 | 0.334465 |
| Shared calibration, 10 off-9 pressures | 0.511558 | 0.356335 |
| Equilibrium-calibration LOPO, all 11 pressures | 0.534014 | 0.347019 |

These values reproduce the reported aggregate result but should not replace fold-level reporting.

### 5.6 Audit conclusion

The manuscript’s main numerical transcription is reliable for the committed preprocessed mean data. The outstanding concerns are inferential and provenance-related, not a failure to reproduce the headline RMSE values.

---

## 6. Section-by-section comments

Line references below correspond to the exact-commit Markdown downloaded for this review; they may shift after editing.

### Title

**Current:** *One flow curve, many explanations: null-first inference for machine and porous-bed dynamics in espresso*

The revised title is strong. “Explanations” is more defensible than “causes,” and “espresso” is explicit. Keep it.

Consider whether “null-first” will be immediately intelligible to a broad journal readership. The manuscript defines it well, so no change is essential. A slightly more descriptive alternative would be:

> **One espresso flow curve, many explanations: distinguishing machine response, static resistance, and temporal porous-bed dynamics**

The current title is shorter and probably preferable.

### Draft status and metadata

- Update the stale “15 July 2026” draft date.
- Replace author, corresponding-author, funding, competing-interest, and acknowledgment placeholders before circulation as a submission candidate.
- The draft-status warning is appropriate during development but should be removed once the clean release exists.

### Abstract

1. Grammar: “Conditional block-resampling ... **but do not resolve**” should be “**but does not resolve**.”
2. Retain the explicit statement that the 9-bar object is an averaged, smoothed, differentiated curve.
3. Add one sentence stating that shot-level cross-validation has not yet been performed, unless that analysis is completed before submission.
4. “Leave-one-pressure-out assessment ... preserves the aggregate advantage” is acceptable only if renamed to clarify equilibrium-calibration holdout.
5. “Temporal flexibility” is the right phrase. Avoid returning to “temporal dynamics are required” without the model-relative qualifier.
6. The abstract is dense. After the missing analyses are completed, reduce the number of parenthetical caveats by using explicit evidence-tier labels.

### Introduction

- The logical framing is strong.
- In the contribution statement, “can establish the need for temporal dynamics” remains stronger than the revised abstract. Use “can provide evidence against specified time-invariant descriptions” or “can support temporal flexibility relative to specified static descriptions.”
- “Machine-only null” should be replaced by “machine-side capacity counterexample” at least on first use.
- Add a brief paragraph distinguishing structural non-identifiability from practical uncertainty and from simple lack of fit. The paper currently uses the concepts correctly but does not name them systematically.

### Section 2: Data and observable definitions

- The observation-operator paragraph is one of the best additions and should be retained.
- Correct the cross-reference “Limitations, §7”; Limitations is §8 in the current manuscript.
- Add a pressure-by-pressure shot-accounting table.
- State the exact source fields used to locate the pressure-stabilization start index.
- Explain whether the alignment uses outcome-related flow information, pressure only, or another signal. Alignment can be a source of information leakage in held-out analyses.
- Explain boundary handling of the 31-sample Savitzky–Golay filter.
- State whether differentiation precedes or follows filtering of mass; the current prose says differentiation and then filtering of flow, which should match code exactly.
- Correct the 110–120 s versus 100 s equilibrium mismatch.
- Use “preprocessed pressure-level mean trajectory” rather than “measured trace” in table and figure titles.

### Section 3: Model-comparison ladder

- Equation for the cubic contains a malformed LaTeX token: `Q_{\text{cub}}` is rendered in the source as `Q_{<tab>ext{cub}}`. Correct it.
- The cubic paragraph is internally contradictory: it says the cubic is not a lower bound, then refers to “this floor.” Remove “floor” and “bound” everywhere.
- Table 1’s “non-mechanistic flexibility bound” should be “same-trace smooth descriptive comparator.”
- Table 1 should encode indirect target access and same-campaign fitting, not only final-equation parameter count.
- State the actual numeric values and uncertainty/provenance of \(P_c,Q_c,k,\ell,m\) in a supplement.
- RC-3b needs an equation, input lineage, and explicit statement of what is and is not estimated from the Waszkiewicz data.

### Section 4: Statistical and diagnostic analysis

- Correct the block-resampling description to match the paired-loss implementation.
- State whether the primary 1,000-resample result has sufficient Monte Carlo precision; 10,000 resamples would be inexpensive and easier to defend.
- Do not call a percentile range a 95% confidence interval without the conditional qualifier.
- Specify ACF normalization, handling of mean residual, and physical lag.
- Rename LOPO as described above.
- Add a prespecified rule for pressure weighting in macro summaries.
- Clarify that sign tests are deterministic compatibility results under assumptions, not statistical sign tests in the usual sense. “Directional/compatibility constraints” may be a less confusing heading.

### Section 5.1: Machine-side capacity

This section is appropriately cautious. Replace “null” with “capacity counterexample” or explicitly define “null” as a model-class counterexample rather than a calibrated null hypothesis.

### Section 5.2: 9-bar ladder

- Table title should say “preprocessed across-shot mean 9-bar trajectory.”
- The \(\Phi(t)\) cross-reference points to §4.3, which is window sensitivity. Target reuse is discussed in §§2.4 and 3.3 and in Limitations.
- The same incorrect §4.3 cross-reference appears in the explanatory paragraph.
- Replace the mixed-scale residual sentence with a table or same-resolution values.
- Show the actual window-sensitivity values rather than only saying the direction persists.
- Retain the recorded-pressure result, but change “not an artifact” to “is not explained by the small recorded pressure drift represented in this dataset.”
- Avoid treating exclusion of zero in fixed-loss resampling as evidence from independent shots.

### Section 5.3: Cross-pressure assessment

- Rename Table 3’s LOPO row.
- Include RC-3b fold values and full method provenance.
- Show the static-versus-\(\Phi(t)\) rank reversal from 3.5–6 bar.
- Report \(Q^2\) together with equilibrium LOPO RMSE and fold plot.
- Identify edge extrapolation folds.
- State whether every pressure mean uses the same number of shots and observation-operator quality.
- Do not imply that exclusion of an equilibrium point proves the temporal trajectory transfers independently.

### Section 5.4: Sign constraints

- The 4%, 1.08 g s⁻¹, and −0.95 claims require explicit claim-map entries and source-data output.
- The remaining viscosity paragraph is not fatal, but it interrupts a tightly scoped results section. Consider reducing it to one sentence in Discussion: “A concentration-linked viscosity decline has the same forward-trace sign and is therefore another non-identifiable candidate.”
- The statement that a coupled swelling/extraction calculation worsens reconstruction belongs in the companion paper unless the exact model, metric, and provenance are supplied here.
- Keep the distinction between “cannot be the sole positive contribution under this isolation” and “is absent.”

### Section 6: Discriminating experiments

- Replace “would establish a fines-migration contribution” with “would support a fines-migration contribution after machine and screen asymmetry controls.”
- Add quantitative protocols in Supplement S8.
- Add an inert-load machine control as a row or common requirement.
- Add sensor-response calibration and pressure-node identity as explicit experimental factors.
- Add an experimental design for independently measuring concentration/viscosity versus porosity/bed height so that dissolution-linked opening and viscosity can actually be separated.

### Discussion

- “Temporal flexibility is required relative to those nulls” is acceptable when tightly qualified, but “strongly disfavors the tested time-invariant reconstructions” is more precise.
- The LOPO discussion should say that it strengthens confidence in the equilibrium calibration’s stability, not in full temporal-model independence.
- The proposed second rig/coffee study is valuable, but shot-level cross-fitting in the existing data must come first.
- The general null-first sequence is useful and could be retained as a boxed framework or figure.

### Limitations

The limitations section is candid but should add:

1. the exact experimental-unit limitation and \(n=5\) at 9 bar;
2. averaging-induced suppression of between-shot temporal variability;
3. alignment/filtering dependence;
4. equilibrium endpoint mismatch until corrected;
5. macro-averaging across unequal pressure evidence;
6. model-domain limitations at low and edge pressures;
7. same-campaign and same-rig information reuse in the pressure analysis.

### Conclusions

The first sentence, “A flow curve can falsify a static null,” is too categorical for the current mean-trajectory and model-class evidence. A curve can strongly disfavor the tested static reconstructions, but “falsify” implies a sharper model and error structure than currently supplied.

“Temporal dynamics are required” should remain explicitly model-relative and observable-relative. Replace “measured 9-bar trace” with “preprocessed five-shot mean 9-bar trajectory.”

### Data and code availability

The present section describes what should happen before submission. A submitted paper needs the completed archive, not a promise. Include:

- immutable release/tag;
- archive DOI;
- exact source commit;
- environment lockfile;
- commands for every table/figure;
- raw-source acquisition instructions and rights;
- generated source-data tables;
- claim manifest;
- clean-tree and bundle-match status.

### Figures

The manuscript still contains specifications rather than figures. The absence of figures prevents a complete assessment of visual truthfulness, axis choices, uncertainty display, and whether the evidence objects are sufficiently separated.

Specific caption fixes:

- Figure 1: “measured 9-bar rising-flow trace” → “preprocessed five-shot mean 9-bar trajectory.”
- Figure 2: “measured flow” → “preprocessed mean flow”; “in-sample flexibility bound” → “same-trace smooth descriptive comparator.”
- Figure 3: “LOPO held-out RMSE” → “equilibrium-calibration LOPO trace RMSE.”
- Figure 3 should show every pressure and branch, not only summary lines.
- Residual plots should use a common vertical scale or clearly state when scales differ.
- Add shot-level spaghetti plots and held-out predictions after P0 analyses are complete.

### References

Seven references are too few for a paper making a general methodological contribution about inverse inference and model discrimination. Add a systematic and transparent literature search covering:

- identifiability and observability;
- model discrimination and experimental design;
- validation with dependent time series;
- inverse problems for integrated/filtered observables;
- porous-media constitutive non-uniqueness;
- espresso pressure, flow, wetting, rheology, swelling, fines, and spatial heterogeneity.

Do not use the literature section merely to accumulate espresso citations; it should establish the methodological novelty and limitations of the inference framework.

---

## 7. Suggested replacement wording

### 7.1 Suggested abstract before shot-level results are available

> Time-resolved espresso outlet flow is an integrated response of the machine, pressure boundary conditions, wetting, evolving bed resistance, extraction, transport, and measurement pipeline; a visually distinctive curve therefore need not identify a unique porous-bed mechanism. We use a null-first comparison to separate three questions: whether a machine/filling subsystem can generate a commonly mechanized shape, whether tested time-invariant descriptions reconstruct a rising-flow trajectory adequately, and whether a better temporal reconstruction identifies its mechanism. A published pump–headspace–infiltration model generates dip and recovery without bed evolution, providing a machine-side capacity counterexample. For a differentiated, approximately 3 s-smoothed, aligned, interpolated mean of five 9-bar shots over 15–95 s, the best constant and static pressure-dependent poroelastic descriptions have RMSE 0.573 and 0.648 g s⁻¹. A same-campaign dissolution-linked porosity trajectory reaches 0.116 g s⁻¹, although its temporal input is partly constructed from the same flow, while a four-parameter cubic fitted and scored on the same mean trajectory reaches 0.096 g s⁻¹. Conditional block resampling of fixed loss sequences supports the reconstruction advantage of the temporal trajectory over the constant description but does not provide between-shot uncertainty or resolve the temporal trajectory against the same-trace cubic. Leaving one equilibrium pressure point out at a time preserves the aggregate ranking within the same campaign, but pressure-dependent rank reversals and structured residuals indicate omitted dynamics. These results strongly disfavor the tested time-invariant reconstructions for the preprocessed mean observable but do not establish held-out-shot prediction or identify a unique bed mechanism. Shot-level cross-fitting and controlled pressure, reversal, rebrew, and spatial-state experiments are required for stronger discrimination.

After completing the shot-level analysis, replace the last two sentences with the actual held-out-shot result rather than retaining the limitation as a caveat.

### 7.2 Suggested conclusion

> The present evidence supports a narrower conclusion than mechanism identification. A machine/filling model can generate dip-and-recovery without an evolving bed, and the committed preprocessed five-shot mean 9-bar trajectory is reconstructed much more closely by time-varying descriptions than by the tested time-invariant descriptions. However, the dissolution-linked trajectory uses a same-campaign temporal input partly constructed from flow, the cubic is fitted and scored on the same trajectory, the pressure holdout excludes only one equilibrium calibration point, and all branches retain structured residuals. The analysis therefore demonstrates mean-trajectory evidence for temporal flexibility relative to specified static descriptions; it does not yet demonstrate held-out-shot prediction, independently measured porosity evolution, or a unique poroelastic–dissolution mechanism. Shot-level cross-fitting and interventions that force competing mechanisms to predict different directional, hysteretic, or spatial responses are the necessary next tests.

### 7.3 Suggested LOPO terminology

Replace:

> LOPO held out, all 11 pressures

with:

> Leave-one-pressure-out equilibrium-calibration sensitivity, all 11 pressure means

Replace:

> held-out trace prediction

with:

> trace reconstruction using equilibrium parameters fitted without that pressure’s equilibrium point; temporal inputs retained from the common campaign

### 7.4 Suggested block-resampling Methods text

> For each model pair, we retained the two pointwise squared-loss sequences and sampled common indices using overlapping, non-circular contiguous blocks with replacement. Each resample was truncated to the original length. We recomputed each branch RMSE from its resampled squared losses and then formed the RMSE difference. Models and preprocessing were not refitted. The percentile range therefore measures sensitivity of the fixed mean-trajectory loss comparison to local serial dependence; it is not a confidence interval for between-shot performance or for the full fit-and-compare procedure.

Adjust “overlapping” and “non-circular” if the implementation is changed.

### 7.5 Suggested evidence-tier note for every main results table

> Evidence level: same-trace descriptive fit, same-campaign target-informed reconstruction, or equilibrium-calibration holdout as labeled. None of these rows constitutes external validation. A “held-out” label is used only when the outcome and every learned input for the scored unit were excluded from fitting.

---

## 8. Recommended revised analysis architecture

### Stage A — freeze the observation operator

1. Record every raw input file and exclusion reason.
2. Freeze start-time alignment, differentiation, filtering, interpolation, and scoring windows before model comparison.
3. Demonstrate that modest defensible changes to smoothing and alignment do not determine the ranking.
4. Preserve individual shots; compute pressure means only for descriptive visualization.

### Stage B — 9-bar shot-level analysis

For each of five outer folds:

1. hold out one complete shot;
2. build pressure-level/TDS/dissolved-mass training objects from the other four;
3. fit all training-only parameters;
4. fit the flexible comparator using training shots only or use a nested leave-segment scheme;
5. predict the held-out shot;
6. score the same fixed window and report failures;
7. save fold-level predictions and residuals.

Primary estimand:

\[
\Delta_s = L_{s,\text{temporal}}-L_{s,\text{static}},
\]

where \(s\) indexes shots, not time samples.

Report the five paired \(\Delta_s\) values directly, their mean/median, and an uncertainty description appropriate to \(n=5\). Avoid pretending the sample supports precise asymptotic inference.

### Stage C — pressure transfer

Conduct at least three clearly named analyses:

1. **Shared internal reconstruction:** all equilibrium points and one common temporal template.
2. **Equilibrium-calibration LOPO:** current procedure, renamed.
3. **Temporal-template pressure holdout:** where data permit, derive the temporal template without the scored pressure and evaluate transfer.

Report per-pressure folds and model-domain status. Treat low-pressure and edge folds separately if the source model is outside quantitative validity there.

### Stage D — external or prospective validation

Use a second coffee/rig or a prospectively collected replicate campaign. Freeze code and parameters before opening the validation data. Measure at least one independent internal-state observable—bed height/strain, soluble mass, concentration/viscosity, porosity, or fines distribution—so that the problem is not reduced again to one outlet curve.

### Stage E — intervention experiments

Choose one or two highest-information perturbations first rather than attempting all proposals at once. A pressure step with complete pressure-node measurement and an inert-load machine control appears the most direct initial experiment; a spent-puck rebrew is operationally simpler and could provide a rapid falsification screen.

---

## 9. Reproducibility release specification

A Paper B2 release should contain at minimum:

```text
paper_b2_release/
├── CITATION.cff
├── environment.lock
├── manifest.json
├── claim_map.json
├── raw_source_manifest.json
├── processed/
│   ├── shot_level_traces.csv
│   ├── pressure_mean_traces.csv
│   ├── equilibrium_points.csv
│   └── observation_operator_metadata.json
├── predictions/
│   ├── same_trace_9bar.csv
│   ├── loso_shot_predictions.csv
│   ├── shared_pressure_predictions.csv
│   └── equilibrium_lopo_predictions.csv
├── diagnostics/
│   ├── residual_statistics.csv
│   ├── window_sensitivity.csv
│   ├── block_sensitivity.csv
│   └── parameter_provenance.csv
├── figures/
│   ├── figure_1.*
│   ├── figure_2.*
│   ├── figure_3.*
│   └── figure_4.*
└── scripts/
    ├── build_all.py
    └── verify_all.py
```

The release verifier should fail when:

- the tree is dirty;
- source and result-bundle commits differ;
- any manuscript claim lacks a path;
- any figure source table is missing;
- a data hash changes without an explicit migration;
- semantic labels contradict information provenance;
- the documented solids sigmoid sign differs from implementation;
- a held-out result uses the scored shot or pressure in any learned input.

---

## 10. Detailed submission checklist

### Scientific scope

- [ ] The principal claim is framed as evidence relative to tested model classes.
- [ ] Same-trace reconstruction is never called prediction.
- [ ] Same-campaign target-informed reconstruction is never called parameter-free.
- [ ] Equilibrium-calibration LOPO is never called a fully held-out temporal validation.
- [ ] Sign constraints are limited to stated isolated branches and boundary conditions.
- [ ] Machine-side capacity is not presented as a calibrated explanation of the Waszkiewicz trace.

### Experimental unit and uncertainty

- [ ] Complete per-shot 9-bar ladder is reported.
- [ ] Leave-one-shot-out \(\Phi(t)\) cross-fitting is complete.
- [ ] Flexible comparator is evaluated out of sample.
- [ ] Shot-level paired differences are shown.
- [ ] Refitting/preprocessing uncertainty is propagated where claimed.
- [ ] Fixed-loss block sensitivity is clearly secondary.

### Data and preprocessing

- [ ] Included and excluded shots are enumerated by pressure.
- [ ] Alignment rule is specified and frozen.
- [ ] Differentiation/filtering order is exact.
- [ ] Savitzky–Golay boundary treatment is specified.
- [ ] Interpolation grid and missing-data policy are specified.
- [ ] SEM versus SD labels are correct in data and text.
- [ ] Equilibrium statistic matches code and source description.

### Models

- [ ] Every equation and parameter value is reported.
- [ ] Parameter/information dependency graph is included.
- [ ] Model validity domains are declared.
- [ ] Pressure nodes and units are unambiguous.
- [ ] RC-3b is fully defined.
- [ ] Cubic is consistently described as same-trace or held-out according to analysis mode.

### Diagnostics

- [ ] Residual-vs-time plots are supplied for all branches.
- [ ] ACF and DW use a common declared time resolution.
- [ ] Fold-level cross-pressure plots are supplied.
- [ ] Window and smoothing sensitivity are supplied.
- [ ] Bias and MAE accompany RMSE.
- [ ] Residual magnitude is compared with shot variability without assuming pointwise independence.

### Reproducibility

- [ ] Clean immutable source commit.
- [ ] Clean result bundle from the same commit.
- [ ] Release archive/DOI.
- [ ] Complete claim map.
- [ ] Figure source data.
- [ ] Environment lock.
- [ ] Data/source rights and acquisition instructions.
- [ ] Correct `solids_calibration.csv` model string and refreshed hashes.
- [ ] CI checks evidence-tier semantics.

### Editorial production

- [ ] Abstract grammar corrected.
- [ ] Cubic LaTeX corrected.
- [ ] Internal cross-references corrected.
- [ ] “Floor/bound” removed.
- [ ] “Measured trace” replaced where the object is a processed mean.
- [ ] “Establish” replaced with “support” in intervention claims.
- [ ] Date and all author declarations completed.
- [ ] Figures embedded.
- [ ] References broadened and checked.

---

## 11. Final decision rationale

Paper B2 has a strong conceptual core and a useful, reproducible numerical observation. The second-round revision has addressed many of the first review’s most important wording and transparency problems. The paper now openly states that its principal object is a heavily processed mean trajectory, that \(\Phi(t)\) partly reuses flow information, that the cubic is in-sample, and that the block analysis is conditional. These are meaningful improvements rather than cosmetic edits.

The remaining barrier is that the paper’s strongest empirical language still rests on one pressure-level mean, while the independent shots and raw source structure needed for a more defensible analysis are available. The repository action plan correctly recognizes this and has not pretended that prose changes substitute for computation. Completing the per-shot, leave-one-shot-out, fully cross-fitted analysis would transform the paper: it would show whether the temporal advantage is reproducible across experimental units and whether it survives removal of target leakage. A held-out flexible comparator would then determine whether the mechanistically motivated trajectory provides genuine predictive structure beyond generic smoothness.

Until those analyses are complete, the paper should be viewed as a rigorous **mean-trajectory reconstruction and experiment-design study**, not as a predictive validation or mechanism-identification result. With the P0 revisions, a clean reproducibility release, and completed figures, it could become a valuable methodological paper for espresso and other coupled machine–porous-media inverse problems.

**Recommendation: major revision, with encouragement to resubmit after the shot-level and cross-fitted analyses are complete.**

---

## 12. Sources reviewed

### Puckworks, exact reviewed commit

- [Paper B2 manuscript](https://raw.githubusercontent.com/trbrewer/puckworks/d9ee264f85b15633f56d540b44066e681979a5fc/docs/PAPER_B2_TEMPORAL_DRAFT.md)
- [Paper B2 review action plan](https://raw.githubusercontent.com/trbrewer/puckworks/d9ee264f85b15633f56d540b44066e681979a5fc/docs/paper2_resource/PAPER_2_REVIEW_ACTION_PLAN.md)
- [Paper B manifest](https://raw.githubusercontent.com/trbrewer/puckworks/d9ee264f85b15633f56d540b44066e681979a5fc/docs/reproducibility/paper_b_manifest.json)
- [Latest Paper B2-specific commit](https://github.com/trbrewer/puckworks/commit/f7e2d4b33eff85b696c8ebe283129d17fab5ab86)
- [Accuracy/down-scoping commit](https://github.com/trbrewer/puckworks/commit/d0a5595)

### Upstream Waszkiewicz source provenance checked during audit

- [Source repository release/tag context](https://github.com/RadostW/espresso/tree/v1.0.1)
- [Zenodo software record](https://doi.org/10.5281/zenodo.18046315)
- [Upstream time-dependent formatter](https://raw.githubusercontent.com/RadostW/espresso/v1.0.1/format_measurements_time_dependent.py)
- [Upstream static-flow fit](https://raw.githubusercontent.com/RadostW/espresso/v1.0.1/fit_model_static_flow_rate.py)
- [Upstream dissolved-solids fit](https://raw.githubusercontent.com/RadostW/espresso/v1.0.1/fit_model_solids.py)

### Independent audit artifact

The supporting machine-readable audit produced for this review records the full-precision values quoted above, including headline RMSEs, window sensitivity, pressure substitution, residual diagnostics, block sensitivity, equilibrium folds, and cross-pressure results.

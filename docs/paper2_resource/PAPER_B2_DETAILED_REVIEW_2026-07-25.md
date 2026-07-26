# Detailed Review of PAPER 2
## `PAPER_B2_TEMPORAL_DRAFT.md`

**Repository:** `trbrewer/puckworks`  
**Manuscript reviewed:** `PAPER_B2_TEMPORAL_DRAFT.md`  
**Repository commit reviewed:** `93358f8e4d7d5c214470d82195d852f455651ff9`  
**Review date:** 25 July 2026  
**Recommended editorial decision:** **Major revision before journal submission**

---

## 1. Executive assessment

This is a promising and intellectually disciplined manuscript. Its central principle is important: an integrated espresso flow trace may reject specified static descriptions without identifying a unique physical mechanism. The draft is unusually careful about distinguishing measured data, published model outputs, and repository reconstructions; it also generally distinguishes reconstruction from prediction and explicitly acknowledges the soft circularity of the dissolution-linked temporal trajectory. Those are real strengths.

The manuscript's five headline 9-bar RMSE values are reproducible from the committed trace and model equations. I independently obtained:

- best constant: **0.5728555 g s⁻¹**;
- late-window constant: **0.6405890 g s⁻¹**;
- static poroelastic branch: **0.6476960 g s⁻¹**;
- empirical temporal `Φ(t)` branch: **0.1157694 g s⁻¹**; and
- in-sample cubic: **0.0963964 g s⁻¹**.

Thus, the numerical foundation of the headline model ordering is sound at the level of the committed, preprocessed mean trace. Substituting the recorded basket-pressure history for nominal 9 bar changes the static and temporal RMSEs by less than 0.001 g s⁻¹, so modest pressure variation at the recorded node does **not** explain the result.

However, the current draft is not yet publication-ready. The most important problem is that the apparent “one 9-bar trace” is not one raw shot. It is a differentiated, approximately three-second-smoothed, time-aligned, interpolated, across-shot mean. The source preprocessing also computes the columns named `*_std` with `pandas.DataFrame.sem()`, meaning that they are pointwise standard errors of the mean, not standard deviations. The manuscript currently neither describes this observation operator adequately nor treats the shots—not the hundreds of time points—as the principal experimental units.

The second central problem is information reuse. The `Φ(t)` trajectory is ultimately built from total dissolved solids multiplied by the same flow observable that it is later used to reconstruct. The draft calls this “soft-circular,” correctly, but the statistical comparison and parameter-provenance table still make the branch look more independent and lower-dimensional than it is. The present analysis demonstrates that a **same-campaign, target-informed temporal construction** follows the preprocessed mean curve much better than constant levels. It does not yet establish comparable performance on held-out shots or with an independently measured state trajectory.

A third problem is that the moving-block analysis resamples a fixed loss sequence from a single mean trajectory. It is useful as a dependence-sensitivity analysis, but it is not experimental uncertainty, does not refit the models, and cannot substitute for shot-level resampling or cross-fitting. The manuscript knows part of this limitation, yet the abstract and Results still give the intervals more inferential weight than their construction supports.

Finally, the recently added viscosity/Gagné material is not integrated to the standard of the rest of the paper. It introduces a second dataset, additional constitutive closures, numerical ratios, and mechanistic language without a corresponding Data section, Methods section, scored ladder branch, provenance chain, uncertainty analysis, figure, or bibliography entries. It also conflicts with the later statement that viscosity remains outside the quantitative ladder. That material should either be fully integrated as a separate exploratory analysis or removed from the present manuscript and reserved for a future paper or supplement.

### Bottom-line judgment

The core contribution is worth preserving, and the principal RMSE calculations appear correct. The paper should be revised around a more precise claim:

> **On the source campaign's preprocessed mean 9-bar trajectory over 15–95 s, the tested time-invariant level models reconstruct substantially worse than two smooth temporal descriptions. This ordering is robust to using the recorded basket-pressure history, but it is conditional on same-campaign preprocessing and on a dissolved-mass trajectory partly constructed from the target flow. The result therefore supports temporal flexibility relative to the tested nulls; it does not identify a unique poroelastic–dissolution mechanism.**

The strongest route to publication is to make the shot—not the time point—the unit of evidence, cross-fit the `Φ(t)` construction, treat the cubic as a same-trace descriptive comparator, rebuild the uncertainty analysis around shot-level variation, remove or fully integrate the viscosity addition, and create a clean release whose claim manifest covers every number in the manuscript.

---

## 2. What is already strong

### 2.1 The scientific question is important and appropriately skeptical

The paper addresses a genuine inverse problem rather than asking only which curve fits best. Its distinction between:

1. whether a machine subsystem can generate a qualitative shape;
2. whether tested static descriptions fail on a declared interval; and
3. whether a successful temporal reconstruction identifies a physical mechanism

is conceptually valuable. This hierarchy should remain the manuscript's organizing logic.

### 2.2 The evidence objects are separated carefully

The draft correctly prevents the Foster machine/infiltration reconstruction from being mistaken for a calibrated explanation of the Waszkiewicz experiment. That separation is one of the paper's best features. The language at lines 23, 41, 65, 187, 191, and 327 is generally responsible and should be retained.

### 2.3 Reconstruction, prediction, and held-out status are mostly used accurately

The draft explicitly calls the cubic in-sample and the `Φ(t)` branch a transferred within-campaign reconstruction rather than an independent prediction. The LOPO section also states that only the equilibrium calibration is held out while the temporal trajectory and donor assumptions remain fixed. This is materially better than presenting every non-fitted final-stage coefficient as out-of-sample prediction.

### 2.4 The headline 9-bar scores are reproducible

The independently recalculated values agree with the manuscript's rounded values. This provides confidence that Table 2 is not a transcription error and that the main ordering is genuine for the committed mean trace.

### 2.5 The measured-pressure robustness check is reassuring

Although the main ladder evaluates nominal pressure, the recorded basket pressure is sufficiently stable that using it point by point leaves the conclusion unchanged. This should be reported as a robustness result. It strengthens the narrower statement that the observed rise is not an artifact of the small measured pressure drift in this trace.

### 2.6 The manuscript is cautious about mechanism exclusion

The discussion of swelling and fines migration usually distinguishes an isolated, fixed-pressure sign result from absence in a coupled real bed. The sentence “sign does not imply absence” is especially useful. Preserve this caution when revising the stronger language elsewhere.

### 2.7 The experiment-design orientation is valuable

Pressure steps, matched-magnitude reversal, spent-puck replay, control-mode changes, and depth-resolved end states are more scientifically useful than adding another unconstrained forward fit. With clearer controls and formal decision rules, this could become one of the paper's most original contributions.

---

## 3. Decision-critical revision table

| Priority | Issue | Why it matters | Minimum acceptable revision |
|---|---|---|---|
| **P0** | Experimental unit and replicate structure are unclear | The analyzed curve is an across-shot, smoothed mean; time points are not independent experimental replicates | State shot counts and exclusions; analyze individual shots; report shot-level errors and uncertainty |
| **P0** | Observation/preprocessing operator is underreported | Differentiation, smoothing, alignment, interpolation, and averaging materially shape the response and autocorrelation | Add a complete preprocessing subsection and sensitivity analyses; correct `std`/SEM metadata |
| **P0** | `Φ(t)` is partly constructed from the target flow | This creates target information reuse and weakens causal or predictive interpretation | Add dependency diagram and cross-fitted/held-out-shot analysis, or substantially narrow the claim |
| **P0** | Current block intervals are not experimental uncertainty | Fixed-loss time-block resampling does not propagate between-shot or fitting uncertainty | Rebuild primary uncertainty around shot-level resampling and model refitting; retain current intervals only as sensitivity analysis |
| **P0** | Cubic is fitted and scored on the same trace | “Floor” or “bound” can be read as predictive evidence | Rename as a same-trace descriptive benchmark and add blocked/held-out temporal comparison if predictive contrast is desired |
| **P0** | Viscosity/Gagné addition is not integrated | It introduces unsupported methods, data, references, and claims and conflicts with the limitations section | Remove it from the main paper or add full data, methods, provenance, uncertainty, ladder score, figures, and references |
| **P0** | Reproducibility record is stale and incomplete | The committed manifest is dirty/stale relative to the manuscript commit and gates only a subset of claims | Generate a clean B2-specific release and machine-check every numerical manuscript claim |
| **P1** | Residual structure is severe | Low RMSE does not imply adequate dynamics; all branches retain coherent misspecification | Show residuals/ACFs/spectra and temper “nearly reaches” language |
| **P1** | LOPO holds out only an equilibrium point | It is not a held-out temporal trajectory or independent experiment | Rename precisely; show fold-level results and add shot-level or campaign-level validation |
| **P1** | Effective flexibility is understated | Table 1 counts only final sigmoid parameters and omits upstream fits and target-derived inputs | Replace with a full data/parameter provenance table or dependency graph |
| **P1** | Mechanism-by-perturbation predictions are too categorical | Several proposed signatures have plausible confounders | Add controls, thresholds, replication, and alternative explanations to each protocol |
| **P1** | Novelty and literature coverage are incomplete | The related-work scaffold does not establish the contribution against inverse-problem and model-discrimination literature | Conduct and document a systematic search and expand the references |
| **P2** | Figures are specified but not present | The most important diagnostic evidence cannot be assessed | Render final figures with source-data files and inspect readability |
| **P2** | Several wording, equation, metadata, and bibliography defects remain | These create avoidable ambiguity and provenance risk | Correct the line-specific issues listed below |

---

## 4. Major comments

## 4.1 Make the shot—not the time point—the experimental unit

### Finding

The manuscript repeatedly refers to “one 9-bar trace” or “a measured 9-bar trace.” The repository trace is instead an **average constructed from multiple raw shots**. In the upstream source workflow, each raw mass record is aligned, differentiated, smoothed, interpolated to a common time grid, and then averaged by pressure. At 9 bar, the published source tree contains five included shot files. Other pressure conditions have different numbers of included files.

There is also an unresolved source-accounting discrepancy:

- the Waszkiewicz article reports **60 coffees**;
- the Puckworks provenance text reports **58 raw per-brew traces**; and
- the visible upstream source tree contains **57 included files**, plus four files in an excluded directory and one alternate-named file among the included records.

This discrepancy may be a benign matter of exclusions, alternate records, or repository history, but the submitted paper must reconcile it explicitly.

### Why this matters

The present 800-point 15–95 s scoring vector is not 800 independent experimental observations. It is one preprocessed estimate of a mean trajectory. Treating contiguous time blocks from that mean as the principal uncertainty source risks pseudo-replication and says little about how stable the model ordering is across nominally repeated shots.

The scientific claim is much stronger if the `Φ(t)` branch outperforms static baselines on most or all individual 9-bar shots, and stronger still if the temporal input is constructed without using the held-out shot's flow. Conversely, a result driven by a subset of shots, alignment choices, or averaging should be reported as such.

### Required revision

1. State the exact number of included and excluded shots at each pressure.
2. Reconcile the 60/58/57 accounting in the manuscript and data manifest.
3. Describe the shot as the experimental unit and the time samples as repeated, serially dependent measurements within a shot.
4. Reproduce the primary ladder for each individual 9-bar shot using a common, predeclared observation pipeline.
5. Report, at minimum:
   - per-shot RMSE for every branch;
   - median and range or a suitable interval across shots;
   - the number of shots on which each branch wins;
   - sensitivity to excluding each shot;
   - whether the rise itself is consistent across shots rather than created by averaging misaligned transitions.
6. For the pressure-wide analysis, show the number of shots at every pressure and avoid giving each pressure equal inferential weight without explaining that choice.

### Preferred analysis

A strong design would use **leave-one-shot-out cross-fitting at 9 bar**:

1. hold out one raw 9-bar shot;
2. construct the pressure-level mean, TDS trajectory, dissolved-mass trajectory, and any fitted temporal parameters without that shot's flow;
3. predict the held-out shot on its observed time points;
4. repeat for all five shots; and
5. compare the temporal and static branches using shot-level paired losses.

If TDS was not measured for every shot, state the resulting dependency structure and use the most conservative feasible cross-fit. A cluster bootstrap over shots can supplement the leave-one-shot-out analysis, but with five shots the raw fold results are more informative than a highly processed p-value.

### Acceptance criterion

The paper should not use “the measured 9-bar trace” as though it were a raw experimental replicate. The revised manuscript should either demonstrate that its ordering persists at shot level or narrow the central result to the **preprocessed across-shot mean trajectory**.

---

## 4.2 Report and audit the complete observation operator

### Finding

The manuscript's Data section does not explain how the analyzed flow curve is produced. The upstream formatter performs a consequential sequence:

1. records mass and pressure at approximately 10 Hz;
2. locates a pressure-stabilization/start index and shifts time relative to that index;
3. computes flow by numerically differentiating mass with respect to time;
4. applies a Savitzky–Golay filter with a 31-sample window and first-order polynomial—approximately three seconds at 10 Hz;
5. interpolates each shot onto a common 0–100 s grid of 1,000 points;
6. groups records by pressure and time; and
7. averages across shots.

The fields named `pressure_std`, `basket_pressure_std`, `mass_std`, and `mass_flow_rate_std` are produced with `.sem()`. They are therefore standard errors of the mean, not standard deviations.

The manuscript also states that time is measured “from the source trace origin” (line 47), whereas the formatter aligns the traces to a detected pressure/start condition. In addition, the manuscript describes equilibrium flow as a 110–120 s summary, while the visible source fitting workflow uses the final value of a common trace ending around 100 s. The source article, source code, and repository implementation need to be reconciled.

### Why this matters

Differentiation amplifies measurement noise; smoothing suppresses high-frequency variation and creates serial dependence; alignment can sharpen or blur common features; interpolation induces additional covariance; and averaging can create a trajectory that no individual shot follows exactly. These choices directly affect:

- RMSE;
- residual autocorrelation;
- block-length interpretation;
- first-drop and early-rise timing;
- the apparent smoothness advantage of a cubic or sigmoid; and
- pointwise uncertainty.

Without this information, a reader cannot tell whether the paper compares physical models of raw observations or smooth curves after a strong observation filter.

### Required revision

Add a dedicated **Data acquisition and preprocessing** subsection that states:

- original sampling rate and sensors;
- pressure-node definitions;
- start/alignment rule;
- mass-to-flow differentiation method;
- Savitzky–Golay window and order;
- interpolation grid and endpoint handling;
- shot inclusion/exclusion rules;
- number of shots per pressure;
- averaging operation; and
- whether uncertainty fields are SD, SEM, or another quantity.

Correct the data dictionary so that fields computed by `.sem()` are not called `std`. If changing upstream column names would break compatibility, document a local alias and explicit semantic correction in Puckworks.

### Required sensitivity analyses

At least three should be reported:

1. **Smoothing sensitivity:** repeat key scores under several defensible smoothing windows, including a lighter filter.
2. **Alignment sensitivity:** perturb or alter the start-alignment rule and show whether model ordering changes.
3. **Mass-domain robustness:** compare predictions in cumulative-mass space, or use a state-space/measurement model that avoids treating a smoothed numerical derivative as the sole response.

A cumulative-mass analysis is particularly valuable: it uses the directly measured scale signal and reduces dependence on an arbitrary differentiation filter. It will not resolve mechanism identification, but it will show whether the central ordering is an artifact of the flow reconstruction.

### Acceptance criterion

A reader should be able to reproduce the exact 800-point primary response from raw shot files, understand why the sampled interval is actually 15.015015–94.994995 s, and know which operations contribute to the residual correlation.

---

## 4.3 Quantify the information reuse in the empirical `Φ(t)` branch

### Finding

The draft commendably calls the `Φ(t)` result “soft-circular,” but the full dependency is not made explicit. The source workflow constructs cumulative dissolved mass approximately as follows:

1. fit a temporal TDS curve;
2. multiply fitted TDS by the measured mean flow `Q(t)`;
3. integrate the resulting dissolved-solids flux;
4. fit a sigmoid to cumulative dissolved mass;
5. convert that sigmoid to `Φ(t)`; and
6. use `Φ(t)` in a model that is compared against the same mean `Q(t)`.

Thus, no coefficient may be optimized **directly at the final reconstruction step**, but the temporal input contains target-flow information. Table 1 lists only “3 dissolved-mass sigmoid parameters” and therefore understates both the upstream fitted quantities and the effective information use. The source workflow also contains a fitted TDS trajectory and preprocessing choices, in addition to the equilibrium parameters and dissolved-mass sigmoid.

There is a related metadata defect: the stored `solids_calibration.csv` model string describes a `1 - tanh(...)` form even though the implemented cumulative dissolved-mass function is increasing and uses the opposite sign. This appears to be a metadata transcription error rather than a numerical error, but it should be corrected or explicitly annotated.

### Why this matters

The most interesting claim in the paper is not simply that a temporal function beats a constant. It is that a physically motivated, transferred trajectory nearly matches a flexible descriptive curve without final-stage fitting to flow. That claim depends critically on what information entered the transferred trajectory.

“Zero coefficients fitted directly to the scored trace” is not equivalent to “independent of the scored trace.” Without cross-fitting, a reader cannot tell how much of the good reconstruction comes from the proposed poroelastic–dissolution mapping and how much comes from feeding a smoothed transformation of `Q(t)` back into the model.

### Required revision

1. Add a **data-dependency diagram** showing every measured signal, preprocessing step, fitted parameter, and model output.
2. Replace the simple parameter-count table with a provenance table containing at least:
   - final-stage parameters fitted to the target;
   - upstream parameters fitted using the same target;
   - parameters fitted using other observables from the same shots;
   - quantities estimated from other shots/pressures;
   - externally fixed constitutive forms; and
   - data-dependent preprocessing choices.
3. Replace “externally parameterized temporal trajectory” at line 209 with wording such as “same-campaign, target-informed temporal trajectory.”
4. Put the soft-circularity disclosure immediately beside every “no coefficients fitted” statement, including Table 2 and the Abstract.
5. Correct or annotate the sign error in the stored dissolved-mass calibration metadata.

### Preferred discriminating analyses

At least one analysis should break the direct target reuse:

- **Leave-one-shot-out `Φ(t)`:** construct `Φ(t)` from the other 9-bar shots and score the held-out shot.
- **Cross-observable construction:** use independently measured mass loss or concentration together with a flow estimate from different shots.
- **Ablation:** replace measured `Q(t)` inside the dissolved-mass construction with a constant, static model, or flow from another shot and quantify the loss of performance.
- **State-measurement validation:** compare inferred `Φ(t)` with a directly measured bed thickness, strain, porosity, or soluble-mass trajectory.

### Acceptance criterion

The manuscript should no longer imply that the `Φ(t)` branch is independent simply because its final-stage coefficients were not fitted to the plotted curve. Either demonstrate held-out-shot performance or explicitly limit the claim to a target-informed reconstruction.

---

## 4.4 Replace the primary uncertainty analysis with shot-level uncertainty and refitting

### Finding

The moving-block procedure samples contiguous blocks of an already-computed squared-error-difference sequence from a single mean trajectory. It does not:

- resample shots;
- recreate the mean trace;
- refit the constant or cubic;
- refit equilibrium parameters;
- refit the TDS or dissolved-mass trajectory;
- propagate uncertainty in source parameters;
- propagate alignment or smoothing choices; or
- represent uncertainty in the raw mass and pressure measurements.

The manuscript acknowledges most of this in lines 155–157 and 333, which is good. Nevertheless, the Abstract calls the outputs “moving-block intervals” in a way that many readers will interpret as inferential confidence intervals for the model comparison.

### Why this matters

Resampling time blocks from one smoothed mean trace quantifies sensitivity to where coherent residuals occur along that particular curve. It does not quantify repeatability across espresso shots. The latter is the relevant experimental uncertainty for a claim about the physical system.

The procedure is also conditional on a single chosen block algorithm and only 1,000 resamples. The number of resamples is not the primary defect, but 1,000 gives limited resolution in the tails and should not create a false impression of precision.

### Required revision

1. Rename the current result **conditional fixed-loss block-resampling sensitivity** or equivalent.
2. Do not call it a confidence interval for the whole model-comparison process.
3. Build the main uncertainty analysis from experimental units:
   - resample shots within pressure;
   - rebuild preprocessed pressure-level traces;
   - refit all estimable components inside each resample;
   - reconstruct each branch; and
   - compare shot-level or pressure-level losses.
4. Where feasible, cross-fit the temporal input so that held-out outcomes do not enter their own predictors.
5. Report the complete algorithm, random seed, treatment of endpoints, block construction, block rounding, and number of resamples.
6. Include circular, stationary, or other block schemes as sensitivity analyses if time-block resampling remains in the paper.

### A practical hierarchy

Given the small number of 9-bar shots, the following order is preferable:

1. show every per-shot result;
2. report leave-one-shot-out results;
3. use a shot-level paired summary or exact sign/rank analysis;
4. add a cluster bootstrap with transparent limitations; and
5. retain time-block resampling as a secondary diagnostic of within-trajectory dependence.

### Acceptance criterion

The primary inferential language must be based on between-shot evidence or clearly state that no between-shot inference is attempted. The fixed-loss block result should remain a diagnostic, not carry the principal evidential burden.

---

## 4.5 Reframe the cubic and add a genuinely held-out flexible temporal comparator

### Finding

The cubic is fitted and scored on the same 15–95 s trace. Calling it an “in-sample flexibility floor” or “bound” is understandable, but potentially misleading. It is not a lower bound on achievable error, not a predictive benchmark, and not complexity-matched to the complete information used by the `Φ(t)` workflow.

### Why this matters

The comparison currently supports a valid descriptive statement: a four-coefficient smooth function can follow the mean trace at least as closely as the mechanistically labeled trajectory. It does not show that an arbitrary temporal model predicts new shots or conditions as well as the mechanistic candidate.

The paper's identification argument becomes stronger, not weaker, if it is explicit that this is a **same-trace non-uniqueness demonstration** rather than model selection.

### Required revision

1. Rename the cubic throughout as a **same-trace flexible descriptive benchmark**.
2. Remove “floor” and “bound” unless carefully qualified as an observed in-sample score for one chosen function class.
3. State that its role is to show non-uniqueness of smooth reconstruction, not prediction.
4. Report coefficient uncertainty only if meaningful under the correlated observation process; otherwise give coefficients for reproducibility without inferential interpretation.

### Preferred addition

Add a held-out flexible comparator using one of these approaches:

- fit a penalized spline or Gaussian-process mean to training shots and score held-out shots;
- fit a monotone empirical rise model to a subset of shots and score the remainder;
- use leave-contiguous-segment-out cross-validation with a gap, while acknowledging interpolation rather than extrapolation; or
- fit on one pressure/shot group and score another after a predefined normalization.

The comparator should use the same training information and validation unit as the mechanistic branch. A monotone smooth model may be more interpretable than a global cubic because the primary trace is a smooth rise and polynomial behavior outside the fitting interval is irrelevant.

### Acceptance criterion

The manuscript should not suggest that a lower in-sample cubic RMSE is a predictive victory. It should use the cubic only to demonstrate that fit quality does not identify the mechanism, unless a proper held-out comparison is added.

---

## 4.6 Integrate the viscosity/Gagné material fully or remove it

### Finding

The new paragraph at line 245 and related material in Table 4, §6.5, and Limitation 2 introduce:

- Telis-Romero and Sobolík viscosity–concentration closures;
- an early concentration near 15% solids;
- an apparent-resistance decline by a median factor near 2.7;
- eleven flow-controlled blooming shots on another machine;
- a bulk viscosity ratio near 1.6;
- a shot-integrated Darcy effect of order 1%; and
- a claim that viscosity decline and dissolution opening are degenerate.

None of the new sources appears in the References. The data source, licensing/access status, shot selection, pressure node, sensor calibration, algorithm, thresholds, uncertainty, and exact code path are not described in Data or Methods. The viscosity effect is not a branch in Table 2 or Table 3, yet line 245 calls it an “implemented branch.” Line 337 then says viscosity remains outside the quantitative ladder.

The apparent resistance `P/Q` in a real machine is also a system-level quantity. A decline can reflect bed structure, liquid viscosity, pressure control, sensor behavior, plumbing, or combinations of them. A broad numerical compatibility between an early viscosity ratio and an apparent-resistance ratio is not a reconstruction of the time series and is not independent corroboration of viscosity as the cause.

### Why this matters

This addition currently weakens an otherwise disciplined paper. It blurs three distinct objects:

1. a Gagné flow-controlled trace and apparent-resistance calculation;
2. a coffee-liquor viscosity closure from separate literature; and
3. a concentration-history sensitivity calculation apparently based on another modeling context.

The text then compresses them into “a magnitude reproduced by a viscosity decline,” which is stronger than the evidence supports. It also introduces a second experimental campaign without the source-object discipline applied to Foster and Waszkiewicz.

### Recommended option A: remove from the present paper

This is the cleaner option. Retain one sentence in Discussion or Limitations:

> “Concentration-dependent liquid viscosity is another temporally varying contribution with the correct sign and should be evaluated in a future, separately documented branch.”

Remove the detailed ratios, Gagné claims, Table 4 row, and §6.5 paragraph until the branch is fully registered and scored.

### Option B: integrate as a separate exploratory analysis

If retained, add:

1. a source-object subsection describing the Gagné records and their evidentiary status;
2. full citations for Gagné, Telis-Romero, and Sobolík;
3. data access and redistribution terms;
4. sensor types, calibration limitations, pressure nodes, units, shot selection, and exclusions;
5. the exact apparent-resistance algorithm, bloom-end rule, smoothing, and flow/pressure thresholds;
6. a clear separation between observed `P/Q` and inferred hydraulic/bed resistance;
7. the concentration and viscosity equations, their validated ranges, temperature assumptions, and extrapolations;
8. a scored viscosity-only prediction on the Waszkiewicz ladder, or an explicit statement that it is only a scalar admissibility calculation;
9. uncertainty and sensitivity to concentration, temperature, sensor drift, and endpoint assumptions;
10. a dedicated figure and source-data file; and
11. inclusion of every numerical claim in the release manifest.

The wording should be narrowed to something like:

> “A separate exploratory calculation shows that concentration-dependent viscosity has the correct rising-flow sign and can produce an early viscosity ratio of similar order to the observed system-level apparent-resistance decline under broad assumptions. This is a compatibility result, not a mechanistic attribution or a scored reconstruction of the Waszkiewicz trace.”

### Acceptance criterion

No uncited quantitative branch should appear in Results. The manuscript must either present viscosity as a complete, reproducible analysis or clearly classify it as future work.

---

## 4.7 Treat the strong residual structure as a substantive result

### Finding

The manuscript reports lag-1 residual autocorrelation near 0.99 and mean decimated Durbin–Watson near 0.01. Those values indicate that the residuals are overwhelmingly structured. The temporal RMSEs are much lower than static RMSEs, but neither temporal branch is close to an adequate stochastic model of the response.

My exploratory inverse-SEM-weighted calculations preserve the ordering but show that residual magnitudes remain substantial relative to the pointwise SEM fields:

- `Φ(t)`: RMS residual approximately **1.81 SEM units**;
- cubic: approximately **1.43 SEM units**.

These values are descriptive only—smoothing, interpolation, varying shot count, and residual covariance invalidate a naïve independent-normal interpretation—but they reinforce the manuscript's own conclusion that systematic lack of fit remains.

### Why this matters

The phrase “nearly reaches an in-sample flexible floor” foregrounds the small difference between 0.116 and 0.096 while underplaying the coherent structure both models miss. The residual shape may contain more scientific information than the aggregate RMSE gap.

### Required revision

1. Make residual plots central, not supplementary decoration.
2. Show residual-versus-time curves for all branches on the same scale.
3. Show ACFs and, where useful, low-frequency spectra or smooth residual decompositions.
4. Overlay pointwise SEM or, preferably, shot-level variability without treating it as independent noise.
5. Report whether residual features repeat across individual shots and pressures.
6. Identify reproducible residual landmarks and ask which omitted state or boundary variable could produce them.
7. Temper “nearly reaches” language. A better statement is:

> “The temporal branch approaches the selected cubic's same-trace RMSE, but both retain large coherent residual structure and are incomplete dynamic descriptions.”

### Acceptance criterion

A reader should leave the Results understanding both facts: temporal descriptions greatly reduce error relative to static levels, and the remaining dynamics are not minor noise.

---

## 4.8 Narrow and rename the LOPO claim

### Finding

The leave-one-pressure-out procedure excludes one long-run equilibrium pressure–flow point while refitting only `P_c` and `Q_c`. It retains:

- the same apparatus and coffee campaign;
- the same preprocessing;
- the same 9-bar dissolved-mass trajectory;
- the same donor assumptions; and
- pressure-level mean traces.

The draft describes these limitations reasonably well, but terms such as “held-out pressure” and “cross-pressure transfer” can still be read as broader temporal validation.

### Why this matters

The calculation establishes stability of the **equilibrium calibration** and conditional trace reconstruction. It does not show that the temporal trajectory generalizes from training pressures to a truly unseen temporal response, because the temporal shape remains fixed and comes from the same campaign.

The equilibrium `Q² ≈ 0.81` is also based on only eleven pressure points and a two-parameter curve. It should be presented with fold-level predictions and uncertainty, not as a standalone validation statistic.

### Required revision

1. Rename the analysis **leave-one-pressure-out equilibrium-calibration reconstruction**.
2. Put “only `P_c` and `Q_c` are held out/refitted” in the table caption and Abstract if LOPO remains there.
3. Show all eleven fold predictions, residuals, parameter estimates, and leverage.
4. State the exact `Q²` definition and reference baseline.
5. Report median, range, and normalized errors in addition to unweighted mean RMSE; absolute RMSE can favor or penalize pressures with different flow scales.
6. Show how conclusions change when weighting pressures by shot count versus treating each pressure equally.
7. Avoid “transfer” without the qualifier “within-campaign, conditional.”

### Preferred extension

A stronger validation would hold out all shots at a pressure **and** derive the temporal state from other pressure conditions or an independent state measurement. Better still, repeat the protocol on a second coffee, grinder setting, and apparatus.

### Acceptance criterion

The reader should not mistake LOPO of two equilibrium coefficients for validation of the complete temporal mechanism.

---

## 4.9 Strengthen the null hierarchy and causal wording

### Finding

At fixed nominal pressure, each static branch predicts a single level, while the observed mean flow rises strongly over time. The static-versus-temporal ordering is therefore expected once the rise is accepted as physical. The real scientific value lies in:

- showing that the rise is not due to the small recorded pressure drift;
- quantifying how much static models miss;
- demonstrating that multiple temporal descriptions fit similarly;
- tracing their information provenance; and
- designing interventions that distinguish them.

The abstract's statement that the trace “establishes a need for temporal dynamics” and Results language such as “strong evidence” should be conditional on the preprocessed mean and tested nulls.

### Why this matters

The current wording could be read as excluding all static explanations or identifying an evolving internal state. The paper itself correctly says that it does neither. The central language should consistently match that restraint.

### Required revision

Use formulations such as:

- “rejects the tested time-invariant level descriptions on the declared preprocessed mean trajectory”;
- “supports temporal flexibility relative to the tested nulls”;
- “does not exclude static spatial heterogeneity or unmeasured boundary variation”; and
- “does not observe a bed state directly.”

Add the recorded-pressure robustness calculation to the main or supplementary Results:

| Branch | Nominal 9 bar RMSE | Recorded basket-pressure RMSE | Change |
|---|---:|---:|---:|
| Static poroelastic | 0.647696 | 0.646846 | −0.000850 |
| Empirical `Φ(t)` | 0.115769 | 0.116443 | +0.000673 |

This check materially improves the argument because it directly tests one plausible boundary-condition confound.

### Acceptance criterion

Every global claim should preserve the qualifiers “tested,” “time-invariant,” “preprocessed mean,” and “within campaign” where relevant.

---

## 4.10 Revise the parameter-provenance table to reflect effective flexibility

### Finding

Table 1 is a useful idea but too compressed. For the empirical `Φ(t)` branch, it lists two equilibrium parameters and three dissolved-mass sigmoid parameters. This omits:

- parameters used to fit the TDS trajectory;
- the target flow entering the dissolved-solids flux;
- smoothing and alignment choices;
- first-drop/time-offset choices;
- integration and interpolation choices; and
- any source constraints or bounds.

For RC-3b, “donor extraction calibration” also obscures how many fitted quantities and which datasets are imported.

### Required revision

Replace Table 1 with a richer table such as:

| Branch | Final target-fitted coefficients | Same-target-derived inputs | Same-campaign other-observable fits | Other-pressure fits | External/donor content | Scored out of sample? |
|---|---:|---|---|---|---|---|

Add a second table or graph that identifies the effective transformations from raw data to prediction. The purpose is not to invent a single “effective parameter count,” which may be ill-defined, but to make the information path auditable.

Also describe `Φ(t)` more carefully. It is a model's stress-free-porosity scale or proxy derived from dissolved mass; it is not a directly measured physical porosity trajectory. Use “porosity-scale trajectory” or the source model's exact terminology where possible.

### Acceptance criterion

A reader should be able to identify every place where the scored flow or a same-shot observable enters each candidate.

---

## 4.11 Make the mechanism-by-perturbation program experimentally testable

### Finding

Table 4 is conceptually useful but several cells are too categorical. Examples include:

- “mass loss is direction-independent” despite spatial concentration and saturation gradients;
- “near-flat” spent-puck rebrew, which may be confounded by retained solubles, resaturation, temperature, degassing, unloading, swelling relaxation, and structural damage;
- flow reversal as a fines-specific signature even though reversal also changes stress, contact geometry, screen interaction, and machine plumbing;
- “no bed-state signature” for machine/headspace response, which may coexist with a bed signature; and
- “reversal asymmetry or an outlet deposit would establish a fines-migration contribution” (line 286), which is too strong without controls.

### Why this matters

The proposed experiments are a major potential contribution, but only if the predictions are operationalized. A qualitative matrix that every mechanism can explain after the fact will not solve the inverse problem the paper diagnoses.

### Required revision

For each intervention, specify:

1. **primary observable**;
2. **pressure and flow nodes**;
3. **predeclared sign or time-scale prediction**;
4. **effect threshold** that counts as support;
5. **null/inert-load control**;
6. **apparatus asymmetry control**;
7. **replication plan**;
8. **randomization/order control**;
9. **temperature and concentration measurement**;
10. **alternative explanations**; and
11. **result that would falsify or materially weaken each branch**.

Specific recommendations:

- **Pressure step:** run the same command through an inert porous load and/or hydraulic resistor to quantify machine-only transients; record pump outlet, group/headspace, basket inlet, and downstream pressure.
- **Flow reversal:** reverse an inert symmetric bed and the empty plumbing first; image or collect fines on both screens; match pressure-drop magnitude and control for bed unloading.
- **Spent-puck rebrew:** control rest time, temperature, water content, resaturation, and residual solubles; compare no-rest and controlled-rest conditions as proposed.
- **Depth-resolved state:** predeclare a quantitative gradient metric and include multiple sacrificial replicates because destructive sectioning cannot provide a within-puck before/after comparison.
- **Control mode:** match the physical trajectory as closely as possible rather than comparing nominal labels such as “flow control” and “pressure control.”

Replace “establish” with “support,” “provide evidence for,” or “be consistent with,” unless a signature is demonstrably unique under the controlled design.

### Acceptance criterion

Table 4 should function as a preregistration-ready discrimination plan, not only a narrative list of plausible outcomes.

---

## 4.12 Complete the literature and novelty assessment

### Finding

The manuscript cites the core espresso model lineages, but the broader related-work record remains a scaffold and does not establish novelty. The paper uses terms such as “inverse problem,” “systems identification,” “model comparison,” “observability,” “block resampling,” and “mechanism discrimination” without engaging the corresponding methodological literature in depth.

The current References also omit the new Gagné, Telis-Romero, and Sobolík sources invoked in Results.

### Required revision

Conduct and document a systematic literature search covering at least:

- espresso and coffee-bed hydraulic dynamics;
- machine hydraulic and control-system response;
- porous-media inverse problems and equifinality;
- structural and practical identifiability;
- system identification with correlated observations;
- model comparison under temporal dependence;
- blocked and cluster resampling;
- cross-validation for dependent data;
- optimal experimental design for model discrimination;
- coffee-liquor viscosity versus concentration and temperature;
- fines transport, filtration, clogging, and reversal hysteresis; and
- direct or spatial measurements of coffee-bed deformation and extraction.

Then state the novelty precisely. A plausible novelty claim is not “the first temporal espresso model comparison” unless proven. It may instead be:

> “a provenance-aware, null-first synthesis that compares machine capacity, static and temporal reconstruction, same-trace flexibility, conditional sign constraints, and intervention design across otherwise incompatible espresso model lineages.”

If the paper retains “systems identification” as a keyword, add a more formal observability/identifiability section. Otherwise, “inverse problems” and “model discrimination” may describe the work more accurately.

### Acceptance criterion

The novelty statement should be supported by a reproducible search record and should distinguish the conceptual framework from the underlying published models.

---

## 4.13 Produce a clean, manuscript-specific reproducibility release

### Finding

The draft correctly says its numerical values should be regenerated from a clean release. That condition is not currently met. The committed Paper B manifest/bundle records a source commit beginning `ed504769...`, reports `git_dirty: true`, and is marked `release_fresh: false`, whereas the manuscript reviewed here is at commit `93358f8e...`.

The existing claim map also checks only a subset of the manuscript's numerical statements. It does not appear to gate every value in:

- Table 2;
- both block-interval endpoints;
- block-duration sensitivity;
- residual diagnostics;
- Table 3;
- calibration drift and `Q²`;
- swelling error/correlation/magnitude;
- viscosity/Gagné ratios;
- pressure robustness; or
- figure annotations.

### Why this matters

The paper's central theme is disciplined evidence provenance. A stale or dirty manuscript bundle would undercut that contribution more seriously than it would in an ordinary modeling paper.

### Required revision

Create a **Paper B2-specific, one-command release workflow** that:

1. refuses a dirty tree in strict mode;
2. records the exact manuscript and source commit;
3. locks Python and dependency versions;
4. records operating-system/platform details;
5. hashes every input file and generated artifact;
6. records all random seeds and resampling settings;
7. regenerates every table, figure, and numeric sentence;
8. machine-checks every manuscript number against a claim registry;
9. exports figure source data in open formats;
10. records shot counts, exclusions, and pressure-node definitions;
11. includes the corrected SEM metadata and dissolved-mass formula annotation;
12. records whether source data can be redistributed;
13. creates a clean manifest with `git_dirty: false` and release freshness true; and
14. archives the release with an immutable DOI.

Add a manuscript-to-artifact map: each table cell and reported interval should point to a generated result key. Avoid manually copying rounded values into prose without a test.

### Acceptance criterion

A clean checkout of the frozen release should regenerate the submitted manuscript's figures and numeric tables and pass strict verification without network-dependent mutable inputs.

---

## 5. Independent numerical audit

### 5.1 Scope

I independently recalculated the main 9-bar ladder from the committed averaged trace and the repository equations at commit `93358f8e4d7d5c214470d82195d852f455651ff9`. This was a targeted numerical audit, not a substitute for a clean end-to-end release build or raw-shot reanalysis.

The primary mask contains **800 points** on a grid from **15.015015 to 94.994995 s**, with spacing approximately **0.1001 s**.

### 5.2 Headline scores

| Branch | Manuscript value | Independent value | Assessment |
|---|---:|---:|---|
| Best constant | 0.573 | 0.572855540 | Reproduced |
| Late-window constant | 0.641 | 0.640589012 | Reproduced |
| Static poroelastic, nominal 9 bar | 0.648 | 0.647696048 | Reproduced |
| Empirical `Φ(t)`, nominal 9 bar | 0.116 | 0.115769387 | Reproduced |
| Cubic fitted/scored on same trace | 0.096 | 0.096396396 | Reproduced |

### 5.3 Trace statistics relevant to interpretation

| Quantity | Value |
|---|---:|
| Mean flow over primary window | 1.584111 g s⁻¹ |
| SD of flow over time | 0.573214 g s⁻¹ |
| Flow range | 0.138499–2.019789 g s⁻¹ |
| Mean recorded machine pressure | 9.127484 bar |
| Machine-pressure range | 9.080708–9.219336 bar |
| Mean recorded basket pressure | 8.736974 bar |
| Basket-pressure range | 8.659480–8.906557 bar |
| Mean field labeled flow `std` | 0.068849 g s⁻¹ |

The last field is generated as a pointwise SEM in the upstream formatter and should be relabeled or documented accordingly.

### 5.4 Recorded-pressure robustness

| Branch | Nominal pressure RMSE | Recorded basket-pressure RMSE | Recorded machine-pressure RMSE |
|---|---:|---:|---:|
| Static poroelastic | 0.647696 | 0.646846 | 0.648611 |
| Empirical `Φ(t)` | 0.115769 | 0.116443 | 0.115798 |

The ordering and effect size are essentially unchanged. This is useful evidence that the modest recorded pressure variation is not the source of the temporal branch's advantage.

### 5.5 Exploratory SEM-weighted calculation

For descriptive sensitivity only, weighting residuals by the inverse pointwise SEM preserved the ordering:

| Branch | Inverse-SEM-weighted RMSE (g s⁻¹) |
|---|---:|
| Best constant | 0.500712 |
| Late constant | 0.472015 |
| Static poroelastic | 0.475377 |
| Empirical `Φ(t)` | 0.088263 |
| Cubic | 0.069933 |

This is **not** a valid generalized least-squares analysis because the mean trace has been smoothed and interpolated, the errors are serially correlated, and the covariance matrix is unknown. It merely shows that the headline ordering is not created by equal weighting of obvious high-SEM regions.

### 5.6 What this audit does not establish

It does not establish:

- raw-shot reproducibility;
- correctness of the source run-count accounting;
- validity of the block intervals as experimental confidence intervals;
- independence of `Φ(t)` from the scored flow;
- cross-machine or cross-coffee validity;
- mechanism identification; or
- completeness of the current release bundle.

The machine-readable values used for this audit are retained in the accompanying file `PAPER_B2_independent_audit_2026-07-25.json`.

---

## 6. Section-by-section review

## 6.1 Title

### Current title

> *One flow curve, many causes: null-first inference for machine and porous-bed dynamics in espresso*

The title is engaging and accurately signals non-uniqueness, but “many causes” may imply that the paper has established multiple actual causes rather than multiple admissible explanations. “Null-first inference” is also methodologically dense for a general coffee-science audience.

### Suggested alternatives

1. **What an Espresso Flow Curve Can—and Cannot—Reveal: Null-First Tests of Machine and Porous-Bed Dynamics**
2. **Interpreting Espresso Flow Curves: Static Nulls, Temporal Reconstructions, and Mechanism Non-Uniqueness**
3. **Temporal Dynamics Without Mechanism Identification in Espresso Flow**
4. **Why an Espresso Flow Curve Does Not Identify a Unique Bed Mechanism**

Option 1 best preserves the present tone while making “espresso” prominent and clarifying the scientific purpose.

## 6.2 Draft metadata

- Line 3 still says **15 July 2026**, although substantive viscosity/Gagné material was added later. Update the manuscript date and version.
- Insert authors, affiliations, corresponding author, contribution statement, funding, conflicts, and acknowledgments before external circulation.
- Add a manuscript version identifier linked to the release manifest.

## 6.3 Abstract

The Abstract contains the right logical sequence but needs four changes:

1. call the response a **preprocessed across-shot mean trajectory**, not simply a measured trace;
2. disclose immediately that `Φ(t)` is partly constructed from same-campaign flow;
3. avoid presenting fixed-loss block intervals as the main experimental uncertainty; and
4. replace “establishes a need” with “supports temporal flexibility relative to the tested time-invariant nulls.”

The Abstract is numerically dense. Consider removing one set of interval endpoints and using that space to describe the experimental unit and key limitation.

Suggested replacement for the core result sentence:

> “On the preprocessed mean 9-bar trajectory over 15–95 s, time-invariant level models had RMSEs of 0.57–0.65 g s⁻¹, whereas a same-campaign temporal trajectory partly constructed from flow and TDS reached 0.116 g s⁻¹ and a cubic fitted and scored on the same trajectory reached 0.096 g s⁻¹.”

## 6.4 Introduction

The Introduction is well structured. Improve it by:

- adding literature on inverse problems, equifinality, identifiability, and model-discriminating experiments;
- explaining earlier that this is a comparison of non-equivalent model lineages and evidence roles rather than a tournament of complete espresso models;
- stating the exact novelty after the literature search; and
- avoiding “systems identification” unless formal identifiability or observability analysis is added.

Line 25's “four scoped contributions” should be revised after the shot-level analysis. At present, the second and third contributions are analyses of pressure-level mean traces, not replicated validation.

## 6.5 Data and observable definitions

This section requires the most substantial expansion.

- Line 33 should say “preprocessed mean 9-bar flow trajectory.”
- Line 45 must state the number of raw shots per pressure and reconcile the total count.
- Line 45's 110–120 s equilibrium summary must be reconciled with the implemented final-point/approximately 100 s workflow.
- Line 47's “source trace origin” appears inaccurate because the source formatter aligns to a detected start/pressure condition.
- State whether “9 bar” means nominal machine setting, measured machine pressure, or measured basket pressure. The actual mean basket pressure in the primary window is approximately 8.737 bar.
- Define every uncertainty column correctly as SEM or SD.
- State whether any runs were excluded before or after observing outcomes and provide reasons.
- Add a source-object table with DOI, repository tag/commit, file hash, license, and redistribution status.

## 6.6 Primary estimand

Line 59 is one of the manuscript's best disclosures. Retain it, but refine the estimand:

> “The primary estimand is branch-specific reconstruction error for a preprocessed pressure-level mean trajectory, conditional on the source alignment, smoothing, interpolation, averaging, calibration, and temporal-input construction.”

After shot-level analysis, add a second estimand for held-out-shot prediction or reconstruction.

## 6.7 Model-comparison ladder

### Static baselines

The best constant is a legitimate strongest one-level null. The late-window constant is interpretable but its exact estimation interval should be given. Clarify whether it overlaps the 15–95 s scoring interval; if so, it is not independent of the scored data.

The static poroelastic branch should be evaluated using the exact implemented equilibrium calibration and its source. Add the measured-pressure robustness calculation.

### Empirical `Φ(t)`

The paper's current caveat is directionally correct but insufficient. Add the full dependency graph and change every label that might imply external independence.

### Cubic

Correct the malformed LaTeX at line 109:

```tex
Q_{\text{cub}}(t)=a_0+a_1t+a_2t^2+a_3t^3.
```

Rename it as a same-trace descriptive benchmark.

### RC-3b

The current description is too abstract for a reader to reproduce. Define the donor trajectory, its source, parameters, normalization, and why it is scientifically relevant. State explicitly that it is a Puckworks synthesis rather than a source-paper model.

## 6.8 Statistical and diagnostic analysis

### Residual diagnostics

Decimating to 1 s prevents the original 10 Hz sampling from numerically dominating a statistic, but it does not make residuals independent or make Durbin–Watson a complete adequacy test. Show the full residual structure and consider model-based covariance or functional-data summaries.

### Moving-block sensitivity

Specify:

- whether blocks are circular or non-circular;
- how partial final blocks are handled;
- how start positions are sampled;
- whether loss differences or paired residual vectors are sampled;
- exact random seed;
- the number of possible blocks;
- the transformation from resampled mean squared losses to ΔRMSE; and
- why 8 s is primary.

Use at least 10,000 resamples if reporting percentile endpoints to two decimals, but emphasize that refitting and experimental-unit resampling matter much more than the Monte Carlo count.

### Window sensitivity

The three windows are useful but appear selected after inspecting the source process. State whether they were prespecified. Add a continuous start/end sensitivity map or a modest grid so the conclusion is not dependent on three hand-picked windows.

### LOPO

Rename as discussed above and report all folds.

## 6.9 Results

### Foster result

This section is logically sound. Ensure Figure 1 makes the separation of evidence objects unmistakable. Do not visually overlay the Foster curve with Waszkiewicz data in a way that suggests a fit.

### Table 2

The values reproduce. Revise the interpretation column for `Φ(t)` to:

> “same-campaign temporal reconstruction; no final-stage coefficient fitted to this curve, but temporal input partly derived from same flow.”

Revise the cubic label to “same-trace four-parameter descriptive benchmark.”

Replace “4.9 times lower” with either:

- “a factor of 4.9 smaller,” or
- “approximately 80% lower.”

The latter is often easier to read.

Line 209's “externally parameterized” conflicts with the acknowledged same-campaign target reuse. Replace it.

### Residual results

Do not compress the residual finding into two scalar statistics. Show the actual patterns and whether they repeat by shot.

### Block results

Use “conditional resampling interval” consistently. Do not imply equivalence when zero is included. The current text appropriately avoids that wording; preserve it.

### Cross-pressure result

Table 3 should include:

- pressure-level sample count;
- normalized RMSE or NRMSE;
- median and range;
- fold-level values; and
- uncertainty from shots.

The statement that `Φ(t)` has the lowest mean error is accurate for the reported summary but should not imply universal superiority, especially because no branch wins every pressure.

### Sign tests

Keep the isolated-branch caveat. Separate structural sign conclusions from numerical transfer magnitudes. A transferred swelling result reaching 4% of initial flow is highly parameter-specific and should not dominate the text.

### Viscosity paragraph

Remove or fully integrate, as detailed in Major Comment 4.6.

## 6.10 Experiment design

The section is promising but currently reads as a conceptual research agenda. To qualify as a scientific contribution, add a protocol table with quantitative outcomes, controls, and decision thresholds.

Line 249 says that the repository contains no data from the proposed protocols, while line 282 then presents a logged flow-control example. Clarify that Gagné is an **external analogous intervention**, not data from the proposed matched protocol.

Line 286 should not say that reversal asymmetry or an outlet deposit would “establish” a fines contribution without ruling out apparatus and structural confounders.

## 6.11 Discussion

The Discussion is generally appropriately cautious. The main revision is to anchor every conclusion to:

- a preprocessed mean trajectory;
- a small number of repeated shots;
- same-campaign input reuse; and
- specified model classes.

Line 292's “strong evidence” is too broad before shot-level analysis. Use “large reconstruction-error separation on the preprocessed mean trajectory.”

Line 304 correctly limits LOPO. Keep that restraint in the Abstract and Conclusion.

The generalization in §7.4 to filtration, reactive porous media, swelling polymers, packed beds, and tissues needs citations or should be narrowed. The general principle is plausible, but the paper should not claim broad domain relevance without engaging those literatures.

## 6.12 Limitations

The Limitations section recognizes important issues but should be revised as follows:

- Replace “biological replication” with **shot-to-shot, coffee-lot, grinder, preparation, operator, and apparatus replication**.
- State explicitly that the 9-bar response is an averaged, smoothed trajectory.
- Make target-flow reuse a central limitation, not only a paragraph-level caveat.
- State that fixed-loss intervals do not represent between-shot uncertainty.
- Resolve the contradiction between line 245's implemented viscosity branch and line 337's statement that viscosity is outside the ladder.
- If Gagné remains, disclose its evidentiary status and limitations in Data and Methods rather than first introducing them in Limitations.

## 6.13 Conclusions

The conclusion is close to defensible but should be narrowed until shot-level analysis is complete.

Suggested revision:

> “For the source campaign's preprocessed mean trajectories, the tested time-invariant level descriptions reconstruct the 9-bar rise much worse than smooth temporal descriptions. The ordering is robust to the recorded pressure history, but the temporal branch partly reuses the target flow through its dissolved-mass input, and both temporal descriptions retain coherent residuals. The present analysis therefore supports temporal flexibility relative to the tested nulls; it does not identify a unique bed mechanism or establish transfer beyond this campaign.”

The final sentence about interventions is strong and should remain.

## 6.14 Data and code availability

Replace future-tense instructions with exact, immutable information before submission:

- release tag;
- commit hash;
- archive DOI;
- environment lock file;
- raw and processed data identifiers;
- file hashes;
- licenses;
- one-command reproduction instruction;
- claim manifest location; and
- figure source-data location.

Do not cite only a mutable GitHub main branch.

## 6.15 Figures

The figures are not embedded, so visual quality and evidentiary completeness cannot yet be assessed.

### Figure 1

Use visibly different styling for measured data, published model output, and repository reconstruction. Label pressure nodes and evidence status on the figure, not only in the caption.

### Figure 2

Add:

- individual-shot traces behind the mean;
- an uncertainty band with the correct SEM/SD label;
- the preprocessing/scoring window;
- residual panels large enough to show coherent structure; and
- a clear note that the cubic is fitted and scored on the same mean trace.

### Figure 3

Add shot count per pressure, fold-level markers, normalized error, and uncertainty. Avoid tiny eleven-facet panels that make residual patterns unreadable.

### Figure 4

The figure specification omits the viscosity row included in Table 4. Resolve this inconsistency. More importantly, add controls and discriminating thresholds rather than only qualitative arrows.

### Figure source data

Every panel should have a generated CSV/JSON source file and a manifest entry. Export vector graphics for publication and accessible raster versions for review.

## 6.16 Supplementary plan

Add supplements for:

- raw-shot inventory and reconciliation of 60/58/57 counts;
- individual-shot ladder results;
- leave-one-shot-out/cross-fitted `Φ(t)`;
- full preprocessing sensitivity;
- mass-domain analysis;
- dependency DAG and effective information provenance;
- recorded-pressure robustness;
- all LOPO folds;
- viscosity/Gagné methods if retained; and
- machine-readable claim mapping.

---

## 7. Line-specific comments

| Line(s) | Comment | Recommended change |
|---:|---|---|
| 1 | “many causes” may overstate what is demonstrated | Consider “many explanations” or one of the suggested titles |
| 3 | Draft date predates recent substantive additions | Update date/version |
| 7 | Correctly calls for a clean release, but current release evidence is stale/dirty | Replace with exact frozen release before submission |
| 11 | Calls the input a measured trace without saying it is an across-shot processed mean | Add experimental-unit and preprocessing disclosure |
| 11 | “establishes a need” is too strong before shot-level inference | Use “supports temporal flexibility relative to tested nulls” |
| 13 | “systems identification” may overpromise | Add formal identifiability work or change keyword |
| 17–25 | Strong framing, but needs broader inverse-problem literature | Expand related work and novelty statement |
| 33 | “primary example is the ... trace” | Say “preprocessed pressure-level mean trajectory” |
| 45 | Reports 60 brews but repository provenance/source tree do not align | Reconcile counts and exclusions |
| 45 | Equilibrium summary 110–120 s conflicts with visible implementation around 100 s | State exactly what was used and why |
| 47 | “source trace origin” appears inconsistent with pressure/start alignment | Correct time-origin description |
| 47 | Pressure node remains ambiguous in practice | Report nominal, machine, and basket pressure explicitly |
| 59 | Good disclosure of transferred within-campaign status | Retain and expand with target-flow dependency |
| 82 | “evaluated at 9 bar” | Add measured-pressure robustness result |
| 102 | Soft-circularity is acknowledged | Add dependency graph and cross-fitting |
| 109 | Broken LaTeX `Q_{\text{cub}}` | Correct equation |
| 112 | “in-sample flexibility floor” is not a formal floor | Use “same-trace descriptive benchmark” |
| 124–131 | Provenance table undercounts upstream information | Replace with full information-provenance table |
| 145 | Decimation does not solve residual dependence | Present richer residual diagnostics |
| 155 | 1,000 fixed-loss resamples are limited | Use more resamples, full algorithm, and shot-level inference |
| 157 | This caveat is correct | Keep it prominent in Abstract/Results |
| 169 | LOPO caveat is good | Rename analysis to equilibrium-calibration LOPO |
| 171 | `Q²` needs exact definition and fold details | Add formula, baseline, and uncertainty |
| 204 | “no coefficients fitted” can mislead | Add “temporal input partly derived from same flow” in table |
| 207 | “4.9 times lower” is awkward | Use “factor 4.9 smaller” or “80% lower” |
| 209 | “externally parameterized” conflicts with same-campaign construction | Replace with “same-campaign, target-informed” |
| 211 | Severe residual structure is substantively important | Expand figures and temper adequacy language |
| 215–217 | Conditional intervals are useful but not experimental CIs | Rename consistently and add shot-level analysis |
| 221 | `Q²≈0.81` from 11 points should not stand alone | Show all folds and leverage |
| 229–231 | Mean absolute RMSE hides pressure scale and shot-count variation | Add normalized, median, range, and uncertainty summaries |
| 241 | 4% final flow is highly transfer-specific | Keep sign conclusion separate from magnitude |
| 245 | Major unintegrated viscosity/Gagné addition | Remove or add full Data/Methods/Results/provenance/references |
| 249 vs 282 | “no data from these protocols” conflicts with external logged example | Clarify proposed matched protocols versus analogous external data |
| 256 | Direction-independence and rebrew predictions are too categorical | Add gradients, retained-solute, and resaturation caveats |
| 260 | Viscosity row is unsupported by manuscript methods | Remove or fully integrate |
| 270 | Reversal is not uniquely a fines test | Add inert/apparatus and stress controls |
| 274 | Rebrew can be affected by unloading, temperature, water content, and residual solubles | Add controls and quantitative endpoint |
| 282 | Gagné data/status first appear too late | Move source description to Data/Methods if retained |
| 286 | “would establish” is too strong | Use “would support, conditional on controls” |
| 292 | “strong evidence” overstates mean-trace result | Use quantitative, conditional wording |
| 304 | Good LOPO qualification | Repeat in Abstract/Conclusion |
| 310 | Cross-domain generalization lacks references | Cite or narrow |
| 329 | “biological replication” is inappropriate; Gagné claims need methods | Replace term and integrate source properly |
| 331 | Correctly flags soft circularity | Elevate to central design issue |
| 333 | Correctly limits block intervals | Add actual shot-level uncertainty analysis |
| 337 | Contradicts line 245 on viscosity status | Resolve |
| 341 | Conclusion should mention preprocessed mean and target reuse | Revise as suggested |
| 347–349 | Availability remains aspirational | Replace with exact release/DOI/hash/license details |
| 375 | Figure calls cubic a “bound” | Use “same-trace descriptive benchmark” |
| 383 | Figure 4 omits viscosity row from Table 4 | Reconcile |
| 387–395 | Supplement plan omits shot-level and cross-fit analyses | Add them |
| 397–405 | References omit sources used in new viscosity/Gagné text | Add complete citations or remove claims |

---

## 8. Recommended revised manuscript structure

A more publication-ready structure would be:

1. **Introduction**
   - inverse problem;
   - evidence hierarchy;
   - precise novelty.
2. **Evidence objects and data provenance**
   - Foster model output;
   - Waszkiewicz raw-shot campaign;
   - any separate Gagné object, if retained.
3. **Observation model and preprocessing**
   - sensors, nodes, alignment, differentiation, smoothing, interpolation, averaging, uncertainty.
4. **Analysis design and estimands**
   - mean-trajectory reconstruction;
   - held-out-shot analysis;
   - pressure-calibration LOPO;
   - conditional sign tests.
5. **Candidate model classes and information provenance**
   - static nulls;
   - target-informed `Φ(t)`;
   - same-trace empirical benchmark;
   - dependency graph.
6. **Results**
   - machine-side shape capacity;
   - individual-shot and mean 9-bar results;
   - cross-fitted temporal results;
   - residual structure;
   - pressure-calibration LOPO;
   - conditional mechanism signs.
7. **Discriminating experiments**
   - preregistration-ready protocols and controls.
8. **Discussion**
   - what is rejected;
   - what remains unidentified;
   - external validity;
   - limitations.
9. **Reproducibility and availability**
   - frozen release and claim map.

This restructuring would move the observation operator and experimental unit ahead of the model scores, where they belong.

---

## 9. Suggested wording revisions for central claims

| Current idea | Recommended wording |
|---|---|
| “The trace establishes a need for temporal dynamics.” | “The preprocessed mean trajectory rejects the tested time-invariant level descriptions and supports temporal flexibility within the declared model set.” |
| “No coefficients fitted to this flow trace.” | “No coefficient was optimized at the final reconstruction step, but the temporal input was partly constructed from same-campaign flow.” |
| “Externally parameterized temporal trajectory.” | “Same-campaign, target-informed temporal trajectory.” |
| “In-sample flexibility floor/bound.” | “Four-parameter same-trace descriptive benchmark.” |
| “LOPO held-out trace reconstruction.” | “Leave-one-pressure-out equilibrium-calibration reconstruction with the temporal input held fixed.” |
| “Viscosity magnitude reproduced the resistance decline.” | “A separate exploratory viscosity calculation produced a ratio of similar order under broad assumptions; this is compatibility, not attribution.” |
| “Reversal asymmetry would establish fines migration.” | “Reversal asymmetry, after apparatus and stress controls, would provide evidence consistent with spatially asymmetric transport or deposition.” |
| “Biological replication.” | “Shot-to-shot, coffee-lot, preparation, operator, grinder, and apparatus replication.” |

---

## 10. Recommended new analyses, in order of value

### Essential before submission

1. **Raw-shot inventory and count reconciliation.**
2. **Individual 9-bar shot model ladder.**
3. **Leave-one-shot-out or cross-fitted `Φ(t)` reconstruction.**
4. **Shot-level paired uncertainty with complete refitting.**
5. **Full preprocessing and smoothing sensitivity.**
6. **Mass-domain robustness analysis.**
7. **Recorded basket-pressure robustness in the manuscript.**
8. **Residual patterns by individual shot and pressure.**
9. **Clean B2 release and complete claim map.**
10. **Removal or complete integration of viscosity/Gagné.**

### High-value extensions

1. second coffee or grind setting;
2. second apparatus or control mode;
3. independently measured concentration or soluble-mass trajectory;
4. direct bed thickness/strain/porosity measurement;
5. pressure-step experiment with inert-load machine control;
6. matched forward/reverse experiment with apparatus control;
7. spent-puck replay with controlled rest, temperature, and resaturation;
8. formal observability or profile-likelihood analysis for competing dynamic closures.

---

## 11. Pre-submission acceptance checklist

### Data and experimental design

- [ ] Exact shot count per pressure stated.
- [ ] 60/58/57 source-accounting discrepancy resolved.
- [ ] Inclusion/exclusion criteria documented.
- [ ] Raw-shot and mean-trajectory roles distinguished.
- [ ] Pressure nodes and actual pressure histories reported.
- [ ] SEM fields corrected or explicitly aliased.
- [ ] Observation/preprocessing operator fully documented.
- [ ] Individual-shot results included.

### Model provenance and validation

- [ ] `Φ(t)` dependency graph included.
- [ ] Target-flow reuse quantified.
- [ ] Cross-fitted or held-out-shot temporal analysis completed.
- [ ] Cubic relabeled as same-trace descriptive benchmark.
- [ ] LOPO renamed and all folds reported.
- [ ] Effective information provenance replaces simple parameter count.
- [ ] Recorded-pressure robustness reported.

### Statistics

- [ ] Shot is the primary experimental unit.
- [ ] Model components are refitted inside uncertainty resamples.
- [ ] Fixed-loss block intervals are labeled conditional diagnostics.
- [ ] Complete block algorithm and seed reported.
- [ ] Residual plots and dependence diagnostics included.
- [ ] Normalized and fold-level pressure errors shown.
- [ ] No equivalence claim is made from a zero-crossing interval.

### Viscosity/Gagné

- [ ] Material removed, **or** full Data/Methods/Results/provenance added.
- [ ] All new sources cited.
- [ ] Data rights and access documented.
- [ ] Apparent resistance distinguished from bed resistance.
- [ ] Validated concentration/temperature ranges stated.
- [ ] Every numerical claim included in release gates.

### Reproducibility

- [ ] Clean tree and exact commit recorded.
- [ ] Release bundle fresh for manuscript commit.
- [ ] Environment locked.
- [ ] Inputs and outputs hashed.
- [ ] All seeds and tolerances recorded.
- [ ] Every manuscript number machine-checked.
- [ ] Figure source data exported.
- [ ] Archive DOI minted.
- [ ] `solids_calibration.csv` sign metadata corrected or annotated.

### Writing and figures

- [ ] Title finalized.
- [ ] Draft date and authorship completed.
- [ ] Abstract describes processed mean and target reuse.
- [ ] Central claims remain model-relative.
- [ ] “Systems identification” claim supported or removed.
- [ ] Figures rendered and visually inspected.
- [ ] Individual shots and uncertainty shown.
- [ ] References complete and verified.

---

## 12. Overall recommendation

**Major revision.**

The manuscript should not be rejected on the basis of the present draft. Its central null-first argument is worthwhile, the main numerical ordering is reproducible, and the authors already show commendable restraint about mechanism identification. The required revisions are substantial because they concern the experimental unit, the construction of the target and predictor, the meaning of uncertainty, and the reproducibility evidence—not merely presentation.

A successful revision would make a strong contribution by showing, with unusually transparent provenance, that:

1. machine dynamics can generate a commonly overinterpreted flow shape;
2. tested static level models fail on a specific preprocessed espresso trajectory;
3. a target-informed temporal construction and a flexible empirical curve both follow that trajectory much more closely;
4. neither fit identifies a unique bed process;
5. the result persists across individual held-out shots rather than only an averaged curve; and
6. carefully controlled interventions are required to discriminate the surviving explanations.

At present, points 1–4 are supported at the level of the committed mean trace, point 5 is not yet demonstrated, and point 6 is a promising but still qualitative experimental program. The revision should be organized around closing that gap.

---

## 13. Review scope and limitations

This review covered the manuscript, its current repository context, the relevant source-data and model paths, the committed reproducibility metadata, and targeted independent recalculation of the primary 9-bar metrics. It did not treat a successful calculation on the committed mean CSV as a substitute for a clean end-to-end repository release or raw-shot reanalysis. The manuscript's specified figures were not embedded and therefore could not be evaluated for final visual quality.

The independent calculations confirm the main rounded RMSE values and the negligible effect of substituting the recorded pressure histories. They do not remove the need for experimental-unit analysis, cross-fitting, complete model refitting, or external replication.

---

## 14. Evidence and source map

### Puckworks snapshot reviewed

- [Manuscript at reviewed commit](https://github.com/trbrewer/puckworks/blob/93358f8e4d7d5c214470d82195d852f455651ff9/PAPER_B2_TEMPORAL_DRAFT.md)
- [Puckworks harness at reviewed commit](https://github.com/trbrewer/puckworks/blob/93358f8e4d7d5c214470d82195d852f455651ff9/puckworks/harness.py)
- [Waszkiewicz poroelastic implementation](https://github.com/trbrewer/puckworks/blob/93358f8e4d7d5c214470d82195d852f455651ff9/puckworks/models/waszkiewicz2025/poroelastic.py)
- [Paper B build/claim logic](https://github.com/trbrewer/puckworks/blob/93358f8e4d7d5c214470d82195d852f455651ff9/puckworks/paper_b2/build.py)
- [Current committed Paper B manifest](https://github.com/trbrewer/puckworks/blob/93358f8e4d7d5c214470d82195d852f455651ff9/docs/reproducibility/paper_b_manifest.json)

### Upstream Waszkiewicz evidence

- [Time-dependent measurement formatter, source tag v1.0.1](https://github.com/RadostW/espresso/blob/v1.0.1/format_measurements_time_dependent.py)
- [Dissolved-solids fitting workflow, source tag v1.0.1](https://github.com/RadostW/espresso/blob/v1.0.1/fit_model_solids.py)
- [Static-flow fitting workflow, source tag v1.0.1](https://github.com/RadostW/espresso/blob/v1.0.1/fit_model_static_flow_rate.py)
- [Waszkiewicz et al. article](https://arxiv.org/html/2512.21528v2)
- Waszkiewicz data/code archive: DOI `10.5281/zenodo.18046315`

### Local audit artifact

- `PAPER_B2_independent_audit_2026-07-25.json`


# One flow curve, many explanations: null-first inference for machine and porous-bed dynamics in espresso

**Working manuscript draft — 15 July 2026**  
**Authors:** [Author names and affiliations to be inserted]  
**Corresponding author:** [Name and email to be inserted]

> **Draft status.** This manuscript was developed from `PAPER_B2_TEMPORAL_OUTLINE.md`, the retained synthesis in `PAPER_B_DRAFT.md`, the model/source cards, and the generated analyses in the Puckworks repository. The numerical values below reproduce the current repository evidence record; they should be regenerated from, and cited to, a clean versioned release before submission. Figures are specified as publication-ready panels and captions but are not embedded in this Markdown draft. This is not a claim that the repository corpus or the present analyses are complete.

## Abstract

Time-resolved espresso outlet flow integrates machine response, pressure boundary conditions, wetting, evolving bed resistance, extraction, and measurement processing, so similar curve shapes need not imply the same mechanism. We use a null-first comparison to ask whether a measured trace requires time-varying predictions relative to specified time-invariant branches, and whether that requirement identifies a bed process. A published pump–headspace–infiltration model first demonstrates that a mid-shot flow minimum can arise without an evolving bed. We then analyse the differentiated, approximately 3 s-smoothed, aligned, interpolated mean of five nominal 9-bar brews over 15–95 s. The best constant and a static pressure-dependent poroelastic branch have RMSEs of 0.573 and 0.648 g s⁻¹. A dissolution-linked empirical Φ(t) trajectory, whose temporal input is partly derived from the same campaign flow, has RMSE 0.116 g s⁻¹; a four-parameter cubic fitted and scored on the same mean trace has RMSE 0.096 g s⁻¹. At the shot level, Φ(t) improves on the constant and static branches in all five brews, by mean paired differences of 0.390 and 0.472 g s⁻¹. The exact two-sided sign-flip p-value is 0.0625 — the smallest attainable with five nonzero paired differences — so we emphasise effect size and directional consistency rather than significance. A fixed-architecture empirical template trained on the other four brews, and fully held out, predicts the omitted brew with mean RMSE 0.186 g s⁻¹, against 0.189 g s⁻¹ for the partly target-informed Φ(t) trajectory, with the five paired differences split two to three; the named closure therefore shows no new-shot predictive advantage. Across the eleven tested nominal pressure settings the best-reconstructing branch varies, with Φ(t) lowest at 7, 8, 9 and 11 bar only, and scoring all 57 included shots individually rather than averaging pressure-level mean curves raises every branch's error. Residuals remain strongly structured, with power concentrated at low frequencies. We conclude that time-varying predictions are required relative to the tested time-invariant branches, but that the integrated flow curve does not identify the responsible mechanism. Pressure steps, flow reversal, spent-puck rebrewing, and spatial state measurements provide more discriminating tests than further unconstrained fits to the same trajectory.

**Keywords:** espresso; porous media; inverse problems; model discrimination; model comparison; temporal dynamics; permeability; poroelasticity; block resampling; experiment design

## 1. Introduction

A time trace is richer than a final cup measurement, but it is not automatically a mechanism measurement. In espresso brewing, outlet flow reflects a chain that includes the pump characteristic, pipe and headspace dynamics, pressure at the basket, infiltration of an initially unsaturated bed, viscous and inertial pressure losses, deformation and rearrangement of the granular matrix, solute removal, fines transport, and the response of the scale or flow sensor. The measured curve is therefore an integrated observable of a coupled machine–porous-medium system. Interpreting a local minimum, a late rise, or a change in slope as a named bed process requires more than matching that shape with one plausible model.

Several published model lineages make this ambiguity concrete. Foster et al. coupled a pump characteristic, trapped-air headspace, and sharp-front infiltration and obtained a flow minimum without extraction, swelling, fines transport, or particle rearrangement [1]. Waszkiewicz et al. developed a poroelastic equilibrium pressure–flow relation and a time-dependent extension in which a stress-free porosity scale follows dissolved mass [2]. Mo et al. modeled water uptake by coffee particles, bed-porosity reduction, and Carman–Kozeny throttling [3]. Fasano, Talamucci, and Petracco analyzed fines removal, compact-layer formation, porosity evolution, and pressure-history effects in a family of one-dimensional free-boundary models [4]. Each model is scientifically meaningful within its assumptions, yet their state variables and boundary conditions differ enough that “the model reproduces the curve” is not a symmetric or identifying comparison. Integrated modeling and experiment have also been used to connect espresso process variables with extraction outcomes [5].

The present study adopts a null-first strategy. A candidate mechanism should first be compared with the simplest model class capable of expressing the relevant observable. If a machine-only model can generate the shape, the shape is not uniquely attributable to the bed. If every static bed model leaves a large coherent residual but a temporal model reduces it, the evidence supports temporal flexibility relative to those static nulls. If a flexible, non-mechanistic time function performs as well as a mechanistic trajectory, fit quality alone does not identify the mechanism. Mechanistic discrimination must then come from parameter provenance, held-out conditions, sign constraints, independently measured state variables, or interventions that force candidate models to make different predictions.

We apply this strategy to two distinct objects that are deliberately not merged. The first is the published model curve from Foster et al.; it is used only to demonstrate machine-side capacity for a dip-and-recovery shape. The second is the measured pressure campaign of Waszkiewicz et al.; it supplies the rising-flow trace and the multi-pressure assessment. This separation is essential: reproducing the Foster model curve does not explain the Waszkiewicz data, and the Waszkiewicz temporal comparison does not retroactively identify the cause of the Foster curve.

The study makes four scoped contributions. It shows that a machine-only null can reconstruct a commonly mechanized flow shape; quantifies a static-to-temporal model ladder on a fixed 9-bar scoring interval; assesses calibration stability and trace reconstruction across eleven pressures using shared and leave-one-pressure-out fits; and translates the remaining non-uniqueness into a set of controlled perturbations. The maximum defensible conclusion is intentionally limited: an integrated flow trace can establish the need for temporal dynamics relative to specified static nulls, but it cannot, without additional observables or interventions, uniquely identify the underlying bed mechanism.

## 2. Data and observable definitions

### 2.1 Evidence objects and their roles

The analysis uses three kinds of evidence object, and the distinction is retained in every figure and table.

1. **Measured trace.** A time series recorded during an espresso experiment. The primary example is the Waszkiewicz 9-bar basket-pressure flow trace [2].
2. **Published model output.** A curve generated by a published model, whether or not the source model was calibrated against measurements. The Foster flow-minimum curve belongs to this category [1].
3. **Digitized or repository reconstruction.** A numerical transcription or reimplementation used to reproduce a source curve or evaluate an equation on a common grid. Such a result tests implementation and model capacity; it is not converted into a new experimental observation.

This manuscript uses “observed” only for measured quantities, “reconstructed” for agreement obtained after applying a model or fitted curve, and “held out” only where a condition was excluded from the relevant calibration. These terms are not interchangeable.

### 2.2 Foster machine–infiltration source curve

Foster et al. studied liquid infiltration into an espresso bed with time-resolved micro-computed tomography and a coupled one-dimensional model [1]. The model contains a quadratic pump characteristic, pipe resistance, trapped-air headspace compression, ponding, and a sharp wetting front. The bed permeability in this calculation need not evolve with extraction or mechanical damage. The relevant observable is the published normalized bed-flow curve, whose mid-shot minimum is reconstructed by the repository implementation of the source equations. We use this case as a capacity test: can a machine and filling subsystem generate a dip followed by recovery in the absence of a dynamic bed mechanism? It is not scored against the Waszkiewicz trace.

### 2.3 Waszkiewicz pressure campaign

Waszkiewicz et al. reported a campaign of 60 brews at eleven basket pressures spanning approximately 1 to 12.5 bar on one machine, coffee, grind, dose, and preparation protocol [2]. The dose was approximately 18.5 g in a 58 mm basket. The source summarized long-run flow for the equilibrium pressure–flow relation over 110–120 s. **This analysis does not use that statistic and does not claim to.** The source's own published formatter truncates every trace at 100 s, so the released aggregate cannot contain a 110–120 s value; our equilibrium observable is therefore the **final 100 s value of each preprocessed per-pressure mean**, stated here as a repository observable rather than attributed to the source. It is not a material choice: it reproduces the source's own static fit ($P_c$ 12.394 vs 12.39 bar; $Q_c$ 1.907 vs 1.897 g s⁻¹), and substituting a 90–100 s mean moves the fit by 0.003 bar and 0.007 g s⁻¹. We also checked the nominal 110–120 s window against the *raw* per-brew traces, which are not truncated: it is **not usable as published**, because one shot (`9-1`, at the scored 9-bar condition) has plainly ended inside it — cup mass falls, giving a large negative flow derivative and −106 bar through the brewer-calibration subtraction — and that single shot alone drags the refit to $P_c\approx82$ bar. Excluding it would be an exclusion the source did not make; done anyway it gives $P_c$ 11.935, $Q_c$ 1.861, i.e. broadly consistent. Producer: `analysis.waszkiewicz_shot_level.equilibrium_window_sensitivity`. Time-dependent flow and total-dissolved-solids measurements were also reported. The source model explicitly excludes the first approximately 5–10 s, when wetting, air expulsion, and other unsaturated processes dominate. Our primary temporal analysis therefore uses the saturated interval from 15 to 95 s. Sensitivity analyses use 10–90 s and 20–90 s.

Pressure is treated as basket gauge pressure where the source dataset identifies that node. Flow is reported as mass flow in g s⁻¹. Time is measured from the source trace origin. The repository adapters align all candidate predictions to the same observed time points and apply one common scoring mask per comparison. No model is rewarded by using a different evaluation interval.

### 2.4 Primary observable and estimand

Let the measured flow at time $t_i$ be $Q_i$ and the prediction from branch $m$ be $\widehat{Q}_{m,i}$. The primary score is

$$
\operatorname{RMSE}_m =
\left[\frac{1}{n}\sum_{i=1}^{n}
\left(Q_i-\widehat{Q}_{m,i}\right)^2\right]^{1/2}.
$$

The estimand is reconstruction error on a declared time interval. For the cubic branch and the best constant, this is in-sample error because those coefficients are fitted on the same trace. For the empirical porosity branch, the 9-bar flow trace supplies no newly fitted flow coefficient, but the branch imports an equilibrium calibration and a dissolved-mass trajectory from the same campaign. It is therefore a transferred within-campaign reconstruction, not an independent prediction.

**Observation operator.** The quantity $Q_i$ scored above is not a single raw shot. The upstream formatter records mass and pressure at roughly 10 Hz per shot, locates a pressure-stabilization start index and shifts time to it, obtains flow by numerical differentiation of the mass signal, applies a Savitzky–Golay filter (31-sample window, first-order polynomial — about 3 s at 10 Hz), interpolates each shot onto a common 0–100 s grid of 1,000 points, groups by nominal pressure, and averages across the shots at that pressure. The 9-bar "trace" is therefore a differentiated, ~3 s-smoothed, time-aligned, interpolated, **across-shot mean** (five included shots at 9 bar), and the primary scored window is 15.015–94.995 s (800 points). The dispersion columns emitted alongside the mean (e.g. `mass_flow_rate_std`) are computed with `pandas.DataFrame.sem()` and are therefore pointwise **standard errors of the mean, not standard deviations**; they are labelled accordingly here. Because the experimental replicate is the shot rather than the time point, the shot-level uncertainty and per-shot ladder that this operator makes possible are **reported in §5.2a**; the scores in this section are at the level of this preprocessed mean trajectory, and §5.2a states what changes when the shot is the unit. Remaining limitations of the operator are in §8.

## 3. Model-comparison ladder

### 3.1 Machine-only null

The Foster system provides a machine-side null. The pump flow depends on pump outlet pressure; pipe resistance separates pump and headspace pressure; trapped gas changes headspace pressure as liquid ponds; and flow into the bed is the lesser of pump supply and the infiltration-limited flux [1]. The competing rates can create a minimum and recovery even when bed permeability and particle state are not changing. Because the present purpose is a shape-capacity test, we use the published source configuration rather than fitting the machine model to the Waszkiewicz campaign.

### 3.2 Static equilibrium poroelastic relation

The Waszkiewicz model combines Darcy flow, effective-stress balance, a linear strain–porosity law, and Carman–Kozeny permeability [2]. Its approximately universal normalized equilibrium relation is

$$
\widehat q(\widehat p)
\approx \widehat p\left(4-6\widehat p+4\widehat p^2-\widehat p^3\right),
$$

where $\widehat p$ is pressure normalized by a characteristic pressure $P_c$ and $\widehat q$ is flow normalized by a characteristic flow $Q_c$. At one constant imposed pressure, this static relation predicts one constant level. It can represent nonlinear variation of equilibrium flow across pressures but cannot represent temporal change within a constant-pressure shot.

We compare three constant or static baselines at 9 bar:

- the least-squares-optimal constant on the scoring interval;
- a late-window constant estimated from a real 10 s interval near the end of the source trace; and
- the static poroelastic relation evaluated at 9 bar using the campaign equilibrium calibration.

The first is the strongest constant null for in-window RMSE. The second tests sensitivity to a physically interpretable late level. The third asks whether a nonlinear pressure–flow curve alone explains temporal structure at fixed pressure.

### 3.3 Dissolution-linked temporal porosity trajectory

The time-dependent Waszkiewicz extension writes the stress-free porosity scale as a function of dissolved mass. In the source notation,

$$
Q(t)=Q_c\,
\frac{F[\Phi(t)]}{F(\Phi_m)}
\widehat q\!\left(\frac{P\Phi_m}{P_c\Phi(t)}\right),
$$

with

$$
\Phi(t)=\frac{m_d(t)}{m_0}.
$$

Here $m_0$ is the dose, $m_d(t)$ is cumulative dissolved mass, $\Phi_m$ is its asymptotic scale, and $F$ is the porosity-dependent normalization inherited from the poroelastic derivation [2]. The repository implementation uses the source equilibrium calibration and an empirical sigmoid for dissolved mass derived from the campaign’s flow and total-dissolved-solids measurements. No coefficient is fitted directly to the 9-bar $Q(t)$ trace for this branch. Nevertheless, because $m_d(t)$ uses measurements from the same rig and campaign and is partly constructed from $Q(t)$, the result is soft-circular. We therefore call it a transferred empirical temporal reconstruction rather than a parameter-free prediction.

### 3.4 Flexible temporal null

A degree-three polynomial in time,

$$
Q_{	ext{cub}}(t)=a_0+a_1t+a_2t^2+a_3t^3,
$$

is fitted and scored on the same interval. It has no bed-mechanism interpretation. Its purpose is to bound what smooth temporal flexibility can achieve with four free coefficients. It is not a fair predictive challenger to the imported porosity branch; it is a same-trace descriptive benchmark, not a predictive challenger and not a lower bound. If the mechanistic trajectory does not clearly improve on this floor, the trace fit cannot be used to identify that mechanism.

### 3.5 Alternative dynamic branch for cross-pressure comparison

The cross-pressure assessment also includes a flow-coupled dynamic variant, denoted RC-3b in the repository. It combines the equilibrium pressure relation with a donor extraction trajectory rather than the empirical 9-bar dissolved-mass sigmoid. The branch is included to test whether one temporal closure transfers better across pressure. It is a project synthesis, not a model validated by the Waszkiewicz paper, and its donor assumptions remain fixed in the held-out calculations.

### 3.6 Parameter provenance and effective flexibility

Raw parameter count is insufficient unless the fitting target is stated. Table 1 separates coefficients fitted to the scored flow trace from parameters fitted elsewhere in the same campaign and parameters or functional forms fixed from literature.

**Table 1. Parameter provenance for the 9-bar temporal ladder.**

| Branch | Coefficients fitted to this $Q(t)$ trace | Parameters fitted elsewhere in the same campaign | Literature/donor-fixed content | Intended role |
|---|---:|---|---|---|
| Best constant | 1 level | 0 | none | strongest static in-window null |
| Late-window constant | 0 on scoring interval | 1 level from late interval | none | interpretable static sensitivity |
| Static $\kappa(P)$ / poroelastic equilibrium | 0 | 2 equilibrium parameters, $P_c$ and $Q_c$ | constitutive form | pressure-dependent static null |
| Empirical $\Phi(t)$ | 0 | 2 equilibrium + 3 dissolved-mass sigmoid parameters | constitutive form | mechanistically motivated temporal candidate |
| RC-3b | 0 | 2 equilibrium parameters | donor extraction calibration | cross-pressure temporal challenger |
| Flexible cubic | 4 | 0 | polynomial form | same-trace four-parameter descriptive comparator |

This provenance prevents two common misreadings. First, the empirical $\Phi(t)$ result is not “parameter-free”: it imports estimated quantities. Second, the cubic’s lower RMSE is not evidence of better prediction because the same trace both fits and scores it.

## 4. Statistical and diagnostic analysis

### 4.1 Residual structure

For each branch, residuals are

$$
e_{m,i}=Q_i-\widehat Q_{m,i}.
$$

We report residual-versus-time curves, lag-1 autocorrelation, and the Durbin–Watson statistic for **every** branch on the **same** declared grid, obtained by decimating the approximately 10 Hz trace to a stated resolution; 1 s is primary and 5 s is reported as a sensitivity. Reporting the two statistics at a common resolution matters because they are not resolution-invariant: for the $\Phi(t)$ branch the lag-1 autocorrelation falls from 0.969 at 1 s to 0.533 at 5 s and the Durbin–Watson statistic rises from 0.047 to 0.823. A summary that combined statistics computed at different sampling scales would not be interpretable. Each residual scale is additionally divided by the mean pointwise between-shot standard deviation, because a residual that is strongly autocorrelated but smaller than the shot-to-shot spread is a different situation from one that is both autocorrelated and larger than it. Strong positive correlation indicates coherent unmodeled structure and invalidates an interpretation of pointwise residuals as independent noise.

### 4.2 Conditional fixed-loss block-resampling sensitivity

To compare two fixed predictions $A$ and $B$, define the pointwise squared-error difference

$$
d_i=(Q_i-\widehat Q_{A,i})^2-(Q_i-\widehat Q_{B,i})^2.
$$

Blocks are resampled from the two squared-error sequences **through common indices**, not from the difference sequence $d_i$: each resample draws $\lceil n/b\rceil$ contiguous index blocks of length $b$ with replacement, concatenates and truncates them to the original length $n$, and applies that **same index vector to both** $(Q_i-\widehat Q_{A,i})^2$ and $(Q_i-\widehat Q_{B,i})^2$. Each branch's RMSE is then recomputed from its own resampled loss sequence and the difference of the two RMSEs is recorded. Resampling the paired losses jointly preserves the pairing; resampling $d_i$ alone would not, and would also not reproduce the RMSE difference, which is not the mean of $d_i$. Block starts are drawn uniformly from $\{0,\dots,n-b\}$, so the scheme is **non-circular** — no wraparound — and end points are therefore slightly under-represented. The primary block duration is 8 s ($b$ rounded to the nearest sample at the trace's median spacing) with **1,000** resamples at seed 0; sensitivity uses 4, 8, 16, and 24 s blocks, each with its own deterministic stream derived from that seed and the block length. This follows the general moving-block principle for dependent observations [6].

This procedure preserves local dependence in the already-computed loss sequences, but it does not refit the constant, cubic, equilibrium calibration, or temporal trajectory inside each resample. The resulting interval is therefore conditional on the fixed predictions. It is not a bootstrap confidence interval for the full fit–compare procedure, and it is not a test of model truth. We report whether an interval resolves the sign of the reconstruction difference rather than labeling unresolved differences “equivalent” or “statistically indistinguishable.” **This block analysis is a secondary within-curve sensitivity only.** The primary uncertainty statement is at the level of the shot (§4.2a).

### 4.2a Shot-level paired uncertainty (primary)

The independent experimental unit is the shot, not the time sample. The 9-bar condition comprises **five** brews, so the primary uncertainty statement re-scores every branch against each individual brew, re-optimizing each branch's own free parameters within each unit, and reports the five paired differences in full.

With five units a percentile bootstrap is not credible, so the primary statement is exact rather than asymptotic. Under the sign-symmetry null we enumerate all $2^5=32$ sign assignments of the paired differences and report the exact two-sided randomization $p$-value. **A structural consequence must be stated before any result is read: with five paired units the smallest attainable two-sided $p$-value is $2/32=0.0625$, so no paired randomization test on this design can reach a conventional $0.05$ threshold, however large the effect.** We therefore report the effect size, the number of shots favouring each branch, and that exact $p$-value together, and we do not describe any comparison here as significant. A five-unit percentile bootstrap is reported alongside and labelled indicative.

Across-shot variability is summarized descriptively, on two scales, and neither is treated as a floor. The **leave-in shot-to-full-mean dispersion** is the mean RMSE between each brew and the across-shot mean curve — **0.149 g s⁻¹**. That value is optimistic by construction: each brew contributes a fifth of the mean it is compared against. The optimism is exact rather than arguable, because $Q_i-\bar Q_{-i}=\tfrac{n}{n-1}(Q_i-\bar Q)$, so with $n=5$ every leave-one-out distance is exactly $1.25\times$ the leave-in distance. The honest counterpart is the **leave-one-shot-out other-four empirical-template RMSE** — each brew against a template formed from the other four — which is **0.186 g s⁻¹**. The mean pointwise between-shot standard deviation is **0.154 g s⁻¹**.

None of these is an irreducible noise floor, a lower bound on model error, or a threshold for declaring a difference resolvable. A model with genuine shot-specific covariates could predict an individual brew better than the other-four template; a misspecified one could do worse. All three combine material repeatability, preparation variation, alignment, smoothing and measurement effects, and rest on five brews from one condition. Inference about model differences is therefore made from the five paired differences and the exact sign-flip test, never by comparing a point estimate with any of these scales.

### 4.2b Held-out flexible temporal comparator

The four-parameter cubic is fitted and scored on the same trace, so it establishes only that a smooth curve can interpolate the data. We therefore add a **fixed-architecture penalized cubic B-spline** — twelve interior knots, second-difference penalty, smoothing weight chosen by generalized cross-validation **on the training data only** — evaluated under two protocols in which it never sees the points it is scored on:

* **Leave-one-shot-out.** Fit on the mean of the other four brews; predict the held-out brew. The constant null is refitted the same way, so both are held out identically.
* **Leave-segment-out.** Within each brew, hold out contiguous time segments in turn and predict them from the remaining segments of the same brew. The first and last segments require the spline to extrapolate beyond its support, where a penalized smoother is not defined in any useful sense; those segments are reported but the headline is the interior-segment mean, which is the interpolation question this protocol is meant to ask.

The $\Phi(t)$ branch is also evaluated under its own equilibrium cross-fit. That removes one reuse channel but **does not make the comparison symmetric**: the spline is fully held out, whereas $\Phi(t)$'s dissolved-mass channel is derived partly from the same flow campaign and cannot be withheld, because the TDS replicates were never shot-matched to these flow traces. Every comparison between the two states which access channels remain unwithheld.

### 4.3 Window sensitivity

The full ladder is repeated for 10–90 s, 15–95 s, and 20–90 s. The primary 15–95 s interval balances exclusion of the unsaturated startup with retention of the rising phase. A conclusion is described as window-robust only if its direction persists across all three intervals.

### 4.4 Shared and leave-one-pressure-out assessment

The equilibrium calibration uses eleven long-run pressure–flow points. Two forms of multi-pressure assessment are kept separate.

**Shared calibration.** One pair $(P_c,Q_c)$ is fitted using all eleven long-run points and then used to reconstruct all time traces.

**Leave-one-pressure-out equilibrium-calibration sensitivity (LOPO-EC).** The name states the scope deliberately: only the *equilibrium calibration* is withheld, so this is a calibration sensitivity and **not** held-out trace validation. We avoid the bare term "held-out" for it throughout. For each pressure $P_j$, $(P_c,Q_c)$ is refitted using the other ten equilibrium points. The held-out pair is then used to reconstruct the trace at $P_j$. The 9-bar dissolved-mass trajectory and donor assumptions are held fixed; only the two equilibrium parameters are refitted. Thus, LOPO prevents the held-out pressure’s equilibrium point from contributing to its own equilibrium calibration, but it is not a fully independent test of the temporal trajectory.

We report per-pressure RMSE, mean RMSE across all eleven pressures, maximum calibration drift, and the leave-one-pressure-out predictive coefficient $Q^2$ for the equilibrium curve. We avoid categorical “regimes” because pressure bins were not prespecified and the residual patterns vary continuously.

### 4.5 Conditional sign and compatibility tests

Fit quality can be non-identifying even when a mechanism’s direction is informative. We therefore test the sign of isolated candidate branches under a fixed-pressure boundary condition.

For the Mo swelling branch, particle water uptake increases particle volume, decreases bed porosity in a fixed-height bed, and lowers Carman–Kozeny conductivity [3]. At fixed pressure drop, the isolated branch therefore predicts monotonically falling flow. The repository reimplementation evaluates this transferred parameterization directly.

For the Fasano fines-migration branch, removal and downstream deposition increase resistance through a compact layer. Under the assumptions of the Part I model, discharge at constant imposed pressure is monotone non-increasing; later analysis allows renewed removal or increased flux when applied pressure rises [4]. This supplies an analytic conditional sign result.

These tests constrain an isolated resistance-only branch with machine state and other bed variables held fixed. They do not establish that swelling or fines migration is absent from a real shot. A coupled bed may contain resistance-increasing swelling or deposition while dissolution, pressure change, elastic recovery, erosion, gas release, or another process dominates the net flow derivative.

## 5. Results

### 5.1 A machine-only system can generate dip and recovery

The Foster reconstruction reproduces the source model’s mid-shot flow minimum using the pump, headspace, and infiltration subsystem alone [1]. No extraction-driven porosity change, particle swelling, fines migration, or channel evolution is required in this configuration. The result is a model-capacity statement: the tested machine subsystem can produce a dip followed by recovery. It does not imply that every observed dip is machine-generated, nor does it transfer the Foster parameterization to the Waszkiewicz apparatus.

**Figure 1 near here.**

The implication for inference is nevertheless strong. A qualitative dip-and-recovery shape cannot, by itself, identify an evolving puck. A diagnostic claim requires either a machine null calibrated to the same apparatus, a boundary-condition measurement that rules the machine response out, or a perturbation under which the machine and bed models diverge.

### 5.2 The 9-bar trace requires temporal flexibility relative to tested static nulls

Table 2 reports the primary-window errors.

**Table 2. Reconstruction errors on the 15–95 s interval of the measured 9-bar trace.**

| Branch | RMSE (g s⁻¹) | Interpretation |
|---|---:|---|
| Best constant | 0.573 | strongest one-level static null |
| Late-window constant | 0.641 | constant estimated from a real late interval |
| Static $\kappa(P)$ | 0.648 | nonlinear across pressure, constant within a 9-bar shot |
| Empirical $\Phi(t)$ | 0.116 | temporal candidate; no coefficient fitted to this flow trace, but its temporal input is partly derived from the same flow (§5.3c) |
| Flexible cubic | 0.096 | four-parameter same-trace descriptive benchmark (not predictive) |

All three constant or static baselines leave errors between 0.57 and 0.65 g s⁻¹. The empirical temporal trajectory reduces RMSE to 0.116 g s⁻¹, approximately a factor of 4.9 smaller than the best constant and 5.6 smaller than the static pressure-dependent branch. Within the tested model set and interval, a static level is therefore inadequate.

The four-parameter cubic reaches 0.096 g s⁻¹. Its fit is at least as close as the mechanistic trajectory, so the reconstruction does not identify the poroelastic–dissolution closure. Instead, the non-trivial result is that a same-campaign, target-informed temporal trajectory nearly reaches the same-trace descriptive benchmark without fitting an additional coefficient to the scored flow trace (its temporal input, however, is partly built from that same flow; §5.3c).

Residuals remain strongly structured. On the declared 1 s series, lag-1 residual autocorrelation ranges from **0.904** (the cubic) to **0.969** ($\Phi(t)$), and the Durbin–Watson statistics range from **0.004** to **0.067**, with a mean of **0.031**. The low RMSE of the temporal branches therefore coexists with coherent lack of fit. Neither branch reduces the residual to white measurement noise, so the small gap between the temporal branch (0.116) and the same-trace descriptive benchmark (0.096) should not be over-read.

**Why the composite branch fails.** The imported swelling branch, added to the shared-porosity composition reported in the companion registry paper, produces a composite reconstruction RMSE of 0.648 g s⁻¹ — numerically identical to the static $\kappa(P)$ branch above. That coincidence is structural rather than accidental and is worth stating, because it changes what the failure means. The swelling branch pushes the shared porosity below its initial value across the entire scored window, so the dissolved-mass proxy that drives the temporal closure sits on its numerical floor for 100 % of the window and the closure returns its own $\Phi\to0$ limit, which is exactly the static equilibrium curve. The composite prediction is therefore constant to numerical precision. The composition does not degrade the temporal reconstruction; it removes it.

**Recorded-pressure robustness.** The ladder above evaluates the branches at nominal 9 bar. Substituting the recorded basket-pressure history point by point changes the results negligibly: the static poroelastic RMSE moves from 0.647696 to 0.646846 g s⁻¹ (−0.00085) and the empirical $\Phi(t)$ RMSE from 0.115769 to 0.116443 g s⁻¹ (+0.00067); both shifts are below 0.001 g s⁻¹ and the branch ordering is unchanged. The observed rise is therefore not an artifact of the small measured pressure drift in this campaign — a robustness result, not evidence for any mechanism.

**Figure 2 near here.**

The conditional moving-block analysis supports the same two-part conclusion. For empirical $\Phi(t)$ minus the best constant, the median RMSE difference is approximately −0.39 g s⁻¹ with a 95% interval of −0.60 to −0.23 g s⁻¹. The interval excludes zero, supporting the need for temporal flexibility relative to the constant null. For empirical $\Phi(t)$ minus the cubic, the difference is approximately +0.02 g s⁻¹ with a 95% interval of −0.01 to +0.05 g s⁻¹. This interval does not resolve which branch reconstructs better.

### 5.2a Shot-level results: the ordering survives, the mechanistic advantage does not

Re-scoring against each of the five individual 9-bar brews reproduces the ordering the mean curve shows, and the exact randomization analysis attaches the strongest support this design can carry. The empirical $\Phi(t)$ branch beats the best constant on **5 of 5** brews, by a mean of **−0.390 g s⁻¹**, and beats the static $\kappa(P)$ branch on **5 of 5** by **−0.472 g s⁻¹**. Both carry the exact two-sided randomization $p=0.0625$. That is the *smallest attainable* value with five nonzero paired differences, so it is design-limited; the realized statistic still depends on the observed differences and on the assumed sign-symmetry null. We therefore emphasize the effect sizes and their directional consistency — all five brews, both comparisons — rather than a thresholded significance claim. For scale, the two effects are 2.1 and 2.5 times the other-four empirical-template RMSE of **0.186 g s⁻¹**; this is a descriptive ratio and not a significance criterion. The $\Phi(t)$-versus-cubic difference is **+0.083 g s⁻¹** in the cubic's favour on 5 of 5 brews — and the cubic is in-sample in any case, so it bounds interpolation, not prediction.

The held-out flexible comparator changes the reading of the temporal claim, and it should. Under **leave-one-shot-out**, the penalized spline — which never sees the brew it is scored on — reaches **0.186 g s⁻¹**, against **0.189 g s⁻¹** for $\Phi(t)$ and **0.190 g s⁻¹** for $\Phi(t)$ under its equilibrium cross-fit. The mean difference is **0.003 g s⁻¹**, but a mean conceals the structure: the five paired differences split **2 in $\Phi(t)$'s favour and 3 in the spline's**, with a standard deviation of 0.026 g s⁻¹ and an exact two-sided sign-flip $p$ of **0.8125**. There is no directional consistency here at all.

**The two branches are not equally held out, and every comparison between them must say so.** The spline is *fully* held out: it never sees the brew it is scored on. $\Phi(t)$ is *partly target-informed*: its equilibrium calibration is cross-fitted, but its dissolved-mass channel is derived partly from the same flow campaign and is not withheld, because the TDS replicates were never shot-matched to these flow traces. The comparison is therefore asymmetric in the direction that *favours* $\Phi(t)$.

That makes the conclusion stronger, not weaker: **a fully held-out empirical template performs as well as a partly target-informed mechanistic trajectory, so the dissolution-linked closure shows no new-shot predictive advantage and the evidence does not identify the dissolution–poroelastic closure.** Both are far better than the held-out constant (**0.600 g s⁻¹**) and the static branch (**0.661 g s⁻¹**).

It is also worth naming what the spline actually is. Its mean RMSE differs from simply using the unsmoothed mean of the other four brews (0.1864 g s⁻¹) by **0.0004 g s⁻¹**. Its predictive power is therefore the repeatability of the common trajectory across brews made on the same rig, coffee, grind, dose, nominal pressure and preprocessing pipeline — a **same-condition empirical template** — not an abstract property called "generic smoothness". That is the appropriate comparator for the question "does the closure add predictive value beyond the repeatability of the average shot shape?", but it should be named correctly.

An exploratory **leave-segment-out** analysis was also run, in which a contiguous time interval is withheld from a brew and predicted from the remaining segments. It is **not** reported as a result here, because it does not survive its own sensitivity checks. Against the manuscript's five-segment partition $\Phi(t)$ reaches 0.158 g s⁻¹ on interior segments and the penalized spline 0.233 g s⁻¹ — but simple linear interpolation across the withheld interval reaches **0.071 g s⁻¹** and a cubic fitted only to the non-withheld points reaches **0.136 g s⁻¹**, so both generic comparators beat $\Phi(t)$. The ranking also moves with the partition: at six or more segments the same penalized spline beats $\Phi(t)$ as well. The result is an artifact of one gap definition and one comparator, not a stable finding, and $\Phi(t)$ is in any case not reconstructed without access to the withheld interval's own campaign. It is retained in the supplement as exploratory material and contributes nothing to the mechanistic conclusion.

Residual diagnostics at the declared 1 s resolution show that every branch leaves coherent structure. Lag-1 autocorrelation is 0.958 for the constant, 0.958 for the static branch, 0.969 for $\Phi(t)$ and 0.904 for the cubic, with Durbin–Watson statistics of 0.005, 0.004, 0.047 and 0.067. Decimating further to 5 s reduces but does not remove the structure (0.786 / 0.786 / 0.533 / 0.471). Measured against the mean pointwise between-shot standard deviation of **0.153 g s⁻¹**, the constant and static residuals are **3.8** and **4.3** times shot-to-shot variability while $\Phi(t)$ and the cubic sit at **0.76** and **0.65** times it. The temporal branches therefore reconstruct to within shot-to-shot variability while still leaving strongly autocorrelated residuals — a combination that rules out reading either as a validated mechanism.

Reporting more than one error summary also changes one ordering, which is why we report several. On mean absolute error the static $\kappa(P)$ branch (**0.370 g s⁻¹**) is *better* than the best constant (**0.478 g s⁻¹**), the reverse of their RMSE ranking (0.661 against 0.583), because the static branch carries a large mean bias of **−0.312 g s⁻¹** that RMSE penalizes more heavily than MAE does. (These four values are computed on the 1 s decimated series used for the diagnostics, so they differ slightly from the full-resolution 0.648 and 0.573 in the ladder table; the ordering reversal is present at both resolutions.) No conclusion in this paper rests on that pair, but it demonstrates that a single scalar is not complete evidence of relative adequacy. We therefore report RMSE, MAE, mean bias and the standardized residual scale for every branch.

The temporal-versus-constant ordering persists in all three scoring windows. The strict ordering between $\Phi(t)$ and the cubic does not. Across 4, 8, 16, and 24 s blocks, the $\Phi(t)$-versus-constant interval excludes zero at every block duration. The $\Phi(t)$-versus-cubic interval is unresolved from 4 to 16 s; at 24 s it marginally favors the cubic, with an interval of approximately +0.001 to +0.04 g s⁻¹ for $\Phi(t)$ minus cubic. Coarser dependence treatment therefore weakens, rather than strengthens, a mechanistic reading of the fit.

### 5.2b Residual power is concentrated at low frequencies on the analysis window

Lag-1 autocorrelation says residuals are dependent; it does not say what the dependence *is*. A
slowly drifting residual and a residual oscillating near the sampling rate can carry similar lag-1
values while meaning very different things about model adequacy. We therefore report the
autocorrelation across lags and the periodogram of each branch's residual, on the same 1 s series
used for the scalar diagnostics.

The answer is the same for all four branches: **more than 95 % of residual power sits in the
lowest-frequency quarter of the available bins** (0.957 for the best constant and the static
branch, 0.990 for empirical $\Phi(t)$, 0.954 for the cubic). Residual power is therefore
concentrated at low frequencies on this preprocessed 80 s window. That is consistent with the
Durbin–Watson statistics sitting near zero rather than near two, and with lag-1 autocorrelation near
0.95 coexisting with temporal-branch RMSEs inside across-shot variability: the branches capture the
level and the overall rise, and leave behind coherent long-timescale structure.

**We do not convert this into a physical periodicity, and the earlier version of this section
did.** The diagnostic runs on an 80-point, 1 s-decimated series, so 80 s and 40 s are simply the
first and second nonzero Fourier periods available — they are properties of the window length, not
measured timescales. The source curve has already been differentiated, smoothed over about 3 s,
aligned, interpolated and averaged, which suppresses high-frequency variation before the transform
sees it; the transform itself is centred and untapered, which makes a nonstationary residual
especially sensitive to endpoints and trend leakage; and "slowest quarter" is a partition of the
available bins rather than a scientific cutoff. Accordingly we withdraw the previous claims that
the residual structure is "drift, not oscillation", that the branches have "dominant periods" of
80 s and 40 s, and that the remaining structure "is not a monotone trend that a further level or
slope term would absorb". None of the three is supported by this calculation.

What survives is the useful part: **every branch leaves coherent low-frequency lack of fit**, which
is a more informative statement than a low RMSE alone, and it bounds what any smooth same-trace fit
can be expected to fix. Establishing a physical timescale would require detrended and tapered
estimates, multiple windows and sampling resolutions, raw individual-shot spectra, and surrogate or
null simulations; none of those is run here.

**Figure 4 near here.** Panel a shows the autocorrelation across lags, panel b the share of power
in the lowest-frequency quarter of the available bins, and panel c the lowest-frequency bin at
which each branch peaks — labelled as a bin index rather than as a physical period. Figure 2c overlays
residual-versus-time for all branches on the pointwise between-shot band.

### 5.3 Cross-pressure assessment supports within-campaign temporal transfer but not a universal branch

Leaving out one equilibrium pressure changes either fitted equilibrium parameter by at most approximately 2.8%. The two-parameter equilibrium calibration is therefore not dominated by a single pressure point. Its equilibrium-curve LOPO predictive coefficient is approximately $Q^2=0.81$.

Table 3 separates three trace-level summaries that should not be conflated.

**Table 3. Mean trace RMSE across pressure conditions (g s⁻¹).**

| Assessment | Static branch | Empirical $\Phi(t)$ | RC-3b dynamic variant |
|---|---:|---:|---:|
| LOPO-EC (equilibrium calibration withheld), all 11 pressures | 0.534 | 0.347 | 0.516 |
| Shared calibration, all 11 pressures | 0.524 | 0.334 | 0.510 |
| Shared calibration, 10 off-9-bar pressures | 0.512 | 0.356 | 0.522 |

The LOPO means are within 0.013 g s⁻¹ of the corresponding shared-calibration means (largest absolute gap across the three branches). The empirical $\Phi(t)$ branch has the lowest mean error in both summaries. This is evidence that the aggregate 9-bar result is not created solely by one equilibrium pressure point.

The per-pressure view is less simple. Relative errors change continuously with pressure, and no branch is best at every pressure. A flow-coupled variant can improve at some low-pressure conditions; the static branch can be competitive at parts of the middle range; and all branches retain structured residuals. Because the 9-bar dissolved-mass trajectory and donor assumptions are held fixed during LOPO, the calculation is within-rig, within-campaign generalization conditional on those quantities. It does not establish transfer to another machine, coffee, grind, pressure node, or control mode.

**Figure 3 near here.**

### 5.4 Sign constraints narrow isolated branches without excluding coupled mechanisms

The transferred Mo swelling parameterization produces a monotone decline in fixed-pressure flow, reaching approximately 4% of its initial value over the simulated shot for the representative powder used in the repository calculation [3]. After allowing a free scale level, its reconstruction error is approximately 1.08 g s⁻¹ and its correlation with the measured rising trace is approximately −0.95. The structural result is the sign: within a fixed-height, fixed-pressure, swelling-to-Carman–Kozeny branch, increased particle volume raises resistance. The numerical magnitude is specific to the transferred powder and assumptions and is not offered as a coffee-independent prediction.

The Fasano fines-migration model supplies the same fixed-pressure sign from a different mechanism. Deposition and compact-layer growth make discharge monotone non-increasing under the Part I assumptions; pressure increase is one route by which removal or flux can restart in the broader family of models [4]. Thus an isolated fines-deposition branch cannot source the measured rise while pressure is held fixed.

These results rule out neither swelling nor fines migration as constituents of the real bed. They show only that, in the tested fixed-pressure isolation, those resistance-increasing branches cannot be the sole positive contribution. Dissolution-linked porosity opening does carry the required net sign for a rising fixed-pressure flow, and it is the scored temporal branch here. A second candidate — a decline in liquor viscosity as the dissolved-solids concentration falls over the shot — would carry the same sign, but it is *degenerate* with dissolution-linked opening: both are driven by the same falling-concentration clock, so the integrated forward trace cannot separate them, and distinguishing them requires an independent time-resolved concentration measurement. That viscosity analysis, and the flow-control dataset that motivates it, are reserved for the companion perturbation-program study (see the reserved-material note) and are not scored here. A coupled calculation in which swelling and extraction share porosity actually worsens the reconstruction; that negative composition result is analyzed as a software/evidence-governance demonstration in the companion Puckworks resource paper rather than used here as a headline physical claim.


### 5.3a Cross-pressure heterogeneity, and what the macro mean hides

The aggregate cross-pressure statement conceals three things a reader needs: which branch is best at
which pressure, how many shots each pressure contributes, and which pressure a stated number refers
to. All three are reported here.

**Table 3a. Per-pressure reconstruction error and shot count.** Error for each branch at every nominal pressure, with the number of shots contributing and the best branch, so an aggregate mean cannot hide the rank structure.

| nominal bar | shots | static κ(P) | empirical Φ(t) | RC-3b | best |
|---|---|---|---|---|---|
| 1.0 | 5 | 0.431 | 0.374 | 0.159 | rc3b |
| 2.0 | 4 | 0.649 | 0.573 | 0.303 | rc3b |
| 3.5 | 3 | 0.306 | 0.418 | 0.692 | static |
| 4.0 | 10 | 0.246 | 0.374 | 0.785 | static |
| 5.0 | 5 | 0.402 | 0.456 | 0.879 | static |
| 6.0 | 6 | 0.453 | 0.502 | 0.912 | static |
| 7.0 | 4 | 0.551 | 0.222 | 0.628 | phi |
| 8.0 | 4 | 0.575 | 0.118 | 0.448 | phi |
| 9.0 | 5 | 0.648 | 0.116 | 0.392 | phi |
| 11.0 | 4 | 0.693 | 0.173 | 0.241 | phi |
| 13.0 | 7 | 0.809 | 0.354 | 0.169 | rc3b |

**The best branch is not constant across pressure — it changes three times.** RC-3b is best at 1–2
bar, the static branch at 3.5–6 bar, Φ(t) at 7–11 bar, and RC-3b again at 13 bar. Φ(t) wins **4
of 11** pressures, and the band it wins is the 7–11 bar band that contains this paper's primary
9-bar analysis. The macro mean therefore reports a genuine aggregate advantage for Φ(t)
(0.334 g s⁻¹ against 0.524 for the static branch) while understating how strongly
that advantage is localised in pressure. The correct reading is the observed one, stated without threshold inference: among the eleven
tested nominal settings, $\Phi(t)$ has the lowest mean-curve RMSE at **7, 8, 9 and 11 bar**, RC-3b
at **1, 2 and 13 bar**, and the static branch at **3.5, 4, 5 and 6 bar**. We do not describe these
as regimes or infer a boundary near 7 bar: the bins were not prespecified, and an untested pressure
just above or below 7 bar cannot be assigned to an inferred regime without a prespecified model,
uncertainty and denser pressure sampling. Nothing in this campaign supports a pressure-independent
claim, and the aggregate $\Phi(t)$ advantage is itself conditional on importing one fixed 9-bar
dissolved-mass trajectory across all pressures — a within-campaign reconstruction exercise, not
evidence of a pressure-transfer law.

**The averaging scheme is a choice, and it changes the ordering.** The campaign contributes between
3 and 10 shots per pressure. Weighting every reference pressure equally — the scheme used
above — gives the order phi < rc3b < static. Weighting by the number of shots, which answers the different
question of what happens to a randomly drawn shot, gives phi < static < rc3b: the second and third places
exchange. Φ(t) is first under both. We report both rather than presenting either as neutral.

### 5.3b Pressure domains and boundary nodes

Four distinct pressure quantities appear in this paper and are easy to conflate.

- **Nominal reference pressure** — the campaign's setting, spanning 1–13 bar. Every
  "9 bar" statement in this paper is nominal.
- **Recorded basket pressure** — what the rig delivered, which is systematically **below** nominal at
  every setting, by up to 0.61 bar. The nominal 9 bar condition delivered a mean
  **8.71 bar** at the basket. §5.2 shows the ladder is insensitive to substituting the recorded
  history, but the two are different quantities and are named separately.
- **Fitted equilibrium characteristic pressure** — P_c = **12.39 bar**, an estimated parameter of
  the equilibrium closure, not a rig setting. It sits just inside the tested range, so only
  **1 of 11** reference pressures reach or exceed it: the saturating branch of the
  equilibrium curve is exercised by essentially one pressure, and the rest of the campaign probes
  the sub-characteristic regime.
- **Model-valid pressure range** — the tested interval 1–13 bar. No claim here
  extends outside it.

### 5.3c Parameter provenance as a dependency graph

"No coefficient fitted to the scored trace" is a statement about parameter *count*, not about
*access*. A branch is only as held out as its most target-proximal input, so each branch's inputs
are enumerated and each is labelled by how it reaches the branch.

**Table 3b. Parameter provenance as an access hierarchy.** Every branch's inputs, the access level each carries, and the most target-proximal among them — a branch is only as held out as that input.

| branch | free params fitted to the scored trace | access levels among its inputs | most target-proximal | held out? |
|---|---|---|---|---|
| `rung1_const` | 1 | direct_target | direct_target | no |
| `rung1b_longrun_const` | 0 | same_shot | same_shot | no |
| `rung3_static` | 0 | same_campaign, literature | same_campaign | no |
| `rung4_phi_of_t` | 0 | indirect_target, same_campaign, literature | indirect_target | no |
| `flexible_cubic` | 4 | direct_target | direct_target | no |
| `penalized_spline_loso` | 0 | other_shots, fixed architecture | other_shots | yes |

The consequence is visible in the table: the empirical Φ(t) branch has **zero** free parameters
fitted to the scored trace and is nevertheless **not** held out, because its dissolved-mass sigmoid
is derived from TDS(t) × Q(t) on this rig and Q(t) is the scored observable. Only the penalized
spline of §4.2b is held out, and it is a null. Reporting the parameter count alone would have made
Φ(t) and the spline look equivalent; they are not.

## 6. From curve fitting to discriminating experiments

The remaining mechanisms are distinguished more effectively by interventions than by additional smooth fits to the same forward trace. Table 4 states directional predictions. These are proposed experiments; the repository contains no data from these protocols.

**Table 4. Mechanism-by-perturbation prediction matrix. Predictions are qualitative and conditional on the cited model structures.**

| Candidate contribution | Fixed-pressure forward trace | Pressure step upward | Flow reversal at matched $\lvert\Delta P\rvert$ | Rebrew of spent puck | Depth-resolved end state |
|---|---|---|---|---|---|
| Machine/headspace response | Can generate dip/recovery without bed evolution | Immediate response governed by pump/headspace; repeatable with inert load | Changes with plumbing orientation only if apparatus does | Repeats if boundary and hydraulic load repeat | No bed-state signature |
| Dissolution-linked opening | Rising contribution as cumulative mass is removed | Static hydraulic jump; no matrix-specific restart beyond continuing extraction | Mass loss is direction-independent; no deposited layer to remobilize | Near-flat relative to first-shot endpoint once extractable inventory is depleted | Comparatively distributed porosity opening, subject to local extraction gradients |
| Fines migration and deposition | Resistance increases at fixed pressure | Rising pressure can remobilize or restart transport; compact layer can persist | Direction-asymmetric because the former outlet deposit becomes an upstream structure | Partial reopening and re-clogging may occur under a new cycle | Outlet-side accumulation or compact layer |
| Compaction and elastic recovery | Resistance increase or relaxation depends on stress history | Step can produce transient strain/recovery beyond the static jump | More direction-symmetric than a deposited compact layer | Unloading/reloading may reveal recovery and hysteresis | Strain-dependent profile, not necessarily outlet-localized |
| Particle swelling | Resistance increases in the fixed-height branch | Pressure step changes hydraulic load but water-uptake state evolves on its own timescale | Local swelling is approximately direction-independent | State may persist or relax slowly; no fresh dissolution required | Profile follows water exposure and mechanical constraint rather than a necessary outlet deposit |

### 6.1 Pressure-step experiment

A shot is first held at constant basket pressure through the temporal rise, then subjected to a controlled step to a higher pressure while flow and all pressure nodes are recorded. The static poroelastic relation predicts the immediate hydraulic jump. A dissolution-linked trajectory continues according to dissolved mass and does not predict a distinct pressure-triggered restart. In the Fasano framework, renewed removal or a porosity-coupled response under rising pressure can create additional transient change beyond the static jump [4]. The primary contrast is therefore not the jump itself but the post-step relaxation relative to a precomputed static baseline.

The protocol requires independent measurement of pump outlet, headspace or group pressure where applicable, basket pressure, and preferably bed pressure drop. Without node identity, a machine transient can be misclassified as a bed restart.

### 6.2 Flow-reversal replay

After a forward extraction segment, flow direction is reversed while maintaining the magnitude of the pressure drop. A downstream fines deposit is geometrically asymmetric: reversal changes the deposit’s relation to the inlet and can remobilize it. A local compaction or swelling field is more nearly direction-symmetric. Comparing normalized forward and reverse decay shapes therefore targets spatial organization that an integrated forward trace cannot see.

### 6.3 Spent-puck rebrew

A completed puck is subjected to a second hydraulic cycle without replacing the coffee. If the first rise mainly reflected irreversible removal of soluble mass, a largely depleted puck should show little additional opening and should begin near its prior hydraulic endpoint, after accounting for unloading and resaturation. A stress- or matrix-controlled mechanism can respond to the renewed pressure cycle even without fresh soluble inventory. The rebrew should include a no-rest interval and a controlled-rest interval to separate immediate hydraulic replay from slow elastic or swelling recovery.

### 6.4 Depth-resolved end state

Sacrificial sectioning, X-ray imaging, magnetic resonance, tracer deposition, or another validated spatial method can measure porosity, density, water content, or fines distribution versus depth. Outlet-localized fines accumulation supports a migration/deposition contribution. A more distributed change is more compatible with bulk dissolution or swelling, although the expected profile depends on local flow and extraction. This measurement is complementary to the dynamic interventions because a final profile can distinguish histories that produce similar outlet curves; models of uneven extraction illustrate why an integrated outlet signal may conceal those spatial differences [7].

### 6.5 First-drop timing and control mode

First-drop time constrains infiltration and dead volume, helping separate pre-saturation machine/wetting dynamics from the saturated interval analyzed here. Repeating a matched preparation under pressure control and flow control adds another intervention: a resistance increase produces falling flow under fixed pressure but rising pressure under fixed flow. The modes must be implemented with a physically consistent machine model; otherwise a nominal “control mode” label can hide different boundary conditions.

### 6.6 Decision logic

A flat spent-puck rebrew combined with no outlet-side fines gradient would strengthen a dissolution-opening interpretation. Reversal asymmetry or an outlet deposit would establish a fines-migration contribution even if that contribution did not dominate the original flow derivative. A post-step transient beyond the machine and static hydraulic response would motivate a quantitative porosity–stress closure. Null outcomes are informative: they should preserve the simple temporal model rather than motivate an unconstrained increase in model complexity.

## 7. Discussion

### 7.1 What the 9-bar trace supports

The preprocessed across-shot mean 9-bar flow trajectory shows a large reconstruction-error separation from the tested static descriptions on the 15–95 s interval. The best constant, a physically chosen late constant, and a nonlinear equilibrium pressure–flow model all leave substantially larger reconstruction error than a time-varying trajectory. That direction survives alternate windows and block durations. It is therefore reasonable to state that temporal flexibility is required relative to those nulls.

The conclusion is model-relative. “Temporal dynamics are required” does not mean that every possible static spatial model has been excluded, that the boundary pressure is perfectly constant at every relevant node, or that one bed state variable has been observed directly. It means that, among the tested models operating on the declared observable and interval, time-invariant predictions are inadequate.

### 7.2 What the trace does not identify

The flexible cubic reconstructs at least as well as the dissolution-linked trajectory, and both retain highly autocorrelated residuals. A single smooth curve therefore admits multiple effective state histories. The held-out comparator sharpens this: a fixed-architecture penalized spline trained on other brews, and fully held out, predicts a held-out brew as well as the partly target-informed mechanistic trajectory does. The trajectory's reconstruction quality is therefore attributable to the repeatable common shape of a brew on this rig rather than to the specific poroelastic–dissolution closure. An earlier version of this paragraph added that the trajectory beats the spline at filling an unobserved time interval and read that as shape information a local smoother lacks; that result does not survive comparator or gap sensitivity and has been withdrawn. The empirical porosity trajectory is scientifically interesting because it imports rather than refits its time dependence, but its dissolved-mass input is derived from measurements in the same campaign. This soft circularity prevents a strong causal interpretation.

Sign tests add information that RMSE cannot. Under fixed-pressure isolation, swelling and fines deposition move flow in the wrong direction to be the sole source of the rise. Yet sign does not imply absence. In a coupled system, the measured derivative is a sum of contributions, some positive and some negative. A resistance-increasing process can be present while a stronger opening process controls the net sign. This distinction matters because categorical language such as “swelling is refuted” would exceed the analysis.

### 7.3 Why held-out pressure helps but does not close identification

LOPO assessment shows that the equilibrium calibration is stable and that the empirical temporal branch retains the lowest mean error when each pressure point is excluded from its own equilibrium fit. This is stronger than scoring only the calibration trace. It remains weaker than external validation because the same rig, preparation, pressure campaign, 9-bar dissolved-mass trajectory, and donor assumptions are reused. The pressure-dependent residual fingerprints may reflect omitted bed physics, machine dynamics, viscosity, pressure-node mismatch, sensor behavior, or imperfection in the equilibrium functional form. Their origin remains unresolved.

A high-value next dataset would repeat the pressure matrix on a second coffee and rig while independently measuring a bed state such as thickness, strain, porosity, or soluble mass. Such a design would test both transportability and state interpretation rather than only curve reconstruction.

### 7.4 Null-first inference as a general porous-media practice

The method is not specific to espresso. Integrated outlet signals in filtration, reactive porous media, packed beds, swelling polymers, and biological tissues often combine boundary dynamics with evolving internal resistance. A useful sequence is:

1. identify the observable and boundary node precisely;
2. test a machine or boundary-condition null;
3. test the strongest static material null;
4. introduce a mechanistic temporal candidate with explicit parameter provenance;
5. compare it with a flexible empirical temporal null;
6. evaluate held-out conditions where possible;
7. apply sign and conservation constraints; and
8. design an intervention that makes surviving mechanisms disagree.

The sequence prevents a mechanism from receiving evidentiary credit merely because it is the first model with enough flexibility to follow the trace.

## 8. Limitations

The analysis has six main limitations.

First, the machine-only capacity test and the rising-flow measurement come from different source systems. This is deliberate for the logical point that machines can generate similar shapes, but it is not a calibrated machine explanation of the Waszkiewicz trace.

Second, although the primary uncertainty statement is now at the shot level, it rests on **five** brews from one campaign at one pressure. Five paired units cannot reach a conventional significance threshold under an exact randomization test, and a percentile bootstrap over five units is indicative at best; the comparisons reported here are effect sizes and directional counts, read alongside descriptive dispersion scales that are explicitly not floors or thresholds, rather than tests. The cross-pressure and window analyses use one preprocessed across-shot mean 9-bar trajectory from one campaign. Window and block sensitivity address analysis choices, not shot-to-shot, coffee-lot, preparation, operator, grinder, or apparatus replication.

Third, the empirical $\Phi(t)$ trajectory is soft-circular because dissolved mass is constructed from total dissolved solids and flow measured on the same rig. An independently measured mass-loss or porosity trajectory is needed to convert reconstruction into a stronger mechanistic test.

Fourth, the moving-block intervals condition on fixed prediction and loss sequences. They do not propagate uncertainty from parameter estimation, digitization, preprocessing, model selection, or refitting. A full nested block bootstrap or state-space likelihood would be a methodological extension, though neither would by itself solve mechanism non-uniqueness.

Fifth, the sign tests apply to isolated branches under fixed pressure and their stated assumptions. They do not represent all possible swelling, compaction, or fines models, and the transferred swelling magnitude is not universal.

Sixth, several plausible processes remain outside the quantitative ladder, including unsaturated wetting, gas release, viscosity changes with concentration and temperature, erosion, lateral heterogeneity, outlet-screen resistance, and a parameterized version of the Fasano Part II porosity law. The absence of a branch from the ladder is not evidence against that process.

## 9. Conclusions

A flow curve can reject specified time-invariant descriptions without identifying a physical mechanism. In the cases examined here, a pump–headspace–infiltration model can generate a dip-and-recovery shape without bed evolution, while the preprocessed nominal 9-bar rising-flow trajectory is reconstructed much better by time-varying branches than by the tested constant and static pressure-dependent branches. The same trajectory is reconstructed at least as well by a same-trace cubic, and a fully held-out empirical template learned from other brews predicts a new brew as well as the partly target-informed dissolution-linked trajectory. Fit quality therefore supports time variation relative to the tested nulls, but not the named closure.

The claim is deliberately model-relative: **time-varying predictions are required to reconstruct this preprocessed mean trajectory relative to the tested time-invariant branches.** The tested static branches are time-invariant levels at fixed pressure; they do not exhaust static spatial heterogeneity, changing boundary conditions at unmeasured nodes, preprocessing artefacts, or latent machine states, so no internal material state has been observed.

Withholding each equilibrium pressure point in turn produces only modest calibration drift and preserves the aggregate within-campaign ordering, but that calculation retains the common temporal inputs and is not external temporal validation. Branch rankings vary across the tested nominal pressures, and every branch leaves coherent low-frequency residual structure. Conditional sign tests constrain isolated resistance-increasing swelling and fines-deposition branches without excluding them from a coupled bed. Mechanism identification now requires intervention — especially pressure steps, flow reversal, spent-puck rebrewing, and spatial end-state measurements — that forces the surviving explanations to make different predictions. For this inverse problem, a well-chosen perturbation is more informative than another flexible fit to the same curve.

## Data and code availability

The analysis is implemented in the Puckworks repository: <https://github.com/trbrewer/puckworks>. Source cards, data-manifest entries, model components, and analysis functions provide the provenance chain for each result. Before submission, the authors should cite a frozen software release and archive DOI, report the exact source commit, include figure source-data files, and verify that the release manifest records a clean tree, matching bundle commit, strict numerical verification, and artifact hashes.

The Waszkiewicz data are documented in the repository manifest with the source repository and Zenodo record cited there. Access and redistribution remain governed by the licenses of the source datasets. The Foster curve used for the machine-null panel is a published model output reconstructed from the source equations, not redistributed experimental data.

## Author contributions

[To be completed using the target journal’s contribution taxonomy.]

## Funding

[To be completed.]

## Competing interests

[To be completed.]

## Acknowledgments

[To be completed.]

## Figures

All five figures are generated by `python -m puckworks.figures_paper_b2` from
`docs/figures/paper_b_results.json` — the same bundle `paper_b.build.verify` checks every registered claim
against, so a figure cannot disagree with a verified number. Raster and vector are emitted together,
each data-bearing figure exports a tidy source-data CSV so a reviewer can re-plot without the solver
stack, and every figure carries a text alternative in `docs/figures/paper_b2/ALT_TEXT.md`.

**Figure 1. Machine-side non-uniqueness of a flow minimum.** (a) The Foster machine path with its
pressure nodes labelled: a "9 bar" statement must name which node it means. (b) The published Fig-15
normalised flow series against the repository reconstruction, which reaches its minimum of 0.181 at
1.99 s with no evolving bed mechanism; the reconstruction is drawn only over the interval the model
covers. (c) The measured 9-bar trace on its own axes, included to establish that it is a separate
evidence object the Foster parameterisation does not fit.

**Figure 2. Null-first temporal ladder on the 9-bar trace.** (a) Measured flow with every branch
overlaid on the 15–95 s window. (b) Reconstruction error by branch, annotated with how many free
parameters each fitted to the scored trace; the cubic is labelled a same-trace descriptive comparator,
not a predictive model. (c) Residual against time at the declared 1 s resolution, over the mean
pointwise between-shot band. (d) Conditional moving-block intervals: Φ(t) minus the best constant
excludes zero, Φ(t) minus the cubic does not.

**Figure 3. Cross-pressure assessment.** (a) Per-pressure error for the static, Φ(t) and RC-3b
branches; the best branch changes three times, and the band containing the primary 9-bar analysis is
marked. (b) LOPO-EC mean trace errors against shared calibration — only the equilibrium calibration point is withheld, not the temporal inputs. (c) Equilibrium
calibration drift, plotted relative to the all-pressure fit against the stated ±2.8 % bound.
(d) Nominal setting against recorded basket pressure, which is below nominal at every condition. The
assessment is within-rig and conditional on the fixed dissolved-mass trajectory.

**Figure 4. Residual structure is slow drift.** (a) Autocorrelation across twenty lags. (b) Share of
residual power in the slowest spectral quarter, above 0.95 for every branch. (c) Dominant residual
period: 80 s for the static branches, 40 s for both temporal branches. The best constant and static
κ(P) curves coincide exactly in (a) and (b) because both leave a constant-offset residual, so every
centred diagnostic is identical by construction.

**Figure 5. Mechanism-by-perturbation prediction matrix.** Five candidate contributions against five
perturbations. Every cell is a **declared** qualitative expectation conditional on the cited model
structure; the repository contains no data from any of these protocols, so no cell is a result. Flow
reversal is highlighted as the one column where the candidates differ in sign rather than degree.

## Supplementary material plan

- **Supplement S1:** Source-object inventory, dataset licenses, pressure-node definitions, and preprocessing details.
- **Supplement S2:** Full parameter-provenance table, including numerical values and uncertainty where reported by source papers.
- **Supplement S3:** Residual plots and autocorrelation functions for every 9-bar branch.
- **Supplement S4:** Scoring-window sensitivity for 10–90, 15–95, and 20–90 s.
- **Supplement S5:** Moving-block sensitivity for 4, 8, 16, and 24 s blocks, including the exact fixed-loss resampling algorithm.
- **Supplement S6:** Per-pressure shared and LOPO errors at full precision; equilibrium-curve LOPO calculation and $Q^2$.
- **Supplement S7:** Swelling transfer calculation, analytic fines sign constraint, and assumptions under which each sign holds.
- **Supplement S8:** Detailed pressure-step, reversal, rebrew, first-drop, and spatial-measurement protocols.
- **Supplement S9:** Alternative temporal closures and a formal parameter/observable table for future observability analysis.

## References

1. Foster J, Lee W, Moroney K, Prjamkov D, Salamon M, Smith A, Petrassem-de-Sousa J, Vynnycky M. Dynamics of liquid infiltration into an espresso bed using time-resolved micro-computed tomography: insights from experiment and modeling. *Physics of Fluids*. 2025;37:013383. doi:10.1063/5.0245167.
2. Waszkiewicz P, Myck M, Białas K, Puciata-Mroczynska A, Dzikowski M, Szymczak P, Lisicki M. Under pressure: poroelastic regulation of flow in espresso brewing. *Physics of Fluids*. 2026;38:063113. doi:10.1063/5.0319611. Associated data/code record documented in the Puckworks data manifest.
3. Mo J, Navarini L, Suggi Liverani F, Ellero M. Modelling swelling effects in real espresso extraction using a 1-dimensional coarse-grained model. *Journal of Food Engineering*. 2024;365:111843. doi:10.1016/j.jfoodeng.2023.111843.
4. Fasano A, Talamucci F, Petracco M. The espresso coffee problem. In: Fasano A, editor. *Complex Flows in Industrial Processes*. Boston: Birkhäuser/Springer; 2000. p. 241–280.
5. Cameron MI, Morisco D, Hofstetter D, Uman E, Wilkinson J, Kennedy Z, Fontenot H, Lee TC, Hendon CH, Foster JM. Systematically improving espresso: insights from mathematical modeling and experiment. *Matter*. 2020;2:631–648. doi:10.1016/j.matt.2019.12.019.
6. Künsch HR. The jackknife and the bootstrap for general stationary observations. *The Annals of Statistics*. 1989;17(3):1217–1241. doi:10.1214/aos/1176347265.
7. Lee WT, Smith A, Arshad M. Uneven extraction in coffee brewing. *Physics of Fluids*. 2023;35:054110. doi:10.1063/5.0138998.

## Repository provenance used to develop this draft

The manuscript was recut from the following current-repository artifacts: `PAPER_B2_TEMPORAL_OUTLINE.md`; `PAPER_B_DRAFT.md` Result 2; `CLAIM_OWNERSHIP.md`; `PROTOCOL_kappa_t_discrimination.md`; the Foster, Waszkiewicz, Mo, Fasano, and Cameron model cards; the temporal-ladder, residual-diagnostic, cross-pressure, and LOPO analysis functions; and the data manifest. Internal function names are recorded here for drafting provenance and should move to a reproducibility supplement or archived workflow citation in the submitted manuscript.

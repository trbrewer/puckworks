# One flow curve, many causes: null-first inference for machine and porous-bed dynamics in espresso

**Working manuscript draft — 15 July 2026**  
**Authors:** [Author names and affiliations to be inserted]  
**Corresponding author:** [Name and email to be inserted]

> **Draft status.** This manuscript was developed from `PAPER_B2_TEMPORAL_OUTLINE.md`, the retained synthesis in `PAPER_B_DRAFT.md`, the model/source cards, and the generated analyses in the Puckworks repository. The numerical values below reproduce the current repository evidence record; they should be regenerated from, and cited to, a clean versioned release before submission. Figures are specified as publication-ready panels and captions but are not embedded in this Markdown draft. This is not a claim that the repository corpus or the present analyses are complete.

## Abstract

Time-resolved espresso flow curves are often interpreted as direct signatures of swelling, compaction, fines migration, dissolution, or channel formation in the porous coffee bed. That interpretation is an inverse problem: the measured outlet flow integrates machine response, pressure boundary conditions, wetting, evolving bed resistance, and measurement effects, so visually similar traces can arise from different causes. We use a null-first comparison to ask two narrower questions: whether a measured trace requires temporal flexibility relative to specified static baselines, and whether that requirement identifies a bed mechanism. First, a published pump–headspace–infiltration model reconstructs a mid-shot flow minimum without any evolving bed process, showing that dip-and-recovery shape alone is not diagnostic. Second, on the saturated 15–95 s interval of a measured 9-bar rising-flow trace, the best constant baseline has root-mean-square error (RMSE) 0.573 g s⁻¹ and a static pressure-dependent poroelastic model has RMSE 0.648 g s⁻¹. A dissolution-linked time-varying porosity trajectory, with no coefficients fitted to that flow trace, reaches 0.116 g s⁻¹. A four-parameter cubic fitted and scored on the same trace reaches 0.096 g s⁻¹. Moving-block intervals on the fixed squared-error sequences support the improvement of the temporal trajectory over the constant baseline (median ΔRMSE approximately −0.39 g s⁻¹; 95% interval −0.60 to −0.23) but do not resolve its difference from the flexible cubic (approximately +0.02 g s⁻¹; −0.01 to +0.05). Leave-one-pressure-out assessment across eleven pressures preserves the aggregate advantage of the empirical temporal branch within the same rig and campaign, while structured residuals and pressure-dependent rank changes show substantial omitted dynamics. Conditional sign tests further show that isolated swelling and fines-deposition branches increase resistance at fixed pressure and therefore cannot, by themselves, generate the observed rising contribution; this does not exclude their presence in a coupled bed. We conclude that the integrated flow trace establishes a need for temporal dynamics relative to the tested static nulls, but does not identify the responsible mechanism. Pressure steps, flow reversal, spent-puck rebrewing, and depth-resolved end states offer more discriminating evidence than another unconstrained fit to the same curve.

**Keywords:** espresso; porous media; systems identification; model comparison; temporal dynamics; permeability; poroelasticity; block resampling; experiment design

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

Waszkiewicz et al. reported a campaign of 60 brews at eleven basket pressures spanning approximately 1 to 12.5 bar on one machine, coffee, grind, dose, and preparation protocol [2]. The dose was approximately 18.5 g in a 58 mm basket. Long-run flow for the equilibrium pressure–flow relation was summarized over 110–120 s. Time-dependent flow and total-dissolved-solids measurements were also reported. The source model explicitly excludes the first approximately 5–10 s, when wetting, air expulsion, and other unsaturated processes dominate. Our primary temporal analysis therefore uses the saturated interval from 15 to 95 s. Sensitivity analyses use 10–90 s and 20–90 s.

Pressure is treated as basket gauge pressure where the source dataset identifies that node. Flow is reported as mass flow in g s⁻¹. Time is measured from the source trace origin. The repository adapters align all candidate predictions to the same observed time points and apply one common scoring mask per comparison. No model is rewarded by using a different evaluation interval.

### 2.4 Primary observable and estimand

Let the measured flow at time $t_i$ be $Q_i$ and the prediction from branch $m$ be $\widehat{Q}_{m,i}$. The primary score is

$$
\operatorname{RMSE}_m =
\left[\frac{1}{n}\sum_{i=1}^{n}
\left(Q_i-\widehat{Q}_{m,i}\right)^2\right]^{1/2}.
$$

The estimand is reconstruction error on a declared time interval. For the cubic branch and the best constant, this is in-sample error because those coefficients are fitted on the same trace. For the empirical porosity branch, the 9-bar flow trace supplies no newly fitted flow coefficient, but the branch imports an equilibrium calibration and a dissolved-mass trajectory from the same campaign. It is therefore a transferred within-campaign reconstruction, not an independent prediction.

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

is fitted and scored on the same interval. It has no bed-mechanism interpretation. Its purpose is to bound what smooth temporal flexibility can achieve with four free coefficients. It is not a fair predictive challenger to the imported porosity branch; it is an in-sample flexibility floor. If the mechanistic trajectory does not clearly improve on this floor, the trace fit cannot be used to identify that mechanism.

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
| Flexible cubic | 4 | 0 | polynomial form | non-mechanistic flexibility bound |

This provenance prevents two common misreadings. First, the empirical $\Phi(t)$ result is not “parameter-free”: it imports estimated quantities. Second, the cubic’s lower RMSE is not evidence of better prediction because the same trace both fits and scores it.

## 4. Statistical and diagnostic analysis

### 4.1 Residual structure

For each branch, residuals are

$$
e_{m,i}=Q_i-\widehat Q_{m,i}.
$$

We report residual-versus-time curves, lag autocorrelation, and Durbin–Watson summaries on a trace decimated to 1 s for the cross-pressure diagnostic. Decimation prevents the approximately 10 Hz sampling interval from dominating the serial-correlation statistic. Strong positive correlation indicates coherent unmodeled structure and invalidates an interpretation of pointwise residuals as independent noise.

### 4.2 Conditional moving-block intervals

To compare two fixed predictions $A$ and $B$, define the pointwise squared-error difference

$$
d_i=(Q_i-\widehat Q_{A,i})^2-(Q_i-\widehat Q_{B,i})^2.
$$

Contiguous blocks of the $d_i$ sequence are sampled with replacement to form resampled loss sequences, following the general moving-block principle for dependent observations [6]. RMSE differences are recomputed from those resampled losses. The primary block duration is 8 s with 1,000 resamples; sensitivity uses 4, 8, 16, and 24 s blocks.

This procedure preserves local dependence in the already-computed loss sequences, but it does not refit the constant, cubic, equilibrium calibration, or temporal trajectory inside each resample. The resulting interval is therefore conditional on the fixed predictions. It is not a bootstrap confidence interval for the full fit–compare procedure, and it is not a test of model truth. We report whether an interval resolves the sign of the reconstruction difference rather than labeling unresolved differences “equivalent” or “statistically indistinguishable.”

### 4.3 Window sensitivity

The full ladder is repeated for 10–90 s, 15–95 s, and 20–90 s. The primary 15–95 s interval balances exclusion of the unsaturated startup with retention of the rising phase. A conclusion is described as window-robust only if its direction persists across all three intervals.

### 4.4 Shared and leave-one-pressure-out assessment

The equilibrium calibration uses eleven long-run pressure–flow points. Two forms of multi-pressure assessment are kept separate.

**Shared calibration.** One pair $(P_c,Q_c)$ is fitted using all eleven long-run points and then used to reconstruct all time traces.

**Leave one pressure out (LOPO).** For each pressure $P_j$, $(P_c,Q_c)$ is refitted using the other ten equilibrium points. The held-out pair is then used to reconstruct the trace at $P_j$. The 9-bar dissolved-mass trajectory and donor assumptions are held fixed; only the two equilibrium parameters are refitted. Thus, LOPO prevents the held-out pressure’s equilibrium point from contributing to its own equilibrium calibration, but it is not a fully independent test of the temporal trajectory.

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
| Empirical $\Phi(t)$ | 0.116 | temporal candidate; no coefficients fitted to this flow trace |
| Flexible cubic | 0.096 | four-parameter in-sample flexibility bound |

All three constant or static baselines leave errors between 0.57 and 0.65 g s⁻¹. The empirical temporal trajectory reduces RMSE to 0.116 g s⁻¹, approximately 4.9 times lower than the best constant and 5.6 times lower than the static pressure-dependent branch. Within the tested model set and interval, a static level is therefore inadequate.

The four-parameter cubic reaches 0.096 g s⁻¹. Its fit is at least as close as the mechanistic trajectory, so the reconstruction does not identify the poroelastic–dissolution closure. Instead, the non-trivial result is that an externally parameterized temporal trajectory nearly reaches an in-sample flexible floor without fitting an additional coefficient to the scored flow trace.

Residuals remain strongly structured. Lag-1 residual autocorrelation is approximately 0.99 in every branch, and the mean decimated Durbin–Watson statistic is approximately 0.01. The low RMSE of the temporal branches therefore coexists with coherent lack of fit. Neither branch reduces the residual to white measurement noise.

**Figure 2 near here.**

The conditional moving-block analysis supports the same two-part conclusion. For empirical $\Phi(t)$ minus the best constant, the median RMSE difference is approximately −0.39 g s⁻¹ with a 95% interval of −0.60 to −0.23 g s⁻¹. The interval excludes zero, supporting the need for temporal flexibility relative to the constant null. For empirical $\Phi(t)$ minus the cubic, the difference is approximately +0.02 g s⁻¹ with a 95% interval of −0.01 to +0.05 g s⁻¹. This interval does not resolve which branch reconstructs better.

The temporal-versus-constant ordering persists in all three scoring windows. The strict ordering between $\Phi(t)$ and the cubic does not. Across 4, 8, 16, and 24 s blocks, the $\Phi(t)$-versus-constant interval excludes zero at every block duration. The $\Phi(t)$-versus-cubic interval is unresolved from 4 to 16 s; at 24 s it marginally favors the cubic, with an interval of approximately +0.001 to +0.04 g s⁻¹ for $\Phi(t)$ minus cubic. Coarser dependence treatment therefore weakens, rather than strengthens, a mechanistic reading of the fit.

### 5.3 Cross-pressure assessment supports within-campaign temporal transfer but not a universal branch

Leaving out one equilibrium pressure changes either fitted equilibrium parameter by at most approximately 2.8%. The two-parameter equilibrium calibration is therefore not dominated by a single pressure point. Its equilibrium-curve LOPO predictive coefficient is approximately $Q^2=0.81$.

Table 3 separates three trace-level summaries that should not be conflated.

**Table 3. Mean trace RMSE across pressure conditions (g s⁻¹).**

| Assessment | Static branch | Empirical $\Phi(t)$ | RC-3b dynamic variant |
|---|---:|---:|---:|
| LOPO held out, all 11 pressures | 0.534 | 0.347 | 0.525 |
| Shared calibration, all 11 pressures | 0.524 | 0.334 | 0.519 |
| Shared calibration, 10 off-9-bar pressures | 0.512 | 0.356 | 0.530 |

The LOPO means are within approximately 0.01–0.02 g s⁻¹ of the corresponding shared-calibration means. The empirical $\Phi(t)$ branch has the lowest mean error in both summaries. This is evidence that the aggregate 9-bar result is not created solely by one equilibrium pressure point.

The per-pressure view is less simple. Relative errors change continuously with pressure, and no branch is best at every pressure. A flow-coupled variant can improve at some low-pressure conditions; the static branch can be competitive at parts of the middle range; and all branches retain structured residuals. Because the 9-bar dissolved-mass trajectory and donor assumptions are held fixed during LOPO, the calculation is within-rig, within-campaign generalization conditional on those quantities. It does not establish transfer to another machine, coffee, grind, pressure node, or control mode.

**Figure 3 near here.**

### 5.4 Sign constraints narrow isolated branches without excluding coupled mechanisms

The transferred Mo swelling parameterization produces a monotone decline in fixed-pressure flow, reaching approximately 4% of its initial value over the simulated shot for the representative powder used in the repository calculation [3]. After allowing a free scale level, its reconstruction error is approximately 1.08 g s⁻¹ and its correlation with the measured rising trace is approximately −0.95. The structural result is the sign: within a fixed-height, fixed-pressure, swelling-to-Carman–Kozeny branch, increased particle volume raises resistance. The numerical magnitude is specific to the transferred powder and assumptions and is not offered as a coffee-independent prediction.

The Fasano fines-migration model supplies the same fixed-pressure sign from a different mechanism. Deposition and compact-layer growth make discharge monotone non-increasing under the Part I assumptions; pressure increase is one route by which removal or flux can restart in the broader family of models [4]. Thus an isolated fines-deposition branch cannot source the measured rise while pressure is held fixed.

These results rule out neither swelling nor fines migration as constituents of the real bed. They show only that, in the tested fixed-pressure isolation, those resistance-increasing branches cannot be the sole positive contribution. Dissolution-linked opening is the only implemented isolated branch in this comparison with the required net sign. A coupled calculation in which swelling and extraction share porosity actually worsens the reconstruction; that negative composition result is analyzed as a software/evidence-governance demonstration in the companion Puckworks resource paper rather than used here as a headline physical claim.

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

The measured 9-bar flow trace contains strong evidence against the tested static descriptions on the 15–95 s interval. The best constant, a physically chosen late constant, and a nonlinear equilibrium pressure–flow model all leave substantially larger reconstruction error than a time-varying trajectory. That direction survives alternate windows and block durations. It is therefore reasonable to state that temporal flexibility is required relative to those nulls.

The conclusion is model-relative. “Temporal dynamics are required” does not mean that every possible static spatial model has been excluded, that the boundary pressure is perfectly constant at every relevant node, or that one bed state variable has been observed directly. It means that, among the tested models operating on the declared observable and interval, time-invariant predictions are inadequate.

### 7.2 What the trace does not identify

The flexible cubic reconstructs at least as well as the dissolution-linked trajectory, and both retain highly autocorrelated residuals. A single smooth curve therefore admits multiple effective state histories. The empirical porosity trajectory is scientifically interesting because it imports rather than refits its time dependence, but its dissolved-mass input is derived from measurements in the same campaign. This soft circularity prevents a strong causal interpretation.

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

Second, the primary temporal comparison uses one 9-bar trace from one campaign. Window and block sensitivity address analysis choices, not biological or apparatus replication.

Third, the empirical $\Phi(t)$ trajectory is soft-circular because dissolved mass is constructed from total dissolved solids and flow measured on the same rig. An independently measured mass-loss or porosity trajectory is needed to convert reconstruction into a stronger mechanistic test.

Fourth, the moving-block intervals condition on fixed prediction and loss sequences. They do not propagate uncertainty from parameter estimation, digitization, preprocessing, model selection, or refitting. A full nested block bootstrap or state-space likelihood would be a methodological extension, though neither would by itself solve mechanism non-uniqueness.

Fifth, the sign tests apply to isolated branches under fixed pressure and their stated assumptions. They do not represent all possible swelling, compaction, or fines models, and the transferred swelling magnitude is not universal.

Sixth, several plausible processes remain outside the quantitative ladder, including unsaturated wetting, gas release, viscosity changes with concentration and temperature, erosion, lateral heterogeneity, outlet-screen resistance, and a parameterized version of the Fasano Part II porosity law. The absence of a branch from the ladder is not evidence against that process.

## 9. Conclusions

A flow curve can falsify a static null without identifying a mechanism. In the cases studied here, a pump–headspace–infiltration model generates a mid-shot flow minimum without bed evolution, and a measured 9-bar rising-flow trace is reconstructed far better by temporal models than by constant or static pressure-dependent baselines. The same trace is also reconstructed at least as well by a flexible cubic, and every tested branch leaves strongly structured residuals. The appropriate conclusion is therefore conditional: temporal dynamics are required relative to the tested static nulls, but the integrated trace does not uniquely identify the bed process.

Cross-pressure leave-one-pressure-out analysis strengthens the within-campaign robustness of the temporal result while preserving substantial pressure-dependent lack of fit. Fixed-pressure sign tests constrain isolated resistance-increasing swelling and fines-deposition branches, but do not exclude them from a coupled bed. The decisive next step is intervention: pressure steps, flow reversal, spent-puck rebrewing, and spatial end-state measurements turn mechanistic narratives into directional predictions. For this inverse problem, a well-chosen perturbation is more informative than another flexible fit to the same curve.

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

## Figure specifications and draft captions

### Figure 1. Machine-side non-uniqueness of a flow minimum

**Panel a:** Schematic of pump outlet, pipe resistance, trapped-air headspace, ponding height, wetting front, and porous bed in the Foster model. Pressure nodes are labeled explicitly. **Panel b:** Published Foster normalized flow curve and repository reconstruction, showing a mid-shot minimum and recovery with no evolving bed mechanism. **Panel c:** Measured Waszkiewicz 9-bar rising-flow trace, shown only to establish that it is a separate evidence object and not fitted by the Foster parameterization. Caption language: the Foster system demonstrates machine-side capacity for the shape; it does not explain the Waszkiewicz trace.

### Figure 2. Null-first temporal ladder on the 9-bar trace

**Panel a:** Measured flow with primary 15–95 s scoring window and predictions from the best constant, late-window constant, static $\kappa(P)$ model, empirical $\Phi(t)$ trajectory, and flexible cubic. **Panel b:** RMSE by branch with parameter-provenance labels. **Panel c:** Residual-versus-time curves. **Panel d:** Conditional moving-block intervals for $\Phi(t)$ minus best constant and $\Phi(t)$ minus cubic. The cubic is labeled “in-sample flexibility bound,” not “predictive model.”

### Figure 3. Cross-pressure assessment

**Panel a:** Shared-calibration prediction and observed trace at each pressure, faceted or arranged on a continuous pressure axis. **Panel b:** Per-pressure RMSE for static, empirical $\Phi(t)$, and RC-3b branches under shared calibration. **Panel c:** LOPO held-out RMSE with open markers; shared-calibration scores shown separately. **Panel d:** Calibration drift in $P_c$ and $Q_c$ when each pressure is omitted. **Panel e:** Decimated residual Durbin–Watson or another residual-structure summary. The caption states that the assessment is within-rig and conditional on the fixed 9-bar dissolved-mass trajectory and donor assumptions.

### Figure 4. Mechanism-by-perturbation program

A matrix with rows for machine/headspace, dissolution opening, fines migration, compaction/recovery, and swelling; columns for pressure step, flow reversal, spent-puck rebrew, control mode, first-drop timing, and depth-resolved end state. Each cell shows only a directional or hysteresis prediction supported by the corresponding model structure. A side panel gives the decision logic and identifies presently missing measurements.

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

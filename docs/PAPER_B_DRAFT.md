# Paper B — draft prose (rev. 2026-07-12, post detailed review)

*Manuscript draft. Two rounds of detailed review adopted; the corrections and their
evidence are logged in **ROADMAP §7.1** (2026-07-12) — see there rather than
restating them here. Verb discipline (load-bearing): "shows/predicts" only for
independent evidence; "reconstructs/is consistent with" for post-fit; "can generate
/ does not generate under the tested parameterization" for qualitative
discrimination; "exhibits in the tested configuration / motivates" for exploratory
synthesis; never "identifies / proves / is the mechanism / unconditionally /
linearly unstable". Figures: `docs/figures/fig{1..5}`. Validation-strength tags stay
in the text.*

**Title.** **Limits of mechanism discrimination from integrated espresso measurements:
matched observables, temporal nulls, and exploratory streamtube dynamics.**
*(Revised per the 3rd review, MAJ-02/B3-21: the paper establishes model capacity,
incompatibility, and a need for temporal flexibility while remaining insufficient to
identify a unique mechanism, so the title leads with the LIMITS of discrimination rather
than asserting it. A stability-focused title remains unavailable — no formal
Jacobian/eigenmode analysis exists.)*

---

## Abstract

Espresso measurements integrate extraction, flow, and bed evolution, allowing
distinct mechanisms to produce similar whole-cup or whole-bed signals. We use a
provenance-tracked model registry and matched-observable, null-first comparisons to
determine what two published datasets can discriminate within a specified model set.
First, we correct an earlier aggregation **in our own comparison pipeline** that
combined distinct milligram solute-mass and gram total-dissolved-solids observables
across brew ratios (the source study reports these as distinct observables; enforcing
a single matched observable is an often-implicit prerequisite, which we make
explicit). At the nominal central settings the TDS-derived extraction-yield cell
means are 18.27, 19.38, and 19.62 % at grinder dials 1.4, 1.7, and 2.0: the means are
**numerically ordered and the middle cell lies 0.24 EY-points below dial 2.0**
(Welch 95 % CI [−0.42, −0.06]), so these **source-derived run-level endpoint estimates**
(computed by the source from measured first fractions plus integration of fitted extraction
kinetics to the target beverage mass — not a directly measured whole-cup endpoint) do not
support an interior maximum at the middle dial in the three selected nominal settings (the
1.4-vs-1.7 interval includes zero, and achieved flow/pressure vary across these nominal
conditions). A calibrated lognormal static-heterogeneity
streamtube ensemble can generate a small interior maximum for some closure choices,
establishing **model capacity rather than identifying channeling** (the closure is
grind-calibrated; incomplete wetting is unmodeled). Second, on a 9-bar rising-flow
trace a machine-only model shows a dip-and-recovery shape is not diagnostic of bed
dynamics, and an empirical time-varying porosity trajectory improves reconstruction
relative to explicitly defined constant baselines — but a flexible non-mechanistic
temporal null does as well, so this establishes a **need for time variation, not a
specific bed mechanism**; the pressure-varying reconstruction error is described by a
continuous residual-vs-pressure curve within the same campaign (not independent
validation, and not pre-specified pressure "regimes"). Finally, an exploratory
uncoupled N-tube composition with extraction-dependent conductance can concentrate
flow strongly in the implemented near-choke, fixed-total-flow, zero-homogenization
configuration; the concentration is floor-independent under a completed numerical
floor sweep but remains regularization- and start-state-dependent and is **not a
stability theorem**. Across the datasets and model classes tested here, integrated
measurements do not uniquely identify a mechanism; spatial, pathway-resolved,
first-drip, or independently measured bed-state observables would be more
discriminating.

---

## 1. Introduction

Below a threshold grind, espresso extraction can stop rising with fineness even
though specific surface area keeps increasing, whereas the homogeneous-flow
extraction models in the lineage we examine (Moroney/Cameron-type Darcy–extraction
models, under the espresso conditions studied here) predict a monotone rise. The
effect is usually attributed to one of a small set of
mechanisms, but the mechanisms have not been run head-to-head against the same
matched observable, and the effect is weak enough that a mechanism can appear to
"reproduce" it for reasons that do not survive scrutiny.

Three *different* objects have been conflated in prior discussion; we keep them
distinct throughout.

| Object | Observable | Dataset | Role here |
|---|---|---|---|
| Cameron fine-grind deviation | EY residual from a homogeneous model vs EK43 dial | cameron2020 | **Calibration source** for the σ(g) closure |
| Schmieder source-derived TDS endpoint | TDS-derived EY (source-derived run-level estimate: measured first fraction + integrated fitted kinetics) at a specified central condition | schmieder2023 | **Matched-observable empirical check** |
| Schmieder RSM curvature | fitted cup-mass surface vs flow, dial, temperature | schmieder2023 | Qualitative smooth/shape, subject to fit uncertainty |

Two confounds are load-bearing. (i) The Schmieder grind axis is a grinder *dial*,
non-monotonic in particle size (the middle dial GL 1.7 is the *finest* by Sauter
diameter, 26.9 µm vs 28.3/29.2), so a "peak at GL 1.7" is a dial statement, not a
particle-size fine-grind dip. (ii) Brew pressure changes with grind at fixed flow,
confounding the grind axis; the source itself notes the difficulty of separating
particle-size and pressure effects.

**Research questions.** (1) What does the corrected empirical target actually show?
(2) Which implemented model classes can produce that response under their registered
parameterizations? (3) What temporal structure is needed to beat specified nulls on
flow traces? (4) What failure appears when static heterogeneity and evolving
conductance are composed? *(We do not claim novelty of a first head-to-head
comparison until a related-work search supports it.)*

## 2. Methods — the registry as an experimental apparatus

Each candidate is a component with typed stage-contracts, explicit assumptions and
validity ranges, and — *where available* — named validation gates. We do **not**
claim universal real-data gating: some components carry only numerical verification
or qualitative gates, and one (the static streamtube) carries none. A passing
regression gate is software reproducibility, not scientific validation. Precise
formulation: "Components carry provenance, assumptions, and validity ranges; where
available, named gates record evidence ranging from numerical verification to
independent experimental comparison."

**No silent observable merge (a data contract).** The Schmieder cup masses are
per-solute and mixed-unit (trigonelline, caffeine, 5-CQA in mg; TDS in g), reported
for three brew ratios and modelled with temperature as a distinct predictor.
Averaging across any of these yields a quantity with no coherent unit. The corrected
adapter requires explicit component / brew-ratio / temperature / flow arguments and
asserts a single unit set (`harness.schmieder_grind_response`). Generalized rule:
*no model comparison may average or align measurements until the observable, unit,
normalization basis, experimental role, and conditioning variables are explicit and
compatible.*

Datasets, with a manifest row each carrying units, license, and validation strength
(names below are **repository dataset keys**, which may differ from the publication
year — e.g. key `waszkiewicz2025` is the Zenodo release of Waszkiewicz et al., published
in *Phys. Fluids* **2026**; the swelling model `mo2023_2` corresponds to Mo et al. *2022*):
schmieder2023, waszkiewicz2025, cameron2020, romancorrochano2017, lee2023.
*(A conventional Methods section — governing equations, calibration/evaluation
splits, numerical tolerances, statistical model, reproducibility package — is
still owed; see §7.)*

## 3. Result 1 — model-capacity discrimination (Fig. 1, Fig. 2)

**The target (matched observable).** TDS-derived extraction-yield cell means at the
nominal central condition are **numerically ordered** across dial: 18.27, 19.38,
19.62 % at dial 1.4/1.7/2.0. The middle-versus-coarse contrast is −0.24 yield-points
with a Welch t 95 % CI [−0.42, −0.06] that **excludes zero**, so the middle cell
lies below dial 2.0 and **the three selected nominal-setting source-derived endpoint
estimates do not support an interior maximum at the middle dial**. We describe the means as *ordered*, not "statistically monotone": a design-aware,
experiment-unit diagnostic (`harness.result1_design_aware_stats`) resolves the
mid-vs-coarse step (dial 1.7 − 2.0 = −0.24 EY-pt, Welch 95 % CI [−0.42, −0.06],
p ≈ 0.016) but **not** the fine-to-mid step (dial 1.4 − 1.7 = −1.11 EY-pt, CI
[−2.41, +0.19], p ≈ 0.068 — includes zero). The overall replicate-level trend is a
rise of +2.26 EY-pt per dial (**t-based** 95 % CI **[1.16, 3.36]**, 10 residual dof —
the earlier [1.29, 3.23] used a normal 1.96 multiplier, an error for a 12-run OLS slope).
Crucially these are **nominal-condition, not achieved-condition, comparisons**, a
**secondary descriptive reanalysis of three selected axis/centre settings** (dose 20 g;
15 nominal settings and 48 complete TDS/BR-1/2 runs in the full design), not the source's
primary factorial inference. The source ran each
setting as **three independently prepared extraction repetitions** (six at the centre
point); those extraction runs — not fractions or dense sensor samples — are the
experimental unit here (1.4 axis, n = 3; 1.7 centre, n = 6; 2.0 axis, n = 3), so the
within-setting spread is run-to-run variance at fixed *nominal* dial, and the Welch
contrast is a **within-campaign, setting-level** difference conditional on those runs
being independent. There is **no replication across machines, coffees, or campaigns**
(one machine, one main coffee), so it does not generalise beyond this campaign. The
*achieved* conditions also differ across the three settings — mean achieved flow
1.92 / 1.90 / 2.00 mL s⁻¹ and, most notably, mean maximum pressure **3.91 / 3.41 /
3.33 bar** at dial 1.4 / 1.7 / 2.0 — so dial is **confounded** with the achieved
conditions and the Welch contrast is not evidence that dial *alone* caused the
difference. Safely stated: the **observed central-setting cell means contain no
middle-dial maximum** (the middle mean is below the 2.0 mean in this campaign);
inferential exclusion of an underlying conditional-response maximum would require a
model for the achieved covariates and run-level variation — a full design-aware model
(achieved covariates + experiment blocks over the whole DoE) is owed (§7).

An interior maximum exists only in the study's own fitted response surface, which
is concave in grind for every observable but weak (schmieder's own adjusted R²
0.41–0.75). Our **primary refit** matches the source predictor contract — set grind
plus the **achieved** flow and temperature, evaluated at the achieved conditions of the
nominal centre point (experiment 7) — and uses a **fixed-design residual bootstrap**
appropriate to the selected design points: adjusted R² **0.64**, grind vertex at dial
**1.74 (95 % CI [1.70, 1.82]**, residual bootstrap), with **99.8 %** of bootstrap fits a
concave maximum whose vertex lies inside the tested dial domain. (A nominal-predictor,
case-bootstrap sensitivity gives a similar 1.73, [1.68, 1.81].) So **the selected
quadratic surface has a conditional interior vertex near 1.74** — the interval is
conditional on the retained seven-term model and design; we do not claim the underlying
physical response necessarily has a maximum. The raw (uncentered) predictors are
ill-conditioned (κ₂(X) ≈ 1.7×10⁶), but the identical fit on centred/scaled predictors is
well-conditioned (κ₂(X) ≈ 3.9) and the offset/scale-invariant vertex is unchanged. The
conditional vertex is **stable to deletion** (`schmieder_rsm_diagnostics`): leave-one-run
gives 1.736–1.765 and leave-one-setting 1.720–1.777 (15/15 fits stay concave and
in-domain); the one mildly influential run (experiment 10, replicate 1; Cook's *D* ≈ 0.44,
leverage 0.19, standardised residual −3.7) does not move it. It is also stable to a
**full-quadratic** form (vertex 1.737; retained-seven AICc lower). **Heteroskedasticity
sensitivity:** the within-setting SD spans ~17× (0.014–0.242 g), so alongside the iid
residual bootstrap we report **wild** bootstraps (Rademacher and Mammen), which preserve
the vertex while modestly widening the interval — the conditional vertex is not an artefact
of iid resampling. All intervals remain **conditional on the selected seven-term model**
(post-selection uncertainty is a separate, disclosed limitation). **A precision caveat, not a criticism of the
source:** the *printed* Table-3 coefficients are rounded (the T² coefficient to
three decimals; with T²≈7921 that rounding moves the absolute prediction by several
grams), so evaluating them literally gives ~6.7 g, whereas the refit reproduces
~3.9 g, near the data and the source's own Figure 4. We therefore use the response
surface for *shape* only, because the published rounded coefficients are numerically
insufficient for absolute reconstruction — **not** because the model over-predicts.
*(Predictors are on the raw scale, so the reported vertex combines the linear,
quadratic, and flow×grind coefficients rather than a single centered term.)*

**Model capacity.** A static-heterogeneity streamtube ensemble represents
permeability heterogeneity as a unit-mean lognormal. The sampled numerical yield
response is concave over the tested support, so lognormal averaging produces a
Jensen-type yield deficit; a grind-dependent width closure can convert the monotone
homogeneous response into a peaked ensemble response (Fig. 1b). This is audited
(`harness.channeling_concavity_audit`): the numerical EY(k) is concave over
**96–97 % of the tested support** at all grinds/pressures, and the lognormal
quadrature mass reaching the clipped boundaries is **<0.2 %**, so clipping does not
drive the ensemble. The deficit is also confirmed **directly**, not only through the
second-derivative sign: the measured Jensen gap J = E[EY(K)] − EY(E[K_eval]) —
evaluated against the **actual post-clipping multiplier mean** (clipping shifts it
from unity by ≤0.005, so the reference is EY(E[K_eval]), not EY(1)) — is
**negative in every cell** (deficit **−4.64 to −1.38 yield-points**; the
largest-magnitude/worst loss ≈ −4.6, the smallest ≈ −1.4), i.e. heterogeneity
genuinely loses yield relative to the mean-permeability reference. *(Global concavity is not claimed — only over the tested
support.)*

**Why this is capacity, not identification, and why the comparison is asymmetric.**
Among the response generators *currently implemented in the registry*, the
calibrated static-heterogeneity branch is the only one that generates an interior
maximum under the tested settings **without altering a source parameter**. The
comparison does not *identify* channeling, because competitor maturity, calibration,
and observables differ, and incomplete wetting is not yet represented:

- static channeling is empirically calibrated to Cameron's grind deviations (partly
  circular — its "external" target is the weak Schmieder smooth);
- the Lee branch generates the shape only at a saturation ceiling set outside the
  measured value (a deliberate sensitivity test, not the measured ceiling);
- size-exclusion supplies a *different* observable (extractable inventory);
- the diffusion branch is a null;
- incomplete wetting, a central competing hypothesis, is unimplemented.

This is a **model-availability and model-capacity audit** (Fig. 2, an evidence
matrix — implementation status, calibration data, evaluation data, observable, free
parameters, fitted-vs-predicted, evidence strength, and the decisive missing
experiment), not a symmetric head-to-head. Every status token in the matrix is
defined, and every mechanism row carries its literature source, in the published
Figure-2 data dictionary (`docs/figures/fig2_evidence_dictionary.md`, generated from
the committed `paper_b_evidence_matrix.csv` + `paper_b_evidence_dictionary.csv`; each
evidence-strength cell also names the ROADMAP §0 validation rung it maps to). A closure-sensitivity sweep finds the
interior maximum is real and grid-converged at the calibrated closure but **fragile
over the tested (s_ref, m) rectangle** — present in **10 of 25 fixed
combinations**, absent for weak channeling — and **small in magnitude**. Reporting
the prominence over the *full* grid rather than only the cells that succeed (which
would condition on success and inflate the typical bump): the **full-grid median
prominence is ≈ 0 yield-points** (interquartile range ≈ [0, 0]), because most of the
grid has no interior maximum at all; among the cells that do, the interior-only
median is ~0.14 yield-points, falling to ~0.03 (near-flat) at 9 bar. *(This grid
fraction is descriptive over a fixed rectangle, not a robustness probability.)* The
model's interior bump is small relative to the observed within-cell replicate
variation, but no formal minimum-detectable-effect analysis is claimed.

## 4. Result 2 — a null-first κ(t) ladder within a specified model set (Fig. 3)

**The null that must be beaten first.** A machine-only model (pump + headspace, no
bed dynamics; foster2025) reconstructs a mid-shot flow minimum on the digitized
source trace (Fig. 3a). Scoped statement: *the dip-and-recovery shape is not, by
itself, diagnostic of a bed mechanism, because the tested machine-only model can
reconstruct it in the source configuration* — not that the shape carries zero
information in every experimental design.

**The 9-bar ladder, scoped.** All comparisons use one explicit evaluation window,
t = 15–95 s, and each baseline is evaluated at its own predicted level (no RMSE is
copied between rungs). Three *distinct* constant nulls — the least-squares-optimal
in-window constant (RMSE 0.573 g/s, one free level), a long-run constant calibrated
on a real 10 s late interval (0.641), and the published static κ(P) evaluated at
9 bar (0.648, **0 coefficients fitted to this flow trace**) — all land at 0.57–0.65 g/s:
at constant 9 bar a static pressure-dependence is observationally identical to a constant.
An empirical dissolution-linked time-varying porosity trajectory with **0 coefficients
fitted to this flow trace** (it imports donor parameters, see below)
reaches RMSE 0.116 g/s (Fig. 3b), beating the *best* of the three constant nulls
~4.9× and the static κ(P) null ~5.6×. **Bound on the claim.** A purely
phenomenological degree-3 polynomial in time (four free parameters, no mechanism)
reaches RMSE 0.096 g/s — at least as good as the mechanistic trajectory. The
honest, scoped claim is therefore: *within the 15–95 s window, tested model set, and
RMSE metric, a time-varying reconstruction is needed (every constant baseline has
substantially larger in-window reconstruction error), but a specific bed mechanism is not
thereby identified — a flexible non-mechanistic time curve reconstructs equally well, and
these are in-sample reconstruction errors on one trace with strongly structured residuals
(mean decimated Durbin–Watson ≈ 0.01), not held-out predictive scores.* The
non-trivial mechanistic content is that a poroelastic Φ(t) with **zero additional
coefficients fitted to this 9-bar flow trace** (though it imports two campaign-calibrated
equilibrium parameters and a 9-bar-TDS-fitted solids sigmoid — see the provenance table
below) nearly reaches the four-parameter flexible floor. The cubic, by contrast, is fit
and scored on the *same* 15–95 s trace, so its RMSE is an **in-sample flexibility bound**,
not a fair predictive competitor. The Φ(t) trajectory is also soft-circular (dissolved
mass derives from the same rig's TDS and flow), and we avoid "parameter-free" because the
donor parameters were estimated elsewhere.

Because the residuals are strongly autocorrelated (lag-1 residual autocorrelation ≈0.99 in
every branch, consistent with the near-zero Durbin–Watson above), a naïve pointwise RMSE
comparison overstates its own precision. We therefore apply a **moving-block resampling of
the already-computed per-timestep squared-error differences** (8 s blocks, 1000 resamples):
this is a *conditional block interval on the fixed loss sequences* — it preserves the
serial dependence but does **not** refit either branch inside each resample, so it is a
dependence-aware uncertainty on the RMSE difference, not a bootstrap of the full
fit-and-compare procedure (B5-04). Read that way it supports both halves of the reading and
neither more: Φ(t) beats the best constant by ΔRMSE ≈ −0.39 g/s with a 95 % interval of
[−0.60, −0.23] that excludes zero — *time variation of some form* is robustly required —
whereas Φ(t) versus the flexible cubic gives ΔRMSE ≈ +0.02 g/s with interval [−0.01, +0.05]
straddling zero, so **the difference is not resolved by this conditional interval** (B5-05;
we do not claim the two are "statistically indistinguishable"), and the fit does not
identify the *mechanism*. The Φ-beats-constant ordering persists across all three fit
windows (10–90, 15–95, 20–90 s); the Φ-versus-cubic difference does not survive as a strict
ordering in any of them (`result2_residual_diagnostics`).

| branch | fitted to THIS Q(t) trace | fitted elsewhere in same campaign | literature/donor-fixed |
|---|---:|---|---|
| best constant | 1 (level) | 0 | 0 |
| static κ(P) | 0 | 2 (equilibrium P_c,Q_c) | constitutive form |
| empirical Φ(t) | 0 | 2 equilibrium + 3 TDS-sigmoid | constitutive form |
| RC-3b | 0 | 2 equilibrium | Cameron donor calibration |
| flexible cubic | 4 | 0 | polynomial form |

**The flexible null bounds *identification*, but a sign test *constrains* the isolated
matrix-resistance branches.** Fit quality alone does not single out a mechanism (the
phenomenological cubic ties the poroelastic trajectory), yet the *direction* of each
candidate's flow contribution does discriminate. Both bed-mechanical competitors —
particle swelling (mo2023_2) and fines migration (fasano2000_partI) — can only *increase*
resistance at fixed pressure, so each predicts *falling* flow: the wrong sign for a rising
residual. Running mo2023_2's own Carman–Kozeny prediction (its validated fixed-Δp mechanism)
gives a monotone-decreasing flow ratio (throttling to ≈4 % of initial over the shot for a
representative illy powder); given a best-case free level it scores RMSE ≈1.08 g/s — *worse
than the best constant null* — and is anti-correlated with the trace (*r* ≈ −0.95, Fig. 3d).
(The **sign** follows from the branch assumptions; the ≈4 %/1.08 g/s **magnitude** is
specific to this one transferred powder parameterization and is not offered as a general
espresso prediction, review MAJ-30.)
For fines
migration the exclusion is analytic: its discharge is monotone non-increasing at constant p₀
(Fasano–Talamucci–Petracco Lemma 8.3, under that model's stated assumptions), and their
Part III result states the flux can rise again *only if the applied pressure increases* — so
under the **imposed fixed-pressure boundary condition** an isolated resistance-only branch
cannot by itself source the rise. This is a **conditional sign constraint** on an *isolated,
resistance-only* branch with machine response and all other state variables held fixed; it is
**not** a general refutation. A real or coupled bed can combine simultaneous dissolution
opening, compaction relaxation, changing saturation, viscosity, gas release, machine/headspace
response, and erosion — swelling or fines may be present while another process dominates the
net sign — and a single transferred powder parameterization cannot license a "coffee-independent"
magnitude or absence. Dissolution-driven porosity *opening* (the Φ(t) trajectory) is the only
*implemented isolated branch in this comparison* with the required net sign. Two named
candidates are declared out of adjudication on this observable rather than silently dropped:
the Fasano Part II porosity-evolution law has no published constitutive constants (an untested
skeleton — parameter-blocked), and lee2023 is a constant-*flow*, grind-indexed extraction-yield
model belonging to the orthogonal fine-grind axis, not this constant-pressure flow trace.
Scoped statement: *within the imposed fixed-pressure model, the tested resistance-only swelling
and fines branches cannot by themselves generate the observed rising contribution; this
constrains isolated branches, not their presence in a coupled bed. Distinguishing dissolution
quantitatively from fines
migration still requires a pressure-step or flow-reversal protocol (owed — specified in
`docs/PROTOCOL_kappa_t_discrimination.md`).*

**Cross-pressure — held-out, conditional on campaign calibration.** With the
published static calibration from the same eleven-pressure campaign, we predict the
other pressures. **Figure 3c now shows both** the shared-calibration curves and the
**leave-one-pressure-out held-out RMSE by pressure** (open markers; review MAJ-26/B3-12) —
the LOPO evidence the argument relies on is now in the figure, not only in the text; the
held-out curves track the shared calibration (max calibration drift ≈2.8 %). This is
**within-rig generalization conditional on campaign-wide constants** (the LOPO refits only
the two-parameter equilibrium pair; the 9-bar-TDS solids trajectory and donor assumptions
stay fixed, MAJ-27), not fully independent out-of-sample validation. The relative
reconstruction errors **vary continuously with pressure** (we reserve "regime" for a
formally defined transition, MAJ-28) — an empirical trajectory has the best held-out mean,
a flow-coupled variant does better at low pressure, the static null at mid-range — but the
pressure bins are descriptive, not predeclared, so we present the continuous
pressure-residual curves rather than categorical winners. **No branch dominates the
three tested branches across all pressures**; migration, compaction, matched-control
swelling, viscosity, and sensor uncertainty remain outside the comparison.

**Leave-one-pressure-out confirms the calibration is not tuned to any single
pressure.** To check that the shared calibration does not smuggle each held-out
pressure into its own prediction, we refit the two-parameter equilibrium pair
(P_c, Q_c) on the other ten pressures and predict the genuinely held-out eleventh
trace. Dropping any single pressure moves (P_c, Q_c) by at most **2.8 %**, and the
held-out mean RMSE (static 0.534, Φ(t) 0.347, RC-3b 0.525 g/s) matches the
shared-calibration mean (0.524 / 0.334 / 0.519) to within ~0.01–0.02 g/s; Φ(t) remains the
lowest-error branch overall and the descriptive separation is unchanged. The eleven-point,
two-parameter equilibrium fit is therefore **not dominated by any single pressure point**.
This does **not** establish that the residual pressure pattern is physical (review MAJ-14):
the 9-bar solids trajectory and other donor assumptions remain fixed, so omitted machine
dynamics, viscosity/sensor effects, an imperfect equilibrium form, or other omitted bed
mechanisms could produce the same pattern — its physical origin is unresolved. This is a
**within-campaign leave-one-pressure-out evaluation of the equilibrium calibration** (with the
9-bar solids trajectory held fixed), not an independent second-rig validation. It is the trace-level,
three-mechanism companion to the equilibrium-curve leave-one-pressure-out test of the
static characteristic alone (`lopo_waszkiewicz_pressure`, Q² ≈ 0.81 on the eleven
long-run points). **Four distinct summaries are kept separate (review AR-B2-08), because
they are easy to conflate:** (a) LOPO held-out, all 11 pressures — static 0.534 / Φ 0.347
/ RC-3b 0.525; (b) shared-calibration, all 11 — 0.524 / 0.334 / 0.519; (c) shared-
calibration, ten off-9-bar — 0.512 / 0.356 / 0.530 (`cross_pressure_discrimination`, full
precision); (d) the equilibrium-curve LOPO Q² (0.81). The 0.512/0.356/0.530 values are the
**shared-calibration off-9-bar** means (c), *not* leave-one-pressure-out held-out means.
Three further diagnostics qualify the aggregation: (i) all summaries are computed from
**unrounded** per-pressure RMSEs; (ii) each branch carries the same **two** flow-fitted
parameters (P_c, Q_c) — Φ(t) and RC-3b add donor parameters fit to *other* observables
(the sigmoid to 9-bar TDS, Cameron to its own calibration), i.e. zero additional flow
degrees of freedom; and (iii) the residual serial-correlation diagnostic
(`residual_autocorr.summary`, computed on the trace **decimated to 1 s** so it reflects
model structure rather than the ≈10 Hz sample spacing) gives a mean Durbin–Watson ≈ 0.01
— a strong positive autocorrelation, i.e. the dynamic model (0 coefficients fitted to this
flow trace) leaves a **systematically structured, non-white residual** (an honest
lack-of-fit the RMSE ranking rides on, not clean noise). Because these residuals are
strongly serially dependent, the pointwise RMSE differences are **in-sample reconstruction
scores over one window, not held-out predictive validation** (MAJ-22/23).

**The composition attempt fails, honestly (Fig. 4).** The registered shared-porosity
synthesis reduces exactly to the poroelastic rung under extraction-only; adding an
imported (pre-parameterized, not free) swelling branch flattens the predicted flow
(residual 0.648 g/s over 15–95 s, worse than the best-constant null of 0.573 g/s on
the same window). Scoped statement: *the imported swelling
parameterization is incompatible with the observed 9-bar trajectory under the
tested shared-porosity composition; the calculation does not distinguish
control-regime, parameter-transfer, initial-condition, or composition-form errors.*
The 14× flow rise the ladder requires can be reconstructed from the adopted porosity
trajectory only through a near-choke poroelastic closure; the auxiliary
Kozeny–Carman relation is too gentle for *that specific reconstruction* (we do not
claim it is physically invalid for espresso beds in general).

## 5. Result 3 (exploratory) — an uncoupled-streamtube composition failure (Fig. 5)

Results 1 and 2 supply a static heterogeneity mechanism and an evolving-porosity
mechanism; we ask what happens when each streamtube carries its own
extraction-driven conductance clock. We build this with grounded scales as an
**exploratory** construction, not a registered component.

**Result, scoped.** In the tested near-choke, flow-controlled configuration the
flow concentrates into a single effective channel — measured by the maximum
single-tube share (→1.0) and the effective channel count (1/Σsᵢ² → 1.0 of the
tubes). The gentle Kozeny–Carman closure stays distributed (~83 of 150).

**Not a stability theorem.** A leading-order argument gives a conductance-ratio gain
G = (M(φ_max)/M(φ₀))^(1−λ), but M(φ₀)→0 at the near-choke shutoff, so for the
poroelastic closure G is **floor-dependent** (it scales ∝1/floor; the
log-linearization is singular at a zero-conductance base state) and its magnitude is
not meaningful — while Kozeny–Carman G≈1.5 is floor-independent (Fig. 5d, supplementary). We do
**not** claim "linear instability" or a "closed-form stability criterion": the base
state is heterogeneous (no Jacobian along that trajectory is computed), the reported
gain is controlled by an imposed floor, and any threshold is operational rather than
derived. What is invariant over the tested floors is the endpoint classification, and
this is **measured, not asserted**: the N-tube integration is re-run at each conductance
floor across the swept range (**1e-6…1e-15**), and the endpoint is unchanged.

**A one-factor-at-a-time (OFAT) robustness study plus a crossed control×lateral×closure
design** (`ntube_robustness_study`; not a full factorial, review MAJ-34) sweeps the
remaining axes, and a **full-trajectory conservation audit** (review MAJ-33) records the
worst share-sum deviation, raw non-negativity of conductance/relative-flow/age, and the
control-law flow balance over **every substep** (not a final-step check):

| swept axis | tested range | endpoint |
|---|---|---|
| tube count *N* | 100 – 800 | concentrates (N_eff→1.0) — **invariant** |
| timestep (substeps) | 4 – 32 | invariant |
| grind *gs* | 1.1 – 2.0 | invariant |
| pressure | 6 – 11 bar | invariant |
| stochastic finite-network realisations | 4 seeds | invariant |
| **lateral homogenisation** | 0 → 0.1 → 0.3 | N_eff 1.0 → 19 → **307 (concentration destroyed)** |
| **control law** | flow vs pressure | flow: N_eff 1.0; **pressure: 219 (no concentration)** |
| closure (negative control) | poroelastic vs CK | poroelastic 1.0; CK 217 (bounded) |

So the concentration endpoint is **invariant on the numerical (N, timestep), stochastic,
and operating (grind, pressure) axes** — reported separately, not collapsed into one flag
(MAJ-40) — and the full-trajectory conservation/non-negativity audit holds throughout
(under flow control the raw total relative flow is conserved by construction; under
pressure control it is free, which the audit now states rather than hides). The endpoint
is **contingent on two physical assumptions**: fixed-*flow* control (under fixed-*pressure*
control tubes do not steal, and N_eff≈219) and near-zero lateral coupling (a homogenisation
blend of only 0.3 already suppresses it, N_eff≈307). Note the endpoint N_eff saturates at
its ~1 lower bound, so its invariance across N is endpoint saturation, not a demonstration
of trajectory/collapse-time convergence (MAJ-35). We therefore add a **timestep-refinement
convergence study** of the switching itself (`ntube_switching_convergence`, review
MAJ-36/B3-14): plotted on the **physical clock** (Fig. 5a, seconds — not normalized shot
time), the **collapse-time event** (first second half the flow enters one tube) stabilises
near **≈2–3 s** as the explicit-Euler step is refined 8–16× (spread ≲0.1 s), with the final
N_eff unchanged. **Scope (B5-08):** this establishes convergence of the *collapse-time
event measured on the output grid under Euler refinement* — NOT a grid-independent
full-trajectory result. A full trajectory-norm convergence (interpolated onto a common
physical-time grid, event-time error vs both spatial and temporal refinement, and at least
one higher-order/adaptive solver) remains owed before the switching can be called a proven
grid-independent physical event rather than a refinement-stable Euler feature. A
**16-realisation stochastic distribution** (review MAJ-38) gives a small median N_eff/N; but
we do NOT call it a "tight" distribution (B5-10): the collapse/switching **time** varies
materially — by ≈39 % across tube count, by >1 s across grind/pressure, and over ≈1.4–3.5 s
across the 16 seeds (some seeds end with two effective channels) — so we report those event
distributions, not only the endpoint N_eff.
This is a genuine sweep-and-conservation robustness result within the tested family, **not**
a proven instability: a physical transverse-Darcy lateral-exchange operator and a formal
Jacobian/finite-time-Lyapunov growth analysis remain owed (§7). We therefore keep Result 3
explicitly exploratory, and state its result precisely as **flow concentrates in the
near-choke, flow-controlled, low-lateral configuration**, not unconditionally.

**What controls it.** The concentration is confined to flow control with low
homogenization (Fig. 5c); the trajectory (Fig. 5a) collapses N_eff→1 while the endpoint
is invariant in N and timestep (Fig. 5b). Under pressure control (independent tubes, no
shared flow to steal) there is no collapse (N_eff≈200+), and a homogenizing term (a
proxy, **not** a physical transverse-Darcy exchange) of only 0.3 suppresses it. The
finding is that the parallel, non-exchanging streamtube composition **can concentrate
strongly** once permeability evolves under flow control — a diagnosed
composition-model failure mode, not a proven physical instability — and it motivates
a physical lateral-exchange closure. *(A genuine stability result — a physical lateral operator,
a Jacobian/finite-time-Lyapunov analysis, and floor/start-time/N/timestep/pressure/
grind sweeps — is owed, §7.)*

## 6. Discussion

The organizing theme is that, **across the datasets and model classes tested here,
integrated observables can erase the structure needed to discriminate mechanisms**:
a whole-cup endpoint hides the inventory–kinetics separation (companion
identifiability study); a single pressure trace leaves several time-dependent bed
mechanisms partially degenerate, and a flexible non-mechanistic temporal null does
as well as the physical branch (Result 2); and a model suggests spatially-resolved
flow would be far more discriminating than any integrated trace (Result 3). We scope
this to the two datasets examined — it is not a claim about all integrated
observables in espresso. Crucially, the per-tube "observations" of Result 3 are
*simulated* — the work motivates spatial observables, it does not provide
experimental evidence that real pucks evolve into one channel.

**What would actually discriminate each result** (the concrete measurement each
degeneracy calls for):

| result | what integration hides | discriminating measurement |
|---|---|---|
| 1 — fine-grind response | inventory vs kinetics vs channeling all fit the cup EY | matched-observable fractions (companion study) + per-grind **first-drip timing** (separates incomplete wetting) + spatial saturation |
| 2 — κ(t) ladder | constant / static-κ(P) / dissolution-Φ(t) / flexible-cubic all reconstruct one trace within a factor | **multi-pressure** traces under matched control + an **independently measured bed-state** (porosity/compaction in situ) to break the Φ(t) soft-circularity |
| 3 — N-tube concentration | a single outlet flow cannot see channel structure | **pathway-resolved / spatial** flow or dye-front imaging; a second-rig transfer set |

Practitioner-facing statement, kept cautious: *static flow heterogeneity remains a
plausible generator of the fine-grind response, but the available integrated
measurements do not identify it uniquely.* We do not assert a physical
flow-control/pressure-control distinction for the real shot until both modes are
analyzed under a physically consistent machine/bed system and tested experimentally.

## 7. Open gaps this paper defines

- Full-precision response-surface reconstruction (source coefficients/model object).
  *Partially addressed:* a documented raw-data refit now reports adjusted R² (0.65), a
  **fixed-design residual-bootstrap** vertex CI ([1.69, 1.80]; a case bootstrap gives a
  similar [1.68, 1.81], and **99.8 %** of bootstrap fits are jointly concave-and-in-domain,
  conditional on the retained seven-term model), a **leave-one-setting-out** Q² over the
  15 experiment IDs with achieved predictors (0.48), and a
  coefficient-covariance / residual panel (`schmieder_rsm_refit.diagnostics`:
  per-coefficient standard errors, residual σ ≈ 0.11, max standardized residual ≈ 3.7,
  max leverage 0.18). The raw (uncentered) predictors are ill-conditioned — the
  **design-matrix** condition number κ₂(X) ≈ 1.7×10⁶ (the Gram κ₂(XᵀX) ≈ 2.7×10¹² is its
  square, and is *not* the design condition number) — so the individual coefficients/SEs
  are numerically unstable while the offset-invariant vertex and predictive Q² are not;
  the interval is conditional on the retained quadratic model and design. The refit now
  runs on **both** the nominal-target and the source's **achieved** flow/temperature
  predictors (`schmieder_rsm_refit(predictors=…)`, MAJ-04): the vertex is insensitive to
  the choice (achieved 1.74 vs target 1.73; adj-R² 0.643 vs 0.649), repairing the method
  mismatch, and the plotted RSM curve (Fig 1) now uses the achieved-predictor fit
  *consumed from the single analysis result* rather than re-fitted in the plotting layer.
  Still owed is the source's own full-precision coefficient/covariance matrix (author
  request).
- A full design-aware, experiment-unit statistical model of the Result-1 dial
  response. *Partially addressed:* `harness.result1_design_aware_stats` now reports
  the per-dial achieved covariates, the run-level replication (3 runs/setting, 6 at the
  centre), both adjacent pairwise Welch contrasts, and a t-based replicate-level trend
  ([1.16, 3.36]); still owed is a
  block/mixed-effects model over the whole DoE (not just the 3 central-condition
  cells) with achieved flow/temperature/pressure as covariates.
- Direct spatial flow/saturation data; a second-rig or second-coffee transfer
  dataset; parameter-identifiability analysis for the temporal branches.
- A physically-derived lateral-exchange network + a genuine stability analysis
  (Jacobian/finite-time-Lyapunov) for Result 3.
- Unsaturated-flow constitutive data (coffee retention curve + relative permeability)
  to instrument incomplete wetting; per-grind first-drip timing as the Result-1
  discriminator (the wetting mechanism moves it, static channeling does not).

---

## Status & to-do (NOT for the manuscript body)

*The review correctly notes that "all gated/committed" is project management, not
scientific readiness, and that Results 1 and 3 needed recomputation — now done.*
- **Corrected (2026-07-12):** the RSM rounding artifact removed; contrast CI replaces
  the noise-floor heuristic; Result 3 downgraded to finite-time concentration; Fig 1
  (refit curve) and Fig 5 (gain-vs-floor) regenerated; abstract "independently gated"
  contradiction removed.
- **Delivered (2026-07-12; narrowed 2026-07-13 per PAPER_B_DETAILED_REVIEW):** Phase-3 —
  a **conditional sign constraint** showing the mo2023_2 swelling and fasano-partI
  fines-migration branches, *as isolated resistance-only branches under fixed pressure*,
  cannot themselves source the rise (rung 5b, `kappa_t_ladder`; NOT a refutation in a
  coupled bed); **trace-level leave-one-pressure-out cross-pressure** calibration-stability
  check (max
  calibration drift 2.8 %, held-out ≈ shared, `cross_pressure_loco`; companion to the
  existing equilibrium-curve `lopo_waszkiewicz_pressure`, Q² ≈ 0.81) + full-precision
  aggregation and flow-parameter counts (`cross_pressure_discrimination`); residual
  serial-correlation via the existing decimated `residual_autocorr.summary` (mean
  Durbin–Watson ≈ 0.01 → honest lack-of-fit); RSM coefficient-covariance / leverage panel
  (`schmieder_rsm_refit.diagnostics`; predictive Q² via `lopo_rsm_design_point`).
- **Still owed before submission (major):** conventional Methods (equations,
  calibration splits, statistics, uncertainty); related-work / novelty search
  (scaffolded in `docs/PAPER_B_RELATED_WORK.md` — card-grounded prior-art matrix +
  claim positioning + the owed systematic-search protocol; **novelty not asserted**,
  DB execution is PI-owed, two DOIs flagged for verification);
  full-precision or refit RSM with covariance (source coefficients — author request);
  a physical lateral operator + formal stability analysis or explicit appendix
  downgrade; Data/Code availability + pinned release; LaTeX. **External-blocked:**
  independent second-rig / second-coffee transfer set; direct spatial flow/saturation
  data; unsaturated-flow constitutive data; the pressure-step / flow-reversal protocol
  that would quantitatively separate fines-migration from dissolution (design specified
  in `docs/PROTOCOL_kappa_t_discrimination.md` — awaiting a reversal/step/rebrew rig).
- **Companion:** Paper A (extraction identifiability, `ANALYSIS_transfer.md`) is a
  separate track, cited here only for the shared observability theme.

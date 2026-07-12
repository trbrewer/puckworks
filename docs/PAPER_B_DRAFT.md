# Paper B — draft prose (rev. 2026-07-12, post detailed review)

*Manuscript draft, **major-revision rewrite** after
`docs/PAPER_B_DRAFT_detailed_review.md`, which is adopted. The review found three
submission-blocking problems in the previous draft — a coefficient-rounding
artifact in the RSM claim, a mis-stated "noise floor", and an over-claimed
linear-stability result — all now corrected in code/docs (ROADMAP §7.1). Verb
discipline: "shows/predicts" only for independent evidence; "reconstructs/is
consistent with" for post-fit; "can generate / does not generate under the tested
parameterization" for qualitative discrimination; "exhibits in the tested
configuration / motivates" for exploratory synthesis; never "identifies / proves /
is the mechanism / unconditionally / linearly unstable". Figures:
`docs/figures/fig{1..5}`. Validation-strength tags stay in the text.*

**Title (review-endorsed).** Mechanism discrimination in espresso flow and
extraction: matched observables, null models, and transient streamtube
concentration.
*(A stability-focused title can be reconsidered only if a formal Jacobian/eigenmode
analysis is completed — it is not.)*

---

## Abstract

Espresso measurements integrate flow, extraction, and bed evolution in ways that
can make distinct mechanisms observationally similar. We use a provenance-tracked
model registry and a null-first comparison hierarchy to test what current data can
distinguish. First, we correct a mixed-observable aggregation in which milligram
solute masses and gram total-dissolved-solids values had been combined across brew
ratios; enforcing a single matched observable is a prerequisite the field has not
stated. At a fixed central condition the resulting TDS-derived extraction-yield
response is monotone across the three grind settings (the middle-versus-coarse
contrast is −0.24 yield-points, 95 % Welch CI [−0.42, −0.06], excluding zero). A
calibrated static-heterogeneity streamtube model can generate an interior maximum
over part of its parameter range, but this is a model-capacity result rather than
causal identification, because the closure is grind-calibrated and incomplete
wetting remains unmodeled. Second, on rising-flow traces a machine-only model shows
that a dip-and-recovery shape is not diagnostic of bed dynamics, while an empirical
time-varying porosity branch reconstructs the 9-bar trace better than specified
flat baselines; performance across pressure is regime-dependent within the same
experimental campaign. Finally, an exploratory uncoupled streamtube extension with
extraction-dependent conductance exhibits strong transient flow concentration in a
tested near-choke, flow-controlled configuration; the result motivates a physical
lateral-exchange model but does not establish a universal instability criterion.
The common conclusion is that integrated observables are insufficient for unique
mechanism identification, and that spatial, pathway-resolved, or first-drip
measurements are needed.

---

## 1. Introduction

Below a threshold grind, espresso extraction can stop rising with fineness even
though specific surface area keeps increasing, and homogeneous-flow models predict
a monotone rise. The effect is usually attributed to one of a small set of
mechanisms, but the mechanisms have not been run head-to-head against the same
matched observable, and the effect is weak enough that a mechanism can appear to
"reproduce" it for reasons that do not survive scrutiny.

Three *different* objects have been conflated in prior discussion; we keep them
distinct throughout.

| Object | Observable | Dataset | Role here |
|---|---|---|---|
| Cameron fine-grind deviation | EY residual from a homogeneous model vs EK43 dial | cameron2020 | **Calibration source** for the σ(g) closure |
| Schmieder raw TDS response | TDS-derived EY at a specified central condition | schmieder2023 | **Matched-observable empirical check** |
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

Datasets, with a manifest row each carrying units, license, and validation strength:
schmieder2023, waszkiewicz2025, cameron2020, romancorrochano2017, lee2023.
*(A conventional Methods section — governing equations, calibration/evaluation
splits, numerical tolerances, statistical model, reproducibility package — is
still owed; see §7.)*

## 3. Result 1 — model-capacity discrimination (Fig. 1, Fig. 2)

**The target (matched observable).** TDS-derived extraction yield at the fixed
central condition is monotone: 18.3, 19.4, 19.6 % at dial 1.4/1.7/2.0. The
middle-versus-coarse contrast is −0.24 yield-points with a Welch t 95 % CI
[−0.42, −0.06] that **excludes zero** — the raw response is statistically monotone,
with no interior bump.

An interior maximum exists only in the study's own fitted response surface, which
is concave in grind for every observable but weak (adjusted R² 0.41–0.75). **A
precision caveat, not a criticism of the source:** the *printed* Table-3
coefficients are rounded (the T² coefficient to three decimals; with T²≈7921 that
rounding moves the absolute prediction by several grams), so evaluating them
literally gives ~6.7 g, whereas a refit to the committed observations reproduces
~3.9 g, near the data and the source's own Figure 4. We therefore use the response
surface for *shape* only, because the published rounded coefficients are numerically
insufficient for absolute reconstruction — **not** because the model over-predicts.

**Model capacity.** A static-heterogeneity streamtube ensemble represents
permeability heterogeneity as a unit-mean lognormal. The sampled numerical yield
response is concave over the tested support, so lognormal averaging produces a
Jensen-type yield deficit; a grind-dependent width closure can convert the monotone
homogeneous response into a peaked ensemble response (Fig. 1b). This is audited
(`harness.channeling_concavity_audit`): the numerical EY(k) is concave over
**96–97 % of the tested support** at all grinds/pressures, and the lognormal
quadrature mass reaching the clipped boundaries is **<0.2 %**, so clipping does not
drive the ensemble. *(Global concavity is not claimed — only over the tested
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
experiment), not a symmetric head-to-head. A closure-sensitivity sweep finds the
interior maximum is real and grid-converged at the calibrated closure but **fragile
over the tested (s_ref, m) rectangle** — present in **10 of 25 pre-specified
combinations**, absent for weak channeling — and **small in magnitude** (median
prominence ~0.14 yield-points; ~0.03, near-flat, at 9 bar). *(This grid fraction is
descriptive over a chosen rectangle, not a robustness probability.)* The model's
interior bump is small relative to the observed within-cell replicate variation,
but no formal minimum-detectable-effect analysis is claimed.

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
9 bar (0.648, zero free parameters) — all land at 0.57–0.65 g/s: at constant 9 bar
a static pressure-dependence is observationally identical to a constant. A
zero-free-parameter empirical dissolution-linked time-varying porosity trajectory
reaches RMSE 0.116 g/s (Fig. 3b), beating the *best* of the three constant nulls
~4.9× and the static κ(P) null ~5.6×. **Bound on the claim.** A purely
phenomenological degree-3 polynomial in time (four free parameters, no mechanism)
reaches RMSE 0.096 g/s — at least as good as the mechanistic trajectory. The
honest, scoped claim is therefore: *within this window and null set, time variation
is required (every constant baseline fails), but a specific bed mechanism is not
thereby identified — a flexible non-mechanistic time curve fits equally well.* The
non-trivial mechanistic content is that a **zero-parameter** poroelastic Φ(t)
nearly reaches the four-parameter flexible floor. The trajectory is also
soft-circular (dissolved mass derives from the same rig's TDS and flow), and we
avoid "parameter-free" because the donor parameters were estimated elsewhere.

**Cross-pressure — held-out, conditional on campaign calibration.** With the
published static calibration from the same eleven-pressure campaign, we predict the
other pressures (Fig. 3c). This is **within-rig generalization conditional on
campaign-wide constants**, not fully independent out-of-sample validation. It is
regime-dependent — an empirical trajectory has the best held-out mean, a flow-coupled
variant does better at low pressure, the static null at mid-range — but the
pressure bins are descriptive, not predeclared, so we present the continuous
pressure-residual curves rather than categorical winners. **No branch dominates the
three tested branches across all pressures**; migration, compaction, matched-control
swelling, viscosity, and sensor uncertainty remain outside the comparison. *(Owed:
full-precision residual aggregation, residual autocorrelation, parameter counts,
and leave-one-pressure-out refitting.)*

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

## 5. Result 3 — an uncoupled-streamtube composition failure (Fig. 5)

Results 1 and 2 supply a static heterogeneity mechanism and an evolving-porosity
mechanism; we ask what happens when each streamtube carries its own
extraction-driven conductance clock. We build this with grounded scales as an
**exploratory** construction, not a registered component.

**Result, scoped.** In the tested near-choke, flow-controlled configuration the
flow concentrates into a single effective channel — measured by the maximum
single-tube share (→1.0) and the effective channel count (1/Σsᵢ² → 1.0 of the
tubes). The gentle Kozeny–Carman closure stays distributed (~110 of 120).

**Not a stability theorem.** A leading-order argument gives a conductance-ratio gain
G = (M(φ_max)/M(φ₀))^(1−λ), but M(φ₀)→0 at the near-choke shutoff, so for the
poroelastic closure G is **floor-dependent** (it scales ∝1/floor; the
log-linearization is singular at a zero-conductance base state) and its magnitude is
not meaningful — while Kozeny–Carman G≈1.5 is floor-independent (Fig. 5b). We do
**not** claim "linear instability" or a "closed-form stability criterion": the base
state is heterogeneous (no Jacobian along that trajectory is computed), the reported
gain is controlled by an imposed floor, and any threshold is operational rather than
derived. What *is* robust and floor-independent is the numerical concentration:
poroelastic drives N_eff→1, Kozeny–Carman does not.

**What controls it.** The concentration is confined to flow control with zero
homogenization (Fig. 5a, at fixed grind gs=1.1); under pressure control (independent
tubes, no shared flow to steal) there is no collapse (N_eff≈84), and a homogenizing
term (a proxy, **not** a physical transverse-Darcy exchange) suppresses it. The
finding is that the parallel, non-exchanging streamtube composition is structurally
unsafe once permeability evolves under flow control, and it motivates a physical
lateral-exchange closure. *(A genuine stability result — a physical lateral operator,
a Jacobian/finite-time-Lyapunov analysis, and floor/start-time/N/timestep/pressure/
grind sweeps — is owed, §7.)*

## 6. Discussion

The organizing theme is that **integrated observables erase the structure needed to
discriminate mechanisms**: a whole-cup endpoint hides the inventory–kinetics
separation (companion identifiability study); a single pressure trace leaves several
time-dependent bed mechanisms partially degenerate (Result 2); and a model suggests
spatially-resolved flow would be far more discriminating than any integrated trace
(Result 3). Crucially, the per-tube "observations" of Result 3 are *simulated* — the
work motivates spatial observables, it does not provide experimental evidence that
real pucks evolve into one channel.

Practitioner-facing statement, kept cautious: *static flow heterogeneity remains a
plausible generator of the fine-grind response, but the available integrated
measurements do not identify it uniquely.* We do not assert a physical
flow-control/pressure-control distinction for the real shot until both modes are
analyzed under a physically consistent machine/bed system and tested experimentally.

## 7. Open gaps this paper defines

- Full-precision response-surface reconstruction (source coefficients/model object)
  or a documented raw-data refit with covariance, adjusted R², residual diagnostics,
  and bootstrap vertex/prominence.
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
- **Still owed before submission (major):** conventional Methods (equations,
  calibration splits, statistics, uncertainty); related-work / novelty search;
  full-precision or refit RSM with covariance; leave-one-pressure-out validation;
  a physical lateral operator + formal stability analysis or explicit appendix
  downgrade; Data/Code availability + pinned release; LaTeX.
- **Companion:** Paper A (extraction identifiability, `ANALYSIS_transfer.md`) is a
  separate track, cited here only for the shared observability theme.

# Paper B — draft prose

*Manuscript draft assembled from `PAPER_OUTLINE.md` and the committed analyses
(`ANALYSIS_P2.md`, `P3_hypotheses.md`) after the review. Verb discipline (review
§3): "shows/predicts" only for independent evidence; "reconstructs/is consistent
with" for post-fit; "can generate/does not generate under the tested
parameterization" for qualitative discrimination; "exhibits in the tested
configuration/motivates" for exploratory synthesis; never "identifies/proves/is
the mechanism/unconditionally". Figures: `docs/figures/fig{1..5}`. This is a
draft; validation-strength tags are load-bearing and stay in the text.*

**Title.** Mechanism discrimination for the fine-grind espresso extraction
anomaly, and a stability test of uncoupled streamtube models.

---

## Abstract

Espresso extraction changes with grind in ways that homogeneous-flow models do
not capture, and the effect is small enough that it is easy to over-claim. We use
a component registry — in which each candidate mechanism is an independently
provenanced, independently gated model rather than a tuned term in a monolith — to
ask which *model classes* can generate the observed response, under an explicit
validation-strength vocabulary. Enforcing matched observables exposes a
prerequisite the field has not stated: the reference dataset's per-solute cup
masses mix milligram solute masses with gram total-dissolved-solids across three
brew ratios, and must never be averaged into one "cup mass". On the corrected,
per-observable target (total-dissolved-solids extraction yield at fixed
conditions), the measured grind response is monotone; an interior maximum appears
only in the study's own weak response surface (adjusted R² 0.41–0.75), and even
that surface over-predicts the measured absolute cup mass ~1.7×, so it is usable
for shape only. Of the implemented response generators, an empirically-calibrated
static-heterogeneity (channeling) closure is the only one that *can generate* an
interior grind maximum without a doctored constant — a model-capacity result, not
identification: the closure is itself grind-calibrated, its interior maximum is
fragile (present in ~40% of its parameter grid) and weak (below the measurement
noise floor), and the incomplete-wetting hypothesis remains untested. On a
rising-flow pressure trace, a null-first ladder shows that a machine-only model
already reproduces the classic dip-and-recover flow signature, that a time-varying
porosity trajectory is nonetheless required to beat the specified flat baselines,
and that dissolution-linked porosity growth is sufficient — but not unique, and
regime-dependent across pressures. Finally, giving each parallel streamtube its
own extraction-driven permeability clock is, in the tested near-choke
configuration under flow control, linearly unstable: a closed-form analysis shows
the perturbation amplification equals the end-to-start conductance ratio, which
diverges for the near-choke closure and is order-unity for a gentle one; the
instability disappears under pressure control or with lateral coupling. The
unifying theme, shared with a companion identifiability study, is that integrated
observables erase the structure needed to discriminate mechanisms.

---

## 1. Introduction

Below a threshold grind, the extraction yield of an espresso shot stops rising
with fineness and can fall, even though the specific surface area keeps
increasing; every homogeneous-flow extraction model predicts a monotone rise
(cameron2020, their Fig. 5). The phenomenon is usually attributed to one of a
small set of mechanisms — channeling, incomplete wetting, a dissolution–flow
instability, size-exclusion of extractable inventory, or simply "flow
inhomogeneity" — but the mechanisms have not been run head-to-head against the
same external constraint, and the anomaly itself is weak enough that a mechanism
can appear to "reproduce" it for reasons that do not survive scrutiny.

Two confounds deserve stating up front. First, the reference grind axis is a
grinder *dial*, and the dial is non-monotonic in particle size: in the schmieder
dataset the middle dial (GL 1.7) is the *finest* by Sauter diameter (26.9 µm vs
28.3/29.2 µm at 1.4/2.0), so a "peak at GL 1.7" is a dial statement, not a
particle-size fine-grind dip. Second, brew pressure varies with grind at fixed
flow, so the grind axis is confounded with pressure. A discrimination that ignores
these will mistake an artifact for a mechanism.

Our contribution is threefold. (i) A registry-based discrimination that enforces
matched observables and honest evidence tiers, and that — after a data-schema
correction — downgrades the fine-grind result from "the anomaly is channeling" to
"static heterogeneity is the only implemented model class *able* to generate the
response, though not identified". (ii) A null-first flow ladder that separates what
a machine-only model already explains from what genuinely requires a bed
mechanism, with a cross-pressure test that finds no universal winner. (iii) A
model-limit discovery: naively coupling the heterogeneity ensemble to an evolving
permeability is linearly unstable in a way we characterize in closed form.

## 2. Methods — the registry as an experimental apparatus

Each candidate is a component with typed stage-contracts, explicit assumptions and
validity ranges, and — where available — named validation gates. A load-bearing
element is the validation-strength vocabulary: *independent* (prediction against
genuinely unused data), *post-fit reconstruction* (source data reproduced with
fitted parameters), *verification* (numerical/analytical self-consistency), and
*qualitative* (shape/mechanism discrimination). We do not claim universal
real-data gating: some components carry only verification or qualitative gates,
and one (the static streamtube) carries none — the manuscript states this rather
than implying every model is data-validated. A passing regression gate is software
reproducibility, not scientific validation, and the two are kept separate.

The correction that motivates §3 promotes a second discipline to a rule: **no
silent observable merge**. The schmieder cup masses are per-solute and mixed-unit
(trigonelline, caffeine, 5-CQA in mg; total dissolved solids in g), reported
separately for three brew ratios and modelled with temperature as a distinct
predictor. Averaging across any of these yields a quantity with no coherent unit.
The corrected data adapter refuses to aggregate across component, unit, brew
ratio, or temperature.

Datasets: schmieder2023 (cup composition and its response surface), waszkiewicz2025
(eleven pressure traces + a static calibration), cameron2020 (a homogeneous
extraction solver), romancorrochano2017 (extractable inventory), lee2023
(dissolution–flow feedback). Each is provenanced with a manifest row carrying its
units, license, and validation strength.

## 3. Result 1 — model-capacity discrimination (Fig. 1, Fig. 2)

**The target, per observable.** We take total-dissolved-solids extraction yield
(EY = TDS cup mass / dose) as the primary observable, since it is the yield
quantity an extraction model produces. At the fixed central condition the measured
EY grind response is monotone increasing (18.3, 19.4, 19.6% at dial 1.4/1.7/2.0;
Fig. 1a). An interior grind maximum exists only in the study's own fitted response
surface, which is concave in grind (negative quadratic coefficient) with a vertex
inside the dial range for every observable — but the fit is weak (adjusted R²
0.41–0.75) and, evaluated at the measured conditions, the surface over-predicts the
absolute cup mass by ~1.7× (its temperature-squared term alone exceeds the whole
cup mass). We therefore use the response surface for *shape* only, never absolute
magnitude, and compare magnitudes on the measured cells.

**Model capacity.** A static-heterogeneity streamtube ensemble represents
permeability heterogeneity as a unit-mean lognormal; because the yield response is
concave in permeability, heterogeneity lowers ensemble yield (a Jensen
inequality), and a grind-dependent width closure converts the monotone homogeneous
response into a peaked ensemble response (Fig. 1b). Of the four implemented
generators, this is the only one that *can generate* an interior maximum without a
doctored constant: the dissolution-instability model (lee2023) produces the shape
only under a saturation ceiling set to twice the measured value; size-exclusion
inventory and pure diffusion are structurally monotone; incomplete wetting is
unimplemented (it lives in the open unsaturated-flow gap and is discriminated by
first-drip delay, not by yield shape). We present this as an evidence matrix
(Fig. 2), not a winner scoreboard.

**Why this is capacity, not identification.** Three facts prevent a stronger
claim. The width closure was calibrated on the same phenomenon (cameron's
grind-deviation data), so reproducing a grind non-monotonicity is partly circular.
A closure-sensitivity sweep finds the interior maximum is real and numerically
converged at the calibrated closure but *fragile* — present in only ~40% of the
closure-parameter grid, and absent for weak channeling — and *weak* (median
prominence ~0.14 yield-points; ~0.03 near-flat at 9 bar, with the peak grind
drifting with pressure). A magnitude comparison on the measured cells shows the
model's interior bump sits **below the replicate noise floor** (~0.22 yield-points),
while the raw data shows no bump at all. Neither side has a strong peak to match or
miss. The defensible statement is: among implemented generators, static
heterogeneity is the only viable one under its registered parameterization;
incomplete wetting remains untested; identification requires a first-drip-delay or
spatially-resolved discriminator.

## 4. Result 2 — a null-first κ(t) ladder and a regime-dependent discriminator (Fig. 3)

**The null that must be beaten first.** A machine-only model (pump + headspace,
zero bed mechanisms; foster2025) reconstructs the mid-shot flow minimum on the
digitized trace (Fig. 3a). The familiar "flow dips then recovers" observation
therefore carries no evidential weight for any bed-side story on its own; we
present it as a separate early-shot demonstration (post-fit reconstruction), not as
a nested model rejected on the saturated trace.

**The 9-bar ladder, scoped.** On the waszkiewicz rising-flow trace, a constant
permeability and a static pressure-dependent permeability are observationally
identical at fixed pressure (RMSE 0.603 g/s each), because a static
pressure-dependence contains no time structure; a dissolution-linked time-varying
porosity trajectory beats that floor 5.4× (RMSE 0.113; Fig. 3b). Within the tested
window and baselines, a time-varying bed mechanism is *required* and
dissolution-driven porosity growth is *sufficient* — but not uniquely identified,
and the trajectory is soft-circular (dissolved mass is derived from the same rig's
TDS and flow).

**Cross-pressure — no universal winner.** With a single fixed calibration we
predict all eleven pressures out of sample (Fig. 3c). The result is
regime-dependent: the empirical dissolution trajectory has the best out-of-sample
mean but a flow-coupled variant wins at low pressure and the static null wins in
the mid-range. This is within-rig generalization (the equilibrium constants were
fit across the same eleven-pressure campaign), not external validation, and it is
more informative than a single winner would be.

**The composition attempt fails honestly (Fig. 4).** The registered
shared-porosity synthesis reduces exactly to the poroelastic rung when only
extraction drives porosity; adding a parameter-free swelling branch *over-closes*
the porosity, flattening the predicted flow (residual 0.648 g/s, worse than the
0.603 flat null). We report this as a branch-compatibility diagnostic — the
parameter-free swelling branch, imported from a fixed-pressure rig, does not apply
to the saturated pre-wet rig — not as a successful full coupling. The 14× flow rise
that the ladder requires can be reconstructed from the adopted porosity trajectory
only through a near-choke poroelastic closure; the auxiliary Kozeny–Carman relation
is too gentle for that specific reconstruction (we do not claim it is physically
invalid for espresso beds in general).

## 5. Result 3 — coupling the two: an uncoupled-streamtube instability (Fig. 5)

Results 1 and 2 supply a static heterogeneity mechanism and an evolving-porosity
mechanism; it is natural to ask what happens when each streamtube carries its own
extraction-driven permeability clock — the per-tube observable a single flow trace
cannot resolve. We build this with grounded scales only (heterogeneity from the
calibrated closure, the extraction clock from the empirical dissolved-mass curve,
the per-tube conductance from the poroelastic closure) as an exploratory
construction, not a registered component.

**Result, scoped.** In the tested near-choke configuration under flow control, the
flow concentrates into a single effective channel within a few seconds — measured
directly by the maximum single-tube share (→1.0) and the effective channel count
(1/Σsᵢ² → 1.0 of the tubes), not inferred from a decile. The gentle Kozeny–Carman
closure stays bounded (effective channels ≈ 110 of 120).

**A closed-form stability criterion.** Linearizing about the uniform state, a
perturbation to one tube's extraction age amplifies over the shot by the
end-to-start conductance ratio, A = (M(φ_max)/M(φ₀))^(1−λ), where λ is the lateral
coupling. For the poroelastic closure M→0 at the near-choke shutoff, so A diverges
(A ≈ 10¹²; linearly unstable); for Kozeny–Carman A ≈ 1.5 (stable). The numerics
match this classification exactly (Fig. 5b). The very near-choke sensitivity that
Result 2 established as *required* for the whole-bed flow rise is thus what
destabilizes the per-tube ensemble.

**What controls it.** A phase map over grind × lateral coupling × control mode
(Fig. 5a) shows the single-channel latch is confined to one corner — flow control
with zero lateral coupling — and is closure-driven, not heterogeneity-driven. Under
pressure control (independent tubes, no shared flow to steal) there is no latch
(effective channels ≈ 84); any lateral coupling ≥ 0.3 also suppresses it. We do
**not** claim an unconditional instability (there is no sweep over every admissible
parameter and no theorem), and the lateral term is a homogenizing proxy, not a
physical transverse-Darcy exchange. The finding is that the parallel,
non-exchanging streamtube assumption becomes inadmissible once permeability
evolves under flow control, and it motivates a physically-derived lateral-coupling
closure.

## 6. Discussion

The through-line is that **integrated observables erase the structure needed to
discriminate mechanisms**. A whole-cup endpoint hides the inventory–kinetics
separation (the companion identifiability study); a single pressure trace leaves
several time-dependent bed mechanisms partially degenerate (Result 2); and a model
suggests that spatially-resolved flow would be far more discriminating than any
integrated trace (Result 3). Crucially, the per-tube "observations" of Result 3 are
*simulated*: the work **motivates** spatial observables, it does not provide them.

For the practitioner-facing anomaly, the honest statement is weaker than "the
fine-grind dip is flow heterogeneity": static flow heterogeneity remains a viable
candidate generator of the fine-grind response, pending a corrected observable
analysis and direct spatial or first-drip validation. We refrain from asserting a
flow-controlled versus pressure-controlled distinction for the *physical* shot
until both control modes are measured, though the model is unambiguous that they
differ.

## 7. Open gaps this paper defines

- **Lateral tube coupling.** A physical transverse-Darcy (or reduced-network)
  exchange closure and the stability boundary in terms of lateral conductance vs
  axial near-choke sensitivity. The phase map and closed-form criterion here are
  the starting point.
- **Unsaturated-flow constitutive data.** A saturation-resolved retention curve
  and relative-permeability for a coffee bed, without which incomplete wetting
  cannot be instrumented (a reference-strength glass-bead analog exists; the
  coffee measurement does not).
- **A discriminating observable for Result 1.** Per-grind first-drip timing, which
  the wetting mechanism moves and static channeling does not.

---

## Status & to-do (not for the manuscript body)

- **Ready:** Results 1–3 analyses + Figs 1–5 (draft-quality), all gated/committed.
- **Needs writing:** related work / novelty positioning (verify no prior
  head-to-head comparison before claiming it); journal-specific framing.
- **Needs rendering polish:** LaTeX captions, journal column sizing.
- **Companion:** Paper A (extraction identifiability) is a separate track
  (`ANALYSIS_transfer.md`), cited here only for the shared theme.

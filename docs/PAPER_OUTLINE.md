# Paper assembly — outline & readiness audit (rev. 2026-07-12)

*CHAT deliverable. **Revised after a detailed review**
(`docs/puckworks_paper_outline_review.md`), which is adopted: it found Result 1's
target dimensionally invalid, Result 2's Fig 4 based on a superseded formulation,
and Result 3 overstated. Those defects have since been fixed in code/docs (see
ROADMAP §7.1, 2026-07-12) and the claims below are the corrected, defensible
ones. Validation-strength tags (ROADMAP §0) are load-bearing and control the
verbs (see the verb table in §3). This file is the plan, not a manuscript.*

**Verb discipline (from the review).** Independent → "shows / predicts held-out
data". Post-fit → "reconstructs / is consistent with". Qualitative discrimination
→ "can generate / does not generate under the tested parameterization".
Exploratory synthesis → "exhibits in the tested configuration / motivates". NOT
supported here → "identifies / proves / is the mechanism / unconditionally".

## 0. How many papers?

Two independent papers plus a possible methods note. The split is endorsed by the
review. **Finish Paper A first** — its evidentiary chain is much stronger.

| | Paper A (extraction / identifiability) | Paper B (flow / bed-dynamics) |
|---|---|---|
| thesis | single-grind whole-cup data cannot separate inventory from kinetics; fractions restore the rate | **mechanism discrimination + model-hierarchy limits** for the fine-grind response and time-dependent flow (NOT "the anomaly is a channeling instability") |
| status | draft exists (`ANALYSIS_transfer.md`); **amber–green** | outline below; **not manuscript-ready — needs reanalysis, not just prose/figures** |
| core data | angeloni2023 (independent), schmieder2023 fractions | schmieder2023 RSM (per observable), waszkiewicz2025 traces, cameron2020, romancorrochano2017 |
| core result | flat valley (G6); fractions resolve it | model-capacity discrimination + null-first κ(t) ladder + regime-dependent cross-pressure + an exploratory concentration result (G-lat) |
| venue feel | food-analytical / chemometrics | transport in porous media / applied math (Foster–Moroney lineage) |

A short **methods note** on the registry (typed contracts, validation-strength
vocabulary, no-silent-constant-merge, and now **no-silent-observable-merge**)
could stand alone or be the shared Methods spine. Defer it.

---

# Paper B — mechanism discrimination for the fine-grind espresso anomaly

*Working title (review-endorsed): **"Mechanism discrimination for the fine-grind
espresso extraction anomaly and a stability test of uncoupled streamtube
models."** Do NOT use "the fine-grind flow anomaly is a channeling instability" —
it conflates an extraction-yield-vs-grind anomaly with a flow-history anomaly, and
conflates the static Result-1 mechanism with the numerical Result-3 concentration.*

## Abstract (corrected claim skeleton)

Espresso extraction changes non-monotonically with grind in ways homogeneous-flow
models do not capture. Using a component registry in which each candidate is an
independently-gated model, we test which model *classes* can generate the observed
response. After enforcing **matched observables** (a data-schema fix — schmieder's
cup masses mix mg solutes and g TDS across brew ratios and must never be averaged
together) and validation-strength labels: of the implemented response generators,
an empirically-calibrated static-heterogeneity closure is the only one that can
generate an interior grind maximum without a doctored constant — a **viability**
result, not identification (the target is a weak-R² empirical RSM feature and the
closure is itself grind-calibrated; incomplete wetting is untested). On a 9-bar
rising-flow trace a **null-first** ladder shows a time-varying porosity trajectory
is required to beat the specified flat baselines and empirical dissolution-linked
Φ(t) is sufficient (not uniquely identified); across 11 pressures the mechanisms
are **regime-dependent with no universal winner**. Finally, an exploratory
uncoupled-streamtube extension exhibits, **in the tested near-choke
configuration**, flow concentration into a single effective channel, motivating a
physically-derived lateral-coupling model. The unifying theme: integrated
observables erase the structure needed to discriminate mechanisms.

## 1. Introduction
- The anomaly, stated carefully: extraction/cup composition changes with grind in
  a way homogeneous models miss; schmieder report a concave grind term in their
  RSM. Note the confound the registry surfaces: schmieder's dial is **non-monotonic
  in particle size** (GL 1.7 is the finest d₃₂), and pressure varies with grind at
  fixed flow — so "peak at GL 1.7" is a dial statement, not a clean fine-grind dip.
- Five standing hypotheses (P3 registry); prior work asserts one without a
  head-to-head test **(verify novelty in related work before claiming this)**.
- Contribution: registry-based discrimination with matched observables and honest
  evidence tiers; a null-first flow ladder; and a model-limit discovery.

## 2. Methods — the registry as an experimental apparatus
- Typed stage contracts; provenance, assumptions, validity ranges; validation-
  strength vocabulary. **Honest scope (review):** components carry provenance and
  *where available* named gates ranging from numerical verification to independent
  comparison — NOT "every model has a real-data gate" (e.g. `brewer2026.streamtube`
  has no `gates=`). A passing QUICK gate is software regression, not validation.
- **No silent observable merge** (new rule, promoted from the Schmieder bug): never
  aggregate across component, unit, brew ratio, or temperature. Enforced in
  `harness.schmieder_grind_response` (raises on mixed units).
- Datasets + the observable/unit contract for each; manifest rows.

## 3. Result 1 — model-capacity discrimination (corrected target)
*(gate_p3_schmieder_peak_discrimination, schmieder_interior_max_target. Strength:
qualitative / model-capacity.)*
- **Target = TDS-derived EY (primary), per observable (not a mixed-unit average).**
  EY = TDS cup mass / 20 g dose · 100 — the yield quantity the model outputs
  (`harness.schmieder_tds_ey`). schmieder's own RSM is concave in grind (β₅<0)
  with an interior vertex for all four observables — but weak (adj-R² 0.41–0.75),
  and the raw TDS-EY grind response at the fixed condition is **monotone
  increasing** (18.3 → 19.4 → 19.6 %); interior max for ≤1/4 across observables.
  Report shape AND magnitude AND uncertainty; do not infer a peak from an argmax.
- **Capacity result.** Of the implemented generators, only the empirically-
  calibrated static-heterogeneity closure produces an interior maximum without a
  doctored constant; lee needs ρ_c=798; size-exclusion/diffusion are monotone;
  incomplete wetting is unimplemented. Flag the σ-calibration circularity (σ was
  fit to cameron grind-deviation data).
- **Closure sensitivity — DONE** (`channeling_interior_max_sensitivity`,
  validation/slow). The interior-max is real and n_grid-converged at the
  calibrated closure but **fragile** (interior in only 40 % of the s_ref × m grid;
  gone for weak channeling) and **weak** (median prominence ~0.14 EY-pt; ~0.03 —
  near-flat — at 9 bar, with the peak grind drifting with pressure). The model
  side is a shallow closure-dependent bump, mirroring the weak-RSM/monotone-raw
  target side. Consequence: the title/abstract must not rest on a channeling peak.
- **Fig 1** — the PRIMARY TDS-EY target: raw replicate EY points at fixed
  flow/BR/temperature (18.3/19.4/19.6 % with error bars), the schmieder RSM EY
  curve (interior vertex 1.75, adj-R² 0.64 annotated), and a separate panel for
  the normalized model EY response. Do NOT overlay mixed-unit masses with EY.
- **Fig 2** — mechanism **evidence matrix** (not a winner scoreboard): implemented?
  · observable matched? · parameters independently constrained? · generates peak? ·
  evidence strength · unresolved discriminating experiment.

## 4. Result 2 — null-first κ(t) ladder + regime-dependent cross-pressure
*(gate_p2_kappa_ladder, gate_foster_fig15_flowmin, gate_p2_cross_pressure. Strength:
post-fit at 9 bar; cross-pressure = within-rig generalization, not external.)*
- **The null that must be beaten first.** Foster machine mode (pump+headspace,
  post-fit reconstruction) independently produces a dip-and-recovery, so that
  signature alone identifies no bed mechanism. Present it as a *separate* early-shot
  demonstration — NOT nested/rejected on the same 15–115 s Waszkiewicz trace.
- **The 9-bar ladder, scoped.** Within the tested window and flat baselines, a
  time-varying porosity trajectory is required and empirical dissolution-linked
  Φ(t) is sufficient (beats the floor ~5.4×) — *not uniquely identified*, and the
  Φ(t) trajectory is soft-circular (m_d from TDS+flow on the same rig).
- **Cross-pressure is DONE (not pending).** One fixed calibration → predict all 11
  pressures: **regime-dependent, no universal winner** (Φ(t) best OOS mean; RC-3b
  low-P; static mid-P). Promote to main text; label within-rig generalization.
- **Poroelastic scope.** "The tested 14× rise cannot be reconstructed from the
  adopted porosity trajectory with the auxiliary Kozeny–Carman relation; the
  near-choke poroelastic closure supplies the required sensitivity." Do NOT claim
  CK is physically invalid for espresso beds.
- **Fig 3** — three panels: Foster early-shot machine-only (labelled post-fit); the
  9-bar ladder; a pressure×mechanism residual heat map.
- **Fig 4** — the **shared-porosity composition diagnostic** (registered
  `brewer2026.coupled_kappa_t`), NOT the superseded multiplicative harness: show
  extraction-only reduction, extraction+swelling composite, observed trace, flat
  baseline, and the FAILED composite residual (~0.648 > ~0.603 null — swelling
  over-closes). An honest branch-compatibility test, not a success plot.

## 5. Result 3 — uncoupled streamtube extension (exploratory)
*(gate_ntube_kappa_t_union. Strength: exploratory synthesis / qualitative. Belongs
in an exploratory section or appendix — NOT "ready, only Fig 5 remaining".)*
- Construction: each streamtube gets its own extraction-driven κ(t) clock; grounded
  scales; NOT a registered component.
- **Result, scoped.** In the *tested near-choke configuration* (gs 1.1, 9 bar,
  N=200, poroelastic), flow concentrates into a single effective channel — measured
  by max single-tube share → 1.0 and N_eff = 1/Σsᵢ² → 1.0 (not a top-decile
  inference); the gentle Kozeny–Carman closure stays bounded (N_eff ~110). EY flow
  and EY response now at the SAME pressure (the earlier 9-bar-flow/5-bar-EY mismatch
  is fixed → 15.1%→2.4%). A homogenizing regularizer (a proxy, not a transverse-
  Darcy term) suppresses it.
- **Not established (do not claim):** unconditional instability (no sweep over
  grind/pressure/closure-slope/flow-vs-pressure control/tube count/clock; no
  stability theorem); that lateral pressure equalization specifically is the cure.
- **Work list before this is a headline (review §7):** derive a physical lateral-
  exchange model; linear-stability analysis about uniform flow; a phase diagram
  over the parameters above; alternative clocks + donor-uncertainty; converged
  integration; single-tube/effective-channel metrics (done); distinguish model
  instability from experimentally-observed channeling.
- **Fig 5** — a **stability map** (phase boundary vs lateral conductance and
  near-choke sensitivity; flow- vs pressure-control; N_eff/max-share;
  convergence/tube-count checks; representative trajectories), not three curves.

## 6. Discussion
- Unifying theme (the real thesis): **integrated observables erase discriminating
  structure** — whole-cup endpoints hide inventory↔kinetics (Paper A), one pressure
  trace leaves κ(t) mechanisms partly degenerate (Result 2), and a model suggests
  spatially-resolved flow would discriminate (Result 3). Result 3's per-tube data
  are *simulated*, so it **motivates** spatial observables, it does not provide them.
- Barista-facing, weakened: "static flow heterogeneity remains a viable candidate
  generator of the fine-grind response, pending a corrected observable analysis and
  direct spatial validation" — NOT "the fine-grind dip is flow heterogeneity."
- Do not assert a flow-controlled vs pressure-controlled distinction until both are
  simulated in the dynamic model.

## 7. Open gaps this paper defines
- **G-lat** — physical lateral tube coupling + the stability boundary (vs axial
  near-choke sensitivity). **G1** — coffee-bed retention curve θ(ψ)+K_r for the
  wetting model (#2; search-target card exists). *(Cross-pressure completion is
  DONE — removed from this list per the review.)*

---

## Readiness audit (adopts the review's revised judgment)

| element | status | requirement before submission |
|---|---|---|
| Two-paper division | **sound** | — |
| Paper A core identifiability | **amber–green** | manuscript conversion: Methods, uncertainty, related work, reproducibility package |
| Paper B framing/title | **red** | separate extraction anomaly / flow-trace result / model concentration; retitle (done above) |
| Schmieder target | **fixed** (was red/blocking) | corrected per-observable RSM + raw + uncertainty; guard added |
| Result 1 (capacity) | **amber** | ✅ closure sensitivity done (fragile 40 %, weak, converged); still: magnitude vs RSM + state circularity (both now in §3) |
| Result 2 9-bar ladder | **amber** | narrow to tested nulls/window; expose same-rig soft circularity |
| Cross-pressure | **amber** | report the completed regime-dependent result; stop calling it pending/fully-independent |
| Coupled κ(t) / Fig 4 | **fixed** (was red) | use shared-porosity component; report the failed composite; card status corrected |
| Result 3 (N-tube) | **red/amber exploratory** | pressure fix (done); physical lateral model; stability analysis + parameter sweep |
| Registry Methods | **amber** | correct universal-gate claim (done in §2); add observable/unit contracts; pin a commit |
| Related work / novelty | **red** | complete before claiming no prior head-to-head comparison |
| Figures | **red** | generate only after the analyses above; render none yet |
| Overall Paper B | **not submission-ready** | scientific reanalysis, not just prose + rendering |

## Priority revision sequence (from the review)

1. ✅ **Schmieder adapter fixed** + observable/unit guard added; old P3 gate
   rewritten to the corrected target (done 2026-07-12).
2. **Recompute Result 1** for a matched observable — ✅ TDS-EY primary target +
   replicate uncertainty + peak-prominence (done 2026-07-12) and ✅ closure
   sensitivity (fragile 40 %, weak, converged; validation/slow). Remaining: the
   magnitude-vs-RSM comparison, then fix the title/abstract (which the sensitivity
   confirms must NOT rest on a channeling peak).
3. ✅ **Coupled-κ lineage reconciled**: card status corrected; Fig 4 must use the
   shared-porosity component's failed composite (done 2026-07-12).
4. **Rewrite Result 2 prose** around its actual evidence: the 9-bar ladder, soft
   circularity, and the completed regime-dependent cross-pressure.
5. **Repair + deepen Result 3**: ✅ pressure fix + proper metrics done; still need a
   physical lateral-coupling model + a linear-stability analysis + a phase diagram.
6. **Only then** generate figures, write the abstract, complete related work; pin
   the exact commit for every manuscript number.

**"Results 1–3 need no further computation" is deleted.** Result 1 needs a
matched-observable reanalysis; Result 2 needs regenerated outputs from the
registered synthesis; Result 3 needs real stability work. Finish Paper A first.

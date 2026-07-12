# Paper assembly — outline & readiness audit

*CHAT deliverable. Draws only on committed, gated results (each claim below cites
its gate or slow script). Validation-strength tags (ROADMAP §0) are load-bearing
and must survive into any manuscript: most extraction agreements are **post-fit
reconstruction**, the mechanism-discrimination results are **qualitative**, and
nothing here is promoted. This file is the plan; it is not itself a manuscript.*

## 0. How many papers?

The committed body of work splits cleanly into **two independent papers** plus a
possible **methods note**. They share the registry infrastructure but have
disjoint theses, data, and audiences — bundling them would blunt both.

| | Paper A (extraction / identifiability) | Paper B (flow / bed-dynamics) |
|---|---|---|
| thesis | single-grind whole-cup data cannot separate inventory from kinetics | the fine-grind flow anomaly is a channeling instability, and coupling it to κ(t) is only well-posed with lateral coupling |
| status | **draft exists** (`ANALYSIS_transfer.md`, paper-track) | **outline below** (this file) |
| core data | angeloni2023 (independent), schmieder2023 fractions | schmieder2023 cup mass, waszkiewicz2025 traces, cameron2020, romancorrochano2017 |
| core result | flat valley (G6); fractions resolve it | P3 verdict (channeling) + κ(t) ladder + N-tube instability (G-lat) |
| venue feel | food-analytical / chemometrics | transport in porous media / applied math (Foster–Moroney lineage) |

A short **methods note** on the registry itself (typed contracts, validation-
strength vocabulary, gate-per-component, no-silent-constant-merge) could stand
alone or become the "Methods" spine both papers cite. Recommend: finish A (nearly
there), assemble B from the outline below, defer the methods note.

---

# Paper B — "The fine-grind flow anomaly is a channeling instability"

*(working title: "Channeling, not kinetics: a null-first discrimination of the
fine-grind extraction anomaly in espresso, and why coupled permeability evolution
needs lateral tube coupling")*

## Abstract (claim skeleton)

Below a grind threshold, espresso extraction yield *drops* as the grind gets
finer while every homogeneous-flow model predicts it should keep rising. We ask
which of five proposed mechanisms actually reproduces the anomaly, using a
component registry in which each candidate is an independently-gated model rather
than a tuned term in a monolith. Against schmieder2023's non-monotonic cup-mass
signature, **only static channeling reproduces an interior grind maximum from
physical parameters**; a dissolution-instability model needs an unphysical
saturation ceiling, and inventory/diffusion mechanisms are structurally monotone.
Separately, on a rising-flow pressure trace, a **null-first** ladder shows a
time-dependent bed mechanism is required and dissolution-driven porosity growth
is sufficient — but only through a **near-choke poroelastic** permeability
closure, not Kozeny–Carman. Finally, uniting the two — giving each channeling
streamtube its own extraction-driven permeability clock — is **unconditionally
unstable** under flow control: flow latches into a single channel unless lateral
pressure equalization between tubes is added. We conclude the static channeling
ensemble is the right tool for the time-averaged dip, and that lateral coupling
is a stability *requirement*, not a refinement, for any dynamic upgrade.

## 1. Introduction
- The anomaly: EY rises with fineness (more surface) until ~GS 1.7, then falls
  (cameron2020 Fig 5 deviations 13.1/6.1/2.6% at GS 1.1/1.3/1.5). Homogeneous
  models keep rising.
- Five standing hypotheses (P3 registry): channeling, incomplete wetting,
  dissolution–flow instability, size-exclusion inventory, flow-inhomogeneity
  pointer. Prior literature asserts one; none had been run head-to-head against
  the same external constraint.
- Contribution: a registry-based **discrimination** (not a fit), three results,
  one negative/instability finding that defines a new gap.

## 2. Methods — the registry as an experimental apparatus
- Typed stage contracts; each model carries provenance, assumptions, validity
  range, and ≥1 gate to real data. Validation-strength vocabulary (independent ·
  post-fit reconstruction · verification · qualitative) — and why it matters here
  (most agreements are post-fit; the discrimination results are qualitative).
- Datasets: schmieder2023 (cup mass vs grind × flow), waszkiewicz2025 (11
  pressure traces), cameron2020 (homogeneous solver), romancorrochano2017
  (tamped κ, y₀ inventory), grindmap (⟨R⟩/S, φ₁). Each with its manifest row.
- Key methodological rule surfaced as a result: **dial spaces are non-portable**
  (rule 9) → the discrimination compares response SHAPE, never dial location.

## 3. Result 1 — the fine-grind dip is a channeling phenomenon
*(gate_p3_schmieder_peak_discrimination, harness.schmieder_peak_discrimination;
gate_p3_channeling_sigma_sweep. Strength: qualitative / mechanism-discrimination.)*
- The target, stated honestly: schmieder cup mass is non-monotonic in grind with
  an interior peak at GL 1.7 — **real but weak** (~1 g/97 g), unambiguous only at
  the lowest flow (flow 2 monotone, flow 3 marginal). No flow-washout overclaim.
- Scoreboard (interior maximum? from physical params?): channeling **yes/yes**;
  lee2023 yes but only at doctored ρ_c=798; size-exclusion y₀ monotone; diffusion
  null monotone. **Only channeling** reproduces it physically.
- Mechanism: a monotone σ(grind) closure through the fines fraction feeds the
  streamtube EY-deficit (Jensen/concavity) → the deficit is largest at the finest
  grind, so channeling ALONE turns a monotone base EY into a peaked ensemble EY.
- Does not exclude incomplete wetting (#2): it lives in the open G1
  continuous-saturation gap and is discriminated by first-drip DELAY, not EY
  shape (the wetting-atom probe, qualitative). #1 and #2 non-exclusive.
- **Fig 1**: base vs ensemble EY(grind) with the σ(φ₁) closure (the peak forming).
- **Fig 2**: the four-mechanism scoreboard (interior-peak × physical) table/panel.

## 4. Result 2 — a null-first κ(t) ladder on rising flow
*(gate_p2_kappa_ladder, gate_foster_fig15_flowmin, gate_p2_cross_pressure,
gate_coupled_kappa_t. Strength: post-fit at 9 bar; the cross-pressure test is the
would-be independent discriminator.)*
- **The null that must be beaten first**: foster machine mode (pump + headspace,
  zero bed mechanisms) reproduces the mid-shot flow minimum (RMSE 1e-4 vs Fig 15)
  → "flow dips then recovers" carries no bed-side evidential weight alone.
- The ladder on waszkiewicz 9-bar: constant κ 0.603 = static κ(P) 0.603 (a
  static P-dependence is observationally a constant at fixed P) ≪ dissolution
  Φ(t) 0.113 (beats the floor 5.4×). **Time-dependent bed required; Φ(t)
  sufficient.** Sufficient ≠ unique.
- **The closure matters**: the 14× flow rise on a small porosity change happens
  because the bed is near-choke, where κ is hypersensitive to ε — the
  **poroelastic** closure is required; Kozeny–Carman is far too gentle (RMSE ~1.5
  vs 0.116). This is the pivot for Result 3.
- Cross-pressure generalization as the honest discriminator (11 pressures; fit at
  9, predict the rest) — report what it does/doesn't separate.
- **Fig 3**: the ladder (RMSE bars) + the null. **Fig 4**: κ/κ₀(t) non-monotone
  trajectory (swelling-closes-then-extraction-opens).

## 5. Result 3 — uniting channeling and κ(t): an unconditional instability
*(gate_ntube_kappa_t_union, harness.ntube_kappa_t_union. Strength: exploratory
synthesis / qualitative. THE new finding.)*
- Construction: each parallel streamtube gets its own extraction-driven κ(t)
  clock — grounded scales only (σ(gs) calibrated, clock = empirical m_d(t),
  conductance M(φ) = poroelastic Q(φ)); no invented parameters. NOT a registered
  component.
- Result: under flow control the poroelastic coupling is **unconditionally
  unstable** — flow latches into a single channel within ~3 s (top-decile share
  0.31→~1.0), EY collapses 16%→2.5% (the gushing-channel disaster).
- Three controls make it a finding, not an artifact: (i) the gentle Kozeny–Carman
  closure does NOT run away → it is the *near-choke sensitivity* (the same
  property Result 2 proved required) that destabilizes the ensemble; (ii)
  step-size invariant; (iii) a lateral pressure-equalization term regularizes it.
- Conclusion / new gap **G-lat**: a dynamic channeling-κ(t) model cannot use
  independent streamtubes — lateral coupling is a *stability requirement*. The
  static ensemble is the correct tool for the time-averaged dip (Result 1); the
  naive dynamic upgrade is diagnostic only.
- **Fig 5**: top-decile flow share vs time, poroelastic (runaway) vs CK (bounded)
  vs poroelastic+lateral (regularized).

## 6. Discussion
- Why "sufficient ≠ identified" recurs (ties to Paper A's identifiability limit):
  a single flow trace (Result 2) and a whole-cup value (Paper A) both integrate
  away the structure that discriminates mechanisms; per-tube (Result 3) and
  fraction-resolved (Paper A §6) observables are what separate them.
- Practical reading for the barista-facing anomaly: the fine-grind dip is flow
  heterogeneity, and it is a *flow-controlled* instability (pump/DE1 regime),
  distinct from a pressure-controlled shot.
- Limits (stated, not hedged): schmieder peak is weak; the σ(φ₁) closure is
  empirical over a calibrated domain; the union is exploratory with unvalidated
  donor branches; incomplete wetting (#2) remains open in G1.

## 7. Open gaps this paper defines
- **G-lat** — lateral tube coupling (stability boundary vs axial near-choke
  sensitivity). **G1** — coffee-bed retention curve θ(ψ)+K_r for the wetting
  model (search-target card exists). Cross-pressure discrimination completion.

---

## Readiness audit (what is manuscript-ready vs needs work)

| element | status | needs before submission |
|---|---|---|
| Result 1 (P3 verdict) | **ready** — gated, reproducible | prose + Figs 1–2 rendered from harness |
| Result 2 (κ(t) ladder + null) | **ready** — gated | cross-pressure §4 tightened; Fig 3–4 |
| Result 3 (N-tube instability) | **ready** — gated, 3 controls | Fig 5; frame as finding+gap, not a model |
| Methods / registry §2 | **ready** — code is the spec | condense to a figure + table |
| Fig generation | **not started** | all five figs (harnesses already emit the arrays) |
| Related work | **not started** | position vs Foster/Moroney, cameron, waszkiewicz |
| Paper A (transfer) | **draft exists** | independent track; finish separately |

**Recommended next build steps** (in order): (1) render Figs 1–5 from the
existing harness outputs into a `docs/figures/` set (each figure is a few lines
over an existing gate/harness call — no new physics); (2) tighten §4 cross-
pressure into a decisive-or-honest statement; (3) draft Paper B prose §1/§6 (the
framing, where the novelty is). Results 1–3 need no further computation.

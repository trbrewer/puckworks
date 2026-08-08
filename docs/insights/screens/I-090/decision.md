# I-090 Cheap Screen Decision

```
CHEAP_SCIENTIFIC_SCREEN
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

## Question

Does `first_drip_time`, measured by data already in the manifest, separate the models that
predict it by more than their within-model uncertainty?

Tension row **T-0171** (`hidden_discriminator` / `discriminator_with_data`): *"2 registered
models name first_drip_time among their interface outputs and 1 manifest dataset measures it."*

## Evidence unit

One `first_drip_time` event per **physically independent extraction**. `de1_fixtureA` is one
recorded Visualizer shot (`20210921T085910`), so the evidence unit count is 1 — established by
the audit, not assumed.

## Method

The protocol ([`PROTOCOL.md`](PROTOCOL.md), frozen and committed before the screen module
existed) runs an **observable-definition gate** (E1 same event across the two components; E2
model event equals measured event; E3 the components are rivals at all) before any discrimination
is attempted, plus an evidence and replicate audit, and permits **exactly one bounded execution**
declared as a `MECHANISM_IDENTITY_CHECK` — explicitly not a discrimination run.

**The gate fails on all three.** The screen therefore ran no discrimination, and instead
demonstrated *why* one is not available.

## Result

### 1. The pair is not a rival pair. It is a producer and its consumer.

`foster2025.machine_mode` (stage `machine`) **generates** the pressure history that
`foster2025.infiltration` (stage `infiltration`) **consumes**. Established three independent
ways, none of which relies on this screen's reading:

- **Card binding.** Both components bind to the *same* card, `docs/cards/foster2025.md`, and that
  card's Interface mapping says so verbatim: *"one card serves `foster2025.infiltration` and
  `foster2025.machine_mode`, so anything listed above is attributed to both."* So T-0171's "2
  registered models name `first_drip_time`" is **one Outputs clause counted twice**. Co-location
  is not a relationship.
- **The modules say it.** `infiltration`: *"their full pump/headspace model … matters only when
  pressure is not measured, and is left as the PUCK LAB 'machine mode' backlog item."*
  `machine_mode`: *"Complements foster2025.infiltration (which consumes a measured P(t)); this is
  the 'machine mode' that produces it."* `docs/cards/foster2025_2.md` adds: *"machine mode can be
  a separate machine-stage component emitting P(t)/Q(t) that infiltration consumes."*
- **The registry stages differ**: `machine` versus `infiltration`.

### 2. They are one front law — demonstrated, not asserted.

Both integrate `φ_T · s · ds/dt = (k/μ) · ΔP`. `machine_mode` as an ODE
(`ds/dt = f_bed/φ_T`), `infiltration` in closed form. Feeding `machine_mode`'s **own implied**
bed-top pressure `ΔP(t) = p_h(H) + p_c + ρg(H+s) − p_a` into `infiltration`'s public
`front_from_pressure` reproduces `machine_mode`'s front trajectory to:

| quadrature grid | RMSE of Δs | max |Δs| |
|---|---|---|
| 400 | 1.72 × 10⁻⁵ mm | 2.4 × 10⁻⁵ mm |
| 1600 | 1.08 × 10⁻⁶ mm | 1.5 × 10⁻⁶ mm |
| 6400 | **7.0 × 10⁻⁸ mm** | **1.2 × 10⁻⁷ mm** |

against a bed depth of 9.975 mm and the existing `gate_foster_ct_trajectory` tolerance of
0.2 mm. The frozen thresholds were RMSE < 0.01 mm and max < 0.02 mm.

**The residual falls with grid refinement, and that is the load-bearing part.** A residual that
did *not* fall would mean the two implementations genuinely differ; the clean ~4× -per-4× -grid
convergence identifies it as trapezoid quadrature error, so the agreement is an identity rather
than a coincidence of tolerance.

Consequence: the two components' first-drip predictions can differ **only** through the pressure
history supplied. That is a boundary condition, not a mechanism. `first_drip_time` cannot
discriminate a mechanism between them, because there is only one mechanism.

### 3. Three different events are called "first drip", with no validated mapping.

| | event | time origin | threshold |
|---|---|---|---|
| **A** | front reaches `z = L` (`infiltration.t_saturate`) | start of the **supplied** trace | none — exact model boundary |
| **B** | saturation in the staged ODE (`machine_mode`, `t_s + t_shift`) | model zero **+ a fitted `t_shift` = 0.796 s** | none — exact model boundary |
| **C** | first sample above 0.5 g on the DE1 scale | the fixture's elapsed-time axis | **0.5 g**, with basket/screen/spout/cup transport and scale response **uncharacterised** |

`docs/cards/foster2025.md` declares C is **not a model output**. Equating A or B with C would
require inventing a transfer model, which the protocol lists as a no-go.

### 4. The evidence cannot support a discrimination uncertainty — and that is not the binding obstacle.

**One** physically independent extraction; 100 samples *of it*. Median cadence 0.270 s, which is
**event resolution, not population variance**. No replicate spread exists; neither component
declares a numerical band on `first_drip_time` (`sign_or_compatibility` and
`source_curve_reproduction` are labels, not bands). The configuration is not fully specified
either: the grind setting is **assumed** (1.9) and κ is **fitted to this same shot** (1.196).

## Primary figure

[`figures/primary.png`](figures/primary.png). Per the candidate's own instruction, the absence of
a spread is made **visually explicit**: panel (c) draws the single-replicate measurement with no
error bar and says why none is drawn. Panel (a) is the producer/consumer chain and the one shared
card; (b) the grid-refinement identity; (d) the three events and the two missing mappings.

## Adversarial check

Eight checks (B1–B8); **none overturned the finding**. Three that mattered:

- **B3 — the shared-card rescue.** Could the implementations differ despite sharing a card?
  Tested on the **front law in each implementation**, not on prose. They do not differ. This is
  the check that could have made the pair genuine rivals, and it is why the identity was computed
  rather than argued.
- **B1 — threshold sensitivity.** The measured event moves with the detection threshold:
  6.793 s at 0.05–0.2 g, 7.018 s at 0.5 g, 7.514 s at 1.0 g, 8.775 s at 2.0 g. That is a
  **1.982 s** span, 7.3 sampling intervals — and **wider than the 1.4 s model bracket
  (6.4–7.8 s)** the existing gate compares against. The event convention moves the measured
  quantity by more than the model spread it is checked against. A single fixed threshold is the
  right choice for a gate; it does not make a threshold crossing equivalent to a model boundary
  crossing.
- **B7 — would replicates have rescued it?** **No.** The obstacles are structural. A replicate
  campaign on `de1_fixtureA` would supply a spread for an event that still has no second model to
  discriminate against. Saying so is the point: commissioning that experiment would waste it.

**B8** guards the opposite over-reading: this screen bounds **one pair**, and does not say
`first_drip_time` is worthless as a discriminator. A genuine test needs two *independent* front
closures under one recorded pressure history.

## Strongest alternative explanation

The candidate's human triage named two, and expected the second to decide the screen:

1. *the observable is defined differently by each model, so the separation is a convention
   artifact* — **partly right, and it is not the decisive fact.** The conventions do differ (B1
   quantifies how much), but the deeper problem is that there is no separation to explain away.
2. *no within-model uncertainty band can be drawn; `de1_fixtureA` is a single fixture* — **factually
   confirmed** (§4 above) and **not decisive**. It would have been the answer for a well-posed
   comparison. Here the comparison is ill-posed upstream of the uncertainty question, which is why
   the disposition is RETIRE rather than the anticipated NEEDS_NEW_DATA.

The remaining alternative — that the pair are rivals whose implementations happen to share a
lineage — is what B3 tests directly and refutes numerically.

## Decision

**RETIRE**

## Why

The two components are not rival predictors of first drip. They are sequential stages of one
pipeline, bound to one card whose Outputs clause the card itself attributes to both, sharing one
sharp-front law demonstrated to 7 × 10⁻⁸ mm. Any difference in their first-drip times is a
difference in the pressure history supplied.

Independently: the model event is not the measured event and no validated mapping exists; and
`de1_fixtureA` lies outside `machine_mode`'s declared configuration (DeLonghi EC685, 59 mm
basket, 10 g fine grind) — which cannot consume a recorded trace at all, so the matched
comparison the candidate asks for could not be constructed without a refit.

The protocol's frozen ordering rule maps this to RETIRE rather than NEEDS_NEW_DATA: the obstacles
are **structural**, and no quantity of new measurement changes them.

## Claim ceiling

A **registry finding** about how a shared-card Outputs clause generates a spurious discriminator
row, plus a **code-level identity** between two implementations.

- It does **not** upgrade either rung. `foster2025.infiltration` remains `sign_or_compatibility`;
  `foster2025.machine_mode` remains `source_curve_reproduction`.
- It does **not** convert within-campaign evidence into independent validation.
- It does **not** establish that the shared front law is **correct**. Two implementations
  agreeing is a statement about the code and the source, not about the physics.
- It does **not** establish mechanism identification in either direction.
- It does **not** validate the unresolved `de1_fixtureA` provenance condition, and does not rely
  on that condition being resolved.
- It licenses **no** reader-facing statement about first drip in espresso.

## Recorded, and deliberately not applied

The evidence audit surfaced a candidate defect and **records** it without correcting it
(`result.json → recorded_findings`, `I090-F1`):

`puckworks/data/MANIFEST.csv`, row `de1_fixtureA`, column `validation_strength`, currently
**`independent (parameter-free triangle)`** — contradicted by `docs/ROADMAP.md` §7.1's own entry
dated **2026-07-16**: *"the permeability comes from `kappa_fitted=1.196` fitted to the same DE1
fixture-A shot and the sharp front is driven by that shot's own pressure trace, so the first-drip
bracket is a wide-bracket compatibility check on **in-sample** data, **not a parameter-free
independent result**."* That entry demoted the component's `evidence_strength` for precisely this
reason, and it post-dates the 2026-07-12 entry that had kept the "foster triangle" among the
legitimate parameter-free uses.

**It is not applied**, for three reasons, and the tests assert the targets are byte-unchanged:

1. CLAUDE.md: the Insight Foundry *"is never an authority"* and *"may not change, promote or
   restate any label, badge or validation rung."*
2. I-045 set the precedent in this layer — it named three correction targets and left them
   byte-unchanged, because editing an evidence label is a separate, human-owned change.
3. The blast radius reaches `docs/ROADMAP.md` body prose, `docs/cards/foster2025.md`'s Status
   line, `docs/CORPUS_ANALYSIS_PLAN.md` and `docs/GUIDED_PULL_LABORATORY.md`. A one-cell
   correction would become a sweep.

**This screen does not adjudicate** whether `independent` is defensible under a strict reading of
ROADMAP §0 — the drip time itself was not used in fitting κ. The finding is that **two live
repository statements contradict each other and the later one is the project's own
adjudication**, not that this screen has re-derived the right rung. It is also independent of
I-045: `tests/test_screen_i045.py` asserts `de1_fixtureA` is *foreign* to that screen's row
selection.

Recommended replacement wording, for a human: *"post-fit reconstruction (in-sample: kappa fitted
to this shot; front driven by this shot's own P(t)) — per ROADMAP §7.1 2026-07-16."*

## Next action

None in this branch. The retirement is recorded in
[`../../RETIRED_CANDIDATES.md`](../../RETIRED_CANDIDATES.md) with its reopen condition.

**Reopen condition.** A **second, independent front closure** is registered and evaluated against
`foster2025.infiltration` under **one recorded pressure history** on one rig — for example
`mo2023_2`'s filling-front switch (Eqs. 29–30), which `docs/cards/mo2023_2.md` already names as
*"a cheap implementation of exactly this backlog item"*. That pair would be a genuine first-drip
discrimination, and it would then **also** need a characterised transport/instrument delay between
front breakthrough and the scale-threshold crossing, plus physically independent replicate
extractions to supply a spread. **Replicates alone do not reopen this candidate** — with no rival
pair there is nothing for a spread to discriminate.

## Reproduction

```
python -m puckworks.analysis.screen_i090_first_drip
python -m pytest tests/test_screen_i090.py -q
```

## Source commit

Base `85f65c0d4b836990152fa4e9bf91c6d292a9e257` (tree `f44eb36c27145e6068009e89fca982138a7401d1`).
`result.json` binds the SHA-256 of `PROTOCOL.md` and of every input file it read.

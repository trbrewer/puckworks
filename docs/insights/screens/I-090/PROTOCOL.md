# I-090 — first-drip discrimination protocol (FROZEN BEFORE EXECUTION)

```
CHEAP_SCIENTIFIC_SCREEN
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

**This document is committed before the screen module exists**, and it is what the screen is
bound to. It freezes the scientific question, the observable-definition gate that runs before any
discrimination is attempted, the evidence and replicate audit, the one bounded execution the
screen is permitted, the decision thresholds and paths, the adversarial checks and the claim
ceiling.

Components under comparison:

```
foster2025.infiltration    (stage: infiltration, runtime, sign_or_compatibility)
foster2025.machine_mode    (stage: machine,      runtime, source_curve_reproduction)
```

Evidence: `de1_fixtureA` (MANIFEST row 27).

---

## 1. Exact scientific question

Does a consistently defined `first_drip_time` distinguish `foster2025.infiltration` from
`foster2025.machine_mode` by more than defensible within-model and measurement uncertainty, using
the repository's declared `de1_fixtureA` evidence?

**The observable-definition gate runs first.** What each authority means by "first drip" is
determined before any discrimination is attempted, because a separation between two *definitions*
is not discrimination.

## 2. Evidence unit

One `first_drip_time` event per physically independent extraction. `de1_fixtureA` is a single
recorded shot (Visualizer fixture `20210921T085910`), so the evidence unit count is what the
audit in §4 must establish rather than assume.

**Densely sampled points within one extraction are not replicates.** A 100-sample trace of one
shot supplies event *resolution*, not population variance, and the two are not interchangeable.

## 3. The observable-definition gate

Three candidate event definitions exist in this repository, and the gate's job is to determine
whether they are the same event.

### 3a. `foster2025.infiltration` — front arrival at the bed base

`front_from_pressure(...)["t_saturate"]`: the time at which the sharp front `s(t)` reaches the
bed depth `L`, under a **recorded or prescribed** pressure history, from the closed form
`s(t) = sqrt(2k ∫₀ᵗ P dt' / (μ φ_T))`. Time origin: the start of the supplied trace. Detection
threshold: none — it is a model boundary crossing, exact by construction.

### 3b. `foster2025.machine_mode` — saturation time under a *modelled* pressure history

`reported_times()[1] = t_s + t_shift`: the saturation event of the staged pump/headspace ODE.
Time origin: the model's own `t = 0`, shifted into the experiment frame by
**`t_shift = 0.796 s`, a fitted start-time alignment** (`FosterParams.t_shift`; the module says
so: *"The authors report times shifted by a fitted start-time alignment t_shift; reported =
model + t_shift."*). This branch **generates** its pressure history from a pump characteristic
and trapped headspace; it takes no recorded `P(t)`.

### 3c. `de1_fixtureA` — first mass on the scale

`observed_first_drip_s(t, weight_g, threshold_g=0.5)`: the first sample whose recorded weight
**strictly exceeds 0.5 g**. This is an instrument event, downstream of basket, screen, spout and
cup, with a detection threshold and a sampling cadence, and with **no transport or
instrumentation delay characterised anywhere in the repository**.

`docs/cards/foster2025.md` declares this one is not a model output, verbatim:
*"`infiltration.observed_first_drip_s` is the measurement-side comparator (first crossing of a
0.5 g scale threshold), **NOT a model output**."*

### 3d. What the gate must establish

- **E1 — is 3a the same event as 3b?** Same physical event (front reaches `z = L`)? Same time
  origin? Same driving pressure history?
- **E2 — is the model event the same as the measured event 3c?** Front breakthrough at a model
  boundary is **not** first registered scale mass unless the repository provides *and validates*
  the mapping. The gate must find that mapping or record its absence. Constructing one here would
  be inventing a transfer model, which is a no-go (§8).
- **E3 — are the two components rivals at all?** Two entries in the registry that share a card
  are not thereby two independent predictions. **Co-location is not a relationship**
  (CLAUDE.md). The gate must establish, from the corpus map and the card, whether the
  `first_drip_time` edge on both components is one Outputs clause counted twice.

## 4. Evidence and replicate audit (runs before any model comparison)

From the fixture and the manifest, determine and record:

- the number of physically independent shots or replicates;
- whether multiple rows are true replicates or samples from one trace;
- measurement cadence and the resulting event resolution;
- whether an experimental spread is available;
- whether either component has an independently declared uncertainty on this observable;
- whether the matched operating configuration is fully specified;
- what the unresolved card or provenance condition permits to be claimed.

**Uncertainty may not be manufactured** from: solver convergence; optimizer residual; fit error
for another target; a single experimental/model residual; between-model separation; a
qualitative evidence-strength label; or an assumed coefficient of variation. This list is frozen
now, before any number is computed.

## 5. Execution — exactly one bounded run is permitted, and it is not a discrimination run

**Execution class: `MECHANISM_IDENTITY_CHECK`.**

If the gate finds that the two components are pipeline stages rather than rivals, that claim must
be *demonstrated*, not asserted. The permitted demonstration is:

1. Solve `machine_mode` **in its own declared configuration** (Foster Table I, the fine-grind fit
   it is gated on). No refit, no parameter change, no new configuration.
2. Extract the driving pressure history that its own solution implies at the bed top,
   `ΔP(t) = p_h(H) + p_c + ρg(H + s) − p_a`.
3. Integrate `foster2025.infiltration`'s **public** closed form under that `ΔP(t)`, from the
   ponding state `s(t_p) = s_p`, using `front_from_pressure`.
4. Compare the two front trajectories `s(t)` over `[t_p, t_s]`.

**Frozen thresholds for the identity claim:** RMSE < 0.01 mm and max |Δs| < 0.02 mm, against a
bed depth `L = 9.975 mm` and the existing `gate_foster_ct_trajectory` tolerance of 0.2 mm. A
**grid-refinement check** must additionally show the residual falling as the quadrature grid is
refined; if it does not fall, the residual is not quadrature error and the identity claim fails.

This run is **not** a discrimination test, produces **no** comparison of either component against
`de1_fixtureA`, and licenses no statement about which model fits the data better. Anything beyond
these four steps is out of scope.

`foster2025.machine_mode` is **not** run against `de1_fixtureA` under any circumstances: it
accepts no recorded pressure history, and supplying one would require refitting its pump
characteristic (§8).

## 6. Decision paths, frozen with their preconditions

1. **No common first-drip definition** (E1 or E2 fails, or E3 shows they are not rivals):
   **RETIRE** with a precise convention/relationship rationale and a reopen condition. No
   decorative model comparison is run.
2. **Common definition exists, but no replicate spread or other defensible discrimination
   uncertainty**: **NEEDS_NEW_DATA**, with a specific measurement request. Model separation alone
   may **not** override missing uncertainty.
3. **Common definition, matched configuration and defensible uncertainty all exist**: execute
   both variants under the exact same declared configuration, compare against the evidence under
   the frozen event definition, stay inside all declared ranges, do not recalibrate or refit.

**Ordering rule, frozen now to prevent a post-result choice between RETIRE and NEEDS_NEW_DATA:**
if the obstacle is *structural* — the components are not rivals, or no common event definition
exists, or the evidence lies outside a component's declared configuration — the disposition is
**RETIRE**, because no quantity of new measurement changes it. NEEDS_NEW_DATA applies only where
the comparison is well posed and the single missing item is a *measurement or an uncertainty*.

A screen that returns RETIRE on structural grounds must state explicitly whether a replicate
campaign would have rescued it. Commissioning an experiment that cannot answer the question is a
worse outcome than the retirement.

## 7. Decision thresholds — the candidate's own criteria, applied without revision

Copied from `docs/insights/candidates/I-090_can_first_drip_time_discriminate_between_the_mod.md`,
Human triage → Decision criteria:

- **SURVIVE** — between-model separation exceeds within-model uncertainty somewhere the data
  lands, under one fixed observable definition.
- **RETIRE** — model predictions overlap once declared uncertainty is drawn, the measurements
  fall outside every model's validity range, or the apparent separation is an
  observable-convention artifact.
- **NEEDS_NEW_DATA** — the measurements are single-replicate and no spread can be drawn.

## 8. No-go conditions

The screen stops and reports rather than proceeding if any of these arise:

- a transport or instrumentation delay would have to be invented to equate front breakthrough
  with first scale mass;
- `machine_mode`'s pump characteristic would have to be refitted to the DE1;
- `kappa_fitted` or any other parameter would have to be re-estimated;
- a population variance would have to be assumed, or inferred from within-trace sampling;
- either component would have to be run outside its declared configuration;
- a replicate count would have to be derived from an assumed coefficient of variation.

## 9. Adversarial checks (all are run; each may overturn the finding)

- **B1 — threshold sensitivity.** Does the 0.5 g threshold choice move the measured event, and by
  how much relative to the sampling cadence?
- **B2 — cadence as uncertainty.** Is sampling cadence being used as a stand-in for replicate
  spread anywhere? It must not be.
- **B3 — the shared-card rescue.** Could the two components be genuine rivals despite sharing a
  card, because the implementations differ? Test the *front law* in each implementation, not the
  prose.
- **B4 — the "same event, different origin" rescue.** If both compute front arrival at `z = L`,
  is the difference only a time origin that could be aligned?
- **B5 — validity range.** Does `de1_fixtureA` lie inside each component's declared range?
- **B6 — the separation-as-uncertainty trap.** Is between-model separation being used as its own
  uncertainty anywhere?
- **B7 — would replicates rescue it?** State plainly whether a replicate campaign changes the
  disposition.
- **B8 — is the observable itself worthless?** If these two are not rivals, does that mean
  `first_drip_time` cannot discriminate anything? It does not, and the screen must say what the
  observable *could* discriminate, without claiming that as a result.

## 10. Expected outputs

```
puckworks/analysis/screen_i090_first_drip.py           deterministic, no RNG, no wall-clock
tests/test_screen_i090.py                              asserts the scientific contract
docs/insights/screens/I-090/result.json                producer-bound, hash-bound
docs/insights/screens/I-090/decision.md                blueprint Appendix C shape
docs/insights/screens/I-090/README.md                  what was run, how to re-run
docs/insights/screens/I-090/figures/primary.png        the primary figure
```

`result.json` binds: candidate id, base commit, **SHA-256 of this protocol file**, input hashes,
the frozen event definitions, models actually executed and the execution count, uncertainty
authorities (or their recorded absence), primary numerical findings, adversarial checks,
decision, rationale, claim ceiling, and whether any administrative exception was invoked.

Per the candidate's own instruction, the primary figure must make the **absence of a spread
visually explicit rather than implied**: single-replicate measurements are drawn as
single-replicate marks, never with an error bar the evidence does not support.

## 11. Correction targets are recorded, never applied

If this screen finds a defect in an evidence label, a manifest cell or a card, it **records** the
finding, names the exact correction target and recommends wording — and does not edit it.

This is not caution for its own sake. CLAUDE.md is explicit that the Insight Foundry *"is never an
authority"* and *"may not change, promote or restate any label, badge or validation rung"*, and
I-045 set the precedent in this layer: its three correction targets were named and deliberately
left byte-unchanged, because editing an evidence label is a separate, human-owned change. A test
asserts the named targets are unmodified by this branch.

## 12. Claim ceiling (frozen before results, and it may not be raised afterwards)

Whatever this screen returns:

- it does **not** upgrade either component's validation rung or evidence class. They remain
  `sign_or_compatibility` and `source_curve_reproduction`;
- it does **not** convert within-campaign evidence into independent validation;
- it does **not** establish that either component is right or wrong about first drip;
- it does **not** establish mechanism identification, in either direction — showing that two
  implementations share a law is a statement about the *code and the source*, not a claim that
  the law is correct;
- it does **not** validate the unresolved `de1_fixtureA` provenance condition, and it may not
  rely on that condition being resolved;
- it does **not** license a public or reader-facing statement about first drip in espresso.

The strongest admissible output class is `experiment_design` (a targeted first-drip campaign) or
`technical_note` (a registry finding about how a shared-card Outputs clause generates a spurious
discriminator row) — per the candidate card, and only downstream of a human decision.

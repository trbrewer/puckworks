# I-072 — matched-observable protocol (FROZEN BEFORE EXECUTION)

```
CHEAP_SCIENTIFIC_SCREEN
NOT_A_PUBLICATION_RESULT
NOT_A_MODEL_VALIDATION_UPGRADE
```

**This document is committed before the screen module exists**, and it is what the screen is
bound to. It freezes the scientific question, the compatibility gate that must be passed before
either component may be executed, the uncertainty authorities, the decision thresholds, the
adversarial checks and the claim ceiling.

Components under comparison:

```
mo2023_2.swelling          (bed_dynamics, runtime, source_curve_reproduction)
brewer2026.streamtube      (bed_dynamics, runtime, within_campaign_held_out)
```

Neither `mo2023_2.coupled_bed` nor `mo2023_2.extraction` is in scope: the candidate names
`mo2023_2.swelling`, and the standing caveat that the three mo2023_2 components are kept
deliberately distinct (ONBOARDING §6) is respected rather than worked around.

---

## 1. Exact scientific question

Under one genuinely matched scenario, do `mo2023_2.swelling` and `brewer2026.streamtube` differ
in sign, ordering, or magnitude on a **physically shared** observable by more than the
uncertainty the repository can actually declare?

The first stage is a **semantic and dimensional compatibility gate**. The two components are not
to be executed merely because both emit quantities that can be drawn on an axis. Execution is
conditional on the gate passing, and the gate is defined in §4 before any code is written.

## 2. Evidence unit

The evidence unit is **one component-pair comparison at one matched operating point**, not a
sweep. A response sweep over grind or pressure is RP-A (ROADMAP §9) and is explicitly out of
scope for the Foundry (`docs/insights/INSIGHT_FOUNDRY_DESIGN.md`; CLAUDE.md Insight Foundry
block).

## 3. Observable definitions, as the authorities state them

Frozen from the registry entry, the module contract and the card, copied rather than paraphrased.

### 3a. `mo2023_2.swelling`

- **Emitted quantity.** `flow_decay(powder, t_eval)` returns `q_rel(t) = q(t)/q(0)`, documented
  in `puckworks/models/mo2023_2/swelling.py` as the *"relative superficial velocity; Δp/μ/L
  cancel"*, together with `eps_b(t)` (bed porosity, Eq. 21) and `d32(t)` (Sauter mean, Eq. 26).
  `flow_decay_ratio(powder, t_end)` returns the scalar `q(t_end)/q(0)`.
- **Mathematical definition.** Carman–Kozeny conductivity ratio
  `ε_b^(3+2n) d₃₂² / (1−ε_b)²`, evaluated at time `t` and normalised by its value at `t=0`.
- **Units.** Dimensionless ratio. `Δp`, `μ` and `L` cancel *by construction* — the module says so
  and the gate depends on it.
- **Total vs normalised.** Bed-**mean** (whole-bed, single 1-D column), normalised to its own
  `t = 0` value.
- **Index.** Indexed by **time**. There is no lateral index: the bed is one column.
- **Evaluation location / pressure node.** No node is exposed. `Δp` is a fixed scalar that
  cancels; the model never evaluates a pressure at a location. §5.9 / ledger A1 therefore does
  not bind this output, and that is itself a compatibility fact, not an oversight.
- **Time origin.** `t = 0` is the instant the dry grain surfaces reach the surface water
  fraction `C_M` (Dirichlet BC `c^w(ℛ)=C_M`); the initial state is a dry grain,
  `c^w(r,0)=0`.
- **Intervention.** **Fixed Δp**, free flow.
- **Initial state / saturation.** Dry grains, instantaneously wetted at the surface. No
  unsaturated-flow stage and no prewet.
- **Geometry.** Fixed bed height; swelling reduces `ε_b` only (Eq. 21). Two representative
  particles (fine, coarse) per powder.
- **Parameter validity range** (registry, verbatim): *"fixed-dP flow DECAY (Fig 3a headline)
  reproduced as a Δp/mu/L-independent RATIO q(60)/q(0): E/H/M within ~5%, F within ~13%, and the
  coarser-throttles-less ordering E<H<M<F; s_m=3.57% (Eq 8) from C_M=0.1 ASSUMED not measured;
  fixed-dP swelling claim is unvalidated in the paper."*
- **Grind descriptor.** Powder identity `E / H / M / F` from `mo2_granulometry()`
  (`θ_f, θ_c, 2R_f, 2R_c, d₃₂`). **There is no grinder dial.**

### 3b. `brewer2026.streamtube`

- **Emitted quantity, Rung A (the gated rung).** `EYResponse.deficit(sigma)` — the relative
  extraction-yield deficit of the heterogeneous ensemble against the homogeneous shot,
  `1 − EY_ensemble(σ)/EY(k=1)`. The per-tube state is a **permeability multiplier** `k_i` drawn
  from a **unit-mean** lognormal (`lognormal_nodes`), constant in time.
- **Emitted quantity, Rung B.** `simulate_ensemble_dynamic` returns `kappa(t)` per tube and a
  total `flow_gs(t)`. Rung B is declared **hypothesis-generating** in the registry `notes`
  (*"Rung B fines migration is hypothesis-generating"*) and carries no gate.
- **Units.** Rung A deficit: dimensionless fraction. `k_i`: dimensionless multiplier on
  permeability.
- **Total vs normalised.** Rung A `k_i` is normalised so the ensemble **mean is exactly one**
  (`lognormal_nodes` returns `k = exp(σξ − σ²/2)`; `simulate_ensemble_dynamic` additionally
  applies `k0 *= 1.0 / k0.mean()`).
- **Index.** Indexed by **tube** (lateral position). Rung A carries no time index for `k`.
- **Evaluation location / pressure node.** All tubes share one common pressure drop,
  `p_bar = 5.0` at the module default; the node is the same single scalar for every tube.
- **Time origin.** Shot start; the shot **ends when total beverage mass reaches `m_out`**, so
  the natural endpoint is a delivered mass, not a clock time.
- **Intervention.** Fixed pressure **and** a fixed delivered-mass endpoint
  (`m_in = 0.020 kg`, `m_out = 0.040 kg`).
- **Initial state / saturation.** Saturated bed. No infiltration stage.
- **Geometry.** K parallel **non-exchanging** tubes (registry `assumptions`, verbatim:
  *"parallel non-exchanging tubes; unit-mean lognormal k; sigma(phi1) is an EMPIRICAL closure
  over the calibrated domain"*).
- **Parameter validity range** (registry, verbatim): *"calibrated at dial 1.1-1.5;
  LOO-interpolated, not externally validated"*.
- **Grind descriptor.** **EK43 dial** `GS`, entering through the Cameron microstructure tables.
- **Card status.** `brewer2026.streamtube` has **no card** at `docs/cards/brewer2026_streamtube.md`
  or `docs/cards/brewer2026.md`. Its validity range and uncertainty must be sourced from the
  registry entry and `gate_streamtube_heldout`, and that provenance is stated on the result.

## 4. The compatibility gate (must pass before any execution)

A **shared observable** exists only where all five of the following align **without** inventing a
parameter, refitting either component, adding physics, constructing an unvalidated adapter,
silently changing the question a component answers, or extrapolating past a declared range:

- **G1 — physical quantity and mathematical definition.**
- **G2 — index and normalisation** (what the quantity is a function of, and what it is
  normalised by).
- **G3 — evaluation location / pressure node** (§5.9, ledger A1).
- **G4 — intervention / boundary condition** (fixed-Δp vs fixed-pressure-and-mass endpoint) and
  initial saturation state.
- **G5 — declared validity domains intersect**, in a descriptor **both** components accept.

**G5 is evaluated under CLAUDE.md rule 9 / ledger A9, G5:** dial spaces are grinder-specific and
non-portable, and no dial may be mapped to another grinder's without an explicit refit adapter.
A numerical coincidence between derived summary statistics (for example a Sauter diameter
`d₃₂` computed on each side) is **not** a matched grind and does not satisfy G5.

**Execution rule.** If the gate fails, **neither component is executed** and the screen ends at
the gate with a RETIRE on "different questions" (§7). The screen module may evaluate **pure
structural constructors that perform no solve** — specifically
`brewer2026.streamtube.lognormal_nodes` and the quantile-midpoint tube construction — in order to
*prove* a structural claim about the ensemble. It may **not** call `EYResponse`,
`simulate_ensemble_dynamic`, `mo2023_2.swelling.flow_decay`, `flow_decay_ratio`,
`swelling_volume_ratio`, or any Cameron solve. The result artifact records exactly which
functions were evaluated and asserts the forbidden set was not entered.

Reading digitised source data (`mo2_fig3a_qdecay`, `mo2_granulometry`,
`cameron2020_fig5_grind_deviation`) is a **data read**, not a model execution, and is permitted.

## 5. Uncertainty authorities

Frozen **before** results, and deliberately restrictive.

**Admissible** as a quantitative uncertainty only if the repository supplies a numerical quantity
with the correct observable, population, units and scope.

- `brewer2026.streamtube`: the only numerical quantity the repository declares is
  `gate_streamtube_heldout`'s **held-out absolute error on the EY relative deviation**
  (leave-one-out over GS 1.1/1.3/1.5, pass threshold `< 0.02`). Its observable is the **EY
  deficit**, its population is three grind settings from one campaign, and its units are a
  dimensionless yield fraction.
- `mo2023_2.swelling`: the registry declares reproduction agreement — *"E/H/M within ~5%, F
  within ~13%"* — and `gate_mo2_swelling_flow_decay` uses a `max_rel_err < 0.20` pass threshold.
  These are **model-vs-source agreement tolerances**, not measurement uncertainties on the
  physical quantity, and the source campaign retains no replicate spread on `q(t)/q(0)`.

**Inadmissible**, and this is a frozen commitment:

- the evidence-strength label `within_campaign_held_out` used as if it were a numerical band;
- the difference between the two components;
- solver tolerance or convergence;
- a fit RMSE for a different observable;
- a gate pass threshold reused as a physical uncertainty;
- an arbitrary percentage band;
- visual line thickness.

If a shared observable is found, the comparison may proceed **only** if an admissible band exists
**for that observable**. If not, the disposition is NEEDS_NEW_DATA naming the missing
characterisation — never a comparison drawn against a borrowed band.

## 6. Adversarial checks (all are run, and each may overturn the finding)

- **A1 — units.** Is any apparent incompatibility only a unit mismatch?
- **A2 — total vs normalised.** Does normalising both to their own `t=0` (or `σ=0`) value make
  them the same quantity?
- **A3 — pressure node.** Does the §5.9 node choice explain the difference?
- **A4 — time origin.** Does aligning `t=0` (wetting instant vs shot start vs mass endpoint)
  reconcile them?
- **A5 — sign convention.** Is one the reciprocal or the complement of the other?
- **A6 — geometry / area scaling.** Does a basket-area or bed-depth factor reconcile them?
- **A7 — fixed-flow vs fixed-pressure.** Is the incompatibility only the intervention, and is
  there a declared conversion? (ONBOARDING: mo2023_2's fixed-q branch is *insensitive* to
  swelling while the fixed-Δp branch throttles hard — the intervention is load-bearing.)
- **A8 — initial saturation / prewet.**
- **A9 — the known composition mis-scale.** `gate_kappa_t_composition_diagnostic` already records
  that mo2023_2's fixed-Δp swelling branch, imported unrefitted into a shared porosity state,
  **over-closes** a saturated pre-wet bed, diagnosed as a mis-scaled branch and *"reported not
  tuned away"*. **Any** difference this screen might report must be shown not to be that same,
  already-known mis-scale. A previously known scaling or composition mismatch may not be
  presented as a new physical discovery.
- **A10 — the d₃₂ rescue.** If the two grind descriptors produce numerically overlapping Sauter
  diameters, does that constitute a matched grind under G5? The frozen answer is **no** unless
  the underlying granulometry (fines fraction and both representative radii) also matches and a
  declared adapter exists; the check computes the numbers and states the disposition either way.
- **A11 — the Rung-B rescue.** Rung B emits `kappa(t)` and a total `flow_gs(t)`, which are
  time-indexed and bed-total, i.e. the index and normalisation `mo2023_2.swelling` uses. Does
  Rung B therefore supply the shared observable G1–G2 need? The check states which parameters a
  Rung-B run would require, whether the repository declares values for them, and whether Rung B
  carries a gate.

## 7. Decision thresholds — the candidate's own criteria, applied without revision

Copied from `docs/insights/candidates/I-072_do_mo2023_2_swelling_and_brewer2026_streamtube_a.md`,
Human triage → Decision criteria:

- **SURVIVE** — the components differ by more than their declared uncertainty at a point inside
  both validity ranges, under one fixed and recorded observable definition.
- **RETIRE** — the curves overlap within declared uncertainty, the validity ranges do not
  intersect, or **no shared observable definition exists** (the expected outcome).
- **NEEDS_NEW_DATA** — neither component can be run in a matched configuration without inventing
  a parameter the cards do not provide — including the case where `brewer2026.streamtube`'s
  missing card leaves its validity range undeclarable.

**Ordering rule, frozen now to prevent a post-result choice between RETIRE and NEEDS_NEW_DATA:**
if the compatibility gate fails on G1–G4 (the components answer different questions), the
disposition is **RETIRE**, because no amount of new data changes what a component computes.
NEEDS_NEW_DATA applies only where G1–G4 pass and the obstacle is a *missing declared value* —
a matched parameter, a validity range, or an uncertainty characterisation.

## 8. No-go conditions

The screen stops and reports rather than proceeding if any of these arise:

- a parameter would have to be invented for either component;
- either component would have to be refitted or recalibrated;
- an adapter between the two grind descriptors would have to be constructed;
- a quantitative comparison would have to borrow an uncertainty from a different observable;
- the comparison would require extrapolating either component past its declared range.

## 9. Expected outputs

```
puckworks/analysis/screen_i072_matched_observable.py   deterministic, no RNG, no wall-clock
tests/test_screen_i072.py                              asserts the scientific contract
docs/insights/screens/I-072/result.json                producer-bound, hash-bound
docs/insights/screens/I-072/decision.md                blueprint Appendix C shape
docs/insights/screens/I-072/README.md                  what was run, how to re-run
docs/insights/screens/I-072/figures/primary.png        the primary figure
```

`result.json` binds: candidate id, base commit, **SHA-256 of this protocol file**, input hashes,
the frozen observable definitions, models executed (and the assertion that the forbidden set was
not entered), uncertainty authorities, adversarial-check outcomes, decision, rationale, claim
ceiling, and whether any administrative exception was invoked.

The primary figure is, per the candidate's own instruction for this branch: *"if no shared
definition survives step 1, the two observable definitions side by side showing why they are not
the same quantity."*

## 10. Claim ceiling (frozen before results, and it may not be raised afterwards)

This screen is a **registry finding about a declared-competitor row**. Whatever it returns:

- it does **not** upgrade either component's validation rung or evidence class;
- it does **not** establish that either component is right, wrong, better or worse;
- it does **not** establish agreement between them — two components that answer different
  questions neither agree nor disagree;
- it does **not** establish that a real bed lacks either mechanism; `docs/cards/mo2023_2.md`
  says a bed can have both;
- it does **not** license any statement about espresso beyond what the two components' own
  gates already license, and those ceilings are `source_curve_reproduction` and
  `within_campaign_held_out` respectively.

The strongest admissible output class is `technical_note`, per the candidate card.
